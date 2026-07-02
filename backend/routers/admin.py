# ============================================
# 审核管理 API 路由
# ============================================
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models import (
    PostRaw, MerchPost, Merch, CraftTag, MerchCraft, IP
)
from backend.schemas import ReviewQueueItem, ReviewAction
from backend.nlp.parser import NLPParser

router = APIRouter(prefix="/api/admin", tags=["管理后台"])

page_router = APIRouter(prefix="/admin", tags=["管理后台页面"])

# 审核页面 HTML 文件路径
_REVIEW_HTML = Path(__file__).parent.parent / "templates" / "admin" / "review.html"

# ENUM 校验集合
VALID_CATEGORIES = {'吧唧', '色纸', '亚克力立牌', '粘土人', '挂件', '文件夹', '海报', '立牌', '其他'}
VALID_RELEASE_METHODS = {'通贩', '场贩', '受注', '限定', '抽选', '未知'}


def _parse_images(post_raw) -> list:
    """安全解析 PostRaw.images —— 可能是 JSON 字符串、list 或 None"""
    import json
    raw = post_raw.images if post_raw else None
    if raw is None:
        return []
    if isinstance(raw, list):
        return raw
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return []
    return []


def _safe_enum(value: str, valid_set: set, default: str) -> str:
    """校验值是否在 ENUM 集合内，不在则返回默认值"""
    if value and value in valid_set:
        return value
    return default


@page_router.get("/review", response_class=HTMLResponse)
def admin_review_page(request: Request):
    """审核队列页面"""
    html = _REVIEW_HTML.read_text(encoding="utf-8")
    return HTMLResponse(html)

# ── 审核队列 ──

@router.get("/review-queue", response_model=dict)
def review_queue(
    review_status: str | None = Query('pending', description="审核状态筛选"),
    limit: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
    search: str | None = Query(None, description="关键字搜索（标题/内容/作者/IP）"),
    db: Session = Depends(get_db),
):
    """获取待审核队列（分页 + 搜索）"""
    import math
    from sqlalchemy import or_

    q = db.query(MerchPost).filter(MerchPost.review_status == review_status)

    # 关键字搜索：标题、内容、作者、IP名称
    if search and search.strip():
        kw = search.strip()
        q = q.join(MerchPost.post_raw).filter(
            or_(
                PostRaw.title.contains(kw),
                PostRaw.content.contains(kw),
                PostRaw.author_name.contains(kw),
                MerchPost.ip_name_hint.contains(kw),
                MerchPost.merch_name.contains(kw),
            )
        )

    total = q.count()
    total_pages = max(1, math.ceil(total / limit))
    items = q.order_by(MerchPost.id.desc()).offset((page - 1) * limit).limit(limit).all()

    result = []
    for mp in items:
        post = mp.post_raw
        import json
        raw_images = None
        if post and post.images:
            if isinstance(post.images, str):
                try: raw_images = json.loads(post.images)
                except: raw_images = []
            elif isinstance(post.images, list):
                raw_images = post.images
        result.append(ReviewQueueItem(
            id=mp.id,
            post_raw_id=mp.post_raw_id,
            post_title=post.title or '',
            post_content=post.content or '',
            post_url=post.post_url or '',
            author_name=post.author_name or '',
            post_time=post.post_time,
            ip_name_hint=mp.ip_name_hint,
            ip_id=mp.ip_id,
            merch_name=mp.merch_name,
            category=mp.category,
            category_hint=mp.category_hint,
            official_price=float(mp.official_price) if mp.official_price else None,
            release_date=mp.release_date,
            release_method=mp.release_method,
            craft_keywords=mp.craft_keywords or [],
            attributes=mp.attributes,
            confidence=float(mp.confidence) if mp.confidence else 0,
            need_review=bool(mp.need_review),
            review_status=mp.review_status,
            images=raw_images or [],
        ))
    return {
        "items": result,
        "total": total,
        "page": page,
        "size": limit,
        "total_pages": total_pages,
    }


