"""
=============================================================================
Order Management Service
=============================================================================
Handles trading order creation, execution, and management.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import structlog

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from db.models import Order, OrderType, OrderStatus, TransactionType, Stock, User
from services.kyc_service import KYCService

logger = structlog.get_logger()


class OrderService:
    """Service for order management."""
    
    @staticmethod
    async def create_order(
        db: AsyncSession,
        user_id: str,
        order_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new trading order.
        
        Args:
            db: Database session
            user_id: User ID
            order_data: Order details
        
        Returns:
            Created order
        """
        try:
            logger.info("order_creation_started", user_id=user_id, order_type=order_data.get("order_type"))
            
            # Validate user
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            if not user:
                return {"error": "User not found", "user_id": user_id}
            
            # Perform AML check for high-value orders
            order_value = order_data.get("quantity", 0) * order_data.get("limit_price", 0)
            if order_value > 10000:
                aml_result = await KYCService.perform_aml_check(db, user_id, order_value)
                if aml_result.get("action") == "block":
                    return {
                        "error": "Order blocked due to AML compliance",
                        "aml_result": aml_result
                    }
            
            # Validate stock
            stock_result = await db.execute(
                select(Stock).where(
                    Stock.symbol == order_data.get("symbol"),
                    Stock.market == order_data.get("market")
                )
            )
            stock = stock_result.scalar_one_or_none()
            if not stock:
                return {"error": "Stock not found", "symbol": order_data.get("symbol")}
            
            # Create order
            order = Order(
                user_id=user_id,
                stock_id=stock.id,
                order_type=OrderType(order_data.get("order_type", "market")),
                side=TransactionType(order_data.get("side", "BUY")),
                quantity=order_data.get("quantity"),
                limit_price=order_data.get("limit_price"),
                stop_price=order_data.get("stop_price"),
                status=OrderStatus.PENDING,
                expires_at=order_data.get("expires_at"),
                notes=order_data.get("notes")
            )
            
            db.add(order)
            await db.commit()
            await db.refresh(order)
            
            logger.info("order_created", order_id=order.id, user_id=user_id)
            
            # Submit order for execution
            if order.order_type == OrderType.MARKET:
                await OrderService._execute_market_order(db, order)
            elif order.order_type == OrderType.LIMIT:
                await OrderService._queue_limit_order(db, order)
            elif order.order_type == OrderType.STOP_LOSS:
                await OrderService._queue_stop_order(db, order)
            
            return {
                "id": order.id,
                "order_type": order.order_type.value,
                "side": order.side.value,
                "quantity": order.quantity,
                "status": order.status.value,
                "created_at": order.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error("order_creation_error", user_id=user_id, error=str(e))
            await db.rollback()
            return {"error": str(e), "user_id": user_id}
    
    @staticmethod
    async def _execute_market_order(db: AsyncSession, order: Order):
        """Execute a market order immediately."""
        try:
            # In production, would integrate with broker API
            # For now, simulate execution at current market price
            
            stock_result = await db.execute(select(Stock).where(Stock.id == order.stock_id))
            stock = stock_result.scalar_one()
            
            execution_price = stock.current_price or 0
            
            if execution_price > 0:
                order.status = OrderStatus.FILLED
                order.filled_quantity = order.quantity
                order.average_fill_price = execution_price
                order.total_filled_value = order.quantity * execution_price
                order.filled_at = datetime.utcnow()
                order.submitted_at = datetime.utcnow()
                
                # Calculate fees (simplified)
                order.commission = order.total_filled_value * Decimal("0.001")  # 0.1%
                order.fees = order.commission
                
                await db.commit()
                
                logger.info("market_order_executed", order_id=order.id, price=execution_price)
            else:
                order.status = OrderStatus.REJECTED
                await db.commit()
                
        except Exception as e:
            logger.error("market_order_execution_error", order_id=order.id, error=str(e))
            order.status = OrderStatus.REJECTED
            await db.commit()
    
    @staticmethod
    async def _queue_limit_order(db: AsyncSession, order: Order):
        """Queue a limit order for execution when price is reached."""
        order.status = OrderStatus.SUBMITTED
        order.submitted_at = datetime.utcnow()
        await db.commit()
        
        logger.info("limit_order_queued", order_id=order.id)
        # In production, would add to order matching engine
    
    @staticmethod
    async def _queue_stop_order(db: AsyncSession, order: Order):
        """Queue a stop-loss order for execution when stop price is reached."""
        order.status = OrderStatus.SUBMITTED
        order.submitted_at = datetime.utcnow()
        await db.commit()
        
        logger.info("stop_order_queued", order_id=order.id)
        # In production, would monitor price and trigger when stop price hit
    
    @staticmethod
    async def cancel_order(
        db: AsyncSession,
        user_id: str,
        order_id: int
    ) -> Dict[str, Any]:
        """Cancel an order."""
        try:
            result = await db.execute(
                select(Order).where(
                    Order.id == order_id,
                    Order.user_id == user_id
                )
            )
            order = result.scalar_one_or_none()
            
            if not order:
                return {"error": "Order not found", "order_id": order_id}
            
            if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]:
                return {
                    "error": f"Cannot cancel order with status: {order.status.value}",
                    "order_id": order_id
                }
            
            order.status = OrderStatus.CANCELLED
            order.cancelled_at = datetime.utcnow()
            await db.commit()
            
            logger.info("order_cancelled", order_id=order_id, user_id=user_id)
            
            return {
                "id": order.id,
                "status": order.status.value,
                "cancelled_at": order.cancelled_at.isoformat()
            }
            
        except Exception as e:
            logger.error("order_cancellation_error", order_id=order_id, error=str(e))
            await db.rollback()
            return {"error": str(e), "order_id": order_id}
    
    @staticmethod
    async def get_orders(
        db: AsyncSession,
        user_id: str,
        status: Optional[OrderStatus] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get user's orders."""
        try:
            query = select(Order).where(Order.user_id == user_id)
            
            if status:
                query = query.where(Order.status == status)
            
            query = query.order_by(Order.created_at.desc()).limit(limit)
            
            result = await db.execute(query)
            orders = result.scalars().all()
            
            return [
                {
                    "id": order.id,
                    "symbol": order.stock.symbol,
                    "order_type": order.order_type.value,
                    "side": order.side.value,
                    "quantity": order.quantity,
                    "filled_quantity": order.filled_quantity,
                    "limit_price": float(order.limit_price) if order.limit_price else None,
                    "status": order.status.value,
                    "created_at": order.created_at.isoformat(),
                    "filled_at": order.filled_at.isoformat() if order.filled_at else None
                }
                for order in orders
            ]
            
        except Exception as e:
            logger.error("get_orders_error", user_id=user_id, error=str(e))
            return []

