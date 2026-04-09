"""素材数据模型"""
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field


class MaterialType(str, Enum):
    VIDEO = "video"          # 视频素材
    IMAGE = "image"          # 图片素材
    AUDIO = "audio"          # 音频/BGM
    VOICEOVER = "voiceover"  # TTS配音
    FONT = "font"            # 字体


class Material(SQLModel, table=True):
    """素材表"""
    __tablename__ = "materials"

    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: Optional[int] = Field(default=None, foreign_key="tenants.id", index=True)
    name: str = Field(max_length=200)
    material_type: MaterialType
    file_path: str = Field(default="")          # 存储路径
    oss_url: str = Field(default="")           # CDN URL
    thumbnail_url: str = Field(default="")     # 缩略图
    duration: float = Field(default=0)         # 时长(秒)，视频/音频用
    file_size: int = Field(default=0)          # 文件大小
    width: int = Field(default=0)              # 宽度，图片/视频用
    height: int = Field(default=0)             # 高度
    tags: str = Field(default="[]")            # JSON tags array
    category: str = Field(default="")         # 分类
    created_at: datetime = Field(default_factory=datetime.utcnow)
