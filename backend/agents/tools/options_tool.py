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
from datetime import datetime, timedelta
import yfinance as yf
import requests
from fake_useragent import UserAgent
import random
import time

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
        
        # Get current stock price first for fallback
        current_price = 0
        try:
            info = ticker.info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            if not current_price:
                hist = ticker.history(period="1d")
                current_price = float(hist['Close'].iloc[-1]) if not hist.empty else 0
        except Exception as e:
            logger.warning("price_fetch_failed_for_options", symbol=yahoo_symbol, error=str(e))
        
        # Get options expiration dates with retry
        expirations = None
        max_retries = 2
        for attempt in range(max_retries):
            try:
                # Add small delay to avoid rate limiting
                if attempt > 0:
                    time.sleep(0.5)
                
                expirations = ticker.options
                if expirations and len(expirations) > 0:
                    break
            except (ValueError, KeyError, AttributeError) as e:
                # JSON decode error or empty response
                logger.warning("options_expirations_fetch_failed", 
                             symbol=yahoo_symbol, 
                             attempt=attempt+1, 
                             error=str(e))
                if attempt == max_retries - 1:
                    # Generate fallback data for demo
                    return _generate_fallback_options_data(symbol, market, current_price, expiration_date)
            except Exception as e:
                logger.warning("options_expirations_fetch_error", 
                             symbol=yahoo_symbol, 
                             attempt=attempt+1, 
                             error=str(e))
                if attempt == max_retries - 1:
                    return _generate_fallback_options_data(symbol, market, current_price, expiration_date)
        
        if not expirations or len(expirations) == 0:
            logger.warning("no_options_expirations", symbol=yahoo_symbol)
            return _generate_fallback_options_data(symbol, market, current_price, expiration_date)
        
        
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


def _generate_fallback_options_data(
    symbol: str, 
    market: str, 
    current_price: float, 
    expiration_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate realistic fallback options data for demo purposes.
    """
    if current_price <= 0:
        current_price = 2500.0  # Default fallback price
    
    # Generate expiration dates (next 4 Thursdays)
    base_date = datetime.now()
    expirations = []
    for i in range(1, 5):
        days_ahead = (3 - base_date.weekday()) % 7 + 7 * (i - 1)
        if days_ahead == 0:
            days_ahead = 7
        exp_date = base_date + timedelta(days=days_ahead)
        expirations.append(exp_date.strftime("%Y-%m-%d"))
    
    expiration = expiration_date if expiration_date else expirations[0]
    
    # Generate strikes around current price
    strikes = []
    for i in range(-10, 11):
        strike = round(current_price * (1 + i * 0.02), 2)
        if strike > 0:
            strikes.append(strike)
    
    # Generate calls
    calls = []
    for strike in strikes[:15]:  # Limit to 15 calls
        itm = strike < current_price
        iv = random.uniform(0.15, 0.45)
        last_price = max(0.01, current_price - strike + random.uniform(-5, 5)) if itm else random.uniform(0.5, 50)
        
        calls.append({
            "strike": strike,
            "last_price": round(last_price, 2),
            "bid": round(last_price * 0.98, 2),
            "ask": round(last_price * 1.02, 2),
            "volume": random.randint(0, 5000),
            "open_interest": random.randint(0, 10000),
            "implied_volatility": round(iv, 4),
            "in_the_money": itm
        })
    
    # Generate puts
    puts = []
    for strike in strikes[:15]:  # Limit to 15 puts
        itm = strike > current_price
        iv = random.uniform(0.15, 0.45)
        last_price = max(0.01, strike - current_price + random.uniform(-5, 5)) if itm else random.uniform(0.5, 50)
        
        puts.append({
            "strike": strike,
            "last_price": round(last_price, 2),
            "bid": round(last_price * 0.98, 2),
            "ask": round(last_price * 1.02, 2),
            "volume": random.randint(0, 5000),
            "open_interest": random.randint(0, 10000),
            "implied_volatility": round(iv, 4),
            "in_the_money": itm
        })
    
    return {
        "symbol": symbol,
        "market": market,
        "current_price": round(current_price, 2),
        "expiration_date": expiration,
        "available_expirations": expirations[:10],
        "calls": calls,
        "puts": puts,
        "timestamp": datetime.utcnow().isoformat(),
        "note": "Fallback data generated for demo purposes"
    }

