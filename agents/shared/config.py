"""
Shared configuration for OpenTalent agents.
Manages environment variables and service URLs.
"""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class AgentConfig(BaseSettings):
    """Shared agent configuration"""

    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    redis_max_connections: int = Field(default=10, env="REDIS_MAX_CONNECTIONS")

    # Database Configuration
    database_url: str = Field(
        default="postgresql://talent_user:password@localhost:5433/talent_ai_interview",
        env="DATABASE_URL",
    )

    # Neo4j Vector Database Configuration
    neo4j_uri: str = Field(default="neo4j+s://4b63e239.databases.neo4j.io", env="NEO4J_URI")
    neo4j_username: str = Field(default="neo4j", env="NEO4J_USERNAME")
    neo4j_password: Optional[str] = Field(default=None, env="NEO4J_PASSWORD")
    neo4j_database: str = Field(default="neo4j", env="NEO4J_DATABASE")

    # Microservice URLs
    conversation_service_url: str = Field(
        default="http://localhost:8003", env="CONVERSATION_SERVICE_URL"
    )
    voice_service_url: str = Field(default="http://localhost:8002", env="VOICE_SERVICE_URL")
    avatar_service_url: str = Field(default="http://localhost:8001", env="AVATAR_SERVICE_URL")
    interview_service_url: str = Field(default="http://localhost:8004", env="INTERVIEW_SERVICE_URL")
    genkit_service_url: str = Field(default="http://localhost:3400", env="GENKIT_SERVICE_URL")

    # Agent URLs
    scout_agent_url: str = Field(default="http://localhost:8090", env="SCOUT_AGENT_URL")
    vetta_agent_url: str = Field(default="http://localhost:8080", env="VETTA_AGENT_URL")

    # Agent Ports
    interviewer_port: int = Field(default=8080, env="INTERVIEWER_PORT")
    scout_port: int = Field(default=8090, env="SCOUT_PORT")

    # API Keys
    google_genai_api_key: Optional[str] = Field(default=None, env="GOOGLE_GENAI_API_KEY")
    contactout_api_key: Optional[str] = Field(default=None, env="CONTACTOUT_API_KEY")
    salesql_api_key: Optional[str] = Field(default=None, env="SALESQL_API_KEY")
    github_token: Optional[str] = Field(default=None, env="GITHUB_TOKEN")

    # Service Timeouts (seconds)
    default_timeout: float = 30.0
    voice_timeout: float = 60.0
    avatar_timeout: float = 120.0
    conversation_timeout: float = 20.0

    # Retry Configuration
    max_retries: int = 3
    retry_backoff_multiplier: float = 1.0
    retry_min_wait: float = 2.0
    retry_max_wait: float = 10.0

    # Circuit Breaker
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60

    # Pagination
    default_page_size: int = 50
    max_page_size: int = 200

    # Message Bus
    message_retention_seconds: int = 86400  # 24 hours

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global config instance
config = AgentConfig()


def get_config() -> AgentConfig:
    """Get global configuration instance"""
    return config
