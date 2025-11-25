"""
=============================================================================
AI Hub - Portfolio Service
=============================================================================
Business logic for portfolio management, P&L calculations, and performance.
=============================================================================
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from decimal import Decimal
import structlog
import asyncio

from db.models import (
    Portfolio,
    PortfolioHolding,
    PortfolioTransaction,
    Stock,
    TransactionType,
    User
)
from agents.tools.stock_price_tool import get_stock_price

logger = structlog.get_logger()


class PortfolioService:
    """Service for managing portfolios and calculating performance metrics."""
    
    @staticmethod
    async def get_or_create_default_portfolio(
        db: AsyncSession,
        user_id: str
    ) -> Portfolio:
        """
        Get user's default portfolio or create if doesn't exist.
        
        Args:
            db: Database session
            user_id: User UUID
        
        Returns:
            Portfolio instance
        """
        result = await db.execute(
            select(Portfolio)
            .where(Portfolio.user_id == user_id)
            .order_by(Portfolio.created_at)
            .limit(1)
        )
        portfolio = result.scalar_one_or_none()
        
        if not portfolio:
            portfolio = Portfolio(
                user_id=user_id,
                name="My Portfolio",
                description="Default portfolio"
            )
            db.add(portfolio)
            await db.commit()
            await db.refresh(portfolio)
            logger.info("default_portfolio_created", user_id=user_id, portfolio_id=portfolio.id)
        
        return portfolio
    
    @staticmethod
    async def create_portfolio(
        db: AsyncSession,
        user_id: str,
        name: str,
        description: Optional[str] = None
    ) -> Portfolio:
        """Create a new portfolio."""
        portfolio = Portfolio(
            user_id=user_id,
            name=name,
            description=description
        )
        db.add(portfolio)
        await db.commit()
        await db.refresh(portfolio)
        
        logger.info("portfolio_created", portfolio_id=portfolio.id, user_id=user_id)
        return portfolio
    
    @staticmethod
    async def get_user_portfolios(
        db: AsyncSession,
        user_id: str
    ) -> List[Portfolio]:
        """Get all portfolios for a user."""
        result = await db.execute(
            select(Portfolio)
            .where(Portfolio.user_id == user_id)
            .order_by(Portfolio.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def add_holding(
        db: AsyncSession,
        portfolio_id: int,
        stock_id: int,
        quantity: int,
        price_per_share: float,
        transaction_date: datetime,
        brokerage_fee: float = 0.0,
        tax: float = 0.0,
        notes: Optional[str] = None
    ) -> PortfolioHolding:
        """
        Add or update stock holding in portfolio.
        
        Creates a BUY transaction and updates holding.
        """
        # Check if holding exists
        result = await db.execute(
            select(PortfolioHolding).where(
                and_(
                    PortfolioHolding.portfolio_id == portfolio_id,
                    PortfolioHolding.stock_id == stock_id
                )
            )
        )
        holding = result.scalar_one_or_none()
        
        total_cost = (Decimal(str(quantity)) * Decimal(str(price_per_share))) + Decimal(str(brokerage_fee)) + Decimal(str(tax))
        
        if holding:
            # Update existing holding (calculate new average price)
            old_total_invested = holding.total_invested
            old_quantity = holding.quantity
            
            new_quantity = old_quantity + quantity
            new_total_invested = old_total_invested + total_cost
            new_average_price = new_total_invested / Decimal(str(new_quantity))
            
            holding.quantity = new_quantity
            holding.average_buy_price = float(new_average_price)
            holding.total_invested = float(new_total_invested)
            holding.last_updated = datetime.utcnow()
        else:
            # Create new holding
            holding = PortfolioHolding(
                portfolio_id=portfolio_id,
                stock_id=stock_id,
                quantity=quantity,
                average_buy_price=price_per_share,
                total_invested=float(total_cost),
                first_buy_date=transaction_date
            )
            db.add(holding)
            await db.flush()  # Get holding ID
        
        # Record transaction
        transaction = PortfolioTransaction(
            portfolio_id=portfolio_id,
            holding_id=holding.id,
            stock_id=stock_id,
            transaction_type=TransactionType.BUY,
            quantity=quantity,
            price_per_share=price_per_share,
            total_amount=float(total_cost),
            brokerage_fee=brokerage_fee,
            tax=tax,
            transaction_date=transaction_date,
            notes=notes
        )
        db.add(transaction)
        
        await db.commit()
        await db.refresh(holding)
        
        # Update portfolio metrics
        await PortfolioService.update_portfolio_metrics(db, portfolio_id)
        
        logger.info(
            "holding_added",
            portfolio_id=portfolio_id,
            stock_id=stock_id,
            quantity=quantity,
            price=price_per_share
        )
        
        return holding
    
    @staticmethod
    async def get_portfolio_holdings(
        db: AsyncSession,
        portfolio_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get all holdings for a portfolio with stock details.
        
        Returns holdings with enriched stock information.
        """
        result = await db.execute(
            select(PortfolioHolding, Stock)
            .join(Stock, PortfolioHolding.stock_id == Stock.id)
            .where(PortfolioHolding.portfolio_id == portfolio_id)
            .order_by(PortfolioHolding.last_updated.desc())
        )
        
        holdings_data = []
        for holding, stock in result.all():
            holdings_data.append({
                "id": holding.id,
                "stock": {
                    "id": stock.id,
                    "symbol": stock.symbol,
                    "company_name": stock.company_name,
                    "market": stock.market.value,
                    "sector": stock.sector,
                    "industry": stock.industry
                },
                "quantity": holding.quantity,
                "average_buy_price": float(holding.average_buy_price),
                "total_invested": float(holding.total_invested),
                "current_price": float(holding.current_price) if holding.current_price else None,
                "current_value": float(holding.current_value) if holding.current_value else None,
                "unrealized_pl": float(holding.unrealized_pl) if holding.unrealized_pl else None,
                "unrealized_pl_percentage": float(holding.unrealized_pl_percentage) if holding.unrealized_pl_percentage else None,
                "realized_pl": float(holding.realized_pl),
                "first_buy_date": holding.first_buy_date.isoformat(),
                "last_updated": holding.last_updated.isoformat()
            })
        
        return holdings_data
    
    @staticmethod
    async def update_holding_price(db: AsyncSession, holding_id: int, force_update: bool = False):
        """
        Update current price and P&L for a holding.
        
        Args:
            db: Database session
            holding_id: Holding ID
            force_update: If False, only update if price is stale (>1 hour old)
        """
        result = await db.execute(
            select(PortfolioHolding).where(PortfolioHolding.id == holding_id)
        )
        holding = result.scalar_one()
        
        # Check if price is recent (less than 1 hour old)
        if not force_update and holding.last_updated:
            time_since_update = datetime.utcnow() - holding.last_updated
            if time_since_update < timedelta(hours=1) and holding.current_price:
                # Price is fresh, skip update
                logger.debug(
                    "holding_price_fresh_skipping_update",
                    holding_id=holding_id,
                    last_updated=holding.last_updated.isoformat()
                )
                return
        
        # Get stock
        result = await db.execute(
            select(Stock).where(Stock.id == holding.stock_id)
        )
        stock = result.scalar_one()
        
        # Fetch current price with timeout (10 seconds)
        try:
            price_data = await asyncio.wait_for(
                get_stock_price.ainvoke({
                    "symbol": stock.symbol,
                    "market": stock.market.value,
                    "period": "1d"
                }),
                timeout=10.0  # 10 second timeout
            )
            
            if "error" not in price_data and price_data.get("current_price"):
                current_price = Decimal(str(price_data["current_price"]))
                current_value = current_price * Decimal(str(holding.quantity))
                unrealized_pl = current_value - Decimal(str(holding.total_invested))
                unrealized_pl_percentage = float(
                    (unrealized_pl / Decimal(str(holding.total_invested)) * 100)
                    if holding.total_invested > 0 else 0
                )
                
                holding.current_price = float(current_price)
                holding.current_value = float(current_value)
                holding.unrealized_pl = float(unrealized_pl)
                holding.unrealized_pl_percentage = unrealized_pl_percentage
                holding.last_updated = datetime.utcnow()
                
                await db.commit()
                
                logger.info(
                    "holding_price_updated",
                    holding_id=holding_id,
                    current_price=float(current_price),
                    unrealized_pl=float(unrealized_pl)
                )
        except asyncio.TimeoutError:
            logger.warning(
                "holding_price_update_timeout",
                holding_id=holding_id,
                symbol=stock.symbol
            )
            # Use existing price if available
            if not holding.current_price and stock.current_price:
                holding.current_price = float(stock.current_price)
                holding.current_value = float(stock.current_price) * Decimal(str(holding.quantity))
                await db.commit()
        except Exception as e:
            logger.error("holding_price_update_failed", holding_id=holding_id, error=str(e))
            # Use existing price if available
            if not holding.current_price and stock.current_price:
                holding.current_price = float(stock.current_price)
                holding.current_value = float(stock.current_price) * Decimal(str(holding.quantity))
                await db.commit()
    
    @staticmethod
    async def update_portfolio_metrics(db: AsyncSession, portfolio_id: int, force_price_update: bool = False):
        """
        Update portfolio-level metrics (total invested, current value, P&L).
        
        Optimized to minimize API calls and database queries.
        
        Args:
            db: Database session
            portfolio_id: Portfolio ID
            force_price_update: If True, force price updates even if prices are fresh. 
                               If False, only update stale prices (>1 hour old).
        """
        # Get portfolio and holdings in optimized query
        portfolio_result = await db.execute(
            select(Portfolio).where(Portfolio.id == portfolio_id)
        )
        portfolio = portfolio_result.scalar_one()
        
        # Get holdings with stock info in a single query (optimized)
        holdings_result = await db.execute(
            select(PortfolioHolding, Stock)
            .join(Stock, PortfolioHolding.stock_id == Stock.id)
            .where(PortfolioHolding.portfolio_id == portfolio_id)
        )
        holdings_data = holdings_result.all()
        
        total_invested = Decimal("0")
        current_value = Decimal("0")
        
        # Only update prices if explicitly requested
        # Otherwise, use cached prices from holdings or stocks
        if force_price_update:
            # Update prices sequentially with timeout protection (each update has its own timeout)
            # Limit to max 5 seconds per holding to prevent long delays
            for holding, stock in holdings_data:
                try:
                    # Each update has a 5-second timeout (reduced from 10s for faster failure)
                    await asyncio.wait_for(
                        PortfolioService.update_holding_price(db, holding.id, force_update=True),
                        timeout=5.0
                    )
                except asyncio.TimeoutError:
                    logger.warning(
                        "holding_price_update_timeout_in_metrics",
                        holding_id=holding.id,
                        symbol=stock.symbol
                    )
                except Exception as e:
                    logger.warning(
                        "holding_price_update_error_in_metrics",
                        holding_id=holding.id,
                        error=str(e)
                    )
                await db.refresh(holding)
        
        # Calculate metrics from holdings (use cached prices if available)
        for holding, stock in holdings_data:
            total_invested += Decimal(str(holding.total_invested or 0))
            # Use current_value if available, otherwise calculate from current_price
            if holding.current_value:
                current_value += Decimal(str(holding.current_value))
            elif holding.current_price:
                current_value += Decimal(str(holding.current_price)) * Decimal(str(holding.quantity))
            elif stock.current_price:
                # Fallback to stock's current price if holding doesn't have one
                current_value += Decimal(str(stock.current_price)) * Decimal(str(holding.quantity))
        
        total_return = current_value - total_invested
        return_percentage = float(
            (total_return / total_invested * 100)
            if total_invested > 0 else 0
        )
        
        portfolio.total_invested = float(total_invested)
        portfolio.current_value = float(current_value)
        portfolio.total_return = float(total_return)
        portfolio.return_percentage = return_percentage
        portfolio.last_updated = datetime.utcnow()
        
        await db.commit()
        
        logger.info(
            "portfolio_metrics_updated",
            portfolio_id=portfolio_id,
            total_invested=float(total_invested),
            current_value=float(current_value),
            total_return=float(total_return),
            return_percentage=return_percentage
        )
    
    @staticmethod
    async def get_portfolio_summary(
        db: AsyncSession,
        portfolio_id: int,
        force_price_update: bool = False
    ) -> Dict[str, Any]:
        """
        Get complete portfolio summary with metrics and holdings.
        
        Optimized to minimize database queries and API calls.
        
        Args:
            db: Database session
            portfolio_id: Portfolio ID
            force_price_update: If True, force price updates. Default False uses cached prices.
        """
        # Only update metrics if explicitly requested or if portfolio is stale
        # Check if portfolio needs update (stale if >5 minutes old)
        portfolio_result = await db.execute(
            select(Portfolio).where(Portfolio.id == portfolio_id)
        )
        portfolio = portfolio_result.scalar_one()
        
        needs_update = force_price_update
        if not needs_update and portfolio.last_updated:
            time_since_update = datetime.utcnow() - portfolio.last_updated
            # Only update if portfolio metrics are stale (>5 minutes)
            needs_update = time_since_update > timedelta(minutes=5)
        
        if needs_update:
            # Update metrics (with smart caching - only update stale prices)
            await PortfolioService.update_portfolio_metrics(db, portfolio_id, force_price_update=force_price_update)
            # Refresh portfolio after update
            await db.refresh(portfolio)
        
        # Get holdings in a single optimized query
        holdings = await PortfolioService.get_portfolio_holdings(db, portfolio_id)
        
        # Calculate sector allocation
        sector_allocation = {}
        for holding in holdings:
            sector = holding["stock"]["sector"] or "Other"
            current_value = holding["current_value"] or 0
            sector_allocation[sector] = sector_allocation.get(sector, 0) + current_value
        
        return {
            "portfolio": {
                "id": portfolio.id,
                "name": portfolio.name,
                "description": portfolio.description,
                "total_invested": float(portfolio.total_invested),
                "current_value": float(portfolio.current_value),
                "total_return": float(portfolio.total_return),
                "return_percentage": float(portfolio.return_percentage),
                "last_updated": portfolio.last_updated.isoformat()
            },
            "holdings": holdings,
            "sector_allocation": sector_allocation,
            "holdings_count": len(holdings)
        }
    
    @staticmethod
    async def delete_holding(
        db: AsyncSession,
        holding_id: int
    ):
        """Delete a holding from portfolio."""
        result = await db.execute(
            select(PortfolioHolding).where(PortfolioHolding.id == holding_id)
        )
        holding = result.scalar_one_or_none()
        
        if holding:
            portfolio_id = holding.portfolio_id
            await db.delete(holding)
            await db.commit()
            
            # Update portfolio metrics
            await PortfolioService.update_portfolio_metrics(db, portfolio_id)
            
            logger.info("holding_deleted", holding_id=holding_id, portfolio_id=portfolio_id)
