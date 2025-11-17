# AI Hub - Complete Deployment Guide

## Quick Start (Development)

### 1. Start Backend Services

Terminal 1: Start PostgreSQL and Redis
cd ai-hub
docker-compose up -d postgres redis

Terminal 2: Start FastAPI
cd backend
source venv/bin/activate
uvicorn main:app --reload

Terminal 3: Start Celery Worker
cd backend
./start_celery.sh

Terminal 4: Start Frontend
cd frontend
npm install
npm run dev


### 2. Access the Application

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/api/docs
- **Celery Flower** (monitoring): http://localhost:5555

Start Flower (optional - for monitoring Celery tasks)
celery -A celery_app flower


## What Each Component Does

### FastAPI Backend (Port 8000)
- Handles API requests
- Runs AI agents for stock analysis
- Manages user authentication
- Serves real-time data

### Celery Worker
- Monitors watchlists every 15 minutes
- Sends email/SMS notifications
- Performs database cleanup
- Runs background analysis tasks

### React Frontend (Port 3000)
- User interface
- Real-time stock analysis
- Portfolio management
- Watchlist monitoring

## Testing the Complete System

### 1. Create Account & Login

Visit: http://localhost:3000/signup
Create account → Auto-login → Dashboard


### 2. Analyze a Stock
Click "Analyze Stock"
Symbol: RELIANCE
Market: NSE (India)
Click "Analyze" → Wait 20-30 seconds


### 3. Add to Watchlist
After analysis, add stock to watchlist
Set alert threshold: 3%
Celery will check every 15 minutes


### 4. Monitor Background Jobs
View Celery logs
tail -f celery.log

Check Flower dashboard
http://localhost:5555


## Production Deployment

### Using Docker Compose (Recommended)

Build and start all services
docker-compose up -d --build

View logs
docker-compose logs -f backend
docker-compose logs -f celery


### Environment Variables for Production

.env
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@postgres:5432/aihub
REDIS_URL=redis://redis:6379
OPENAI_API_KEY=your-production-key
SECRET_KEY=generate-with-openssl-rand-hex-32

Email (production SMTP)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key

SMS (Twilio)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890


## Monitoring & Maintenance

### Check System Health

API health
curl http://localhost:8000/health

Database connections
docker-compose exec postgres pg_isready

Redis status
docker-compose exec redis redis-cli ping

Celery tasks
celery -A celery_app inspect active


### View Logs

FastAPI logs
docker-compose logs -f backend

Celery worker logs
docker-compose logs -f celery

Database logs
docker-compose logs -f postgres


## Scaling Tips

1. **Horizontal Scaling**: Add more Celery workers

celery -A celery_app worker --concurrency=4


2. **Database Connection Pooling**: Already configured (10 connections)

3. **Redis Caching**: Implement for frequently accessed data

4. **CDN**: Serve frontend static files via CDN

## Troubleshooting

### Celery not running tasks

Check if Redis is accessible
redis-cli ping

Restart Celery worker
pkill celery
./start_celery.sh


### Database connection errors

Check PostgreSQL
docker-compose ps postgres

Reset database
docker-compose down -v
docker-compose up -d postgres
alembic upgrade head


### Frontend not connecting to API
Check CORS settings in main.py
Verify proxy in vite.config.ts
Check if backend is running on port 8000


---

**Your AI Hub is now fully operational!** 🚀

Test the complete flow:
1. Sign up → Login
2. Analyze RELIANCE stock
3. Add to watchlist
4. Wait 15 minutes → Check notifications
