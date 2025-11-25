"""
=============================================================================
AI Hub - Celery Application Configuration
=============================================================================
Configures Celery for background task processing.

Celery handles:
- Periodic watchlist monitoring
- Sending notifications
- Database cleanup tasks
- Report generation

This runs separately from the FastAPI application.
=============================================================================
"""

from celery import Celery
from celery.schedules import crontab
import structlog

from core.config import settings

logger = structlog.get_logger()

# Create Celery app
celery_app = Celery(
    "aihub_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "tasks.watchlist_tasks",
        "tasks.maintenance_tasks",
        "tasks.notification_tasks",
        "tasks.portfolio_tasks",
        "tasks.stock_tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=240,  # Soft limit at 4 minutes
    worker_prefetch_multiplier=1,  # One task at a time
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
)

# Periodic task schedule
celery_app.conf.beat_schedule = {
    "monitor-watchlists": {
        "task": "tasks.watchlist_tasks.monitor_all_watchlists",
        "schedule": crontab(minute=f"*/{settings.STOCK_MONITORING_INTERVAL_MINUTES}"),  # Every 15 minutes
    },
    "cleanup-old-notifications": {
        "task": "tasks.maintenance_tasks.cleanup_old_notifications",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}

logger.info("celery_app_configured", broker=settings.REDIS_URL)
