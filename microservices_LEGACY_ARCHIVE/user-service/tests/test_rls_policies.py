"""
Integration tests for PostgreSQL Row-Level Security (RLS) policies.

Tests verify that RLS policies correctly enforce:
- Admin users can access all data across tenants
- Recruiters can only access data within their tenant
- Candidates can only access their own data
- Cross-tenant isolation is maintained
"""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.models import User, UserProfile, UserPreferences, UserActivity, UserSession


@pytest.mark.integration
@pytest.mark.asyncio
class TestUsersTableRLS:
    """Test RLS policies on users table."""

    async def test_admin_can_select_all_users(self, test_db: AsyncSession):
        """Admin can SELECT users from all tenants."""
        # Set admin context
        await test_db.execute(text("SET app.user_role = 'admin'"))
        await test_db.execute(text("SET app.user_email = 'admin@example.com'"))
        await test_db.execute(text("SET app.tenant_id = 'tenant1'"))

        # Create users in different tenants
        user1 = User(
            id=uuid4(),
            email="user1@tenant1.com",
            full_name="User 1",
            tenant_id="tenant1",
            role="candidate",
            status="active",
        )
        user2 = User(
            id=uuid4(),
            email="user2@tenant2.com",
            full_name="User 2",
            tenant_id="tenant2",
            role="candidate",
            status="active",
        )
        test_db.add_all([user1, user2])
        await test_db.commit()

        # Admin should see both users
        result = await test_db.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        assert count >= 2, "Admin should see users from all tenants"

    async def test_recruiter_tenant_isolation(self, test_db: AsyncSession):
        """Recruiter can only SELECT users from their tenant."""
        # Create users in different tenants
        user1_id = uuid4()
        user2_id = uuid4()

        await test_db.execute(text("SET app.user_role = 'admin'"))
        user1 = User(
            id=user1_id,
            email="user1@tenant1.com",
            full_name="User 1",
            tenant_id="tenant1",
            role="candidate",
            status="active",
        )
        user2 = User(
            id=user2_id,
            email="user2@tenant2.com",
            full_name="User 2",
            tenant_id="tenant2",
            role="candidate",
            status="active",
        )
        test_db.add_all([user1, user2])
        await test_db.commit()

        # Switch to recruiter context in tenant1
        await test_db.execute(text("SET app.user_role = 'recruiter'"))
        await test_db.execute(text("SET app.user_email = 'recruiter@tenant1.com'"))
        await test_db.execute(text("SET app.tenant_id = 'tenant1'"))

        # Query users
        result = await test_db.execute(
            text("SELECT email FROM users WHERE email = :email"), {"email": "user1@tenant1.com"}
        )
        tenant1_user = result.scalar()

        result = await test_db.execute(
            text("SELECT email FROM users WHERE email = :email"), {"email": "user2@tenant2.com"}
        )
        tenant2_user = result.scalar()

        assert tenant1_user == "user1@tenant1.com", "Should see user from same tenant"
        assert tenant2_user is None, "Should NOT see user from different tenant"

    async def test_candidate_can_only_select_self(self, test_db: AsyncSession):
        """Candidate can only SELECT their own user record."""
        # Create two candidates
        user1_id = uuid4()
        user2_id = uuid4()

        await test_db.execute(text("SET app.user_role = 'admin'"))
        user1 = User(
            id=user1_id,
            email="candidate1@example.com",
            full_name="Candidate 1",
            tenant_id="tenant1",
            role="candidate",
            status="active",
        )
        user2 = User(
            id=user2_id,
            email="candidate2@example.com",
            full_name="Candidate 2",
            tenant_id="tenant1",
            role="candidate",
            status="active",
        )
        test_db.add_all([user1, user2])
        await test_db.commit()

        # Switch to candidate1 context
        await test_db.execute(text("SET app.user_role = 'candidate'"))
        await test_db.execute(text("SET app.user_email = 'candidate1@example.com'"))
        await test_db.execute(text("SET app.tenant_id = 'tenant1'"))

        # Query users
        result = await test_db.execute(
            text("SELECT email FROM users WHERE email = :email"),
            {"email": "candidate1@example.com"},
        )
        own_user = result.scalar()

        result = await test_db.execute(
            text("SELECT email FROM users WHERE email = :email"),
            {"email": "candidate2@example.com"},
        )
        other_user = result.scalar()

        assert own_user == "candidate1@example.com", "Should see own record"
        assert other_user is None, "Should NOT see other candidate's record"

    async def test_recruiter_can_insert_within_tenant(self, test_db: AsyncSession):
        """Recruiter can INSERT users in their tenant."""
        await test_db.execute(text("SET app.user_role = 'recruiter'"))
        await test_db.execute(text("SET app.user_email = 'recruiter@tenant1.com'"))
        await test_db.execute(text("SET app.tenant_id = 'tenant1'"))

        # Insert user in same tenant
        user = User(
            id=uuid4(),
            email="newuser@tenant1.com",
            full_name="New User",
            tenant_id="tenant1",  # Same tenant
            role="candidate",
            status="active",
        )
        test_db.add(user)
        await test_db.commit()

        # Verify user was created
        result = await test_db.execute(
            text("SELECT email FROM users WHERE email = :email"), {"email": "newuser@tenant1.com"}
        )
        assert result.scalar() == "newuser@tenant1.com"

    async def test_recruiter_cannot_insert_different_tenant(self, test_db: AsyncSession):
        """Recruiter CANNOT INSERT users in different tenant."""
        await test_db.execute(text("SET app.user_role = 'recruiter'"))
        await test_db.execute(text("SET app.user_email = 'recruiter@tenant1.com'"))
        await test_db.execute(text("SET app.tenant_id = 'tenant1'"))

        # Try to insert user in different tenant
        user = User(
            id=uuid4(),
            email="newuser@tenant2.com",
            full_name="New User",
            tenant_id="tenant2",  # Different tenant
            role="candidate",
            status="active",
        )
        test_db.add(user)

        with pytest.raises(Exception):
            await test_db.commit()

        await test_db.rollback()

    async def test_admin_can_delete_any_user(self, test_db: AsyncSession):
        """Admin can DELETE users from any tenant."""
        # Create user
        user_id = uuid4()
        user = User(
            id=user_id,
            email="todelete@tenant1.com",
            full_name="To Delete",
            tenant_id="tenant1",
            role="candidate",
            status="active",
        )
        test_db.add(user)
        await test_db.commit()

        # Set admin context
        await test_db.execute(text("SET app.user_role = 'admin'"))
        await test_db.execute(text("SET app.user_email = 'admin@example.com'"))

        # Delete user
        await test_db.execute(text("DELETE FROM users WHERE id = :id"), {"id": str(user_id)})
        await test_db.commit()

        # Verify user was deleted
        result = await test_db.execute(
            text("SELECT COUNT(*) FROM users WHERE id = :id"), {"id": str(user_id)}
        )
        assert result.scalar() == 0


