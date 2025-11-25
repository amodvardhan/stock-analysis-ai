"""
=============================================================================
News Service
=============================================================================
Service layer for news functionality.
=============================================================================
"""

from typing import Dict, Any, Optional
import structlog
from datetime import datetime

from agents.news_agent import NewsAgent
from core.redis_client import cache

logger = structlog.get_logger()


class NewsService:
    """Service for news operations."""
    
    @staticmethod
    async def get_news(
        symbol: Optional[str] = None,
        market: Optional[str] = None,
        limit: int = 10,
        days_back: int = 7
    ) -> Dict[str, Any]:
        """
        Get news for a stock or market.
        
        Args:
            symbol: Stock symbol (optional)
            market: Market identifier (optional)
            limit: Maximum number of news items
            days_back: Number of days to look back
        
        Returns:
            News data with sentiment analysis
        """
        cache_key = f"news:{symbol or 'market'}:{market or 'all'}:{limit}:{days_back}"
        
        # Check cache (shorter TTL for news - 2 minutes)
        cached = cache.get(cache_key)
        if cached:
            logger.info("news_cache_hit", symbol=symbol, market=market)
            return cached
        
        try:
            agent = NewsAgent()
            result = await agent.analyze(
                symbol=symbol,
                market=market,
                limit=limit,
                days_back=days_back
            )
            
            # Cache for 2 minutes (news changes frequently)
            cache.set(cache_key, result, ttl=120)
            
            return result
            
        except Exception as e:
            logger.error("news_service_error", symbol=symbol, error=str(e))
            return {
                "error": str(e),
                "symbol": symbol
            }

