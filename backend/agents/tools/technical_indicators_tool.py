"""
=============================================================================
AI Hub - Technical Indicators Calculation Tool
=============================================================================
Calculates comprehensive technical indicators for stock analysis.

This tool computes:
- Exponential Moving Averages (EMA 9, 21, 50)
- Relative Strength Index (RSI)
- Moving Average Convergence Divergence (MACD)
- Bollinger Bands
- Overall trend analysis and trading signals

Dependencies:
- pandas-ta: For technical indicator calculations
- yfinance: For price data (via stock_price_tool)
=============================================================================
"""

from typing import Dict, Any
import pandas as pd
import numpy as np  # ← ADD THIS LINE
from langchain_core.tools import tool
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
import structlog
from datetime import datetime

from agents.tools.stock_price_tool import get_stock_price

logger = structlog.get_logger()


def convert_numpy_types(obj: Any) -> Any:
    """
    Convert numpy types to Python native types for msgpack serialization.
    
    LangGraph uses msgpack which doesn't support numpy types.
    This recursively converts numpy.float64, numpy.int64, etc. to float, int.
    
    Args:
        obj: Object potentially containing numpy types
    
    Returns:
        Object with numpy types converted to Python native types
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    return obj


@tool
async def calculate_technical_indicators(
    symbol: str,
    market: str = "india_nse",
    period: str = "3mo"
) -> Dict[str, Any]:
    """
    Calculate comprehensive technical analysis indicators for a stock.
    
    This function performs the following analysis:
    1. Fetches historical price data
    2. Calculates multiple technical indicators
    3. Determines overall trend and signals
    4. Provides actionable trading insights
    
    Args:
        symbol: Stock ticker symbol (e.g., "RELIANCE", "INFY")
        market: Market identifier (india_nse, india_bse, us_nyse, us_nasdaq)
        period: Historical data period (3mo, 6mo, 1y, etc.)
    
    Returns:
        Dict containing:
        - symbol: Stock ticker
        - analyzed_at: Timestamp of analysis
        - indicators: Dict with all technical indicators
            - ema: Exponential moving averages
            - rsi: Relative strength index
            - macd: MACD indicator
            - bollinger_bands: Bollinger bands data
            - summary: Overall analysis summary
    
    Example:
        >>> result = await calculate_technical_indicators("RELIANCE", "india_nse", "3mo")
        >>> print(result['indicators']['summary']['overall_signal'])
        'buy'
    """
    try:
        logger.info("calculating_technical_indicators", symbol=symbol)
        
        # Fetch price data using async invocation
        # IMPORTANT: Use .ainvoke() for async tools, not .invoke()
        price_data = await get_stock_price.ainvoke({
            "symbol": symbol,
            "market": market,
            "period": period
        })
        
        if "error" in price_data:
            logger.error("price_data_fetch_failed", symbol=symbol, error=price_data["error"])
            return price_data
        
        # Convert to pandas DataFrame for technical analysis
        df = pd.DataFrame(price_data['historical_data'])
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        df = df.sort_index()
        
        # Validate sufficient data
        if len(df) < 50:
            return {
                "error": f"Insufficient data (need at least 50 days, got {len(df)})",
                "symbol": symbol
            }
        
        indicators = {}
        current_price = df['close'].iloc[-1]
        
        # =================================================================
        # EMA (Exponential Moving Averages)
        # =================================================================
        ema_9 = EMAIndicator(close=df['close'], window=9).ema_indicator().iloc[-1]
        ema_21 = EMAIndicator(close=df['close'], window=21).ema_indicator().iloc[-1]
        ema_50 = EMAIndicator(close=df['close'], window=50).ema_indicator().iloc[-1]
        
        # Determine trend based on EMA alignment
        if current_price > ema_9 > ema_21 > ema_50:
            trend = "strong_uptrend"
        elif current_price > ema_21:
            trend = "uptrend"
        elif current_price < ema_9 < ema_21 < ema_50:
            trend = "strong_downtrend"
        elif current_price < ema_21:
            trend = "downtrend"
        else:
            trend = "sideways"
        
        indicators['ema'] = {
            "ema_9": round(ema_9, 2),
            "ema_21": round(ema_21, 2),
            "ema_50": round(ema_50, 2),
            "current_price": round(current_price, 2),
            "trend": trend,
            "signal": "bullish" if "uptrend" in trend else "bearish" if "downtrend" in trend else "neutral"
        }
        
        # =================================================================
        # RSI (Relative Strength Index)
        # =================================================================
        rsi_value = RSIIndicator(close=df['close'], window=14).rsi().iloc[-1]
        
        # Determine RSI signal
        if rsi_value > 70:
            rsi_signal = "overbought"
            rsi_interpretation = "Stock may be overvalued, potential pullback"
        elif rsi_value < 30:
            rsi_signal = "oversold"
            rsi_interpretation = "Stock may be undervalued, potential bounce"
        else:
            rsi_signal = "neutral"
            rsi_interpretation = "Stock is in normal trading range"
        
        indicators['rsi'] = {
            "value": round(rsi_value, 2),
            "signal": rsi_signal,
            "interpretation": rsi_interpretation
        }
        
        # =================================================================
        # MACD (Moving Average Convergence Divergence)
        # =================================================================
        macd = MACD(close=df['close'])
        macd_line = macd.macd().iloc[-1]
        signal_line = macd.macd_signal().iloc[-1]
        
        indicators['macd'] = {
            "macd_line": round(macd_line, 2),
            "signal_line": round(signal_line, 2),
            "signal": "bullish" if macd_line > signal_line else "bearish",
            "interpretation": "MACD above signal (bullish)" if macd_line > signal_line else "MACD below signal (bearish)"
        }
        
        # =================================================================
        # Bollinger Bands
        # =================================================================
        bb = BollingerBands(close=df['close'], window=20, window_dev=2)
        bb_upper = bb.bollinger_hband().iloc[-1]
        bb_lower = bb.bollinger_lband().iloc[-1]
        bb_middle = bb.bollinger_mavg().iloc[-1]
        
        # Determine Bollinger Band signal
        if current_price >= bb_upper:
            bb_signal = "overbought"
            bb_interpretation = "Price at upper band, potential reversal"
        elif current_price <= bb_lower:
            bb_signal = "oversold"
            bb_interpretation = "Price at lower band, potential bounce"
        else:
            bb_signal = "normal"
            bb_interpretation = "Price within normal range"
        
        indicators['bollinger_bands'] = {
            "upper_band": round(bb_upper, 2),
            "middle_band": round(bb_middle, 2),
            "lower_band": round(bb_lower, 2),
            "signal": bb_signal,
            "interpretation": bb_interpretation
        }
        
        # =================================================================
        # Overall Summary & Signal Generation
        # =================================================================
        # Count bullish and bearish signals
        bullish_count = sum([
            1 for ind in [indicators['ema'], indicators['rsi'], indicators['macd'], indicators['bollinger_bands']]
            if ind.get('signal') in ['bullish', 'oversold']
        ])
        
        bearish_count = sum([
            1 for ind in [indicators['ema'], indicators['rsi'], indicators['macd'], indicators['bollinger_bands']]
            if ind.get('signal') in ['bearish', 'overbought']
        ])
        
        # Determine overall signal
        if bullish_count >= 3:
            overall_signal = "buy"
        elif bearish_count >= 3:
            overall_signal = "sell"
        else:
            overall_signal = "hold"
        
        # Calculate confidence based on indicator agreement
        total_indicators = 4
        max_agreement = max(bullish_count, bearish_count)
        confidence = round((max_agreement / total_indicators) * 100, 2)
        
        indicators['summary'] = {
            "overall_signal": overall_signal,
            "bullish_indicators": bullish_count,
            "bearish_indicators": bearish_count,
            "neutral_indicators": total_indicators - bullish_count - bearish_count,
            "confidence": confidence,
            "recommendation": f"{overall_signal.upper()} with {confidence}% confidence based on {max_agreement}/{total_indicators} indicators"
        }
        
        logger.info(
            "technical_indicators_calculated",
            symbol=symbol,
            signal=overall_signal,
            confidence=confidence
        )
        
        # Convert numpy types before returning to avoid msgpack serialization errors
        return {
            "symbol": symbol,
            "analyzed_at": datetime.utcnow().isoformat(),
            "indicators": convert_numpy_types(indicators) 
        }
        
    except Exception as e:
        logger.error("technical_analysis_failed", symbol=symbol, error=str(e))
        return {
            "error": str(e),
            "symbol": symbol,
            "analyzed_at": datetime.utcnow().isoformat()
        }
