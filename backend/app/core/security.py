"""JWT 认证工具"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.config import settings


class TokenData(BaseModel):
    """Token携带的数据"""
    user_id: int
    tenant_id: int
    role: str


class TokenPayload(BaseModel):
    """完整Payload"""
    sub: str  # user_id
    tenant_id: int
    role: str
    exp: datetime
    iat: datetime


def create_access_token(user_id: int, tenant_id: int, role: str, expires_delta: Optional[timedelta] = None) -> str:
    """生成JWT Access Token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),
        "tenant_id": tenant_id,
        "role": role,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[TokenData]:
    """解码JWT Token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return TokenData(
            user_id=int(payload["sub"]),
            tenant_id=payload["tenant_id"],
            role=payload["role"],
        )
    except JWTError:
        return None
