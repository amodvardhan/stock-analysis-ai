"""
=============================================================================
Financials Service
=============================================================================
Service layer for financial analysis functionality.
=============================================================================
"""

from typing import Dict, Any
import structlog

from agents.financials_agent import FinancialsAgent
from core.redis_client import cache

logger = structlog.get_logger()


class FinancialsService:
    """Service for financial analysis operations."""
    
    @staticmethod
    async def get_financial_analysis(
        symbol: str,
        market: str = "india_nse"
    ) -> Dict[str, Any]:
        """
        Get comprehensive financial analysis.
        
        Args:
            symbol: Stock symbol
            market: Market identifier
        
        Returns:
            Financial analysis data
        """
        cache_key = f"financial_analysis:{symbol}:{market}"
        
        # Check cache (1 hour TTL)
        cached = cache.get(cache_key)
        if cached:
            logger.info("financial_analysis_cache_hit", symbol=symbol)
            return cached
        
        try:
            agent = FinancialsAgent()
            result = await agent.analyze(
                symbol=symbol,
                market=market
            )
            
            # Cache for 1 hour
            cache.set(cache_key, result, ttl=3600)
            
            return result
            
        except Exception as e:
            logger.error("financials_service_error", symbol=symbol, error=str(e))
            return {
                "error": str(e),
                "symbol": symbol
            }

