"""
Celery configuration for background tasks.
"""

from celery import Celery
from src.core.config import settings

celery_app = Celery(
    "bookstream",
    broker=str(settings.CELERY_BROKER_URL),
    backend=str(settings.CELERY_RESULT_BACKEND),
    include=["src.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    result_expires=86400,
    beat_schedule={
        "cleanup-old-sessions": {
            "task": "src.workers.tasks.cleanup_old_sessions",
            "schedule": 86400,  # Daily
        },
        "update-analytics": {
            "task": "src.workers.tasks.update_daily_analytics",
            "schedule": 3600,  # Hourly
        },
        "send-reading-reminders": {
            "task": "src.workers.tasks.send_reading_reminders",
            "schedule": 3600,  # Hourly
        },
    },
)
