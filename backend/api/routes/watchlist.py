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
from typing import List
import structlog

from core.database import get_db
from db.models import User, MarketType
from schemas.stock_schemas import (
    WatchlistAddRequest,
    WatchlistResponse,
    WatchlistListResponse,
    WatchlistStockResponse
)
from api.routes.auth import get_current_user
from services.watchlist_service import WatchlistService

logger = structlog.get_logger()
router = APIRouter()


# =============================================================================
# Route: Get Watchlist
# =============================================================================
@router.get(
    "/",
    response_model=WatchlistListResponse,
    summary="Get user's watchlist",
    description="Retrieve all stocks in user's watchlist"
)
async def get_watchlist(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> WatchlistListResponse:
    """
    Get all stocks in user's watchlist.
    
    These are stocks the user wants to monitor for buy/sell opportunities.
    """
    logger.info("get_watchlist_requested", user_id=str(current_user.id))
    
    try:
        items_data = await WatchlistService.get_user_watchlist(db, str(current_user.id))
        
        # Convert to response format
        items = []
        for item_data in items_data:
            items.append(
                WatchlistResponse(
                    id=item_data["id"],
                    stock=WatchlistStockResponse(
                        id=item_data["stock"]["id"],
                        symbol=item_data["stock"]["symbol"],
                        company_name=item_data["stock"]["company_name"],
                        market=item_data["stock"]["market"],
                        sector=item_data["stock"].get("sector"),
                        industry=item_data["stock"].get("industry"),
                        current_price=item_data["stock"].get("current_price"),
                    ),
                    alert_on_price_change=item_data["alert_on_price_change"],
                    alert_threshold_percent=item_data["alert_threshold_percent"],
                    alert_on_ai_signal=item_data["alert_on_ai_signal"],
                    target_buy_price=item_data["target_buy_price"],
                    target_sell_price=item_data["target_sell_price"],
                    notes=item_data["notes"],
                    created_at=item_data["created_at"],
                    updated_at=item_data["updated_at"],
                )
            )
        
        logger.info(
            "watchlist_retrieved",
            user_id=str(current_user.id),
            items_count=len(items)
        )
        
        return WatchlistListResponse(items=items, count=len(items))
        
    except Exception as e:
        logger.error("get_watchlist_failed", user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch watchlist: {str(e)}"
        )


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
    If the stock already exists, it will be updated.
    """
    logger.info(
        "add_to_watchlist_requested",
        user_id=str(current_user.id),
        symbol=request.symbol,
        market=request.market
    )
    
    try:
        # Validate market type
        try:
            market_type = MarketType(request.market)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid market: {request.market}"
            )
        
        # Add or update watchlist item
        watchlist_item = await WatchlistService.add_to_watchlist(
            db=db,
            user_id=str(current_user.id),
            symbol=request.symbol.upper(),
            market=request.market,
            alert_on_price_change=request.alert_on_price_change,
            alert_threshold_percent=request.alert_threshold_percent,
            alert_on_ai_signal=request.alert_on_ai_signal,
            target_buy_price=request.target_buy_price,
            target_sell_price=request.target_sell_price,
            notes=request.notes,
        )
        
        # Fetch the complete watchlist item with stock data
        items_data = await WatchlistService.get_user_watchlist(db, str(current_user.id))
        item_data = next((item for item in items_data if item["id"] == watchlist_item.id), None)
        
        if not item_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created watchlist item"
            )
        
        logger.info(
            "stock_added_to_watchlist",
            user_id=str(current_user.id),
            symbol=request.symbol,
            watchlist_id=watchlist_item.id
        )
        
        return WatchlistResponse(
            id=item_data["id"],
            stock=WatchlistStockResponse(
                id=item_data["stock"]["id"],
                symbol=item_data["stock"]["symbol"],
                company_name=item_data["stock"]["company_name"],
                market=item_data["stock"]["market"],
                sector=item_data["stock"].get("sector"),
                industry=item_data["stock"].get("industry"),
                current_price=item_data["stock"].get("current_price"),
            ),
            alert_on_price_change=item_data["alert_on_price_change"],
            alert_threshold_percent=item_data["alert_threshold_percent"],
            alert_on_ai_signal=item_data["alert_on_ai_signal"],
            target_buy_price=item_data["target_buy_price"],
            target_sell_price=item_data["target_sell_price"],
            notes=item_data["notes"],
            created_at=item_data["created_at"],
            updated_at=item_data["updated_at"],
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "add_to_watchlist_failed",
            user_id=str(current_user.id),
            symbol=request.symbol,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add stock to watchlist: {str(e)}"
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
    
    try:
        success = await WatchlistService.remove_from_watchlist(
            db=db,
            user_id=str(current_user.id),
            watchlist_id=watchlist_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Watchlist item not found"
            )
        
        logger.info(
            "stock_removed_from_watchlist",
            user_id=str(current_user.id),
            watchlist_id=watchlist_id
        )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "remove_from_watchlist_failed",
            user_id=str(current_user.id),
            watchlist_id=watchlist_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove from watchlist: {str(e)}"
        )

