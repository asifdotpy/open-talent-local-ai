import uuid
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_update_status_happy_path():
    # Create candidate (defaults to status 'new')
    payload = {"email": "test.status@example.com", "first_name": "Status", "last_name": "Tester"}
    headers = {"Authorization": "Bearer test-token"}
    r = client.post("/api/v1/candidates", json=payload, headers=headers)
    assert r.status_code == 201
    data = r.json()
    candidate_id = data["id"]
    assert data["status"] == "new"

    # Update status to reviewing with auth
    r2 = client.patch(
        f"/api/v1/candidates/{candidate_id}/status", json={"status": "reviewing"}, headers=headers
    )
    assert r2.status_code == 200
    updated = r2.json()
    assert updated["status"] == "reviewing"


def test_update_status_unauthorized():
    # Create candidate
    payload = {"email": "unauth.status@example.com", "first_name": "NoAuth", "last_name": "User"}
    r = client.post(
        "/api/v1/candidates", json=payload, headers={"Authorization": "Bearer test-token"}
    )
    assert r.status_code == 201
    candidate_id = r.json()["id"]

    # Attempt status update without auth
    r2 = client.patch(f"/api/v1/candidates/{candidate_id}/status", json={"status": "reviewing"})
    assert r2.status_code == 401


def test_update_status_not_found():
    # Random ID that doesn't exist
    unknown_id = str(uuid.uuid4())
    headers = {"Authorization": "Bearer test-token"}
    r = client.patch(
        f"/api/v1/candidates/{unknown_id}/status", json={"status": "reviewing"}, headers=headers
    )
    assert r.status_code == 404
