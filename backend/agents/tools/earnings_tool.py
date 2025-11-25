"""
=============================================================================
Earnings Calendar Tool
=============================================================================
Tool for fetching earnings calendar and IPO data.
Uses Yahoo Finance for earnings data.
=============================================================================
"""

from typing import Dict, Any, List, Optional
from langchain_core.tools import tool
import structlog
from datetime import datetime, timedelta
import yfinance as yf
from fake_useragent import UserAgent

from core.redis_client import cache

logger = structlog.get_logger()
ua = UserAgent()


@tool
async def get_earnings_calendar(
    market: str = "india_nse",
    days_ahead: int = 30
) -> Dict[str, Any]:
    """
    Get earnings calendar for upcoming earnings.
    
    Note: Yahoo Finance doesn't have a direct earnings calendar API.
    This uses a list of popular stocks and checks their earnings dates.
    
    Args:
        market: Market identifier
        days_ahead: Number of days to look ahead
    
    Returns:
        Dict with earnings calendar
    """
    cache_key = f"earnings_calendar:{market}:{days_ahead}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    try:
        # Popular stocks for each market
        popular_stocks = {
            "india_nse": [
                "RELIANCE", "TCS", "HDFCBANK", "INFY", "HINDUNILVR",
                "ICICIBANK", "BHARTIARTL", "SBIN", "BAJFINANCE", "LICI"
            ],
            "us_nyse": [
                "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
                "META", "NVDA", "JPM", "V", "JNJ"
            ],
            "us_nasdaq": [
                "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"
            ]
        }
        
        stocks = popular_stocks.get(market, [])
        earnings_events = []
        
        for symbol in stocks:
            try:
                # Format symbol
                if market == "india_nse" and not symbol.endswith(".NS"):
                    yahoo_symbol = f"{symbol}.NS"
                elif market == "india_bse" and not symbol.endswith(".BO"):
                    yahoo_symbol = f"{symbol}.BO"
                else:
                    yahoo_symbol = symbol
                
                ticker = yf.Ticker(yahoo_symbol)
                info = ticker.info
                
                # Get earnings date
                earnings_date = info.get('earningsDate') or info.get('mostRecentQuarter')
                if earnings_date:
                    if isinstance(earnings_date, (int, float)):
                        earnings_dt = datetime.fromtimestamp(earnings_date)
                    else:
                        earnings_dt = datetime.fromisoformat(str(earnings_date))
                    
                    # Check if within days_ahead
                    if earnings_dt <= datetime.now() + timedelta(days=days_ahead):
                        earnings_events.append({
                            "symbol": symbol,
                            "company_name": info.get('longName') or symbol,
                            "earnings_date": earnings_dt.strftime("%Y-%m-%d"),
                            "fiscal_year_end": info.get('fiscalYearEnd'),
                            "estimated_eps": info.get('trailingEps')
                        })
            except Exception as e:
                logger.warning("earnings_date_fetch_failed", symbol=symbol, error=str(e))
                continue
        
        # Sort by earnings date
        earnings_events.sort(key=lambda x: x["earnings_date"])
        
        result = {
            "market": market,
            "earnings_events": earnings_events,
            "total_events": len(earnings_events),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Cache for 6 hours
        cache.set(cache_key, result, ttl=21600)
        return result
        
    except Exception as e:
        logger.error("earnings_calendar_fetch_failed", market=market, error=str(e))
        return {
            "market": market,
            "earnings_events": [],
            "error": str(e)
        }


@tool
async def get_ipo_calendar(
    market: str = "india_nse",
    days_ahead: int = 90
) -> Dict[str, Any]:
    """
    Get IPO calendar.
    
    Note: Yahoo Finance doesn't have direct IPO calendar API.
    This would need integration with specialized IPO data providers.
    For now, returns structure for future implementation.
    
    Args:
        market: Market identifier
        days_ahead: Number of days to look ahead
    
    Returns:
        Dict with IPO calendar
    """
    cache_key = f"ipo_calendar:{market}:{days_ahead}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    try:
        # Placeholder structure - would need real IPO data source
        # In production, integrate with:
        # - NSE/BSE IPO data APIs
        # - SEBI IPO data
        # - Specialized financial data providers
        
        result = {
            "market": market,
            "upcoming_ipos": [],
            "recent_ipos": [],
            "note": "IPO data requires specialized data source integration",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Cache for 1 day
        cache.set(cache_key, result, ttl=86400)
        return result
        
    except Exception as e:
        logger.error("ipo_calendar_fetch_failed", market=market, error=str(e))
        return {
            "market": market,
            "upcoming_ipos": [],
            "error": str(e)
        }

