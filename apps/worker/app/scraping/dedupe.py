from __future__ import annotations

from datetime import timedelta

from redis.asyncio import Redis


class JobDeduper:
    """Redis-backed helper ensuring duplicate job payloads are ignored."""

    def __init__(self, redis: Redis, namespace: str = "scrape:dedupe", ttl_seconds: int = 60 * 60 * 24):
        self.redis = redis
        self.namespace = namespace
        self.ttl_seconds = ttl_seconds

    async def is_duplicate(self, fingerprint: str) -> bool:
        key = f"{self.namespace}:{fingerprint}"
        added = await self.redis.set(key, "1", nx=True, ex=self.ttl_seconds)
        return added is None

    async def reset(self, fingerprint: str) -> None:
        key = f"{self.namespace}:{fingerprint}"
        await self.redis.expire(key, timedelta(seconds=self.ttl_seconds))

