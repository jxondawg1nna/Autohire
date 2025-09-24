from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    database_url: str = "sqlite:///./autohire.db"
    redis_url: str = "redis://localhost:6379/0"
    minio_endpoint: str = "http://localhost:9000"
    minio_access_key: str = "minio"
    minio_secret_key: str = "minio-secret"
    meilisearch_url: str = "http://localhost:7700"
    meilisearch_api_key: str = "test-key"
    qdrant_url: str = "http://localhost:6333"
    keycloak_url: str = "http://localhost:8080"
    keycloak_realm: str = "autohire"
    keycloak_client_id: str = "autohire-api"
    keycloak_client_secret: str = "dev-secret"
    posthog_api_key: str | None = None
    allowed_origins: List[str] = []


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[arg-type]
