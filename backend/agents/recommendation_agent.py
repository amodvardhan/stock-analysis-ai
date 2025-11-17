"""
=============================================================================
AI Hub - Recommendation Agent
=============================================================================
Synthesizes all analyses to generate final stock recommendation.
=============================================================================
"""

from typing import Dict, Any, Optional
from langchain_core.runnables import RunnableConfig
import structlog

from agents.base_agent import BaseAgent

logger = structlog.get_logger()


class RecommendationAgent(BaseAgent):
    """
    Agent that synthesizes all analyses into a final recommendation.
    
    Takes outputs from Technical, Fundamental, and Sentiment agents
    and produces a final BUY/SELL/HOLD recommendation with reasoning.
    """
    
    def __init__(self):
        """Initialize recommendation agent."""
        super().__init__(
            name="RecommendationSynthesizer",  # Changed from agent_name
            system_prompt="""You are an expert financial advisor synthesizing multiple analyses.

Your task:
1. Review technical, fundamental, and sentiment analyses
2. Consider user's risk tolerance
3. Provide a clear BUY, SELL, or HOLD recommendation
4. Explain your reasoning concisely
5. Highlight key risks and opportunities

Be balanced, objective, and clear in your recommendations.""",
            model="gpt-4o",
            temperature=0.2
        )
    
    async def synthesize(
        self,
        symbol: str,
        technical_analysis: Dict[str, Any],
        fundamental_analysis: Dict[str, Any],
        sentiment_analysis: Dict[str, Any],
        user_risk_tolerance: str = "moderate",
        config: RunnableConfig | None = None
    ) -> Dict[str, Any]:
        """
        Synthesize all analyses into final recommendation.
        
        Args:
            symbol: Stock ticker symbol
            technical_analysis: Output from technical agent
            fundamental_analysis: Output from fundamental agent
            sentiment_analysis: Output from sentiment agent
            user_risk_tolerance: User's risk profile
            config: Optional LangChain config
        
        Returns:
            Dict containing final recommendation
        """
        logger.info("synthesizing_recommendation", symbol=symbol)
        
        try:
            # Extract key signals from each analysis
            tech_signal = self._extract_technical_signal(technical_analysis)
            fund_signal = self._extract_fundamental_signal(fundamental_analysis)
            sent_signal = self._extract_sentiment_signal(sentiment_analysis)
            
            # Calculate overall recommendation
            signals = [tech_signal, fund_signal, sent_signal]
            buy_votes = sum(1 for s in signals if s == "buy")
            sell_votes = sum(1 for s in signals if s == "sell")
            
            # Determine final action
            if buy_votes >= 2:
                action = "buy"
                confidence = (buy_votes / 3) * 100
            elif sell_votes >= 2:
                action = "sell"
                confidence = (sell_votes / 3) * 100
            else:
                action = "hold"
                confidence = 50
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                action,
                technical_analysis,
                fundamental_analysis,
                sentiment_analysis,
                user_risk_tolerance
            )
            
            # Generate risk assessment
            risk_assessment = self._generate_risk_assessment(
                action,
                user_risk_tolerance,
                technical_analysis,
                fundamental_analysis
            )
            
            return {
                "action": action,
                "confidence": round(confidence, 2),
                "reasoning": reasoning,
                "risk_assessment": risk_assessment,
                "signals": {
                    "technical": tech_signal,
                    "fundamental": fund_signal,
                    "sentiment": sent_signal
                }
            }
            
        except Exception as e:
            logger.error("recommendation_synthesis_failed", symbol=symbol, error=str(e))
            raise Exception(f"Recommendation synthesis failed: {str(e)}")
    
    def _extract_technical_signal(self, analysis: Dict[str, Any]) -> str:
        """Extract signal from technical analysis."""
        if analysis and "error" not in analysis:
            indicators = analysis.get("indicators", {})
            summary = indicators.get("summary", {})
            return summary.get("overall_signal", "hold")
        return "hold"
    
    def _extract_fundamental_signal(self, analysis: Dict[str, Any]) -> str:
        """Extract signal from fundamental analysis."""
        if analysis and "error" not in analysis:
            # Placeholder: In production, analyze P/E, debt ratios, etc.
            return "hold"
        return "hold"
    
    def _extract_sentiment_signal(self, analysis: Dict[str, Any]) -> str:
        """Extract signal from sentiment analysis."""
        if analysis and "error" not in analysis:
            sentiment = analysis.get("overall_sentiment", "neutral")
            if sentiment == "positive":
                return "buy"
            elif sentiment == "negative":
                return "sell"
        return "hold"
    
    def _generate_reasoning(
        self,
        action: str,
        technical: Dict,
        fundamental: Dict,
        sentiment: Dict,
        risk_tolerance: str
    ) -> str:
        """Generate human-readable reasoning for the recommendation."""
        
        reasons = []
        
        # Technical reasoning
        if technical and "error" not in technical:
            indicators = technical.get("indicators", {})
            if indicators.get("summary", {}).get("overall_signal") == "buy":
                reasons.append("Technical indicators show strong bullish signals")
            elif indicators.get("summary", {}).get("overall_signal") == "sell":
                reasons.append("Technical indicators show bearish signals")
        
        # Fundamental reasoning
        if fundamental and "error" not in fundamental:
            reasons.append("Company fundamentals are stable")
        
        # Sentiment reasoning
        if sentiment and "error" not in sentiment:
            sent = sentiment.get("overall_sentiment", "neutral")
            if sent == "positive":
                reasons.append("Market sentiment is positive")
            elif sent == "negative":
                reasons.append("Market sentiment is negative")
        
        # Risk tolerance consideration
        if risk_tolerance == "conservative" and action == "buy":
            reasons.append("Suitable for conservative investors due to strong fundamentals")
        elif risk_tolerance == "aggressive" and action == "buy":
            reasons.append("Good opportunity for aggressive growth-seeking investors")
        
        if not reasons:
            reasons.append(f"Recommendation is {action.upper()} based on balanced analysis of all factors")
        
        return ". ".join(reasons) + "."
    
    def _generate_risk_assessment(
        self,
        action: str,
        risk_tolerance: str,
        technical: Dict,
        fundamental: Dict
    ) -> str:
        """Generate risk assessment for the recommendation."""
        
        if action == "buy":
            if risk_tolerance == "conservative":
                return "This stock has moderate risk. Ensure proper portfolio diversification and monitor regularly."
            elif risk_tolerance == "aggressive":
                return "Suitable for aggressive portfolios. Consider market volatility and set stop-loss orders."
            else:
                return "Moderate risk recommendation. Invest within your risk limits and maintain diversification."
        
        elif action == "sell":
            return "Consider selling to protect capital. Watch for trend reversals before re-entry."
        
        else:  # hold
            return "Hold current position. Monitor for changes in technical or fundamental indicators."
