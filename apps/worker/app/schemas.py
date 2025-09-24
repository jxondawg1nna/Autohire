from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class NormalizedJob(BaseModel):
    """Normalized job representation shared with the API ingestion endpoint."""

    external_id: str = Field(..., description="Stable identifier from the upstream source.")
    title: str = Field(..., description="Job title as published by the source.")
    company: str = Field(..., description="Hiring company or organization name.")
    description: str = Field(..., description="HTML or plaintext job description body.")
    source_url: str = Field(..., description="Canonical URL for the job posting.")
    location: str | None = Field(default=None, description="Free-form location string supplied by the source.")
    remote: bool | None = Field(default=None, description="Whether the posting advertises remote work.")
    employment_type: str | None = Field(default=None, description="Employment type such as full-time or contract.")
    salary_min: int | None = Field(default=None, description="Minimum salary or rate expressed in minor currency units.")
    salary_max: int | None = Field(default=None, description="Maximum salary or rate expressed in minor currency units.")
    currency: str | None = Field(default=None, description="ISO-4217 currency code if compensation is provided.")
    posted_at: datetime | None = Field(default=None, description="Datetime supplied by the source for when the job was posted.")
    scraped_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp recorded when the worker normalized the job.",
    )
    source: str | None = Field(default=None, description="Adapter slug responsible for scraping the job.")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary adapter-specific metadata retained for diagnostics.",
    )


class ScrapeRunResult(BaseModel):
    """Return payload for completed scrape tasks."""

    adapter: str
    run_id: str
    processed: int
    sent: int
    dropped: int
    ingestion_response: dict[str, Any] | None = None


class ScrapeDispatchSummary(BaseModel):
    """Summary returned by the schedule dispatcher task."""

    evaluated: int
    dispatched: int
    skipped: int
    details: list[dict[str, Any]] = Field(default_factory=list)

