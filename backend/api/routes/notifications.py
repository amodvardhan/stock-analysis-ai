"""
=============================================================================
AI Hub - Notifications Routes
=============================================================================
Retrieve user notifications.

Endpoints:
- GET /notifications - Get user's notifications
- PUT /notifications/{id}/read - Mark notification as read
=============================================================================
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime
import structlog

from core.database import get_db
from db.models import User, Notification
from api.routes.auth import get_current_user

logger = structlog.get_logger()
router = APIRouter()


@router.get(
    "/",
    summary="Get user notifications",
    description="Retrieve all notifications for the current user"
)
async def get_notifications(
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's notifications.
    
    Args:
        unread_only: If True, only return unread notifications
    """
    logger.info("get_notifications_requested", user_id=str(current_user.id))
    
    query = select(Notification).where(Notification.user_id == current_user.id)
    
    if unread_only:
        query = query.where(Notification.is_read == False)
    
    query = query.order_by(Notification.created_at.desc()).limit(50)
    
    result = await db.execute(query)
    notifications = result.scalars().all()
    
    return [
        {
            "id": n.id,
            "type": n.notification_type.value,
            "title": n.title,
            "message": n.message,
            "status": n.status.value,
            "is_read": n.is_read,
            "created_at": n.created_at,
            "read_at": n.read_at
        }
        for n in notifications
    ]


@router.put(
    "/{notification_id}/read",
    summary="Mark notification as read"
)
async def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark a notification as read.
    """
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        )
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Notification marked as read"}