@router.post("/review/{mp_id}/approve")
def review_approve(mp_id: int, db: Session = Depends(get_db)):
    """审核通过 — 入库到 merch 正式表"""
    mp = db.query(MerchPost).filter(MerchPost.id == mp_id).first()
    if not mp:
        raise HTTPException(404, "记录不存在")

    import json

    # IP 匹配：先用 ip_id 查；无则用 ip_name_hint 查；查不到就自动创建
    ip_id = mp.ip_id
    if not ip_id and mp.ip_name_hint:
        ip_row = db.query(IP).filter(IP.name == mp.ip_name_hint).first()
        if ip_row:
            ip_id = ip_row.id
        else:
            # 本地没有这个 IP → 自动创建
            new_ip = IP(
                name=mp.ip_name_hint,
                category='动漫',        # 默认分类，后续可手动改
                aliases=[],
                description='自动创建于审核入库'
            )
            db.add(new_ip)
            db.flush()
            ip_id = new_ip.id
    if not ip_id:
        # 最后兜底：归入"其他未分类"
        fallback = db.query(IP).filter(IP.name == '其他未分类').first()
        if not fallback:
            fallback = IP(name='其他未分类', category='其他')
            db.add(fallback)
            db.flush()
        ip_id = fallback.id

    attrs = mp.attributes or {}
    if isinstance(attrs, str):
        try: attrs = json.loads(attrs)
        except: attrs = {}
    if not isinstance(attrs, dict):
        attrs = {}
    crafts = mp.craft_keywords
    if isinstance(crafts, str):
        try: crafts = json.loads(crafts)
        except: crafts = []

    # 安全解析 images（可能是 JSON 字符串）
    all_images = _parse_images(mp.post_raw)
    image_url = ','.join(all_images) if all_images else None

    # 新 IP 自动补封面
    ip_r = db.query(IP).filter(IP.id == ip_id).first()
    if ip_r and image_url:
        ip_r.cover_url = image_url.split(',')[0]

    # 校验 ENUM 字段
    safe_category = _safe_enum(mp.category, VALID_CATEGORIES, '其他')
    safe_method = _safe_enum(mp.release_method, VALID_RELEASE_METHODS, '未知')

    merch = Merch(
        ip_id=ip_id,
        name=mp.merch_name or mp.post_raw.title or '未命名周边',
        category=safe_category,
        official_price=mp.official_price,
        release_date=mp.release_date,
        release_method=safe_method,
        attributes=json.dumps({'crafts': crafts}, ensure_ascii=False),
        image_url=','.join(all_images) if all_images else None,
        source_platform='weibo',
        source_url=mp.post_raw.post_url,
        original_post_id=mp.post_raw_id,
    )
    db.add(merch)
    db.flush()  # 获取 merch.id

    # 关联工艺标签
    if mp.craft_keywords:
        for craft_name in mp.craft_keywords:
            tag = db.query(CraftTag).filter(CraftTag.name == craft_name).first()
            if tag:
                mc = MerchCraft(merch_id=merch.id, craft_id=tag.id)
                db.add(mc)

    # 更新状态
    mp.review_status = 'approved'
    mp.reviewed_at = datetime.utcnow()
    mp.post_raw.status = 'approved'

    db.commit()
    return {"ok": True, "merch_id": merch.id}