@pytest.mark.integration
@pytest.mark.asyncio
class TestUserProfilesTableRLS:
    """Test RLS policies on user_profiles table."""

    async def test_admin_can_access_all_profiles(self, test_db: AsyncSession):
        """Admin can SELECT all profiles."""
        await test_db.execute(text("SET app.user_role = 'admin'"))

        # Create profiles
        user1 = User(
            id=uuid4(),
            email="user1@tenant1.com",
            full_name="User 1",
            tenant_id="tenant1",
            role="candidate",
            status="active",
        )
        test_db.add(user1)
        await test_db.flush()

        profile1 = UserProfile(
            user_id=user1.id,
            phone="+1234567890",
            location="San Francisco",
        )
        test_db.add(profile1)
        await test_db.commit()

        result = await test_db.execute(text("SELECT COUNT(*) FROM user_profiles"))
        count = result.scalar()
        assert count >= 1

    async def test_candidate_can_access_own_profile(self, test_db: AsyncSession):
        """Candidate can SELECT their own profile."""
        # Create user and profile as admin
        await test_db.execute(text("SET app.user_role = 'admin'"))

        user = User(
            id=uuid4(),
            email="candidate@example.com",
            full_name="Candidate",
            tenant_id="tenant1",
            role="candidate",
            status="active",
        )
        test_db.add(user)
        await test_db.flush()

        profile = UserProfile(
            user_id=user.id,
            phone="+1234567890",
            location="New York",
        )
        test_db.add(profile)
        await test_db.commit()

        # Switch to candidate context
        await test_db.execute(text("SET app.user_role = 'candidate'"))
        await test_db.execute(text("SET app.user_email = 'candidate@example.com'"))
        await test_db.execute(text("SET app.tenant_id = 'tenant1'"))

        # Query profile
        result = await test_db.execute(
            text("SELECT location FROM user_profiles WHERE user_id = :user_id"),
            {"user_id": str(user.id)},
        )
        location = result.scalar()
        assert location == "New York"


