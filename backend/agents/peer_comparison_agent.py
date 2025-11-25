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
                    price_data = await get_stock_price(symbol=symbol, market=market, period="1y")
                    fundamental_data = await get_fundamental_data(symbol=symbol, market=market)
                    
                    stocks_data.append({
                        "symbol": symbol,
                        "price_data": price_data,
                        "fundamental_data": fundamental_data
                    })
                except Exception as e:
                    logger.warning("stock_data_fetch_failed", symbol=symbol, error=str(e))
                    continue
            
            if not stocks_data:
                return {
                    "error": "Failed to fetch data for any stocks",
                    "symbols": symbols
                }
            
            # Create comparison matrix
            comparison = self._create_comparison_matrix(stocks_data)
            
            # Identify best performers
            best_performers = self._identify_best_performers(stocks_data)
            
            # Generate AI insights
            insights = await self._generate_comparison_insights(stocks_data, comparison)
            
            result = {
                "symbols": symbols,
                "market": market,
                "comparison": comparison,
                "best_performers": best_performers,
                "insights": insights,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info("peer_comparison_completed", symbols=symbols)
            return result
            
        except Exception as e:
            logger.error("peer_comparison_failed", symbols=symbols, error=str(e))
            return {
                "error": str(e),
                "symbols": symbols
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
            
            price = stock["price_data"]
            fund = stock["fundamental_data"]
            fund_details = fund.get("fundamental_details", {})
            
            # Price metrics
            if "current_price" not in matrix["metrics"]:
                matrix["metrics"]["current_price"] = {}
            matrix["metrics"]["current_price"][symbol] = price.get("current_price", 0)
            
            if "change_percent" not in matrix["metrics"]:
                matrix["metrics"]["change_percent"] = {}
            matrix["metrics"]["change_percent"][symbol] = price.get("change_percent", 0)
            
            # Valuation metrics
            valuation = fund_details.get("valuation_metrics", {})
            if "pe_ratio" not in matrix["metrics"]:
                matrix["metrics"]["pe_ratio"] = {}
            matrix["metrics"]["pe_ratio"][symbol] = valuation.get("pe_ratio")
            
            if "market_cap" not in matrix["metrics"]:
                matrix["metrics"]["market_cap"] = {}
            matrix["metrics"]["market_cap"][symbol] = valuation.get("market_cap")
            
            # Profitability
            profitability = fund_details.get("profitability", {})
            if "roe" not in matrix["metrics"]:
                matrix["metrics"]["roe"] = {}
            matrix["metrics"]["roe"][symbol] = profitability.get("roe")
            
            if "profit_margins" not in matrix["metrics"]:
                matrix["metrics"]["profit_margins"] = {}
            matrix["metrics"]["profit_margins"][symbol] = profitability.get("profit_margins")
            
            # Growth
            growth = fund_details.get("growth", {})
            if "revenue_growth" not in matrix["metrics"]:
                matrix["metrics"]["revenue_growth"] = {}
            matrix["metrics"]["revenue_growth"][symbol] = growth.get("revenue_growth")
        
        return matrix
    
    def _identify_best_performers(self, stocks_data: List[Dict[str, Any]]) -> Dict[str, str]:
        """Identify best performers in each category."""
        best = {}
        
        # Best price performance
        best_price = max(
            stocks_data,
            key=lambda x: x["price_data"].get("change_percent", 0)
        )
        best["price_performance"] = best_price["symbol"]
        
        # Best ROE
        best_roe = max(
            stocks_data,
            key=lambda x: x["fundamental_data"].get("fundamental_details", {}).get("profitability", {}).get("roe", 0) or 0
        )
        best["roe"] = best_roe["symbol"]
        
        # Best growth
        best_growth = max(
            stocks_data,
            key=lambda x: x["fundamental_data"].get("fundamental_details", {}).get("growth", {}).get("revenue_growth", 0) or 0
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

