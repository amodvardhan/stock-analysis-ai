"""
=============================================================================
Sector Service
=============================================================================
Service layer for sector analysis functionality.
=============================================================================
"""

from typing import Dict, Any, Optional
import structlog

from agents.sector_analysis_agent import SectorAnalysisAgent
from core.redis_client import cache

logger = structlog.get_logger()


class SectorService:
    """Service for sector analysis operations."""
    
    @staticmethod
    async def get_sector_analysis(
        market: str = "india_nse",
        sector: Optional[str] = None,
        compare_sectors: bool = False
    ) -> Dict[str, Any]:
        """
        Get sector analysis.
        
        Args:
            market: Market identifier
            sector: Specific sector to analyze (optional)
            compare_sectors: Whether to compare all sectors
        
        Returns:
            Sector analysis data
        """
        cache_key = f"sector_analysis:{market}:{sector or 'all'}:{compare_sectors}"
        
        # Check cache (5 minutes TTL)
        cached = cache.get(cache_key)
        if cached:
            logger.info("sector_analysis_cache_hit", market=market, sector=sector)
            return cached
        
        try:
            agent = SectorAnalysisAgent()
            result = await agent.analyze(
                market=market,
                sector=sector,
                compare_sectors=compare_sectors
            )
            
            # Cache for 5 minutes
            cache.set(cache_key, result, ttl=300)
            
            return result
            
        except Exception as e:
            logger.error("sector_service_error", market=market, sector=sector, error=str(e))
            return {
                "error": str(e),
                "market": market,
                "sector": sector
            }

