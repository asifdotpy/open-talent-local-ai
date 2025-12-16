"""Test runner script for user service.

Run this to test the user profile creation with PostgreSQL.
"""

import os
import subprocess
import sys

from sqlalchemy import create_engine, text


def check_database_connection(db_url):
    """Check if the database is accessible."""
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def main():
    """Main test runner function."""
    # Get test database URL
    test_db_url = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql://testuser:testpass@localhost:5433/test_user_service",
    )

    print("🧪 TALENT AI User Service - Test Runner")
    print("=" * 50)
    print(f"Test Database: {test_db_url}")

    # Check database connection
    if not check_database_connection(test_db_url):
        print("\n💡 To set up a test database:")
        print("1. Using Docker (recommended):")
        print("   docker run --name postgres-test-user-service \\")
        print("     -e POSTGRES_USER=testuser \\")
        print("     -e POSTGRES_PASSWORD=testpass \\")
        print("     -e POSTGRES_DB=test_user_service \\")
        print("     -p 5433:5432 -d postgres:15")
        print("\n2. Set environment variable:")
        print(f'   export TEST_DATABASE_URL="{test_db_url}"')
        print("\n3. Or run the setup script:")
        print("   bash setup_test_db.sh")
        return 1

    print("✅ Database connection successful!")

    # Run tests
    print("\n🚀 Running tests...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        env={**os.environ, "TEST_DATABASE_URL": test_db_url},
        check=False,
    )

    return result.returncode


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
