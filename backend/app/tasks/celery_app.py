"""
Celery application configuration.

WHY: AI processing takes 15-60 seconds per lead. You CANNOT do this
synchronously in an HTTP request — users would timeout, and you'd block
your API workers. Celery offloads to background workers.

SCALING:
- 10k users: 2-4 Celery workers, single Redis
- 100k users: 10-20 workers, Redis Cluster, dedicated worker pools per agent type
"""

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "leadgen",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_default_retry_delay=60,
    task_max_retries=3,
    imports=["app.tasks.lead_processing"],
)
