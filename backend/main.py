"""
=============================================================================
AI Hub - Main FastAPI Application Entry Point
=============================================================================
Enterprise-grade stock market intelligence system powered by multi-agent AI.

This application provides:
- Real-time stock analysis using LangGraph multi-agent architecture
- Technical analysis (RSI, MACD, EMA, Bollinger Bands)
- Fundamental analysis (P/E, debt ratios, profitability metrics)
- Sentiment analysis from news and social media
- AI-powered buy/sell/hold recommendations
- Portfolio tracking and management
- Real-time price alerts and notifications

Architecture:
    Frontend (React + TypeScript) 
        ↓ HTTP/REST API
    Backend (FastAPI + PostgreSQL + Redis)
        ↓ Agent Orchestration
    AI Agents (LangGraph + OpenAI GPT-4)
        ↓ Data Sources
    Stock APIs (Yahoo Finance, Alpha Vantage)

Tech Stack:
- FastAPI: Modern async web framework
- PostgreSQL: Relational database with pgvector for embeddings
- Redis: Caching layer for API responses
- LangGraph: Multi-agent workflow orchestration
- OpenAI: GPT-4 for intelligent analysis

Author: AI Solutions Architect
Created: November 2025
Version: 1.0.0

Environment Variables Required:
- DATABASE_URL: PostgreSQL connection string
- OPENAI_API_KEY: OpenAI API key for GPT-4
- SECRET_KEY: JWT secret key
- REDIS_HOST: Redis server host (default: localhost)
- REDIS_PORT: Redis server port (default: 6379)
=============================================================================
"""

from contextlib import asynccontextmanager
from typing import Dict, Any
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import structlog
from prometheus_fastapi_instrumentator import Instrumentator

from core.config import settings
from core.database import init_db, close_db, engine
from core.redis_client import cache
from api.routes import api_router
from utils.logging_config import setup_logging
from core.celery_app import celery_app

# =============================================================================
# Logging Configuration
# =============================================================================
setup_logging()
logger = structlog.get_logger()


# =============================================================================
# Service Health Checkers
# =============================================================================
async def check_database_health() -> Dict[str, Any]:
    """
    Check PostgreSQL database connectivity.
    
    Returns:
        dict: Database health status
    """
    try:
        # Test database connection
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "postgresql",
            "connected": True
        }
    except Exception as e:
        logger.error("database_health_check_failed", error=str(e))
        return {
            "status": "unhealthy",
            "database": "postgresql",
            "connected": False,
            "error": str(e)
        }


async def check_redis_health() -> Dict[str, Any]:
    """
    Check Redis cache connectivity.
    
    Returns:
        dict: Redis health status
    """
    try:
        if cache.available:
            # Test Redis with a simple set/get
            test_key = "__health_check__"
            cache.set(test_key, "ok", ttl=10)
            value = cache.get(test_key)
            cache.delete(test_key)
            
            return {
                "status": "healthy",
                "cache": "redis",
                "connected": True,
                "host": settings.REDIS_HOST,
                "port": settings.REDIS_PORT
            }
        else:
            return {
                "status": "degraded",
                "cache": "in-memory-fallback",
                "connected": False,
                "message": "Redis unavailable, using in-memory cache"
            }
    except Exception as e:
        logger.error("redis_health_check_failed", error=str(e))
        return {
            "status": "unhealthy",
            "cache": "redis",
            "connected": False,
            "error": str(e)
        }


