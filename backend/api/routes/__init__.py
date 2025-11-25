"""
API Routes package initialization.
"""

from fastapi import APIRouter
from api.routes import (
    auth, analysis, portfolio, stocks, notifications, watchlist, recommendations,
    backtesting, orders, security, risk, explainability, market
)

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

# Market data endpoints (new)
api_router.include_router(market.router, prefix="/market", tags=["Market Data"])

# New professional features
api_router.include_router(backtesting.router, prefix="/backtesting", tags=["Backtesting"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
api_router.include_router(security.router, prefix="/security", tags=["Security"])
api_router.include_router(risk.router, prefix="/risk", tags=["Risk Management"])
api_router.include_router(explainability.router, prefix="/explainability", tags=["AI Explainability"])

__all__ = ["api_router"]
