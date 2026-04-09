"""认证 API - 手机号登录 / 微信登录 / Token刷新"""
import random
import re
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_session
from app.core.security import create_access_token, TokenData
from app.models.tenant import User, Tenant, TenantMember, MemberRole, MemberStatus
from app.schemas.auth import (
    SendCodeRequest, SendCodeResponse,
    PhoneLoginRequest, LoginResponse, UserInfo, TenantInfo,
    SwitchTenantRequest, SwitchTenantResponse,
)

router = APIRouter(tags=["认证"])

# 模拟验证码存储（生产环境用Redis）
_mock_codes: dict[str, tuple[str, datetime]] = {}


def _generate_code() -> str:
    """生成6位数字验证码"""
    return str(random.randint(100000, 999999))


def _is_code_valid(phone: str, code: str) -> bool:
    """验证验证码是否有效"""
    if phone not in _mock_codes:
        return False
    stored_code, expire_at = _mock_codes[phone]
    return stored_code == code and datetime.utcnow() < expire_at


def _clear_code(phone: str):
    _mock_codes.pop(phone, None)


def _get_user_tenants(user_id: int, session: AsyncSession):
    """获取用户所属的所有租户"""
    # TODO: use selectinload for members
    pass


@router.post("/phone/send-code", response_model=SendCodeResponse)
async def send_code(req: SendCodeRequest, session: AsyncSession = Depends(get_session)):
    """发送手机验证码（模拟）"""
    # 验证手机号格式
    if not re.match(r"^1[3-9]\d{9}$", req.phone):
        raise HTTPException(status_code=400, detail="手机号格式不正确")

    code = _generate_code()
    # 模拟：有效期5分钟
    _mock_codes[req.phone] = (code, datetime.utcnow() + timedelta(minutes=5))

    # 实际项目这里调用短信服务（阿里云/腾讯云）
    print(f"[模拟验证码] 手机号 {req.phone} 的验证码是: {code}")

    return SendCodeResponse(expire_in=300)


@router.post("/phone/login", response_model=LoginResponse)
async def phone_login(req: PhoneLoginRequest, session: AsyncSession = Depends(get_session)):
    """手机号登录"""
    # 验证验证码
    if not _is_code_valid(req.phone, req.code):
        raise HTTPException(status_code=400, detail="验证码错误或已过期")

    _clear_code(req.phone)

    # 查找或创建用户
    result = await session.execute(select(User).where(User.phone == req.phone))
    user = result.scalar_one_or_none()

    if not user:
        # 新用户：自动创建并加入默认租户
        user = User(phone=req.phone, nickname=req.phone[-4:])
        session.add(user)
        await session.flush()  # 获取 user.id

        # 创建用户第一个租户（个人版）
        tenant = Tenant(name=f"{user.nickname}的团队", plan="free")
        session.add(tenant)
        await session.flush()

        # 自动加入该租户
        member = TenantMember(
            tenant_id=tenant.id,
            user_id=user.id,
            role=MemberRole.OWNER,
            status=MemberStatus.ACTIVE,
        )
        session.add(member)

    # 更新最后登录时间
    user.last_login_at = datetime.utcnow()

    # 获取用户所属租户列表
    member_result = await session.execute(
        select(TenantMember, Tenant)
        .join(Tenant, TenantMember.tenant_id == Tenant.id)
        .where(TenantMember.user_id == user.id, TenantMember.status == MemberStatus.ACTIVE)
    )
    member_rows = member_result.all()

    if not member_rows:
        raise HTTPException(status_code=500, detail="用户无所属租户，请联系管理员")

    tenants = [
        TenantInfo(id=t.id, name=t.name, plan=t.plan, role=m.role.value)
        for m, t in member_rows
    ]
    # 默认使用第一个租户
    primary = member_rows[0]
    current_tenant_id = primary[0].tenant_id
    current_role = primary[0].role

    # 生成Token
    access_token = create_access_token(
        user_id=user.id,
        tenant_id=current_tenant_id,
        role=current_role.value,
    )

    await session.commit()

    return LoginResponse(
        access_token=access_token,
        user=UserInfo.model_validate(user),
        tenants=tenants,
        current_tenant_id=current_tenant_id,
    )


@router.post("/tenant/switch", response_model=SwitchTenantResponse)
async def switch_tenant(
    req: SwitchTenantRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """切换当前租户"""
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="未认证")

    # 验证用户是否属于该租户
    member_result = await session.execute(
        select(TenantMember).where(
            TenantMember.user_id == user_id,
            TenantMember.tenant_id == req.tenant_id,
            TenantMember.status == MemberStatus.ACTIVE,
        )
    )
    member = member_result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=403, detail="无权访问该租户")

    # 生成新Token
    new_token = create_access_token(
        user_id=user_id,
        tenant_id=req.tenant_id,
        role=member.role.value,
    )

    return SwitchTenantResponse(
        access_token=new_token,
        tenant_id=req.tenant_id,
        role=member.role.value,
    )


@router.get("/me")
async def get_current_user(request: Request):
    """获取当前登录用户信息"""
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="未认证")
    return {
        "user_id": user_id,
        "tenant_id": request.state.tenant_id,
        "role": request.state.role,
    }
