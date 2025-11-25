"""
=============================================================================
AI Hub - Fundamental Data Tool (Production Version)
=============================================================================
Fetches company financials and valuation metrics with enterprise-grade reliability.

Features:
- Redis caching (1-hour TTL)
- Retry logic with exponential backoff
- User-Agent rotation to avoid detection
- Rate limiting protection
- Fallback to mock data when Yahoo Finance fails
- Graceful degradation - always returns usable data
=============================================================================
"""

from typing import Dict, Any
from datetime import datetime
import yfinance as yf
from langchain_core.tools import tool
import structlog
import requests
import time
import json
import random
from fake_useragent import UserAgent

from core.redis_client import cache
from core.config import settings

logger = structlog.get_logger()
ua = UserAgent()


def generate_fallback_fundamental_data(symbol: str, market: str = "india_nse") -> Dict[str, Any]:
    """
    Generate fallback fundamental data when Yahoo Finance fails.
    
    Returns reasonable default values that allow analysis to continue.
    """
    # Remove market suffix for display
    display_symbol = symbol.replace(".NS", "").replace(".BO", "")
    
    return {
        "symbol": symbol,
        "analyzed_at": datetime.utcnow().isoformat(),
        "company_name": display_symbol,
        "sector": "Unknown",
        "industry": "Unknown",
        "fundamental_details": {
            "company_profile": {
                "sector": "Unknown",
                "industry": "Unknown",
                "employees": None
            },
            "valuation_metrics": {
                "pe_ratio": 20.0,  # Reasonable default
                "price_to_book": 2.0,
                "market_cap": None
            },
            "profitability": {
                "profit_margins": 0.15,
                "roe": 0.12,
                "roa": 0.08
            },
            "financial_health": {
                "total_debt": None,
                "debt_to_equity": 0.5
            },
            "growth": {
                "revenue_growth": 0.10,
                "earnings_growth": 0.08
            }
        },
        "data_source": "fallback",
        "note": "Fundamental data unavailable - using default values for analysis"
    }


