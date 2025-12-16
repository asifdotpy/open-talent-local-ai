import importlib
import os
import pytest
import httpx
from httpx import ASGITransport


def _load_app():
    if "services.ai-auditing-service.main" in importlib.sys.modules:
        del importlib.sys.modules["services.ai-auditing-service.main"]
    spec = importlib.util.spec_from_file_location(
        "ai_auditing_main",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py")),
    )
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module.app


@pytest.fixture
async def async_client():
    app = _load_app()
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver", timeout=5.0) as client:
        yield client


@pytest.mark.asyncio
async def test_run_status_report_flow(async_client):
    run = await async_client.post("/api/v1/audit/run", json={"target": "services/security-service"})
    assert run.status_code == 200
    job_id = run.json()["job_id"]

    # Wait for background worker to complete
    import asyncio
    # Poll status until completed (timeout 2s)
    for _ in range(10):
        s = await async_client.get(f"/api/v1/audit/status/{job_id}")
        if s.status_code == 200 and (s.json().get("status") in ["completed", "COMPLETED"]):
            break
        await asyncio.sleep(0.2)
    rep = await async_client.get(f"/api/v1/audit/report/{job_id}")
    assert rep.status_code == 200


@pytest.mark.asyncio
async def test_rules_config_history(async_client):
    rules = await async_client.get("/api/v1/audit/rules")
    assert rules.status_code == 200

    cfg = await async_client.get("/api/v1/audit/config")
    assert cfg.status_code == 200

    new_cfg = cfg.json()
    new_cfg["max_findings"] = 123
    put = await async_client.put("/api/v1/audit/config", json=new_cfg)
    assert put.status_code == 200

    hist = await async_client.get("/api/v1/audit/history")
    assert hist.status_code == 200
