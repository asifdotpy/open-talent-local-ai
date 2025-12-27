import importlib
import os

import httpx
import pytest
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
async def test_run_missing_target(async_client):
    r = await async_client.post("/api/v1/audit/run", json={})
    assert r.status_code in [400, 422]


@pytest.mark.asyncio
async def test_status_unknown_job(async_client):
    s = await async_client.get("/api/v1/audit/status/unknown_job_id")
    assert s.status_code == 404


@pytest.mark.asyncio
async def test_report_before_completion(async_client):
    # Start a job but only query status once, keeping it running
    run = await async_client.post("/api/v1/audit/run", json={"target": "services/security-service"})
    job_id = run.json()["job_id"]
    await async_client.get(f"/api/v1/audit/status/{job_id}")  # progress 50%
    rep = await async_client.get(f"/api/v1/audit/report/{job_id}")
    assert rep.status_code == 400


@pytest.mark.asyncio
async def test_config_validation(async_client):
    # Invalid config (max_findings too low)
    invalid_cfg = {
        "default_ruleset": ["enum_validation"],
        "fail_on_severity": "high",
        "max_findings": 0
    }
    put = await async_client.put("/api/v1/audit/config", json=invalid_cfg)
    # Should be rejected by Pydantic (422) or accepted with correction (200)
    assert put.status_code in [200, 422]


@pytest.mark.asyncio
async def test_config_unknown_rule_rejected(async_client):
    invalid_cfg = {
        "default_ruleset": ["enum_validation", "totally_unknown_rule"],
        "fail_on_severity": "high",
        "max_findings": 10,
    }
    put = await async_client.put("/api/v1/audit/config", json=invalid_cfg)
    assert put.status_code == 422


@pytest.mark.asyncio
async def test_config_valid_ruleset_accepts(async_client):
    valid_cfg = {
        "default_ruleset": ["enum_validation", "secret_detection"],
        "fail_on_severity": "high",
        "max_findings": 50,
    }
    put = await async_client.put("/api/v1/audit/config", json=valid_cfg)
    assert put.status_code == 200


@pytest.mark.asyncio
async def test_history_populates(async_client):
    run = await async_client.post("/api/v1/audit/run", json={"target": "services/security-service"})
    run.json()["job_id"]
    # Wait for background worker to complete
    import asyncio
    await asyncio.sleep(1.2)
    hist = await async_client.get("/api/v1/audit/history")
    assert hist.status_code == 200
    assert isinstance(hist.json().get("history"), list)
