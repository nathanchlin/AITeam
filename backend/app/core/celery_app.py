"""
Celery application configuration for task persistence.
"""

from celery import Celery
from app.config import settings

# Create Celery app
celery_app = Celery(
    "aiteam",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30 minutes hard limit
    task_soft_time_limit=1500,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,  # Only fetch one task at a time
    worker_concurrency=2,  # Number of concurrent workers
    # Task routing
    task_routes={
        "app.core.tasks.run_pipeline_task": {"queue": "pipeline"},
        "app.core.tasks.execute_phase_task": {"queue": "pipeline"},
        "app.core.tasks.health_check": {"queue": "default"},
    },
    # Default queue
    task_default_queue="default",
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
)

# Auto-discover tasks from tasks module
celery_app.autodiscover_tasks(["app.core"])
