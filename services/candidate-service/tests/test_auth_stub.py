"""Tests for authentication stub - verifies that:
1. Requests without Authorization header work (use DEFAULT_USER_ID)
2. Requests with test token work
3. Endpoints no longer return 401 Unauthorized
4. All endpoints are guarded but accessible with auth stub.
"""

import pytest
from fastapi.testclient import TestClient
from main import DEFAULT_USER_ID, TEST_TOKEN, app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestAuthStub:
    """Test authentication stub behavior."""

    def test_no_auth_header_returns_user(self, client):
        """Verify requests without auth header use DEFAULT_USER_ID."""
        response = client.get("/api/v1/candidates")
        assert (
            response.status_code == 200
        ), f"Expected 200, got {response.status_code}: {response.json()}"
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_with_test_token_returns_user(self, client):
        """Verify requests with test token work."""
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        response = client.get("/api/v1/candidates", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_with_invalid_token_still_works(self, client):
        """Verify requests with invalid token still work (fallback to default user)."""
        headers = {"Authorization": "Bearer invalid-token-xyz"}
        response = client.get("/api/v1/candidates", headers=headers)
        # Auth stub accepts any token for testing
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_malformed_auth_header_still_works(self, client):
        """Verify malformed auth headers don't break requests."""
        headers = {"Authorization": "NotBearer token"}
        response = client.get("/api/v1/candidates", headers=headers)
        assert response.status_code == 200

    def test_candidates_endpoint_accessible_without_401(self, client):
        """Verify candidates endpoint returns 200, not 401."""
        response = client.get("/api/v1/candidates")
        assert response.status_code != 401
        assert response.status_code == 200

    def test_applications_endpoint_accessible_without_401(self, client):
        """Verify applications endpoint doesn't return 401."""
        response = client.get("/api/v1/applications")
        assert response.status_code != 401

    def test_create_candidate_without_auth(self, client):
        """Verify POST endpoints work without explicit auth."""
        response = client.post(
            "/api/v1/candidates", json={"email": "test@example.com", "full_name": "Test User"}
        )
        # Should not return 401 Unauthorized
        assert response.status_code != 401
        # Should either succeed (201) or fail with validation error (422)
        assert response.status_code in [201, 422]

    def test_create_candidate_with_test_token(self, client):
        """Verify POST endpoints work with test token."""
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        response = client.post(
            "/api/v1/candidates",
            json={"email": "test2@example.com", "full_name": "Test User 2"},
            headers=headers,
        )
        assert response.status_code != 401

    def test_no_401_responses_in_list_endpoints(self, client):
        """Verify all list endpoints return 200, not 401."""
        endpoints = [
            "/api/v1/candidates",
            "/api/v1/applications",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert (
                response.status_code == 200
            ), f"{endpoint} returned {response.status_code}, expected 200"

    def test_auth_header_variations(self, client):
        """Verify different auth header formats are handled gracefully."""
        test_cases = [
            ("Bearer test-token-12345", 200),  # Valid test token
            ("bearer test-token-12345", 200),  # Lowercase scheme
            ("Bearer xyz", 200),  # Different token (still allowed)
            ("", 200),  # Empty header (uses default)
        ]

        for auth_value, expected_status in test_cases:
            headers = {}
            if auth_value:
                headers["Authorization"] = auth_value

            response = client.get("/api/v1/candidates", headers=headers)
            assert (
                response.status_code == expected_status
            ), f"Auth: '{auth_value}' returned {response.status_code}, expected {expected_status}"


class TestAuthStubIntegration:
    """Test auth stub with actual endpoint operations."""

    def test_create_and_list_workflow_without_auth(self, client):
        """Verify full create/list workflow works without explicit auth."""
        # Create a candidate
        create_response = client.post(
            "/api/v1/candidates",
            json={"email": "workflow@example.com", "full_name": "Workflow Test User"},
        )
        assert create_response.status_code in [201, 422]

        # List candidates
        list_response = client.get("/api/v1/candidates")
        assert list_response.status_code == 200
        data = list_response.json()
        assert isinstance(data, dict)
        assert "items" in data

    def test_create_and_list_workflow_with_token(self, client):
        """Verify full workflow works with test token."""
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}

        # Create
        create_response = client.post(
            "/api/v1/candidates",
            json={"email": "token-workflow@example.com", "full_name": "Token Workflow Test"},
            headers=headers,
        )
        assert create_response.status_code in [201, 422]

        # List
        list_response = client.get("/api/v1/candidates", headers=headers)
        assert list_response.status_code == 200


class TestAuthStubConstants:
    """Test auth stub configuration constants."""

    def test_test_token_is_defined(self):
        """Verify TEST_TOKEN constant is defined."""
        assert TEST_TOKEN is not None
        assert isinstance(TEST_TOKEN, str)
        assert len(TEST_TOKEN) > 0

    def test_default_user_id_is_defined(self):
        """Verify DEFAULT_USER_ID constant is defined."""
        assert DEFAULT_USER_ID is not None
        assert isinstance(DEFAULT_USER_ID, str)
        assert len(DEFAULT_USER_ID) > 0

    def test_constants_are_reasonable(self):
        """Verify constants have reasonable values."""
        assert "test" in TEST_TOKEN.lower()
        assert "test" in DEFAULT_USER_ID.lower()
