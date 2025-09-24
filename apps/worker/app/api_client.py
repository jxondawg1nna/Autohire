from __future__ import annotations

from typing import Iterable

import httpx

from .config import WorkerSettings
from .schemas import NormalizedJob
from .scraping.schedule import ScrapeScheduleEntry


class JobApiClient:
    """HTTP client responsible for communicating with the AutoHire API service."""

    def __init__(self, settings: WorkerSettings):
        headers = {"User-Agent": "autohire-worker/0.1"}
        if settings.api_token:
            headers["Authorization"] = f"Bearer {settings.api_token}"
        self._client = httpx.AsyncClient(
            base_url=settings.api_base_url,
            headers=headers,
            timeout=settings.request_timeout_seconds,
        )

    async def ingest_jobs(self, adapter: str, run_id: str, jobs: Iterable[NormalizedJob]) -> dict:
        payload = {
            "adapter": adapter,
            "run_id": run_id,
            "jobs": [job.model_dump(mode="json") for job in jobs],
        }
        response = await self._client.post("/api/jobs/ingest", json=payload)
        response.raise_for_status()
        return response.json()

    async def fetch_schedule(self) -> list[ScrapeScheduleEntry]:
        response = await self._client.get("/api/jobs/schedule")
        response.raise_for_status()
        data = response.json()
        schedules = data.get("schedules", [])
        return [ScrapeScheduleEntry.model_validate(entry) for entry in schedules]

    async def close(self) -> None:
        await self._client.aclose()

