"""
Technical Indicators Calculation Tool
Calculates RSI, MACD, Bollinger Bands, EMA, and other technical indicators.
"""

from typing import Dict, Any
from datetime import datetime
import pandas as pd
from langchain_core.tools import tool
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
import structlog

from agents.tools.stock_price_tool import get_stock_price

logger = structlog.get_logger()


@tool
async def calculate_technical_indicators(
    symbol: str,
    market: str = "india_nse",
    period: str = "3mo"
) -> Dict[str, Any]:
    """
    Calculate comprehensive technical analysis indicators.
    
    Computes:
    - Moving Averages (EMA 9, 21, 50)
    - RSI (Relative Strength Index)
    - MACD (Moving Average Convergence Divergence)
    - Bollinger Bands
    - Overall trend and signals
    
    Args:
        symbol: Stock ticker symbol
        market: Market identifier
        period: Historical period (minimum 3mo recommended)
    
    Returns:
        Dict containing all technical indicators and signals
    """
    try:
        logger.info("calculating_technical_indicators", symbol=symbol)
        
        # Get price data
        price_data = await get_stock_price(symbol, market, period)
        
        if "error" in price_data:
            return price_data
        
        # Convert to DataFrame
        df = pd.DataFrame(price_data['historical_data'])
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        
        if len(df) < 50:
            return {
                "error": "Insufficient data (need at least 50 days)",
                "symbol": symbol
            }
        
        indicators = {}
        current_price = df['close'].iloc[-1]
        
        # EMA (Exponential Moving Averages)
        ema_9 = EMAIndicator(close=df['close'], window=9).ema_indicator().iloc[-1]
        ema_21 = EMAIndicator(close=df['close'], window=21).ema_indicator().iloc[-1]
        ema_50 = EMAIndicator(close=df['close'], window=50).ema_indicator().iloc[-1]
        
        # Determine trend
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
        
        # RSI
        rsi_value = RSIIndicator(close=df['close'], window=14).rsi().iloc[-1]
        rsi_signal = "overbought" if rsi_value > 70 else "oversold" if rsi_value < 30 else "neutral"
        
        indicators['rsi'] = {
            "value": round(rsi_value, 2),
            "signal": rsi_signal,
            "interpretation": f"Stock is {rsi_signal}"
        }
        
        # MACD
        macd = MACD(close=df['close'])
        macd_line = macd.macd().iloc[-1]
        signal_line = macd.macd_signal().iloc[-1]
        
        indicators['macd'] = {
            "macd_line": round(macd_line, 2),
            "signal_line": round(signal_line, 2),
            "signal": "bullish" if macd_line > signal_line else "bearish"
        }
        
        # Bollinger Bands
        bb = BollingerBands(close=df['close'], window=20, window_dev=2)
        bb_upper = bb.bollinger_hband().iloc[-1]
        bb_lower = bb.bollinger_lband().iloc[-1]
        
        bb_signal = "overbought" if current_price >= bb_upper else "oversold" if current_price <= bb_lower else "normal"
        
        indicators['bollinger_bands'] = {
            "upper_band": round(bb_upper, 2),
            "lower_band": round(bb_lower, 2),
            "signal": bb_signal
        }
        
        # Overall Summary
        bullish = sum([
            1 for ind in [indicators['ema'], indicators['rsi'], indicators['macd'], indicators['bollinger_bands']]
            if ind.get('signal') in ['bullish', 'oversold', 'uptrend', 'strong_uptrend']
        ])
        
        bearish = sum([
            1 for ind in [indicators['ema'], indicators['rsi'], indicators['macd'], indicators['bollinger_bands']]
            if ind.get('signal') in ['bearish', 'overbought', 'downtrend', 'strong_downtrend']
        ])
        
        indicators['summary'] = {
            "overall_signal": "buy" if bullish >= 3 else "sell" if bearish >= 3 else "hold",
            "bullish_indicators": bullish,
            "bearish_indicators": bearish,
            "confidence": round(max(bullish, bearish) / 4 * 100, 2)
        }
        
        return {
            "symbol": symbol,
            "analyzed_at": datetime.utcnow().isoformat(),
            "indicators": indicators
        }
        
    except Exception as e:
        logger.error("technical_analysis_failed", symbol=symbol, error=str(e))
        return {"error": str(e), "symbol": symbol}
