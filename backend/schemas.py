# ============================================
# Pydantic 请求/响应模型
# ============================================
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


# ── IP ──
class IPBase(BaseModel):
    name: str
    aliases: Optional[list[str]] = None
    category: Optional[str] = None
    cover_url: Optional[str] = None
    description: Optional[str] = None


class IPOut(IPBase):
    id: int
    merch_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IPDetail(IPOut):
    pass


# ── 周边 ──
class MerchOut(BaseModel):
    id: int
    ip_id: int
    ip_name: str = ""
    name: str
    category: Optional[str] = None
    official_price: Optional[float] = None
    release_date: Optional[date] = None
    release_method: Optional[str] = None
    is_discontinued: bool = False
    attributes: Optional[dict | list] = None  # 允许 dict 或 list
    image_url: Optional[str] = None
    source_platform: Optional[str] = None
    source_url: Optional[str] = None
    crafts: list[str] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class MerchDetail(MerchOut):
    updated_at: datetime


class MerchListResult(BaseModel):
    items: list[MerchOut]
    total: int
    page: int
    size: int


# ── 工艺 ──
class CraftOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


# ── 统计 ──
class StatsOut(BaseModel):
    total_merch: int
    total_ip: int
    total_crafts: int
    ip_distribution: list[dict]       # [{ip_name, ip_id, count}]
    category_distribution: list[dict] # [{category, count}]
    recent_updates: int               # 近7天新增


# ── 审核后台 ──
class ReviewQueueItem(BaseModel):
    id: int
    post_raw_id: int
    post_title: str
    post_content: str
    post_url: str
    author_name: str
    post_time: Optional[datetime]
    ip_name_hint: Optional[str]
    ip_id: Optional[int]
    merch_name: Optional[str]
    category: Optional[str]
    category_hint: Optional[str]
    official_price: Optional[float]
    # 帖子所有图片
    images: Optional[list[str]] = None
    release_date: Optional[date]
    release_method: Optional[str]
    craft_keywords: Optional[list]
    attributes: Optional[dict]
    confidence: Optional[float]
    need_review: bool
    review_status: str

    model_config = {"from_attributes": True}


class ReviewAction(BaseModel):
    """审核操作请求体"""
    ip_id: Optional[int] = None
    ip_name: Optional[str] = None
    merch_name: Optional[str] = None
    category: Optional[str] = None
    official_price: Optional[float] = None
    release_date: Optional[str] = None   # 改为 str，前端可能传空字符串
    release_method: Optional[str] = None
    craft_keywords: Optional[list[str]] = None
    attributes: Optional[dict] = None
    # 新增：多品类 + 对应价格
    categories: Optional[list[dict]] = None  # [{"category":"吧唧","price":38},{"category":"色纸","price":58}]
    release_methods: Optional[list[str]] = None  # ["通贩","场售"]


class ReviewQueueResult(BaseModel):
    """审核队列分页响应"""
    items: list[ReviewQueueItem]
    total: int
    page: int
    size: int
    total_pages: int
