"""
=============================================================================
Market Overview Service
=============================================================================
Service layer for market overview functionality.
=============================================================================
"""

from typing import Dict, Any
import structlog
from datetime import datetime

from agents.market_overview_agent import MarketOverviewAgent
from core.redis_client import cache

logger = structlog.get_logger()


class MarketOverviewService:
    """Service for market overview operations."""
    
    @staticmethod
    async def get_market_overview(
        market: str = "india_nse",
        include_sectors: bool = True,
        include_indices: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive market overview.
        
        Args:
            market: Market identifier
            include_sectors: Include sector analysis
            include_indices: Include index performance
        
        Returns:
            Market overview data
        """
        cache_key = f"market_overview:{market}:{include_sectors}:{include_indices}"
        
        # Check cache
        cached = cache.get(cache_key)
        if cached:
            logger.info("market_overview_cache_hit", market=market)
            return cached
        
        try:
            agent = MarketOverviewAgent()
            result = await agent.analyze(
                market=market,
                include_sectors=include_sectors,
                include_indices=include_indices
            )
            
            # Cache for 5 minutes
            cache.set(cache_key, result, ttl=300)
            
            return result
            
        except Exception as e:
            logger.error("market_overview_service_error", market=market, error=str(e))
            return {
                "error": str(e),
                "market": market
            }

