"""
=============================================================================
AI Hub - Structured Logging Configuration
=============================================================================
Configures structured logging using structlog for better observability.

Structured logs are JSON-formatted and include context (request IDs, user IDs, etc.)
making debugging and monitoring much easier.
=============================================================================
"""

import logging
import sys
import structlog
from core.config import settings


def setup_logging():
    """
    Configure structured logging for the application.
    
    This sets up:
    - JSON-formatted logs for production
    - Pretty console logs for development
    - Request ID tracking
    - Timestamp on every log entry
    """
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            # Use JSON in production, pretty console in development
            structlog.processors.JSONRenderer()
            if settings.ENVIRONMENT == "production"
            else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
