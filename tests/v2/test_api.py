"""
Omnix V2 API tests.
Run with: OMNIX_DEV_MODE=1 pytest tests/v2/ -v
"""
import pytest
from httpx import AsyncClient, ASGITransport

from backend.server import app


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/api/v2/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["version"] == "2.0.0"


@pytest.mark.asyncio
async def test_config_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/api/v2/config")
    assert r.status_code == 200
    assert "ollama_host" in r.json()
    assert "ollama_model" in r.json()


@pytest.mark.asyncio
async def test_current_game():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/api/v2/game/current")
    assert r.status_code == 200
    assert "name" in r.json()


@pytest.mark.asyncio
async def test_system_stats():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/api/v2/stats/system")
    assert r.status_code == 200
    body = r.json()
    assert "cpu" in body
    assert "ram" in body


@pytest.mark.asyncio
async def test_ollama_models():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/api/v2/ollama/models")
    assert r.status_code == 200
    assert "models" in r.json()


@pytest.mark.asyncio
async def test_license_status_dev_mode():
    import os
    os.environ["OMNIX_DEV_MODE"] = "1"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/api/v2/license/status")
    assert r.status_code == 200
    assert r.json()["valid"] is True
    assert r.json()["dev_mode"] is True


@pytest.mark.asyncio
async def test_knowledge_packs():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/api/v2/knowledge/packs")
    assert r.status_code == 200
    assert "packs" in r.json()


@pytest.mark.asyncio
async def test_macros_list():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/api/v2/macros")
    assert r.status_code == 200
    assert "macros" in r.json()
