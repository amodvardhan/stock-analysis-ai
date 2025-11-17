First Time Setup

# 1. Clone/create your project directory
mkdir ai-hub && cd ai-hub

# 2. Create the directory structure
mkdir -p backend frontend

# 3. Copy all the files provided above to their respective locations

# 4. Run the setup script
./setup.sh

# 5. Edit your environment variables
nano backend/.env
# Add your OPENAI_API_KEY and other keys

# 6. Generate a secret key
python3 -c "import secrets; print(secrets.token_hex(32))"
# Copy this to SECRET_KEY in .env


Daily Development Workflow
# 1. Start infrastructure
./start-dev.sh

# 2. Open 4 terminals and run:

# Terminal 1 - Backend API
cd backend
source venv/bin/activate
uvicorn main:app --reload
# Access: http://localhost:8000/api/docs

# Terminal 2 - Celery Worker
cd backend
source venv/bin/activate
celery -A celery_app worker --loglevel=info

# Terminal 3 - Celery Beat (for scheduled tasks)
cd backend
source venv/bin/activate
celery -A celery_app beat --loglevel=info

# Terminal 4 - Frontend
cd frontend
npm run dev
# Access: http://localhost:3000


Stopping Everything
# Stop infrastructure
./stop-dev.sh

# Stop Python processes
# Press Ctrl+C in each terminal


Database Management
# View database in pgAdmin (optional)
docker-compose --profile tools up -d pgadmin
# Visit: http://localhost:5050
# Login: admin@aihub.com / admin123

# Open PostgreSQL shell
./backend/scripts/db-shell.sh

# Open Redis CLI
./backend/scripts/redis-shell.sh

# Reset database (WARNING: deletes all data)
./backend/scripts/db-reset.sh


