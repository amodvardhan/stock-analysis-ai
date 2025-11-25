from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.config import settings
from core.database import Base
from db.models import *  # Import all models

# this is the Alembic Config object
config = context.config

# Override sqlalchemy.url with our config
# Convert async URL to sync URL for Alembic (replace asyncpg with psycopg3)
database_url = settings.DATABASE_URL
if "postgresql+asyncpg://" in database_url:
    # Use psycopg3 (psycopg) for Alembic migrations
    database_url = database_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
elif "postgresql://" in database_url and "+" not in database_url:
    # Plain postgresql:// URL, use psycopg3
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://")
config.set_main_option("sqlalchemy.url", database_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Get the database URL from config (set in line 18)
    database_url = config.get_main_option("sqlalchemy.url")
    
    # Create configuration dict for engine_from_config
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = database_url
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
