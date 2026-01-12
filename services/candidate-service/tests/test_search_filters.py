from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
AUTH = {"Authorization": "Bearer test-token"}


def test_search_with_basic_query():
    # Create test candidates
    cand1 = {"email": "python.dev@example.com", "first_name": "Alice", "last_name": "Python"}
    cand2 = {"email": "java.dev@example.com", "first_name": "Bob", "last_name": "Java"}
    r1 = client.post("/api/v1/candidates", json=cand1, headers=AUTH)
    r2 = client.post("/api/v1/candidates", json=cand2, headers=AUTH)

    assert r1.status_code == 201
    assert r2.status_code == 201

    # Search for Python developer
    r3 = client.get("/api/v1/candidates/search?query=Python", headers=AUTH)
    assert r3.status_code == 200
    result = r3.json()
    assert "total" in result
    assert "query" in result
    assert "filters_applied" in result
    assert "results" in result


def test_search_with_skills_filter():
    # Create candidate with skills
    cand = {"email": "skilled.dev@example.com", "first_name": "Charlie", "last_name": "Developer"}
    r = client.post("/api/v1/candidates", json=cand, headers=AUTH)
    assert r.status_code == 201
    candidate_id = r.json()["id"]

    # Add skills
    skill1 = {"skill": "Python", "proficiency": "advanced"}
    skill2 = {"skill": "FastAPI", "proficiency": "advanced"}
    client.post(f"/api/v1/candidates/{candidate_id}/skills", json=skill1, headers=AUTH)
    client.post(f"/api/v1/candidates/{candidate_id}/skills", json=skill2, headers=AUTH)

    # Search with skill filter
    r2 = client.get("/api/v1/candidates/search?query=developer&skills=Python", headers=AUTH)
    assert r2.status_code == 200
    result = r2.json()
    assert result["filters_applied"]["skills"] == ["python"]


def test_search_with_multiple_filters():
    # Create candidate
    cand = {"email": "senior.dev@example.com", "first_name": "Senior", "last_name": "Dev"}
    r = client.post("/api/v1/candidates", json=cand, headers=AUTH)
    assert r.status_code == 201
    candidate_id = r.json()["id"]

    # Add skills
    skills = [
        {"skill": "Python", "proficiency": "expert"},
        {"skill": "React", "proficiency": "advanced"},
        {"skill": "AWS", "proficiency": "advanced"},
    ]
    for skill in skills:
        client.post(f"/api/v1/candidates/{candidate_id}/skills", json=skill, headers=AUTH)

    # Search with multiple filters
    r2 = client.get(
        "/api/v1/candidates/search?query=developer&skills=Python,React&min_experience=3&location=NYC&tags=remote",
        headers=AUTH,
    )
    assert r2.status_code == 200
    result = r2.json()
    assert result["filters_applied"]["skills"] == ["python", "react"]
    assert result["filters_applied"]["min_experience"] == 3
    assert result["filters_applied"]["location"] == "nyc"
    assert result["filters_applied"]["tags"] == ["remote"]


def test_search_with_limit():
    # Search with custom limit
    r = client.get("/api/v1/candidates/search?query=test&limit=10", headers=AUTH)
    assert r.status_code == 200
    result = r.json()
    assert len(result["results"]) <= 10


def test_search_invalid_limit():
    # Limit too high (max 100)
    r = client.get("/api/v1/candidates/search?query=test&limit=1000", headers=AUTH)
    assert r.status_code == 422  # Validation error


def test_search_missing_query():
    # Missing required query parameter
    r = client.get("/api/v1/candidates/search", headers=AUTH)
    assert r.status_code == 422  # Validation error


def test_search_case_insensitive_filters():
    # Create candidate
    cand = {"email": "case.test@example.com", "first_name": "Case", "last_name": "Test"}
    r = client.post("/api/v1/candidates", json=cand, headers=AUTH)
    assert r.status_code == 201
    candidate_id = r.json()["id"]

    # Add skill with mixed case
    skill = {"skill": "JavaScript", "proficiency": "intermediate"}
    client.post(f"/api/v1/candidates/{candidate_id}/skills", json=skill, headers=AUTH)

    # Search with lowercase skill filter
    r2 = client.get("/api/v1/candidates/search?query=developer&skills=javascript", headers=AUTH)
    assert r2.status_code == 200
    result = r2.json()
    # Should match despite case difference
    assert result["filters_applied"]["skills"] == ["javascript"]
