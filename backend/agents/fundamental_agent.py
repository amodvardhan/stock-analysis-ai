"""
=============================================================================
AI Hub - Fundamental Analysis Agent
=============================================================================
Analyzes company financials, valuation metrics, and business fundamentals.
=============================================================================
"""

from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
import structlog

from agents.base_agent import BaseAgent
from agents.tools import get_fundamental_data

logger = structlog.get_logger()


class FundamentalAnalysisAgent(BaseAgent):
    """
    Agent specialized in fundamental analysis.
    
    Evaluates company financials, valuation ratios, and business health.
    """
    
    def __init__(self):
        """Initialize fundamental analysis agent."""
        super().__init__(
            name="FundamentalAnalyst",
            system_prompt="""You are a fundamental analysis expert.
            
            Analyze company financials and business metrics to provide insights on:
            - Valuation (P/E ratio, Price-to-Book, Market Cap)
            - Profitability (Profit margins, ROE, ROA)
            - Financial health (Debt ratios, Cash flow)
            - Growth prospects
            
            Be thorough and conservative in your valuations.""",
            model="gpt-4o-mini"
        )
    
    async def analyze(
        self,
        symbol: str,
        market: str,
        config: RunnableConfig | None = None
    ) -> Dict[str, Any]:
        """
        Run fundamental analysis on a stock.
        
        Args:
            symbol: Stock ticker symbol
            market: Market identifier
            config: Optional LangChain config
        
        Returns:
            Dict containing fundamental analysis results
        """
        try:
            logger.info("fundamental_analysis_started", symbol=symbol, market=market)
            
            # Call the tool correctly using ainvoke()
            fundamental_data = await get_fundamental_data.ainvoke({
                "symbol": symbol,
                "market": market
            })
            
            if "error" in fundamental_data:
                raise Exception(fundamental_data["error"])
            
            return {
                "agent": "FundamentalAnalyst",
                "symbol": symbol,
                "fundamental_details": fundamental_data.get("fundamental_details", {}),
                "analyzed_at": fundamental_data.get("analyzed_at")
            }
            
        except Exception as e:
            logger.error("fundamental_analysis_failed", symbol=symbol, error=str(e))
            raise Exception(f"Fundamental analysis failed: {str(e)}")
