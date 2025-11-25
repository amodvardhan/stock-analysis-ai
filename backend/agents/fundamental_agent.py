"""
=============================================================================
AI Hub - Fundamental Analysis Agent
=============================================================================
Analyzes company financials, valuation metrics, and business fundamentals.
=============================================================================
"""

from typing import Dict, Any
from datetime import datetime
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
            
            # Call tool with dict input
            tool_input = {
                "symbol": symbol,
                "market": market
            }
            
            fundamental_data = await get_fundamental_data.ainvoke(tool_input)
            
            # Even if there's an error or fallback data, return it gracefully
            # The orchestrator and recommendation service can handle partial data
            if "error" in fundamental_data and fundamental_data.get("data_source") != "fallback":
                logger.warning("fundamental_data_has_error", symbol=symbol, error=fundamental_data.get("error"))
                # Return a minimal response that allows analysis to continue
                return {
                    "agent": "FundamentalAnalyst",
                    "symbol": symbol,
                    "fundamental_details": {},
                    "analyzed_at": datetime.utcnow().isoformat(),
                    "error": fundamental_data.get("error"),
                    "note": "Fundamental data unavailable - analysis continues with technical and sentiment data"
                }
            
            return {
                "agent": "FundamentalAnalyst",
                "symbol": symbol,
                "fundamental_details": fundamental_data.get("fundamental_details", {}),
                "analyzed_at": fundamental_data.get("analyzed_at"),
                "data_source": fundamental_data.get("data_source", "yahoo_finance")
            }
            
        except Exception as e:
            logger.error("fundamental_analysis_failed", symbol=symbol, error=str(e))
            # Return graceful error response instead of raising
            # This allows the orchestrator to continue with other analyses
            return {
                "agent": "FundamentalAnalyst",
                "symbol": symbol,
                "fundamental_details": {},
                "analyzed_at": datetime.utcnow().isoformat(),
                "error": str(e),
                "note": "Fundamental analysis failed - continuing with available data"
            }
