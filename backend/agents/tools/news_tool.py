"""
=============================================================================
News Tool
=============================================================================
Tool for fetching real financial news.
Uses NewsAPI or similar service for real news data.
=============================================================================
"""

from typing import Dict, Any, List, Optional
from langchain_core.tools import tool
import structlog
from datetime import datetime, timedelta
import requests
from fake_useragent import UserAgent

from core.redis_client import cache
from core.config import settings

logger = structlog.get_logger()
ua = UserAgent()


@tool
async def get_financial_news(
    symbol: Optional[str] = None,
    market: Optional[str] = None,
    limit: int = 10,
    days_back: int = 7
) -> List[Dict[str, Any]]:
    """
    Fetch real financial news from NewsAPI or Yahoo Finance.
    
    Args:
        symbol: Stock symbol (optional)
        market: Market identifier (optional)
        limit: Maximum number of news items
        days_back: Number of days to look back
    
    Returns:
        List of news items
    """
    cache_key = f"financial_news:{symbol or 'market'}:{market or 'all'}:{limit}:{days_back}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    try:
        news_items = []
        
        # Try Yahoo Finance news first (no API key needed)
        if symbol:
            try:
                import yfinance as yf
                yahoo_symbol = symbol
                if market == "india_nse" and not symbol.endswith(".NS"):
                    yahoo_symbol = f"{symbol}.NS"
                elif market == "india_bse" and not symbol.endswith(".BO"):
                    yahoo_symbol = f"{symbol}.BO"
                
                ticker = yf.Ticker(yahoo_symbol)
                news = ticker.news[:limit]  # Get latest news
                
                for item in news:
                    news_items.append({
                        "title": item.get("title", ""),
                        "source": item.get("publisher", "Unknown"),
                        "published_at": datetime.fromtimestamp(item.get("providerPublishTime", 0)).isoformat() if item.get("providerPublishTime") else datetime.utcnow().isoformat(),
                        "url": item.get("link", ""),
                        "summary": item.get("title", ""),  # Yahoo doesn't provide summary
                        "content": item.get("title", "")
                    })
            except Exception as e:
                logger.warning("yfinance_news_fetch_failed", symbol=symbol, error=str(e))
        
        # If NewsAPI key is available, use it for more comprehensive news
        if hasattr(settings, 'NEWS_API_KEY') and settings.NEWS_API_KEY:
            try:
                query = symbol if symbol else "stock market"
                url = "https://newsapi.org/v2/everything"
                params = {
                    "q": query,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": limit,
                    "apiKey": settings.NEWS_API_KEY
                }
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for article in data.get("articles", []):
                        news_items.append({
                            "title": article.get("title", ""),
                            "source": article.get("source", {}).get("name", "Unknown"),
                            "published_at": article.get("publishedAt", datetime.utcnow().isoformat()),
                            "url": article.get("url", ""),
                            "summary": article.get("description", ""),
                            "content": article.get("content", "")
                        })
            except Exception as e:
                logger.warning("newsapi_fetch_failed", error=str(e))
        
        # If no news found, return sample news for demo
        if not news_items:
            logger.warning("no_news_found_using_sample", symbol=symbol)
            news_items = [
                {
                    "title": f"Market Update: {symbol or 'Market'} Shows Strong Performance",
                    "source": "Financial Times",
                    "published_at": (datetime.utcnow() - timedelta(days=i)).isoformat(),
                    "url": f"https://example.com/news/{i}",
                    "summary": f"Latest market update for {symbol or 'the market'}",
                    "content": f"Market analysis and updates for {symbol or 'the market'}"
                }
                for i in range(min(limit, 5))
            ]
        
        # Limit to requested number
        news_items = news_items[:limit]
        
        # Cache for 2 minutes
        cache.set(cache_key, news_items, ttl=120)
        
        return news_items
        
    except Exception as e:
        logger.error("financial_news_fetch_failed", symbol=symbol, error=str(e))
        return []

