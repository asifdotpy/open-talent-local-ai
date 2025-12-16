# User Service Tests - Quick Reference

## Run Tests

```bash
# All tests with coverage
./run-tests.sh

# Unit tests only (fast)
PYTHONPATH=. pytest tests/test_jwt_utils.py -v

# Integration tests only
PYTHONPATH=. pytest tests/ -m integration -v

# Specific test
PYTHONPATH=. pytest tests/test_jwt_utils.py::TestJWTClaims::test_jwt_claims_valid -v
```

## Test Structure

```
tests/
├── conftest.py              # Fixtures (DB, auth, sample data)
├── test_jwt_utils.py        # Unit: JWT verification (20+ tests)
├── test_rls_policies.py     # Integration: RLS policies (15+ tests)
└── test_api_endpoints.py    # Integration: API endpoints (20+ tests)
```

## Prerequisites

```bash
# Start Docker Compose
docker-compose up -d

# Verify services running
docker ps | grep user_service
```

## Fixtures Available

**Database:**
- `test_db` - Database session with RLS context
- `test_client` - FastAPI AsyncClient

**Authentication:**
- `admin_token`, `recruiter_token`, `candidate_token`
- `admin_claims`, `recruiter_claims`, `candidate_claims`
- `auth_headers_admin`, `auth_headers_recruiter`, `auth_headers_candidate`

**Sample Data:**
- `sample_user_data`, `sample_profile_data`, `sample_preferences_data`

## Common Test Patterns

### Test Authentication
```python
async def test_requires_auth(test_client):
    response = await test_client.get("/api/v1/users")
    assert response.status_code == 401
```

### Test RBAC
```python
@patch("app.utils.verify_jwt_with_security_service")
async def test_admin_only(mock_verify, test_client, admin_token):
    mock_verify.return_value = {"valid": True}
    response = await test_client.delete("/api/v1/users/123")
    assert response.status_code == 200
```

### Test RLS Policy
```python
async def test_tenant_isolation(test_db):
    await test_db.execute(text("SET app.tenant_id = 'tenant1'"))
    result = await test_db.execute(text("SELECT tenant_id FROM users"))
    assert all(row[0] == "tenant1" for row in result)
```

## Test Coverage

| Component | Tests | Coverage Target |
|-----------|-------|-----------------|
| JWT Utils | 20+ | 90%+ |
| RLS Policies | 15+ | 90%+ |
| API Endpoints | 20+ | 80%+ |
| **Total** | **55+** | **75%+** |

## Troubleshooting

**Import Error:**
```bash
# Always set PYTHONPATH
PYTHONPATH=. pytest tests/ -v
```

**Database Not Found:**
```bash
# Start Docker Compose
docker-compose up -d
sleep 5  # Wait for DB to be ready
```

**RLS Policy Failures:**
```bash
# Re-apply migrations
alembic upgrade head
```

## Documentation

- [TEST_SUITE_DOCUMENTATION.md](TEST_SUITE_DOCUMENTATION.md) - Full guide
- [TEST_IMPLEMENTATION_COMPLETE.md](TEST_IMPLEMENTATION_COMPLETE.md) - Summary