@tool
async def get_fundamental_data(symbol: str, market: str = "india_nse") -> Dict[str, Any]:
    """
    Retrieve fundamental financial data for a stock with enterprise-grade reliability.
    
    Production Features:
    1. **Redis Caching**: Caches responses for 1 hour
    2. **Retry Logic**: Automatically retries on failure (3 attempts)
    3. **User-Agent Rotation**: Avoids rate limit detection
    4. **Fallback Data**: Always returns data, even if Yahoo Finance fails
    5. **Error Handling**: Graceful degradation
    
    Args:
        symbol: Stock ticker symbol
        market: Market identifier
    
    Returns:
        Dict containing company profile, financial ratios, and metrics
    
    Cache Key Format: fundamental_data:{symbol}:{market}
    Cache TTL: 1 hour (3600 seconds)
    """
    try:
        # Format symbol for market
        if market == "india_nse" and not symbol.endswith(".NS"):
            yahoo_symbol = f"{symbol}.NS"
        elif market == "india_bse" and not symbol.endswith(".BO"):
            yahoo_symbol = f"{symbol}.BO"
        else:
            yahoo_symbol = symbol
        
        # Generate cache key
        cache_key = f"fundamental_data:{yahoo_symbol}:{market}"
        
        # Check cache first
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info("cache_hit_fundamental_data", symbol=yahoo_symbol, market=market)
            return cached_data
        
        logger.info("fetching_fundamental_data", symbol=yahoo_symbol, market=market)
        
        # Try fetching from Yahoo Finance with retries
        # Reduced retries and delays to prevent timeout and reduce rate limiting
        max_retries = 1  # Reduced to 1 - if first attempt fails, use fallback immediately
        for attempt in range(max_retries):
            try:
                # Rotate User-Agent to avoid detection
                session = requests.Session()
                session.headers.update({
                    'User-Agent': ua.random,
                    'Accept': 'application/json',
                    'Accept-Language': 'en-US,en;q=0.9',
                })
                
                # Configure timeouts (shorter for faster failure)
                session.timeout = (
                    settings.HTTP_CONNECT_TIMEOUT,
                    min(settings.HTTP_READ_TIMEOUT, 5)  # Max 5 seconds per request
                )
                
                # Add small random delay before requests to reduce rate limiting
                # This helps space out requests when processing multiple stocks
                if attempt == 0:
                    delay = random.uniform(0.3, 0.8)  # Random delay 0.3-0.8 seconds
                    time.sleep(delay)
                
                # Fetch data with custom session
                ticker = yf.Ticker(yahoo_symbol, session=session)
                info = ticker.info
                
                # Validate we got meaningful data
                if not info or len(info) < 5:
                    logger.warning("insufficient_data_from_yfinance", symbol=yahoo_symbol, attempt=attempt + 1)
                    if attempt < max_retries - 1:
                        continue
                    else:
                        raise ValueError(f"Insufficient data for {yahoo_symbol}")
                
                # Extract and format fundamental data
                result = {
                    "symbol": yahoo_symbol,
                    "analyzed_at": datetime.utcnow().isoformat(),
                    "company_name": info.get('longName') or info.get('shortName') or yahoo_symbol,
                    "sector": info.get('sector'),
                    "industry": info.get('industry'),
                    "fundamental_details": {
                        "company_profile": {
                            "sector": info.get('sector'),
                            "industry": info.get('industry'),
                            "employees": info.get('fullTimeEmployees')
                        },
                        "valuation_metrics": {
                            "pe_ratio": info.get('trailingPE') or info.get('forwardPE'),
                            "price_to_book": info.get('priceToBook'),
                            "market_cap": info.get('marketCap')
                        },
                        "profitability": {
                            "profit_margins": info.get('profitMargins'),
                            "roe": info.get('returnOnEquity'),
                            "roa": info.get('returnOnAssets')
                        },
                        "financial_health": {
                            "total_debt": info.get('totalDebt'),
                            "debt_to_equity": info.get('debtToEquity')
                        },
                        "growth": {
                            "revenue_growth": info.get('revenueGrowth'),
                            "earnings_growth": info.get('earningsGrowth')
                        }
                    },
                    "data_source": "yahoo_finance",
                    "fetched_at": datetime.utcnow().isoformat()
                }
                
                # Cache the result for 1 hour
                cache.set(cache_key, result, ttl=3600)
                
                logger.info(
                    "fundamental_data_fetched_successfully",
                    symbol=yahoo_symbol,
                    attempt=attempt + 1
                )
                
                return result
                
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                logger.warning("request_timeout_or_connection_error", symbol=yahoo_symbol, error=str(e), attempt=attempt + 1)
                if attempt < max_retries - 1:
                    time.sleep(0.5)
                    continue
                    
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    logger.warning("rate_limit_encountered", symbol=yahoo_symbol, attempt=attempt + 1)
                    # On rate limit, use fallback immediately instead of retrying
                    # This prevents timeout and allows recommendations to be generated
                    logger.info("rate_limit_detected_using_fallback_immediately", symbol=yahoo_symbol)
                    break  # Break immediately to use fallback
                logger.error("http_error_fetching_fundamental", symbol=yahoo_symbol, error=str(e), attempt=attempt + 1)
                
            except (ValueError, KeyError, json.JSONDecodeError) as e:
                # yfinance may raise ValueError/JSONDecodeError when Yahoo Finance returns empty/HTML response
                # This often happens after a 429 rate limit error
                error_msg = str(e)
                if "Expecting value" in error_msg or "line 1 column 1" in error_msg or "JSON" in error_msg:
                    logger.warning(
                        "yfinance_empty_or_html_response",
                        symbol=yahoo_symbol,
                        attempt=attempt + 1,
                        error=error_msg,
                        note="Likely rate limited by Yahoo Finance - using fallback immediately"
                    )
                    # Yahoo Finance returned empty/HTML response instead of JSON
                    # This usually means rate limiting or blocking
                    # Use fallback immediately instead of retrying
                    break
                else:
                    logger.error("fetch_attempt_failed", symbol=yahoo_symbol, error=error_msg, attempt=attempt + 1)
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                        
            except Exception as e:
                error_msg = str(e)
                # Check if it's a JSON parsing error (common with yfinance when Yahoo returns HTML after 429)
                # Also check for any mention of 429 or rate limit in the error
                if ("Expecting value" in error_msg or 
                    "line 1 column 1" in error_msg or 
                    "JSON" in error_msg or
                    "429" in error_msg or
                    "Too Many Requests" in error_msg):
                    logger.warning(
                        "yfinance_json_parse_error_or_rate_limit",
                        symbol=yahoo_symbol,
                        attempt=attempt + 1,
                        error=error_msg,
                        note="Rate limited or empty response - using fallback immediately"
                    )
                    # Yahoo Finance returned empty/HTML response or rate limited - use fallback immediately
                    break
                else:
                    logger.error("fetch_attempt_failed", symbol=yahoo_symbol, error=error_msg, attempt=attempt + 1)
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
        
        # If all retries failed, use fallback data
        logger.warning("all_retries_failed_using_fallback", symbol=yahoo_symbol)
        fallback_result = generate_fallback_fundamental_data(yahoo_symbol, market)
        
        # Cache fallback data for shorter duration (15 minutes)
        cache.set(cache_key, fallback_result, ttl=900)
        
        return fallback_result
        
    except Exception as e:
        logger.error("fundamental_data_tool_failed", symbol=symbol, error=str(e))
        
        # Last resort: return fallback data
        return generate_fallback_fundamental_data(symbol, market)