@router.post("/review/{mp_id}/edit")
def review_edit(mp_id: int, data: ReviewAction, db: Session = Depends(get_db)):
    """编辑后入库 — 用修改后的数据创建 merch"""
    mp = db.query(MerchPost).filter(MerchPost.id == mp_id).first()
    if not mp:
        raise HTTPException(404, "记录不存在")

    import json

    # 用提交的数据覆盖（未提供的保持原值）
    final_ip_id = data.ip_id or mp.ip_id
    hint = data.ip_name or mp.ip_name_hint
    if not final_ip_id and hint:
        ip_row = db.query(IP).filter(IP.name == hint).first()
        if ip_row:
            final_ip_id = ip_row.id
        else:
            # 编辑入库时 IP 不存在 → 自动创建
            new_ip = IP(
                name=hint,
                category='动漫',
                aliases=[],
                description='编辑审核时自动创建'
            )
            db.add(new_ip)
            db.flush()
            final_ip_id = new_ip.id
    # 兜底：用 hint 创建（即使是 None 的 hint 也会走下面 fallback）
    if not final_ip_id:
        fallback_hint = hint or '其他未分类'
        fallback = db.query(IP).filter(IP.name == fallback_hint).first()
        if not fallback:
            fallback = IP(name=fallback_hint, category='其他')
            db.add(fallback)
            db.flush()
        final_ip_id = fallback.id
    final_name = data.merch_name or mp.merch_name or mp.post_raw.title or '未命名周边'

    # release_date 现在是 str | None，需要安全解析
    from datetime import date as date_type
    final_date = mp.release_date  # 默认保持原值
    if data.release_date and data.release_date.strip():
        try:
            final_date = date_type.fromisoformat(data.release_date.strip())
        except (ValueError, TypeError):
            pass  # 格式不对时保持原值

    # 发售方式多选 → 取第一个有效的作为 ENUM 值；完整列表存入 attributes.multimethods
    final_methods = data.release_methods or []
    if not final_methods and mp.release_method:
        final_methods = [mp.release_method] if mp.release_method != '未知' else []
    safe_method = '未知'
    for m in final_methods:
        if m in VALID_RELEASE_METHODS and m != '未知':
            safe_method = m
            break
    if safe_method == '未知' and data.release_method and data.release_method in VALID_RELEASE_METHODS:
        safe_method = data.release_method

    # 工艺
    final_crafts = data.craft_keywords or mp.craft_keywords or []
    if isinstance(final_crafts, str):
        try: final_crafts = json.loads(final_crafts)
        except: final_crafts = []

    # 安全解析 images（修复：images 在数据库中是 JSON 字符串，不能直接 [0]）
    all_images = _parse_images(mp.post_raw)
    first_image = all_images[0] if all_images else None

    # 多品类创建
    categories = data.categories or [{
        "category": data.category or mp.category or '其他',
        "price": data.official_price if data.official_price is not None else mp.official_price
    }]
    result = []
    for info in categories:
        if isinstance(info, dict):
            cat = info.get('category') or '其他'
            price = info.get('price')
        else:
            cat = str(info)
            price = None
        # ENUM 校验
        cat = _safe_enum(cat, VALID_CATEGORIES, '其他')
        m = Merch(
            ip_id=final_ip_id,
            name=final_name,
            category=cat,
            official_price=price,
            release_date=final_date,
            release_method=safe_method,
            attributes=json.dumps({
                'crafts': final_crafts,
                'multimethods': final_methods,  # 完整多选发售方式
            }, ensure_ascii=False),
            image_url=','.join(all_images) if all_images else None,
            source_platform='weibo',
            source_url=mp.post_raw.post_url,
            original_post_id=mp.post_raw_id,
        )
        db.add(m)
        db.flush()
        # 关联工艺
        for craft_name in final_crafts:
            tag = db.query(CraftTag).filter(CraftTag.name == craft_name).first()
            if tag:
                mc2 = MerchCraft(merch_id=m.id, craft_id=tag.id)
                db.add(mc2)
        result.append(m.id)

    # 自动更新 IP 封面
    ip_r = db.query(IP).filter(IP.id == final_ip_id).first()
    if ip_r and first_image:
        ip_r.cover_url = first_image

    mp.review_status = 'edited'
    mp.reviewed_at = datetime.utcnow()
    mp.post_raw.status = 'approved'
    db.commit()
    return {"ok": True, "merch_ids": result}


