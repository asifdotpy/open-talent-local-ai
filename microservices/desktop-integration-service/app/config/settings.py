"""Configuration management for Desktop Integration Service."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Service URLs
    granite_interview_url: str = "http://localhost:8005"  # Fixed: Was 8000, actual port is 8005
    conversation_url: str = "http://localhost:8003"
    voice_url: str = "http://localhost:8002"
    avatar_url: str = "http://localhost:8001"
    interview_url: str = "http://localhost:8004"
    analytics_url: str = "http://localhost:8007"
    ollama_url: str = "http://localhost:11434"
    agents_url: Optional[str] = None  # Optional: agent orchestration service

    # Service configuration
    service_timeout: float = 30.0
    health_check_timeout: float = 5.0
    max_retries: int = 3
    health_cache_ttl: int = 5  # seconds
    models_cache_ttl: int = 30  # seconds

    # Application
    port: int = 8009
    host: str = "0.0.0.0"
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
