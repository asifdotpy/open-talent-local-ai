import os

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "User Service"
    PROJECT_NAME: str = "OpenTalent User Service"
    VERSION: str = "0.1.0"
    database_url: str = os.getenv(
        "USER_SERVICE_DATABASE_URL",
        "postgresql+asyncpg://supabase_user:supabase_pass@localhost:54322/user_service",
    )
    echo_sql: bool = os.getenv("USER_SERVICE_ECHO_SQL", "false").lower() == "true"

    # Security Service Integration
    security_service_url: str = os.getenv(
        "SECURITY_SERVICE_URL",
        "http://localhost:8010",
    )
    security_service_timeout: int = int(os.getenv("SECURITY_SERVICE_TIMEOUT", "5"))

    # JWT Configuration (must match Security Service)
    jwt_secret_key: str = os.getenv(
        "SECURITY_SECRET_KEY",
        "DEV_ONLY_INSECURE_SECRET_CHANGE_ME",
    )
    jwt_algorithm: str = "HS256"

    # Testing convenience: allow insecure tokens for external black-box tests
    allow_unsafe_test_tokens: bool = (
        os.getenv("ALLOW_UNSAFE_TEST_TOKENS", "false").lower() == "true"
    )


settings = Settings()
