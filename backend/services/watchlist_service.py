from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from db.models import Watchlist, Stock, MarketType

logger = structlog.get_logger()


class WatchlistService:
    @staticmethod
    async def get_user_watchlist(
        db: AsyncSession,
        user_id: str,
    ) -> List[Dict[str, Any]]:
        # Convert string to UUID if needed
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        result = await db.execute(
            select(Watchlist, Stock)
            .join(Stock, Watchlist.stock_id == Stock.id)
            .where(Watchlist.user_id == user_uuid)
            .order_by(Watchlist.created_at.desc())
        )
        items: list[dict] = []
        for wl, stock in result.all():
            items.append(
                {
                    "id": wl.id,
                    "stock": {
                        "id": stock.id,
                        "symbol": stock.symbol,
                        "company_name": stock.company_name,
                        "market": stock.market.value,
                        "sector": stock.sector,
                        "industry": stock.industry,
                        "current_price": stock.current_price,
                    },
                    "alert_on_price_change": wl.alert_on_price_change,
                    "alert_threshold_percent": wl.alert_threshold_percent,
                    "alert_on_ai_signal": wl.alert_on_ai_signal,
                    "target_buy_price": wl.target_buy_price,
                    "target_sell_price": wl.target_sell_price,
                    "notes": wl.notes,
                    "created_at": wl.created_at,
                    "updated_at": wl.updated_at,
                }
            )
        return items

    @staticmethod
    async def add_to_watchlist(
        db: AsyncSession,
        user_id: str,
        symbol: str,
        market: str,
        alert_on_price_change: bool,
        alert_threshold_percent: float,
        alert_on_ai_signal: bool,
        target_buy_price: Optional[float],
        target_sell_price: Optional[float],
        notes: Optional[str],
    ) -> Watchlist:
        # Convert string to UUID if needed
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        # Get or create stock
        result = await db.execute(
            select(Stock).where(
                and_(
                    Stock.symbol == symbol.upper(),
                    Stock.market == MarketType(market),
                )
            )
        )
        stock = result.scalar_one_or_none()
        if not stock:
            stock = Stock(
                symbol=symbol.upper(),
                market=MarketType(market),
                company_name=symbol.upper(),
            )
            db.add(stock)
            await db.flush()
            await db.refresh(stock)

        # Check existing watchlist entry (unique per user+stock)
        result = await db.execute(
            select(Watchlist).where(
                and_(Watchlist.user_id == user_uuid, Watchlist.stock_id == stock.id)
            )
        )
        wl = result.scalar_one_or_none()
        if wl:
            # Update existing
            wl.alert_on_price_change = alert_on_price_change
            wl.alert_threshold_percent = alert_threshold_percent
            wl.alert_on_ai_signal = alert_on_ai_signal
            wl.target_buy_price = target_buy_price
            wl.target_sell_price = target_sell_price
            wl.notes = notes
            wl.updated_at = datetime.utcnow()
        else:
            # Create new
            wl = Watchlist(
                user_id=user_uuid,
                stock_id=stock.id,
                alert_on_price_change=alert_on_price_change,
                alert_threshold_percent=alert_threshold_percent,
                alert_on_ai_signal=alert_on_ai_signal,
                target_buy_price=target_buy_price,
                target_sell_price=target_sell_price,
                notes=notes,
            )
            db.add(wl)

        await db.commit()
        await db.refresh(wl)
        logger.info(
            "watchlist_item_saved",
            user_id=user_id,
            stock_id=stock.id,
            watchlist_id=wl.id,
        )
        return wl

    @staticmethod
    async def remove_from_watchlist(
        db: AsyncSession,
        user_id: str,
        watchlist_id: int,
    ):
        # Convert string to UUID if needed
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        result = await db.execute(
            select(Watchlist).where(
                and_(
                    Watchlist.id == watchlist_id,
                    Watchlist.user_id == user_uuid,
                )
            )
        )
        wl = result.scalar_one_or_none()
        if not wl:
            return False
        await db.delete(wl)
        await db.commit()
        logger.info(
            "watchlist_item_deleted",
            user_id=user_id,
            watchlist_id=watchlist_id,
        )
        return True
