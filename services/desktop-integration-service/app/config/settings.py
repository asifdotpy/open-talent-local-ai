"""Configuration management for Desktop Integration Service."""


from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Service URLs (All 14 OpenTalent Microservices)
    # AI & Conversation Services
    granite_interview_url: str = "http://localhost:8005"
    conversation_url: str = "http://localhost:8002"
    interview_url: str = "http://localhost:8005"

    # Voice & Avatar Services
    voice_url: str = "http://localhost:8003"
    avatar_url: str = "http://localhost:8004"

    # Core Services
    scout_url: str = "http://localhost:8000"
    user_url: str = "http://localhost:8001"
    candidate_url: str = "http://localhost:8006"

    # Analytics & Monitoring Services
    analytics_url: str = "http://localhost:8007"
    security_url: str = "http://localhost:8010"
    notification_url: str = "http://localhost:8011"
    ai_auditing_url: str = "http://localhost:8012"
    explainability_url: str = "http://localhost:8013"

    # AI Model Service
    ollama_url: str = "http://localhost:11434"

    # Optional: Agent Orchestration Service
    agents_url: str | None = None

    # Service configuration
    service_timeout: float = 30.0
    health_check_timeout: float = 5.0
    max_retries: int = 3
    health_cache_ttl: int = 5  # seconds
    models_cache_ttl: int = 30  # seconds

    # Application
    port: int = 8009
    host: str = "127.0.0.1"
    debug: bool = False
    log_level: str = "INFO"

    # Feature flags
    enable_voice: bool = True
    enable_avatar: bool = True
    enable_analytics: bool = True
    enable_agents: bool = False

    # CORS
    cors_origins: list = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create global settings instance
settings = Settings()
