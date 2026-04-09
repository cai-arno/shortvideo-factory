"""视频剪辑数据模型"""
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field


class VideoStatus(str, Enum):
    PENDING = "pending"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"


class Video(SQLModel, table=True):
    """视频表"""
    __tablename__ = "videos"

    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: Optional[int] = Field(default=None, foreign_key="tenants.id", index=True)
    title: str = Field(max_length=200)
    script_id: Optional[int] = Field(default=None, foreign_key="scripts.id")
    template_id: Optional[int] = Field(default=None, foreign_key="templates.id")
    output_path: str = Field(default="")        # 渲染输出路径
    thumbnail_path: str = Field(default="")     # 封面图路径
    duration: int = Field(default=0)            # 视频时长(秒)
    width: int = Field(default=1080)
    height: int = Field(default=1920)
    file_size: int = Field(default=0)           # 文件大小(bytes)
    status: VideoStatus = Field(default=VideoStatus.PENDING)
    progress: int = Field(default=0)            # 渲染进度 0-100
    error_message: str = Field(default="")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
