"""
=============================================================================
AI Hub - Celery Configuration
=============================================================================
Configures Celery for distributed task processing.

Features:
- Redis as message broker and result backend
- Automatic task discovery
- Scheduled periodic tasks (Celery Beat)
- Task monitoring and retry logic
- Rate limiting and task priority

Usage:
    # Start worker:
    celery -A core.celery_app worker --loglevel=info
    
    # Start beat (scheduler):
    celery -A core.celery_app beat --loglevel=info
    
    # Start flower (monitoring UI):
    celery -A core.celery_app flower
=============================================================================
"""

from celery import Celery
from celery.schedules import crontab
import structlog

from core.config import settings

logger = structlog.get_logger()

# =============================================================================
# Celery Application Instance
# =============================================================================
celery_app = Celery(
    "ai_hub",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
    include=[
        "tasks.stock_tasks",
        "tasks.notification_tasks",
        "tasks.portfolio_tasks",
        "tasks.watchlist_tasks",      
        "tasks.maintenance_tasks",  
    ]
)

# =============================================================================
# Celery Configuration
# =============================================================================
celery_app.conf.update(
    # Task execution settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    
    # Task result settings
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={
        "master_name": "mymaster",
        "visibility_timeout": 3600,
    },
    
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    
    # Task routing
    task_routes={
        "tasks.stock_tasks.*": {"queue": "stock_analysis"},
        "tasks.notification_tasks.*": {"queue": "notifications"},
        "tasks.portfolio_tasks.*": {"queue": "portfolio"},
    },
    
    # Rate limiting
    task_annotations={
        "tasks.stock_tasks.update_stock_price": {"rate_limit": "100/m"},
        "tasks.notification_tasks.send_email": {"rate_limit": "50/m"},
    },
    
    # Task retry settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Logging
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s",
)

# =============================================================================
# Periodic Tasks Schedule (Celery Beat)
# =============================================================================
celery_app.conf.beat_schedule = {
    # Update stock prices every 5 minutes during market hours
    "update-stock-prices-every-5-minutes": {
        "task": "tasks.stock_tasks.update_all_stock_prices",
        "schedule": crontab(minute="*/5", hour="9-15", day_of_week="0-4"),  # Mon-Fri, 9AM-3PM
    },
    
    # Check price alerts every minute
    "check-price-alerts": {
        "task": "tasks.notification_tasks.check_price_alerts",
        "schedule": crontab(minute="*"),  # Every minute
    },
    
    # Update portfolio values every 10 minutes
    "update-portfolio-values": {
        "task": "tasks.portfolio_tasks.update_all_portfolios",
        "schedule": crontab(minute="*/10"),
    },
    
    # Clean up old analysis data daily at midnight
    "cleanup-old-analysis": {
        "task": "tasks.stock_tasks.cleanup_old_analysis",
        "schedule": crontab(hour=0, minute=0),  # Daily at midnight
    },
    
    # Send daily portfolio summary at 4 PM
    "send-daily-summary": {
        "task": "tasks.notification_tasks.send_daily_portfolio_summary",
        "schedule": crontab(hour=16, minute=0),  # 4 PM daily
    },
}

logger.info("celery_configured", broker=settings.REDIS_HOST)
