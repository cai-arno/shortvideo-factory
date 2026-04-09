"""认证 Schema"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ---- 请求 ----

class SendCodeRequest(BaseModel):
    phone: str = Field(..., min_length=11, max_length=20)


class PhoneLoginRequest(BaseModel):
    phone: str = Field(..., min_length=11, max_length=20)
    code: str = Field(..., min_length=4, max_length=6)


class SwitchTenantRequest(BaseModel):
    tenant_id: int


# ---- 响应 ----

class TenantInfo(BaseModel):
    id: int
    name: str
    plan: str
    role: str

    class Config:
        from_attributes = True


class UserInfo(BaseModel):
    id: int
    phone: str
    nickname: str
    avatar: str
    created_at: datetime

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo
    tenants: List[TenantInfo]
    current_tenant_id: int


class SendCodeResponse(BaseModel):
    message: str = "验证码已发送"
    expire_in: int = 300  # 5分钟


class SwitchTenantResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    tenant_id: int
    role: str
