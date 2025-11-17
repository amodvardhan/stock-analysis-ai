"""
=============================================================================
AI Hub - Stock Analysis Background Tasks
=============================================================================
Handles background processing for stock data updates and analysis.
=============================================================================
"""

from typing import List
from datetime import datetime, timedelta
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from core.celery_app import celery_app
from core.database import async_session_maker
from db.models import Stock, StockAnalysis
from agents.tools.stock_price_tool import get_stock_price

logger = structlog.get_logger()


@celery_app.task(name="tasks.stock_tasks.update_stock_price", bind=True, max_retries=3)
def update_stock_price(self, stock_id: int, symbol: str, market: str):
    """
    Update price data for a single stock.
    
    Args:
        stock_id: Database ID of the stock
        symbol: Stock ticker symbol
        market: Market identifier
    
    Returns:
        dict: Updated price information
    """
    try:
        logger.info("updating_stock_price", stock_id=stock_id, symbol=symbol)
        
        # Fetch latest price (this is async, need to handle properly)
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        price_data = loop.run_until_complete(
            get_stock_price.ainvoke({
                "symbol": symbol,
                "market": market,
                "period": "1d"
            })
        )
        
        if "error" in price_data:
            raise Exception(price_data["error"])
        
        # Update database
        async def update_db():
            async with async_session_maker() as session:
                result = await session.execute(
                    select(Stock).where(Stock.id == stock_id)
                )
                stock = result.scalar_one_or_none()
                
                if stock:
                    stock.current_price = price_data["current_price"]
                    stock.previous_close = price_data["previous_close"]
                    stock.last_data_refresh = datetime.utcnow()
                    await session.commit()
                    
                    logger.info(
                        "stock_price_updated",
                        stock_id=stock_id,
                        symbol=symbol,
                        price=price_data["current_price"]
                    )
        
        loop.run_until_complete(update_db())
        loop.close()
        
        return {
            "status": "success",
            "stock_id": stock_id,
            "symbol": symbol,
            "price": price_data["current_price"]
        }
        
    except Exception as e:
        logger.error("stock_price_update_failed", stock_id=stock_id, error=str(e))
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@celery_app.task(name="tasks.stock_tasks.update_all_stock_prices")
def update_all_stock_prices():
    """
    Update prices for all tracked stocks.
    
    This task runs periodically to keep stock data fresh.
    Queues individual update tasks for each stock.
    """
    try:
        logger.info("updating_all_stock_prices")
        
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def get_stocks():
            async with async_session_maker() as session:
                result = await session.execute(select(Stock))
                return result.scalars().all()
        
        stocks = loop.run_until_complete(get_stocks())
        loop.close()
        
        # Queue individual update tasks
        for stock in stocks:
            update_stock_price.delay(stock.id, stock.symbol, stock.market.value)
        
        logger.info("queued_stock_updates", count=len(stocks))
        
        return {"status": "success", "stocks_queued": len(stocks)}
        
    except Exception as e:
        logger.error("bulk_stock_update_failed", error=str(e))
        return {"status": "error", "error": str(e)}


@celery_app.task(name="tasks.stock_tasks.cleanup_old_analysis")
def cleanup_old_analysis():
    """
    Clean up analysis data older than 30 days.
    
    Runs daily to keep database size manageable.
    """
    try:
        logger.info("cleaning_old_analysis")
        
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def delete_old():
            async with async_session_maker() as session:
                cutoff_date = datetime.utcnow() - timedelta(days=30)
                result = await session.execute(
                    select(StockAnalysis).where(
                        StockAnalysis.analyzed_at < cutoff_date
                    )
                )
                old_analyses = result.scalars().all()
                
                for analysis in old_analyses:
                    await session.delete(analysis)
                
                await session.commit()
                return len(old_analyses)
        
        deleted_count = loop.run_until_complete(delete_old())
        loop.close()
        
        logger.info("old_analysis_cleaned", deleted_count=deleted_count)
        
        return {"status": "success", "deleted_count": deleted_count}
        
    except Exception as e:
        logger.error("cleanup_failed", error=str(e))
        return {"status": "error", "error": str(e)}
