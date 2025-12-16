# User Service Test Suite Documentation

**Last Updated:** December 14, 2025  
**Test Coverage:** Unit + Integration Tests  
**Database:** PostgreSQL 15 (Docker Compose)

## Test Suite Overview

The User Service test suite provides comprehensive coverage of:

1. **Unit Tests** - Fast, isolated tests with no external dependencies
   - JWT verification and claims extraction
   - RBAC (Role-Based Access Control)
   - Pydantic model validation

2. **Integration Tests** - Tests against real Docker Compose database
   - PostgreSQL Row-Level Security (RLS) policies
   - API endpoints with JWT authentication
   - Multi-tenant isolation
   - Cross-role access control

## Test Structure

```
tests/
├── __init__.py                    # Tests package
├── conftest.py                    # Shared fixtures and test configuration
├── test_jwt_utils.py              # Unit tests for JWT verification
├── test_rls_policies.py           # Integration tests for PostgreSQL RLS
└── test_api_endpoints.py          # Integration tests for API endpoints
```

## Running Tests

### Quick Start

```bash
# Run all tests
cd /home/asif1/open-talent/services/user-service
./run-tests.sh
```

### Run Specific Test Suites

```bash
# Activate virtual environment
source /home/asif1/open-talent/.venv-1/bin/activate

# Unit tests only (fast, no DB required)
PYTHONPATH=. pytest tests/test_jwt_utils.py -v

# Integration tests only (requires Docker Compose)
PYTHONPATH=. pytest tests/test_rls_policies.py -v -m integration
PYTHONPATH=. pytest tests/test_api_endpoints.py -v -m integration

# Run specific test class
PYTHONPATH=. pytest tests/test_jwt_utils.py::TestJWTClaims -v

# Run specific test method
PYTHONPATH=. pytest tests/test_jwt_utils.py::TestJWTClaims::test_jwt_claims_valid -v
```

### Run with Coverage

```bash
# Coverage report in terminal
PYTHONPATH=. pytest tests/ --cov=app --cov-report=term-missing

# Generate HTML coverage report
PYTHONPATH=. pytest tests/ --cov=app --cov-report=html

# View HTML report
python -m http.server 8000 -d htmlcov
# Open: http://localhost:8000
```

## Test Categories

### Unit Tests (test_jwt_utils.py)

**Purpose:** Test JWT verification, claims extraction, and RBAC logic in isolation.

**Test Classes:**

1. **TestJWTClaims** - JWT claims model validation
   - `test_jwt_claims_valid` - Valid JWT claims creation
   - `test_jwt_claims_minimal` - Claims with only required fields
   - `test_jwt_claims_missing_email` - Validation fails without email

2. **TestSecurityServiceVerification** - JWT verification via Security Service
   - `test_verify_jwt_with_security_service_success` - Successful verification
   - `test_verify_jwt_with_security_service_invalid` - Invalid token rejection
   - `test_verify_jwt_with_security_service_timeout` - Timeout handling

3. **TestLocalJWTVerification** - Local JWT verification fallback
   - `test_verify_jwt_locally_valid` - Valid JWT token verification
   - `test_verify_jwt_locally_expired` - Expired token rejection
   - `test_verify_jwt_locally_invalid_signature` - Invalid signature rejection
   - `test_verify_jwt_locally_malformed` - Malformed token rejection

4. **TestGetJWTClaims** - JWT claims extraction from Authorization header
   - `test_get_jwt_claims_valid_token` - Successful claims extraction
   - `test_get_jwt_claims_missing_header` - Missing Authorization header
   - `test_get_jwt_claims_invalid_format` - Invalid header format
   - `test_get_jwt_claims_wrong_scheme` - Wrong authentication scheme
   - `test_get_jwt_claims_missing_email` - Token without email claim

5. **TestRequireRole** - Role-based access control (RBAC)
   - `test_require_role_admin_allowed` - Admin role requirement passes
   - `test_require_role_admin_denied` - Non-admin role rejection
   - `test_require_role_multiple_allowed` - Multiple allowed roles
   - `test_require_role_no_role_in_claims` - Missing role rejection
   - `test_require_role_case_sensitive` - Case-sensitive role comparison

**Run Command:**
```bash
PYTHONPATH=. pytest tests/test_jwt_utils.py -v
```

### Integration Tests - PostgreSQL RLS (test_rls_policies.py)

**Purpose:** Verify PostgreSQL Row-Level Security policies enforce correct access control.

**Test Classes:**

