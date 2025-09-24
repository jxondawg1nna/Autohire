from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator

from playwright.async_api import Playwright

from ...schemas import NormalizedJob

logger = logging.getLogger(__name__)


class ScraperException(Exception):
    """Raised when an adapter fails in a recoverable way."""


@dataclass(slots=True)
class AdapterContext:
    """Shared contextual data made available to scraping adapters."""

    rate_limit: "RateLimiter"
    browser_name: str = "chromium"

    async def throttle(self) -> None:
        """Wait until the rate limiter allows another outbound request."""

        await self.rate_limit.acquire()


class BaseSiteAdapter(ABC):
    """Base class for job board scrapers powered by Playwright."""

    slug: str
    display_name: str
    rate_limit_per_minute: int = 30
    dedupe_ttl_seconds: int = 60 * 60 * 24

    def __init__(self, context: AdapterContext):
        self.context = context

    @abstractmethod
    async def scrape(self, playwright: Playwright) -> AsyncIterator[NormalizedJob]:
        """Yield normalized jobs discovered by the adapter."""

    def dedupe_key(self, job: NormalizedJob) -> str:
        """Fingerprint used to deduplicate jobs downstream."""

        return job.external_id or job.source_url

    async def throttle(self) -> None:
        """Convenience wrapper used by subclasses."""

        await self.context.throttle()


from ..limiters import RateLimiter  # noqa: E402  (circular-friendly import)

