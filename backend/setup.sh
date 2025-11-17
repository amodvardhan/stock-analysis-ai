#!/bin/bash
# =============================================================================
# AI Hub - Development Setup Script
# =============================================================================
# This script sets up your local development environment
# =============================================================================

set -e  # Exit on error

echo "🚀 AI Hub - Development Environment Setup"
echo "=========================================="
echo ""

# -------------------------
# Step 1: Check Prerequisites
# -------------------------
echo "📋 Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first."
    exit 1
fi
echo "✅ Docker found"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed."
    exit 1
fi
echo "✅ Docker Compose found"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed."
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python found (version $PYTHON_VERSION)"

# Check Node.js (for frontend)
if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js not found. Frontend won't work without it."
else
    NODE_VERSION=$(node --version)
    echo "✅ Node.js found (version $NODE_VERSION)"
fi

echo ""

# -------------------------
# Step 2: Start Docker Services
# -------------------------
echo "🐳 Starting Docker services (PostgreSQL, Redis)..."
docker-compose up -d postgres redis

echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check if services are running
if docker ps | grep -q aihub_postgres; then
    echo "✅ PostgreSQL is running on localhost:5432"
else
    echo "❌ PostgreSQL failed to start"
    docker-compose logs postgres
    exit 1
fi

if docker ps | grep -q aihub_redis; then
    echo "✅ Redis is running on localhost:6379"
else
    echo "❌ Redis failed to start"
    docker-compose logs redis
    exit 1
fi

echo ""

# -------------------------
# Step 3: Setup Python Virtual Environment
# -------------------------
echo "🐍 Setting up Python virtual environment..."

cd .. # go back to the root directory
cd backend # go to the backend directory

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Verify activation
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi
echo "✅ Virtual environment activated: $VIRTUAL_ENV"

echo ""

# Upgrade pip
echo "📦 Upgrading pip..."
if pip install --upgrade pip; then
    echo "✅ pip upgraded successfully"
else
    echo "❌ Failed to upgrade pip"
    exit 1
fi

echo ""

# Install dependencies
echo "📦 Installing Python dependencies (this may take 3-5 minutes)..."
echo "   Please be patient, downloading packages..."
echo ""

if pip install -r requirements.txt; then
    echo ""
    echo "✅ All Python dependencies installed successfully"
else
    echo ""
    echo "❌ Failed to install dependencies"
    echo ""
    echo "Common issues and fixes:"
    echo "1. If you see compilation errors, install build tools:"
    echo "   macOS: xcode-select --install"
    echo "   Ubuntu: sudo apt-get install python3-dev build-essential"
    echo ""
    echo "2. If specific packages fail, try installing them separately:"
    echo "   pip install package-name"
    echo ""
    echo "3. Check the error message above for specific package issues"
    exit 1
fi

echo ""

# -------------------------
# Step 4: Check .env file
# -------------------------
echo "🔧 Checking environment configuration..."

if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env file created"
        echo ""
        echo "⚠️  IMPORTANT: You MUST edit backend/.env and add your API keys!"
        echo "   Required: OPENAI_API_KEY, SECRET_KEY"
        echo ""
    else
        echo "❌ .env.example not found. Please create .env manually."
        exit 1
    fi
else
    echo "✅ .env file exists"
fi

# Generate secret key suggestion
echo ""
echo "💡 Generate a SECRET_KEY with this command:"
echo "   python3 -c \"import secrets; print(secrets.token_hex(32))\""
echo ""

# -------------------------
# Step 5: Setup Database
# -------------------------
echo "🗄️  Setting up database..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env file created"
        echo ""
        echo "⚠️  IMPORTANT: You MUST edit backend/.env and add your API keys!"
        echo "   Required: OPENAI_API_KEY, SECRET_KEY"
        echo ""
    else
        echo "❌ .env.example not found. Please create .env manually."
        exit 1
    fi
else
    echo "✅ .env file exists"
fi

