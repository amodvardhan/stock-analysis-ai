#!/bin/bash
# =============================================================================
# AI Hub - Stop Development Environment
# =============================================================================

echo "🛑 Stopping AI Hub Development Environment..."

# Stop Docker services
docker-compose down

echo "✅ All Docker services stopped"
echo ""
echo "💡 Your Python processes (FastAPI, Celery) need to be stopped manually:"
echo "   Press Ctrl+C in each terminal running Python"
