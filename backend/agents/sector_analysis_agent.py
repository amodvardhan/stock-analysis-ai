"""
=============================================================================
Sector Analysis Agent
=============================================================================
Agent responsible for:
- Sector-wise performance analysis
- Sector comparison
- Sector trends identification
- Sector-specific recommendations
=============================================================================
"""

from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime, timedelta

from agents.base_agent import BaseAgent
from agents.tools.market_data_tool import get_sector_performance

logger = structlog.get_logger()


class SectorAnalysisAgent(BaseAgent):
    """
    Agent that analyzes sector performance and trends.
    """
    
    def __init__(self):
        system_prompt = """You are a Sector Analysis Specialist focusing on:
        1. Analyzing sector-wise performance
        2. Comparing sectors
        3. Identifying sector trends
        4. Providing sector-specific insights
        5. Recommending sector allocation strategies
        
        Always provide data-driven, actionable sector analysis."""
        
        super().__init__(
            name="SectorAnalyst",
            system_prompt=system_prompt,
            model="gpt-4o-mini",
            temperature=0.1
        )
    
    async def analyze(
        self,
        market: str = "india_nse",
        sector: Optional[str] = None,
        compare_sectors: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze sector performance.
        
        Args:
            market: Market identifier
            sector: Specific sector to analyze (optional)
            compare_sectors: Whether to compare all sectors
        
        Returns:
            Dict containing sector analysis
        """
        logger.info("sector_analysis_started", market=market, sector=sector)
        
        try:
            if sector:
                # Analyze specific sector
                sector_data = await self._analyze_single_sector(market, sector)
                result = {
                    "market": market,
                    "sector": sector,
                    "timestamp": datetime.utcnow().isoformat(),
                    "sector_data": sector_data,
                    "insights": await self._generate_sector_insights(sector_data, sector)
                }
            else:
                # Analyze all sectors
                all_sectors = await self._analyze_all_sectors(market)
                result = {
                    "market": market,
                    "timestamp": datetime.utcnow().isoformat(),
                    "sectors": all_sectors,
                    "comparison": await self._compare_sectors(all_sectors) if compare_sectors else None,
                    "insights": await self._generate_market_sector_insights(all_sectors)
                }
            
            logger.info("sector_analysis_completed", market=market, sector=sector)
            return result
            
        except Exception as e:
            logger.error("sector_analysis_failed", market=market, sector=sector, error=str(e))
            return {
                "error": str(e),
                "market": market,
                "sector": sector
            }
    
    async def _analyze_single_sector(
        self,
        market: str,
        sector: str
    ) -> Dict[str, Any]:
        """Analyze a single sector using real data."""
        try:
            sectors_data = await get_sector_performance.ainvoke({"market": market})
            sector_data = sectors_data.get("sectors", {}).get(sector, {})
            
            return {
                "sector": sector,
                "total_stocks": 0,  # Would need to count stocks in sector
                "avg_change": sector_data.get("avg_change", 0),
                "avg_volume": 0,
                "top_gainers": sector_data.get("top_gainers", []),
                "top_losers": sector_data.get("top_losers", []),
                "sector_metrics": {
                    "pe_ratio": 0,
                    "market_cap": 0,
                    "dividend_yield": 0
                }
            }
        except Exception as e:
            logger.error("sector_analysis_failed", sector=sector, error=str(e))
            return {
                "sector": sector,
                "total_stocks": 0,
                "avg_change": 0,
                "avg_volume": 0,
                "top_gainers": [],
                "top_losers": [],
                "sector_metrics": {}
            }
    
    async def _analyze_all_sectors(self, market: str) -> Dict[str, Dict[str, Any]]:
        """Analyze all sectors in the market using real data."""
        try:
            result = await get_sector_performance.ainvoke({"market": market})
            sectors_data = result.get("sectors", {})
            
            # Format to match expected structure
            formatted_sectors = {}
            for sector, data in sectors_data.items():
                formatted_sectors[sector] = {
                    "sector": sector,
                    "total_stocks": 0,
                    "avg_change": data.get("avg_change", 0),
                    "avg_volume": 0,
                    "top_gainers": data.get("top_gainers", []),
                    "top_losers": data.get("top_losers", []),
                    "sector_metrics": {}
                }
            
            return formatted_sectors
        except Exception as e:
            logger.error("all_sectors_analysis_failed", market=market, error=str(e))
            return {}
    
    async def _compare_sectors(
        self,
        sectors_data: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compare all sectors."""
        # Rank sectors by performance
        ranked = sorted(
            sectors_data.items(),
            key=lambda x: x[1].get("avg_change", 0),
            reverse=True
        )
        
        return {
            "best_performer": ranked[0][0] if ranked else None,
            "worst_performer": ranked[-1][0] if ranked else None,
            "ranking": [
                {
                    "sector": sector,
                    "performance": data.get("avg_change", 0),
                    "rank": idx + 1
                }
                for idx, (sector, data) in enumerate(ranked)
            ]
        }
    
    async def _generate_sector_insights(
        self,
        sector_data: Dict[str, Any],
        sector: str
    ) -> str:
        """Generate insights for a specific sector."""
        prompt = f"""Analyze this sector performance:
        
        Sector: {sector}
        Average Change: {sector_data.get('avg_change', 0)}%
        Total Stocks: {sector_data.get('total_stocks', 0)}
        
        Provide:
        1. Sector performance assessment
        2. Key drivers of performance
        3. Outlook for the sector
        4. Investment recommendations
        
        Keep response concise."""
        
        try:
            insights = await self.invoke(prompt)
            return insights
        except Exception as e:
            logger.error("sector_insights_generation_failed", error=str(e))
            return "Sector analysis in progress."
    
    async def _generate_market_sector_insights(
        self,
        sectors_data: Dict[str, Dict[str, Any]]
    ) -> str:
        """Generate insights for all sectors."""
        prompt = f"""Analyze sector performance across the market:
        
        Number of sectors: {len(sectors_data)}
        
        Top performing sectors:
        {self._get_top_sectors(sectors_data, top_n=3)}
        
        Provide:
        1. Overall sector trends
        2. Sector rotation patterns
        3. Investment opportunities
        4. Sector allocation recommendations
        
        Keep response concise and actionable."""
        
        try:
            insights = await self.invoke(prompt)
            return insights
        except Exception as e:
            logger.error("market_sector_insights_generation_failed", error=str(e))
            return "Sector analysis in progress."
    
    def _get_top_sectors(
        self,
        sectors_data: Dict[str, Dict[str, Any]],
        top_n: int = 3
    ) -> str:
        """Get top performing sectors."""
        ranked = sorted(
            sectors_data.items(),
            key=lambda x: x[1].get("avg_change", 0),
            reverse=True
        )
        
        return "\n".join([
            f"{idx + 1}. {sector}: {data.get('avg_change', 0):.2f}%"
            for idx, (sector, data) in enumerate(ranked[:top_n])
        ])

