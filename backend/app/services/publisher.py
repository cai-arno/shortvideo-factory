"""平台发布服务"""
import asyncio
import httpx
from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime

from app.core.config import settings
from app.core.database import async_session
from app.models.publishing import PublishRecord, Platform, PublishStatus
from app.models.video import Video


class BasePublisher(ABC):
    """发布平台基类"""

    @abstractmethod
    async def publish(self, record: PublishRecord, video_path: str) -> dict:
        """发布视频，返回平台响应"""
        pass

    @abstractmethod
    async def get_status(self, record: PublishRecord) -> PublishStatus:
        """查询发布状态"""
        pass


class DouyinPublisher(BasePublisher):
    """抖音开放平台发布器"""

    API_BASE = "https://open.douyin.com"

    def __init__(self):
        self.client_id = settings.DOUYIN_CLIENT_ID
        self.client_secret = settings.DOUYIN_CLIENT_SECRET

    async def publish(self, record: PublishRecord, video_path: str) -> dict:
        """上传并发布视频到抖音"""
        if not self.client_id or not self.client_secret:
            return await self._mock_publish(record)

        access_token = await self._get_access_token()
        if not access_token:
            return {"error": "Failed to get access token"}

        # 1. 申请上传
        upload_url = await self._apply_upload(access_token, record)
        if not upload_url:
            return {"error": "Failed to apply for upload"}

        # 2. 上传视频文件
        video_id = await self._upload_video(upload_url, video_path)
        if not video_id:
            return {"error": "Failed to upload video"}

        # 3. 发布视频
        result = await self._publish_video(access_token, video_id, record)
        return result

    async def _get_access_token(self) -> Optional[str]:
        """获取 access_token"""
        # 实际实现需要先完成 OAuth 授权流程
        # 此处从数据库或缓存获取已保存的 token
        return None

    async def _apply_upload(self, token: str, record: PublishRecord) -> Optional[str]:
        """申请视频上传"""
        url = f"{self.API_BASE}/video/upload/"
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "publish_time": int(record.scheduled_at.timestamp()) if record.scheduled_at else 0,
        }
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url, headers=headers, data=data, timeout=30)
                if resp.status_code == 200:
                    return resp.json().get("upload_url")
            except Exception as e:
                print(f"Apply upload error: {e}")
        return None

    async def _upload_video(self, upload_url: str, video_path: str) -> Optional[str]:
        """上传视频文件"""
        import os
        file_size = os.path.getsize(video_path)
        headers = {"Content-Type": "video/mp4"}

        with open(video_path, "rb") as f:
            async with httpx.AsyncClient() as client:
                try:
                    resp = await client.post(
                        upload_url,
                        headers=headers,
                        content=f.read(),
                        timeout=120,
                    )
                    if resp.status_code == 200:
                        return resp.json().get("video_id")
                except Exception as e:
                    print(f"Upload video error: {e}")
        return None

    async def _publish_video(self, token: str, video_id: str, record: PublishRecord) -> dict:
        """发布视频"""
        url = f"{self.API_BASE}/video/publish/"
        headers = {"Authorization": f"Bearer {token}"}
        data = {"video_id": video_id}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url, headers=headers, data=data, timeout=30)
                return resp.json()
            except Exception as e:
                return {"error": str(e)}

    async def _mock_publish(self, record: PublishRecord) -> dict:
        """演示模式：模拟发布"""
        await asyncio.sleep(2)  # 模拟网络延迟

        # 模拟发布结果
        return {
            "platform_video_id": f"mock_{record.id}_{int(datetime.utcnow().timestamp())}",
            "status": "published",
            "url": f"https://www.douyin.com/video/mock_{record.id}",
        }

    async def get_status(self, record: PublishRecord) -> PublishStatus:
        """查询发布状态"""
        if record.platform_video_id:
            # 真实实现：调用平台 API 查询状态
            return PublishStatus.PUBLISHED
        return PublishStatus.FAILED


class KuaishouPublisher(BasePublisher):
    """快手开放平台发布器"""

    async def publish(self, record: PublishRecord, video_path: str) -> dict:
        """发布视频到快手"""
        # 类似抖音实现
        await asyncio.sleep(2)
        return {
            "platform_video_id": f"ks_mock_{record.id}",
            "status": "published",
            "url": f"https://www.kuaishou.com/video/mock_{record.id}",
        }

    async def get_status(self, record: PublishRecord) -> PublishStatus:
        return PublishStatus.PUBLISHED


class PublisherFactory:
    """发布器工厂"""

    _publishers = {
        Platform.DOUYIN: DouyinPublisher,
        Platform.KUAISHOU: KuaishouPublisher,
    }

    @classmethod
    def get_publisher(cls, platform: Platform) -> BasePublisher:
        return cls._publishers.get(platform, DouyinPublisher)()


async def publish_task(record_id: int):
    """后台发布任务入口"""
    async with async_session() as session:
        record = await session.get(PublishRecord, record_id)
        if not record:
            return

        # 获取视频路径
        video = await session.get(Video, record.video_id)
        if not video or not video.output_path:
            record.status = PublishStatus.FAILED
            record.error_message = "Video not found or not rendered"
            await session.commit()
            return

        record.status = PublishStatus.PUBLISHING
        await session.commit()

        try:
            publisher = PublisherFactory.get_publisher(record.platform)
            result = await publisher.publish(record, video.output_path)

            if "error" in result:
                record.status = PublishStatus.FAILED
                record.error_message = result["error"]
            else:
                record.status = PublishStatus.PUBLISHED
                record.platform_video_id = result.get("platform_video_id", "")
                record.platform_url = result.get("url", "")

            await session.commit()

        except Exception as e:
            record.status = PublishStatus.FAILED
            record.error_message = str(e)
            await session.commit()
