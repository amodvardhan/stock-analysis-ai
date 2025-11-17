"""
=============================================================================
AI Hub - Notification Tasks
=============================================================================
Background tasks for sending notifications (email, SMS).
=============================================================================
"""

from celery import shared_task
import emails
import structlog
from twilio.rest import Client

from core.config import settings

logger = structlog.get_logger()


@shared_task(name="tasks.notification_tasks.send_email_notification")
def send_email_notification(user_email: str, subject: str, message: str):
    """
    Send email notification to user.
    
    Args:
        user_email: Recipient email address
        subject: Email subject
        message: Email body (plain text)
    """
    try:
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.warning("email_not_configured", user_email=user_email)
            return {"status": "skipped", "reason": "SMTP not configured"}
        
        # Create email
        email_message = emails.Message(
            subject=subject,
            mail_from=(settings.SMTP_FROM, "AI Hub Alerts"),
            text=message,
        )
        
        # Send via SMTP
        response = email_message.send(
            to=user_email,
            smtp={
                "host": settings.SMTP_HOST,
                "port": settings.SMTP_PORT,
                "user": settings.SMTP_USER,
                "password": settings.SMTP_PASSWORD,
                "tls": True,
            }
        )
        
        logger.info("email_sent", user_email=user_email, subject=subject)
        return {"status": "sent", "user_email": user_email}
        
    except Exception as e:
        logger.error("email_send_failed", user_email=user_email, error=str(e))
        return {"status": "failed", "error": str(e)}


@shared_task(name="tasks.notification_tasks.send_sms_notification")
def send_sms_notification(phone_number: str, message: str):
    """
    Send SMS notification to user via Twilio.
    
    Args:
        phone_number: Recipient phone number (E.164 format)
        message: SMS message body
    """
    try:
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            logger.warning("sms_not_configured", phone_number=phone_number)
            return {"status": "skipped", "reason": "Twilio not configured"}
        
        # Initialize Twilio client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        # Send SMS
        twilio_message = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        
        logger.info("sms_sent", phone_number=phone_number, sid=twilio_message.sid)
        return {"status": "sent", "sid": twilio_message.sid}
        
    except Exception as e:
        logger.error("sms_send_failed", phone_number=phone_number, error=str(e))
        return {"status": "failed", "error": str(e)}
