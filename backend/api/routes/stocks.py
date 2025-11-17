"""
=============================================================================
AI Hub - Watchlist Management Routes
=============================================================================
Manage stocks user wants to monitor.

Endpoints:
- GET /watchlist - Get all watchlist items
- POST /watchlist - Add stock to watchlist
- DELETE /watchlist/{id} - Remove from watchlist
=============================================================================
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import structlog

from core.database import get_db
from db.models import User, Stock, Watchlist
from schemas.stock_schemas import WatchlistAddRequest, WatchlistResponse
from api.routes.auth import get_current_user
from agents.tools import get_stock_price

logger = structlog.get_logger()
router = APIRouter()


# =============================================================================
# Route: Get Watchlist
# =============================================================================
@router.get(
    "/",
    response_model=List[WatchlistResponse],
    summary="Get user's watchlist",
    description="Retrieve all stocks in user's watchlist"
)
async def get_watchlist(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[WatchlistResponse]:
    """
    Get all stocks in user's watchlist.
    
    These are stocks the user wants to monitor for buy/sell opportunities.
    """
    logger.info("get_watchlist_requested", user_id=str(current_user.id))
    
    result = await db.execute(
        select(Watchlist, Stock)
        .join(Stock, Watchlist.stock_id == Stock.id)
        .where(Watchlist.user_id == current_user.id)
        .order_by(Watchlist.created_at.desc())
    )
    
    watchlist_items = []
    for watchlist_item, stock in result:
        watchlist_items.append(
            WatchlistResponse(
                id=watchlist_item.id,
                symbol=stock.symbol,
                company_name=stock.company_name,
                current_price=stock.current_price,
                alert_threshold_percent=watchlist_item.alert_threshold_percent,
                target_buy_price=watchlist_item.target_buy_price,
                target_sell_price=watchlist_item.target_sell_price,
                notes=watchlist_item.notes,
                created_at=watchlist_item.created_at
            )
        )
    
    logger.info("watchlist_retrieved", user_id=str(current_user.id), items_count=len(watchlist_items))
    return watchlist_items


# =============================================================================
# Route: Add to Watchlist
# =============================================================================
@router.post(
    "/",
    response_model=WatchlistResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add stock to watchlist",
    description="Add a stock to monitor for buy/sell opportunities"
)
async def add_to_watchlist(
    request: WatchlistAddRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> WatchlistResponse:
    """
    Add a stock to user's watchlist.
    
    AI agents will continuously monitor this stock and send alerts.
    """
    logger.info(
        "add_to_watchlist_requested",
        user_id=str(current_user.id),
        symbol=request.symbol
    )
    
    # Check if already in watchlist
    result = await db.execute(
        select(Watchlist)
        .join(Stock, Watchlist.stock_id == Stock.id)
        .where(
            Watchlist.user_id == current_user.id,
            Stock.symbol == request.symbol,
            Stock.market == request.market
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock already in watchlist"
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
        # Fetch stock data
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
                previous_close=stock_data.get('previous_close')
            )
            db.add(stock)
            await db.flush()
            
        except Exception as e:
            logger.error("failed_to_fetch_stock_data", symbol=request.symbol, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid stock symbol or market"
            )
    
    # Create watchlist entry
    watchlist_item = Watchlist(
        user_id=current_user.id,
        stock_id=stock.id,
        alert_threshold_percent=request.alert_threshold_percent,
        target_buy_price=request.target_buy_price,
        target_sell_price=request.target_sell_price,
        notes=request.notes
    )
    
    db.add(watchlist_item)
    await db.commit()
    await db.refresh(watchlist_item)
    
    logger.info(
        "stock_added_to_watchlist",
        user_id=str(current_user.id),
        symbol=request.symbol
    )
    
    return WatchlistResponse(
        id=watchlist_item.id,
        symbol=stock.symbol,
        company_name=stock.company_name,
        current_price=stock.current_price,
        alert_threshold_percent=watchlist_item.alert_threshold_percent,
        target_buy_price=watchlist_item.target_buy_price,
        target_sell_price=watchlist_item.target_sell_price,
        notes=watchlist_item.notes,
        created_at=watchlist_item.created_at
    )


# =============================================================================
# Route: Remove from Watchlist
# =============================================================================
@router.delete(
    "/{watchlist_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove stock from watchlist",
    description="Stop monitoring a stock"
)
async def remove_from_watchlist(
    watchlist_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove a stock from watchlist.
    """
    logger.info(
        "remove_from_watchlist_requested",
        user_id=str(current_user.id),
        watchlist_id=watchlist_id
    )
    
    result = await db.execute(
        select(Watchlist).where(
            Watchlist.id == watchlist_id,
            Watchlist.user_id == current_user.id
        )
    )
    watchlist_item = result.scalar_one_or_none()
    
    if not watchlist_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist item not found"
        )
    
    await db.delete(watchlist_item)
    await db.commit()
    
    logger.info(
        "stock_removed_from_watchlist",
        user_id=str(current_user.id),
        watchlist_id=watchlist_id
    )
    
    return None
