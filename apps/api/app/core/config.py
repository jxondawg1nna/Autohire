from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables.

    Defaults enable local development and automated tests without a
    fully provisioned infrastructure stack. Production deployments
    should override these values via environment variables or secrets
    management.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    database_url: str = "postgresql+asyncpg://autohire:autohire@localhost:5432/autohire"
    redis_url: str = "redis://localhost:6379/0"
    minio_endpoint: str = "http://localhost:9000"
    minio_access_key: str = "autohire"
    minio_secret_key: str = "autohire"
    meilisearch_url: str = "http://localhost:7700"
    meilisearch_api_key: str = "development"
    qdrant_url: str = "http://localhost:6333"
    keycloak_url: str = "http://localhost:8080"
    keycloak_realm: str = "autohire"
    keycloak_client_id: str = "autohire"
    keycloak_client_secret: str = "development"
    opencats_base_url: str = "http://localhost:8081"
    opencats_api_key: str = "development"
    posthog_api_key: str | None = None
    allowed_origins: List[str] = []
    celery_task_eager: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[arg-type]
