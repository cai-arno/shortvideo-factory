"""脚本生成 API"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.script import Script, ScriptStatus, ScriptType
from app.schemas.script import (
    ScriptGenerateRequest,
    ScriptResponse,
    ScriptListResponse,
)
from app.services.script_generator import ScriptGenerator

router = APIRouter()


@router.post("/generate", response_model=ScriptResponse)
async def generate_script(
    req: ScriptGenerateRequest,
    session: AsyncSession = Depends(get_session),
):
    """AI 生成脚本"""
    generator = ScriptGenerator(session)

    try:
        script = await generator.generate(
            topic=req.topic,
            script_type=req.script_type,
            quantity=req.quantity,
            style=req.style,
        )
        return script
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=ScriptListResponse)
async def list_scripts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[ScriptStatus] = None,
    script_type: Optional[ScriptType] = None,
    session: AsyncSession = Depends(get_session),
):
    """获取脚本列表"""
    query = select(Script)
    if status:
        query = query.where(Script.status == status)
    if script_type:
        query = query.where(Script.script_type == script_type)

    total = await session.scalar(select(func.count()).select_from(query.subquery()))
    scripts = await session.execute(
        query.offset((page - 1) * page_size).limit(page_size).order_by(Script.created_at.desc())
    )
    items = scripts.scalars().all()

    return ScriptListResponse(
        items=[ScriptResponse.model_validate(s) for s in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{script_id}", response_model=ScriptResponse)
async def get_script(script_id: int, session: AsyncSession = Depends(get_session)):
    """获取单个脚本"""
    script = await session.get(Script, script_id)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    return script


@router.delete("/{script_id}")
async def delete_script(script_id: int, session: AsyncSession = Depends(get_session)):
    """删除脚本"""
    script = await session.get(Script, script_id)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    await session.delete(script)
    await session.commit()
    return {"message": "deleted"}
