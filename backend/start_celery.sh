#!/bin/bash
# =============================================================================
# Start Celery Worker and Beat Scheduler
# =============================================================================

echo "Starting Celery worker and beat scheduler..."

# Start Celery worker in background
celery -A celery_app worker --loglevel=info &

# Start Celery beat scheduler
celery -A celery_app beat --loglevel=info
