"""
=============================================================================
Order Management API Routes
=============================================================================
Endpoints for creating, managing, and tracking trading orders.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import structlog

from core.database import get_db
from db.models import User, Order, OrderStatus, OrderType, TransactionType
from api.routes.auth import get_current_user
from services.order_service import OrderService

logger = structlog.get_logger()
router = APIRouter()


class OrderCreateRequest(BaseModel):
    symbol: str
    market: str
    order_type: str  # market, limit, stop_loss, stop_limit
    side: str  # BUY or SELL
    quantity: int
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    expires_at: Optional[str] = None
    notes: Optional[str] = None


class OrderResponse(BaseModel):
    id: int
    symbol: str
    order_type: str
    side: str
    quantity: int
    filled_quantity: int
    limit_price: Optional[float]
    status: str
    created_at: str
    filled_at: Optional[str] = None


@router.post("/", response_model=OrderResponse)
async def create_order(
    request: OrderCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> OrderResponse:
    """Create a new trading order."""
    try:
        logger.info(
            "order_creation_requested",
            user_id=str(current_user.id),
            symbol=request.symbol,
            order_type=request.order_type
        )
        
        order_data = {
            "symbol": request.symbol,
            "market": request.market,
            "order_type": request.order_type,
            "side": request.side,
            "quantity": request.quantity,
            "limit_price": request.limit_price,
            "stop_price": request.stop_price,
            "expires_at": request.expires_at,
            "notes": request.notes
        }
        
        result = await OrderService.create_order(
            db=db,
            user_id=str(current_user.id),
            order_data=order_data
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        # Fetch the created order
        from sqlalchemy import select
        order_result = await db.execute(
            select(Order).where(Order.id == result["id"])
        )
        order = order_result.scalar_one()
        
        return OrderResponse(
            id=order.id,
            symbol=order.stock.symbol,
            order_type=order.order_type.value,
            side=order.side.value,
            quantity=order.quantity,
            filled_quantity=order.filled_quantity,
            limit_price=float(order.limit_price) if order.limit_price else None,
            status=order.status.value,
            created_at=order.created_at.isoformat(),
            filled_at=order.filled_at.isoformat() if order.filled_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("order_creation_error", user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Order creation failed: {str(e)}"
        )


@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[OrderResponse]:
    """Get user's orders."""
    try:
        order_status = OrderStatus(status_filter) if status_filter else None
        
        orders = await OrderService.get_orders(
            db=db,
            user_id=str(current_user.id),
            status=order_status,
            limit=100
        )
        
        return [
            OrderResponse(**order) for order in orders
        ]
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {status_filter}"
        )
    except Exception as e:
        logger.error("get_orders_error", user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch orders: {str(e)}"
        )


@router.delete("/{order_id}")
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Cancel an order."""
    try:
        result = await OrderService.cancel_order(
            db=db,
            user_id=str(current_user.id),
            order_id=order_id
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("order_cancellation_error", user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Order cancellation failed: {str(e)}"
        )

