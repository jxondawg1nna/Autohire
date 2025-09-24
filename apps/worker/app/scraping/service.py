from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from celery import Celery
from playwright.async_api import async_playwright
from redis.asyncio import Redis

from ..api_client import JobApiClient
from ..config import WorkerSettings
from ..schemas import ScrapeDispatchSummary, ScrapeRunResult
from .adapters import ADAPTER_REGISTRY, AdapterContext, get_adapter
from .dedupe import JobDeduper
from .limiters import RateLimiter
from .schedule import ScrapeDispatchRecord, ScrapeScheduleEntry

logger = logging.getLogger(__name__)


@dataclass
class ScraperRuntime:
    settings: WorkerSettings
    api_client: JobApiClient
    redis: Redis


@asynccontextmanager
async def build_runtime(settings: WorkerSettings):
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    api_client = JobApiClient(settings)
    try:
        yield ScraperRuntime(settings=settings, api_client=api_client, redis=redis)
    finally:
        await api_client.close()
        await redis.aclose()


class ScrapeService:
    def __init__(self, runtime: ScraperRuntime):
        self.runtime = runtime

    async def run_adapter(self, adapter_slug: str, run_id: str | None = None) -> ScrapeRunResult:
        adapter_cls = get_adapter(adapter_slug)
        rate_limiter = RateLimiter(adapter_cls.rate_limit_per_minute)
        dedupe = JobDeduper(
            self.runtime.redis,
            namespace=f"scrape:dedupe:{adapter_slug}",
            ttl_seconds=adapter_cls.dedupe_ttl_seconds,
        )
        context = AdapterContext(rate_limit=rate_limiter, browser_name=self.runtime.settings.playwright_browser)
        adapter = adapter_cls(context)
        processed = 0
        dropped = 0
        collected: list[NormalizedJob] = []
        run_id = run_id or str(uuid4())

        async with async_playwright() as playwright:
            if not hasattr(playwright, context.browser_name):
                raise ValueError(
                    f"Unsupported browser '{context.browser_name}' for Playwright context"
                )
            async for job in adapter.scrape(playwright):
                processed += 1
                job.source = adapter.slug
                fingerprint = adapter.dedupe_key(job)
                if await dedupe.is_duplicate(fingerprint):
                    dropped += 1
                    continue
                collected.append(job)

        ingestion_response: dict | None = None
        if collected:
            ingestion_response = await self.runtime.api_client.ingest_jobs(adapter.slug, run_id, collected)

        logger.info(
            "scrape-run-complete",
            extra={
                "adapter": adapter.slug,
                "run_id": run_id,
                "processed": processed,
                "sent": len(collected),
                "dropped": dropped,
            },
        )
        return ScrapeRunResult(
            adapter=adapter.slug,
            run_id=run_id,
            processed=processed,
            sent=len(collected),
            dropped=dropped,
            ingestion_response=ingestion_response,
        )

class ScheduleDispatcher:
    def __init__(self, runtime: ScraperRuntime, celery_app: Celery):
        self.runtime = runtime
        self.celery_app = celery_app

    async def dispatch(self) -> ScrapeDispatchSummary:
        schedules = await self.runtime.api_client.fetch_schedule()
        if not schedules:
            schedules = [
                ScrapeScheduleEntry(
                    adapter=adapter_slug,
                    interval_minutes=self.runtime.settings.default_scrape_interval_minutes,
                    enabled=True,
                )
                for adapter_slug in ADAPTER_REGISTRY.keys()
            ]
        now = datetime.now(timezone.utc)
        details: list[dict] = []
        dispatched = 0
        for entry in schedules:
            record = await self._handle_entry(entry, now)
            if record.dispatched:
                dispatched += 1
            details.append(record.model_dump())
        logger.info(
            "scrape-dispatch-complete",
            extra={"evaluated": len(schedules), "dispatched": dispatched, "skipped": len(schedules) - dispatched},
        )
        skipped = len(schedules) - dispatched
        return ScrapeDispatchSummary(evaluated=len(schedules), dispatched=dispatched, skipped=skipped, details=details)

    async def _handle_entry(self, entry: ScrapeScheduleEntry, now: datetime) -> ScrapeDispatchRecord:
        redis_key = f"scrape:last_dispatch:{entry.adapter}"
        raw_last_run = await self.runtime.redis.get(redis_key)
        last_dispatched_at = datetime.fromisoformat(raw_last_run) if raw_last_run else None
        if not entry.is_due(last_dispatched_at, now):
            return ScrapeDispatchRecord(adapter=entry.adapter, dispatched=False, reason="not_due")

        run_id = str(uuid4())
        self.celery_app.send_task(
            "autohire.scrape.run",
            kwargs={"adapter_name": entry.adapter, "run_id": run_id},
            queue=self.runtime.settings.scrape_queue_name,
        )
        await self.runtime.redis.set(redis_key, now.isoformat(), ex=int(entry.interval_minutes * 60))
        return ScrapeDispatchRecord(adapter=entry.adapter, run_id=run_id, dispatched=True)


async def execute_scrape(adapter_name: str, settings: WorkerSettings, run_id: str | None = None) -> ScrapeRunResult:
    async with build_runtime(settings) as runtime:
        service = ScrapeService(runtime)
        return await service.run_adapter(adapter_name, run_id)


async def dispatch_scheduled_scrapes(celery_app: Celery, settings: WorkerSettings) -> ScrapeDispatchSummary:
    async with build_runtime(settings) as runtime:
        dispatcher = ScheduleDispatcher(runtime, celery_app)
        return await dispatcher.dispatch()

