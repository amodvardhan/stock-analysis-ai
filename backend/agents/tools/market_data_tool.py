"""
=============================================================================
Market Data Tool
=============================================================================
Tool for fetching real market data including:
- Market indices
- Top gainers/losers
- Sector performance
- Market statistics
=============================================================================
"""

from typing import Dict, Any, List
import yfinance as yf
from langchain_core.tools import tool
import structlog
from datetime import datetime
import requests
from fake_useragent import UserAgent

from core.redis_client import cache
from agents.tools.stock_price_tool import get_stock_price

logger = structlog.get_logger()
ua = UserAgent()


@tool
async def get_market_indices(market: str = "india_nse") -> Dict[str, Any]:
    """
    Get real market indices data.
    
    Args:
        market: Market identifier
    
    Returns:
        Dict with indices performance
    """
    cache_key = f"market_indices:{market}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    try:
        # Map market to indices
        indices_map = {
            "india_nse": {
                "NIFTY 50": "^NSEI",
                "NIFTY BANK": "^NSEBANK",
                "NIFTY IT": "^CNXIT",
                "NIFTY AUTO": "^CNXAUTO"
            },
            "india_bse": {
                "SENSEX": "^BSESN",
                "BSE BANKEX": "^BSBANK",
                "BSE IT": "^BSIT",
                "BSE AUTO": "^BSAUTO"
            },
            "us_nyse": {
                "DJIA": "^DJI",
                "S&P 500": "^GSPC",
                "NYSE COMPOSITE": "^NYA"
            },
            "us_nasdaq": {
                "NASDAQ": "^IXIC",
                "NASDAQ 100": "^NDX",
                "NASDAQ COMPOSITE": "^IXIC"
            }
        }
        
        indices_symbols = indices_map.get(market, {})
        indices_data = {}
        
        for index_name, yahoo_symbol in indices_symbols.items():
            try:
                ticker = yf.Ticker(yahoo_symbol)
                hist = ticker.history(period="2d")
                info = ticker.info
                
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    previous = hist['Close'].iloc[-2] if len(hist) > 1 else current
                    change = current - previous
                    change_percent = (change / previous * 100) if previous > 0 else 0
                    
                    indices_data[index_name] = {
                        "value": round(float(current), 2),
                        "change": round(float(change), 2),
                        "change_percent": round(float(change_percent), 2),
                        "status": "active"
                    }
                else:
                    indices_data[index_name] = {
                        "value": 0,
                        "change": 0,
                        "change_percent": 0,
                        "status": "unavailable"
                    }
            except Exception as e:
                logger.warning("index_fetch_failed", index=index_name, error=str(e))
                indices_data[index_name] = {
                    "value": 0,
                    "change": 0,
                    "change_percent": 0,
                    "status": "error"
                }
        
        result = {
            "market": market,
            "indices": indices_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        cache.set(cache_key, result, ttl=300)  # 5 minutes
        return result
        
    except Exception as e:
        logger.error("market_indices_fetch_failed", market=market, error=str(e))
        return {
            "market": market,
            "indices": {},
            "error": str(e)
        }


@tool
async def get_top_gainers_losers(market: str = "india_nse", limit: int = 20) -> Dict[str, Any]:
    """
    Get top gainers and losers for a market.
    
    Note: Yahoo Finance doesn't have a direct API for this.
    We'll use a list of popular stocks and calculate their performance.
    
    Args:
        market: Market identifier
        limit: Number of stocks to return
    
    Returns:
        Dict with gainers and losers
    """
    cache_key = f"market_movers:{market}:{limit}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    try:
        # Popular stocks for each market
        popular_stocks = {
            "india_nse": [
                "RELIANCE", "TCS", "HDFCBANK", "INFY", "HINDUNILVR",
                "ICICIBANK", "BHARTIARTL", "SBIN", "BAJFINANCE", "LICI",
                "ITC", "LT", "HCLTECH", "AXISBANK", "KOTAKBANK",
                "ASIANPAINT", "MARUTI", "TITAN", "NESTLEIND", "ULTRACEMCO"
            ],
            "india_bse": [
                "RELIANCE", "TCS", "HDFCBANK", "INFY", "HINDUNILVR"
            ],
            "us_nyse": [
                "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
                "META", "NVDA", "JPM", "V", "JNJ"
            ],
            "us_nasdaq": [
                "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
                "META", "NVDA", "AMD", "INTC", "ADBE"
            ]
        }
        
        stocks = popular_stocks.get(market, [])[:limit * 2]  # Get more to filter
        
        gainers = []
        losers = []
        all_data = []
        
        for symbol in stocks:
            try:
                price_data = await get_stock_price(symbol=symbol, market=market, period="2d")
                
                if price_data and price_data.get("current_price") and price_data.get("change_percent") is not None:
                    all_data.append({
                        "symbol": symbol,
                        "company_name": symbol,  # Would need to fetch from fundamental data
                        "current_price": price_data["current_price"],
                        "previous_close": price_data.get("previous_close", price_data["current_price"]),
                        "change": price_data.get("change", 0),
                        "change_percent": price_data["change_percent"],
                        "volume": 0  # Would need to fetch separately
                    })
            except Exception as e:
                logger.warning("stock_data_fetch_failed", symbol=symbol, error=str(e))
                continue
        
        # Sort by change_percent
        all_data.sort(key=lambda x: x.get("change_percent", 0), reverse=True)
        
        gainers = all_data[:limit]
        losers = list(reversed(all_data[-limit:])) if len(all_data) >= limit else []
        
        result = {
            "market": market,
            "gainers": gainers,
            "losers": losers,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        cache.set(cache_key, result, ttl=300)  # 5 minutes
        return result
        
    except Exception as e:
        logger.error("market_movers_fetch_failed", market=market, error=str(e))
        return {
            "market": market,
            "gainers": [],
            "losers": [],
            "error": str(e)
        }


@tool
async def get_sector_performance(market: str = "india_nse") -> Dict[str, Any]:
    """
    Get sector-wise performance.
    
    Args:
        market: Market identifier
    
    Returns:
        Dict with sector performance
    """
    cache_key = f"sector_performance:{market}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    try:
        # Sector-wise stock mapping (simplified - in production, use proper sector classification)
        sector_stocks = {
            "Banking": ["HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK"],
            "IT": ["TCS", "INFY", "HCLTECH", "WIPRO", "TECHM"],
            "Pharma": ["SUNPHARMA", "DRREDDY", "CIPLA", "LUPIN", "DIVISLAB"],
            "Auto": ["MARUTI", "M&M", "TATAMOTORS", "BAJAJ-AUTO", "HEROMOTOCO"],
            "FMCG": ["HINDUNILVR", "ITC", "NESTLEIND", "BRITANNIA", "DABUR"],
            "Energy": ["RELIANCE", "ONGC", "IOC", "BPCL", "HPCL"],
            "Metals": ["TATASTEEL", "JSWSTEEL", "HINDALCO", "VEDL", "NMDC"],
            "Real Estate": ["DLF", "GODREJPROP", "OBEROIRLTY", "PRESTIGE", "SOBHA"],
            "Telecom": ["BHARTIARTL", "IDEA", "RCOM"],
            "Media": ["ZEE", "SUNTV", "NETWORK18"]
        }
        
        sectors_data = {}
        
        for sector, stocks in sector_stocks.items():
            sector_changes = []
            sector_volume = 0
            
            for symbol in stocks[:3]:  # Sample 3 stocks per sector
                try:
                    price_data = await get_stock_price(symbol=symbol, market=market, period="2d")
                    if price_data and price_data.get("change_percent") is not None:
                        sector_changes.append(price_data["change_percent"])
                except Exception as e:
                    logger.warning("sector_stock_fetch_failed", sector=sector, symbol=symbol, error=str(e))
                    continue
            
            avg_change = sum(sector_changes) / len(sector_changes) if sector_changes else 0
            
            sectors_data[sector] = {
                "performance": avg_change,
                "top_gainers": [],
                "top_losers": [],
                "avg_change": round(avg_change, 2)
            }
        
        result = {
            "market": market,
            "sectors": sectors_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        cache.set(cache_key, result, ttl=600)  # 10 minutes
        return result
        
    except Exception as e:
        logger.error("sector_performance_fetch_failed", market=market, error=str(e))
        return {
            "market": market,
            "sectors": {},
            "error": str(e)
        }

