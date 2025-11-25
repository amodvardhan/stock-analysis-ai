"""
=============================================================================
Corporate Actions Service
=============================================================================
Service layer for corporate actions functionality.
=============================================================================
"""

from typing import Dict, Any
import structlog

from agents.tools.corporate_actions_tool import get_corporate_actions
from core.redis_client import cache

logger = structlog.get_logger()


class CorporateActionsService:
    """Service for corporate actions operations."""
    
    @staticmethod
    async def get_corporate_actions(
        symbol: str,
        market: str = "india_nse",
        action_type: str = "all"
    ) -> Dict[str, Any]:
        """
        Get corporate actions for a stock.
        
        Args:
            symbol: Stock symbol
            market: Market identifier
            action_type: Type of action (dividend, split, all)
        
        Returns:
            Corporate actions data
        """
        cache_key = f"corporate_actions:{symbol}:{market}:{action_type}"
        
        # Check cache (1 hour TTL)
        cached = cache.get(cache_key)
        if cached:
            logger.info("corporate_actions_cache_hit", symbol=symbol)
            return cached
        
        try:
            result = await get_corporate_actions.ainvoke({
                "symbol": symbol,
                "market": market,
                "action_type": action_type
            })
            
            # Cache for 1 hour
            cache.set(cache_key, result, ttl=3600)
            
            return result
            
        except Exception as e:
            logger.error("corporate_actions_service_error", symbol=symbol, error=str(e))
            return {
                "error": str(e),
                "symbol": symbol
            }

