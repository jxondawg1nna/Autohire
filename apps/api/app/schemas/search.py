from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class JobLocation(BaseModel):
    city: str | None = None
    region: str | None = None
    country: str | None = None
    latitude: float | None = Field(default=None, description="Latitude in decimal degrees")
    longitude: float | None = Field(default=None, description="Longitude in decimal degrees")


class SearchHit(BaseModel):
    id: str
    external_id: str
    title: str
    description: str | None = None
    location: JobLocation | None = None
    metadata: dict[str, Any] | None = None
    score: float = 0.0
    highlights: dict[str, Any] | None = None
    distance_km: float | None = None
    indexed_at: datetime | None = None


class FacetBucket(BaseModel):
    name: str
    count: int


class SearchResponse(BaseModel):
    query: str
    total: int
    hits: list[SearchHit]
    facets: dict[str, list[FacetBucket]] = Field(default_factory=dict)


class JobSearchFilters(BaseModel):
    query: str = ""
    employment_types: list[str] = Field(default_factory=list)
    remote: bool | None = None
    min_compensation: int | None = None
    max_compensation: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    radius_km: float | None = None
