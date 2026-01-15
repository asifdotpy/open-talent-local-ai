"""
Pytest configuration and shared fixtures for User Service tests.
"""

from datetime import UTC, datetime, timedelta

import jwt
import pytest
from app.config import settings
from app.utils import JWTClaims
from fastapi import Header, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

# Use NullPool for tests to avoid connection reuse issues with asyncpg
test_engine = create_async_engine(settings.database_url, poolclass=NullPool)
TestAsyncSessionLocal = async_sessionmaker(
    bind=test_engine, expire_on_commit=False, class_=AsyncSession
)


@pytest.fixture
async def client(test_db, seed_users):
    """Create a truly async test client with dependency overrides and seeded users."""
    from app.database import get_session
    from app.main import app
    from app.utils import get_jwt_claims
    from httpx import ASGITransport, AsyncClient

    # Override JWT claims
    async def override_get_jwt_claims(authorization: str = Header(None)):
        if not authorization:
            raise HTTPException(status_code=401, detail="Unauthorized")
        try:
            scheme, token = authorization.split(" ", 1)
            payload = jwt.decode(token, options={"verify_signature": False})
            return JWTClaims(**payload)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token")

    async def override_get_session():
        async with TestAsyncSessionLocal() as session:
            yield session

    async def override_get_session_with_rls(
        authorization: str = Header(None),
    ):
        if not authorization:
            raise HTTPException(status_code=401, detail="Unauthorized")
        claims = await override_get_jwt_claims(authorization)
        async with TestAsyncSessionLocal() as session:
            # Set RLS context variables
            await session.execute(text(f"SET LOCAL app.user_email = '{claims.email}';"))
            await session.execute(text(f"SET LOCAL app.user_role = '{claims.role}';"))
            await session.execute(text(f"SET LOCAL app.tenant_id = '{claims.tenant_id}';"))
            yield session

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_jwt_claims] = override_get_jwt_claims
    from app.database import get_session_with_rls

    app.dependency_overrides[get_session_with_rls] = override_get_session_with_rls

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_client(client):
    """Alias for client to support older tests."""
    yield client


