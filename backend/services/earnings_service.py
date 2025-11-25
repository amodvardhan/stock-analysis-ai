"""
=============================================================================
Earnings Calendar Service
=============================================================================
Service layer for earnings calendar functionality.
=============================================================================
"""

from typing import Dict, Any
import structlog

from agents.tools.earnings_tool import get_earnings_calendar, get_ipo_calendar
from core.redis_client import cache

logger = structlog.get_logger()


class EarningsService:
    """Service for earnings calendar operations."""
    
    @staticmethod
    async def get_earnings_calendar(
        market: str = "india_nse",
        days_ahead: int = 30
    ) -> Dict[str, Any]:
        """
        Get earnings calendar.
        
        Args:
            market: Market identifier
            days_ahead: Number of days to look ahead
        
        Returns:
            Earnings calendar data
        """
        cache_key = f"earnings_calendar:{market}:{days_ahead}"
        
        # Check cache (6 hours TTL)
        cached = cache.get(cache_key)
        if cached:
            logger.info("earnings_calendar_cache_hit", market=market)
            return cached
        
        try:
            result = await get_earnings_calendar.ainvoke({
                "market": market,
                "days_ahead": days_ahead
            })
            
            # Cache for 6 hours
            cache.set(cache_key, result, ttl=21600)
            
            return result
            
        except Exception as e:
            logger.error("earnings_service_error", market=market, error=str(e))
            return {
                "error": str(e),
                "market": market
            }
    
    @staticmethod
    async def get_ipo_calendar(
        market: str = "india_nse",
        days_ahead: int = 90
    ) -> Dict[str, Any]:
        """
        Get IPO calendar.
        
        Args:
            market: Market identifier
            days_ahead: Number of days to look ahead
        
        Returns:
            IPO calendar data
        """
        cache_key = f"ipo_calendar:{market}:{days_ahead}"
        
        # Check cache (1 day TTL)
        cached = cache.get(cache_key)
        if cached:
            logger.info("ipo_calendar_cache_hit", market=market)
            return cached
        
        try:
            result = await get_ipo_calendar.ainvoke({
                "market": market,
                "days_ahead": days_ahead
            })
            
            # Cache for 1 day
            cache.set(cache_key, result, ttl=86400)
            
            return result
            
        except Exception as e:
            logger.error("ipo_service_error", market=market, error=str(e))
            return {
                "error": str(e),
                "market": market
            }

