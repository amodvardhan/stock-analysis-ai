"""
=============================================================================
AI Hub - Portfolio Management Routes
=============================================================================
Manage user's stock portfolio (holdings).

Endpoints:
- GET /portfolio/summary - Get portfolio summary with P&L
- GET /portfolio/holdings - Get all holdings
- POST /portfolio/holdings - Add stock to portfolio
- DELETE /portfolio/holdings/{id} - Remove holding
- POST /portfolio/refresh - Refresh prices
=============================================================================
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import structlog

from core.database import get_db
from db.models import User, Stock, Portfolio, PortfolioHolding, MarketType
from api.routes.auth import get_current_user  # ← FIXED: Changed from api.dependencies
from services.portfolio_service import PortfolioService

logger = structlog.get_logger()
router = APIRouter()




# =============================================================================
# Request/Response Schemas
# =============================================================================
class PortfolioAddRequest(BaseModel):
    """Request to add stock to portfolio."""
    symbol: str = Field(..., description="Stock symbol (e.g., RELIANCE)")
    market: str = Field(..., description="Market (india_nse, india_bse, us_nyse, us_nasdaq)")
    quantity: int = Field(..., gt=0, description="Number of shares")
    purchase_price: float = Field(..., gt=0, description="Purchase price per share")
    purchase_date: datetime = Field(default_factory=datetime.utcnow, description="Purchase date")
    brokerage_fee: float = Field(default=0.0, ge=0, description="Brokerage charges")
    tax: float = Field(default=0.0, ge=0, description="Tax paid")
    notes: str = Field(default=None, max_length=500, description="Optional notes")


class HoldingResponse(BaseModel):
    """Individual holding response."""
    id: int
    stock: dict
    quantity: int
    average_buy_price: float
    total_invested: float
    current_price: float = None
    current_value: float = None
    unrealized_pl: float = None
    unrealized_pl_percentage: float = None
    realized_pl: float
    first_buy_date: str
    last_updated: str


class PortfolioSummaryResponse(BaseModel):
    """Complete portfolio summary."""
    portfolio: dict
    holdings: List[dict]
    sector_allocation: dict
    holdings_count: int


# =============================================================================
# Route: Get Portfolio Summary
# =============================================================================
@router.get(
    "/summary",
    response_model=PortfolioSummaryResponse,
    summary="Get portfolio summary",
    description="Get complete portfolio with holdings, metrics, and sector allocation"
)
async def get_portfolio_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    refresh: bool = Query(default=False, description="Force refresh of stock prices (slower)")
):
    """
    Get complete portfolio summary.
    
    By default, uses cached prices (updated within last hour) for fast response.
    Set refresh=true to force update all prices (may take longer).
    
    Returns:
    - Portfolio metrics (total invested, current value, P&L, return %)
    - All holdings with current prices and P&L
    - Sector allocation breakdown
    - Holdings count
    """
    # Capture user_id early to avoid issues if session is rolled back
    user_id = str(current_user.id)
    
    try:
        logger.info("portfolio_summary_requested", user_id=user_id, refresh=refresh)
        
        # Get or create default portfolio
        portfolio = await PortfolioService.get_or_create_default_portfolio(
            db, user_id
        )
        
        # Get complete summary (with optional price refresh)
        summary = await PortfolioService.get_portfolio_summary(
            db, portfolio.id, force_price_update=refresh
        )
        
        logger.info(
            "portfolio_summary_retrieved",
            user_id=user_id,
            portfolio_id=portfolio.id,
            holdings_count=summary["holdings_count"]
        )
        
        return summary
        
    except Exception as e:
        # Rollback the session if there was an error
        try:
            await db.rollback()
        except Exception:
            pass  # Ignore rollback errors
        
        logger.error("portfolio_summary_failed", error=str(e), user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch portfolio summary: {str(e)}"
        )


# =============================================================================
# Route: Get Holdings
# =============================================================================
@router.get(
    "/holdings",
    summary="Get all holdings",
    description="Get list of all holdings in portfolio"
)
async def get_holdings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all holdings for user's portfolio.
    
    Returns list of holdings with stock details and P&L.
    """
    # Capture user_id early to avoid issues if session is rolled back
    user_id = str(current_user.id)
    
    try:
        logger.info("holdings_list_requested", user_id=user_id)
        
        # Get portfolio
        portfolio = await PortfolioService.get_or_create_default_portfolio(
            db, user_id
        )
        
        # Get holdings
        holdings = await PortfolioService.get_portfolio_holdings(db, portfolio.id)
        
        logger.info(
            "holdings_list_retrieved",
            user_id=user_id,
            holdings_count=len(holdings)
        )
        
        return {"holdings": holdings, "count": len(holdings)}
        
    except Exception as e:
        try:
            await db.rollback()
        except Exception:
            pass  # Ignore rollback errors
        
        logger.error("holdings_list_failed", error=str(e), user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch holdings: {str(e)}"
        )


