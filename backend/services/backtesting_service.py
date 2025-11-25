"""
=============================================================================
Backtesting Service
=============================================================================
Allows users to test trading strategies against historical data.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import structlog
import pandas as pd
import numpy as np

from agents.tools.stock_price_tool import get_stock_price
from agents.tools.technical_indicators_tool import calculate_technical_indicators

logger = structlog.get_logger()


class BacktestingService:
    """Service for backtesting trading strategies."""
    
    @staticmethod
    async def backtest_strategy(
        symbol: str,
        market: str,
        start_date: str,
        end_date: str,
        initial_capital: float,
        strategy: Dict[str, Any],
        commission: float = 0.001  # 0.1% commission
    ) -> Dict[str, Any]:
        """
        Backtest a trading strategy against historical data.
        
        Args:
            symbol: Stock symbol
            market: Market identifier
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            initial_capital: Starting capital
            strategy: Strategy configuration
            commission: Trading commission rate
        
        Returns:
            Backtest results with performance metrics
        """
        try:
            logger.info(
                "backtest_started",
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                strategy=strategy.get("type")
            )
            
            # Fetch historical data
            logger.info("fetching_historical_data", symbol=symbol, market=market)
            price_data = await get_stock_price(symbol=symbol, market=market, period="1y")
            
            if "error" in price_data:
                logger.warning("price_data_error", symbol=symbol, error=price_data.get("error"))
                return {
                    "error": f"Failed to fetch historical data: {price_data.get('error', 'Unknown error')}",
                    "symbol": symbol
                }
            
            if not price_data.get("historical_data"):
                logger.warning("no_historical_data", symbol=symbol, price_data_keys=list(price_data.keys()))
                return {
                    "error": "No historical data available for this symbol",
                    "symbol": symbol,
                    "hint": "Please check if the symbol is correct and try again"
                }
            
            # Convert to DataFrame
            try:
                historical_data = price_data["historical_data"]
                if not historical_data or len(historical_data) == 0:
                    return {
                        "error": "Historical data is empty",
                        "symbol": symbol
                    }
                
                df = pd.DataFrame(historical_data)
                
                # Check required columns
                required_columns = ['date', 'close']
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    return {
                        "error": f"Missing required columns in historical data: {missing_columns}",
                        "symbol": symbol,
                        "available_columns": list(df.columns)
                    }
                
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date')
                
                # Filter by date range
                start = pd.to_datetime(start_date)
                end = pd.to_datetime(end_date)
                df = df[(df.index >= start) & (df.index <= end)]
                
                if df.empty:
                    logger.warning("empty_date_range", symbol=symbol, start_date=start_date, end_date=end_date)
                    return {
                        "error": f"No data available for the specified date range ({start_date} to {end_date})",
                        "symbol": symbol,
                        "hint": "Try a different date range or check if the symbol has data for this period"
                    }
                
                logger.info("data_prepared", symbol=symbol, rows=len(df), start=df.index.min(), end=df.index.max())
                
            except Exception as e:
                logger.error("dataframe_error", symbol=symbol, error=str(e), exc_info=True)
                return {
                    "error": f"Error processing historical data: {str(e)}",
                    "symbol": symbol
                }
            
            # Calculate technical indicators
            indicators = await calculate_technical_indicators(symbol, market, "1y")
            
            # Run backtest based on strategy type
            strategy_type = strategy.get("type", "simple_momentum")
            
            if strategy_type == "simple_momentum":
                results = await BacktestingService._backtest_momentum(
                    df, initial_capital, strategy, commission
                )
            elif strategy_type == "mean_reversion":
                results = await BacktestingService._backtest_mean_reversion(
                    df, initial_capital, strategy, commission
                )
            elif strategy_type == "rsi_strategy":
                results = await BacktestingService._backtest_rsi(
                    df, indicators, initial_capital, strategy, commission
                )
            else:
                return {
                    "error": f"Unknown strategy type: {strategy_type}",
                    "available_strategies": ["simple_momentum", "mean_reversion", "rsi_strategy"]
                }
            
            # Validate results
            if not results or "trades" not in results:
                return {
                    "error": "Backtest strategy did not return valid results",
                    "symbol": symbol
                }
            
            # Calculate performance metrics
            try:
                performance = BacktestingService._calculate_performance_metrics(
                    results, initial_capital
                )
            except Exception as e:
                logger.error("performance_calculation_error", symbol=symbol, error=str(e))
                return {
                    "error": f"Error calculating performance metrics: {str(e)}",
                    "symbol": symbol
                }
            
            logger.info(
                "backtest_completed",
                symbol=symbol,
                total_return=performance.get("total_return_percent"),
                sharpe_ratio=performance.get("sharpe_ratio"),
                trades_count=len(results.get("trades", []))
            )
            
            # Ensure all required fields are present
            response = {
                "symbol": symbol,
                "market": market,
                "start_date": start_date,
                "end_date": end_date,
                "strategy": strategy,
                "initial_capital": initial_capital,
                "performance": performance,
                "trades": results.get("trades", []),
                "equity_curve": results.get("equity_curve", []),
                "backtested_at": datetime.utcnow().isoformat()
            }
            
            # Validate response structure
            if not response.get("trades"):
                logger.warning("no_trades_generated", symbol=symbol, strategy=strategy.get("type"))
            
            if not response.get("equity_curve"):
                logger.warning("no_equity_curve", symbol=symbol)
                # Generate minimal equity curve if missing
                response["equity_curve"] = [
                    {"date": start_date, "equity": initial_capital},
                    {"date": end_date, "equity": performance.get("final_capital", initial_capital)}
                ]
            
            return response
            
        except Exception as e:
            logger.error("backtest_error", symbol=symbol, error=str(e))
            return {
                "error": str(e),
                "symbol": symbol
            }
    
    @staticmethod
    async def _backtest_momentum(
        df: pd.DataFrame,
        initial_capital: float,
        strategy: Dict[str, Any],
        commission: float
    ) -> Dict[str, Any]:
        """Backtest a simple momentum strategy."""
        capital = initial_capital
        shares = 0
        trades = []
        equity_curve = []
        
        lookback = strategy.get("lookback_period", 20)
        entry_threshold = strategy.get("entry_threshold", 0.02)  # 2% price increase
        
        for i in range(lookback, len(df)):
            current_price = df.iloc[i]['close']
            past_price = df.iloc[i - lookback]['close']
            price_change = (current_price - past_price) / past_price
            
            # Entry signal: price increased by threshold
            if shares == 0 and price_change >= entry_threshold:
                shares = int(capital / current_price)
                cost = shares * current_price * (1 + commission)
                capital -= cost
                trades.append({
                    "date": df.index[i].isoformat(),
                    "type": "BUY",
                    "price": current_price,
                    "shares": shares,
                    "cost": cost
                })
            
            # Exit signal: price decreased
            elif shares > 0 and price_change < -entry_threshold:
                proceeds = shares * current_price * (1 - commission)
                capital += proceeds
                trades.append({
                    "date": df.index[i].isoformat(),
                    "type": "SELL",
                    "price": current_price,
                    "shares": shares,
                    "proceeds": proceeds
                })
                shares = 0
            
            # Calculate current equity
            current_equity = capital + (shares * current_price if shares > 0 else 0)
            equity_curve.append({
                "date": df.index[i].isoformat(),
                "equity": current_equity
            })
        
        # Close any open positions
        if shares > 0:
            final_price = df.iloc[-1]['close']
            proceeds = shares * final_price * (1 - commission)
            capital += proceeds
            trades.append({
                "date": df.index[-1].isoformat(),
                "type": "SELL",
                "price": final_price,
                "shares": shares,
                "proceeds": proceeds
            })
        
        return {
            "trades": trades,
            "equity_curve": equity_curve,
            "final_capital": capital
        }
    
    @staticmethod
    async def _backtest_mean_reversion(
        df: pd.DataFrame,
        initial_capital: float,
        strategy: Dict[str, Any],
        commission: float
    ) -> Dict[str, Any]:
        """Backtest a mean reversion strategy."""
        capital = initial_capital
        shares = 0
        trades = []
        equity_curve = []
        
        lookback = strategy.get("lookback_period", 20)
        std_threshold = strategy.get("std_threshold", 2.0)  # 2 standard deviations
        
        for i in range(lookback, len(df)):
            current_price = df.iloc[i]['close']
            recent_prices = df.iloc[i - lookback:i]['close']
            mean_price = recent_prices.mean()
            std_price = recent_prices.std()
            
            z_score = (current_price - mean_price) / std_price if std_price > 0 else 0
            
            # Entry: price is below mean (oversold)
            if shares == 0 and z_score <= -std_threshold:
                shares = int(capital / current_price)
                cost = shares * current_price * (1 + commission)
                capital -= cost
                trades.append({
                    "date": df.index[i].isoformat(),
                    "type": "BUY",
                    "price": current_price,
                    "shares": shares,
                    "cost": cost
                })
            
            # Exit: price returns to mean
            elif shares > 0 and z_score >= 0:
                proceeds = shares * current_price * (1 - commission)
                capital += proceeds
                trades.append({
                    "date": df.index[i].isoformat(),
                    "type": "SELL",
                    "price": current_price,
                    "shares": shares,
                    "proceeds": proceeds
                })
                shares = 0
            
            current_equity = capital + (shares * current_price if shares > 0 else 0)
            equity_curve.append({
                "date": df.index[i].isoformat(),
                "equity": current_equity
            })
        
        if shares > 0:
            final_price = df.iloc[-1]['close']
            proceeds = shares * final_price * (1 - commission)
            capital += proceeds
            trades.append({
                "date": df.index[-1].isoformat(),
                "type": "SELL",
                "price": final_price,
                "shares": shares,
                "proceeds": proceeds
            })
        
        return {
            "trades": trades,
            "equity_curve": equity_curve,
            "final_capital": capital
        }
    
    @staticmethod
    async def _backtest_rsi(
        df: pd.DataFrame,
        indicators: Dict[str, Any],
        initial_capital: float,
        strategy: Dict[str, Any],
        commission: float
    ) -> Dict[str, Any]:
        """Backtest an RSI-based strategy."""
        capital = initial_capital
        shares = 0
        trades = []
        equity_curve = []
        
        oversold = strategy.get("oversold_level", 30)
        overbought = strategy.get("overbought_level", 70)
        
        # Get RSI values (simplified - would need to calculate for each period)
        rsi_value = indicators.get("rsi", {}).get("value", 50)
        
        for i in range(1, len(df)):
            current_price = df.iloc[i]['close']
            # In a real implementation, calculate RSI for each period
            # For now, use a simplified version
            
            # Entry: RSI < oversold
            if shares == 0 and rsi_value < oversold:
                shares = int(capital / current_price)
                cost = shares * current_price * (1 + commission)
                capital -= cost
                trades.append({
                    "date": df.index[i].isoformat(),
                    "type": "BUY",
                    "price": current_price,
                    "shares": shares,
                    "cost": cost
                })
            
            # Exit: RSI > overbought
            elif shares > 0 and rsi_value > overbought:
                proceeds = shares * current_price * (1 - commission)
                capital += proceeds
                trades.append({
                    "date": df.index[i].isoformat(),
                    "type": "SELL",
                    "price": current_price,
                    "shares": shares,
                    "proceeds": proceeds
                })
                shares = 0
            
            current_equity = capital + (shares * current_price if shares > 0 else 0)
            equity_curve.append({
                "date": df.index[i].isoformat(),
                "equity": current_equity
            })
        
        if shares > 0:
            final_price = df.iloc[-1]['close']
            proceeds = shares * final_price * (1 - commission)
            capital += proceeds
            trades.append({
                "date": df.index[-1].isoformat(),
                "type": "SELL",
                "price": final_price,
                "shares": shares,
                "proceeds": proceeds
            })
        
        return {
            "trades": trades,
            "equity_curve": equity_curve,
            "final_capital": capital
        }
    
    @staticmethod
    def _calculate_performance_metrics(
        results: Dict[str, Any],
        initial_capital: float
    ) -> Dict[str, Any]:
        """Calculate performance metrics from backtest results."""
        final_capital = results.get("final_capital", initial_capital)
        equity_curve = results.get("equity_curve", [])
        trades = results.get("trades", [])
        
        # Total return
        total_return = final_capital - initial_capital
        total_return_percent = (total_return / initial_capital) * 100
        
        # Calculate returns for Sharpe ratio
        returns = []
        for i in range(1, len(equity_curve)):
            prev_equity = equity_curve[i - 1]["equity"]
            curr_equity = equity_curve[i]["equity"]
            if prev_equity > 0:
                returns.append((curr_equity - prev_equity) / prev_equity)
        
        # Sharpe ratio (simplified, assuming risk-free rate = 0)
        sharpe_ratio = 0
        if returns:
            mean_return = np.mean(returns)
            std_return = np.std(returns)
            if std_return > 0:
                sharpe_ratio = (mean_return / std_return) * np.sqrt(252)  # Annualized
        
        # Max drawdown
        max_drawdown = 0
        peak = initial_capital
        for point in equity_curve:
            equity = point["equity"]
            if equity > peak:
                peak = equity
            drawdown = (peak - equity) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # Win rate
        winning_trades = 0
        total_trades = len([t for t in trades if t["type"] == "SELL"])
        # Simplified - would need to track P&L per trade
        
        return {
            "initial_capital": initial_capital,
            "final_capital": final_capital,
            "total_return": total_return,
            "total_return_percent": total_return_percent,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "max_drawdown_percent": max_drawdown * 100,
            "total_trades": len(trades),
            "win_rate": (winning_trades / total_trades * 100) if total_trades > 0 else 0
        }

