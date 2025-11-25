"""
=============================================================================
Market Movers Service
=============================================================================
Service layer for market movers functionality.
=============================================================================
"""

from typing import Dict, Any
import structlog

from agents.market_movers_agent import MarketMoversAgent
from core.redis_client import cache

logger = structlog.get_logger()


class MarketMoversService:
    """Service for market movers operations."""
    
    @staticmethod
    async def get_market_movers(
        market: str = "india_nse",
        movers_type: str = "all",
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get market movers (gainers, losers, active stocks).
        
        Args:
            market: Market identifier
            movers_type: Type of movers (gainers, losers, active, all)
            limit: Maximum number of stocks
        
        Returns:
            Market movers data
        """
        cache_key = f"market_movers:{market}:{movers_type}:{limit}"
        
        # Check cache (3 minutes TTL)
        cached = cache.get(cache_key)
        if cached:
            logger.info("market_movers_cache_hit", market=market)
            return cached
        
        try:
            agent = MarketMoversAgent()
            result = await agent.analyze(
                market=market,
                movers_type=movers_type,
                limit=limit
            )
            
            # Cache for 3 minutes
            cache.set(cache_key, result, ttl=180)
            
            return result
            
        except Exception as e:
            logger.error("market_movers_service_error", market=market, error=str(e))
            return {
                "error": str(e),
                "market": market
            }

