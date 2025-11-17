"""
Stock Price Fetching Tool
Fetches current and historical stock prices using yfinance.
"""

from typing import Dict, Any
from datetime import datetime
import yfinance as yf
from langchain_core.tools import tool
import structlog

logger = structlog.get_logger()


@tool
async def get_stock_price(
    symbol: str,
    market: str = "india_nse",
    period: str = "1mo"
) -> Dict[str, Any]:
    """
    Fetch current and historical stock price data.
    
    Args:
        symbol: Stock ticker symbol (e.g., "RELIANCE", "AAPL")
        market: Market identifier (india_nse, india_bse, us_nyse, us_nasdaq)
        period: Historical data period (1d, 5d, 1mo, 3mo, 6mo, 1y)
    
    Returns:
        Dict containing:
        - current_price: Latest stock price
        - previous_close: Previous day's closing price
        - price_change: Absolute price change
        - price_change_percent: Percentage price change
        - volume: Trading volume
        - market_cap: Market capitalization
        - historical_data: List of OHLCV data points
    """
    try:
        # Add market suffix to symbol
        if market == "india_nse" and not symbol.endswith(".NS"):
            symbol = f"{symbol}.NS"
        elif market == "india_bse" and not symbol.endswith(".BO"):
            symbol = f"{symbol}.BO"
        
        logger.info("fetching_stock_price", symbol=symbol, market=market)
        
        # Fetch data
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period=period)
        
        if hist.empty:
            return {
                "error": f"No data found for {symbol}",
                "symbol": symbol,
                "market": market
            }
        
        # Calculate metrics
        current_price = hist['Close'].iloc[-1]
        previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        price_change = current_price - previous_close
        price_change_percent = (price_change / previous_close * 100) if previous_close else 0
        
        # Convert historical data
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
            "market": market,
            "current_price": round(current_price, 2),
            "previous_close": round(previous_close, 2),
            "price_change": round(price_change, 2),
            "price_change_percent": round(price_change_percent, 2),
            "volume": int(hist['Volume'].iloc[-1]),
            "market_cap": info.get('marketCap'),
            "52_week_high": info.get('fiftyTwoWeekHigh'),
            "52_week_low": info.get('fiftyTwoWeekLow'),
            "pe_ratio": info.get('trailingPE'),
            "historical_data": historical_data[-30:],  # Last 30 days
            "data_points": len(historical_data)
        }
        
        logger.info("stock_price_fetched", symbol=symbol, price=current_price)
        return result
        
    except Exception as e:
        logger.error("stock_price_fetch_failed", symbol=symbol, error=str(e))
        return {
            "error": f"Failed to fetch stock price: {str(e)}",
            "symbol": symbol,
            "market": market
        }
