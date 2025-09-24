from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    redis_url: str = "redis://redis:6379/0"
    database_url: str
    meilisearch_url: str
    meilisearch_api_key: str
    qdrant_url: str
    meilisearch_jobs_index: str = "jobs"
    qdrant_jobs_collection: str = "jobs"
    embedding_model_name: str = "mini-lm-deterministic"
    embedding_dimensions: int = 384


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[arg-type]
