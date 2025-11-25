"""
=============================================================================
News Agent
=============================================================================
Agent responsible for:
- Fetching financial news
- Analyzing news sentiment
- Categorizing news by relevance
- Providing news-based insights
=============================================================================
"""

from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime, timedelta

from agents.base_agent import BaseAgent
from agents.tools.news_tool import get_financial_news

logger = structlog.get_logger()


class NewsAgent(BaseAgent):
    """
    Agent that fetches and analyzes financial news.
    """
    
    def __init__(self):
        system_prompt = """You are a Financial News Analyst specializing in:
        1. Analyzing financial news articles
        2. Extracting key information and sentiment
        3. Identifying market-moving news
        4. Categorizing news by relevance and impact
        5. Providing actionable insights from news
        
        Always provide accurate, unbiased analysis."""
        
        super().__init__(
            name="NewsAnalyst",
            system_prompt=system_prompt,
            model="gpt-4o-mini",
            temperature=0.1
        )
    
    async def analyze(
        self,
        symbol: Optional[str] = None,
        market: Optional[str] = None,
        limit: int = 10,
        days_back: int = 7
    ) -> Dict[str, Any]:
        """
        Analyze news for a stock or market.
        
        Args:
            symbol: Stock symbol (optional, for stock-specific news)
            market: Market identifier (optional)
            limit: Maximum number of news items
            days_back: Number of days to look back
        
        Returns:
            Dict containing news analysis
        """
        logger.info(
            "news_analysis_started",
            symbol=symbol,
            market=market,
            limit=limit
        )
        
        try:
            # Fetch news (in real implementation, use news API)
            news_items = await self._fetch_news(symbol, market, limit, days_back)
            
            # Analyze sentiment for each news item
            analyzed_news = []
            for item in news_items:
                sentiment = await self._analyze_news_sentiment(item)
                analyzed_news.append({
                    **item,
                    "sentiment": sentiment
                })
            
            # Generate overall insights
            overall_insights = await self._generate_news_insights(analyzed_news, symbol)
            
            result = {
                "symbol": symbol,
                "market": market,
                "timestamp": datetime.utcnow().isoformat(),
                "news_items": analyzed_news,
                "summary": {
                    "total_news": len(analyzed_news),
                    "positive_count": sum(1 for n in analyzed_news if n["sentiment"]["label"] == "positive"),
                    "negative_count": sum(1 for n in analyzed_news if n["sentiment"]["label"] == "negative"),
                    "neutral_count": sum(1 for n in analyzed_news if n["sentiment"]["label"] == "neutral"),
                    "overall_sentiment": self._calculate_overall_sentiment(analyzed_news)
                },
                "insights": overall_insights
            }
            
            logger.info("news_analysis_completed", symbol=symbol, items_count=len(analyzed_news))
            return result
            
        except Exception as e:
            logger.error("news_analysis_failed", symbol=symbol, error=str(e))
            return {
                "error": str(e),
                "symbol": symbol
            }
    
    async def _fetch_news(
        self,
        symbol: Optional[str],
        market: Optional[str],
        limit: int,
        days_back: int
    ) -> List[Dict[str, Any]]:
        """Fetch real news from news APIs."""
        try:
            news_items = await get_financial_news.ainvoke({
                "symbol": symbol,
                "market": market,
                "limit": limit,
                "days_back": days_back
            })
            return news_items
        except Exception as e:
            logger.error("news_fetch_failed", symbol=symbol, error=str(e))
            return []
    
    async def _analyze_news_sentiment(self, news_item: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment of a news article."""
        prompt = f"""Analyze the sentiment of this financial news article:
        
        Title: {news_item.get('title', '')}
        Summary: {news_item.get('summary', '')}
        
        Provide:
        1. Sentiment label (positive/negative/neutral)
        2. Sentiment score (0-100, where 50 is neutral)
        3. Key points that influenced the sentiment
        4. Market impact assessment (high/medium/low)
        
        Respond in JSON format:
        {{
            "label": "positive|negative|neutral",
            "score": 75,
            "key_points": ["point1", "point2"],
            "market_impact": "high|medium|low"
        }}"""
        
        try:
            response = await self.invoke(prompt)
            # Parse JSON response (in real implementation, use structured output)
            return {
                "label": "neutral",
                "score": 50,
                "key_points": [],
                "market_impact": "medium"
            }
        except Exception as e:
            logger.error("sentiment_analysis_failed", error=str(e))
            return {
                "label": "neutral",
                "score": 50,
                "key_points": [],
                "market_impact": "medium"
            }
    
    async def _generate_news_insights(
        self,
        news_items: List[Dict[str, Any]],
        symbol: Optional[str]
    ) -> str:
        """Generate overall insights from news."""
        if not news_items:
            return "No recent news available."
        
        prompt = f"""Based on the following news articles, provide key insights:
        
        {'Stock: ' + symbol if symbol else 'Market-wide news'}
        Number of articles: {len(news_items)}
        
        News Summary:
        {self._summarize_news(news_items)}
        
        Provide:
        1. Key themes and trends
        2. Most impactful news items
        3. Overall market/news sentiment
        4. Actionable insights for investors
        
        Keep response concise and actionable."""
        
        try:
            insights = await self.invoke(prompt)
            return insights
        except Exception as e:
            logger.error("insights_generation_failed", error=str(e))
            return "News analysis in progress."
    
    def _summarize_news(self, news_items: List[Dict[str, Any]]) -> str:
        """Create a summary of news items."""
        summaries = []
        for item in news_items[:5]:  # Top 5
            summaries.append(f"- {item.get('title', 'No title')} ({item.get('sentiment', {}).get('label', 'unknown')})")
        return "\n".join(summaries)
    
    def _calculate_overall_sentiment(self, news_items: List[Dict[str, Any]]) -> str:
        """Calculate overall sentiment from news items."""
        if not news_items:
            return "neutral"
        
        positive = sum(1 for n in news_items if n.get("sentiment", {}).get("label") == "positive")
        negative = sum(1 for n in news_items if n.get("sentiment", {}).get("label") == "negative")
        
        if positive > negative * 1.5:
            return "positive"
        elif negative > positive * 1.5:
            return "negative"
        else:
            return "neutral"

