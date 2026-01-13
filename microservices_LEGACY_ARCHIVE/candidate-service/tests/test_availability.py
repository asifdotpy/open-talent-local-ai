import uuid
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)
AUTH = {"Authorization": "Bearer test-token"}


def test_availability_crud_happy_path():
    # Create candidate
    cand = {
        "email": "availability.user@example.com",
        "first_name": "Availability",
        "last_name": "Tester",
    }
    r = client.post("/api/v1/candidates", json=cand, headers=AUTH)
    assert r.status_code == 201
    candidate_id = r.json()["id"]

    # Create availability slot
    start = datetime.utcnow() + timedelta(days=1)
    end = start + timedelta(hours=2)
    payload = {
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "timezone": "America/New_York",
        "is_available": True,
        "notes": "Morning slot preferred",
    }
    r2 = client.post(f"/api/v1/candidates/{candidate_id}/availability", json=payload, headers=AUTH)
    assert r2.status_code == 201
    avail = r2.json()
    avail_id = avail["id"]
    assert avail["is_available"] is True
    assert avail["timezone"] == "America/New_York"

    # List availability
    r3 = client.get(f"/api/v1/candidates/{candidate_id}/availability", headers=AUTH)
    assert r3.status_code == 200
    items = r3.json()
    assert any(a["id"] == avail_id for a in items)

    # Get availability
    r4 = client.get(f"/api/v1/candidates/{candidate_id}/availability/{avail_id}", headers=AUTH)
    assert r4.status_code == 200
    assert r4.json()["id"] == avail_id

    # Update availability
    upd = {"is_available": False, "notes": "Rescheduled"}
    r5 = client.put(
        f"/api/v1/candidates/{candidate_id}/availability/{avail_id}", json=upd, headers=AUTH
    )
    assert r5.status_code == 200
    assert r5.json()["is_available"] is False
    assert r5.json()["notes"] == "Rescheduled"

    # Delete availability
    r6 = client.delete(f"/api/v1/candidates/{candidate_id}/availability/{avail_id}", headers=AUTH)
    assert r6.status_code == 204


def test_availability_unauthorized_and_not_found():
    # Create candidate
    cand = {"email": "availability.noauth@example.com", "first_name": "No", "last_name": "Auth"}
    r = client.post("/api/v1/candidates", json=cand, headers=AUTH)
    assert r.status_code == 201
    candidate_id = r.json()["id"]

    # Create availability without auth
    start = datetime.utcnow() + timedelta(days=2)
    end = start + timedelta(hours=1)
    payload = {"start_time": start.isoformat(), "end_time": end.isoformat()}
    r2 = client.post(f"/api/v1/candidates/{candidate_id}/availability", json=payload)
    assert r2.status_code == 401

    # Get availability with unknown ID
    unknown_avail = str(uuid.uuid4())
    r3 = client.get(f"/api/v1/candidates/{candidate_id}/availability/{unknown_avail}", headers=AUTH)
    assert r3.status_code == 404

    # List for unknown candidate
    unknown_candidate = str(uuid.uuid4())
    r4 = client.get(f"/api/v1/candidates/{unknown_candidate}/availability", headers=AUTH)
    assert r4.status_code == 404
