from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Fincas"
    debug: bool = True

    database_url: str = "postgresql+asyncpg://fincas:fincas_dev@localhost:5432/fincas"
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    secret_key: str = "dev-secret-key-change-in-production"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    encryption_key: str = "dev-encryption-key-32-bytes-long!"

    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    ai_default_provider: str = "ollama"
    ai_default_model: str | None = None

    pluggy_client_id: str | None = None
    pluggy_client_secret: str | None = None

    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None

    sentry_dsn: str | None = None

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