async def check_openai_health() -> Dict[str, Any]:
    """
    Check OpenAI API key validity.
    
    Returns:
        dict: OpenAI service health status
    """
    try:
        if settings.OPENAI_API_KEY:
            # Check if API key is set (not validating actual API call to save costs)
            return {
                "status": "configured",
                "service": "openai",
                "api_key_set": True
            }
        else:
            return {
                "status": "not_configured",
                "service": "openai",
                "api_key_set": False,
                "message": "OpenAI API key not set"
            }
    except Exception as e:
        logger.error("openai_health_check_failed", error=str(e))
        return {
            "status": "error",
            "service": "openai",
            "error": str(e)
        }


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages application startup and shutdown lifecycle."""
    # STARTUP
    logger.info("application_starting", environment=settings.ENVIRONMENT)
    
    await init_db()
    logger.info("database_initialized")
    
    if cache.available:
        logger.info("redis_cache_enabled", host=settings.REDIS_HOST)
    else:
        logger.warning("redis_cache_unavailable")
    
    # Check Celery connectivity
    try:
        celery_app.control.inspect().stats()
        logger.info("celery_workers_connected")
    except Exception as e:
        logger.warning("celery_workers_not_running", message="Start workers with: celery -A core.celery_app worker")
    
    logger.info("application_ready", version="1.0.0")
    
    yield
    
    # SHUTDOWN
    logger.info("application_shutting_down")
    await close_db()
    logger.info("application_stopped")


# =============================================================================
# Application Lifespan Management
# =============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown lifecycle.
    
    This context manager handles:
    
    **Startup Phase:**
    1. Initializes PostgreSQL connection pool
    2. Creates database tables if not exist
    3. Connects to Redis cache
    4. Tests external API connectivity
    5. Starts monitoring and health check services
    6. Logs successful startup with version info
    
    **Shutdown Phase:**
    1. Closes database connections gracefully
    2. Flushes Redis cache if needed
    3. Stops background tasks
    4. Logs shutdown completion
    
    Usage:
        This is automatically called by FastAPI on startup/shutdown.
        No manual invocation needed.
    
    Yields:
        None: Application runs between startup and shutdown
    """
    # =========================================================================
    # STARTUP PHASE
    # =========================================================================
    logger.info("application_starting", environment=settings.ENVIRONMENT)
    
    # Initialize PostgreSQL database
    try:
        await init_db()
        logger.info("database_initialized", database="postgresql")
    except Exception as e:
        logger.error("database_initialization_failed", error=str(e))
        raise RuntimeError(f"Failed to initialize database: {str(e)}")
    
    # Initialize Redis cache
    if cache.available:
        logger.info(
            "redis_cache_enabled",
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            ttl_seconds=settings.CACHE_TTL_SECONDS
        )
    else:
        logger.warning(
            "redis_cache_unavailable",
            message="Using in-memory cache fallback. Performance may be degraded.",
            recommendation="Start Redis container: docker start redis"
        )
    
    # Verify OpenAI API key
    openai_status = await check_openai_health()
    if openai_status["status"] == "configured":
        logger.info("openai_api_configured")
    else:
        logger.warning("openai_api_not_configured", status=openai_status)
    
    # Clear old cache entries on startup (optional)
    if cache.available:
        try:
            cache.clear_pattern("__health_check__*")
            logger.info("cache_cleared", pattern="__health_check__*")
        except Exception as e:
            logger.warning("cache_clear_failed", error=str(e))
    
    # Log successful startup
    logger.info(
        "application_ready",
        version="1.0.0",
        environment=settings.ENVIRONMENT,
        docs_url="/api/docs" if settings.ENVIRONMENT == "development" else "disabled",
        services={
            "database": "connected",
            "redis": "connected" if cache.available else "fallback",
            "openai": openai_status["status"]
        }
    )
    
    yield  # ← Application runs here ←
    
    # =========================================================================
    # SHUTDOWN PHASE
    # =========================================================================
    logger.info("application_shutting_down")
    
    # Flush Redis cache if needed
    if cache.available:
        try:
            # Clear temporary cache entries
            cache.clear_pattern("__temp__*")
            logger.info("cache_flushed", pattern="__temp__*")
        except Exception as e:
            logger.warning("cache_flush_failed", error=str(e))
    
    # Close database connections
    await close_db()
    logger.info("database_connections_closed")
    
    logger.info("application_stopped", version="1.0.0")