@pytest.mark.integration
@pytest.mark.asyncio
class TestUserPreferencesTableRLS:
    """Test RLS policies on user_preferences table."""

    async def test_candidate_can_manage_own_preferences(self, test_db: AsyncSession):
        """Candidate can SELECT, INSERT, UPDATE their own preferences."""
        # Create user as admin
        await test_db.execute(text("SET app.user_role = 'admin'"))

        user = User(
            id=uuid4(),
            email="candidate@example.com",
            full_name="Candidate",
            tenant_id="tenant1",
            role="candidate",
            status="active",
        )
        test_db.add(user)
        await test_db.commit()

        # Switch to candidate context
        await test_db.execute(text("SET app.user_role = 'candidate'"))
        await test_db.execute(text("SET app.user_email = 'candidate@example.com'"))
        await test_db.execute(text("SET app.tenant_id = 'tenant1'"))

        # INSERT preferences
        prefs = UserPreferences(
            user_id=user.id,
            email_notifications=True,
            language="en",
            timezone="UTC",
        )
        test_db.add(prefs)
        await test_db.commit()

        # SELECT preferences
        result = await test_db.execute(
            text("SELECT language FROM user_preferences WHERE user_id = :user_id"),
            {"user_id": str(user.id)},
        )
        language = result.scalar()
        assert language == "en"

        # UPDATE preferences
        await test_db.execute(
            text("UPDATE user_preferences SET language = 'es' WHERE user_id = :user_id"),
            {"user_id": str(user.id)},
        )
        await test_db.commit()

        result = await test_db.execute(
            text("SELECT language FROM user_preferences WHERE user_id = :user_id"),
            {"user_id": str(user.id)},
        )
        language = result.scalar()
        assert language == "es"


@pytest.mark.integration
@pytest.mark.asyncio
class TestUserActivityTableRLS:
    """Test RLS policies on user_activity table."""

    async def test_recruiter_can_view_tenant_activity(self, test_db: AsyncSession):
        """Recruiter can SELECT activity within their tenant."""
        # Create user and activity as admin
        await test_db.execute(text("SET app.user_role = 'admin'"))

        user = User(
            id=uuid4(),
            email="user@tenant1.com",
            full_name="User",
            tenant_id="tenant1",
            role="candidate",
            status="active",
        )
        test_db.add(user)
        await test_db.flush()

        activity = UserActivity(
            user_id=user.id,
            activity_type="login",
            tenant_id="tenant1",
        )
        test_db.add(activity)
        await test_db.commit()

        # Switch to recruiter context
        await test_db.execute(text("SET app.user_role = 'recruiter'"))
        await test_db.execute(text("SET app.user_email = 'recruiter@tenant1.com'"))
        await test_db.execute(text("SET app.tenant_id = 'tenant1'"))

        # Query activity
        result = await test_db.execute(
            text("SELECT activity_type FROM user_activity WHERE user_id = :user_id"),
            {"user_id": str(user.id)},
        )
        activity_type = result.scalar()
        assert activity_type == "login"


@pytest.mark.integration
@pytest.mark.asyncio
class TestUserSessionsTableRLS:
    """Test RLS policies on user_sessions table."""

    async def test_candidate_can_view_own_sessions(self, test_db: AsyncSession):
        """Candidate can SELECT their own sessions."""
        # Create user and session as admin
        await test_db.execute(text("SET app.user_role = 'admin'"))

        user = User(
            id=uuid4(),
            email="candidate@example.com",
            full_name="Candidate",
            tenant_id="tenant1",
            role="candidate",
            status="active",
        )
        test_db.add(user)
        await test_db.flush()

        session = UserSession(
            user_id=user.id,
            session_token="test-token-123",
            ip_address="127.0.0.1",
            user_agent="TestClient",
        )
        test_db.add(session)
        await test_db.commit()

        # Switch to candidate context
        await test_db.execute(text("SET app.user_role = 'candidate'"))
        await test_db.execute(text("SET app.user_email = 'candidate@example.com'"))
        await test_db.execute(text("SET app.tenant_id = 'tenant1'"))

        # Query session
        result = await test_db.execute(
            text("SELECT session_token FROM user_sessions WHERE user_id = :user_id"),
            {"user_id": str(user.id)},
        )
        token = result.scalar()
        assert token == "test-token-123"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
