"""
=============================================================================
AI Hub - Recommendation Agent
=============================================================================
Synthesizes all analyses to generate final stock recommendation with
target prices and actionable insights for retail investors.
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
    
    Provides actionable insights including:
    - BUY/SELL/HOLD recommendation
    - Target price
    - Stop loss price
    - Entry price range
    - Time horizon
    - Investment scenarios
    """
    
    def __init__(self):
        """Initialize recommendation agent."""
        super().__init__(
            name="RecommendationSynthesizer",
            system_prompt="""You are an expert financial advisor synthesizing multiple analyses.

Your task:
1. Review technical, fundamental, and sentiment analyses
2. Consider user's risk tolerance
3. Provide a clear BUY, SELL, or HOLD recommendation
4. Calculate target prices and stop loss levels
5. Explain your reasoning concisely
6. Highlight key risks and opportunities

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
        Synthesize all analyses into final recommendation with target prices.
        
        Args:
            symbol: Stock ticker symbol
            technical_analysis: Output from technical agent
            fundamental_analysis: Output from fundamental agent
            sentiment_analysis: Output from sentiment agent
            user_risk_tolerance: User's risk profile
            config: Optional LangChain config
        
        Returns:
            Dict containing final recommendation with target prices
        """
        logger.info("synthesizing_recommendation", symbol=symbol)
        
        try:
            # Extract current price
            current_price = self._extract_current_price(technical_analysis)
            
            # Extract key signals
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
            
            # Calculate target prices based on technical levels
            price_targets = self._calculate_price_targets(
                current_price,
                technical_analysis,
                action,
                user_risk_tolerance
            )
            
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
            
            # Calculate time horizon
            time_horizon = self._calculate_time_horizon(action, user_risk_tolerance)
            
            # Generate investment scenarios
            investment_scenarios = self._generate_investment_scenarios(
                current_price,
                price_targets,
                action
            )
            
            return {
                "action": action,
                "confidence": round(confidence, 2),
                "reasoning": reasoning,
                "risk_assessment": risk_assessment,
                "price_targets": price_targets,
                "time_horizon": time_horizon,
                "investment_scenarios": investment_scenarios,
                "signals": {
                    "technical": tech_signal,
                    "fundamental": fund_signal,
                    "sentiment": sent_signal
                }
            }
            
        except Exception as e:
            logger.error("recommendation_synthesis_failed", symbol=symbol, error=str(e))
            raise Exception(f"Recommendation synthesis failed: {str(e)}")
    
    def _extract_current_price(self, analysis: Dict[str, Any]) -> float:
        """Extract current price from technical analysis."""
        if analysis and "error" not in analysis:
            indicators = analysis.get("indicators", {})
            ema = indicators.get("ema", {})
            return ema.get("current_price", 0)
        return 0
    
    def _calculate_price_targets(
        self,
        current_price: float,
        technical_analysis: Dict[str, Any],
        action: str,
        risk_tolerance: str
    ) -> Dict[str, float]:
        """
        Calculate target prices based on technical levels.
        
        For BUY:
        - Entry: Current price or slightly below
        - Stop Loss: Below key support
        - Target: Above key resistance
        
        For SELL:
        - Exit Price: Current price
        - Stop Loss: Not applicable
        
        For HOLD:
        - Watch Levels: Key support/resistance
        """
        if current_price == 0:
            return {}
        
        indicators = technical_analysis.get("indicators", {}) if technical_analysis else {}
        
        if action == "buy":
            # Calculate based on risk tolerance
            risk_multiplier = {
                "conservative": 0.05,  # 5% risk
                "moderate": 0.08,      # 8% risk
                "aggressive": 0.12     # 12% risk
            }.get(risk_tolerance, 0.08)
            
            reward_multiplier = {
                "conservative": 0.10,  # 10% reward (1:2 risk-reward)
                "moderate": 0.16,      # 16% reward (1:2 risk-reward)
                "aggressive": 0.24     # 24% reward (1:2 risk-reward)
            }.get(risk_tolerance, 0.16)
            
            # Use Bollinger Bands for better targets if available
            bollinger = indicators.get("bollinger_bands", {})
            lower_band = bollinger.get("lower_band")
            upper_band = bollinger.get("upper_band")
            
            entry_price = current_price * 0.98  # Slight dip entry
            stop_loss = lower_band * 0.98 if lower_band else current_price * (1 - risk_multiplier)
            target_price = upper_band * 1.02 if upper_band else current_price * (1 + reward_multiplier)
            
            return {
                "entry_price": round(entry_price, 2),
                "stop_loss": round(stop_loss, 2),
                "target_price": round(target_price, 2),
                "risk_amount": round(entry_price - stop_loss, 2),
                "reward_amount": round(target_price - entry_price, 2),
                "risk_reward_ratio": round((target_price - entry_price) / (entry_price - stop_loss), 2) if (entry_price - stop_loss) > 0 else 0
            }
        
        elif action == "sell":
            return {
                "exit_price": round(current_price, 2),
                "stop_loss": None,
                "target_price": None
            }
        
        else:  # hold
            # Provide watch levels
            bollinger = indicators.get("bollinger_bands", {})
            return {
                "support_level": round(bollinger.get("lower_band", current_price * 0.95), 2),
                "resistance_level": round(bollinger.get("upper_band", current_price * 1.05), 2),
                "current_price": round(current_price, 2)
            }
    
    def _calculate_time_horizon(self, action: str, risk_tolerance: str) -> str:
        """Calculate recommended time horizon."""
        if action == "buy":
            if risk_tolerance == "conservative":
                return "Long-term (6-12 months)"
            elif risk_tolerance == "aggressive":
                return "Short-term (1-3 months)"
            else:
                return "Medium-term (3-6 months)"
        elif action == "sell":
            return "Immediate"
        else:
            return "Ongoing monitoring"
    
    def _generate_investment_scenarios(
        self,
        current_price: float,
        price_targets: Dict[str, float],
        action: str
    ) -> Dict[str, Any]:
        """
        Generate investment scenarios for different investment amounts.
        
        Shows potential profit/loss for $1000, $5000, $10000 investments.
        """
        if action != "buy" or not price_targets or current_price == 0:
            return {}
        
        entry_price = price_targets.get("entry_price", current_price)
        target_price = price_targets.get("target_price", 0)
        stop_loss = price_targets.get("stop_loss", 0)
        
        if target_price == 0:
            return {}
        
        scenarios = {}
        for amount in [1000, 5000, 10000]:
            shares = amount / entry_price
            profit_at_target = (target_price - entry_price) * shares
            loss_at_stop = (entry_price - stop_loss) * shares if stop_loss else 0
            
            scenarios[f"invest_{amount}"] = {
                "investment": amount,
                "shares": round(shares, 2),
                "entry_price": round(entry_price, 2),
                "potential_profit": round(profit_at_target, 2),
                "potential_loss": round(loss_at_stop, 2),
                "profit_percentage": round((profit_at_target / amount) * 100, 2),
                "loss_percentage": round((loss_at_stop / amount) * 100, 2) if loss_at_stop else 0
            }
        
        return scenarios
    
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
        
        if technical and "error" not in technical:
            indicators = technical.get("indicators", {})
            if indicators.get("summary", {}).get("overall_signal") == "buy":
                reasons.append("Technical indicators show strong bullish signals with positive momentum")
            elif indicators.get("summary", {}).get("overall_signal") == "sell":
                reasons.append("Technical indicators show bearish signals and negative momentum")
        
        if fundamental and "error" not in fundamental:
            reasons.append("Company fundamentals are stable")
        
        if sentiment and "error" not in sentiment:
            sent = sentiment.get("overall_sentiment", "neutral")
            if sent == "positive":
                reasons.append("Market sentiment is positive")
            elif sent == "negative":
                reasons.append("Market sentiment is negative")
        
        if risk_tolerance == "conservative" and action == "buy":
            reasons.append("Suitable for conservative investors with focus on capital preservation")
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
                return "This stock has moderate risk. Ensure proper portfolio diversification and monitor regularly. Set strict stop loss."
            elif risk_tolerance == "aggressive":
                return "Suitable for aggressive portfolios. Consider market volatility and set trailing stop-loss orders for profit protection."
            else:
                return "Moderate risk recommendation. Invest within your risk limits and maintain diversification. Use stop loss orders."
        
        elif action == "sell":
            return "Consider selling to protect capital. Watch for trend reversals before re-entry. Book profits/cut losses as per your plan."
        
        else:  # hold
            return "Hold current position. Monitor for changes in technical or fundamental indicators. Set price alerts at key levels."
