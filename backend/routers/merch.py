# ============================================
# 周边相关 API 路由
# ============================================
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from backend.database import get_db
from backend.models import Merch, MerchCraft, CraftTag, IP
from backend.schemas import MerchOut, MerchDetail, CraftOut, StatsOut

router = APIRouter(prefix="/api/merch", tags=["周边"])


def _build_merch_out(merch: Merch) -> MerchOut:
    """将 ORM 对象转成 MerchOut，附带工艺列表和 IP 名"""
    import json
    crafts = [c.name for c in merch.crafts if c.name] if merch.crafts else []
    # 处理 attributes 可能是 str/list 的情况
    attrs = merch.attributes
    if isinstance(attrs, str):
        try:
            attrs = json.loads(attrs)
        except (json.JSONDecodeError, TypeError):
            attrs = None
    if isinstance(attrs, list):
        attrs = {"crafts": attrs}
    if not isinstance(attrs, dict):
        attrs = None
    return MerchOut(
        id=merch.id,
        ip_id=merch.ip_id,
        ip_name=merch.ip.name if merch.ip else "",
        name=merch.name,
        category=merch.category,
        official_price=float(merch.official_price) if merch.official_price else None,
        release_date=merch.release_date,
        release_method=merch.release_method,
        is_discontinued=bool(merch.is_discontinued),
        attributes=attrs,
        image_url=merch.image_url,
        source_platform=merch.source_platform,
        source_url=merch.source_url,
        crafts=crafts,
        created_at=merch.created_at,
    )


@router.get("/merch")
def list_merch(
    ip_id: int | None = Query(None, description="IP ID"),
    category: str | None = Query(None, description="品类: 吧唧/色纸/亚克力立牌/..."),
    craft: str | None = Query(None, description="工艺筛选"),
    is_discontinued: int | None = Query(None, description="是否绝版 0/1"),
    search: str | None = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """周边列表，支持多维度筛选"""
    q = db.query(Merch).filter(Merch.status == 'active')

    if ip_id:
        q = q.filter(Merch.ip_id == ip_id)
    if category:
        q = q.filter(Merch.category == category)
    if is_discontinued is not None:
        q = q.filter(Merch.is_discontinued == is_discontinued)
    if search:
        q = q.filter(Merch.name.contains(search))

    # 工艺筛选通过关联表
    if craft:
        q = q.join(MerchCraft, Merch.id == MerchCraft.merch_id)\
             .join(CraftTag, MerchCraft.craft_id == CraftTag.id)\
             .filter(CraftTag.name == craft)

    total = q.count()
    items = q.order_by(Merch.release_date.desc(), Merch.id.desc())\
             .offset((page - 1) * size).limit(size).all()

    return {
        "items": [_build_merch_out(m) for m in items],
        "total": total,
        "page": page,
        "size": size,
    }


@router.get("/merch/{merch_id}", response_model=MerchDetail)
def get_merch(merch_id: int, db: Session = Depends(get_db)):
    """获取单个周边详情"""
    merch = db.query(Merch).filter(Merch.id == merch_id).first()
    if not merch:
        raise HTTPException(status_code=404, detail="周边不存在")

    crafts = [c.name for c in merch.crafts] if merch.crafts else []
    import json
    attrs = merch.attributes
    if isinstance(attrs, str):
        try: attrs = json.loads(attrs)
        except: attrs = {}
    if isinstance(attrs, list): attrs = {"crafts": attrs}
    if not isinstance(attrs, dict): attrs = None
    return MerchDetail(
        id=merch.id,
        ip_id=merch.ip_id,
        ip_name=merch.ip.name if merch.ip else "",
        name=merch.name,
        category=merch.category,
        official_price=float(merch.official_price) if merch.official_price else None,
        release_date=merch.release_date,
        release_method=merch.release_method,
        is_discontinued=bool(merch.is_discontinued),
        attributes=attrs,
        image_url=merch.image_url,
        source_platform=merch.source_platform,
        source_url=merch.source_url,
        crafts=crafts,
        created_at=merch.created_at,
        updated_at=merch.updated_at,
    )


@router.get("/crafts", response_model=list[CraftOut])
def list_crafts(db: Session = Depends(get_db)):
    """获取所有工艺标签"""
    return db.query(CraftTag).order_by(CraftTag.name).all()


@router.get("/stats", response_model=StatsOut)
def get_stats(db: Session = Depends(get_db)):
    """首页统计数据"""
    from datetime import datetime, timedelta

    total_merch = db.query(func.count(Merch.id)).filter(Merch.status == 'active').scalar()
    total_ip = db.query(func.count(IP.id)).scalar()
    total_crafts = db.query(func.count(CraftTag.id)).scalar()

    # IP 分布
    ip_dist = db.query(
        IP.name, IP.id, func.count(Merch.id).label('cnt')
    ).join(Merch, Merch.ip_id == IP.id)\
     .filter(Merch.status == 'active')\
     .group_by(IP.id).order_by(func.count(Merch.id).desc()).all()

    # 品类分布
    cat_dist = db.query(
        Merch.category, func.count(Merch.id).label('cnt')
    ).filter(Merch.status == 'active')\
     .group_by(Merch.category).order_by(func.count(Merch.id).desc()).all()

    # 近 7 天新增
    recent = 0
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent = db.query(func.count(Merch.id)).filter(
        Merch.status == 'active', Merch.created_at >= week_ago
    ).scalar()

    return StatsOut(
        total_merch=total_merch,
        total_ip=total_ip,
        total_crafts=total_crafts,
        ip_distribution=[{"ip_name": r[0], "ip_id": r[1], "count": r[2]} for r in ip_dist],
        category_distribution=[{"category": r[0], "count": r[1]} for r in cat_dist],
        recent_updates=recent,
    )
