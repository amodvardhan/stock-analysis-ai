#!/bin/bash
# =============================================================================
# AI Hub - Quick Development Start
# =============================================================================
# Use this script to quickly start your development environment
# =============================================================================

echo "🚀 Starting AI Hub Development Environment..."
echo ""

# Start Docker services
echo "🐳 Starting Docker services..."
docker-compose up -d postgres redis

# Wait for services
echo "⏳ Waiting for services..."
sleep 3

echo ""
echo "✅ Infrastructure ready!"
echo ""
echo "📝 Now run these commands in separate terminals:"
echo ""
echo "Terminal 1 - FastAPI Backend:"
echo "  cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo ""
echo "Terminal 2 - Celery Worker:"
echo "  cd backend && source venv/bin/activate && celery -A celery_app worker --loglevel=info"
echo ""
echo "Terminal 3 - Celery Beat:"
echo "  cd backend && source venv/bin/activate && celery -A celery_app beat --loglevel=info"
echo ""
echo "Terminal 4 - Frontend:"
echo "  cd frontend && npm run dev"
echo ""
