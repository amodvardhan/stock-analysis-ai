"""
=============================================================================
Market Movers Agent
=============================================================================
Agent responsible for identifying:
- Top gainers
- Top losers
- Most active stocks
- Volume leaders
- Price movers
=============================================================================
"""

from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime

from agents.base_agent import BaseAgent
from agents.tools.market_data_tool import get_top_gainers_losers

logger = structlog.get_logger()


class MarketMoversAgent(BaseAgent):
    """
    Agent that identifies market movers (gainers, losers, active stocks).
    """
    
    def __init__(self):
        system_prompt = """You are a Market Movers Analyst specializing in:
        1. Identifying top gainers and losers
        2. Analyzing volume leaders
        3. Detecting unusual price movements
        4. Providing insights on market activity
        5. Highlighting potential trading opportunities
        
        Always provide accurate, data-driven analysis."""
        
        super().__init__(
            name="MarketMoversAnalyst",
            system_prompt=system_prompt,
            model="gpt-4o-mini",
            temperature=0.1
        )
    
    async def analyze(
        self,
        market: str = "india_nse",
        movers_type: str = "all",  # "gainers", "losers", "active", "all"
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Analyze market movers.
        
        Args:
            market: Market identifier
            movers_type: Type of movers to analyze
            limit: Maximum number of stocks to return
        
        Returns:
            Dict containing market movers analysis
        """
        logger.info(
            "market_movers_analysis_started",
            market=market,
            movers_type=movers_type
        )
        
        try:
            # Get market movers data
            # In real implementation, fetch from market data API
            movers_data = await self._get_market_movers(market, movers_type, limit)
            
            # Generate AI insights
            insights = await self._generate_movers_insights(movers_data, market, movers_type)
            
            result = {
                "market": market,
                "movers_type": movers_type,
                "timestamp": datetime.utcnow().isoformat(),
                "gainers": movers_data.get("gainers", []),
                "losers": movers_data.get("losers", []),
                "most_active": movers_data.get("most_active", []),
                "volume_leaders": movers_data.get("volume_leaders", []),
                "insights": insights
            }
            
            logger.info("market_movers_analysis_completed", market=market)
            return result
            
        except Exception as e:
            logger.error("market_movers_analysis_failed", market=market, error=str(e))
            return {
                "error": str(e),
                "market": market
            }
    
    async def _get_market_movers(
        self,
        market: str,
        movers_type: str,
        limit: int
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get market movers data from real API."""
        try:
            result = await get_top_gainers_losers.ainvoke({
                "market": market,
                "limit": limit
            })
            
            gainers = result.get("gainers", [])
            losers = result.get("losers", [])
            
            # For most_active, we'll use gainers+losers sorted by volume (if available)
            # For now, use top gainers as most active
            most_active = (gainers + losers)[:limit]
            
            return {
                "gainers": gainers[:limit],
                "losers": losers[:limit],
                "most_active": most_active,
                "volume_leaders": most_active  # Same as most_active for now
            }
        except Exception as e:
            logger.error("market_movers_fetch_failed", market=market, error=str(e))
            return {
                "gainers": [],
                "losers": [],
                "most_active": [],
                "volume_leaders": []
            }
    
    async def _generate_movers_insights(
        self,
        movers_data: Dict[str, List[Dict[str, Any]]],
        market: str,
        movers_type: str
    ) -> str:
        """Generate AI insights on market movers."""
        prompt = f"""Analyze the following market movers data:
        
        Market: {market}
        Type: {movers_type}
        
        Top Gainers: {len(movers_data.get('gainers', []))} stocks
        Top Losers: {len(movers_data.get('losers', []))} stocks
        Most Active: {len(movers_data.get('most_active', []))} stocks
        
        Provide:
        1. Key patterns in market movements
        2. Notable sectors or themes
        3. Potential reasons for movements
        4. Trading opportunities or warnings
        
        Keep response concise and actionable."""
        
        try:
            insights = await self.invoke(prompt)
            return insights
        except Exception as e:
            logger.error("movers_insights_generation_failed", error=str(e))
            return "Market movers analysis in progress."

