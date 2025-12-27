"""Comprehensive endpoint coverage for avatar-service scaffold (ai-orchestra-simulation base).
Tests exercise planned critical and complementary endpoints using the in-process app from main.py.
"""

from __future__ import annotations

import importlib.util
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def app():
    main_path = Path(__file__).resolve().parents[1] / "main.py"
    spec = importlib.util.spec_from_file_location("avatar_main", main_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.app


@pytest.fixture(scope="function")
def client(app):
    return TestClient(app)


@pytest.fixture(scope="function")
def avatar_id() -> str:
    return f"test-avatar-{uuid.uuid4().hex[:6]}"


@pytest.fixture(scope="function")
def session_id(client):
    res = client.post("/api/v1/avatars/session", json={})
    return res.json()["session_id"]


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "healthy"
    # Accept either scaffold health or voice health shape
    if "components" in body:
        assert body["components"].get("api") == "healthy"


def test_render_and_sequence(client, avatar_id):
    r1 = client.post("/api/v1/avatars/render", json={"avatar_id": avatar_id, "format": "png"})
    assert r1.status_code == 200
    assert "frame_url" in r1.json()

    seq = client.post("/api/v1/avatars/render/sequence", json={"avatar_id": avatar_id, "format": "png"})
    assert seq.status_code == 200
    assert len(seq.json()["frames"]) == 3


def test_lipsync_and_phonemes(client, avatar_id):
    lip = client.post("/api/v1/avatars/lipsync", json={"avatar_id": avatar_id, "text": "hello"})
    assert lip.status_code == 200
    assert len(lip.json()["phonemes"]) > 0

    ph = client.post("/api/v1/avatars/phonemes", json={"text": "hello"})
    assert ph.status_code == 200
    assert len(ph.json()["phonemes"]) > 0

    timing = client.post("/api/v1/avatars/phonemes/timing", json={"phonemes": ["A", "B"], "audio_duration": 0.2})
    assert timing.status_code == 200
    assert len(timing.json()["alignment"]) == 2


def test_emotion_and_state(client, avatar_id):
    set_emotion = client.post(
        "/api/v1/avatars/emotions",
        json={"avatar_id": avatar_id, "emotion": "happy", "intensity": 0.7},
    )
    assert set_emotion.status_code == 200

    get_emotion = client.get(f"/api/v1/avatars/{avatar_id}/emotions")
    assert get_emotion.status_code == 200
    assert get_emotion.json()["emotion"] == "happy"

    patch_state = client.patch(f"/api/v1/avatars/{avatar_id}/state", json={"state": {"pose": "wave"}})
    assert patch_state.status_code == 200
    state = client.get(f"/api/v1/avatars/{avatar_id}/state")
    assert state.status_code == 200
    assert state.json()["state"]["pose"] == "wave"


def test_presets_crud(client):
    created = client.post("/api/v1/avatars/presets", json={"name": "Hero", "values": {"style": "hero"}})
    assert created.status_code == 200
    preset_id = created.json()["preset_id"]

    fetched = client.get(f"/api/v1/avatars/presets/{preset_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Hero"

    updated = client.patch(f"/api/v1/avatars/presets/{preset_id}", json={"values": {"style": "heroic"}})
    assert updated.status_code == 200
    assert updated.json()["values"]["style"] == "heroic"

    listed = client.get("/api/v1/avatars/presets")
    assert listed.status_code == 200
    assert any(p["name"] == "Hero" for p in listed.json()["presets"])

    deleted = client.delete(f"/api/v1/avatars/presets/{preset_id}")
    assert deleted.status_code == 200
    assert deleted.json()["deleted"] == preset_id


def test_customize_and_snapshot(client, avatar_id):
    custom = client.post(
        "/api/v1/avatars/customize",
        json={"avatar_id": avatar_id, "traits": {"outfit": "casual"}},
    )
    assert custom.status_code == 200
    assert custom.json()["traits"]["outfit"] == "casual"

    snap_get = client.get(f"/api/v1/avatars/{avatar_id}/snapshot")
    assert snap_get.status_code == 200
    snap_post = client.post(f"/api/v1/avatars/{avatar_id}/snapshot", json={"note": "check"})
    assert snap_post.status_code == 200
    assert "snapshot_id" in snap_post.json()


def test_assets_and_models(client, avatar_id):
    assets = client.get("/api/v1/avatars/assets")
    assert assets.status_code == 200
    upload = client.post("/api/v1/avatars/assets/upload")
    assert upload.status_code == 200

    models = client.get("/api/v1/avatars/models")
    assert models.status_code == 200
    select = client.post("/api/v1/avatars/models/select", json={"avatar_id": avatar_id, "model_id": "granite-avatar-pro"})
    assert select.status_code == 200
    assert select.json()["model_id"] == "granite-avatar-pro"


def test_sessions_and_streams(client, session_id, avatar_id):
    # avatar stream
    with client.websocket_connect(f"/api/v1/avatars/{avatar_id}/stream") as ws:
        assert ws.receive_json()["event"] == "connected"
        assert ws.receive_json()["event"] == "heartbeat"
    # session stream
    with client.websocket_connect(f"/api/v1/avatars/session/{session_id}/stream") as ws:
        assert ws.receive_json()["event"] == "connected"
        assert ws.receive_json()["event"] == "heartbeat"

    delete = client.delete(f"/api/v1/avatars/session/{session_id}")
    assert delete.status_code == 200
    assert delete.json()["deleted"] is True


def test_config_performance_status_version(client):
    cfg = client.get("/api/v1/avatars/config")
    assert cfg.status_code == 200
    upd = client.put("/api/v1/avatars/config", json={"quality": "high", "fps": 60, "shading": "toon"})
    assert upd.status_code == 200
    perf = client.get("/api/v1/avatars/performance")
    assert perf.status_code == 200
    status = client.get("/api/v1/avatars/status")
    assert status.status_code == 200
    version = client.get("/api/v1/avatars/version")
    assert version.status_code == 200


def test_voice_attach_detach(client, avatar_id):
    attach_global = client.post("/api/v1/avatars/voice/attach")
    assert attach_global.status_code == 200

    attach = client.post(f"/api/v1/avatars/{avatar_id}/voice/attach")
    assert attach.status_code == 200
    assert attach.json()["voice_attached"] is True

    status = client.get(f"/api/v1/avatars/{avatar_id}/voice/status")
    assert status.status_code == 200

    detach = client.delete(f"/api/v1/avatars/{avatar_id}/voice/detach")
    assert detach.status_code == 200
    assert detach.json()["voice_attached"] is False

    detach_global = client.delete("/api/v1/avatars/voice/detach")
    assert detach_global.status_code == 200