@pytest.fixture(scope="session", autouse=True)
async def initialize_test_db():
    """Initialize the test database once for the entire session."""
    from app.models import Base

    async with test_engine.begin() as conn:
        # Drop and recreate schema to ensure clean state and correct Enum types
        await conn.execute(text("DROP SCHEMA public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))
        await conn.run_sync(Base.metadata.create_all)

        # Create a non-superuser for RLS testing
        await conn.execute(text("DROP ROLE IF EXISTS rls_test_user;"))
        await conn.execute(text("CREATE ROLE rls_test_user WITH LOGIN PASSWORD 'rls_test_pass';"))
        await conn.execute(text("GRANT ALL ON SCHEMA public TO rls_test_user;"))
        await conn.execute(text("GRANT ALL ON ALL TABLES IN SCHEMA public TO rls_test_user;"))
        await conn.execute(text("GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO rls_test_user;"))
        await conn.execute(
            text("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO rls_test_user;")
        )

        # Enable RLS on all tables
        tables = ["users", "user_profiles", "user_preferences", "user_activity", "user_sessions"]
        for table in tables:
            await conn.execute(text(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;"))
            await conn.execute(text(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY;"))

        # Create RLS Policies (based on migration 0002)

        # USERS Table Policies
        await conn.execute(
            text(
                "CREATE POLICY users_admin_all ON users FOR ALL TO PUBLIC USING (current_setting('app.user_role', true) = 'admin');"
            )
        )
        await conn.execute(
            text(
                "CREATE POLICY users_tenant_select ON users FOR SELECT TO PUBLIC USING (tenant_id IS NOT NULL AND tenant_id = current_setting('app.tenant_id', true) AND current_setting('app.user_role', true) IN ('recruiter', 'candidate'));"
            )
        )
        await conn.execute(
            text(
                "CREATE POLICY users_self_select ON users FOR SELECT TO PUBLIC USING (email = current_setting('app.user_email', true));"
            )
        )
        await conn.execute(
            text(
                "CREATE POLICY users_tenant_insert ON users FOR INSERT TO PUBLIC WITH CHECK (current_setting('app.user_role', true) IN ('admin', 'recruiter') AND (current_setting('app.user_role', true) = 'admin' OR tenant_id = current_setting('app.tenant_id', true)));"
            )
        )
        await conn.execute(
            text(
                "CREATE POLICY users_tenant_update ON users FOR UPDATE TO PUBLIC USING (current_setting('app.user_role', true) = 'admin' OR (tenant_id = current_setting('app.tenant_id', true) AND current_setting('app.user_role', true) IN ('recruiter', 'candidate')) OR email = current_setting('app.user_email', true));"
            )
        )
        await conn.execute(
            text(
                "CREATE POLICY users_admin_delete ON users FOR DELETE TO PUBLIC USING (current_setting('app.user_role', true) = 'admin');"
            )
        )

        # USER_PROFILES Table Policies
        await conn.execute(
            text(
                "CREATE POLICY user_profiles_admin_all ON user_profiles FOR ALL TO PUBLIC USING (current_setting('app.user_role', true) = 'admin');"
            )
        )
        await conn.execute(
            text(
                "CREATE POLICY user_profiles_tenant_select ON user_profiles FOR SELECT TO PUBLIC USING (tenant_id IS NOT NULL AND tenant_id = current_setting('app.tenant_id', true) AND current_setting('app.user_role', true) IN ('recruiter', 'candidate'));"
            )
        )
        await conn.execute(
            text(
                "CREATE POLICY user_profiles_self_select ON user_profiles FOR SELECT TO PUBLIC USING (user_id IN (SELECT id FROM users WHERE email = current_setting('app.user_email', true)));"
            )
        )
        await conn.execute(
            text(
                "CREATE POLICY user_profiles_tenant_modify ON user_profiles FOR ALL TO PUBLIC USING (current_setting('app.user_role', true) = 'admin' OR tenant_id = current_setting('app.tenant_id', true) OR user_id IN (SELECT id FROM users WHERE email = current_setting('app.user_email', true)));"
            )
        )

        # USER_PREFERENCES Table Policies
        await conn.execute(
            text(
                "CREATE POLICY user_preferences_admin_all ON user_preferences FOR ALL TO PUBLIC USING (current_setting('app.user_role', true) = 'admin');"
            )
        )
        await conn.execute(
            text(
                "CREATE POLICY user_preferences_tenant_select ON user_preferences FOR SELECT TO PUBLIC USING (tenant_id IS NOT NULL AND tenant_id = current_setting('app.tenant_id', true) AND current_setting('app.user_role', true) IN ('recruiter', 'candidate'));"
            )
        )
        await conn.execute(
            text(
                "CREATE POLICY user_preferences_self_all ON user_preferences FOR ALL TO PUBLIC USING (user_id IN (SELECT id FROM users WHERE email = current_setting('app.user_email', true)));"
            )
        )

        # USER_ACTIVITY Table Policies
        await conn.execute(
            text(
                "CREATE POLICY user_activity_admin_all ON user_activity FOR ALL TO PUBLIC USING (current_setting('app.user_role', true) = 'admin');"
            )
        )
        await conn.execute(
            text(
                "CREATE POLICY user_activity_tenant_select ON user_activity FOR SELECT TO PUBLIC USING (tenant_id IS NOT NULL AND tenant_id = current_setting('app.tenant_id', true) AND current_setting('app.user_role', true) IN ('recruiter', 'candidate'));"
            )
        )
        await conn.execute(
            text(
                "CREATE POLICY user_activity_self_all ON user_activity FOR ALL TO PUBLIC USING (user_id IN (SELECT id FROM users WHERE email = current_setting('app.user_email', true)));"
            )
        )

        # USER_SESSIONS Table Policies
        await conn.execute(
            text(
                "CREATE POLICY user_sessions_admin_all ON user_sessions FOR ALL TO PUBLIC USING (current_setting('app.user_role', true) = 'admin');"
            )
        )
        await conn.execute(
            text(
                "CREATE POLICY user_sessions_tenant_select ON user_sessions FOR SELECT TO PUBLIC USING (tenant_id IS NOT NULL AND tenant_id = current_setting('app.tenant_id', true) AND current_setting('app.user_role', true) IN ('recruiter', 'candidate'));"
            )
        )
        await conn.execute(
            text(
                "CREATE POLICY user_sessions_self_all ON user_sessions FOR ALL TO PUBLIC USING (user_id IN (SELECT id FROM users WHERE email = current_setting('app.user_email', true)));"
            )
        )

    yield


@pytest.fixture(scope="function")
async def test_db():
    """Create a new database session for each test with isolation."""
    async with test_engine.begin() as conn:
        await conn.execute(
            text(
                "TRUNCATE TABLE user_sessions, user_activity, user_preferences, user_profiles, users CASCADE;"
            )
        )

    async with TestAsyncSessionLocal() as session:
        yield session
        await session.close()


@pytest.fixture(scope="function")
async def rls_test_db(test_db):
    """Specific database session for RLS testing using a non-superuser. Inherits truncation from test_db. Uses a single connection to ensure session-level variables persist."""
    # Build a new URL with the RLS user
    import re

    url = settings.database_url
    rls_url = re.sub(r"://[^:]+:[^@]+@", "://rls_test_user:rls_test_pass@", url)

    rls_engine = create_async_engine(rls_url, poolclass=NullPool)

    # Use a single connection for the entire session
    async with rls_engine.connect() as conn:
        # Create a session bound to this connection
        async with AsyncSession(bind=conn, expire_on_commit=False) as session:
            yield session
            await session.close()

    await rls_engine.dispose()


@pytest.fixture
async def seed_users(test_db):
    """Seed basic users for authenticated tests."""
    from app.models import User, UserRole, UserStatus

    admin = User(
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        tenant_id="tenant1",
        created_at=datetime.now(UTC).replace(tzinfo=None),
        updated_at=datetime.now(UTC).replace(tzinfo=None),
    )
    recruiter = User(
        email="recruiter@example.com",
        first_name="Recruiter",
        last_name="User",
        role=UserRole.RECRUITER,
        status=UserStatus.ACTIVE,
        tenant_id="tenant1",
        created_at=datetime.now(UTC).replace(tzinfo=None),
        updated_at=datetime.now(UTC).replace(tzinfo=None),
    )
    candidate = User(
        email="candidate@example.com",
        first_name="Candidate",
        last_name="User",
        role=UserRole.CANDIDATE,
        status=UserStatus.ACTIVE,
        tenant_id="tenant1",
        created_at=datetime.now(UTC).replace(tzinfo=None),
        updated_at=datetime.now(UTC).replace(tzinfo=None),
    )
    test_db.add_all([admin, recruiter, candidate])
    await test_db.commit()
    return {"admin": admin, "recruiter": recruiter, "candidate": candidate}


@pytest.fixture
def admin_token():
    return create_jwt_token("admin@example.com", role="admin")


@pytest.fixture
def recruiter_token():
    return create_jwt_token("recruiter@example.com", role="recruiter")


@pytest.fixture
def candidate_token():
    return create_jwt_token("candidate@example.com", role="candidate")


@pytest.fixture
def auth_headers_admin(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def auth_headers_recruiter(recruiter_token):
    return {"Authorization": f"Bearer {recruiter_token}"}


@pytest.fixture
def auth_headers_candidate(candidate_token):
    return {"Authorization": f"Bearer {candidate_token}"}


def create_jwt_token(
    email: str,
    user_id: str = "7ec0c2e3-3e1e-4b7e-9876-543210abcdef",
    role: str = "admin",
    tenant_id: str = "tenant1",
    exp_minutes: int = 30,
) -> str:
    """Create JWT token for testing."""
    settings.allow_unsafe_test_tokens = True

    payload = {
        "email": email,
        "user_id": user_id,
        "role": role,
        "tenant_id": tenant_id,
        "exp": int(
            (
                datetime.now(UTC).replace(tzinfo=None) + timedelta(minutes=exp_minutes)
            ).timestamp()
        ),
        "iat": int(datetime.now(UTC).replace(tzinfo=None).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


@pytest.fixture
def sample_user_data():
    return {
        "email": "newuser@example.com",
        "first_name": "New",
        "last_name": "User",
        "password": "Password123!",
        "role": "candidate",
        "tenant_id": "tenant1",
    }


@pytest.fixture
def sample_profile_data():
    return {
        "bio": "Test biography",
        "location": "San Francisco",
        "phone": "+14155552671",
        "company": "Test Co",
        "job_title": "Engineer",
        "tenant_id": "tenant1",
    }


@pytest.fixture
def sample_preferences_data():
    return {
        "theme": "dark",
        "language": "en",
        "notification_email": True,
        "notification_push": True,
        "tenant_id": "tenant1",
    }
