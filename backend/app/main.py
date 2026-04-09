"""FastAPI 应用入口"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api import scripts, videos, materials, templates, publishing, analytics, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(scripts.router, prefix="/api/v1/scripts", tags=["脚本生成"])
app.include_router(videos.router, prefix="/api/v1/videos", tags=["视频剪辑"])
app.include_router(materials.router, prefix="/api/v1/materials", tags=["素材中心"])
app.include_router(templates.router, prefix="/api/v1/templates", tags=["模板管理"])
app.include_router(publishing.router, prefix="/api/v1/publishing", tags=["发布管理"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["数据看板"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}

from app.middleware.tenant import TenantMiddleware
app.add_middleware(TenantMiddleware)
