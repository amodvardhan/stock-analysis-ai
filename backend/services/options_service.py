"""
=============================================================================
Options Service
=============================================================================
Service layer for options chain functionality.
=============================================================================
"""

from typing import Dict, Any, Optional
import structlog

from agents.options_agent import OptionsAgent
from core.redis_client import cache

logger = structlog.get_logger()


class OptionsService:
    """Service for options operations."""
    
    @staticmethod
    async def get_options_analysis(
        symbol: str,
        market: str = "india_nse",
        expiration_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get options chain analysis.
        
        Args:
            symbol: Stock symbol
            market: Market identifier
            expiration_date: Expiration date (optional)
        
        Returns:
            Options analysis data
        """
        cache_key = f"options_analysis:{symbol}:{market}:{expiration_date or 'latest'}"
        
        # Check cache (5 minutes TTL)
        cached = cache.get(cache_key)
        if cached:
            logger.info("options_analysis_cache_hit", symbol=symbol)
            return cached
        
        try:
            agent = OptionsAgent()
            result = await agent.analyze(
                symbol=symbol,
                market=market,
                expiration_date=expiration_date
            )
            
            # Cache for 5 minutes
            cache.set(cache_key, result, ttl=300)
            
            return result
            
        except Exception as e:
            logger.error("options_service_error", symbol=symbol, error=str(e))
            return {
                "error": str(e),
                "symbol": symbol
            }

