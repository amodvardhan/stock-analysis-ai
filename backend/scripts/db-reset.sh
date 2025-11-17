#!/bin/bash
# Reset database (useful during development)

echo "⚠️  This will DELETE all data. Are you sure? (yes/no)"
read answer

if [ "$answer" = "yes" ]; then
    echo "Resetting database..."
    
    # Drop and recreate database
    docker-compose exec postgres psql -U aihub_user -c "DROP DATABASE IF EXISTS aihub_stock_intelligence;"
    docker-compose exec postgres psql -U aihub_user -c "CREATE DATABASE aihub_stock_intelligence;"
    
    # Run migrations
    source venv/bin/activate
    alembic upgrade head
    
    echo "✅ Database reset complete"
else
    echo "❌ Cancelled"
fi
