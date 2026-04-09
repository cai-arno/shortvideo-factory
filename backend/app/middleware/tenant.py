"""租户中间件 - 自动注入 tenant_id 到 request.state"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.security import decode_token


class TenantMiddleware(BaseHTTPMiddleware):
    """租户上下文中间件

    从 Authorization Header 解析 JWT，自动注入:
    - request.state.user_id
    - request.state.tenant_id
    - request.state.role
    """

    EXEMPT_PATHS = [
        "/health",
        "/api/v1/auth/phone/send-code",
        "/api/v1/auth/phone/login",
        "/api/v1/auth/wechat/code2session",
        "/docs",
        "/redoc",
        "/openapi.json",
    ]

    async def dispatch(self, request: Request, call_next) -> Response:
        # 放行免认证路径
        if any(request.url.path.startswith(p) for p in self.EXEMPT_PATHS):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return Response(content='{"detail":"Missing or invalid Authorization header"}', 
                          status_code=401, media_type="application/json")

        token = auth_header[7:]
        token_data = decode_token(token)

        if not token_data:
            return Response(content='{"detail":"Invalid or expired token"}',
                          status_code=401, media_type="application/json")

        # 注入到 request.state，供后续路由使用
        request.state.user_id = token_data.user_id
        request.state.tenant_id = token_data.tenant_id
        request.state.role = token_data.role

        return await call_next(request)
