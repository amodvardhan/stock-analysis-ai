"""
=============================================================================
AI Hub - Maintenance Tasks
=============================================================================
Background tasks for database cleanup and maintenance.
=============================================================================
"""

from celery import shared_task
from sqlalchemy import delete
from datetime import datetime, timedelta
import asyncio
import structlog

from core.database import AsyncSessionLocal
from db.models import Notification, StockAnalysis

logger = structlog.get_logger()


@shared_task(name="tasks.maintenance_tasks.cleanup_old_notifications")
def cleanup_old_notifications():
    """
    Delete read notifications older than 30 days.
    
    Runs daily at 2 AM (configured in celery_app.py).
    """
    logger.info("cleanup_old_notifications_started")
    
    asyncio.run(_cleanup_notifications_async())
    
    logger.info("cleanup_old_notifications_completed")
    return {"status": "completed"}


async def _cleanup_notifications_async():
    """Delete old read notifications."""
    async with AsyncSessionLocal() as db:
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            result = await db.execute(
                delete(Notification).where(
                    Notification.is_read == True,
                    Notification.created_at < cutoff_date
                )
            )
            
            deleted_count = result.rowcount
            await db.commit()
            
            logger.info("old_notifications_deleted", count=deleted_count)
            
        except Exception as e:
            logger.error("notification_cleanup_failed", error=str(e))
            await db.rollback()
