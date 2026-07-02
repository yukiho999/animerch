# ============================================
# SQLAlchemy ORM 模型
# ============================================
from datetime import datetime

from sqlalchemy import (
    Column, BigInteger, String, Text, DECIMAL, Date, DateTime,
    Enum, JSON, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship

from backend.database import Base


# 品类枚举
MERCH_CATEGORY = (
    '吧唧', '色纸', '亚克力立牌', '粘土人',
    '挂件', '文件夹', '海报', '立牌', '其他'
)
# 发售方式枚举
RELEASE_METHOD = ('通贩', '场贩', '受注', '限定', '抽选', '未知')
# 帖子状态枚举
POST_STATUS = ('pending', 'parsed', 'approved', 'rejected', 'error')
# 审核状态枚举
REVIEW_STATUS = ('pending', 'approved', 'rejected', 'edited')
# 展示状态枚举
DISPLAY_STATUS = ('active', 'hidden')


class IP(Base):
    __tablename__ = 'ip'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    aliases = Column(JSON)
    category = Column(String(50))
    cover_url = Column(String(1000))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    merchs = relationship('Merch', back_populates='ip')


class Merch(Base):
    __tablename__ = 'merch'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ip_id = Column(BigInteger, ForeignKey('ip.id'), nullable=False)
    name = Column(String(500), nullable=False)
    category = Column(Enum(*MERCH_CATEGORY))
    official_price = Column(DECIMAL(10, 2))
    release_date = Column(Date)
    release_method = Column(Enum(*RELEASE_METHOD), default='未知')
    is_discontinued = Column(TINYINT(1), default=0)
    attributes = Column(JSON)
    image_url = Column(String(2000))
    source_platform = Column(String(50), default='weibo')
    source_url = Column(String(2000))
    original_post_id = Column(BigInteger, ForeignKey('post_raw.id'))
    status = Column(Enum(*DISPLAY_STATUS), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    ip = relationship('IP', back_populates='merchs')
    original_post = relationship('PostRaw', backref='merch')
    crafts = relationship('CraftTag', secondary='merch_craft', backref='merchs')

    __table_args__ = (
        Index('idx_merch_ip', 'ip_id'),
        Index('idx_merch_category', 'category'),
        Index('idx_merch_release_date', 'release_date'),
        Index('idx_merch_discontinued', 'is_discontinued'),
        Index('idx_merch_status', 'status'),
    )


class CraftTag(Base):
    __tablename__ = 'craft_tag'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)


class MerchCraft(Base):
    __tablename__ = 'merch_craft'

    merch_id = Column(BigInteger, ForeignKey('merch.id', ondelete='CASCADE'), primary_key=True)
    craft_id = Column(BigInteger, ForeignKey('craft_tag.id'), primary_key=True)


class PostRaw(Base):
    __tablename__ = 'post_raw'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    platform = Column(String(50), nullable=False, default='weibo')
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
    status = Column(Enum(*POST_STATUS), default='pending')
    error_msg = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('platform', 'post_id', name='uk_post'),
        Index('idx_post_status', 'status'),
        Index('idx_post_time', 'post_time'),
    )


class MerchPost(Base):
    __tablename__ = 'merch_post'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    post_raw_id = Column(BigInteger, ForeignKey('post_raw.id'), nullable=False, unique=True)
    ip_name_hint = Column(String(200))
    ip_id = Column(BigInteger, ForeignKey('ip.id'))
    merch_name = Column(String(500))
    category_hint = Column(String(50))
    category = Column(Enum(*MERCH_CATEGORY))
    official_price = Column(DECIMAL(10, 2))
    release_date = Column(Date)
    release_method = Column(Enum(*RELEASE_METHOD), default='未知')
    craft_keywords = Column(JSON)
    attributes = Column(JSON)
    confidence = Column(DECIMAL(3, 2), default=0.00)
    need_review = Column(TINYINT(1), default=1)
    review_status = Column(Enum(*REVIEW_STATUS), default='pending')
    reviewed_by = Column(String(50))
    reviewed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    post_raw = relationship('PostRaw', backref='merch_post')
    matched_ip = relationship('IP', backref='merch_posts')

    __table_args__ = (
        Index('idx_mp_review_status', 'review_status'),
        Index('idx_mp_ip_id', 'ip_id'),
    )