@router.post("/review/{mp_id}/reject")
def review_reject(mp_id: int, db: Session = Depends(get_db)):
    """拒绝 — 不入库"""
    mp = db.query(MerchPost).filter(MerchPost.id == mp_id).first()
    if not mp:
        raise HTTPException(404, "记录不存在")

    mp.review_status = 'rejected'
    mp.reviewed_at = datetime.utcnow()
    mp.post_raw.status = 'rejected'
    db.commit()
    return {"ok": True}


# ── 爬虫触发 ──

@router.post("/crawl/trigger")
def trigger_crawl(
    keyword: str | None = Query(None),
    db: Session = Depends(get_db),
):
    """手动触发一次爬虫 — 云端模式（用 cookie 直接调微博 API）"""
    from backend.nlp.parser import NLPParser
    import threading

    def _run():
        from backend.database import SessionLocal
        sdb = SessionLocal()
        try:
            WEIBO_COOKIE = os.environ.get("WEIBO_COOKIE", "")
            if not WEIBO_COOKIE:
                print("[Crawl] WARNING: WEIBO_COOKIE not set")
                return

            import httpx, urllib.parse, json as _json, re as _re, time as _time
            from datetime import datetime as _dt

            # 解析 cookie
            if WEIBO_COOKIE.strip().startswith("["):
                try:
                    cookies = _json.loads(WEIBO_COOKIE)
                    cookie_str = "; ".join(f"{c['name']}={c['value']}" for c in cookies)
                except:
                    cookie_str = WEIBO_COOKIE
            else:
                cookie_str = WEIBO_COOKIE

            client = httpx.Client(
                headers={
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
                    "Cookie": cookie_str,
                    "Referer": "https://m.weibo.cn/",
                    "X-Requested-With": "XMLHttpRequest",
                },
                timeout=30, follow_redirects=True,
            )

            keywords = [keyword] if keyword else [
                "周边 上新", "谷子 发售", "吧唧 新品", "动漫周边 上新",
            ]
            total = 0
            try:
                for kw in keywords:
                    for pg in range(1, 4):
                        cid = f"100103type=1&q={urllib.parse.quote(kw)}"
                        url = f"https://m.weibo.cn/api/container/getIndex?containerid={cid}&page={pg}"
                        try:
                            resp = client.get(url)
                            data = resp.json()
                        except Exception as e:
                            print(f"[Crawl] request failed: {e}")
                            break
                        cards = data.get("data", {}).get("cards", []) if isinstance(data, dict) else []
                        page_count = 0
                        for card in cards:
                            def _collect_mblogs(obj, result):
                                if isinstance(obj, dict):
                                    if obj.get("mblog"): result.append(obj["mblog"])
                                    for v in obj.values(): _collect_mblogs(v, result)
                                elif isinstance(obj, list):
                                    for item in obj: _collect_mblogs(item, result)

                            mblogs = []
                            _collect_mblogs(card, mblogs)
                            for mblog in mblogs:
                                tid = str(mblog.get("id", "") or mblog.get("mid", "") or "")
                                if not tid: continue
                                if sdb.query(PostRaw).filter(
                                    PostRaw.platform == "weibo", PostRaw.post_id == tid
                                ).first(): continue

                                text = _re.sub(r"<[^>]+>", "", (mblog.get("text", "") or ""))
                                user = mblog.get("user", {}) or {}
                                author = user.get("screen_name", "") if isinstance(user, dict) else ""
                                images = []
                                for pic in mblog.get("pics") or []:
                                    if isinstance(pic, dict):
                                        u = pic.get("large", {}).get("url") or pic.get("url", "")
                                        if u: images.append(u)
                                ct = mblog.get("created_at", "")
                                try:
                                    created = _dt.fromisoformat(ct.replace(" +0800", "")) if ct else _dt.utcnow()
                                except:
                                    created = _dt.utcnow()
                                sdb.add(PostRaw(
                                    platform="weibo", post_id=tid, author_name=author or "",
                                    author_uid="", title=text[:700] if text else "", content=text,
                                    images=images, video_url="", post_url=f"https://m.weibo.cn/detail/{tid}",
                                    post_time=created, raw_json=mblog,
                                ))
                                page_count += 1
                            if page_count and page_count % 10 == 0:
                                sdb.commit()
                        if page_count:
                            sdb.commit()
                        total += page_count
                        print(f"[Crawl] {kw} page {pg}: {page_count} items")
                        if page_count == 0: break
                        _time.sleep(2)
            finally:
                client.close()

            # NLP 解析
            if total > 0:
                parser = NLPParser()
                parser.parse_pending(db=sdb)
            print(f"[Crawl] Done: {total} new posts")
        finally:
            sdb.close()

    t = threading.Thread(target=_run, daemon=True)
    t.start()

    return {"ok": True, "message": "云端爬虫已在后台启动"}


