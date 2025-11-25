"""
=============================================================================
Peer Comparison Service
=============================================================================
Service layer for peer comparison functionality.
=============================================================================
"""

from typing import Dict, Any, List
import structlog
from datetime import datetime

from agents.peer_comparison_agent import PeerComparisonAgent
from core.redis_client import cache

logger = structlog.get_logger()


class PeerComparisonService:
    """Service for peer comparison operations."""
    
    @staticmethod
    async def compare_stocks(
        symbols: List[str],
        market: str = "india_nse"
    ) -> Dict[str, Any]:
        """
        Compare multiple stocks.
        
        Args:
            symbols: List of stock symbols
            market: Market identifier
        
        Returns:
            Comparison analysis data
        """
        # Create cache key from sorted symbols
        symbols_key = "_".join(sorted(symbols))
        cache_key = f"peer_comparison:{symbols_key}:{market}"
        
        # Check cache (10 minutes TTL)
        cached = cache.get(cache_key)
        if cached:
            logger.info("peer_comparison_cache_hit", symbols=symbols)
            return cached
        
        try:
            agent = PeerComparisonAgent()
            result = await agent.analyze(
                symbols=symbols,
                market=market
            )
            
            # Cache for 10 minutes
            cache.set(cache_key, result, ttl=600)
            
            return result
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error("peer_comparison_service_error", 
                       symbols=symbols, 
                       error=str(e),
                       error_type=type(e).__name__,
                       traceback=error_trace)
            return {
                "error": str(e),
                "symbols": symbols,
                "comparison": {"symbols": [], "metrics": {}},
                "best_performers": {},
                "insights": f"Comparison failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }

