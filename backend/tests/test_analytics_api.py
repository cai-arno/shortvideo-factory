import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_analytics_overview():
    """测试数据概览接口"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    # 验证数据结构
    assert "scripts" in data
    assert "videos" in data
    assert "publishing" in data


@pytest.mark.asyncio
async def test_analytics_trends():
    """测试趋势数据接口"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/analytics/trends?days=7")
    assert response.status_code == 200
    data = response.json()
    assert "scripts" in data
    assert "videos" in data
    assert "publishes" in data


@pytest.mark.asyncio
async def test_analytics_platforms():
    """测试平台统计数据"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/analytics/platforms")
    assert response.status_code == 200
    data = response.json()
    assert "platforms" in data
    assert isinstance(data["platforms"], list)


@pytest.mark.asyncio
async def test_analytics_top_videos():
    """测试 TOP 视频接口"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/analytics/top?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
