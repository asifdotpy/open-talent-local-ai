from app.core.config import settings
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test the health check endpoint."""
    response = client.get(f"{settings.API_V1_STR}/system/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_db_status(client: TestClient):
    """Test the database status endpoint."""
    response = client.get(f"{settings.API_V1_STR}/system/db-status")
    assert response.status_code == 200
    data = response.json()
    print(f"DB Status response: {data}")  # Add debug print
    assert data["db_status"] == "ok"
    assert "system_version" in data
