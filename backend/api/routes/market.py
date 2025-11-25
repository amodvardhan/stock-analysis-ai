"""
=============================================================================
Market API Routes
=============================================================================
Endpoints for market overview, movers, sectors, and news.
=============================================================================
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel
import structlog
from services.market_overview_service import MarketOverviewService
from services.market_movers_service import MarketMoversService
from services.sector_service import SectorService
from services.news_service import NewsService
from services.options_service import OptionsService
from services.financials_service import FinancialsService
from services.peer_comparison_service import PeerComparisonService
from services.corporate_actions_service import CorporateActionsService
from services.earnings_service import EarningsService
from api.routes.auth import get_current_user
from db.models import User

logger = structlog.get_logger()
router = APIRouter()


# Market Overview Endpoints
@router.get("/overview")
async def get_market_overview(
    market: str = Query(default="india_nse", description="Market identifier"),
    include_sectors: bool = Query(default=True, description="Include sector analysis"),
    include_indices: bool = Query(default=True, description="Include index performance"),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive market overview.
    
    Returns:
        - Market indices performance
        - Sector-wise performance
        - Market statistics
        - AI-powered insights
    """
    try:
        result = await MarketOverviewService.get_market_overview(
            market=market,
            include_sectors=include_sectors,
            include_indices=include_indices
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error("market_overview_endpoint_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# Market Movers Endpoints
@router.get("/movers")
async def get_market_movers(
    market: str = Query(default="india_nse", description="Market identifier"),
    movers_type: str = Query(
        default="all",
        description="Type of movers: gainers, losers, active, all"
    ),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of stocks"),
    current_user: User = Depends(get_current_user)
):
    """
    Get market movers (top gainers, losers, most active).
    
    Returns:
        - Top gainers
        - Top losers
        - Most active stocks
        - Volume leaders
        - AI insights
    """
    try:
        result = await MarketMoversService.get_market_movers(
            market=market,
            movers_type=movers_type,
            limit=limit
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error("market_movers_endpoint_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# Sector Analysis Endpoints
@router.get("/sectors")
async def get_sector_analysis(
    market: str = Query(default="india_nse", description="Market identifier"),
    sector: Optional[str] = Query(default=None, description="Specific sector to analyze"),
    compare_sectors: bool = Query(default=False, description="Compare all sectors"),
    current_user: User = Depends(get_current_user)
):
    """
    Get sector analysis.
    
    Returns:
        - Sector performance data
        - Sector comparison (if requested)
        - AI-powered insights
    """
    try:
        result = await SectorService.get_sector_analysis(
            market=market,
            sector=sector,
            compare_sectors=compare_sectors
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error("sector_analysis_endpoint_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# News Endpoints
@router.get("/news")
async def get_news(
    symbol: Optional[str] = Query(default=None, description="Stock symbol for stock-specific news"),
    market: Optional[str] = Query(default=None, description="Market identifier"),
    limit: int = Query(default=10, ge=1, le=50, description="Maximum number of news items"),
    days_back: int = Query(default=7, ge=1, le=30, description="Number of days to look back"),
    current_user: User = Depends(get_current_user)
):
    """
    Get financial news with sentiment analysis.
    
    Returns:
        - News items with sentiment
        - Overall sentiment summary
        - AI-powered insights
    """
    try:
        result = await NewsService.get_news(
            symbol=symbol,
            market=market,
            limit=limit,
            days_back=days_back
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error("news_endpoint_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# Options Chain Endpoints
@router.get("/options/{symbol}")
async def get_options_chain(
    symbol: str,
    market: str = Query(default="india_nse", description="Market identifier"),
    expiration_date: Optional[str] = Query(default=None, description="Expiration date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user)
):
    """
    Get options chain analysis for a stock.
    
    Returns:
        - Options chain data (calls and puts)
        - Greeks and metrics
        - Strategy recommendations
        - AI insights
    """
    try:
        result = await OptionsService.get_options_analysis(
            symbol=symbol,
            market=market,
            expiration_date=expiration_date
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error("options_endpoint_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# Financials Endpoints
@router.get("/financials/{symbol}")
async def get_financial_analysis(
    symbol: str,
    market: str = Query(default="india_nse", description="Market identifier"),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive financial analysis.
    
    Returns:
        - Financial statements (P&L, Balance Sheet, Cash Flow)
        - Key ratios
        - Financial health score
        - Year-over-year analysis
        - AI insights
    """
    try:
        result = await FinancialsService.get_financial_analysis(
            symbol=symbol,
            market=market
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Financial analysis service returned empty result")
        
        # Only raise error if we have no useful data
        if "error" in result and result["error"]:
            if "financial_statements" not in result and "key_ratios" not in result:
                raise HTTPException(status_code=500, detail=result["error"])
            # If we have partial data, include the error but don't fail
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error("financials_endpoint_error", 
                    error=str(e), 
                    error_type=type(e).__name__,
                    traceback=error_trace,
                    symbol=symbol)
        raise HTTPException(status_code=500, detail=f"Financial analysis failed: {str(e)}")


# Peer Comparison Models
class CompareStocksRequest(BaseModel):
    symbols: List[str]


# Peer Comparison Endpoints
@router.post("/compare")
async def compare_stocks(
    request: CompareStocksRequest,
    market: str = Query(default="india_nse", description="Market identifier"),
    current_user: User = Depends(get_current_user)
):
    """
    Compare multiple stocks side-by-side.
    
    Returns:
        - Comparison matrix
        - Best performers
        - AI insights
    """
    try:
        symbols = request.symbols
        if not symbols or not isinstance(symbols, list):
            raise HTTPException(status_code=400, detail="Symbols must be a list")
        
        if len(symbols) < 2:
            raise HTTPException(status_code=400, detail="At least 2 symbols required for comparison")
        
        if len(symbols) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 symbols allowed for comparison")
        
        # Validate symbols are strings
        symbols = [str(s).upper().strip() for s in symbols if s]
        if len(symbols) < 2:
            raise HTTPException(status_code=400, detail="At least 2 valid symbols required")
        
        logger.info("peer_comparison_request", symbols=symbols, market=market)
        
        result = await PeerComparisonService.compare_stocks(
            symbols=symbols,
            market=market
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Comparison service returned empty result")
        
        if "error" in result and result["error"]:
            logger.error("peer_comparison_result_has_error", error=result["error"], symbols=symbols)
            # Don't raise 500 if we have partial data
            if "comparison" not in result and "best_performers" not in result:
                raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error("peer_comparison_endpoint_error", 
                    error=str(e), 
                    error_type=type(e).__name__,
                    traceback=error_trace,
                    symbols=symbols if 'symbols' in locals() else None)
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


# Corporate Actions Endpoints
@router.get("/corporate-actions/{symbol}")
async def get_corporate_actions(
    symbol: str,
    market: str = Query(default="india_nse", description="Market identifier"),
    action_type: str = Query(default="all", description="Type: dividend, split, all"),
    current_user: User = Depends(get_current_user)
):
    """
    Get corporate actions for a stock.
    
    Returns:
        - Dividend history
        - Stock split history
        - Upcoming events
    """
    try:
        result = await CorporateActionsService.get_corporate_actions(
            symbol=symbol,
            market=market,
            action_type=action_type
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error("corporate_actions_endpoint_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# Earnings Calendar Endpoints
@router.get("/earnings")
async def get_earnings_calendar(
    market: str = Query(default="india_nse", description="Market identifier"),
    days_ahead: int = Query(default=30, ge=1, le=90, description="Days to look ahead"),
    current_user: User = Depends(get_current_user)
):
    """
    Get earnings calendar.
    
    Returns:
        - Upcoming earnings announcements
        - Earnings dates
        - Estimated EPS
    """
    try:
        result = await EarningsService.get_earnings_calendar(
            market=market,
            days_ahead=days_ahead
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error("earnings_calendar_endpoint_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# IPO Calendar Endpoints
@router.get("/ipos")
async def get_ipo_calendar(
    market: str = Query(default="india_nse", description="Market identifier"),
    days_ahead: int = Query(default=90, ge=1, le=180, description="Days to look ahead"),
    current_user: User = Depends(get_current_user)
):
    """
    Get IPO calendar.
    
    Returns:
        - Upcoming IPOs
        - Recent IPOs
    """
    try:
        result = await EarningsService.get_ipo_calendar(
            market=market,
            days_ahead=days_ahead
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error("ipo_calendar_endpoint_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

