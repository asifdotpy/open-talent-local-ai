"""Test cases for user profile creation endpoint."""

from fastapi import status


class TestUserProfileCreation:
    """Test cases for user profile creation endpoint."""

    def test_create_user_profile_success(self, client):
        """Test successful user profile creation."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
        }

        response = client.post("/users/profile", json=user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert "id" in data
        assert "created_at" in data

    def test_create_user_profile_minimal_data(self, client):
        """Test user profile creation with minimal required data."""
        user_data = {
            "username": "testuser2",
            "email": "test2@example.com",
            # full_name is optional
        }

        response = client.post("/users/profile", json=user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert data["full_name"] is None

    def test_create_user_profile_duplicate_username(self, client):
        """Test user profile creation with duplicate username."""
        user_data = {
            "username": "testuser",
            "email": "test1@example.com",
            "full_name": "Test User 1",
        }

        # Create first user
        response1 = client.post("/users/profile", json=user_data)
        assert response1.status_code == status.HTTP_201_CREATED

        # Try to create second user with same username
        user_data2 = {
            "username": "testuser",  # Same username
            "email": "test2@example.com",
            "full_name": "Test User 2",
        }
        response2 = client.post("/users/profile", json=user_data2)

        assert response2.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in response2.json()["detail"]

    def test_create_user_profile_duplicate_email(self, client):
        """Test user profile creation with duplicate email."""
        user_data = {
            "username": "testuser1",
            "email": "test@example.com",
            "full_name": "Test User 1",
        }

        # Create first user
        response1 = client.post("/users/profile", json=user_data)
        assert response1.status_code == status.HTTP_201_CREATED

        # Try to create second user with same email
        user_data2 = {
            "username": "testuser2",
            "email": "test@example.com",  # Same email
            "full_name": "Test User 2",
        }
        response2 = client.post("/users/profile", json=user_data2)

        assert response2.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in response2.json()["detail"]

    def test_create_user_profile_invalid_data(self, client):
        """Test user profile creation with invalid data."""
        # Test with missing required fields
        invalid_data = {
            "username": "te",  # Too short (minimum 3 chars)
            "email": "invalid-email",  # Invalid email format
        }

        response = client.post("/users/profile", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_user_profile_long_username(self, client):
        """Test user profile creation with username too long."""
        invalid_data = {
            "username": "a" * 51,  # Too long (max 50 chars)
            "email": "test@example.com",
        }

        response = client.post("/users/profile", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_user_profile_empty_data(self, client):
        """Test user profile creation with empty data."""
        response = client.post("/users/profile", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestOtherEndpoints:
    """Test other endpoints for basic functionality."""

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "User Service is running!"

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database_connection"] == "ok"
