# ============================================
# 云端爬虫 — 独立脚本（不依赖 backend 模块），在 GitHub Actions 上运行
# ============================================
import json, os, re, sys, time, urllib.parse
from datetime import datetime

# ── Cookie 解析 ──
def _parse_cookie(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("["):
        try:
            cookies = json.loads(raw)
            return "; ".join(f"{c['name']}={c['value']}" for c in cookies)
        except json.JSONDecodeError:
            pass
    return raw

WEIBO_COOKIE = _parse_cookie(os.environ.get("WEIBO_COOKIE", ""))
print(f"[crawler] cookie prefix: {(WEIBO_COOKIE[:50] + '...') if WEIBO_COOKIE else 'EMPTY'}")

DB_URL = os.environ.get("DATABASE_URL", "")
if not DB_URL:
    print("FATAL: DATABASE_URL not set"); sys.exit(1)

# ── 数据库独立连接 ──
from sqlalchemy import create_engine, Column, BigInteger, String, Text, JSON, DateTime, Integer, Float
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine(
    DB_URL,
    pool_size=5, max_overflow=10, pool_pre_ping=True, echo=False,
    connect_args={"ssl": {"verify_cert": True, "verify_identity": True}} if "tidbcloud" in DB_URL else {},
)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# 定义 PostRaw 模型（独立，不引用 backend.models）
class PostRaw(Base):
    __tablename__ = "post_raw"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    platform = Column(String(50), default="weibo")
    post_id = Column(String(100), nullable=False)
    author_name = Column(String(200))
    author_uid = Column(String(100))
    title = Column(String(1000))
    content = Column(Text)
    images = Column(JSON)
    video_url = Column(String(2000))
    post_url = Column(String(2000))
    post_time = Column(DateTime)
    raw_json = Column(JSON)
    status = Column(String(50), default="pending")
    error_msg = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

import httpx

SEARCH_KEYWORDS = [
    "周边 上新", "谷子 发售", "吧唧 新品", "色纸 预售", "亚克力 上新",
    "镭射票 上新", "动漫周边", "同人周边", "国谷 上新", "周边 通贩",
    "周边 场贩", "周边 预约",
]
MAX_PAGES = 2

def _clean_html(text: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r'<img\s+[^>]*alt="([^"]*)"[^>]*>', r'\1', text)
    text = re.sub(r"<a\s[^>]*>", "", text)
    text = re.sub(r"</a>", "", text)
    text = re.sub(r"<span[^>]*>", "", text)
    text = re.sub(r"</span>", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.rstrip()
    if text.endswith('...全文'): text = text[:-4]
    elif text.endswith('全文'): text = text[:-2]
    return text.strip().rstrip('...').rstrip()

def _collect_mblogs(obj, result):
    if isinstance(obj, dict):
        if obj.get("mblog"): result.append(obj["mblog"])
        for v in obj.values(): _collect_mblogs(v, result)
    elif isinstance(obj, list):
        for item in obj: _collect_mblogs(item, result)

def run():
    client = httpx.Client(
        headers={
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
            "Cookie": WEIBO_COOKIE,
            "Referer": "https://m.weibo.cn/",
            "X-Requested-With": "XMLHttpRequest",
        },
        timeout=30, follow_redirects=True,
    )
    db = SessionLocal()
    total_saved = 0
    try:
        for i, kw in enumerate(SEARCH_KEYWORDS):
            saved = 0
            for pg in range(1, MAX_PAGES + 1):
                cid = f"100103type=1&q={urllib.parse.quote(kw)}"
                url = f"https://m.weibo.cn/api/container/getIndex?containerid={cid}&page={pg}"
                try:
                    resp = client.get(url)
                    data = resp.json()
                except Exception as e:
                    print(f"  [{kw}] request failed: {e}")
                    break
                cards = data.get("data", {}).get("cards", []) if isinstance(data, dict) else []
                page_count = 0
                for card in cards:
                    mblogs = []
                    _collect_mblogs(card, mblogs)
                    for mblog in mblogs:
                        tid = str(mblog.get("id", "") or mblog.get("mid", "") or "")
                        if not tid: continue
                        if db.query(PostRaw).filter(
                            PostRaw.platform == "weibo", PostRaw.post_id == tid
                        ).first():
                            continue
                        text = _clean_html(mblog.get("text", "") or "")
                        user = mblog.get("user", {}) or {}
                        author = user.get("screen_name", "") if isinstance(user, dict) else ""
                        images = []
                        for pic in mblog.get("pics") or []:
                            if isinstance(pic, dict):
                                u = pic.get("large", {}).get("url") or pic.get("url", "")
                                if u: images.append(u)
                        ct = mblog.get("created_at", "")
                        try:
                            created = datetime.fromisoformat(ct.replace(" +0800", "")) if ct else datetime.utcnow()
                        except:
                            created = datetime.utcnow()
                        db.add(PostRaw(
                            platform="weibo", post_id=tid, author_name=author or "",
                            author_uid="", title=text[:700] if text else "", content=text,
                            images=images, video_url="", post_url=f"https://m.weibo.cn/detail/{tid}",
                            post_time=created, raw_json=mblog,
                        ))
                        page_count += 1
                    if page_count and page_count % 10 == 0:
                        db.commit()
                if page_count:
                    db.commit()
                saved += page_count
                print(f"  [{kw}] page {pg}: {page_count} items (total={saved})")
                if page_count == 0: break
                time.sleep(2)
            total_saved += saved
            time.sleep(2)
        print(f"\nDone! Total new posts: {total_saved}")
    finally:
        client.close()
        db.close()

if __name__ == "__main__":
    run()
