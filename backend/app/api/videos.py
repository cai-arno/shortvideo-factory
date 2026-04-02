"""视频剪辑 API"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.video import Video, VideoStatus
from app.models.script import Script
from app.schemas.video import (
    VideoCreateRequest,
    VideoRenderRequest,
    VideoResponse,
    VideoListResponse,
)
from app.services.video_renderer import render_video_task

router = APIRouter()


@router.post("", response_model=VideoResponse)
async def create_video(
    req: VideoCreateRequest,
    session: AsyncSession = Depends(get_session),
):
    """创建视频剪辑任务"""
    # 获取脚本标题作为视频标题
    title = f"视频_{req.script_id}"
    script = await session.get(Script, req.script_id)
    if script:
        title = f"视频_{script.id}_{script.title[:20]}"

    video = Video(
        title=title,
        script_id=req.script_id,
        template_id=req.template_id,
        status=VideoStatus.PENDING,
    )
    session.add(video)
    await session.commit()
    await session.refresh(video)
    return video


@router.post("/render", response_model=VideoResponse)
async def render_video(
    req: VideoRenderRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """提交视频渲染"""
    video = await session.get(Video, req.video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    video.status = VideoStatus.RENDERING
    await session.commit()

    background_tasks.add_task(render_video_task, req.video_id)
    return video


@router.get("", response_model=VideoListResponse)
async def list_videos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[VideoStatus] = None,
    session: AsyncSession = Depends(get_session),
):
    """获取视频列表"""
    query = session.query(Video)
    if status:
        query = query.where(Video.status == status)

    total = await session.scalar(query.count())
    videos = await session.execute(
        query.offset((page - 1) * page_size).limit(page_size).order_by(Video.created_at.desc())
    )
    items = videos.scalars().all()

    return VideoListResponse(
        items=[VideoResponse.model_validate(v) for v in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(video_id: int, session: AsyncSession = Depends(get_session)):
    """获取单个视频"""
    video = await session.get(Video, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video