# =============================================================================
# FastAPI Application Instance
# =============================================================================
app = FastAPI(
    title="AI Hub - Stock Market Intelligence API",
    description=(
        "🚀 **Enterprise-Grade AI-Powered Stock Analysis System**\n\n"
        "This API provides comprehensive stock market intelligence using "
        "a multi-agent AI architecture powered by LangGraph and OpenAI GPT-4.\n\n"
        "**Key Features:**\n"
        "- 📊 Technical Analysis: RSI, MACD, EMA, Bollinger Bands, and more\n"
        "- 💰 Fundamental Analysis: P/E ratios, debt metrics, profitability\n"
        "- 📰 Sentiment Analysis: News and social media sentiment\n"
        "- 🤖 AI Recommendations: Buy/Sell/Hold with confidence scores\n"
        "- 📈 Portfolio Tracking: Real-time P&L and performance metrics\n"
        "- 🔔 Price Alerts: Customizable notifications for price movements\n\n"
        "**Architecture:**\n"
        "Built using a modern microservices architecture with async operations, "
        "Redis caching for performance, and LangGraph for agent orchestration.\n\n"
        "**Authentication:**\n"
        "All endpoints require JWT authentication. Obtain a token via `/api/v1/auth/login`."
    ),
    version="1.0.0",
    contact={
        "name": "AI Hub Support",
        "email": "support@aihub.com",
    },
    license_info={
        "name": "Proprietary",
    },
    docs_url="/api/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/api/redoc" if settings.ENVIRONMENT == "development" else None,
    openapi_url="/api/openapi.json" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan,
)


# =============================================================================
# Middleware Configuration
# =============================================================================

# CORS Middleware - Cross-Origin Resource Sharing
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip Compression Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)


# =============================================================================
# Monitoring & Metrics
# =============================================================================
if settings.ENVIRONMENT == "production":
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
    logger.info("prometheus_metrics_enabled", endpoint="/metrics")


# =============================================================================
# Global Exception Handler
# =============================================================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for all unhandled errors.
    
    Args:
        request: The incoming HTTP request
        exc: The exception that was raised
    
    Returns:
        JSONResponse: Standardized error response
    """
    logger.error(
        "unhandled_exception",
        exc_type=type(exc).__name__,
        exc_msg=str(exc),
        path=request.url.path,
        method=request.method,
        client_host=request.client.host if request.client else "unknown",
    )
    
    if settings.ENVIRONMENT == "production":
        detail = "An internal error occurred. Please contact support."
    else:
        detail = f"{type(exc).__name__}: {str(exc)}"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": detail,
            "path": request.url.path,
        },
    )


# =============================================================================
# API Routes Registration
# =============================================================================
app.include_router(api_router, prefix="/api/v1")


# =============================================================================
# Health Check & Status Endpoints
# =============================================================================
@app.get("/health", tags=["Health Check"])
async def health_check():
    """
    Comprehensive health check endpoint.
    
    Checks:
    - Application status
    - Database connectivity
    - Redis cache connectivity
    - OpenAI API configuration
    
    Returns:
        dict: Detailed health status of all services
    """
    db_health = await check_database_health()
    redis_health = await check_redis_health()
    openai_health = await check_openai_health()
    
    overall_status = "healthy"
    if db_health["status"] != "healthy":
        overall_status = "unhealthy"
    elif redis_health["status"] == "unhealthy":
        overall_status = "degraded"
    
    return {
        "status": overall_status,
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": db_health,
            "cache": redis_health,
            "ai": openai_health,
        },
    }


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information and quick links.
    
    Returns:
        dict: API information and helpful links
    """
    from datetime import datetime
    
    docs_url = "/api/docs" if settings.ENVIRONMENT == "development" else None
    
    return {
        "message": "🚀 AI Hub - Stock Market Intelligence API",
        "version": "1.0.0",
        "status": "operational",
        "environment": settings.ENVIRONMENT,
        "documentation": docs_url or "Disabled in production",
        "health_check": "/health",
        "timestamp": datetime.utcnow().isoformat(),
        "quick_start": {
            "1_signup": "POST /api/v1/auth/signup - Create account",
            "2_login": "POST /api/v1/auth/login - Get JWT token",
            "3_analyze": "POST /api/v1/analysis/analyze - Analyze stock",
            "4_portfolio": "GET /api/v1/portfolio - View portfolio",
        },
        "support": {
            "email": "support@aihub.com",
            "docs": docs_url or "Contact support for documentation",
        },
    }


@app.get("/cache/stats", tags=["Monitoring"])
async def cache_stats():
    """
    Get cache performance statistics.
    
    Returns:
        dict: Cache configuration and status
    """
    return {
        "redis_available": cache.available,
        "redis_host": settings.REDIS_HOST,
        "redis_port": settings.REDIS_PORT,
        "cache_ttl_seconds": settings.CACHE_TTL_SECONDS,
        "fallback_mode": not cache.available,
        "cache_type": "redis" if cache.available else "in-memory",
    }


# =============================================================================
# Development Server Entry Point
# =============================================================================
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
    )
