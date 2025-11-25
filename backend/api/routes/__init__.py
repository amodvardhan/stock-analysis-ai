"""
API Routes package initialization.
"""

from fastapi import APIRouter
from api.routes import auth, analysis, portfolio, stocks, notifications, watchlist, recommendations

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["AI Analysis"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio"])

# If stocks.router is your generic stock info router, keep it like:
api_router.include_router(stocks.router, prefix="/stocks", tags=["Stocks"])

# Use the dedicated watchlist router here:
api_router.include_router(watchlist.router, prefix="/watchlist", tags=["Watchlist"])

api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])

# AI-powered stock recommendations
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])

__all__ = ["api_router"]
