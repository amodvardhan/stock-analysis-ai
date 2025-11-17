"""
Fundamental Data Tool
Fetches company financials and valuation metrics.
"""

from typing import Dict, Any
from datetime import datetime
import yfinance as yf
from langchain_core.tools import tool
import structlog

logger = structlog.get_logger()


@tool
async def get_fundamental_data(symbol: str, market: str = "india_nse") -> Dict[str, Any]:
    """
    Retrieve fundamental financial data for a stock.
    
    Args:
        symbol: Stock ticker symbol
        market: Market identifier
    
    Returns:
        Dict containing company profile, financial ratios, and metrics
    """
    try:
        if market == "india_nse" and not symbol.endswith(".NS"):
            symbol = f"{symbol}.NS"
        elif market == "india_bse" and not symbol.endswith(".BO"):
            symbol = f"{symbol}.BO"
        
        logger.info("fetching_fundamental_data", symbol=symbol)
        
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return {
            "symbol": symbol,
            "analyzed_at": datetime.utcnow().isoformat(),
            "company_name": info.get('longName', symbol),
            "sector": info.get('sector'),
            "industry": info.get('industry'),
            "fundamental_details": {
                "company_profile": {
                    "sector": info.get('sector'),
                    "industry": info.get('industry'),
                    "employees": info.get('fullTimeEmployees')
                },
                "valuation": {
                    "pe_ratio": info.get('trailingPE'),
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
            }
        }
        
    except Exception as e:
        logger.error("fundamental_data_failed", symbol=symbol, error=str(e))
        return {"error": str(e), "symbol": symbol}
