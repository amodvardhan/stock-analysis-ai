"""
=============================================================================
Market Overview Agent
=============================================================================
Agent responsible for providing comprehensive market overview including:
- Market indices performance
- Sector-wise performance
- Market statistics
- Overall market sentiment
=============================================================================
"""

from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime, timedelta

from agents.base_agent import BaseAgent
from agents.tools.market_data_tool import get_market_indices, get_sector_performance

logger = structlog.get_logger()


class MarketOverviewAgent(BaseAgent):
    """
    Agent that provides comprehensive market overview and statistics.
    """
    
    def __init__(self):
        system_prompt = """You are a Market Overview Analyst specializing in providing comprehensive 
        market insights and statistics. Your role is to:
        1. Analyze overall market performance
        2. Identify key market trends
        3. Provide sector-wise breakdown
        4. Highlight market movers
        5. Assess overall market sentiment
        
        Always provide data-driven insights with clear explanations."""
        
        super().__init__(
            name="MarketOverviewAnalyst",
            system_prompt=system_prompt,
            model="gpt-4o-mini",
            temperature=0.1
        )
    
    async def analyze(
        self,
        market: str = "india_nse",
        include_sectors: bool = True,
        include_indices: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze overall market overview.
        
        Args:
            market: Market identifier
            include_sectors: Whether to include sector analysis
            include_indices: Whether to include index performance
        
        Returns:
            Dict containing market overview
        """
        logger.info("market_overview_analysis_started", market=market)
        
        try:
            # Get major indices for the market
            indices = await self._get_market_indices(market)
            
            # Get sector performance
            sectors_data = {}
            if include_sectors:
                sectors_data = await self._get_sector_performance(market)
            
            # Get market statistics
            market_stats = await self._get_market_statistics(market)
            
            # Generate AI insights
            ai_insights = await self._generate_market_insights(
                indices, sectors_data, market_stats, market
            )
            
            result = {
                "market": market,
                "timestamp": datetime.utcnow().isoformat(),
                "indices": indices if include_indices else {},
                "sectors": sectors_data if include_sectors else {},
                "statistics": market_stats,
                "ai_insights": ai_insights,
                "overall_sentiment": self._calculate_market_sentiment(indices, sectors_data)
            }
            
            logger.info("market_overview_analysis_completed", market=market)
            return result
            
        except Exception as e:
            logger.error("market_overview_analysis_failed", market=market, error=str(e))
            return {
                "error": str(e),
                "market": market
            }
    
    async def _get_market_indices(self, market: str) -> Dict[str, Any]:
        """Get major market indices from real API."""
        try:
            result = await get_market_indices.ainvoke({"market": market})
            return result.get("indices", {})
        except Exception as e:
            logger.error("market_indices_fetch_failed", market=market, error=str(e))
            return {}
    
    async def _get_sector_performance(self, market: str) -> Dict[str, Any]:
        """Get sector-wise performance from real API."""
        try:
            result = await get_sector_performance.ainvoke({"market": market})
            return result.get("sectors", {})
        except Exception as e:
            logger.error("sector_performance_fetch_failed", market=market, error=str(e))
            return {}
    
    async def _get_market_statistics(self, market: str) -> Dict[str, Any]:
        """Get overall market statistics."""
        return {
            "total_stocks": 0,
            "advancing": 0,
            "declining": 0,
            "unchanged": 0,
            "total_volume": 0,
            "market_cap": 0
        }
    
    async def _generate_market_insights(
        self,
        indices: Dict[str, Any],
        sectors: Dict[str, Any],
        stats: Dict[str, Any],
        market: str
    ) -> str:
        """Generate AI-powered market insights."""
        prompt = f"""Analyze the following market data and provide key insights:
        
        Market: {market}
        Indices Performance: {indices}
        Sector Performance: {sectors}
        Market Statistics: {stats}
        
        Provide:
        1. Overall market trend (bullish/bearish/neutral)
        2. Key sectors driving the market
        3. Notable market movements
        4. Short-term outlook (1-3 days)
        
        Keep the response concise and actionable."""
        
        try:
            insights = await self.invoke(prompt)
            return insights
        except Exception as e:
            logger.error("ai_insights_generation_failed", error=str(e))
            return "Market analysis in progress. Please check back shortly."
    
    def _calculate_market_sentiment(
        self,
        indices: Dict[str, Any],
        sectors: Dict[str, Any]
    ) -> str:
        """Calculate overall market sentiment."""
        # Simple sentiment calculation based on indices
        positive_count = sum(
            1 for idx in indices.values()
            if idx.get("change_percent", 0) > 0
        )
        total_indices = len(indices) if indices else 1
        
        if positive_count / total_indices > 0.7:
            return "bullish"
        elif positive_count / total_indices < 0.3:
            return "bearish"
        else:
            return "neutral"

