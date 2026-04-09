"""ComfyUI 集成服务"""
import httpx
import asyncio
import os
from typing import Optional, Dict, Any
from datetime import datetime

COMFYUI_URL = "http://localhost:8188"
OUTPUT_DIR = "/home/arno/ComfyUI/output"

WORKFLOW_TEMPLATE = {
    "prompt": {
        "1": {
            "class_type": "LoadWanVideoT5TextEncoder",
            "inputs": {
                "model_name": "models_t5_umt5-xxl-enc-bf16.pth",
                "precision": "bf16"
            }
        },
        "2": {
            "class_type": "WanVideoTextEncode",
            "inputs": {
                "positive_prompt": "",
                "negative_prompt": "blurry, low quality, distorted, watermark, text, logo, bad anatomy",
                "force_offload": True,
                "t5": ["1", 0]
            }
        },
        "3": {
            "class_type": "WanVideoModelLoader",
            "inputs": {
                "model": "diffusion_pytorch_model.safetensors",
                "base_precision": "bf16",
                "quantization": "fp8_e4m3fn",
                "load_device": "offload_device"
            }
        },
        "4": {
            "class_type": "WanVideoEmptyEmbeds",
            "inputs": {
                "width": 832,
                "height": 480,
                "num_frames": 49,
                "batch_size": 1
            }
        },
        "5": {
            "class_type": "WanVideoVAELoader",
            "inputs": {
                "model_name": "Wan2.1_VAE.pth",
                "precision": "bf16"
            }
        },
        "6": {
            "class_type": "WanVideoSampler",
            "inputs": {
                "model": ["3", 0],
                "image_embeds": ["4", 0],
                "text_embeds": ["2", 0],
                "steps": 25,
                "cfg": 8.0,
                "shift": 5.0,
                "scheduler": "unipc",
                "seed": 42,
                "force_offload": True,
                "riflex_freq_index": 0
            }
        },
        "7": {
            "class_type": "WanVideoDecode",
            "inputs": {
                "vae": ["5", 0],
                "samples": ["6", 0],
                "enable_vae_tiling": True,
                "tile_x": 128,
                "tile_y": 128,
                "tile_stride_x": 64,
                "tile_stride_y": 64
            }
        },
        "8": {
            "class_type": "VHS_VideoCombine",
            "inputs": {
                "images": ["7", 0],
                "frame_rate": 16,
                "format": "video/h264-mp4",
                "filename_prefix": "video_factory",
                "loop_count": 0,
                "save_output": True,
                "pingpong": False
            }
        }
    }
}


async def check_comfyui_status() -> Dict[str, Any]:
    """检查ComfyUI状态"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{COMFYUI_URL}/api/system_stats")
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "status": "online",
                    "comfyui_version": data.get("system", {}).get("comfyui_version"),
                    "gpu": data.get("devices", [{}])[0].get("name") if data.get("devices") else None,
                }
    except Exception:
        pass
    return {"status": "offline"}


async def submit_video_task(
    prompt_text: str,
    negative_prompt: str = "blurry, low quality, distorted, watermark, text, logo, bad anatomy",
    width: int = 832,
    height: int = 480,
    frames: int = 49,
    steps: int = 25,
    cfg: float = 8.0,
    seed: int = -1,
) -> Optional[str]:
    """提交视频生成任务，返回task_id"""
    workflow = WORKFLOW_TEMPLATE.copy()
    workflow["prompt"]["2"]["inputs"]["positive_prompt"] = prompt_text
    workflow["prompt"]["2"]["inputs"]["negative_prompt"] = negative_prompt
    workflow["prompt"]["4"]["inputs"]["width"] = width
    workflow["prompt"]["4"]["inputs"]["height"] = height
    workflow["prompt"]["4"]["inputs"]["num_frames"] = frames
    workflow["prompt"]["6"]["inputs"]["steps"] = steps
    workflow["prompt"]["6"]["inputs"]["cfg"] = cfg
    workflow["prompt"]["6"]["inputs"]["seed"] = seed if seed >= 0 else int(datetime.now().timestamp()) % 2147483647
    workflow["prompt"]["8"]["inputs"]["filename_prefix"] = f"video_factory_{int(datetime.now().timestamp())}"

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{COMFYUI_URL}/prompt", json=workflow)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("prompt_id")
    except Exception as e:
        print(f"提交任务失败: {e}")
    return None


async def get_task_result(prompt_id: str) -> Optional[Dict[str, Any]]:
    """获取任务结果"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{COMFYUI_URL}/history/{prompt_id}")
            if resp.status_code == 200:
                data = resp.json()
                task_data = data.get(prompt_id, {})
                status_str = task_data.get("status", {}).get("status_str")
                outputs = task_data.get("outputs", {})
                
                # 查找输出文件
                video_path = None
                for node_id, output in outputs.items():
                    if isinstance(output, dict) and output.get("type") == "output":
                        images = output.get("images", [])
                        if images:
                            video_path = images[0] if isinstance(images[0], str) else None
                
                return {
                    "status": status_str,
                    "outputs": outputs,
                    "video_path": video_path,
                }
    except Exception as e:
        print(f"查询任务失败: {e}")
    return None


async def wait_for_completion(prompt_id: str, max_wait: int = 300) -> Optional[Dict[str, Any]]:
    """等待任务完成"""
    waited = 0
    while waited < max_wait:
        await asyncio.sleep(5)
        waited += 5
        result = await get_task_result(prompt_id)
        if result and result.get("status") in ["success", "completed"]:
            return result
        if result and result.get("status") == "failed":
            return result
    return {"status": "timeout"}
