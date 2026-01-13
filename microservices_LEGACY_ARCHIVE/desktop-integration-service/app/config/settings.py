"""Configuration management for Desktop Integration Service."""

from typing import Optional
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Service URLs (All 14 OpenTalent Microservices)
    # AI & Conversation Services
    granite_interview_url: str = Field(
        default="http://localhost:8005",
        validation_alias=AliasChoices("GRANITE_INTERVIEW_URL", "GRANITE_INTERVIEW_SERVICE_URL"),
    )
    conversation_url: str = Field(
        default="http://localhost:8002",
        validation_alias=AliasChoices("CONVERSATION_URL", "CONVERSATION_SERVICE_URL"),
    )
    interview_url: str = Field(
        default="http://localhost:8005",
        validation_alias=AliasChoices("INTERVIEW_URL", "INTERVIEW_SERVICE_URL"),
    )

    # Voice & Avatar Services
    voice_url: str = Field(
        default="http://localhost:8003",
        validation_alias=AliasChoices("VOICE_URL", "VOICE_SERVICE_URL"),
    )
    avatar_url: str = Field(
        default="http://localhost:8004",
        validation_alias=AliasChoices("AVATAR_URL", "AVATAR_SERVICE_URL"),
    )

    # Core Services
    scout_url: str = Field(
        default="http://localhost:8000",
        validation_alias=AliasChoices(
            "SCOUT_URL",
        ),
    )
    user_url: str = Field(
        default="http://localhost:8001",
        validation_alias=AliasChoices(
            "USER_URL",
        ),
    )
    candidate_url: str = Field(
        default="http://localhost:8006",
        validation_alias=AliasChoices(
            "CANDIDATE_URL",
        ),
    )

    # Analytics & Monitoring Services
    analytics_url: str = Field(
        default="http://localhost:8007",
        validation_alias=AliasChoices("ANALYTICS_URL", "ANALYTICS_SERVICE_URL"),
    )
    security_url: str = Field(
        default="http://localhost:8010",
        validation_alias=AliasChoices(
            "SECURITY_URL",
        ),
    )
    notification_url: str = Field(
        default="http://localhost:8011",
        validation_alias=AliasChoices(
            "NOTIFICATION_URL",
        ),
    )
    ai_auditing_url: str = Field(
        default="http://localhost:8012",
        validation_alias=AliasChoices(
            "AI_AUDITING_URL",
        ),
    )
    explainability_url: str = Field(
        default="http://localhost:8013",
        validation_alias=AliasChoices(
            "EXPLAINABILITY_URL",
        ),
    )

    # AI Model Service
    ollama_url: str = Field(
        default="http://localhost:11434",
        validation_alias=AliasChoices(
            "OLLAMA_URL",
        ),
    )

    # Optional: Agent Orchestration Service
    agents_url: Optional[str] = None

    # Service configuration
    service_timeout: float = Field(
        default=30.0,
        validation_alias=AliasChoices(
            "SERVICE_TIMEOUT",
        ),
    )
    health_check_timeout: float = Field(
        default=5.0,
        validation_alias=AliasChoices(
            "HEALTH_CHECK_TIMEOUT",
        ),
    )
    max_retries: int = Field(
        default=3,
        validation_alias=AliasChoices(
            "MAX_RETRIES",
        ),
    )
    health_cache_ttl: int = Field(
        default=5, validation_alias=AliasChoices("HEALTH_CACHE_TTL", "CACHE_TTL_SECONDS")
    )  # seconds
    models_cache_ttl: int = Field(
        default=30,
        validation_alias=AliasChoices(
            "MODELS_CACHE_TTL",
        ),
    )  # seconds

    # Application
    port: int = Field(
        default=8009,
        validation_alias=AliasChoices(
            "PORT",
        ),
    )
    host: str = Field(
        default="0.0.0.0",
        validation_alias=AliasChoices(
            "HOST",
        ),
    )
    debug: bool = Field(
        default=False,
        validation_alias=AliasChoices(
            "DEBUG",
        ),
    )
    log_level: str = Field(
        default="INFO",
        validation_alias=AliasChoices(
            "LOG_LEVEL",
        ),
    )

    # Feature flags
    enable_voice: bool = Field(
        default=True,
        validation_alias=AliasChoices(
            "ENABLE_VOICE",
        ),
    )
    enable_avatar: bool = Field(
        default=True,
        validation_alias=AliasChoices(
            "ENABLE_AVATAR",
        ),
    )
    enable_analytics: bool = Field(
        default=True,
        validation_alias=AliasChoices(
            "ENABLE_ANALYTICS",
        ),
    )
    enable_agents: bool = Field(
        default=False,
        validation_alias=AliasChoices(
            "ENABLE_AGENTS",
        ),
    )

    # CORS
    cors_origins: list = Field(
        default_factory=lambda: ["*"],
        validation_alias=AliasChoices(
            "CORS_ORIGINS",
        ),
    )
    # Settings behaviour
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Create global settings instance
settings = Settings()
