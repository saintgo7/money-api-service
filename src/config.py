"""Application configuration."""
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "Money API Service"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    secret_key: str

    # Database
    database_url: str
    redis_url: str
    clickhouse_host: str = "localhost"
    clickhouse_port: int = 9000
    clickhouse_db: str = "api_analytics"

    # AI APIs
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    replicate_api_key: Optional[str] = None
    elevenlabs_api_key: Optional[str] = None

    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic_usage: str = "api-usage-events"

    # Rate Limiting (requests per minute)
    rate_limit_free: int = 10
    rate_limit_starter: int = 60
    rate_limit_pro: int = 300
    rate_limit_enterprise: int = 1000

    # Pricing (USD)
    price_text_claude: float = 0.003
    price_text_gpt4: float = 0.006
    price_image_sdxl: float = 0.02
    price_image_dalle: float = 0.04
    price_audio_transcribe: float = 0.006
    price_audio_synthesize: float = 0.015

    # Monitoring
    sentry_dsn: Optional[str] = None
    prometheus_port: int = 9090

    # CORS
    cors_origins: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
