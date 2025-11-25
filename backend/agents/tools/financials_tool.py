"""
=============================================================================
Financial Statements Tool
=============================================================================
Tool for fetching detailed financial statements.
Uses Yahoo Finance for financial data.
=============================================================================
"""

from typing import Dict, Any, Optional
from langchain_core.tools import tool
import structlog
from datetime import datetime
import yfinance as yf
import pandas as pd
from fake_useragent import UserAgent

from core.redis_client import cache

logger = structlog.get_logger()
ua = UserAgent()


@tool
async def get_financial_statements(
    symbol: str,
    market: str = "india_nse",
    statement_type: str = "all"  # "income", "balance", "cashflow", "all"
) -> Dict[str, Any]:
    """
    Fetch detailed financial statements.
    
    Args:
        symbol: Stock ticker symbol
        market: Market identifier
        statement_type: Type of statement to fetch
    
    Returns:
        Dict with financial statements
    """
    cache_key = f"financial_statements:{symbol}:{market}:{statement_type}"
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
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Get income statement
        if statement_type in ["income", "all"]:
            try:
                income_stmt = ticker.financials
                if income_stmt is not None and not income_stmt.empty:
                    result["income_statement"] = _format_dataframe(income_stmt)
            except Exception as e:
                logger.warning("income_statement_fetch_failed", symbol=yahoo_symbol, error=str(e))
                result["income_statement"] = None
        
        # Get balance sheet
        if statement_type in ["balance", "all"]:
            try:
                balance_sheet = ticker.balance_sheet
                if balance_sheet is not None and not balance_sheet.empty:
                    result["balance_sheet"] = _format_dataframe(balance_sheet)
            except Exception as e:
                logger.warning("balance_sheet_fetch_failed", symbol=yahoo_symbol, error=str(e))
                result["balance_sheet"] = None
        
        # Get cash flow
        if statement_type in ["cashflow", "all"]:
            try:
                cashflow = ticker.cashflow
                if cashflow is not None and not cashflow.empty:
                    result["cashflow_statement"] = _format_dataframe(cashflow)
            except Exception as e:
                logger.warning("cashflow_fetch_failed", symbol=yahoo_symbol, error=str(e))
                result["cashflow_statement"] = None
        
        # Get quarterly data
        if statement_type == "all":
            try:
                quarterly_income = ticker.quarterly_financials
                if quarterly_income is not None and not quarterly_income.empty:
                    result["quarterly_income"] = _format_dataframe(quarterly_income)
            except Exception as e:
                logger.warning("quarterly_financials_fetch_failed", symbol=yahoo_symbol, error=str(e))
        
        # Get key financial ratios
        try:
            info = ticker.info
            result["key_ratios"] = {
                "pe_ratio": info.get('trailingPE') or info.get('forwardPE'),
                "price_to_book": info.get('priceToBook'),
                "price_to_sales": info.get('priceToSalesTrailing12Months'),
                "debt_to_equity": info.get('debtToEquity'),
                "current_ratio": info.get('currentRatio'),
                "quick_ratio": info.get('quickRatio'),
                "roe": info.get('returnOnEquity'),
                "roa": info.get('returnOnAssets'),
                "profit_margin": info.get('profitMargins'),
                "operating_margin": info.get('operatingMargins'),
                "revenue_growth": info.get('revenueGrowth'),
                "earnings_growth": info.get('earningsGrowth')
            }
        except Exception as e:
            logger.warning("key_ratios_fetch_failed", symbol=yahoo_symbol, error=str(e))
            result["key_ratios"] = {}
        
        # Cache for 1 hour
        cache.set(cache_key, result, ttl=3600)
        return result
        
    except Exception as e:
        logger.error("financial_statements_fetch_failed", symbol=symbol, error=str(e))
        return {
            "symbol": symbol,
            "error": str(e),
            "income_statement": None,
            "balance_sheet": None,
            "cashflow_statement": None
        }
    
def _format_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
        """Convert DataFrame to JSON-serializable format."""
        if df is None or df.empty:
            return {}
        
        # Convert to dict with dates as strings
        result = {}
        for col in df.columns:
            result[str(col)] = {}
            for idx, val in df[col].items():
                if pd.notna(val):
                    result[str(col)][str(idx)] = float(val) if isinstance(val, (int, float)) else str(val)
        
        return result

