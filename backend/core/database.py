"""
=============================================================================
AI Hub - Database Configuration
=============================================================================
SQLAlchemy async engine and session management.
=============================================================================
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text  # ← ADD THIS IMPORT
import structlog

from core.config import settings

logger = structlog.get_logger()

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.ENVIRONMENT == "development",
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# Declarative Base
class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


# Dependency to get database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides database session for FastAPI routes.
    
    Usage:
        @router.get("/")
        async def route(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database on application startup.
    
    Creates pgvector extension and all tables.
    """
    try:
        async with engine.begin() as conn:
            # Create pgvector extension - USE text() for raw SQL
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))  # ← FIX HERE
            
            # Create all tables defined in models
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("database_initialized_successfully")
        
    except Exception as e:
        logger.error("database_initialization_failed", error=str(e))
        raise


async def close_db():
    """
    Close database connections on application shutdown.
    """
    try:
        await engine.dispose()
        logger.info("database_connections_closed")
    except Exception as e:
        logger.error("database_close_failed", error=str(e))
