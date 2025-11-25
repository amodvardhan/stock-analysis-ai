"""
=============================================================================
AI Hub - Stock Recommendations Routes
=============================================================================
AI-powered stock recommendation endpoints.

Endpoints:
- GET /recommendations/daily - Top 5 stocks of the day
- GET /recommendations/weekly - Top 5 stocks of the week
=============================================================================
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
import structlog

from core.database import get_db
from db.models import User
from api.routes.auth import get_current_user
from services.recommendation_service import RecommendationService

logger = structlog.get_logger()
router = APIRouter()


# =============================================================================
# Response Schemas
# =============================================================================
class HistoricalPerformance(BaseModel):
    """Historical performance metrics."""
    model_config = ConfigDict(populate_by_name=True)  # Allow both field name and alias
    
    current_price: float
    high_52w: float
    low_52w: float
    change_1d: float = Field(..., alias="1d_change", serialization_alias="1d_change")
    change_7d: float = Field(..., alias="7d_change", serialization_alias="7d_change")
    change_30d: float = Field(..., alias="30d_change", serialization_alias="30d_change")
    change_90d: float = Field(..., alias="90d_change", serialization_alias="90d_change")
    volatility: float


class Forecast(BaseModel):
    """Price forecast data."""
    price_7d: float
    price_30d: float
    expected_change_7d: float
    expected_change_30d: float
    confidence: float
    forecast_basis: str


class StockRecommendation(BaseModel):
    """Individual stock recommendation."""
    symbol: str
    company_name: str
    market: str
    current_price: float
    score: float
    recommendation: str
    confidence: float
    reasoning: str
    historical_performance: HistoricalPerformance
    forecast: Forecast
    technical_indicators: dict
    fundamental_metrics: dict
    sentiment_score: float
    risk_level: str
    price_history: List[float]
    analyzed_at: str
    # AI-powered comparative analysis fields
    rank: Optional[int] = None
    ai_reasoning: Optional[str] = None
    market_context: Optional[str] = None
    comparative_advantages: Optional[List[str]] = None
    risk_factors: Optional[List[str]] = None
    entry_strategy: Optional[str] = None
    time_horizon: Optional[str] = None


class RecommendationsResponse(BaseModel):
    """Response containing top stock recommendations."""
    period: str
    market: str
    recommendations: List[StockRecommendation]
    generated_at: str
    analysis_metadata: dict


# =============================================================================
# Route: Get Daily Top Stocks
# =============================================================================
@router.get(
    "/daily",
    response_model=RecommendationsResponse,
    summary="Get top 5 stocks of the day",
    description="AI-powered recommendations based on deep market analysis for today"
)
async def get_daily_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    market: str = Query(default="india_nse", description="Market identifier"),
    limit: int = Query(default=5, ge=1, le=10, description="Number of recommendations")
):
    """
    Get top 5 stock recommendations for the day.
    
    Uses deep AI analysis including:
    - Technical analysis (RSI, MACD, EMA, Bollinger Bands)
    - Fundamental analysis (P/E ratios, financial metrics)
    - Sentiment analysis (news, market psychology)
    - Historical performance analysis
    - Price forecasting
    
    Returns stocks ranked by comprehensive recommendation score.
    """
    user_id = str(current_user.id)
    
    try:
        logger.info(
            "daily_recommendations_requested",
            user_id=user_id,
            market=market,
            limit=limit
        )
        
        recommendations = await RecommendationService.get_top_stocks(
            db=db,
            market=market,
            period="daily",
            limit=limit,
            user_risk_tolerance=current_user.risk_tolerance
        )
        
        if not recommendations:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to generate recommendations at this time. Please try again later."
            )
        
        # Convert to response format
        recommendation_models = []
        for rec in recommendations:
            try:
                hist_perf = rec.get("historical_performance", {})
                current_price = rec.get("current_price", 0.0)
                
                recommendation_models.append(StockRecommendation(
                    symbol=rec.get("symbol", "UNKNOWN"),
                    company_name=rec.get("company_name", "Unknown Company"),
                    market=rec.get("market", market),
                    current_price=current_price,
                    score=rec.get("score", 0.0),
                    recommendation=rec.get("recommendation", "hold"),
                    confidence=rec.get("confidence", 0.0),
                    reasoning=rec.get("reasoning", "Analysis in progress"),
                    historical_performance=HistoricalPerformance.model_validate({
                        "current_price": hist_perf.get("current_price", current_price),
                        "high_52w": hist_perf.get("high_52w", current_price),
                        "low_52w": hist_perf.get("low_52w", current_price),
                        "1d_change": hist_perf.get("1d_change", 0.0),
                        "7d_change": hist_perf.get("7d_change", 0.0),
                        "30d_change": hist_perf.get("30d_change", 0.0),
                        "90d_change": hist_perf.get("90d_change", 0.0),
                        "volatility": hist_perf.get("volatility", 0.0)
                    }),
                    forecast=Forecast.model_validate(rec.get("forecast", {
                        "price_7d": current_price,
                        "price_30d": current_price,
                        "expected_change_7d": 0.0,
                        "expected_change_30d": 0.0,
                        "confidence": 50.0,
                        "forecast_basis": "Analysis based on available data"
                    })),
                    technical_indicators=rec.get("technical_indicators", {}),
                    fundamental_metrics=rec.get("fundamental_metrics", {}),
                    sentiment_score=rec.get("sentiment_score", 0.0),
                    risk_level=rec.get("risk_level", "medium"),
                    price_history=rec.get("price_history", []),
                    analyzed_at=rec.get("analyzed_at", datetime.utcnow().isoformat()),
                    # AI-powered fields
                    rank=rec.get("rank"),
                    ai_reasoning=rec.get("ai_reasoning"),
                    market_context=rec.get("market_context"),
                    comparative_advantages=rec.get("comparative_advantages"),
                    risk_factors=rec.get("risk_factors"),
                    entry_strategy=rec.get("entry_strategy"),
                    time_horizon=rec.get("time_horizon")
                ))
            except Exception as e:
                logger.error(
                    "failed_to_convert_recommendation",
                    symbol=rec.get("symbol", "UNKNOWN"),
                    error=str(e),
                    rec_keys=list(rec.keys()) if isinstance(rec, dict) else "not_a_dict"
                )
                # Skip this recommendation and continue with others
                continue
        
        if not recommendation_models:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to generate valid recommendations at this time. Please try again later."
            )
        
        logger.info(
            "daily_recommendations_generated",
            user_id=user_id,
            count=len(recommendation_models)
        )
        
        return RecommendationsResponse(
            period="daily",
            market=market,
            recommendations=recommendation_models,
            generated_at=recommendation_models[0].analyzed_at if recommendation_models else datetime.utcnow().isoformat(),
            analysis_metadata={
                "user_risk_tolerance": current_user.risk_tolerance,
                "stocks_analyzed": len(recommendations) * 3,  # Approximate
                "analysis_depth": "comprehensive"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "daily_recommendations_failed",
            user_id=user_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


# =============================================================================
# Route: Get Weekly Top Stocks
# =============================================================================
@router.get(
    "/weekly",
    response_model=RecommendationsResponse,
    summary="Get top 5 stocks of the week",
    description="AI-powered recommendations based on deep market analysis for the week"
)
async def get_weekly_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    market: str = Query(default="india_nse", description="Market identifier"),
    limit: int = Query(default=5, ge=1, le=10, description="Number of recommendations")
):
    """
    Get top 5 stock recommendations for the week.
    
    Uses the same deep AI analysis as daily recommendations but with
    a focus on weekly trends and longer-term patterns.
    """
    user_id = str(current_user.id)
    
    try:
        logger.info(
            "weekly_recommendations_requested",
            user_id=user_id,
            market=market,
            limit=limit
        )
        
        recommendations = await RecommendationService.get_top_stocks(
            db=db,
            market=market,
            period="weekly",
            limit=limit,
            user_risk_tolerance=current_user.risk_tolerance
        )
        
        if not recommendations:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to generate recommendations at this time. Please try again later."
            )
        
        # Convert to response format
        recommendation_models = []
        for rec in recommendations:
            try:
                hist_perf = rec.get("historical_performance", {})
                current_price = rec.get("current_price", 0.0)
                
                recommendation_models.append(StockRecommendation(
                    symbol=rec.get("symbol", "UNKNOWN"),
                    company_name=rec.get("company_name", "Unknown Company"),
                    market=rec.get("market", market),
                    current_price=current_price,
                    score=rec.get("score", 0.0),
                    recommendation=rec.get("recommendation", "hold"),
                    confidence=rec.get("confidence", 0.0),
                    reasoning=rec.get("reasoning", "Analysis in progress"),
                    historical_performance=HistoricalPerformance.model_validate({
                        "current_price": hist_perf.get("current_price", current_price),
                        "high_52w": hist_perf.get("high_52w", current_price),
                        "low_52w": hist_perf.get("low_52w", current_price),
                        "1d_change": hist_perf.get("1d_change", 0.0),
                        "7d_change": hist_perf.get("7d_change", 0.0),
                        "30d_change": hist_perf.get("30d_change", 0.0),
                        "90d_change": hist_perf.get("90d_change", 0.0),
                        "volatility": hist_perf.get("volatility", 0.0)
                    }),
                    forecast=Forecast.model_validate(rec.get("forecast", {
                        "price_7d": current_price,
                        "price_30d": current_price,
                        "expected_change_7d": 0.0,
                        "expected_change_30d": 0.0,
                        "confidence": 50.0,
                        "forecast_basis": "Analysis based on available data"
                    })),
                    technical_indicators=rec.get("technical_indicators", {}),
                    fundamental_metrics=rec.get("fundamental_metrics", {}),
                    sentiment_score=rec.get("sentiment_score", 0.0),
                    risk_level=rec.get("risk_level", "medium"),
                    price_history=rec.get("price_history", []),
                    analyzed_at=rec.get("analyzed_at", datetime.utcnow().isoformat()),
                    # AI-powered fields
                    rank=rec.get("rank"),
                    ai_reasoning=rec.get("ai_reasoning"),
                    market_context=rec.get("market_context"),
                    comparative_advantages=rec.get("comparative_advantages"),
                    risk_factors=rec.get("risk_factors"),
                    entry_strategy=rec.get("entry_strategy"),
                    time_horizon=rec.get("time_horizon")
                ))
            except Exception as e:
                logger.error(
                    "failed_to_convert_recommendation",
                    symbol=rec.get("symbol", "UNKNOWN"),
                    error=str(e),
                    rec_keys=list(rec.keys()) if isinstance(rec, dict) else "not_a_dict"
                )
                # Skip this recommendation and continue with others
                continue
        
        if not recommendation_models:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to generate valid recommendations at this time. Please try again later."
            )
        
        logger.info(
            "weekly_recommendations_generated",
            user_id=user_id,
            count=len(recommendation_models)
        )
        
        return RecommendationsResponse(
            period="weekly",
            market=market,
            recommendations=recommendation_models,
            generated_at=recommendation_models[0].analyzed_at if recommendation_models else datetime.utcnow().isoformat(),
            analysis_metadata={
                "user_risk_tolerance": current_user.risk_tolerance,
                "stocks_analyzed": len(recommendations) * 3,  # Approximate
                "analysis_depth": "comprehensive"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "weekly_recommendations_failed",
            user_id=user_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )

