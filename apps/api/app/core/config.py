from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    database_url: str
    redis_url: str
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    meilisearch_url: str
    meilisearch_api_key: str
    qdrant_url: str
    keycloak_url: str
    keycloak_realm: str
    keycloak_client_id: str
    keycloak_client_secret: str
    posthog_api_key: str | None = None
    allowed_origins: List[str] = []


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
