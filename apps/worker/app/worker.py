from __future__ import annotations

from celery import Celery

from .config import get_settings

settings = get_settings()

celery_app = Celery(
    "autohire",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks"],
)
celery_app.conf.task_default_queue = "default"
celery_app.conf.result_expires = 3600


@celery_app.task(name="autohire.echo")
def echo(message: str) -> str:
    """Simple heartbeat task for smoke testing the worker stack."""

    return message
