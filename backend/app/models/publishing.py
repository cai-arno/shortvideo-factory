"""发布渠道数据模型"""
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field


class Platform(str, Enum):
    DOUYIN = "douyin"      # 抖音
    KUAISHOU = "kuaishou"  # 快手
    WECHAT = "wechat"      # 视频号
    XIGUA = "xigua"        # 西瓜视频
    BILIBILI = "bilibili"  # B站


class PublishStatus(str, Enum):
    DRAFT = "draft"        # 草稿
    PENDING = "pending"    # 待发布
    PUBLISHING = "publishing"  # 发布中
    PUBLISHED = "published"    # 已发布
    FAILED = "failed"          # 失败


class PublishRecord(SQLModel, table=True):
    """发布记录表"""
    __tablename__ = "publish_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: Optional[int] = Field(default=None, foreign_key="tenants.id", index=True)
    video_id: int = Field(foreign_key="videos.id")
    platform: Platform
    status: PublishStatus = Field(default=PublishStatus.DRAFT)
    platform_video_id: str = Field(default="")  # 平台返回的视频ID
    platform_url: str = Field(default="")       # 平台视频URL
    scheduled_at: Optional[datetime] = Field(default=None)  # 定时发布时间
    published_at: Optional[datetime] = Field(default=None)
    error_message: str = Field(default="")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
