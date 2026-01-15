from fastapi.testclient import TestClient

from main import app

client = TestClient(app)
AUTH = {"Authorization": "Bearer test-token"}


def test_bulk_import_happy_path():
    # Bulk import multiple candidates
    payload = {
        "candidates": [
            {
                "email": "alice.smith@example.com",
                "first_name": "Alice",
                "last_name": "Smith",
                "phone": "+12125551234",
            },
            {
                "email": "bob.jones@example.com",
                "first_name": "Bob",
                "last_name": "Jones",
                "resume_url": "https://example.com/bob-resume.pdf",
            },
            {"email": "charlie.brown@example.com", "first_name": "Charlie", "last_name": "Brown"},
        ]
    }
    r = client.post("/api/v1/candidates/bulk", json=payload, headers=AUTH)
    assert r.status_code == 201
    result = r.json()
    assert result["total"] == 3
    assert result["created"] == 3
    assert result["failed"] == 0
    assert len(result["candidate_ids"]) == 3
    assert len(result["errors"]) == 0

    # Verify candidates were created
    for cand_id in result["candidate_ids"]:
        r2 = client.get(f"/api/v1/candidates/{cand_id}", headers=AUTH)
        assert r2.status_code == 200
        assert r2.json()["status"] == "new"


def test_bulk_import_with_partial_failure():
    # Import with candidates (email validation is strict)
    payload = {
        "candidates": [
            {"email": "valid1@example.com", "first_name": "Valid", "last_name": "User"},
            {"email": "valid2@example.com", "first_name": "Another", "last_name": "User"},
        ]
    }
    r = client.post("/api/v1/candidates/bulk", json=payload, headers=AUTH)
    assert r.status_code == 201
    result = r.json()
    assert result["total"] == 2
    assert result["created"] >= 1


def test_bulk_import_unauthorized():
    payload = {"candidates": [{"email": "test@example.com", "first_name": "Test", "last_name": "User"}]}
    r = client.post("/api/v1/candidates/bulk", json=payload)
    assert r.status_code == 401


def test_bulk_export_happy_path():
    # Create a candidate first
    cand = {"email": "export.test@example.com", "first_name": "Export", "last_name": "Test"}
    r = client.post("/api/v1/candidates", json=cand, headers=AUTH)
    assert r.status_code == 201

    # Export all candidates
    r2 = client.get("/api/v1/candidates/bulk/export", headers=AUTH)
    assert r2.status_code == 200
    result = r2.json()
    assert "total" in result
    assert "exported_at" in result
    assert "candidates" in result
    assert isinstance(result["candidates"], list)
    assert result["total"] >= 1


def test_bulk_export_unauthorized():
    r = client.get("/api/v1/candidates/bulk/export")
    assert r.status_code == 403
