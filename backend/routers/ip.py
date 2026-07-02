# ============================================
# IP 相关 API 路由
# ============================================
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models import IP, Merch
from backend.schemas import IPOut, IPDetail

router = APIRouter(prefix="/api/ip", tags=["IP"])


@router.get("/ip", response_model=dict)
def list_ips(
    category: str | None = Query(None, description="分类筛选"),
    search: str | None = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(12, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db),
):
    """获取 IP 列表，支持分类筛选、搜索和分页"""
    q = db.query(IP)

    if category:
        q = q.filter(IP.category == category)
    if search:
        q = q.filter(IP.name.contains(search))

    total = q.count()
    ips = q.order_by(IP.name).offset((page - 1) * size).limit(size).all()

    items = []
    for ip in ips:
        count = db.query(func.count(Merch.id)).filter(
            Merch.ip_id == ip.id, Merch.status == 'active'
        ).scalar()
        item = IPOut(
            id=ip.id,
            name=ip.name,
            aliases=ip.aliases or [],
            category=ip.category,
            cover_url=ip.cover_url,
            description=ip.description,
            merch_count=count,
            created_at=ip.created_at,
            updated_at=ip.updated_at,
        )
        items.append(item)
    return {"items": items, "total": total, "page": page, "size": size}


@router.get("/ip/{ip_id}", response_model=IPDetail)
def get_ip(ip_id: int, db: Session = Depends(get_db)):
    """获取单个 IP 详情"""
    ip = db.query(IP).filter(IP.id == ip_id).first()
    if not ip:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="IP not found")

    count = db.query(func.count(Merch.id)).filter(
        Merch.ip_id == ip.id, Merch.status == 'active'
    ).scalar()

    return IPDetail(
        id=ip.id,
        name=ip.name,
        aliases=ip.aliases or [],
        category=ip.category,
        cover_url=ip.cover_url,
        description=ip.description,
        merch_count=count,
        created_at=ip.created_at,
        updated_at=ip.updated_at,
    )


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    """获取现有的 IP 分类列表"""
    results = db.query(IP.category, func.count(IP.id)).group_by(IP.category).all()
    return [{"name": r[0], "count": r[1]} for r in results if r[0]]
