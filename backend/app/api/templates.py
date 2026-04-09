"""模板管理 API"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.template import Template, TemplateType
from app.schemas.template import TemplateResponse, TemplateListResponse

router = APIRouter()


@router.get("", response_model=TemplateListResponse)
async def list_templates(
    template_type: Optional[TemplateType] = None,
    script_type: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    """获取模板列表"""
    query = select(Template).where(Template.is_active == True)
    if template_type:
        query = query.where(Template.template_type == template_type)
    if script_type:
        query = query.where(Template.script_type == script_type)

    templates = await session.execute(query.order_by(Template.created_at.desc()))
    items = templates.scalars().all()

    return TemplateListResponse(
        items=[TemplateResponse.model_validate(t) for t in items],
        total=len(items),
    )


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: int, session: AsyncSession = Depends(get_session)):
    """获取单个模板"""
    template = await session.get(Template, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template