# Create __init__.py files to make directories Python packages
echo "Creating package __init__.py files..."
touch __init__.py
touch core/__init__.py
touch db/__init__.py
touch api/__init__.py
mkdir -p api/routes && touch api/routes/__init__.py
touch agents/__init__.py
mkdir -p schemas && touch schemas/__init__.py
mkdir -p services && touch services/__init__.py
mkdir -p utils && touch utils/__init__.py
mkdir -p tasks && touch tasks/__init__.py
echo "✅ Package structure created"

# Initialize Alembic if not already done
if [ ! -d "alembic/versions" ]; then
    echo "Initializing Alembic migrations directory..."
    mkdir -p alembic/versions
fi

# Set PYTHONPATH and run migrations
echo "Running database migrations..."
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

if alembic upgrade head 2>&1; then
    echo "✅ Database migrations completed"
else
    echo "⚠️  Database migrations may have issues."
    echo "   This is OK if you haven't configured .env yet."
    echo "   Run migrations manually after configuring .env:"
    echo "   cd backend && source venv/bin/activate"
    echo "   export PYTHONPATH=\$PYTHONPATH:\$(pwd)"
    echo "   alembic upgrade head"
fi


# -------------------------
# Step 6: Frontend Setup (if Node.js is available)
# -------------------------
if command -v node &> /dev/null; then
    echo "⚛️  Setting up frontend..."
    cd ../frontend
    
    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies (this may take 2-3 minutes)..."
        if npm install; then
            echo "✅ Frontend dependencies installed"
        else
            echo "❌ Failed to install frontend dependencies"
            echo "   Try running manually: cd frontend && npm install"
        fi
    else
        echo "✅ Frontend dependencies already installed"
    fi
    
    cd ../backend
else
    echo "⚠️  Skipping frontend setup (Node.js not found)"
fi

echo ""

# -------------------------
# Step 7: Verify Installation
# -------------------------
echo "🔍 Verifying installation..."

# Check if key packages are installed
if python -c "import fastapi, sqlalchemy, langchain, langgraph" 2>/dev/null; then
    echo "✅ Key Python packages verified"
else
    echo "⚠️  Some Python packages may be missing"
    echo "   Run: pip list | grep -E 'fastapi|sqlalchemy|langchain'"
fi

echo ""

# -------------------------
# Summary
# -------------------------
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Configure your environment variables:"
echo "   nano backend/.env"
echo ""
echo "   Required variables:"
echo "   - OPENAI_API_KEY: Get from https://platform.openai.com/api-keys"
echo "   - SECRET_KEY: Generate with: python3 -c \"import secrets; print(secrets.token_hex(32))\""
echo ""
echo "2. After configuring .env, run migrations if they failed:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   alembic upgrade head"
echo ""
echo "3. Start the development environment:"
echo ""
echo "   Terminal 1 - FastAPI Backend:"
echo "     cd backend"
echo "     source venv/bin/activate"
echo "     uvicorn main:app --reload"
echo ""
echo "   Terminal 2 - Celery Worker:"
echo "     cd backend"
echo "     source venv/bin/activate"
echo "     celery -A celery_app worker --loglevel=info"
echo ""
echo "   Terminal 3 - Celery Beat:"
echo "     cd backend"
echo "     source venv/bin/activate"
echo "     celery -A celery_app beat --loglevel=info"
echo ""
echo "   Terminal 4 - Frontend:"
echo "     cd frontend"
echo "     npm run dev"
echo ""
echo "=========================================="
echo "🌐 Access Points:"
echo "   Frontend:  http://localhost:3000"
echo "   API Docs:  http://localhost:8000/api/docs"
echo "   Database:  localhost:5432"
echo "   Redis:     localhost:6379"
echo "=========================================="
echo ""
echo "💡 Quick commands:"
echo "   Start services:  ./start-dev.sh"
echo "   Stop services:   ./stop-dev.sh"
echo ""
echo "📚 Troubleshooting:"
echo "   If you encounter issues, check:"
echo "   - Docker containers: docker-compose ps"
echo "   - Docker logs: docker-compose logs postgres redis"
echo "   - Python packages: pip list"
echo ""
