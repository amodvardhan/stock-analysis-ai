"""
API Routes package initialization.
"""

from fastapi import APIRouter
from api.routes import auth, analysis, portfolio, stocks, notifications

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["AI Analysis"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio"])
api_router.include_router(stocks.router, prefix="/watchlist", tags=["Watchlist"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])

__all__ = ["api_router"]
