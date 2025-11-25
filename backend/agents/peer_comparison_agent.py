"""
=============================================================================
Peer Comparison Agent
=============================================================================
Agent responsible for comparing stocks:
- Multi-stock comparison
- Peer group identification
- Comparative metrics
- Best-in-class identification
=============================================================================
"""

from typing import Dict, Any, List
import structlog
from datetime import datetime

from agents.base_agent import BaseAgent
from agents.tools.stock_price_tool import get_stock_price
from agents.tools.fundamental_data_tool import get_fundamental_data

logger = structlog.get_logger()


class PeerComparisonAgent(BaseAgent):
    """
    Agent that compares multiple stocks.
    """
    
    def __init__(self):
        system_prompt = """You are a Peer Comparison Analyst specializing in:
        1. Comparing multiple stocks side-by-side
        2. Identifying peer groups
        3. Analyzing relative performance
        4. Recommending best-in-class stocks
        5. Highlighting competitive advantages
        
        Always provide clear, comparative analysis."""
        
        super().__init__(
            name="PeerComparisonAnalyst",
            system_prompt=system_prompt,
            model="gpt-4o-mini",
            temperature=0.1
        )
    
    async def analyze(
        self,
        symbols: List[str],
        market: str = "india_nse"
    ) -> Dict[str, Any]:
        """
        Compare multiple stocks.
        
        Args:
            symbols: List of stock symbols to compare
            market: Market identifier
        
        Returns:
            Dict containing comparative analysis
        """
        logger.info("peer_comparison_started", symbols=symbols, market=market)
        
        try:
            # Fetch data for all symbols
            stocks_data = []
            for symbol in symbols:
                try:
                    price_data = await get_stock_price.ainvoke({
                        "symbol": symbol,
                        "market": market,
                        "period": "1y"
                    })
                    
                    # Skip if price data has error
                    if price_data.get("error"):
                        logger.warning("price_data_has_error", symbol=symbol, error=price_data.get("error"))
                        continue
                    
                    fundamental_data = await get_fundamental_data.ainvoke({
                        "symbol": symbol,
                        "market": market
                    })
                    
                    # Skip if fundamental data has error (but allow fallback data)
                    if fundamental_data.get("error") and fundamental_data.get("data_source") != "fallback_demo":
                        logger.warning("fundamental_data_has_error", symbol=symbol, error=fundamental_data.get("error"))
                        # Still include it but with empty fundamental_details
                        if "fundamental_details" not in fundamental_data:
                            fundamental_data["fundamental_details"] = {}
                    
                    stocks_data.append({
                        "symbol": symbol,
                        "price_data": price_data,
                        "fundamental_data": fundamental_data
                    })
                except Exception as e:
                    logger.warning("stock_data_fetch_failed", symbol=symbol, error=str(e))
                    continue
            
            if not stocks_data:
                logger.error("no_stocks_data_available", symbols=symbols)
                return {
                    "error": "Failed to fetch data for any stocks",
                    "symbols": symbols,
                    "comparison": {"symbols": [], "metrics": {}},
                    "best_performers": {},
                    "insights": "Unable to fetch data for comparison. Please try again later."
                }
            
            # Create comparison matrix
            try:
                comparison = self._create_comparison_matrix(stocks_data)
            except Exception as e:
                logger.error("comparison_matrix_creation_failed", error=str(e))
                comparison = {"symbols": [s["symbol"] for s in stocks_data], "metrics": {}}
            
            # Identify best performers
            try:
                best_performers = self._identify_best_performers(stocks_data)
            except Exception as e:
                logger.error("best_performers_identification_failed", error=str(e))
                best_performers = {}
            
            # Generate AI insights
            try:
                insights = await self._generate_comparison_insights(stocks_data, comparison)
            except Exception as e:
                logger.error("comparison_insights_generation_failed", error=str(e))
                insights = "Comparison analysis completed. Detailed insights unavailable."
            
            result = {
                "symbols": [s["symbol"] for s in stocks_data],
                "market": market,
                "comparison": comparison,
                "best_performers": best_performers,
                "insights": insights,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info("peer_comparison_completed", 
                       symbols=result["symbols"], 
                       stocks_count=len(stocks_data),
                       metrics_count=len(comparison.get("metrics", {})))
            return result
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error("peer_comparison_failed", 
                        symbols=symbols, 
                        error=str(e),
                        error_type=type(e).__name__,
                        traceback=error_trace)
            return {
                "error": str(e),
                "symbols": symbols,
                "error_type": type(e).__name__
            }
    
    def _create_comparison_matrix(self, stocks_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create comparison matrix of key metrics."""
        matrix = {
            "symbols": [],
            "metrics": {}
        }
        
        for stock in stocks_data:
            symbol = stock["symbol"]
            matrix["symbols"].append(symbol)
            
            price = stock.get("price_data", {})
            fund = stock.get("fundamental_data", {})
            fund_details = fund.get("fundamental_details", {}) if fund else {}
            
            # Price metrics (safe access with defaults)
            if "current_price" not in matrix["metrics"]:
                matrix["metrics"]["current_price"] = {}
            matrix["metrics"]["current_price"][symbol] = price.get("current_price") if price else None
            
            if "change_percent" not in matrix["metrics"]:
                matrix["metrics"]["change_percent"] = {}
            matrix["metrics"]["change_percent"][symbol] = price.get("change_percent") if price else None
            
            # Valuation metrics
            valuation = fund_details.get("valuation_metrics", {}) if fund_details else {}
            if "pe_ratio" not in matrix["metrics"]:
                matrix["metrics"]["pe_ratio"] = {}
            matrix["metrics"]["pe_ratio"][symbol] = valuation.get("pe_ratio") if valuation else None
            
            if "market_cap" not in matrix["metrics"]:
                matrix["metrics"]["market_cap"] = {}
            matrix["metrics"]["market_cap"][symbol] = valuation.get("market_cap") if valuation else None
            
            # Profitability
            profitability = fund_details.get("profitability", {}) if fund_details else {}
            if "roe" not in matrix["metrics"]:
                matrix["metrics"]["roe"] = {}
            matrix["metrics"]["roe"][symbol] = profitability.get("roe") if profitability else None
            
            if "profit_margins" not in matrix["metrics"]:
                matrix["metrics"]["profit_margins"] = {}
            matrix["metrics"]["profit_margins"][symbol] = profitability.get("profit_margins") if profitability else None
            
            # Growth
            growth = fund_details.get("growth", {}) if fund_details else {}
            if "revenue_growth" not in matrix["metrics"]:
                matrix["metrics"]["revenue_growth"] = {}
            matrix["metrics"]["revenue_growth"][symbol] = growth.get("revenue_growth") if growth else None
        
        return matrix
    
    def _identify_best_performers(self, stocks_data: List[Dict[str, Any]]) -> Dict[str, str]:
        """Identify best performers in each category."""
        best = {}
        
        if not stocks_data:
            return best
        
        # Best price performance (filter out None values)
        valid_price_stocks = [s for s in stocks_data if s.get("price_data", {}).get("change_percent") is not None]
        if valid_price_stocks:
            best_price = max(
                valid_price_stocks,
                key=lambda x: x["price_data"].get("change_percent", 0) or 0
            )
            best["price_performance"] = best_price["symbol"]
        
        # Best ROE (filter out None values)
        valid_roe_stocks = [
            s for s in stocks_data 
            if s.get("fundamental_data", {}).get("fundamental_details", {}).get("profitability", {}).get("roe") is not None
        ]
        if valid_roe_stocks:
            best_roe = max(
                valid_roe_stocks,
                key=lambda x: x.get("fundamental_data", {}).get("fundamental_details", {}).get("profitability", {}).get("roe", 0) or 0
            )
            best["roe"] = best_roe["symbol"]
        
        # Best growth (filter out None values)
        valid_growth_stocks = [
            s for s in stocks_data 
            if s.get("fundamental_data", {}).get("fundamental_details", {}).get("growth", {}).get("revenue_growth") is not None
        ]
        if valid_growth_stocks:
            best_growth = max(
                valid_growth_stocks,
                key=lambda x: x.get("fundamental_data", {}).get("fundamental_details", {}).get("growth", {}).get("revenue_growth", 0) or 0
            )
            best["revenue_growth"] = best_growth["symbol"]
        
        return best
    
    async def _generate_comparison_insights(
        self,
        stocks_data: List[Dict[str, Any]],
        comparison: Dict[str, Any]
    ) -> str:
        """Generate AI insights on comparison."""
        symbols = [s["symbol"] for s in stocks_data]
        best = self._identify_best_performers(stocks_data)
        
        prompt = f"""Compare these stocks: {', '.join(symbols)}
        
        Comparison Matrix:
        {self._format_comparison_for_ai(comparison)}
        
        Best Performers:
        - Price Performance: {best.get('price_performance')}
        - ROE: {best.get('roe')}
        - Revenue Growth: {best.get('revenue_growth')}
        
        Provide:
        1. Overall comparison summary
        2. Best-in-class stock for investment
        3. Key differentiators
        4. Risk-return profile comparison
        5. Investment recommendations
        
        Keep response concise and actionable."""
        
        try:
            insights = await self.invoke(prompt)
            return insights
        except Exception as e:
            logger.error("comparison_insights_generation_failed", error=str(e))
            return "Comparison analysis in progress."
    
    def _format_comparison_for_ai(self, comparison: Dict[str, Any]) -> str:
        """Format comparison data for AI prompt."""
        lines = []
        for metric, values in comparison.get("metrics", {}).items():
            lines.append(f"{metric}:")
            for symbol, value in values.items():
                lines.append(f"  {symbol}: {value}")
        return "\n".join(lines)

