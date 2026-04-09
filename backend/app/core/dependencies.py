"""认证与权限依赖"""
from typing import Optional
from fastapi import Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.tenant import (
    has_permission, MemberRole, User, TenantMember, MemberStatus,
)
from app.core.security import TokenData, decode_token


class CurrentUser:
    """当前登录用户（从 request.state 提取）"""
    def __init__(self, request: Request):
        self.user_id: int = getattr(request.state, "user_id", None)
        self.tenant_id: int = getattr(request.state, "tenant_id", None)
        self.role: str = getattr(request.state, "role", None)

    def require_auth(self):
        if not self.user_id:
            raise HTTPException(status_code=401, detail="未认证")
        return self


def get_current_user(request: Request) -> CurrentUser:
    """FastAPI 依赖：获取当前用户"""
    return CurrentUser(request)


def require_permission(resource: str, action: str):
    """权限校验装饰器（用于 FastAPI 路由）"""
    def dep(request: Request = Depends(get_current_user)):
        cu = CurrentUser(request)
        cu.require_auth()
        if not has_permission(MemberRole(cu.role), resource, action):
            raise HTTPException(status_code=403, detail=f"无权执行 {action} {resource}")
        return cu
    return dep
