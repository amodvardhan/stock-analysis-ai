"""
=============================================================================
AI Hub - Technical Analysis Agent
=============================================================================
Analyzes stocks using technical indicators (RSI, MACD, EMA, etc.)
=============================================================================
"""

from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
import structlog

from agents.base_agent import BaseAgent
from agents.tools import calculate_technical_indicators

logger = structlog.get_logger()


class TechnicalAnalysisAgent(BaseAgent):
    """
    Agent specialized in technical analysis.
    
    Uses technical indicators like RSI, MACD, Bollinger Bands, and EMA
    to determine if a stock is overbought, oversold, or in a good trend.
    """
    
    def __init__(self):
        """Initialize technical analysis agent."""
        super().__init__(
            name="TechnicalAnalyst",
            system_prompt="""You are a technical analysis expert.
            
            Analyze stock price patterns and technical indicators to provide insights on:
            - Trend direction (uptrend, downtrend, sideways)
            - Momentum (overbought, oversold, neutral)
            - Support and resistance levels
            - Entry and exit points
            
            Be objective and data-driven in your analysis.""",
            model="gpt-4o-mini"
        )
    
    async def analyze(
        self,
        symbol: str,
        market: str,
        config: RunnableConfig | None = None
    ) -> Dict[str, Any]:
        """
        Run technical analysis on a stock.
        
        Args:
            symbol: Stock ticker symbol
            market: Market identifier
            config: Optional LangChain config
        
        Returns:
            Dict containing technical analysis results
        """
        try:
            logger.info("technical_analysis_started", symbol=symbol, market=market)
            
            # Call the tool correctly using invoke() instead of __call__()
            indicators_data = await calculate_technical_indicators.ainvoke({
                "symbol": symbol,
                "market": market,
                "period": "3mo"
            })
            
            if "error" in indicators_data:
                raise Exception(indicators_data["error"])
            
            # Return the indicators
            return {
                "agent": "TechnicalAnalyst",
                "symbol": symbol,
                "indicators": indicators_data.get("indicators", {}),
                "analyzed_at": indicators_data.get("analyzed_at")
            }
            
        except Exception as e:
            logger.error("technical_analysis_failed", symbol=symbol, error=str(e))
            raise Exception(f"Technical analysis failed: {str(e)}")
