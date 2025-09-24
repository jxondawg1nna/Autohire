from __future__ import annotations

import asyncio
import time
from collections import deque


class RateLimiter:
    """Simple in-memory rate limiter shared by scraping adapters."""

    def __init__(self, max_calls: int, period: float = 60.0):
        self.max_calls = max_calls
        self.period = period
        self._events: dict[str, deque[float]] = {}
        self._lock = asyncio.Lock()

    async def acquire(self, key: str = "default") -> None:
        if self.max_calls <= 0:
            return

        async with self._lock:
            now = time.monotonic()
            events = self._events.setdefault(key, deque())
            while events and now - events[0] > self.period:
                events.popleft()
            if len(events) < self.max_calls:
                events.append(now)
                return
            sleep_for = self.period - (now - events[0])

        await asyncio.sleep(max(sleep_for, 0))
        await self.acquire(key)

