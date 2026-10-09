import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_root_endpoint() -> None:
    """Verify that root endpoint responds with 200 OK and expected metadata."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["project"] == "SoleMarket API"
    assert "version" in data


@pytest.mark.asyncio
async def test_liveness_probe() -> None:
    """Verify that health liveness probe responds with 200 OK and healthy status."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health/live")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "solemarket-backend"
