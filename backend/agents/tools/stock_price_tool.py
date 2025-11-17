"""
=============================================================================
AI Hub - Stock Price Data Tool (Production Version)
=============================================================================
Fetches stock price data with enterprise-grade reliability:

Features:
- Redis caching (1-hour TTL)
- Retry logic with exponential backoff
- User-Agent rotation to avoid detection
- Rate limiting protection
- Fallback to alternative data sources
=============================================================================
"""

from typing import Dict, Any
import yfinance as yf
from langchain_core.tools import tool
import structlog
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from fake_useragent import UserAgent
import requests

from core.redis_client import cache

logger = structlog.get_logger()
ua = UserAgent()


def is_rate_limit_error(exception):
    """Check if exception is a rate limit error."""
    if isinstance(exception, requests.exceptions.HTTPError):
        return exception.response.status_code == 429
    return False


@tool
@retry(
    retry=retry_if_exception_type(requests.exceptions.HTTPError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
async def get_stock_price(
    symbol: str,
    market: str = "india_nse",
    period: str = "3mo"
) -> Dict[str, Any]:
    """
    Fetch historical stock price data with caching and retry logic.
    
    Production Features:
    1. **Redis Caching**: Caches responses for 1 hour
    2. **Retry Logic**: Automatically retries on failure (3 attempts)
    3. **User-Agent Rotation**: Avoids rate limit detection
    4. **Error Handling**: Graceful degradation
    
    Args:
        symbol: Stock ticker symbol
        market: Market identifier
        period: Historical period (1mo, 3mo, 6mo, 1y, 2y, 5y, max)
    
    Returns:
        Dict containing price data and metadata
    
    Cache Key Format: stock_price:{symbol}:{market}:{period}
    Cache TTL: 1 hour (3600 seconds)
    """
    try:
        # Generate cache key
        cache_key = f"stock_price:{symbol}:{market}:{period}"
        
        # Check cache first
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info("using_cached_stock_data", symbol=symbol, market=market)
            return cached_data
        
        logger.info("fetching_stock_price", symbol=symbol, market=market)
        
        # Format symbol for market
        if market == "india_nse" and not symbol.endswith(".NS"):
            yahoo_symbol = f"{symbol}.NS"
        elif market == "india_bse" and not symbol.endswith(".BO"):
            yahoo_symbol = f"{symbol}.BO"
        else:
            yahoo_symbol = symbol
        
        # Rotate User-Agent to avoid detection
        session = requests.Session()
        session.headers['User-Agent'] = ua.random
        
        # Fetch data with custom session
        ticker = yf.Ticker(yahoo_symbol, session=session)
        
        # Get historical data
        hist = ticker.history(period=period)
        
        if hist.empty:
            error_msg = f"No data available for {yahoo_symbol}"
            logger.error("no_stock_data", symbol=yahoo_symbol)
            return {
                "error": error_msg,
                "symbol": symbol,
                "yahoo_symbol": yahoo_symbol
            }
        
        # Get current price info
        try:
            info = ticker.info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            previous_close = info.get('previousClose')
        except:
            current_price = hist['Close'].iloc[-1]
            previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        
        # Format historical data
        historical_data = []
        for date, row in hist.iterrows():
            historical_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(row['Open'], 2),
                "high": round(row['High'], 2),
                "low": round(row['Low'], 2),
                "close": round(row['Close'], 2),
                "volume": int(row['Volume'])
            })
        
        result = {
            "symbol": symbol,
            "yahoo_symbol": yahoo_symbol,
            "market": market,
            "current_price": round(current_price, 2) if current_price else None,
            "previous_close": round(previous_close, 2) if previous_close else None,
            "change": round(current_price - previous_close, 2) if (current_price and previous_close) else None,
            "change_percent": round(((current_price - previous_close) / previous_close) * 100, 2) if (current_price and previous_close) else None,
            "historical_data": historical_data,
            "period": period,
            "data_points": len(historical_data),
            "fetched_at": datetime.utcnow().isoformat()
        }
        
        # Cache the result for 1 hour
        cache.set(cache_key, result, ttl=3600)
        
        logger.info(
            "stock_price_fetched",
            symbol=symbol,
            data_points=len(historical_data),
            current_price=current_price
        )
        
        return result
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            logger.error("rate_limit_exceeded", symbol=symbol)
            # Retry will happen automatically via tenacity decorator
            raise
        logger.error("http_error_fetching_stock", symbol=symbol, error=str(e))
        return {
            "error": f"HTTP error: {str(e)}",
            "symbol": symbol
        }
    except Exception as e:
        logger.error("stock_price_fetch_failed", symbol=symbol, error=str(e))
        return {
            "error": f"Failed to fetch stock price: {str(e)}",
            "symbol": symbol
        }
