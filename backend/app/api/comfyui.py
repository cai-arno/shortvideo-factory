"""ComfyUI 视频生成 API"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from app.services.comfyui_service import (
    check_comfyui_status,
    submit_video_task,
    wait_for_completion,
    get_task_result,
)

router = APIRouter()


class VideoGenerateRequest(BaseModel):
    prompt: str
    negative_prompt: str = "blurry, low quality, distorted, watermark, text, logo, bad anatomy"
    width: int = 832
    height: int = 480
    frames: int = 49
    steps: int = 25
    cfg: float = 8.0
    seed: int = -1


class VideoGenerateResponse(BaseModel):
    task_id: str
    status: str
    message: str


@router.get("/status")
async def get_status():
    """检查ComfyUI状态"""
    status = await check_comfyui_status()
    return status


@router.post("/generate", response_model=VideoGenerateResponse)
async def generate_video(
    req: VideoGenerateRequest,
    background_tasks: BackgroundTasks,
):
    """提交视频生成任务"""
    status = await check_comfyui_status()
    if status.get("status") != "online":
        raise HTTPException(status_code=503, detail="ComfyUI未连接")

    task_id = await submit_video_task(
        prompt_text=req.prompt,
        negative_prompt=req.negative_prompt,
        width=req.width,
        height=req.height,
        frames=req.frames,
        steps=req.steps,
        cfg=req.cfg,
        seed=req.seed,
    )

    if not task_id:
        raise HTTPException(status_code=500, detail="任务提交失败")

    return VideoGenerateResponse(
        task_id=task_id,
        status="queued",
        message="任务已提交，请通过task_id查询结果"
    )


@router.get("/result/{task_id}")
async def get_result(task_id: str):
    """查询任务结果"""
    result = await get_task_result(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="任务不存在或查询失败")
    return result
