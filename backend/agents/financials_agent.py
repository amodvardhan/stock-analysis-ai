"""
=============================================================================
Financials Deep Dive Agent
=============================================================================
Agent responsible for deep financial analysis:
- Financial statements analysis
- Ratio analysis
- Year-over-year comparisons
- Financial health scoring
=============================================================================
"""

from typing import Dict, Any
import structlog
from datetime import datetime

from agents.base_agent import BaseAgent
from agents.tools.financials_tool import get_financial_statements
from agents.tools.fundamental_data_tool import get_fundamental_data

logger = structlog.get_logger()


class FinancialsAgent(BaseAgent):
    """
    Agent that performs deep financial analysis.
    """
    
    def __init__(self):
        system_prompt = """You are a Financial Analysis Specialist focusing on:
        1. Analyzing financial statements (P&L, Balance Sheet, Cash Flow)
        2. Calculating and interpreting financial ratios
        3. Year-over-year and quarter-over-quarter comparisons
        4. Assessing financial health and stability
        5. Identifying trends and red flags
        
        Always provide comprehensive, data-driven financial analysis."""
        
        super().__init__(
            name="FinancialAnalyst",
            system_prompt=system_prompt,
            model="gpt-4o-mini",
            temperature=0.1
        )
    
    async def analyze(
        self,
        symbol: str,
        market: str = "india_nse"
    ) -> Dict[str, Any]:
        """
        Perform deep financial analysis.
        
        Args:
            symbol: Stock symbol
            market: Market identifier
        
        Returns:
            Dict containing comprehensive financial analysis
        """
        logger.info("financial_analysis_started", symbol=symbol, market=market)
        
        try:
            # Get financial statements
            financials = await get_financial_statements.ainvoke({
                "symbol": symbol,
                "market": market,
                "statement_type": "all"
            })
            
            if "error" in financials:
                return {
                    "error": financials["error"],
                    "symbol": symbol
                }
            
            # Get fundamental data for additional context
            fundamental = await get_fundamental_data(symbol=symbol, market=market)
            
            # Calculate financial health score
            health_score = self._calculate_health_score(financials, fundamental)
            
            # Generate AI insights
            insights = await self._generate_financial_insights(financials, fundamental, symbol)
            
            # Year-over-year analysis
            yoy_analysis = self._analyze_yoy(financials)
            
            result = {
                "symbol": symbol,
                "market": market,
                "financial_statements": {
                    "income_statement": financials.get("income_statement"),
                    "balance_sheet": financials.get("balance_sheet"),
                    "cashflow_statement": financials.get("cashflow_statement"),
                    "quarterly_income": financials.get("quarterly_income")
                },
                "key_ratios": financials.get("key_ratios", {}),
                "financial_health": {
                    "score": health_score["score"],
                    "grade": health_score["grade"],
                    "strengths": health_score["strengths"],
                    "weaknesses": health_score["weaknesses"]
                },
                "yoy_analysis": yoy_analysis,
                "insights": insights,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info("financial_analysis_completed", symbol=symbol)
            return result
            
        except Exception as e:
            logger.error("financial_analysis_failed", symbol=symbol, error=str(e))
            return {
                "error": str(e),
                "symbol": symbol
            }
    
    def _calculate_health_score(
        self,
        financials: Dict[str, Any],
        fundamental: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate financial health score."""
        score = 50  # Base score
        strengths = []
        weaknesses = []
        
        ratios = financials.get("key_ratios", {})
        fund_details = fundamental.get("fundamental_details", {})
        
        # Profitability
        if ratios.get("roe") and ratios["roe"] > 0.15:
            score += 10
            strengths.append("Strong ROE")
        elif ratios.get("roe") and ratios["roe"] < 0.05:
            score -= 10
            weaknesses.append("Low ROE")
        
        # Debt management
        debt_to_equity = ratios.get("debt_to_equity") or fund_details.get("financial_health", {}).get("debt_to_equity")
        if debt_to_equity and debt_to_equity < 0.5:
            score += 10
            strengths.append("Low debt-to-equity ratio")
        elif debt_to_equity and debt_to_equity > 2.0:
            score -= 10
            weaknesses.append("High debt-to-equity ratio")
        
        # Profit margins
        profit_margin = ratios.get("profit_margin") or fund_details.get("profitability", {}).get("profit_margins")
        if profit_margin and profit_margin > 0.15:
            score += 10
            strengths.append("Strong profit margins")
        elif profit_margin and profit_margin < 0.05:
            score -= 5
            weaknesses.append("Low profit margins")
        
        # Growth
        revenue_growth = ratios.get("revenue_growth") or fund_details.get("growth", {}).get("revenue_growth")
        if revenue_growth and revenue_growth > 0.10:
            score += 10
            strengths.append("Strong revenue growth")
        elif revenue_growth and revenue_growth < 0:
            score -= 10
            weaknesses.append("Declining revenue")
        
        # Liquidity
        current_ratio = ratios.get("current_ratio")
        if current_ratio and 1.5 <= current_ratio <= 3.0:
            score += 5
            strengths.append("Good liquidity")
        elif current_ratio and current_ratio < 1.0:
            score -= 10
            weaknesses.append("Poor liquidity")
        
        score = max(0, min(100, score))
        
        # Grade
        if score >= 80:
            grade = "A"
        elif score >= 70:
            grade = "B"
        elif score >= 60:
            grade = "C"
        elif score >= 50:
            grade = "D"
        else:
            grade = "F"
        
        return {
            "score": score,
            "grade": grade,
            "strengths": strengths if strengths else ["No major strengths identified"],
            "weaknesses": weaknesses if weaknesses else ["No major weaknesses identified"]
        }
    
    def _analyze_yoy(self, financials: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze year-over-year changes."""
        income = financials.get("income_statement")
        if not income:
            return {}
        
        # Extract revenue and profit data if available
        # This is simplified - in production, would parse dates properly
        return {
            "revenue_growth": financials.get("key_ratios", {}).get("revenue_growth"),
            "earnings_growth": financials.get("key_ratios", {}).get("earnings_growth"),
            "note": "Detailed YOY analysis requires parsing financial statement dates"
        }
    
    async def _generate_financial_insights(
        self,
        financials: Dict[str, Any],
        fundamental: Dict[str, Any],
        symbol: str
    ) -> str:
        """Generate AI insights on financials."""
        ratios = financials.get("key_ratios", {})
        health = self._calculate_health_score(financials, fundamental)
        
        prompt = f"""Analyze the financial health of {symbol}:
        
        Key Ratios:
        - P/E Ratio: {ratios.get('pe_ratio', 'N/A')}
        - ROE: {ratios.get('roe', 'N/A')}
        - ROA: {ratios.get('roa', 'N/A')}
        - Debt-to-Equity: {ratios.get('debt_to_equity', 'N/A')}
        - Current Ratio: {ratios.get('current_ratio', 'N/A')}
        - Profit Margin: {ratios.get('profit_margin', 'N/A')}
        - Revenue Growth: {ratios.get('revenue_growth', 'N/A')}
        
        Financial Health Score: {health['score']}/100 (Grade: {health['grade']})
        Strengths: {', '.join(health['strengths'])}
        Weaknesses: {', '.join(health['weaknesses'])}
        
        Provide:
        1. Overall financial health assessment
        2. Key strengths and concerns
        3. Comparison to industry standards
        4. Investment implications
        5. Risk factors
        
        Keep response comprehensive but concise."""
        
        try:
            insights = await self.invoke(prompt)
            return insights
        except Exception as e:
            logger.error("financial_insights_generation_failed", error=str(e))
            return "Financial analysis in progress."

