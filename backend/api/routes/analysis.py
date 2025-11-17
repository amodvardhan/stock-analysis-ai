"""
=============================================================================
AI Hub - Stock Analysis Routes
=============================================================================
Main AI-powered stock analysis endpoints.

This is where the magic happens - calls the multi-agent system!

Endpoints:
- POST /analyze - Analyze a stock using AI agents
=============================================================================
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from core.database import get_db
from db.models import User, Stock, StockAnalysis, TradingSignal
from schemas.stock_schemas import StockAnalysisRequest, StockAnalysisResponse
from api.routes.auth import get_current_user
from agents.orchestrator import analyze_stock
from datetime import datetime, timedelta

logger = structlog.get_logger()
router = APIRouter()


# =============================================================================
# Route: Analyze Stock
# =============================================================================
@router.post(
    "/analyze",
    response_model=StockAnalysisResponse,
    summary="Analyze stock with AI agents",
    description="""
    Perform comprehensive AI-powered stock analysis using multi-agent system.
    
    The system runs three specialist agents in parallel:
    - Technical Analysis Agent (chart patterns, indicators)
    - Fundamental Analysis Agent (company financials, valuation)
    - Sentiment Analysis Agent (news, market psychology)
    
    Then synthesizes their recommendations into a final buy/sell/hold decision.
    
    This typically takes 15-30 seconds to complete.
    """
)
async def analyze_stock_endpoint(
    request: StockAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> StockAnalysisResponse:
    """
    Main stock analysis endpoint.
    
    This is the core of the AI Hub - calls the multi-agent orchestrator!
    """
    logger.info(
        "stock_analysis_requested",
        user_id=str(current_user.id),
        symbol=request.symbol,
        market=request.market
    )
    
    try:
        # Call the multi-agent orchestrator
        result = await analyze_stock(
            symbol=request.symbol,
            market=request.market,
            company_name=request.company_name,
            user_risk_tolerance=request.user_risk_tolerance or current_user.risk_tolerance
        )
        
        # Check for errors
        if "error" in result.get("final_recommendation", {}):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["final_recommendation"]["error"]
            )
        
        # Save analysis to database (in background to not slow down response)
        await save_analysis_to_db(db, result)
        
        logger.info(
            "stock_analysis_completed",
            user_id=str(current_user.id),
            symbol=request.symbol,
            recommendation=result["final_recommendation"].get("final_recommendation")
        )
        
        return StockAnalysisResponse(**result)
        
    except Exception as e:
        logger.error(
            "stock_analysis_failed",
            user_id=str(current_user.id),
            symbol=request.symbol,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


async def save_analysis_to_db(db: AsyncSession, analysis_result: dict):
    """
    Save analysis results to database for future reference.
    
    This allows:
    - Historical tracking of recommendations
    - Performance evaluation (were our predictions correct?)
    - Pattern learning over time
    """
    try:
        symbol = analysis_result["symbol"]
        market = analysis_result["market"]
        
        # Get or create stock record
        result = await db.execute(
            select(Stock).where(
                Stock.symbol == symbol,
                Stock.market == market
            )
        )
        stock = result.scalar_one_or_none()
        
        if not stock:
            # Create new stock record
            tech_analysis = analysis_result["analyses"].get("technical", {})
            fund_analysis = analysis_result["analyses"].get("fundamental", {})
            
            stock = Stock(
                symbol=symbol,
                market=market,
                company_name=fund_analysis.get("company_name", symbol),
                sector=fund_analysis.get("fundamental_details", {}).get("company_profile", {}).get("sector"),
                current_price=tech_analysis.get("current_price"),
                last_data_refresh=datetime.utcnow()
            )
            db.add(stock)
            await db.flush()  # Get stock.id
        
        # Save stock analysis
        final_rec = analysis_result["final_recommendation"]
        
        stock_analysis = StockAnalysis(
            stock_id=stock.id,
            analysis_type="comprehensive",
            confidence_score=final_rec.get("confidence", 0) / 100,
            technical_indicators=analysis_result["analyses"].get("technical", {}).get("technical_details"),
            fundamental_metrics=analysis_result["analyses"].get("fundamental", {}).get("fundamental_details"),
            sentiment_analysis=analysis_result["analyses"].get("sentiment", {}).get("sentiment_details"),
            summary=final_rec.get("synthesis_reasoning", ""),
            recommendation=final_rec.get("final_recommendation", "hold"),
            reasoning=final_rec.get("full_synthesis", ""),
            risk_level=final_rec.get("risk_level", "medium"),
            agent_metadata={
                "technical_confidence": analysis_result["analyses"].get("technical", {}).get("confidence"),
                "fundamental_confidence": analysis_result["analyses"].get("fundamental", {}).get("confidence"),
                "sentiment_confidence": analysis_result["analyses"].get("sentiment", {}).get("confidence"),
            },
            analyzed_at=datetime.utcnow(),
            valid_until=datetime.utcnow() + timedelta(hours=24)  # Analysis valid for 24 hours
        )
        db.add(stock_analysis)
        
        # If strong recommendation, create trading signal
        if final_rec.get("final_recommendation") in ["strong_buy", "strong_sell", "buy", "sell"]:
            trading_signal = TradingSignal(
                stock_id=stock.id,
                analysis_id=None,  # Will be set after commit
                signal_type=final_rec["final_recommendation"].replace("strong_", ""),
                signal_strength=final_rec.get("confidence", 0) / 100,
                trigger_price=final_rec.get("entry_price", stock.current_price),
                target_price=final_rec.get("target_price"),
                stop_loss=final_rec.get("stop_loss"),
                reason=final_rec.get("synthesis_reasoning", ""),
                is_active=True,
                executed=False,
                generated_at=datetime.utcnow()
            )
            db.add(trading_signal)
        
        await db.commit()
        logger.info("analysis_saved_to_database", symbol=symbol)
        
    except Exception as e:
        logger.error("failed_to_save_analysis", symbol=symbol, error=str(e))
        # Don't raise - we don't want to fail the API call if saving fails
