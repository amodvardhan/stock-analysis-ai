"""
=============================================================================
Corporate Actions Tool
=============================================================================
Tool for fetching corporate actions data.
Uses Yahoo Finance for corporate actions.
=============================================================================
"""

from typing import Dict, Any, List
from langchain_core.tools import tool
import structlog
from datetime import datetime, timedelta
import yfinance as yf
from fake_useragent import UserAgent

from core.redis_client import cache

logger = structlog.get_logger()
ua = UserAgent()


@tool
async def get_corporate_actions(
    symbol: str,
    market: str = "india_nse",
    action_type: str = "all"  # "dividend", "split", "all"
) -> Dict[str, Any]:
    """
    Fetch corporate actions for a stock.
    
    Args:
        symbol: Stock ticker symbol
        market: Market identifier
        action_type: Type of corporate action
    
    Returns:
        Dict with corporate actions data
    """
    cache_key = f"corporate_actions:{symbol}:{market}:{action_type}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    try:
        # Format symbol for market
        if market == "india_nse" and not symbol.endswith(".NS"):
            yahoo_symbol = f"{symbol}.NS"
        elif market == "india_bse" and not symbol.endswith(".BO"):
            yahoo_symbol = f"{symbol}.BO"
        else:
            yahoo_symbol = symbol
        
        ticker = yf.Ticker(yahoo_symbol)
        
        result = {
            "symbol": symbol,
            "market": market,
            "dividends": [],
            "splits": [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Get dividend history
        if action_type in ["dividend", "all"]:
            try:
                dividend_history = ticker.dividends
                if dividend_history is not None and not dividend_history.empty:
                    for date, amount in dividend_history.tail(20).items():  # Last 20 dividends
                        result["dividends"].append({
                            "date": date.strftime("%Y-%m-%d"),
                            "amount": float(amount),
                            "type": "dividend"
                        })
            except Exception as e:
                logger.warning("dividend_history_fetch_failed", symbol=yahoo_symbol, error=str(e))
        
        # Get stock split history
        if action_type in ["split", "all"]:
            try:
                split_history = ticker.splits
                if split_history is not None and not split_history.empty:
                    for date, ratio in split_history.tail(20).items():  # Last 20 splits
                        result["splits"].append({
                            "date": date.strftime("%Y-%m-%d"),
                            "ratio": float(ratio),
                            "type": "split",
                            "description": f"{ratio}:1 split"
                        })
            except Exception as e:
                logger.warning("split_history_fetch_failed", symbol=yahoo_symbol, error=str(e))
        
        # Get upcoming events from info
        try:
            info = ticker.info
            # Check for ex-dividend date
            ex_dividend_date = info.get('exDividendDate')
            if ex_dividend_date:
                result["upcoming_dividend"] = {
                    "ex_date": datetime.fromtimestamp(ex_dividend_date).strftime("%Y-%m-%d") if isinstance(ex_dividend_date, (int, float)) else str(ex_dividend_date),
                    "amount": info.get('dividendRate', 0)
                }
        except Exception as e:
            logger.warning("upcoming_events_fetch_failed", symbol=yahoo_symbol, error=str(e))
        
        # Sort by date (most recent first)
        result["dividends"].sort(key=lambda x: x["date"], reverse=True)
        result["splits"].sort(key=lambda x: x["date"], reverse=True)
        
        # Cache for 1 hour
        cache.set(cache_key, result, ttl=3600)
        return result
        
    except Exception as e:
        logger.error("corporate_actions_fetch_failed", symbol=symbol, error=str(e))
        return {
            "symbol": symbol,
            "error": str(e),
            "dividends": [],
            "splits": []
        }

