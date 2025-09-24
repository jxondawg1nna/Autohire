from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    """Runtime configuration for the worker service."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    api_base_url: str = Field(default="http://api:8000", validation_alias=AliasChoices("API_BASE_URL", "api_base_url"))
    api_token: str | None = Field(default=None, validation_alias=AliasChoices("API_TOKEN", "api_token"))
    redis_url: str = Field(default="redis://redis:6379/0", validation_alias=AliasChoices("REDIS_URL", "redis_url"))
    scrape_dispatch_interval_seconds: int = Field(
        default=60,
        ge=5,
        description="How frequently Celery beat evaluates scraping schedules.",
        validation_alias=AliasChoices("SCRAPE_DISPATCH_INTERVAL_SECONDS", "scrape_dispatch_interval_seconds"),
    )
    default_scrape_interval_minutes: int = Field(
        default=60,
        ge=1,
        description="Fallback cadence when no explicit schedule exists for an adapter.",
        validation_alias=AliasChoices("DEFAULT_SCRAPE_INTERVAL_MINUTES", "default_scrape_interval_minutes"),
    )
    request_timeout_seconds: float = Field(
        default=20.0,
        gt=0,
        description="HTTP timeout when communicating with the API service.",
        validation_alias=AliasChoices("REQUEST_TIMEOUT_SECONDS", "request_timeout_seconds"),
    )
    playwright_browser: Literal["chromium", "firefox", "webkit"] = Field(
        default="chromium",
        validation_alias=AliasChoices("PLAYWRIGHT_BROWSER", "playwright_browser"),
    )
    dedupe_ttl_hours: int = Field(
        default=24,
        ge=1,
        description="How long scraped job fingerprints remain in Redis for deduplication.",
        validation_alias=AliasChoices("SCRAPE_DEDUPE_TTL_HOURS", "dedupe_ttl_hours"),
    )
    scrape_queue_name: str = Field(
        default="scrape",
        min_length=1,
        validation_alias=AliasChoices("SCRAPE_QUEUE_NAME", "scrape_queue_name"),
    )


@lru_cache
def get_settings() -> WorkerSettings:
    """Return a cached instance of :class:`WorkerSettings`."""

    return WorkerSettings()  # type: ignore[arg-type]

