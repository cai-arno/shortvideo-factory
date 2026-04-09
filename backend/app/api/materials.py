"""素材管理 API"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.config import settings
from app.models.material import Material, MaterialType
from app.schemas.material import (
    MaterialUploadResponse,
    MaterialResponse,
    MaterialListResponse,
)
from app.services.material_uploader import MaterialUploader

router = APIRouter()


@router.post("/upload", response_model=MaterialUploadResponse)
async def upload_material(
    file: UploadFile = File(...),
    material_type: MaterialType = Query(...),
    name: Optional[str] = None,
    category: str = Query(""),
    tags: str = Query("[]"),
    session: AsyncSession = Depends(get_session),
):
    """上传素材"""
    if file.size and file.size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    uploader = MaterialUploader(session)
    try:
        material = await uploader.upload(
            file=file,
            material_type=material_type,
            name=name or file.filename,
            category=category,
            tags=tags,
        )
        return material
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=MaterialListResponse)
async def list_materials(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    material_type: Optional[MaterialType] = None,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    """获取素材列表"""
    query = select(Material)
    if material_type:
        query = query.where(Material.material_type == material_type)
    if category:
        query = query.where(Material.category == category)
    if keyword:
        query = query.where(Material.name.ilike(f"%{keyword}%"))

    total = await session.scalar(select(func.count()).select_from(query.subquery()))
    materials = await session.execute(
        query.offset((page - 1) * page_size).limit(page_size).order_by(Material.created_at.desc())
    )
    items = materials.scalars().all()

    return MaterialListResponse(
        items=[MaterialResponse.model_validate(m) for m in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{material_id}", response_model=MaterialResponse)
async def get_material(material_id: int, session: AsyncSession = Depends(get_session)):
    """获取单个素材"""
    material = await session.get(Material, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return material


@router.delete("/{material_id}")
async def delete_material(material_id: int, session: AsyncSession = Depends(get_session)):
    """删除素材"""
    material = await session.get(Material, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    await session.delete(material)
    await session.commit()
    return {"message": "deleted"}
