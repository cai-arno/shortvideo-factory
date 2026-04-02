"""发布管理 API"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.publishing import PublishRecord, Platform, PublishStatus
from app.schemas.publishing import (
    PublishRequest,
    PublishResponse,
    PublishListResponse,
)
from app.services.publisher import publish_task

router = APIRouter()


@router.post("", response_model=PublishResponse)
async def create_publish(
    req: PublishRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """创建发布任务"""
    record = PublishRecord(
        video_id=req.video_id,
        platform=req.platform,
        status=PublishStatus.PENDING,
        scheduled_at=req.scheduled_at,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)

    if not req.scheduled_at:
        record.status = PublishStatus.PUBLISHING
        await session.commit()
        background_tasks.add_task(publish_task, record.id)

    return record


@router.get("", response_model=PublishListResponse)
async def list_publish_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    platform: Optional[Platform] = None,
    status: Optional[PublishStatus] = None,
    session: AsyncSession = Depends(get_session),
):
    """获取发布记录列表"""
    query = session.query(PublishRecord)
    if platform:
        query = query.where(PublishRecord.platform == platform)
    if status:
        query = query.where(PublishRecord.status == status)

    total = await session.scalar(query.count())
    records = await session.execute(
        query.offset((page - 1) * page_size).limit(page_size).order_by(PublishRecord.created_at.desc())
    )
    items = records.scalars().all()

    return PublishListResponse(
        items=[PublishResponse.model_validate(r) for r in items],
        total=total,
    )


@router.get("/{record_id}", response_model=PublishResponse)
async def get_publish_record(record_id: int, session: AsyncSession = Depends(get_session)):
    """获取发布记录"""
    record = await session.get(PublishRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record
