"""
=============================================================================
Options Chain Analysis Agent
=============================================================================
Agent responsible for analyzing options chain data:
- Options chain analysis
- Greeks calculation
- Strike price recommendations
- Options strategy suggestions
=============================================================================
"""

from typing import Dict, Any, Optional, List
import structlog
from datetime import datetime

from agents.base_agent import BaseAgent
from agents.tools.options_tool import get_options_chain
from agents.tools.stock_price_tool import get_stock_price

logger = structlog.get_logger()


class OptionsAgent(BaseAgent):
    """
    Agent that analyzes options chain data.
    """
    
    def __init__(self):
        system_prompt = """You are an Options Trading Analyst specializing in:
        1. Analyzing options chain data
        2. Calculating Greeks (Delta, Gamma, Theta, Vega)
        3. Identifying profitable options strategies
        4. Recommending strike prices
        5. Assessing risk-reward ratios
        
        Always provide data-driven, actionable options analysis."""
        
        super().__init__(
            name="OptionsAnalyst",
            system_prompt=system_prompt,
            model="gpt-4o-mini",
            temperature=0.1
        )
    
    async def analyze(
        self,
        symbol: str,
        market: str = "india_nse",
        expiration_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze options chain for a stock.
        
        Args:
            symbol: Stock symbol
            market: Market identifier
            expiration_date: Expiration date (optional)
        
        Returns:
            Dict containing options analysis
        """
        logger.info("options_analysis_started", symbol=symbol, market=market)
        
        try:
            # Get options chain data
            options_data = await get_options_chain.ainvoke({
                "symbol": symbol,
                "market": market,
                "expiration_date": expiration_date
            })
            
            if "error" in options_data:
                return {
                    "error": options_data["error"],
                    "symbol": symbol
                }
            
            # Get current stock price
            price_data = await get_stock_price(symbol=symbol, market=market, period="1d")
            current_price = price_data.get("current_price", options_data.get("current_price", 0))
            
            # Calculate key metrics
            metrics = self._calculate_options_metrics(options_data, current_price)
            
            # Generate AI insights
            insights = await self._generate_options_insights(options_data, current_price, symbol)
            
            # Recommend strategies
            strategies = await self._recommend_strategies(options_data, current_price, symbol)
            
            result = {
                "symbol": symbol,
                "market": market,
                "current_price": current_price,
                "expiration_date": options_data.get("expiration_date"),
                "available_expirations": options_data.get("available_expirations", []),
                "calls": options_data.get("calls", []),
                "puts": options_data.get("puts", []),
                "metrics": metrics,
                "insights": insights,
                "strategies": strategies,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info("options_analysis_completed", symbol=symbol)
            return result
            
        except Exception as e:
            logger.error("options_analysis_failed", symbol=symbol, error=str(e))
            return {
                "error": str(e),
                "symbol": symbol
            }
    
    def _calculate_options_metrics(
        self,
        options_data: Dict[str, Any],
        current_price: float
    ) -> Dict[str, Any]:
        """Calculate key options metrics."""
        calls = options_data.get("calls", [])
        puts = options_data.get("puts", [])
        
        # Find at-the-money options
        atm_call = min(calls, key=lambda x: abs(x["strike"] - current_price)) if calls else None
        atm_put = min(puts, key=lambda x: abs(x["strike"] - current_price)) if puts else None
        
        # Calculate total open interest
        total_call_oi = sum(c["open_interest"] for c in calls)
        total_put_oi = sum(p["open_interest"] for p in puts)
        
        # Put-call ratio
        put_call_ratio = total_put_oi / total_call_oi if total_call_oi > 0 else 0
        
        # Max pain (simplified - would need full calculation)
        max_pain = current_price  # Placeholder
        
        return {
            "current_price": current_price,
            "atm_call_strike": atm_call["strike"] if atm_call else None,
            "atm_put_strike": atm_put["strike"] if atm_put else None,
            "total_call_oi": total_call_oi,
            "total_put_oi": total_put_oi,
            "put_call_ratio": round(put_call_ratio, 2),
            "max_pain": round(max_pain, 2),
            "total_volume": sum(c["volume"] for c in calls) + sum(p["volume"] for p in puts)
        }
    
    async def _generate_options_insights(
        self,
        options_data: Dict[str, Any],
        current_price: float,
        symbol: str
    ) -> str:
        """Generate AI insights on options chain."""
        calls = options_data.get("calls", [])
        puts = options_data.get("puts", [])
        metrics = self._calculate_options_metrics(options_data, current_price)
        
        prompt = f"""Analyze this options chain data:
        
        Stock: {symbol}
        Current Price: ${current_price}
        Expiration: {options_data.get('expiration_date')}
        
        Options Metrics:
        - Put-Call Ratio: {metrics.get('put_call_ratio')}
        - Total Call OI: {metrics.get('total_call_oi')}
        - Total Put OI: {metrics.get('total_put_oi')}
        - Total Volume: {metrics.get('total_volume')}
        
        Provide:
        1. Market sentiment (bullish/bearish/neutral) based on put-call ratio
        2. Key support/resistance levels from options data
        3. Notable open interest concentrations
        4. Implied volatility assessment
        5. Trading opportunities
        
        Keep response concise and actionable."""
        
        try:
            insights = await self.invoke(prompt)
            return insights
        except Exception as e:
            logger.error("options_insights_generation_failed", error=str(e))
            return "Options analysis in progress."
    
    async def _recommend_strategies(
        self,
        options_data: Dict[str, Any],
        current_price: float,
        symbol: str
    ) -> List[Dict[str, Any]]:
        """Recommend options strategies."""
        calls = options_data.get("calls", [])
        puts = options_data.get("puts", [])
        
        strategies = []
        
        # Simple strategy recommendations based on data
        if calls and puts:
            # Find liquid options (high volume/OI)
            liquid_calls = sorted(calls, key=lambda x: x["volume"] + x["open_interest"], reverse=True)[:3]
            liquid_puts = sorted(puts, key=lambda x: x["volume"] + x["open_interest"], reverse=True)[:3]
            
            if liquid_calls:
                strategies.append({
                    "strategy": "Long Call",
                    "description": f"Buy call at strike ${liquid_calls[0]['strike']}",
                    "risk_level": "high",
                    "potential_profit": "unlimited",
                    "max_loss": f"${liquid_calls[0]['ask']}"
                })
            
            if liquid_puts:
                strategies.append({
                    "strategy": "Long Put",
                    "description": f"Buy put at strike ${liquid_puts[0]['strike']}",
                    "risk_level": "high",
                    "potential_profit": f"${liquid_puts[0]['strike'] - liquid_puts[0]['ask']}",
                    "max_loss": f"${liquid_puts[0]['ask']}"
                })
        
        return strategies

