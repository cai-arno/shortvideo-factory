"""多租户数据模型"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Dict, Any
from sqlmodel import SQLModel, Field, JSON, JSON


class TenantPlan(str, Enum):
    FREE = "free"
    PRO = "pro"
    TEAM = "team"
    ENTERPRISE = "enterprise"


class MemberRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class MemberStatus(str, Enum):
    ACTIVE = "active"
    INVITED = "invited"
    DISABLED = "disabled"


class Tenant(SQLModel, table=True):
    """租户表"""
    __tablename__ = "tenants"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    plan: TenantPlan = Field(default=TenantPlan.FREE)
    settings: Dict[str, Any] = Field(default_factory=dict, sa_type=JSON)  # JSON
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class User(SQLModel, table=True):
    """用户表"""
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    phone: str = Field(max_length=20, unique=True, index=True)
    union_id: Optional[str] = Field(default=None, index=True)  # 微信UnionID
    nickname: str = Field(default="", max_length=100)
    avatar: str = Field(default="", max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: datetime = Field(default_factory=datetime.utcnow)


class TenantMember(SQLModel, table=True):
    """租户成员表"""
    __tablename__ = "tenant_members"

    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenants.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    role: MemberRole = Field(default=MemberRole.VIEWER)
    status: MemberStatus = Field(default=MemberStatus.ACTIVE)
    invited_by: Optional[int] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        unique_together = [("tenant_id", "user_id")]


# ---- 权限矩阵 ----

# 资源类型
RESOURCE_SCRIPT = "script"
RESOURCE_VIDEO = "video"
RESOURCE_TEMPLATE = "template"
RESOURCE_TASK = "task"
RESOURCE_MATERIAL = "material"
RESOURCE_MEMBER = "member"

# 操作类型
ACTION_CREATE = "create"
ACTION_READ = "read"
ACTION_UPDATE = "update"
ACTION_DELETE = "delete"
ACTION_SHARE = "share"
ACTION_PUBLISH = "publish"
ACTION_INVITE = "invite"

# 权限矩阵：role -> {resource: {action: True}}
ROLE_PERMISSIONS = {
    MemberRole.OWNER: {
        RESOURCE_SCRIPT: {ACTION_CREATE, ACTION_READ, ACTION_UPDATE, ACTION_DELETE, ACTION_SHARE, ACTION_PUBLISH},
        RESOURCE_VIDEO: {ACTION_CREATE, ACTION_READ, ACTION_UPDATE, ACTION_DELETE, ACTION_SHARE, ACTION_PUBLISH},
        RESOURCE_TEMPLATE: {ACTION_CREATE, ACTION_READ, ACTION_UPDATE, ACTION_DELETE, ACTION_SHARE},
        RESOURCE_TASK: {ACTION_CREATE, ACTION_READ, ACTION_UPDATE, ACTION_DELETE},
        RESOURCE_MATERIAL: {ACTION_CREATE, ACTION_READ, ACTION_UPDATE, ACTION_DELETE, ACTION_SHARE},
        RESOURCE_MEMBER: {ACTION_CREATE, ACTION_READ, ACTION_UPDATE, ACTION_DELETE, ACTION_INVITE},
    },
    MemberRole.ADMIN: {
        RESOURCE_SCRIPT: {ACTION_CREATE, ACTION_READ, ACTION_UPDATE, ACTION_DELETE, ACTION_SHARE, ACTION_PUBLISH},
        RESOURCE_VIDEO: {ACTION_CREATE, ACTION_READ, ACTION_UPDATE, ACTION_DELETE, ACTION_SHARE, ACTION_PUBLISH},
        RESOURCE_TEMPLATE: {ACTION_CREATE, ACTION_READ, ACTION_UPDATE, ACTION_DELETE, ACTION_SHARE},
        RESOURCE_TASK: {ACTION_CREATE, ACTION_READ, ACTION_UPDATE, ACTION_DELETE},
        RESOURCE_MATERIAL: {ACTION_CREATE, ACTION_READ, ACTION_UPDATE, ACTION_DELETE, ACTION_SHARE},
        RESOURCE_MEMBER: {ACTION_CREATE, ACTION_READ, ACTION_UPDATE, ACTION_DELETE, ACTION_INVITE},
    },
    MemberRole.EDITOR: {
        RESOURCE_SCRIPT: {ACTION_CREATE, ACTION_READ, ACTION_UPDATE, ACTION_PUBLISH},
        RESOURCE_VIDEO: {ACTION_CREATE, ACTION_READ, ACTION_UPDATE, ACTION_PUBLISH},
        RESOURCE_TEMPLATE: {ACTION_READ},
        RESOURCE_TASK: {ACTION_CREATE, ACTION_READ, ACTION_UPDATE},
        RESOURCE_MATERIAL: {ACTION_CREATE, ACTION_READ, ACTION_UPDATE},
        RESOURCE_MEMBER: {ACTION_READ},
    },
    MemberRole.VIEWER: {
        RESOURCE_SCRIPT: {ACTION_READ},
        RESOURCE_VIDEO: {ACTION_READ},
        RESOURCE_TEMPLATE: {ACTION_READ},
        RESOURCE_TASK: {ACTION_READ},
        RESOURCE_MATERIAL: {ACTION_READ},
        RESOURCE_MEMBER: {ACTION_READ},
    },
}


def has_permission(role: MemberRole, resource: str, action: str) -> bool:
    """检查角色是否有指定资源+操作的权限"""
    return action in ROLE_PERMISSIONS.get(role, {}).get(resource, set())