1. **TestUsersTableRLS** - RLS policies on users table
   - `test_admin_can_select_all_users` - Admin sees all tenants
   - `test_recruiter_tenant_isolation` - Recruiter sees only their tenant
   - `test_candidate_can_only_select_self` - Candidate sees only themselves
   - `test_recruiter_can_insert_within_tenant` - Recruiter can create users in tenant
   - `test_recruiter_cannot_insert_different_tenant` - Cross-tenant insert denied
   - `test_admin_can_delete_any_user` - Admin can delete any user

2. **TestUserProfilesTableRLS** - RLS policies on user_profiles table
   - `test_admin_can_access_all_profiles` - Admin sees all profiles
   - `test_candidate_can_access_own_profile` - Candidate sees own profile

3. **TestUserPreferencesTableRLS** - RLS policies on user_preferences table
   - `test_candidate_can_manage_own_preferences` - Candidate can CRUD own preferences

4. **TestUserActivityTableRLS** - RLS policies on user_activity table
   - `test_recruiter_can_view_tenant_activity` - Recruiter sees tenant activity

5. **TestUserSessionsTableRLS** - RLS policies on user_sessions table
   - `test_candidate_can_view_own_sessions` - Candidate sees own sessions

**Run Command:**
```bash
# Requires Docker Compose running
docker-compose up -d
PYTHONPATH=. pytest tests/test_rls_policies.py -v -m integration
```

### Integration Tests - API Endpoints (test_api_endpoints.py)

**Purpose:** Test API endpoints with real HTTP requests and JWT authentication.

**Test Classes:**

1. **TestHealthEndpoint** - Health check endpoint
   - `test_health_check_no_auth` - Health endpoint accessible without auth

2. **TestUserEndpoints** - User CRUD endpoints
   - `test_list_users_requires_auth` - Authentication required
   - `test_list_users_with_auth` - Admin can list users
   - `test_create_user` - Admin can create users
   - `test_get_user_by_id` - Get user by ID
   - `test_get_nonexistent_user` - 404 for nonexistent user
   - `test_update_user` - Admin can update users
   - `test_delete_user` - Admin can delete users
   - `test_recruiter_tenant_isolation` - Recruiter sees only tenant users

3. **TestUserProfileEndpoints** - User profile endpoints
   - `test_create_user_profile` - Create user profile
   - `test_get_user_profile` - Get user profile

4. **TestUserPreferencesEndpoints** - User preferences endpoints
   - `test_create_user_preferences` - Candidate can create preferences

5. **TestSearchAndFilters** - Search and filter functionality
   - `test_search_users_by_email` - Search users by email
   - `test_filter_users_by_role` - Filter users by role
   - `test_pagination` - Pagination parameters

**Run Command:**
```bash
# Requires Docker Compose running
docker-compose up -d
PYTHONPATH=. pytest tests/test_api_endpoints.py -v -m integration
```

## Test Fixtures (conftest.py)

Shared fixtures available to all tests:

### Database Fixtures

- **`test_engine`** - Test database engine (session scope)
- **`test_db`** - Test database session with RLS context (function scope)
- **`test_client`** - FastAPI AsyncClient with test DB override (function scope)

### Authentication Fixtures

- **`admin_token`** - Valid JWT token for admin user
- **`recruiter_token`** - Valid JWT token for recruiter user
- **`candidate_token`** - Valid JWT token for candidate user
- **`admin_claims`** - Admin JWT claims object
- **`recruiter_claims`** - Recruiter JWT claims object
- **`candidate_claims`** - Candidate JWT claims object
- **`auth_headers_admin`** - Authorization headers with admin token
- **`auth_headers_recruiter`** - Authorization headers with recruiter token
- **`auth_headers_candidate`** - Authorization headers with candidate token

### Sample Data Fixtures

- **`sample_user_data`** - Sample user creation data
- **`sample_profile_data`** - Sample user profile data
- **`sample_preferences_data`** - Sample user preferences data

### Fixture Usage Example

```python
@pytest.mark.asyncio
async def test_admin_can_create_user(
    test_client: AsyncClient,
    admin_token: str,
    sample_user_data: dict,
):
    """Admin can create users."""
    response = await test_client.post(
        "/api/v1/users",
        json=sample_user_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
```

## Test Configuration (pytest.ini)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
pythonpath = .
addopts = -v --strict-markers --tb=short
markers =
    unit: Unit tests (fast, no external dependencies)
    integration: Integration tests (requires database)
    slow: Slow running tests
asyncio_mode = auto
```

## Prerequisites

### Docker Compose Services

Integration tests require Docker Compose services to be running:

```bash
# Start services
docker-compose up -d

