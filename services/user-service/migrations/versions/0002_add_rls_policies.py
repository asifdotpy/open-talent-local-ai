"""add row-level security policies

Revision ID: 0002_add_rls_policies
Revises: 0001_initial
Create Date: 2025-12-14
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = '0002_add_rls_policies'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade():
    """
    Enable Row-Level Security (RLS) on all user-related tables.

    RLS Policies:
    1. Admin Role: Full access to all rows (bypass RLS)
    2. Recruiter/Candidate: Access only rows matching their tenant_id
    3. Self Access: Users can always access their own records (by email)

    Note: PostgreSQL RLS uses session variables set by application:
    - current_setting('app.user_email')
    - current_setting('app.user_role')
    - current_setting('app.tenant_id')
    """

    # ========================================================================
    # ENABLE RLS ON ALL TABLES
    # ========================================================================

    op.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE user_activity ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;")

    # ========================================================================
    # USERS TABLE POLICIES
    # ========================================================================

    # Policy 1: Admin can see all users
    op.execute("""
        CREATE POLICY users_admin_all ON users
        FOR ALL
        TO PUBLIC
        USING (
            current_setting('app.user_role', true) = 'admin'
        );
    """)

    # Policy 2: Users can see users in their tenant
    op.execute("""
        CREATE POLICY users_tenant_select ON users
        FOR SELECT
        TO PUBLIC
        USING (
            tenant_id IS NOT NULL
            AND tenant_id = current_setting('app.tenant_id', true)
            AND current_setting('app.user_role', true) IN ('recruiter', 'candidate')
        );
    """)

    # Policy 3: Users can see their own record (by email)
    op.execute("""
        CREATE POLICY users_self_select ON users
        FOR SELECT
        TO PUBLIC
        USING (
            email = current_setting('app.user_email', true)
        );
    """)

    # Policy 4: Recruiters and admins can insert users in their tenant
    op.execute("""
        CREATE POLICY users_tenant_insert ON users
        FOR INSERT
        TO PUBLIC
        WITH CHECK (
            current_setting('app.user_role', true) IN ('admin', 'recruiter')
            AND (
                current_setting('app.user_role', true) = 'admin'
                OR tenant_id = current_setting('app.tenant_id', true)
            )
        );
    """)

    # Policy 5: Users can update users in their tenant
    op.execute("""
        CREATE POLICY users_tenant_update ON users
        FOR UPDATE
        TO PUBLIC
        USING (
            current_setting('app.user_role', true) = 'admin'
            OR (
                tenant_id = current_setting('app.tenant_id', true)
                AND current_setting('app.user_role', true) IN ('recruiter', 'candidate')
            )
            OR email = current_setting('app.user_email', true)
        );
    """)

    # Policy 6: Only admins can delete users
    op.execute("""
        CREATE POLICY users_admin_delete ON users
        FOR DELETE
        TO PUBLIC
        USING (
            current_setting('app.user_role', true) = 'admin'
        );
    """)

    # ========================================================================
    # USER_PROFILES TABLE POLICIES
    # ========================================================================

    # Policy 1: Admin can see all profiles
    op.execute("""
        CREATE POLICY user_profiles_admin_all ON user_profiles
        FOR ALL
        TO PUBLIC
        USING (
            current_setting('app.user_role', true) = 'admin'
        );
    """)

    # Policy 2: Users can see profiles in their tenant
    op.execute("""
        CREATE POLICY user_profiles_tenant_select ON user_profiles
        FOR SELECT
        TO PUBLIC
        USING (
            tenant_id IS NOT NULL
            AND tenant_id = current_setting('app.tenant_id', true)
            AND current_setting('app.user_role', true) IN ('recruiter', 'candidate')
        );
    """)

    # Policy 3: Users can see their own profile
    op.execute("""
        CREATE POLICY user_profiles_self_select ON user_profiles
        FOR SELECT
        TO PUBLIC
        USING (
            user_id IN (
                SELECT id FROM users WHERE email = current_setting('app.user_email', true)
            )
        );
    """)

    # Policy 4: Users can insert/update their own profile or tenant profiles
    op.execute("""
        CREATE POLICY user_profiles_tenant_modify ON user_profiles
        FOR ALL
        TO PUBLIC
        USING (
            current_setting('app.user_role', true) = 'admin'
            OR tenant_id = current_setting('app.tenant_id', true)
            OR user_id IN (
                SELECT id FROM users WHERE email = current_setting('app.user_email', true)
            )
        );
    """)

    # ========================================================================
    # USER_PREFERENCES TABLE POLICIES
    # ========================================================================

    # Policy 1: Admin can see all preferences
    op.execute("""
        CREATE POLICY user_preferences_admin_all ON user_preferences
        FOR ALL
        TO PUBLIC
        USING (
            current_setting('app.user_role', true) = 'admin'
        );
    """)

    # Policy 2: Users can see preferences in their tenant
    op.execute("""
        CREATE POLICY user_preferences_tenant_select ON user_preferences
        FOR SELECT
        TO PUBLIC
        USING (
            tenant_id IS NOT NULL
            AND tenant_id = current_setting('app.tenant_id', true)
            AND current_setting('app.user_role', true) IN ('recruiter', 'candidate')
        );
    """)

    # Policy 3: Users can manage their own preferences
    op.execute("""
        CREATE POLICY user_preferences_self_all ON user_preferences
        FOR ALL
        TO PUBLIC
        USING (
            user_id IN (
                SELECT id FROM users WHERE email = current_setting('app.user_email', true)
            )
        );
    """)

    # ========================================================================
    # USER_ACTIVITY TABLE POLICIES
    # ========================================================================

    # Policy 1: Admin can see all activity
    op.execute("""
        CREATE POLICY user_activity_admin_all ON user_activity
        FOR ALL
        TO PUBLIC
        USING (
            current_setting('app.user_role', true) = 'admin'
        );
    """)

    # Policy 2: Users can see activity in their tenant
    op.execute("""
        CREATE POLICY user_activity_tenant_select ON user_activity
        FOR SELECT
        TO PUBLIC
        USING (
            tenant_id IS NOT NULL
            AND tenant_id = current_setting('app.tenant_id', true)
            AND current_setting('app.user_role', true) IN ('recruiter', 'candidate')
        );
    """)

    # Policy 3: Users can see and create their own activity
    op.execute("""
        CREATE POLICY user_activity_self_all ON user_activity
        FOR ALL
        TO PUBLIC
        USING (
            user_id IN (
                SELECT id FROM users WHERE email = current_setting('app.user_email', true)
            )
        );
    """)

    # ========================================================================
    # USER_SESSIONS TABLE POLICIES
    # ========================================================================

    # Policy 1: Admin can see all sessions
    op.execute("""
        CREATE POLICY user_sessions_admin_all ON user_sessions
        FOR ALL
        TO PUBLIC
        USING (
            current_setting('app.user_role', true) = 'admin'
        );
    """)

    # Policy 2: Users can see sessions in their tenant
    op.execute("""
        CREATE POLICY user_sessions_tenant_select ON user_sessions
        FOR SELECT
        TO PUBLIC
        USING (
            tenant_id IS NOT NULL
            AND tenant_id = current_setting('app.tenant_id', true)
            AND current_setting('app.user_role', true) IN ('recruiter', 'candidate')
        );
    """)

    # Policy 3: Users can manage their own sessions
    op.execute("""
        CREATE POLICY user_sessions_self_all ON user_sessions
        FOR ALL
        TO PUBLIC
        USING (
            user_id IN (
                SELECT id FROM users WHERE email = current_setting('app.user_email', true)
            )
        );
    """)


def downgrade():
    """Drop all RLS policies and disable RLS on tables."""

    # ========================================================================
    # DROP POLICIES - USERS TABLE
    # ========================================================================

    op.execute("DROP POLICY IF EXISTS users_admin_all ON users;")
    op.execute("DROP POLICY IF EXISTS users_tenant_select ON users;")
    op.execute("DROP POLICY IF EXISTS users_self_select ON users;")
    op.execute("DROP POLICY IF EXISTS users_tenant_insert ON users;")
    op.execute("DROP POLICY IF EXISTS users_tenant_update ON users;")
    op.execute("DROP POLICY IF EXISTS users_admin_delete ON users;")

    # ========================================================================
    # DROP POLICIES - USER_PROFILES TABLE
    # ========================================================================

    op.execute("DROP POLICY IF EXISTS user_profiles_admin_all ON user_profiles;")
    op.execute("DROP POLICY IF EXISTS user_profiles_tenant_select ON user_profiles;")
    op.execute("DROP POLICY IF EXISTS user_profiles_self_select ON user_profiles;")
    op.execute("DROP POLICY IF EXISTS user_profiles_tenant_modify ON user_profiles;")

    # ========================================================================
    # DROP POLICIES - USER_PREFERENCES TABLE
    # ========================================================================

    op.execute("DROP POLICY IF EXISTS user_preferences_admin_all ON user_preferences;")
    op.execute("DROP POLICY IF EXISTS user_preferences_tenant_select ON user_preferences;")
    op.execute("DROP POLICY IF EXISTS user_preferences_self_all ON user_preferences;")

    # ========================================================================
    # DROP POLICIES - USER_ACTIVITY TABLE
    # ========================================================================

    op.execute("DROP POLICY IF EXISTS user_activity_admin_all ON user_activity;")
    op.execute("DROP POLICY IF EXISTS user_activity_tenant_select ON user_activity;")
    op.execute("DROP POLICY IF EXISTS user_activity_self_all ON user_activity;")

    # ========================================================================
    # DROP POLICIES - USER_SESSIONS TABLE
    # ========================================================================

    op.execute("DROP POLICY IF EXISTS user_sessions_admin_all ON user_sessions;")
    op.execute("DROP POLICY IF EXISTS user_sessions_tenant_select ON user_sessions;")
    op.execute("DROP POLICY IF EXISTS user_sessions_self_all ON user_sessions;")

    # ========================================================================
    # DISABLE RLS ON ALL TABLES
    # ========================================================================

    op.execute("ALTER TABLE users DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE user_preferences DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE user_activity DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE user_sessions DISABLE ROW LEVEL SECURITY;")
