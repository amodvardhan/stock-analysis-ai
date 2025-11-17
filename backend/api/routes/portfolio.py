"""
=============================================================================
AI Hub - Portfolio Management Routes
=============================================================================
Manage user's stock portfolio (holdings).

Endpoints:
- GET /portfolio - Get all portfolio holdings
- POST /portfolio - Add stock to portfolio
- DELETE /portfolio/{id} - Remove stock from portfolio
- GET /portfolio/summary - Get portfolio summary with P&L
=============================================================================
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
import structlog

from core.database import get_db
from db.models import User, Stock, Portfolio
from schemas.stock_schemas import PortfolioAddRequest, PortfolioResponse
from api.routes.auth import get_current_user
from agents.tools import get_stock_price

logger = structlog.get_logger()
router = APIRouter()


# =============================================================================
# Route: Get Portfolio
# =============================================================================
@router.get(
    "/",
    response_model=List[PortfolioResponse],
    summary="Get user's portfolio",
    description="Retrieve all stocks in user's portfolio with current values"
)
async def get_portfolio(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[PortfolioResponse]:
    """
    Get all portfolio holdings for the current user.
    
    Returns holdings with:
    - Purchase details
    - Current price and value
    - Profit/loss calculations
    """
    logger.info("get_portfolio_requested", user_id=str(current_user.id))
    
    # Fetch user's portfolio with stock details
    result = await db.execute(
        select(Portfolio, Stock)
        .join(Stock, Portfolio.stock_id == Stock.id)
        .where(Portfolio.user_id == current_user.id)
        .order_by(Portfolio.created_at.desc())
    )
    
    holdings = []
    for portfolio_item, stock in result:
        # Calculate current value and P&L
        current_price = stock.current_price or portfolio_item.purchase_price
        current_value = current_price * portfolio_item.quantity
        cost_basis = portfolio_item.purchase_price * portfolio_item.quantity
        profit_loss = current_value - cost_basis
        profit_loss_percent = (profit_loss / cost_basis * 100) if cost_basis > 0 else 0
        
        # Update portfolio record (in background)
        portfolio_item.current_value = current_value
        portfolio_item.profit_loss = profit_loss
        portfolio_item.profit_loss_percent = profit_loss_percent
        
        holdings.append(
            PortfolioResponse(
                id=portfolio_item.id,
                symbol=stock.symbol,
                company_name=stock.company_name,
                quantity=portfolio_item.quantity,
                purchase_price=portfolio_item.purchase_price,
                current_price=current_price,
                current_value=current_value,
                profit_loss=profit_loss,
                profit_loss_percent=profit_loss_percent,
                purchase_date=portfolio_item.purchase_date
            )
        )
    
    # Commit P&L updates
    await db.commit()
    
    logger.info("portfolio_retrieved", user_id=str(current_user.id), holdings_count=len(holdings))
    return holdings


# =============================================================================
# Route: Add to Portfolio
# =============================================================================
@router.post(
    "/",
    response_model=PortfolioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add stock to portfolio",
    description="Record a stock purchase in your portfolio"
)
async def add_to_portfolio(
    request: PortfolioAddRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> PortfolioResponse:
    """
    Add a stock holding to user's portfolio.
    
    This records a purchase for tracking purposes.
    """
    logger.info(
        "add_to_portfolio_requested",
        user_id=str(current_user.id),
        symbol=request.symbol
    )
    
    # Get or create stock record
    result = await db.execute(
        select(Stock).where(
            Stock.symbol == request.symbol,
            Stock.market == request.market
        )
    )
    stock = result.scalar_one_or_none()
    
    if not stock:
        # Fetch stock data and create record
        try:
            stock_data = await get_stock_price(request.symbol, request.market)
            
            if "error" in stock_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Could not fetch stock data: {stock_data['error']}"
                )
            
            stock = Stock(
                symbol=request.symbol,
                market=request.market,
                company_name=stock_data.get('symbol', request.symbol),
                current_price=stock_data.get('current_price'),
                previous_close=stock_data.get('previous_close'),
                market_cap=stock_data.get('market_cap'),
                pe_ratio=stock_data.get('pe_ratio')
            )
            db.add(stock)
            await db.flush()
            
        except Exception as e:
            logger.error("failed_to_fetch_stock_data", symbol=request.symbol, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid stock symbol or market"
            )
    
    # Create portfolio entry
    portfolio_item = Portfolio(
        user_id=current_user.id,
        stock_id=stock.id,
        quantity=request.quantity,
        purchase_price=request.purchase_price,
        purchase_date=request.purchase_date,
        current_value=request.purchase_price * request.quantity,
        profit_loss=0,
        profit_loss_percent=0
    )
    
    db.add(portfolio_item)
    await db.commit()
    await db.refresh(portfolio_item)
    
    logger.info(
        "stock_added_to_portfolio",
        user_id=str(current_user.id),
        symbol=request.symbol,
        quantity=request.quantity
    )
    
    return PortfolioResponse(
        id=portfolio_item.id,
        symbol=stock.symbol,
        company_name=stock.company_name,
        quantity=portfolio_item.quantity,
        purchase_price=portfolio_item.purchase_price,
        current_price=stock.current_price,
        current_value=portfolio_item.current_value,
        profit_loss=portfolio_item.profit_loss,
        profit_loss_percent=portfolio_item.profit_loss_percent,
        purchase_date=portfolio_item.purchase_date
    )


# =============================================================================
# Route: Remove from Portfolio
# =============================================================================
@router.delete(
    "/{portfolio_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove stock from portfolio",
    description="Delete a holding from your portfolio"
)
async def remove_from_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove a stock holding from portfolio.
    
    Use this when you've sold a stock.
    """
    logger.info(
        "remove_from_portfolio_requested",
        user_id=str(current_user.id),
        portfolio_id=portfolio_id
    )
    
    # Fetch and verify ownership
    result = await db.execute(
        select(Portfolio).where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id
        )
    )
    portfolio_item = result.scalar_one_or_none()
    
    if not portfolio_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio item not found"
        )
    
    await db.delete(portfolio_item)
    await db.commit()
    
    logger.info(
        "stock_removed_from_portfolio",
        user_id=str(current_user.id),
        portfolio_id=portfolio_id
    )
    
    return None