@router.post("/crawl/reparse")
def trigger_reparse(db: Session = Depends(get_db)):
    """重新运行 NLP 解析所有 pending 帖子"""
    parser = NLPParser()
    count = parser.parse_pending(db=db)
    return {"ok": True, "parsed_count": count}


# ── 统计 ──

@router.get("/stats")
def admin_stats(db: Session = Depends(get_db)):
    """管理后台统计数据"""
    total_raw = db.query(func.count(PostRaw.id)).scalar()
    pending_raw = db.query(func.count(PostRaw.id)).filter(PostRaw.status == 'pending').scalar()
    pending_review = db.query(func.count(MerchPost.id)).filter(MerchPost.review_status == 'pending').scalar()
    approved = db.query(func.count(Merch.id)).filter(Merch.status == 'active').scalar()

    return {
        "total_posts": total_raw,
        "pending_parse": pending_raw,
        "pending_review": pending_review,
        "approved_merch": approved,
    }


# ── 临时：删除坏数据 & 修复 IP ──

@router.delete("/merch/{merch_id}")
def delete_merch(merch_id: int, db: Session = Depends(get_db)):
    """删除一条周边记录"""
    m = db.query(Merch).filter(Merch.id == merch_id).first()
    if not m:
        raise HTTPException(404, "周边不存在")
    db.delete(m)
    db.commit()
    return {"ok": True, "deleted": merch_id}


@router.delete("/ip/{ip_id}")
def delete_ip(ip_id: int, db: Session = Depends(get_db)):
    """删除一个IP（仅当无关联周边时）"""
    ip = db.query(IP).filter(IP.id == ip_id).first()
    if not ip:
        raise HTTPException(404, "IP不存在")
    # 检查是否有未删除的 merch 关联
    related = db.query(Merch).filter(Merch.ip_id == ip_id, Merch.status == 'active').count()
    if related > 0:
        raise HTTPException(400, f"该IP下仍有{related}条周边，请先删除周边")
    # 解除关联的 merch_post
    db.query(MerchPost).filter(MerchPost.ip_id == ip_id).update({MerchPost.ip_id: None})
    db.delete(ip)
    db.commit()
    return {"ok": True, "deleted": ip_id}


@router.post("/fix-ip-cover")
def fix_ip_covers(db: Session = Depends(get_db)):
    """修复没有 cover_url 的 IP —— 从关联的 merch 取第一张图片"""
    ips = db.query(IP).all()
    fixed = []
    for ip in ips:
        if ip.cover_url:
            continue
        # 找最新的有价值 merch 图片
        m = db.query(Merch).filter(
            Merch.ip_id == ip.id,
            Merch.status == 'active',
            Merch.image_url.isnot(None),
        ).order_by(Merch.release_date.desc(), Merch.id.desc()).first()
        if m and m.image_url:
            first_img = m.image_url.split(',')[0].strip()
            if first_img:
                ip.cover_url = first_img
                fixed.append({"id": ip.id, "name": ip.name, "cover": first_img})
    if fixed:
        db.commit()
    return {"ok": True, "fixed": fixed}