# =============================================================================
# Route: Add to Portfolio
# =============================================================================
@router.post(
    "/holdings",
    status_code=status.HTTP_201_CREATED,
    summary="Add stock to portfolio",
    description="Add a new stock holding or update existing one"
)
async def add_to_portfolio(
    request: PortfolioAddRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add stock to portfolio.
    
    - Creates new holding if doesn't exist
    - Updates existing holding (calculates new average price)
    - Records transaction history
    - Updates portfolio metrics
    """
    # Capture user_id early to avoid issues if session is rolled back
    user_id = str(current_user.id)
    
    try:
        logger.info(
            "add_to_portfolio_requested",
            user_id=user_id,
            symbol=request.symbol,
            quantity=request.quantity
        )
        
        # Get or create portfolio
        portfolio = await PortfolioService.get_or_create_default_portfolio(
            db, user_id
        )
        
        # Find or create stock
        result = await db.execute(
            select(Stock).where(
                Stock.symbol == request.symbol.upper(),
                Stock.market == MarketType(request.market)
            )
        )
        stock = result.scalar_one_or_none()
        
        if not stock:
            # Create stock entry
            stock = Stock(
                symbol=request.symbol.upper(),
                market=MarketType(request.market),
                company_name=request.symbol.upper(),  # Will be updated by background task
                current_price=request.purchase_price
            )
            db.add(stock)
            await db.commit()
            await db.refresh(stock)
            
            logger.info("stock_created", symbol=request.symbol, stock_id=stock.id)
        
        # Add holding
        holding = await PortfolioService.add_holding(
            db=db,
            portfolio_id=portfolio.id,
            stock_id=stock.id,
            quantity=request.quantity,
            price_per_share=request.purchase_price,
            transaction_date=request.purchase_date,
            brokerage_fee=request.brokerage_fee,
            tax=request.tax,
            notes=request.notes
        )
        
        logger.info(
            "holding_added",
            user_id=user_id,
            portfolio_id=portfolio.id,
            stock_symbol=request.symbol,
            holding_id=holding.id,
            quantity=request.quantity
        )
        
        return {
            "message": "Stock added to portfolio successfully",
            "holding_id": holding.id,
            "portfolio_id": portfolio.id,
            "symbol": request.symbol,
            "quantity": request.quantity,
            "average_buy_price": float(holding.average_buy_price)
        }
        
    except Exception as e:
        try:
            await db.rollback()
        except Exception:
            pass  # Ignore rollback errors
        
        logger.error(
            "add_to_portfolio_failed",
            error=str(e),
            user_id=user_id,
            symbol=request.symbol
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add stock to portfolio: {str(e)}"
        )


# =============================================================================
# Route: Remove from Portfolio
# =============================================================================
@router.delete(
    "/holdings/{holding_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove holding",
    description="Remove a stock holding from portfolio"
)
async def remove_from_portfolio(
    holding_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove a holding from portfolio.
    
    - Deletes the holding
    - Updates portfolio metrics
    - Keeps transaction history
    """
    # Capture user_id early to avoid issues if session is rolled back
    user_id = str(current_user.id)
    
    try:
        logger.info(
            "remove_holding_requested",
            user_id=user_id,
            holding_id=holding_id
        )
        
        # Verify ownership
        result = await db.execute(
            select(PortfolioHolding, Portfolio)
            .join(Portfolio, PortfolioHolding.portfolio_id == Portfolio.id)
            .where(
                PortfolioHolding.id == holding_id,
                Portfolio.user_id == current_user.id
            )
        )
        holding_data = result.first()
        
        if not holding_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Holding not found or not owned by user"
            )
        
        # Delete holding
        await PortfolioService.delete_holding(db, holding_id)
        
        logger.info(
            "holding_removed",
            user_id=user_id,
            holding_id=holding_id
        )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        try:
            await db.rollback()
        except Exception:
            pass  # Ignore rollback errors
        
        logger.error(
            "remove_holding_failed",
            error=str(e),
            user_id=user_id,
            holding_id=holding_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove holding: {str(e)}"
        )


# =============================================================================
# Route: Refresh Portfolio
# =============================================================================
@router.post(
    "/refresh",
    summary="Refresh portfolio",
    description="Update current prices and recalculate P&L for all holdings"
)
async def refresh_portfolio(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh portfolio prices and metrics.
    
    - Fetches latest prices for all holdings
    - Recalculates unrealized P&L
    - Updates portfolio-level metrics
    """
    # Capture user_id early to avoid issues if session is rolled back
    user_id = str(current_user.id)
    
    try:
        logger.info("portfolio_refresh_requested", user_id=user_id)
        
        # Get portfolio
        portfolio = await PortfolioService.get_or_create_default_portfolio(
            db, user_id
        )
        
        # Update all metrics
        await PortfolioService.update_portfolio_metrics(db, portfolio.id)
        
        logger.info(
            "portfolio_refreshed",
            user_id=user_id,
            portfolio_id=portfolio.id
        )
        
        return {
            "message": "Portfolio refreshed successfully",
            "portfolio_id": portfolio.id,
            "refreshed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        try:
            await db.rollback()
        except Exception:
            pass  # Ignore rollback errors
        
        logger.error(
            "portfolio_refresh_failed",
            error=str(e),
            user_id=user_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh portfolio: {str(e)}"
        )
