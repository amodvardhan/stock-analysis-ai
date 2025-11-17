"""
=============================================================================
AI Hub - Main FastAPI Application Entry Point
=============================================================================
This is the main application file that initializes FastAPI, configures
middleware, registers routes, and sets up lifecycle events.

Author: AI Solutions Architect
Date: November 2025
=============================================================================
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import structlog
from prometheus_fastapi_instrumentator import Instrumentator

from core.config import settings
from core.database import init_db, close_db
from api.routes import api_router
from utils.logging_config import setup_logging

# -------------------------
# Setup Structured Logging
# -------------------------
setup_logging()
logger = structlog.get_logger()


# -------------------------
# Application Lifespan Events
# -------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown events.
    
    Startup:
        - Initialize database connection pool
        - Start background monitoring tasks
        - Log application start
    
    Shutdown:
        - Close database connections gracefully
        - Stop background tasks
        - Log application shutdown
    """
    # Startup
    logger.info("application_starting", environment=settings.ENVIRONMENT)
    
    # Initialize database
    await init_db()
    logger.info("database_initialized")
    
    # TODO: Start Celery background tasks for stock monitoring
    # start_stock_monitoring_tasks()
    
    logger.info("application_ready", version="1.0.0")
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("application_shutting_down")
    await close_db()
    logger.info("application_stopped")


# -------------------------
# FastAPI Application Instance
# -------------------------
app = FastAPI(
    title="AI Hub - Stock Market Intelligence API",
    description=(
        "Enterprise-grade AI-powered stock market analysis system using "
        "multi-agent architecture for intelligent buy/sell recommendations."
    ),
    version="1.0.0",
    docs_url="/api/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/api/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan,
)


# -------------------------
# Middleware Configuration
# -------------------------

# CORS - Allow frontend to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression for responses > 1KB
app.add_middleware(GZipMiddleware, minimum_size=1000)


# -------------------------
# Prometheus Metrics
# -------------------------
if settings.ENVIRONMENT == "production":
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")


# -------------------------
# Global Exception Handler
# -------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catches all unhandled exceptions and returns a standardized error response.
    Logs the error with full context for debugging.
    
    Args:
        request: The incoming request that caused the error
        exc: The exception that was raised
    
    Returns:
        JSONResponse with error details (sanitized in production)
    """
    logger.error(
        "unhandled_exception",
        exc_type=type(exc).__name__,
        exc_msg=str(exc),
        path=request.url.path,
        method=request.method,
    )
    
    # Don't expose internal errors in production
    if settings.ENVIRONMENT == "production":
        detail = "An internal error occurred. Please contact support."
    else:
        detail = str(exc)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": detail,
            "path": request.url.path,
        },
    )


# -------------------------
# API Routes Registration
# -------------------------
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
# app.include_router(stocks.router, prefix="/api/v1/stocks", tags=["Stocks"])
# app.include_router(portfolio.router, prefix="/api/v1/portfolio", tags=["Portfolio"])
# app.include_router(
#     notifications.router, prefix="/api/v1/notifications", tags=["Notifications"]
# )
# app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["AI Analysis"])

app.include_router(api_router, prefix="/api/v1")

# -------------------------
# Health Check Endpoints
# -------------------------
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Simple health check endpoint for monitoring and load balancers.
    
    Returns:
        dict: Status of the application
    """
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
    }


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    
    Returns:
        dict: Welcome message and API documentation link
    """
    return {
        "message": "AI Hub - Stock Market Intelligence API",
        "version": "1.0.0",
        "docs": "/api/docs" if settings.ENVIRONMENT == "development" else "Disabled in production",
        "status": "operational",
    }


# -------------------------
# Entry Point for Development
# -------------------------
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False,
        log_level=settings.LOG_LEVEL.lower(),
    )
