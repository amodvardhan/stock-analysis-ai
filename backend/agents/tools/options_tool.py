"""
=============================================================================
Options Chain Tool
=============================================================================
Tool for fetching options chain data.
Uses Yahoo Finance for options data.
=============================================================================
"""

from typing import Dict, Any, List, Optional
from langchain_core.tools import tool
import structlog
from datetime import datetime
import yfinance as yf
import requests
from fake_useragent import UserAgent

from core.redis_client import cache

logger = structlog.get_logger()
ua = UserAgent()


@tool
async def get_options_chain(
    symbol: str,
    market: str = "india_nse",
    expiration_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch options chain data for a stock.
    
    Args:
        symbol: Stock ticker symbol
        market: Market identifier
        expiration_date: Expiration date (YYYY-MM-DD), optional
    
    Returns:
        Dict with options chain data including calls and puts
    """
    cache_key = f"options_chain:{symbol}:{market}:{expiration_date or 'latest'}"
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
        
        # Get options expiration dates
        try:
            expirations = ticker.options
        except Exception as e:
            logger.warning("options_expirations_fetch_failed", symbol=yahoo_symbol, error=str(e))
            return {
                "symbol": symbol,
                "error": "Options data not available for this symbol",
                "calls": [],
                "puts": []
            }
        
        if not expirations or len(expirations) == 0:
            return {
                "symbol": symbol,
                "error": "No options available for this symbol",
                "calls": [],
                "puts": []
            }
        
        # Use specified expiration or latest
        expiration = expiration_date if expiration_date else expirations[0]
        
        # Get options chain
        try:
            opt_chain = ticker.option_chain(expiration)
            
            # Format calls
            calls = []
            if hasattr(opt_chain, 'calls') and opt_chain.calls is not None:
                for _, row in opt_chain.calls.iterrows():
                    calls.append({
                        "strike": float(row.get('strike', 0)),
                        "last_price": float(row.get('lastPrice', 0)),
                        "bid": float(row.get('bid', 0)),
                        "ask": float(row.get('ask', 0)),
                        "volume": int(row.get('volume', 0)),
                        "open_interest": int(row.get('openInterest', 0)),
                        "implied_volatility": float(row.get('impliedVolatility', 0)) if row.get('impliedVolatility') else 0,
                        "in_the_money": bool(row.get('inTheMoney', False))
                    })
            
            # Format puts
            puts = []
            if hasattr(opt_chain, 'puts') and opt_chain.puts is not None:
                for _, row in opt_chain.puts.iterrows():
                    puts.append({
                        "strike": float(row.get('strike', 0)),
                        "last_price": float(row.get('lastPrice', 0)),
                        "bid": float(row.get('bid', 0)),
                        "ask": float(row.get('ask', 0)),
                        "volume": int(row.get('volume', 0)),
                        "open_interest": int(row.get('openInterest', 0)),
                        "implied_volatility": float(row.get('impliedVolatility', 0)) if row.get('impliedVolatility') else 0,
                        "in_the_money": bool(row.get('inTheMoney', False))
                    })
            
            # Get current stock price for reference
            try:
                info = ticker.info
                current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            except:
                hist = ticker.history(period="1d")
                current_price = float(hist['Close'].iloc[-1]) if not hist.empty else 0
            
            result = {
                "symbol": symbol,
                "market": market,
                "current_price": round(current_price, 2),
                "expiration_date": expiration,
                "available_expirations": list(expirations)[:10],  # Limit to 10
                "calls": calls,
                "puts": puts,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Cache for 5 minutes
            cache.set(cache_key, result, ttl=300)
            return result
            
        except Exception as e:
            logger.error("options_chain_fetch_failed", symbol=yahoo_symbol, expiration=expiration, error=str(e))
            return {
                "symbol": symbol,
                "error": f"Failed to fetch options chain: {str(e)}",
                "calls": [],
                "puts": []
            }
            
    except Exception as e:
        logger.error("options_tool_failed", symbol=symbol, error=str(e))
        return {
            "symbol": symbol,
            "error": str(e),
            "calls": [],
            "puts": []
        }

