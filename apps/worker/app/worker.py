from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

from celery import Celery
from kombu import Queue

from .config import get_settings
from .scraping import dispatch_scheduled_scrapes, execute_scrape

logger = logging.getLogger(__name__)

CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
CELERY_BACKEND_URL = CELERY_BROKER_URL

celery_app = Celery("autohire", broker=CELERY_BROKER_URL, backend=CELERY_BACKEND_URL)
settings = get_settings()

celery_app.conf.update(
    task_default_queue="default",
    result_expires=3600,
    task_queues=(Queue("default"), Queue(settings.scrape_queue_name)),
    beat_schedule={
        "dispatch-scrape-jobs": {
            "task": "autohire.scrape.dispatch",
            "schedule": settings.scrape_dispatch_interval_seconds,
            "options": {"queue": settings.scrape_queue_name},
        }
    },
    timezone="UTC",
)


@celery_app.task(name="autohire.echo", queue="default")
def echo(message: str) -> str:
    """Simple heartbeat task for smoke testing the worker stack."""

    return message


@celery_app.task(name="autohire.scrape.run", queue=settings.scrape_queue_name)
def run_scrape(adapter_name: str, run_id: str | None = None) -> dict[str, Any]:
    """Execute a scraping adapter and persist results via the API."""

    try:
        result = asyncio.run(execute_scrape(adapter_name, settings, run_id))
    except Exception:  # pragma: no cover - Celery captures the traceback
        logger.exception("scrape-run-failed", extra={"adapter": adapter_name, "run_id": run_id})
        raise
    return result.model_dump()


@celery_app.task(name="autohire.scrape.dispatch", queue=settings.scrape_queue_name)
def dispatch_scrape_jobs() -> dict[str, Any]:
    """Evaluate configured scrape cadences and enqueue adapter runs."""

    try:
        result = asyncio.run(dispatch_scheduled_scrapes(celery_app, settings))
    except Exception:  # pragma: no cover - Celery captures the traceback
        logger.exception("scrape-dispatch-failed")
        raise
    return result.model_dump()
