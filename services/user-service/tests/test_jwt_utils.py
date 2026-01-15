"""
Unit tests for JWT verification and claims extraction.

Tests:
- JWT verification with Security Service
- JWT local verification fallback
- Claims extraction and validation
- RBAC role enforcement
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import jwt
import pytest
from app.config import settings
from app.utils import (
    JWTClaims,
    get_jwt_claims,
    require_role,
    verify_jwt_locally,
    verify_jwt_with_security_service,
)
from fastapi import HTTPException


class TestJWTClaims:
    """Test JWT claims model validation."""

    def test_jwt_claims_valid(self):
        """Test valid JWT claims creation."""
        claims = JWTClaims(
            email="user@example.com",
            user_id="123",
            role="admin",
            tenant_id="tenant1",
            exp=1234567890,
            iat=1234567800,
        )
        assert claims.email == "user@example.com"
        assert claims.role == "admin"
        assert claims.tenant_id == "tenant1"

    def test_jwt_claims_minimal(self):
        """Test JWT claims with only required fields."""
        claims = JWTClaims(email="user@example.com")
        assert claims.email == "user@example.com"
        assert claims.role is None
        assert claims.tenant_id is None

    def test_jwt_claims_missing_email(self):
        """Test JWT claims validation fails without email."""
        with pytest.raises(Exception):
            JWTClaims()


@pytest.mark.asyncio
class TestSecurityServiceVerification:
    """Test JWT verification with Security Service."""

    async def test_verify_jwt_with_security_service_success(self):
        """Test successful JWT verification via Security Service."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"valid": True, "email": "user@example.com"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            result = await verify_jwt_with_security_service("valid_token")

            assert result["valid"] is True
            assert result["email"] == "user@example.com"

    async def test_verify_jwt_with_security_service_invalid(self):
        """Test JWT verification failure via Security Service."""
        mock_response = MagicMock()
        mock_response.status_code = 401

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            result = await verify_jwt_with_security_service("invalid_token")

            assert result["valid"] is False

    async def test_verify_jwt_with_security_service_timeout(self):
        """Test JWT verification fallback on timeout."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=Exception("Connection timeout")
            )

            result = await verify_jwt_with_security_service("token")

            assert result["valid"] is False
            assert "error" in result


class TestLocalJWTVerification:
    """Test local JWT verification fallback."""

    def test_verify_jwt_locally_valid(self):
        """Test valid JWT token local verification."""
        # Create valid token
        payload = {
            "email": "user@example.com",
            "role": "admin",
            "tenant_id": "tenant1",
            "exp": datetime.now(UTC).replace(tzinfo=None) + timedelta(minutes=30),
            "iat": datetime.now(UTC).replace(tzinfo=None),
        }
        token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

        result = verify_jwt_locally(token)

        assert result["email"] == "user@example.com"
        assert result["role"] == "admin"
        assert result["tenant_id"] == "tenant1"

    def test_verify_jwt_locally_expired(self):
        """Test expired JWT token rejection."""
        payload = {
            "email": "user@example.com",
            "exp": datetime.now(UTC).replace(tzinfo=None) - timedelta(minutes=1),  # Expired
        }
        token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

        with pytest.raises(HTTPException) as exc:
            verify_jwt_locally(token)

        assert exc.value.status_code == 401
        assert "expired" in exc.value.detail.lower()

    def test_verify_jwt_locally_invalid_signature(self):
        """Test JWT token with invalid signature."""
        payload = {"email": "user@example.com"}
        token = jwt.encode(payload, "wrong_secret", algorithm=settings.jwt_algorithm)

        with pytest.raises(HTTPException) as exc:
            verify_jwt_locally(token)

        assert exc.value.status_code == 401
        assert "invalid" in exc.value.detail.lower()

    def test_verify_jwt_locally_malformed(self):
        """Test malformed JWT token."""
        with pytest.raises(HTTPException) as exc:
            verify_jwt_locally("not.a.valid.token")

        assert exc.value.status_code == 401


@pytest.mark.asyncio
class TestGetJWTClaims:
    """Test JWT claims extraction from Authorization header."""

    async def test_get_jwt_claims_valid_token(self):
        """Test successful claims extraction."""
        payload = {
            "email": "user@example.com",
            "user_id": "123",
            "role": "recruiter",
            "tenant_id": "tenant1",
            "exp": datetime.now(UTC).replace(tzinfo=None) + timedelta(minutes=30),
        }
        token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

        with patch("app.utils.verify_jwt_with_security_service") as mock_verify:
            mock_verify.return_value = {"valid": True, "email": "user@example.com"}

            claims = await get_jwt_claims(authorization=f"Bearer {token}")

            assert claims.email == "user@example.com"
            assert claims.role == "recruiter"
            assert claims.tenant_id == "tenant1"

    async def test_get_jwt_claims_missing_header(self):
        """Test missing Authorization header."""
        with pytest.raises(HTTPException) as exc:
            await get_jwt_claims(authorization=None)

        assert exc.value.status_code == 401
        assert "missing" in exc.value.detail.lower()

    async def test_get_jwt_claims_invalid_format(self):
        """Test invalid Authorization header format."""
        with pytest.raises(HTTPException) as exc:
            await get_jwt_claims(authorization="InvalidFormat")

        assert exc.value.status_code == 401

    async def test_get_jwt_claims_wrong_scheme(self):
        """Test wrong authentication scheme."""
        with pytest.raises(HTTPException) as exc:
            await get_jwt_claims(authorization="Basic dXNlcjpwYXNz")

        assert exc.value.status_code == 401

    async def test_get_jwt_claims_missing_email(self):
        """Test token without email claim."""
        payload = {
            "user_id": "123",
            "exp": datetime.now(UTC).replace(tzinfo=None) + timedelta(minutes=30),
        }
        token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

        with patch("app.utils.verify_jwt_with_security_service") as mock_verify:
            mock_verify.return_value = {"valid": True}

            with pytest.raises(HTTPException) as exc:
                await get_jwt_claims(authorization=f"Bearer {token}")

            assert exc.value.status_code == 401
            assert "email" in exc.value.detail.lower()


@pytest.mark.asyncio
class TestRequireRole:
    """Test role-based access control (RBAC)."""

    async def test_require_role_admin_allowed(self):
        """Test admin role requirement passes."""
        claims = JWTClaims(email="admin@example.com", role="admin")
        checker = require_role("admin")

        result = await checker(claims)

        assert result.role == "admin"

    async def test_require_role_admin_denied(self):
        """Test non-admin role rejection."""
        claims = JWTClaims(email="user@example.com", role="candidate")
        checker = require_role("admin")

        with pytest.raises(HTTPException) as exc:
            await checker(claims)

        assert exc.value.status_code == 403
        assert "admin" in exc.value.detail.lower()

    async def test_require_role_multiple_allowed(self):
        """Test multiple allowed roles."""
        claims = JWTClaims(email="recruiter@example.com", role="recruiter")
        checker = require_role("admin", "recruiter")

        result = await checker(claims)

        assert result.role == "recruiter"

    async def test_require_role_no_role_in_claims(self):
        """Test rejection when role is missing from claims."""
        claims = JWTClaims(email="user@example.com", role=None)
        checker = require_role("admin")

        with pytest.raises(HTTPException) as exc:
            await checker(claims)

        assert exc.value.status_code == 403

    async def test_require_role_case_sensitive(self):
        """Test role comparison is case-sensitive."""
        claims = JWTClaims(email="user@example.com", role="Admin")  # Uppercase
        checker = require_role("admin")  # Lowercase

        with pytest.raises(HTTPException) as exc:
            await checker(claims)

        assert exc.value.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
