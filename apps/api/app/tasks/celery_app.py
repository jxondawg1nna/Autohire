"""Celery application configuration for AutoHire."""

from __future__ import annotations

from celery import Celery

from app.core.config import get_settings


settings = get_settings()

if settings.celery_task_eager:
    broker_url = "memory://"
    backend_url = "cache+memory://"
else:
    broker_url = settings.redis_url
    backend_url = settings.redis_url

celery_app = Celery("autohire", broker=broker_url, backend=backend_url)

celery_app.conf.update(task_always_eager=settings.celery_task_eager)

__all__ = ["celery_app"]

