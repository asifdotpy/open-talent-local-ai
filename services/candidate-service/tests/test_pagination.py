"""Test pagination for list endpoints."""
import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)
AUTH = {"Authorization": "Bearer test-token"}


@pytest.fixture(autouse=True)
def setup_test_data():
    """Create test data for pagination tests."""
    # Create 15 test candidates
    candidates = []
    for i in range(15):
        payload = {
            "email": f"candidate{i}@example.com",
            "first_name": f"User{i}",
            "last_name": f"Test{i}",
            "phone": "+12345678900",
            "resume_url": "https://example.com/resume.pdf",
        }
        r = client.post("/api/v1/candidates", json=payload, headers=AUTH)
        if r.status_code == 201:
            candidates.append(r.json())

    # Create 10 applications
    if candidates:
        for i in range(10):
            payload = {
                "candidate_id": candidates[i % len(candidates)]["id"],
                "job_id": f"job-{i}",
                "cover_letter": f"I am interested in job {i}",
                "status": "applied",
            }
            client.post("/api/v1/applications", json=payload, headers=AUTH)

    yield

    # Cleanup is handled by the app's cleanup on candidate deletion


def test_list_candidates_pagination_first_page():
    """Test first page of candidates pagination."""
    r = client.get("/api/v1/candidates?offset=0&limit=5", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 5
    assert data["offset"] == 0
    assert data["limit"] == 5
    assert len(data["items"]) <= 5
    assert "has_next" in data
    assert "has_previous" in data
    assert "page" in data
    assert "total_pages" in data


def test_list_candidates_pagination_middle_page():
    """Test middle page of candidates pagination."""
    r = client.get("/api/v1/candidates?offset=5&limit=5", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["offset"] == 5
    assert data["limit"] == 5
    assert data["page"] == 2  # (5 // 5) + 1 = 2


def test_list_candidates_pagination_default():
    """Test default pagination parameters."""
    r = client.get("/api/v1/candidates", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["offset"] == 0
    assert data["limit"] == 20  # default
    assert "items" in data


def test_list_candidates_pagination_has_next():
    """Test has_next flag."""
    # Get first 5 items when there are more than 5 total
    r = client.get("/api/v1/candidates?offset=0&limit=5", headers=AUTH)
    data = r.json()
    if data["total"] > 5:
        assert data["has_next"] is True
    else:
        assert data["has_next"] is False


def test_list_candidates_pagination_has_previous():
    """Test has_previous flag."""
    # Offset 0 should have no previous
    r = client.get("/api/v1/candidates?offset=0&limit=5", headers=AUTH)
    data = r.json()
    assert data["has_previous"] is False

    # Offset > 0 should have previous
    r = client.get("/api/v1/candidates?offset=5&limit=5", headers=AUTH)
    data = r.json()
    if data["total"] > 5:
        assert data["has_previous"] is True


def test_list_candidates_pagination_max_limit():
    """Test maximum limit enforcement."""
    r = client.get("/api/v1/candidates?limit=50", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["limit"] == 50  # Should accept 50 (valid)


def test_list_candidates_pagination_invalid_limit():
    """Test limit validation."""
    r = client.get("/api/v1/candidates?limit=150", headers=AUTH)
    assert r.status_code == 422  # Validation error - limit > 100


def test_list_candidates_pagination_total_pages():
    """Test total_pages calculation."""
    r = client.get("/api/v1/candidates?offset=0&limit=5", headers=AUTH)
    data = r.json()
    total = data["total"]
    expected_pages = (total + 5 - 1) // 5  # (total + limit - 1) // limit
    assert data["total_pages"] == expected_pages


def test_list_applications_pagination():
    """Test applications list pagination."""
    r = client.get("/api/v1/applications?offset=0&limit=5", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "total" in data
    assert "offset" in data
    assert "limit" in data
    assert "items" in data
    assert "has_next" in data
    assert "has_previous" in data


def test_list_interviews_pagination():
    """Test interviews list pagination."""
    # Create a candidate first
    payload = {
        "email": "interview_test@example.com",
        "first_name": "Interview",
        "last_name": "Test",
        "phone": "+12345678900",
        "resume_url": "https://example.com/resume.pdf",
    }
    r = client.post("/api/v1/candidates", json=payload, headers=AUTH)
    candidate_id = r.json()["id"]

    # Create some interviews
    from datetime import datetime, timedelta

    for i in range(5):
        interview_payload = {
            "title": f"Interview {i}",
            "scheduled_at": (datetime.now() + timedelta(days=i)).isoformat(),
            "interviewer": f"Interviewer {i}",
            "location": "Remote",
            "status": "scheduled",
        }
        client.post(
            f"/api/v1/candidates/{candidate_id}/interviews", json=interview_payload, headers=AUTH
        )

    # Test pagination
    r = client.get(f"/api/v1/candidates/{candidate_id}/interviews?offset=0&limit=2", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["offset"] == 0
    assert data["limit"] == 2
    assert len(data["items"]) <= 2


def test_list_assessments_pagination():
    """Test assessments list pagination."""
    # Create a candidate first
    payload = {
        "email": "assess_test@example.com",
        "first_name": "Assessment",
        "last_name": "Test",
        "phone": "+12345678900",
        "resume_url": "https://example.com/resume.pdf",
    }
    r = client.post("/api/v1/candidates", json=payload, headers=AUTH)
    candidate_id = r.json()["id"]

    # Create some assessments
    for i in range(5):
        assess_payload = {
            "title": f"Assessment {i}",
            "description": f"Description {i}",
            "assessment_type": "coding",
            "status": "pending",
        }
        client.post(
            f"/api/v1/candidates/{candidate_id}/assessments", json=assess_payload, headers=AUTH
        )

    # Test pagination
    r = client.get(f"/api/v1/candidates/{candidate_id}/assessments?offset=0&limit=2", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["offset"] == 0
    assert data["limit"] == 2
    assert len(data["items"]) <= 2


def test_list_availability_pagination():
    """Test availability list pagination."""
    # Create a candidate first
    payload = {
        "email": "avail_test@example.com",
        "first_name": "Availability",
        "last_name": "Test",
        "phone": "+12345678900",
        "resume_url": "https://example.com/resume.pdf",
    }
    r = client.post("/api/v1/candidates", json=payload, headers=AUTH)
    candidate_id = r.json()["id"]

    # Create some availability slots
    from datetime import datetime, timedelta

    for i in range(5):
        avail_payload = {
            "start_time": (datetime.now() + timedelta(days=i)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=i, hours=1)).isoformat(),
            "timezone": "UTC",
            "is_available": True,
        }
        client.post(
            f"/api/v1/candidates/{candidate_id}/availability", json=avail_payload, headers=AUTH
        )

    # Test pagination
    r = client.get(f"/api/v1/candidates/{candidate_id}/availability?offset=0&limit=2", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["offset"] == 0
    assert data["limit"] == 2
    assert len(data["items"]) <= 2


def test_list_skills_pagination():
    """Test skills list pagination."""
    # Create a candidate first
    payload = {
        "email": "skills_test@example.com",
        "first_name": "Skills",
        "last_name": "Test",
        "phone": "+12345678900",
        "resume_url": "https://example.com/resume.pdf",
    }
    r = client.post("/api/v1/candidates", json=payload, headers=AUTH)
    candidate_id = r.json()["id"]

    # Add some skills
    skills = ["Python", "FastAPI", "PostgreSQL", "React", "Docker"]
    for skill in skills:
        skill_payload = {"skill": skill, "proficiency": "advanced"}
        client.post(f"/api/v1/candidates/{candidate_id}/skills", json=skill_payload, headers=AUTH)

    # Test pagination
    r = client.get(f"/api/v1/candidates/{candidate_id}/skills?offset=0&limit=2", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["offset"] == 0
    assert data["limit"] == 2
    assert len(data["skills"]) <= 2


def test_pagination_offset_boundary():
    """Test pagination at offset boundary."""
    # Get candidates with very high offset
    r = client.get("/api/v1/candidates?offset=1000&limit=10", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["offset"] == 1000
    # items should be empty or have fewer items if total < offset
    assert isinstance(data["items"], list)


def test_pagination_single_item():
    """Test pagination with single item per page."""
    r = client.get("/api/v1/candidates?offset=0&limit=1", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["limit"] == 1
    assert len(data["items"]) <= 1


def test_pagination_metadata_consistency():
    """Test pagination metadata consistency."""
    r = client.get("/api/v1/candidates?offset=10&limit=5", headers=AUTH)
    assert r.status_code == 200
    data = r.json()

    # Verify calculations
    expected_page = (10 // 5) + 1  # = 3
    assert data["page"] == expected_page

    expected_has_previous = 10 > 0  # = True
    assert data["has_previous"] == expected_has_previous

    expected_has_next = data["total"] > (10 + 5)
    assert data["has_next"] == expected_has_next