# Verify services
docker ps | grep user_service
# Should show:
# - user_service_db (postgres:15-alpine)
# - user_service_postgrest (postgrest/postgrest:v12.2.0)
```

### Python Dependencies

All test dependencies are installed:

```bash
# Test framework
- pytest               # Test runner
- pytest-asyncio       # Async test support
- pytest-cov           # Coverage reporting
- faker                # Test data generation

# Already installed for service
- httpx                # Async HTTP client (for API tests)
- pyjwt                # JWT token generation
```

## Test Database

Integration tests use a separate test database to avoid polluting production data:

- **Production DB:** `user_service` (port 54322)
- **Test DB:** `user_service_test` (created automatically)

Test database is automatically:
- Created before tests run (session scope)
- Populated with schema (via SQLAlchemy `create_all`)
- Rolled back after each test (function scope)
- Dropped after test session completes

## Mocking Strategy

### Unit Tests

Unit tests mock external dependencies:

```python
from unittest.mock import patch, AsyncMock

@patch("app.utils.verify_jwt_with_security_service")
async def test_with_mock(mock_verify):
    mock_verify.return_value = {"valid": True, "email": "user@example.com"}
    # Test code here
```

### Integration Tests

Integration tests use real database but may mock Security Service:

```python
@patch("app.utils.verify_jwt_with_security_service")
async def test_api_endpoint(mock_verify, test_client):
    # Mock Security Service JWT verification
    mock_verify.return_value = {"valid": True, "email": "admin@example.com"}
    
    # Test against real database
    response = await test_client.get("/api/v1/users")
```

## Coverage Goals

| Component | Target Coverage | Current |
|-----------|----------------|---------|
| **app/utils.py** (JWT) | 90%+ | TBD |
| **app/routers.py** (API) | 80%+ | TBD |
| **app/models.py** | 70%+ | TBD |
| **app/schemas.py** | 70%+ | TBD |
| **Overall** | 75%+ | TBD |

## Common Test Patterns

### Testing Authentication

```python
@pytest.mark.asyncio
async def test_endpoint_requires_auth(test_client):
    """Test endpoint rejects requests without JWT."""
    response = await test_client.get("/api/v1/users")
    assert response.status_code == 401
```

### Testing RBAC

```python
@pytest.mark.asyncio
async def test_admin_only_endpoint(
    test_client,
    admin_token,
    candidate_token,
):
    """Test admin-only endpoint rejects non-admin users."""
    # Admin succeeds
    response = await test_client.delete(
        "/api/v1/users/123",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    
    # Candidate fails
    response = await test_client.delete(
        "/api/v1/users/123",
        headers={"Authorization": f"Bearer {candidate_token}"}
    )
    assert response.status_code == 403
```

### Testing RLS Policies

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_rls_policy(test_db):
    """Test PostgreSQL RLS policy enforcement."""
    # Set RLS context
    await test_db.execute(text("SET app.user_role = 'recruiter'"))
    await test_db.execute(text("SET app.tenant_id = 'tenant1'"))
    
    # Query should only return tenant1 users
    result = await test_db.execute(text("SELECT tenant_id FROM users"))
    for row in result:
        assert row[0] == "tenant1"
```

## Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'app'`

**Solution:** Set `PYTHONPATH=.` before running pytest:
```bash
PYTHONPATH=. pytest tests/ -v
```

### Database Connection Errors

**Problem:** `Connection refused` or `Database not found`

**Solution:**
1. Start Docker Compose: `docker-compose up -d`
2. Verify database is running: `docker ps | grep user_service_db`
3. Check database URL in `.env`: `DATABASE_URL=postgresql+asyncpg://...`

### RLS Policy Failures

**Problem:** RLS tests fail with "insufficient privileges"

**Solution:**
1. Verify RLS policies are applied: `docker exec user_service_db psql -U user_service -d user_service -c "\d+ users"`
2. Re-run migrations: `alembic upgrade head`
3. Check session variables are set in test fixtures

### Async Test Warnings

**Problem:** `RuntimeWarning: coroutine was never awaited`

**Solution:** Mark async tests with `@pytest.mark.asyncio`:
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

## CI/CD Integration

Tests can be run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    docker-compose up -d
    sleep 5  # Wait for DB to be ready
    source .venv-1/bin/activate
    PYTHONPATH=. pytest tests/ --cov=app --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
```

## Next Steps

1. **Increase Coverage:** Add more tests for edge cases
2. **Performance Tests:** Add tests for bulk operations, pagination
3. **Load Tests:** Add locust/k6 tests for concurrent users
4. **E2E Tests:** Add Playwright/Selenium tests for UI flows
5. **Contract Tests:** Add Pact tests for Security Service integration

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
