"""Adapter registry for Playwright-powered job board scrapers."""

from .base import AdapterContext, BaseSiteAdapter, ScraperException
from .demo import DemoBoardAdapter

ADAPTER_REGISTRY: dict[str, type[BaseSiteAdapter]] = {
    DemoBoardAdapter.slug: DemoBoardAdapter,
}


def get_adapter(slug: str) -> type[BaseSiteAdapter]:
    try:
        return ADAPTER_REGISTRY[slug]
    except KeyError as exc:  # pragma: no cover - defensive guard
        raise ScraperException(f"Unknown adapter requested: {slug}") from exc


__all__ = [
    "AdapterContext",
    "ADAPTER_REGISTRY",
    "BaseSiteAdapter",
    "DemoBoardAdapter",
    "ScraperException",
    "get_adapter",
]

