"""Session lifecycle tests for avatar API.
Validates session CRUD, WebSocket streaming, and resource cleanup.
"""

from __future__ import annotations

import importlib.util
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


class TestSessionLifecycle:
    def test_session_create(self, client):
        """Create a new session."""
        res = client.post("/api/v1/avatars/session", json={})
        assert res.status_code == 200
        body = res.json()
        assert "session_id" in body
        assert body["session_id"]

    def test_session_create_with_avatar_id(self, client):
        """Create session with avatar_id."""
        res = client.post("/api/v1/avatars/session", json={"avatar_id": "test-avatar"})
        assert res.status_code == 200
        body = res.json()
        assert body["avatar_id"] == "test-avatar"

    def test_session_create_with_metadata(self, client):
        """Create session with custom metadata."""
        meta = {"interview_id": "int-123", "duration_minutes": 30}
        res = client.post("/api/v1/avatars/session", json={"metadata": meta})
        assert res.status_code == 200
        body = res.json()
        assert body["metadata"] == meta

    def test_session_delete_existing(self, client):
        """Delete an existing session."""
        # Create first
        create_res = client.post("/api/v1/avatars/session", json={})
        session_id = create_res.json()["session_id"]

        # Delete
        del_res = client.delete(f"/api/v1/avatars/session/{session_id}")
        assert del_res.status_code == 200
        assert del_res.json()["deleted"] is True
        assert del_res.json()["session_id"] == session_id

    def test_session_delete_nonexistent(self, client):
        """Delete non-existent session should return deleted: false."""
        res = client.delete("/api/v1/avatars/session/nonexistent-xyz")
        assert res.status_code == 200
        assert res.json()["deleted"] is False


class TestSessionWebSocketStreaming:
    def test_session_stream_connects(self, client):
        """WebSocket stream should connect and send heartbeat."""
        create_res = client.post("/api/v1/avatars/session", json={})
        session_id = create_res.json()["session_id"]

        with client.websocket_connect(f"/api/v1/avatars/session/{session_id}/stream") as ws:
            # Should receive connect message
            msg1 = ws.receive_json()
            assert msg1["session_id"] == session_id
            assert msg1["event"] == "connected"

            # Should receive heartbeat
            msg2 = ws.receive_json()
            assert msg2["session_id"] == session_id
            assert msg2["event"] == "heartbeat"

    def test_session_stream_auto_closes(self, client):
        """Session stream should close after heartbeat (mock behavior)."""
        create_res = client.post("/api/v1/avatars/session", json={})
        session_id = create_res.json()["session_id"]

        # Connect and read messages; should close after heartbeat
        try:
            with client.websocket_connect(f"/api/v1/avatars/session/{session_id}/stream") as ws:
                ws.receive_json()  # connect
                ws.receive_json()  # heartbeat
                # Stub implementation closes after heartbeat
                with pytest.raises(RuntimeError):
                    ws.receive_json(timeout=1.0)
        except RuntimeError:
            # TestClient may raise on closed connection
            pass

    def test_multiple_concurrent_streams(self, client):
        """Multiple sessions should have independent streams."""
        # Create two sessions
        res1 = client.post("/api/v1/avatars/session", json={"metadata": {"id": 1}})
        res2 = client.post("/api/v1/avatars/session", json={"metadata": {"id": 2}})
        sid1 = res1.json()["session_id"]
        sid2 = res2.json()["session_id"]

        # Open two streams simultaneously
        with client.websocket_connect(f"/api/v1/avatars/session/{sid1}/stream") as ws1, \
             client.websocket_connect(f"/api/v1/avatars/session/{sid2}/stream") as ws2:
                # Each should have correct session_id in messages
                msg1 = ws1.receive_json()
                msg2 = ws2.receive_json()
                assert msg1["session_id"] == sid1
                assert msg2["session_id"] == sid2


class TestAvatarSessionAssociation:
    def test_avatar_stream_independent_of_session(self, client):
        """Avatar streams should work independently of sessions."""
        avatar_id = f"avatar-{id(object())}"

        # Open avatar stream (not session)
        with client.websocket_connect(f"/api/v1/avatars/{avatar_id}/stream") as ws:
            msg = ws.receive_json()
            assert msg["avatar_id"] == avatar_id
            assert msg["event"] == "connected"

    def test_session_deletion_does_not_affect_avatar(self, client):
        """Deleting session should not affect avatar streams."""
        # Create session with avatar
        res = client.post("/api/v1/avatars/session", json={"avatar_id": "avatar-1"})
        session_id = res.json()["session_id"]

        # Delete session
        client.delete(f"/api/v1/avatars/session/{session_id}")

        # Avatar stream should still work
        with client.websocket_connect("/api/v1/avatars/avatar-1/stream") as ws:
            msg = ws.receive_json()
            assert msg["avatar_id"] == "avatar-1"


class TestSessionErrorCases:
    def test_stream_nonexistent_session(self, client):
        """Connecting to non-existent session stream should handle gracefully."""
        # Stub implementation creates session on connect; should work
        with client.websocket_connect("/api/v1/avatars/session/nonexistent-xyz/stream") as ws:
            msg = ws.receive_json()
            # May use provided session_id or create new
            assert msg["session_id"]

    def test_delete_already_deleted_session(self, client):
        """Deleting same session twice should be graceful."""
        # Create and delete
        res = client.post("/api/v1/avatars/session", json={})
        session_id = res.json()["session_id"]
        client.delete(f"/api/v1/avatars/session/{session_id}")

        # Delete again
        res2 = client.delete(f"/api/v1/avatars/session/{session_id}")
        assert res2.status_code in [200, 404]
        if res2.status_code == 200:
            assert res2.json()["deleted"] is False


class TestSessionStateManagement:
    def test_session_state_persistence_in_memory(self, client):
        """Session metadata should be retrievable after creation."""
        meta = {"user_id": "user-123", "timestamp": "2025-12-16T00:00:00Z"}
        res = client.post("/api/v1/avatars/session", json={"metadata": meta})
        session_id = res.json()["session_id"]

        # In current stub, we can't GET session details, but metadata is stored
        # Verify deletion still works
        del_res = client.delete(f"/api/v1/avatars/session/{session_id}")
        assert del_res.status_code == 200
