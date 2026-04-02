"""视频渲染服务 - FFmpeg 集成"""
import asyncio
import json
import os
import subprocess
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.core.database import async_session
from app.models.video import Video, VideoStatus
from app.models.script import Script
from app.models.template import Template


class VideoRenderer:
    """基于 FFmpeg 的视频渲染引擎"""

    def __init__(self, video_id: int):
        self.video_id = video_id
        self.video: Optional[Video] = None
        self.script: Optional[Script] = None
        self.template: Optional[Template] = None
        self.output_dir = Path(settings.OSS_BUCKET) if settings.OSS_BUCKET else Path("outputs")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def load(self):
        """加载视频任务及相关数据"""
        async with async_session() as session:
            self.video = await session.get(Video, self.video_id)
            if not self.video:
                raise ValueError(f"Video {self.video_id} not found")

            if self.video.script_id:
                self.script = await session.get(Script, self.video.script_id)
            if self.video.template_id:
                self.template = await session.get(Template, self.video.template_id)

    async def update_progress(self, progress: int, status: VideoStatus = None):
        """更新渲染进度"""
        async with async_session() as session:
            video = await session.get(Video, self.video_id)
            if video:
                video.progress = progress
                if status:
                    video.status = status
                await session.commit()

    async def render(self) -> bool:
        """执行渲染"""
        try:
            await self.update_progress(0, VideoStatus.RENDERING)

            # 1. 准备素材和参数
            await self.update_progress(10)
            cmd = self._build_ffmpeg_command()
            if not cmd:
                # 演示模式：生成空白视频
                cmd = self._build_demo_command()

            # 2. 执行 FFmpeg
            await self.update_progress(20)
            result = await self._run_ffmpeg(cmd)

            if result != 0:
                raise RuntimeError(f"FFmpeg exited with code {result}")

            await self.update_progress(90)

            # 3. 获取输出文件信息
            output_path = self._get_output_path()
            info = await self._probe(output_path)

            # 4. 更新数据库
            async with async_session() as session:
                video = await session.get(Video, self.video_id)
                if video:
                    video.output_path = str(output_path)
                    video.duration = info.get("duration", 0)
                    video.width = info.get("width", 1080)
                    video.height = info.get("height", 1920)
                    video.file_size = info.get("file_size", 0)
                    video.thumbnail_path = str(output_path.with_suffix(".jpg"))
                    video.status = VideoStatus.COMPLETED
                    video.progress = 100
                    await session.commit()

            return True

        except Exception as e:
            async with async_session() as session:
                video = await session.get(Video, self.video_id)
                if video:
                    video.status = VideoStatus.FAILED
                    video.error_message = str(e)
                    await session.commit()
            return False

    def _build_ffmpeg_command(self) -> Optional[list]:
        """构建 FFmpeg 命令"""
        if not self.script or not self.template:
            return None

        # 读取模板配置
        template_config = self._load_template_config()
        if not template_config:
            return None

        output_path = self._get_output_path()
        cmd = [
            settings.FFMPEG_PATH,
            "-y",  # 覆盖输出
            "-loglevel", "info",
        ]

        # 输入素材
        for idx, material_path in enumerate(template_config.get("inputs", [])):
            cmd.extend(["-i", material_path])

        # 滤镜链
        filter_chain = self._build_filter_chain(template_config)
        if filter_chain:
            cmd.extend(["-vf", filter_chain])

        # 音频（如果有脚本配音）
        if self.script.voiceover_path:
            cmd.extend(["-i", self.script.voiceover_path, "-map", "[v]", "-map", "[a]"])
        else:
            cmd.extend(["-map", "[v]"])

        # 输出编码参数
        cmd.extend([
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            "-movflags", "+faststart",
            str(output_path),
        ])

        return cmd

    def _build_demo_command(self) -> list:
        """演示模式：生成测试视频（彩色画面 + 静音）"""
        output_path = self._get_output_path()
        return [
            settings.FFMPEG_PATH,
            "-y",
            "-f", "lavfi",
            "-i", f"color=c=0x6C5CE7:s=1080x1920:d={self.video.duration or 5 if self.video else 5}",
            "-f", "lavfi",
            "-i", "anullsrc=r=44100:cl=stereo",
            "-shortest",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-c:a", "aac",
            str(output_path),
        ]

    def _build_filter_chain(self, config: dict) -> Optional[str]:
        """构建 FFmpeg 滤镜链"""
        filters = []

        # 缩放到目标分辨率
        filters.append(f"scale={self.video.width if self.video else 1080}:{self.video.height if self.video else 1920}:force_original_aspect_ratio=decrease,pad=ceil(iw/2)*2:ceil(ih/2)*2")

        # 添加文字水印（脚本标题）
        if self.script:
            title = self.script.title[:20] if self.script.title else ""
            if title:
                filters.append(
                    f"drawtext=text='{title}':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=h-100:border_w=2:border_color=black@0.5"
                )

        return ",".join(filters) if filters else None

    def _load_template_config(self) -> Optional[dict]:
        """加载模板配置"""
        if not self.template or not self.template.config:
            return None
        if isinstance(self.template.config, dict):
            return self.template.config
        try:
            return json.loads(self.template.config)
        except (json.JSONDecodeError, TypeError):
            return None

    def _get_output_path(self) -> Path:
        """获取输出路径"""
        filename = f"video_{self.video_id}_{int(asyncio.get_event_loop().time())}.mp4"
        return self.output_dir / filename

    async def _run_ffmpeg(self, cmd: list) -> int:
        """执行 FFmpeg 命令"""
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            error_msg = stderr.decode() if stderr else "unknown error"
            print(f"FFmpeg error: {error_msg[:500]}")

        return proc.returncode

    async def _probe(self, path: Path) -> dict:
        """使用 ffprobe 获取视频信息"""
        cmd = [
            settings.FFPROBE_PATH,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(path),
        ]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()

            if proc.returncode == 0:
                data = json.loads(stdout.decode())
                video_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
                format_info = data.get("format", {})

                return {
                    "duration": int(float(format_info.get("duration", 0))),
                    "width": int(video_stream.get("width", 1080)),
                    "height": int(video_stream.get("height", 1920)),
                    "file_size": int(format_info.get("size", 0)),
                }
        except Exception as e:
            print(f"Probe error: {e}")

        # 回退默认值
        return {
            "duration": 5,
            "width": 1080,
            "height": 1920,
            "file_size": 0,
        }


async def render_video_task(video_id: int):
    """后台渲染任务入口"""
    renderer = VideoRenderer(video_id)
    try:
        await renderer.load()
        await renderer.render()
    except Exception as e:
        print(f"Render task {video_id} failed: {e}")
        async with async_session() as session:
            video = await session.get(Video, video_id)
            if video:
                video.status = VideoStatus.FAILED
                video.error_message = str(e)
                await session.commit()
