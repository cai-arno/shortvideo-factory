"""模板数据模型"""
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field


class TemplateType(str, Enum):
    CAPCUT = "capcut"        # 剪映模板
    SUBTITLE = "subtitle"    # 字幕样式
    COVER = "cover"          # 封面模板
    TRANSITION = "transition"  # 转场效果


class Template(SQLModel, table=True):
    """模板表"""
    __tablename__ = "templates"

    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: Optional[int] = Field(default=None, foreign_key="tenants.id", index=True)
    name: str = Field(max_length=200)
    template_type: TemplateType
    file_path: str = Field(default="")         # 模板文件路径
    thumbnail_url: str = Field(default="")     # 预览图
    config: str = Field(default="{}")          # JSON 配置
    script_type: str = Field(default="")      # 适用的脚本类型
    tags: str = Field(default="[]")            # 标签
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
