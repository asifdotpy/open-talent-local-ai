import uuid

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)
AUTH = {"Authorization": "Bearer test-token"}


def test_assessment_crud_happy_path():
    # Create candidate
    cand = {
        "email": "assessment.user@example.com",
        "first_name": "Assessment",
        "last_name": "Tester",
    }
    r = client.post("/api/v1/candidates", json=cand, headers=AUTH)
    assert r.status_code == 201
    candidate_id = r.json()["id"]

    # Create assessment
    payload = {
        "title": "Technical Coding Test",
        "description": "30-minute Python algorithm challenge",
        "assessment_type": "coding",
        "status": "pending",
    }
    r2 = client.post(f"/api/v1/candidates/{candidate_id}/assessments", json=payload, headers=AUTH)
    assert r2.status_code == 201
    assessment = r2.json()
    assessment_id = assessment["id"]
    assert assessment["status"] == "pending"
    assert assessment["assessment_type"] == "coding"

    # List assessments
    r3 = client.get(f"/api/v1/candidates/{candidate_id}/assessments", headers=AUTH)
    assert r3.status_code == 200
    items = r3.json()
    assert any(a["id"] == assessment_id for a in items)

    # Get assessment
    r4 = client.get(f"/api/v1/candidates/{candidate_id}/assessments/{assessment_id}", headers=AUTH)
    assert r4.status_code == 200
    assert r4.json()["id"] == assessment_id

    # Update assessment with score and status
    upd = {"status": "completed", "score": 85.5}
    r5 = client.put(f"/api/v1/candidates/{candidate_id}/assessments/{assessment_id}", json=upd, headers=AUTH)
    assert r5.status_code == 200
    assert r5.json()["status"] == "completed"
    assert r5.json()["score"] == 85.5

    # Delete assessment
    r6 = client.delete(f"/api/v1/candidates/{candidate_id}/assessments/{assessment_id}", headers=AUTH)
    assert r6.status_code == 204


def test_assessment_unauthorized_and_not_found():
    # Create candidate
    cand = {"email": "assessment.noauth@example.com", "first_name": "No", "last_name": "Auth"}
    r = client.post("/api/v1/candidates", json=cand, headers=AUTH)
    assert r.status_code == 201
    candidate_id = r.json()["id"]

    # Create assessment without auth
    payload = {"title": "Unauthorized Assessment", "assessment_type": "technical"}
    r2 = client.post(f"/api/v1/candidates/{candidate_id}/assessments", json=payload)
    assert r2.status_code == 401

    # Get assessment with unknown ID
    unknown_assessment = str(uuid.uuid4())
    r3 = client.get(f"/api/v1/candidates/{candidate_id}/assessments/{unknown_assessment}", headers=AUTH)
    assert r3.status_code == 404

    # List for unknown candidate
    unknown_candidate = str(uuid.uuid4())
    r4 = client.get(f"/api/v1/candidates/{unknown_candidate}/assessments", headers=AUTH)
    assert r4.status_code == 404
