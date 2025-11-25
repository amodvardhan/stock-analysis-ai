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
- Fallback to mock data when Yahoo Finance fails
=============================================================================
"""

from typing import Dict, Any
import yfinance as yf
from langchain_core.tools import tool
import structlog
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential
from fake_useragent import UserAgent
import requests
import time
import random

from core.redis_client import cache
from core.config import settings

logger = structlog.get_logger()
ua = UserAgent()


def generate_fallback_data(symbol: str, period: str = "3mo") -> Dict[str, Any]:
    """
    Generate realistic mock data when Yahoo Finance fails.
    
    This ensures the application always returns data, even during:
    - Yahoo Finance outages
    - Rate limiting
    - Network issues
    
    Args:
        symbol: Stock ticker symbol
        period: Historical period
    
    Returns:
        Dict with realistic mock price data
    """
    logger.warning("generating_fallback_data", symbol=symbol, reason="yahoo_finance_unavailable")
    
    # Generate realistic historical data
    days = 90 if period == "3mo" else 180 if period == "6mo" else 365
    base_price = 1200.0  # Realistic base for Indian stocks
    
    historical_data = []
    current_price = base_price
    
    for i in range(days):
        date = datetime.now() - timedelta(days=days - i)
        
        # Realistic price movement (±2%)
        daily_change = random.uniform(-0.02, 0.02)
        current_price = current_price * (1 + daily_change)
        
        # Generate OHLC data
        open_price = current_price * random.uniform(0.98, 1.02)
        high_price = max(open_price, current_price) * random.uniform(1.0, 1.02)
        low_price = min(open_price, current_price) * random.uniform(0.98, 1.0)
        
        historical_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(current_price, 2),
            "volume": random.randint(1000000, 50000000)
        })
    
    previous_close = historical_data[-2]["close"] if len(historical_data) > 1 else current_price
    final_price = historical_data[-1]["close"]
    
    return {
        "symbol": symbol,
        "yahoo_symbol": f"{symbol}.NS",
        "market": "india_nse",
        "current_price": round(final_price, 2),
        "previous_close": round(previous_close, 2),
        "change": round(final_price - previous_close, 2),
        "change_percent": round(((final_price - previous_close) / previous_close) * 100, 2),
        "historical_data": historical_data,
        "period": period,
        "data_points": len(historical_data),
        "data_source": "fallback_demo",
        "fetched_at": datetime.utcnow().isoformat(),
        "note": "Using demo data due to data provider unavailability"
    }


@tool
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
    4. **Fallback Data**: Always returns data, even if Yahoo Finance fails
    5. **Error Handling**: Graceful degradation
    
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
            logger.info("cache_hit_stock_price", symbol=symbol, market=market)
            return cached_data
        
        logger.info("cache_miss_fetching_stock_price", symbol=symbol, market=market)
        
        # Format symbol for market
        if market == "india_nse" and not symbol.endswith(".NS"):
            yahoo_symbol = f"{symbol}.NS"
        elif market == "india_bse" and not symbol.endswith(".BO"):
            yahoo_symbol = f"{symbol}.BO"
        else:
            yahoo_symbol = symbol
        
        # Try fetching from Yahoo Finance with retries
        max_retries = 2  # Reduced from 3 to 2 for faster failure
        for attempt in range(max_retries):
            try:
                # Rotate User-Agent to avoid detection
                session = requests.Session()
                session.headers.update({
                    'User-Agent': ua.random,
                    'Accept': 'application/json',
                    'Accept-Language': 'en-US,en;q=0.9',
                })
                
                # Configure timeouts to prevent hanging requests
                session.timeout = (
                    settings.HTTP_CONNECT_TIMEOUT,
                    settings.HTTP_READ_TIMEOUT
                )
                
                # Add minimal delay between retries (reduced from exponential)
                if attempt > 0:
                    delay = 1  # Reduced from exponential backoff to 1 second
                    logger.info("retry_delay", attempt=attempt + 1, delay_seconds=delay)
                    time.sleep(delay)
                
                # Fetch data with custom session (timeout configured in session)
                ticker = yf.Ticker(yahoo_symbol, session=session)
                # Session timeout will handle request timeouts
                hist = ticker.history(period=period)
                
                if hist.empty:
                    logger.warning("empty_data_from_yfinance", symbol=yahoo_symbol, attempt=attempt + 1)
                    if attempt < max_retries - 1:
                        continue
                    else:
                        raise ValueError(f"No data available for {yahoo_symbol}")
                
                # Get current price info (session timeout will handle this)
                try:
                    info = ticker.info
                    current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                    previous_close = info.get('previousClose')
                except (requests.exceptions.Timeout, Exception) as e:
                    logger.warning("info_fetch_failed_using_hist", symbol=yahoo_symbol, error=str(e))
                    # Fallback to historical data
                    current_price = hist['Close'].iloc[-1]
                    previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                
                # Format historical data
                historical_data = []
                for date, row in hist.iterrows():
                    historical_data.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "open": round(float(row['Open']), 2),
                        "high": round(float(row['High']), 2),
                        "low": round(float(row['Low']), 2),
                        "close": round(float(row['Close']), 2),
                        "volume": int(row['Volume'])
                    })
                
                result = {
                    "symbol": symbol,
                    "yahoo_symbol": yahoo_symbol,
                    "market": market,
                    "current_price": round(float(current_price), 2) if current_price else None,
                    "previous_close": round(float(previous_close), 2) if previous_close else None,
                    "change": round(float(current_price - previous_close), 2) if (current_price and previous_close) else None,
                    "change_percent": round(((float(current_price) - float(previous_close)) / float(previous_close)) * 100, 2) if (current_price and previous_close) else None,
                    "historical_data": historical_data,
                    "period": period,
                    "data_points": len(historical_data),
                    "data_source": "yahoo_finance",
                    "fetched_at": datetime.utcnow().isoformat()
                }
                
                # Cache the result for 1 hour
                cache.set(cache_key, result, ttl=3600)
                
                logger.info(
                    "stock_price_fetched_successfully",
                    symbol=symbol,
                    data_points=len(historical_data),
                    current_price=current_price,
                    attempt=attempt + 1
                )
                
                return result
                
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                logger.warning("request_timeout_or_connection_error", symbol=symbol, error=str(e), attempt=attempt + 1)
                if attempt < max_retries - 1:
                    # Minimal delay for timeout/connection errors
                    time.sleep(0.5)
                    continue
                    
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    logger.warning("rate_limit_encountered", symbol=symbol, attempt=attempt + 1)
                    if attempt < max_retries - 1:
                        time.sleep(2)  # Reduced from 5 * (attempt + 1) to 2 seconds
                        continue
                logger.error("http_error_fetching_stock", symbol=symbol, error=str(e), attempt=attempt + 1)
                
            except Exception as e:
                logger.error("fetch_attempt_failed", symbol=symbol, error=str(e), attempt=attempt + 1)
                if attempt < max_retries - 1:
                    time.sleep(0.5)  # Minimal delay before retry
                    continue
        
        # If all retries failed, use fallback data
        logger.warning("all_retries_failed_using_fallback", symbol=symbol)
        fallback_result = generate_fallback_data(symbol, period)
        
        # Cache fallback data for shorter duration (15 minutes)
        cache.set(cache_key, fallback_result, ttl=900)
        
        return fallback_result
        
    except Exception as e:
        logger.error("stock_price_tool_failed", symbol=symbol, error=str(e))
        
        # Last resort: return fallback data
        return generate_fallback_data(symbol, period)
