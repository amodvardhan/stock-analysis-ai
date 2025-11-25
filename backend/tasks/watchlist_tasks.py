"""
=============================================================================
AI Hub - Watchlist Monitoring Tasks
=============================================================================
Background tasks for monitoring user watchlists and generating alerts.

These tasks run periodically (every 15 minutes by default) to:
1. Check all watchlisted stocks for price changes
2. Generate buy/sell signals if thresholds are met
3. Send notifications to users
=============================================================================
"""

from celery import shared_task
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import structlog
from datetime import datetime

from core.database import AsyncSessionLocal
from db.models import Watchlist, Stock, User, TradingSignal, Notification, NotificationType, NotificationStatus
from agents.tools import get_stock_price
from tasks.notification_tasks import send_email

logger = structlog.get_logger()


@shared_task(name="tasks.watchlist_tasks.monitor_all_watchlists")
def monitor_all_watchlists():
    """
    Main task that monitors all watchlists.
    
    This is called by Celery Beat every X minutes (configured in settings).
    It runs asynchronously to check all stocks in all users' watchlists.
    """
    logger.info("watchlist_monitoring_started")
    
    # Create a new event loop for this task to avoid conflicts with Celery's prefork workers
    # This ensures each task has its own isolated event loop
    loop = None
    old_loop = None
    try:
        # Get the current loop (if any) and store it
        try:
            old_loop = asyncio.get_event_loop()
        except RuntimeError:
            # No event loop exists, which is fine
            pass
        
        # Create and set a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the async function
        loop.run_until_complete(_monitor_watchlists_async())
        
        logger.info("watchlist_monitoring_completed")
        return {"status": "completed", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error("watchlist_monitoring_failed", error=str(e))
        raise
    finally:
        # Clean up: ensure all async operations are complete before closing the loop
        if loop:
            try:
                # Give any pending operations a chance to complete
                pending = [t for t in asyncio.all_tasks(loop) if not t.done()]
                if pending:
                    # Wait a short time for tasks to complete
                    loop.run_until_complete(
                        asyncio.wait(pending, timeout=1.0, return_when=asyncio.ALL_COMPLETED)
                    )
                    # Cancel any remaining tasks
                    for task in pending:
                        if not task.done():
                            task.cancel()
                    # Wait for cancellation
                    if pending:
                        loop.run_until_complete(
                            asyncio.gather(*pending, return_exceptions=True)
                        )
            except Exception as cleanup_error:
                logger.warning("event_loop_cleanup_warning", error=str(cleanup_error))
            finally:
                # Close the loop and reset
                try:
                    loop.close()
                except Exception:
                    pass
                asyncio.set_event_loop(None)
                
                # Restore the old loop if it existed (though it shouldn't in Celery workers)
                if old_loop and not old_loop.is_closed():
                    try:
                        asyncio.set_event_loop(old_loop)
                    except Exception:
                        pass


async def _monitor_watchlists_async():
    """
    Async implementation of watchlist monitoring.
    
    Steps:
    1. Fetch all active watchlist items
    2. Group by stock to avoid duplicate API calls
    3. Check each stock's current price
    4. Generate alerts if thresholds are met
    5. Create notifications for users
    """
    db = None
    try:
        # Create a fresh session for this task
        db = AsyncSessionLocal()
        
        # Fetch all watchlist items with user and stock details
        result = await db.execute(
            select(Watchlist, Stock, User)
            .join(Stock, Watchlist.stock_id == Stock.id)
            .join(User, Watchlist.user_id == User.id)
            .where(User.is_active == True)
        )
        
        watchlist_items = result.all()
        logger.info("watchlist_items_fetched", count=len(watchlist_items))
        
        # Group by stock to minimize API calls
        stocks_to_check = {}
        for watchlist_item, stock, user in watchlist_items:
            stock_key = f"{stock.symbol}_{stock.market}"
            if stock_key not in stocks_to_check:
                stocks_to_check[stock_key] = {
                    "stock": stock,
                    "watchers": []
                }
            stocks_to_check[stock_key]["watchers"].append((watchlist_item, user))
        
        # Check each unique stock
        for stock_key, data in stocks_to_check.items():
            await _check_stock_and_alert(db, data["stock"], data["watchers"])
        
        await db.commit()
        
    except Exception as e:
        logger.error("watchlist_monitoring_failed", error=str(e))
        if db:
            await db.rollback()
        raise
    finally:
        # Ensure session is properly closed
        if db:
            await db.close()


async def _check_stock_and_alert(
    db: AsyncSession,
    stock: Stock,
    watchers: list
):
    """
    Check a single stock and generate alerts for all watchers.
    
    Args:
        db: Database session
        stock: Stock object
        watchers: List of (watchlist_item, user) tuples
    """
    try:
        # Fetch current stock price
        price_data = await get_stock_price(
            symbol=stock.symbol,
            market=stock.market.value,
            period="1d"
        )
        
        if "error" in price_data:
            logger.warning("stock_price_fetch_failed", symbol=stock.symbol, error=price_data["error"])
            return
        
        current_price = price_data.get("current_price")
        previous_close = stock.current_price or price_data.get("previous_close")
        
        if not current_price or not previous_close:
            return
        
        # Calculate price change percentage
        price_change_percent = ((current_price - previous_close) / previous_close) * 100
        
        # Update stock record
        stock.current_price = current_price
        stock.previous_close = previous_close
        stock.last_data_refresh = datetime.utcnow()
        
        logger.info(
            "stock_checked",
            symbol=stock.symbol,
            current_price=current_price,
            change_percent=round(price_change_percent, 2)
        )
        
        # Check each watcher's alert conditions
        for watchlist_item, user in watchers:
            should_alert = False
            alert_reason = ""
            
            # Check price change threshold
            if abs(price_change_percent) >= watchlist_item.alert_threshold_percent:
                should_alert = True
                direction = "increased" if price_change_percent > 0 else "decreased"
                alert_reason = f"Price {direction} by {abs(price_change_percent):.2f}%"
            
            # Check target buy price
            elif watchlist_item.target_buy_price and current_price <= watchlist_item.target_buy_price:
                should_alert = True
                alert_reason = f"Price reached your buy target of ₹{watchlist_item.target_buy_price}"
            
            # Check target sell price
            elif watchlist_item.target_sell_price and current_price >= watchlist_item.target_sell_price:
                should_alert = True
                alert_reason = f"Price reached your sell target of ₹{watchlist_item.target_sell_price}"
            
            # Send alert if conditions met
            if should_alert:
                await _send_watchlist_alert(
                    db=db,
                    user=user,
                    stock=stock,
                    current_price=current_price,
                    price_change_percent=price_change_percent,
                    reason=alert_reason
                )
        
    except Exception as e:
        logger.error("stock_check_failed", symbol=stock.symbol, error=str(e))


async def _send_watchlist_alert(
    db: AsyncSession,
    user: User,
    stock: Stock,
    current_price: float,
    price_change_percent: float,
    reason: str
):
    """
    Send alert notification to user about watchlist stock.
    
    Args:
        db: Database session
        user: User object
        stock: Stock object
        current_price: Current stock price
        price_change_percent: Price change percentage
        reason: Alert reason
    """
    try:
        # Create notification record
        title = f"Alert: {stock.symbol} - {reason}"
        message = f"""
Watchlist Alert for {stock.company_name} ({stock.symbol})

{reason}

Current Price: ₹{current_price:.2f}
Change: {price_change_percent:+.2f}%

Consider analyzing this stock for potential action.
        """.strip()
        
        # Create in-app notification
        notification = Notification(
            user_id=user.id,
            notification_type=NotificationType.IN_APP,
            title=title,
            message=message,
            status=NotificationStatus.SENT,
            is_read=False
        )
        db.add(notification)
        
        # Send email if user has email notifications enabled
        if user.email_notifications:
            # Note: send_email expects user_id, not user_email
            # We'll need to get user_id or update the function signature
            send_email.delay(
                user_id=user.id,
                subject=title,
                body=message
            )
        
        logger.info(
            "watchlist_alert_sent",
            user_id=str(user.id),
            symbol=stock.symbol,
            reason=reason
        )
        
    except Exception as e:
        logger.error("alert_send_failed", user_id=str(user.id), symbol=stock.symbol, error=str(e))