# =============================================================================
# Route: Portfolio Summary
# =============================================================================
@router.get(
    "/summary",
    summary="Get portfolio summary",
    description="Get aggregated portfolio statistics (total value, P&L, etc.)"
)
async def get_portfolio_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get portfolio summary with aggregated statistics.
    
    Returns:
    - Total portfolio value
    - Total profit/loss
    - Total P&L percentage
    - Number of holdings
    - Best/worst performers
    """
    logger.info("get_portfolio_summary_requested", user_id=str(current_user.id))
    
    # Get all portfolio items
    result = await db.execute(
        select(Portfolio, Stock)
        .join(Stock, Portfolio.stock_id == Stock.id)
        .where(Portfolio.user_id == current_user.id)
    )
    
    holdings = list(result)
    
    if not holdings:
        return {
            "total_holdings": 0,
            "total_invested": 0,
            "current_value": 0,
            "total_profit_loss": 0,
            "total_profit_loss_percent": 0,
            "best_performer": None,
            "worst_performer": None
        }
    
    total_invested = 0
    total_current_value = 0
    performers = []
    
    for portfolio_item, stock in holdings:
        cost_basis = portfolio_item.purchase_price * portfolio_item.quantity
        current_price = stock.current_price or portfolio_item.purchase_price
        current_value = current_price * portfolio_item.quantity
        profit_loss_percent = ((current_value - cost_basis) / cost_basis * 100) if cost_basis > 0 else 0
        
        total_invested += cost_basis
        total_current_value += current_value
        
        performers.append({
            "symbol": stock.symbol,
            "profit_loss_percent": profit_loss_percent
        })
    
    total_profit_loss = total_current_value - total_invested
    total_profit_loss_percent = (total_profit_loss / total_invested * 100) if total_invested > 0 else 0
    
    # Find best and worst performers
    performers.sort(key=lambda x: x["profit_loss_percent"], reverse=True)
    
    return {
        "total_holdings": len(holdings),
        "total_invested": round(total_invested, 2),
        "current_value": round(total_current_value, 2),
        "total_profit_loss": round(total_profit_loss, 2),
        "total_profit_loss_percent": round(total_profit_loss_percent, 2),
        "best_performer": performers[0] if performers else None,
        "worst_performer": performers[-1] if performers else None
    }
