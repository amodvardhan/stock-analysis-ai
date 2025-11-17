# AI Hub - Stock Market Intelligence System

Enterprise-grade AI-powered stock market analysis using multi-agent architecture.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- OpenAI API Key
- (Optional) Alpha Vantage API Key

### Step 1: Clone and Setup

Create project directory
mkdir ai-hub && cd ai-hub

Create backend directory
mkdir backend && cd backend

Create virtual environment
python -m venv venv

Activate virtual environment
On macOS/Linux:
source venv/bin/activate

On Windows:
venv\Scripts\activate

Install dependencies
pip install -r requirements.txt


### Step 2: Environment Configuration

Copy environment template
cp .env.example .env

Edit .env and add your API keys
nano .env # or use your preferred editor


**Required variables in `.env`:**

Database
DATABASE_URL=postgresql://aihub_user:aihub_password_2025@localhost:5432/aihub_stock_intelligence

OpenAI (REQUIRED)
OPENAI_API_KEY=sk-your-key-here

Security (generate with: openssl rand -hex 32)
SECRET_KEY=your-secret-key-here

Optional: Alpha Vantage for more stock data
ALPHA_VANTAGE_API_KEY=your-key-here


### Step 3: Start Services

Start PostgreSQL and Redis
docker-compose up -d postgres redis

Wait for services to be healthy (about 10 seconds)
docker-compose ps

Run database migrations
cd backend
alembic upgrade head


### Step 4: Run the Application

Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

Or run everything with Docker
docker-compose up


### Step 5: Test the API

**Access API Documentation:**

http://localhost:8000/api/docs


## 📚 API Usage Examples

### 1. Register a User

curl -X POST "http://localhost:8000/api/v1/auth/signup"
-H "Content-Type: application/json"
-d '{
"email": "[email protected]",
"password": "SecurePass123",
"full_name": "John Doe"
}'


**Response:**
{
"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
"token_type": "bearer"
}


### 2. Analyze a Stock (The Main Feature!)

Save your token
TOKEN="your-token-from-signup"

Analyze Reliance Industries (NSE)
curl -X POST "http://localhost:8000/api/v1/analysis/analyze"
-H "Authorization: Bearer $TOKEN"
-H "Content-Type: application/json"
-d '{
"symbol": "RELIANCE",
"market": "india_nse",
"company_name": "Reliance Industries Limited",
"user_risk_tolerance": "moderate"
}'


**Response (simplified):**
{
"symbol": "RELIANCE",
"final_recommendation": {
"final_recommendation": "buy",
"confidence": 78,
"entry_price": 2450.50,
"target_price": 2680.00,
"stop_loss": 2350.00,
"risk_level": "medium",
"synthesis_reasoning": "All three agents show positive signals..."
},
"analyses": {
"technical": { ... },
"fundamental": { ... },
"sentiment": { ... }
}
}


### 3. Add to Watchlist

curl -X POST "http://localhost:8000/api/v1/watchlist/"
-H "Authorization: Bearer $TOKEN"
-H "Content-Type: application/json"
-d '{
"symbol": "TCS",
"market": "india_nse",
"alert_threshold_percent": 3.0,
"notes": "Monitoring for entry opportunity"
}'


### 4. Add to Portfolio

curl -X POST "http://localhost:8000/api/v1/portfolio/"
-H "Authorization: Bearer $TOKEN"
-H "Content-Type: application/json"
-d '{
"symbol": "RELIANCE",
"market": "india_nse",
"quantity": 10,
"purchase_price": 2450.50,
"purchase_date": "2025-11-17T12:00:00Z"
}'


## 🧪 Testing Stock Analysis

### Test with Different Markets

**Indian Stock (NSE):**
{
"symbol": "RELIANCE",
"market": "india_nse"
}


**US Stock (NASDAQ):**

**US Stock (NYSE):**
{
"symbol": "JPM",
"market": "us_nyse"
}


## 🏗️ Architecture Overview


┌─────────────┐
│ User │
└──────┬──────┘
│ HTTP Request
▼
┌──────────────────────────────────────┐
│ FastAPI Backend │
├──────────────────────────────────────┤
│ ┌────────────────────────────────┐ │
│ │ Multi-Agent Orchestrator │ │
│ └─────────┬──────────────────────┘ │
│ │ │
│ ┌────────┴────────┐ │
│ │ LangGraph │ │
│ │ StateGraph │ │
│ └────────┬────────┘ │
│ │ │
│ ┌────────┴────────┬────────────┐ │
│ │ │ │ │
│ ▼ ▼ ▼ │
│ ┌──────┐ ┌──────────┐ ┌──────┐│
│ │Tech │ │Fundamental│ │Senti-││
│ │Agent │ │ Agent │ │ment ││
│ └──────┘ └──────────┘ └──────┘│
│ │ │ │ │
│ └────────┬────────┴────────────┘ │
│ │ │
│ ▼ │
│ ┌────────────────┐ │
│ │ Recommendation │ │
│ │ Agent │ │
│ └────────────────┘ │
└──────────────────────────────────────┘
│
▼
┌──────────────┐
│ PostgreSQL │
│ + pgvector │
└──────────────┘


## 📊 Database Schema

Run migrations to create tables:

cd backend
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head


## 🔒 Security Features

- ✅ JWT authentication
- ✅ Password hashing with bcrypt
- ✅ Input validation with Pydantic
- ✅ CORS protection
- ✅ OWASP LLM Top 10 compliance
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ Rate limiting ready

## 🐛 Troubleshooting

### Database Connection Error
Check if PostgreSQL is running
docker-compose ps

View logs
docker-compose logs postgres


### OpenAI API Error
Verify your API key
echo $OPENAI_API_KEY

Test API key
curl https://api.openai.com/v1/models
-H "Authorization: Bearer $OPENAI_API_KEY"


### Import Errors
Reinstall dependencies
pip install --upgrade -r requirements.txt


## 📈 Performance Tips

1. **Use caching**: Redis caches stock data for 5 minutes
2. **Batch requests**: Analyze multiple stocks asynchronously
3. **Use GPT-4o-mini**: For PoC, it's 90% cheaper than GPT-4
4. **Monitor LLM costs**: Check LangSmith dashboard

## 🚦 Next Steps

1. ✅ **Test the API** using the examples above
2. 📧 **Configure email notifications** (update SMTP settings)
3. 📱 **Add SMS alerts** (configure Twilio)
4. 🎨 **Build frontend** (React + TypeScript)
5. 📊 **Add monitoring** (Celery for background tasks)
6. 🔄 **Implement caching** (Redis for frequently accessed data)

## 📝 License

MIT License - feel free to use this for learning or production!

---

**Built with ❤️ using Python, FastAPI, LangGraph, and OpenAI**
