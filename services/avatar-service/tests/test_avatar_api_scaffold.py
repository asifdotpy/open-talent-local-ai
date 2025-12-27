"""Lightweight tests for scaffolded avatar API endpoints."""

import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient


def load_app():
    main_path = Path(__file__).resolve().parents[1] / "main.py"
    spec = importlib.util.spec_from_file_location("avatar_main", main_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.app


client = TestClient(load_app())


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_render_endpoint():
    response = client.post(
        "/api/v1/avatars/render",
        json={"avatar_id": "test", "width": 256, "height": 256, "format": "png"},
    )
    data = response.json()
    assert response.status_code == 200
    assert data["avatar_id"] == "test"
    assert "frame_url" in data


def test_state_patch_and_get():
    client.patch("/api/v1/avatars/example/state", json={"state": {"pose": "wave"}})
    res = client.get("/api/v1/avatars/example/state")
    assert res.status_code == 200
    assert res.json()["state"]["pose"] == "wave"


def test_presets_and_phonemes():
    presets = client.get("/api/v1/avatars/presets")
    assert presets.status_code == 200
    phonemes = client.post("/api/v1/avatars/phonemes", json={"text": "hello"})
    assert phonemes.status_code == 200
    assert len(phonemes.json().get("phonemes", [])) > 0


def test_websocket_stream():
    with client.websocket_connect("/api/v1/avatars/ws-avatar/stream") as ws:
        first = ws.receive_json()
        assert first["avatar_id"] == "ws-avatar"
        heartbeat = ws.receive_json()
        assert heartbeat["event"] == "heartbeat"
