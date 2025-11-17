"""
=============================================================================
AI Hub - Sentiment Analysis Agent
=============================================================================
Analyzes news sentiment and market sentiment for stocks.
=============================================================================
"""

from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
import structlog

from agents.base_agent import BaseAgent
from agents.tools import analyze_sentiment

logger = structlog.get_logger()


class SentimentAnalysisAgent(BaseAgent):
    """
    Agent specialized in sentiment analysis.
    
    Analyzes news, social media, and market sentiment for stocks.
    """
    
    def __init__(self):
        """Initialize sentiment analysis agent."""
        super().__init__(
            name="SentimentAnalyst",
            system_prompt="""You are a market sentiment analysis expert.
            
            Analyze news and market sentiment to provide insights on:
            - Overall market sentiment (positive, negative, neutral)
            - Key news events and their impact
            - Social media sentiment trends
            - Market mood and investor confidence
            
            Be objective and consider multiple sources.""",
            model="gpt-4o-mini"
        )
    
    async def analyze(
        self,
        symbol: str,
        company_name: str,
        config: RunnableConfig | None = None
    ) -> Dict[str, Any]:
        """
        Run sentiment analysis on a stock.
        
        Args:
            symbol: Stock ticker symbol
            company_name: Full company name
            config: Optional LangChain config
        
        Returns:
            Dict containing sentiment analysis results
        """
        try:
            logger.info("sentiment_analysis_started", symbol=symbol)
            
            # Call the tool correctly using ainvoke()
            sentiment_data = await analyze_sentiment.ainvoke({
                "symbol": symbol,
                "company_name": company_name
            })
            
            if "error" in sentiment_data:
                raise Exception(sentiment_data["error"])
            
            return {
                "agent": "SentimentAnalyst",
                "symbol": symbol,
                "sentiment_details": sentiment_data.get("sentiment_details", {}),
                "overall_sentiment": sentiment_data.get("overall_sentiment"),
                "analyzed_at": sentiment_data.get("analyzed_at")
            }
            
        except Exception as e:
            logger.error("sentiment_analysis_failed", symbol=symbol, error=str(e))
            raise Exception(f"Sentiment analysis failed: {str(e)}")
