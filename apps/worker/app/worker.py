from __future__ import annotations

import os

from celery import Celery

CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
CELERY_BACKEND_URL = CELERY_BROKER_URL

celery_app = Celery("autohire", broker=CELERY_BROKER_URL, backend=CELERY_BACKEND_URL)
celery_app.conf.task_default_queue = "default"
celery_app.conf.result_expires = 3600


@celery_app.task(name="autohire.echo")
def echo(message: str) -> str:
    """Simple heartbeat task for smoke testing the worker stack."""

    return message
