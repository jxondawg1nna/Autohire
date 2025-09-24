from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class ScrapeScheduleEntry(BaseModel):
    """Represents adapter cadence configuration fetched from the API."""

    adapter: str
    interval_minutes: int = Field(gt=0)
    enabled: bool = True
    last_run_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    def is_due(self, last_dispatch_at: datetime | None, now: datetime | None = None) -> bool:
        if not self.enabled:
            return False
        reference = last_dispatch_at or self.last_run_at
        now = now or datetime.now(timezone.utc)
        if reference is None:
            return True
        elapsed = now - reference
        return elapsed.total_seconds() >= self.interval_minutes * 60


class ScrapeDispatchRecord(BaseModel):
    adapter: str
    run_id: str | None = None
    dispatched: bool = False
    reason: str | None = None

