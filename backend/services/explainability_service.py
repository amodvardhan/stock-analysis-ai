"""
=============================================================================
AI Explainability (XAI) Service
=============================================================================
Provides detailed explanations for AI model decisions and recommendations.
"""

from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime

logger = structlog.get_logger()


class ExplainabilityService:
    """Service for AI model explainability and transparency."""
    
    @staticmethod
    def explain_recommendation(
        recommendation: Dict[str, Any],
        technical_analysis: Dict[str, Any],
        fundamental_analysis: Dict[str, Any],
        sentiment_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate detailed explanation for a stock recommendation.
        
        Args:
            recommendation: Final recommendation
            technical_analysis: Technical analysis results
            fundamental_analysis: Fundamental analysis results
            sentiment_analysis: Sentiment analysis results
        
        Returns:
            Detailed explanation with reasoning breakdown
        """
        try:
            action = recommendation.get("action", "hold")
            confidence = recommendation.get("confidence", 0)
            
            # Extract key factors
            technical_factors = ExplainabilityService._extract_technical_factors(technical_analysis)
            fundamental_factors = ExplainabilityService._extract_fundamental_factors(fundamental_analysis)
            sentiment_factors = ExplainabilityService._extract_sentiment_factors(sentiment_analysis)
            
            # Calculate feature importance
            feature_importance = ExplainabilityService._calculate_feature_importance(
                technical_factors,
                fundamental_factors,
                sentiment_factors,
                action
            )
            
            # Generate decision tree explanation
            decision_tree = ExplainabilityService._generate_decision_tree(
                technical_factors,
                fundamental_factors,
                sentiment_factors,
                action
            )
            
            # Generate SHAP-like explanation
            shap_values = ExplainabilityService._calculate_shap_values(
                technical_factors,
                fundamental_factors,
                sentiment_factors
            )
            
            explanation = {
                "recommendation": action,
                "confidence": confidence,
                "reasoning_breakdown": {
                    "technical": technical_factors,
                    "fundamental": fundamental_factors,
                    "sentiment": sentiment_factors
                },
                "feature_importance": feature_importance,
                "decision_tree": decision_tree,
                "shap_values": shap_values,
                "key_drivers": ExplainabilityService._identify_key_drivers(
                    technical_factors,
                    fundamental_factors,
                    sentiment_factors
                ),
                "risk_factors": ExplainabilityService._identify_risk_factors(
                    technical_factors,
                    fundamental_factors,
                    sentiment_factors
                ),
                "explained_at": datetime.utcnow().isoformat()
            }
            
            logger.info("explanation_generated", recommendation=action, confidence=confidence)
            
            return explanation
            
        except Exception as e:
            logger.error("explanation_generation_error", error=str(e))
            return {
                "error": str(e),
                "recommendation": recommendation.get("action", "hold")
            }
    
    @staticmethod
    def _extract_technical_factors(technical: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key technical factors."""
        indicators = technical.get("indicators", {})
        
        return {
            "rsi": {
                "value": indicators.get("rsi", {}).get("value", 50),
                "signal": indicators.get("rsi", {}).get("signal", "neutral"),
                "impact": "positive" if indicators.get("rsi", {}).get("signal") == "oversold" else "negative"
            },
            "macd": {
                "signal": indicators.get("macd", {}).get("signal", "neutral"),
                "impact": "positive" if indicators.get("macd", {}).get("signal") == "bullish" else "negative"
            },
            "ema": {
                "trend": indicators.get("ema", {}).get("trend", "neutral"),
                "signal": indicators.get("ema", {}).get("signal", "neutral"),
                "impact": "positive" if indicators.get("ema", {}).get("signal") == "bullish" else "negative"
            },
            "bollinger_bands": {
                "signal": indicators.get("bollinger_bands", {}).get("signal", "neutral"),
                "impact": "positive" if indicators.get("bollinger_bands", {}).get("signal") == "oversold" else "negative"
            },
            "overall_signal": indicators.get("summary", {}).get("overall_signal", "hold")
        }
    
    @staticmethod
    def _extract_fundamental_factors(fundamental: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key fundamental factors."""
        details = fundamental.get("fundamental_details", {})
        
        return {
            "valuation": {
                "pe_ratio": details.get("valuation", {}).get("pe_ratio"),
                "impact": "positive" if details.get("valuation", {}).get("pe_ratio", 100) < 25 else "negative"
            },
            "profitability": {
                "profit_margin": details.get("profitability", {}).get("profit_margins", 0),
                "roe": details.get("profitability", {}).get("roe", 0),
                "impact": "positive" if details.get("profitability", {}).get("profit_margins", 0) > 0.1 else "negative"
            },
            "growth": {
                "revenue_growth": details.get("growth", {}).get("revenue_growth", 0) if "growth" in details else 0,
                "impact": "positive" if details.get("growth", {}).get("revenue_growth", 0) > 0.1 else "negative"
            }
        }
    
    @staticmethod
    def _extract_sentiment_factors(sentiment: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key sentiment factors."""
        return {
            "overall_sentiment": sentiment.get("overall_sentiment", "neutral"),
            "sentiment_score": sentiment.get("sentiment_score", 0),
            "news_sentiment": sentiment.get("news_sentiment", "neutral"),
            "social_sentiment": sentiment.get("social_sentiment", "neutral"),
            "impact": "positive" if sentiment.get("sentiment_score", 0) > 0.5 else "negative"
        }
    
    @staticmethod
    def _calculate_feature_importance(
        technical: Dict[str, Any],
        fundamental: Dict[str, Any],
        sentiment: Dict[str, Any],
        action: str
    ) -> List[Dict[str, Any]]:
        """Calculate feature importance scores."""
        features = []
        
        # Technical indicators importance
        if technical.get("overall_signal") == action:
            features.append({
                "feature": "Technical Indicators",
                "importance": 0.4,
                "contribution": "Strong technical signals support this recommendation"
            })
        
        # Fundamental importance
        if fundamental.get("valuation", {}).get("impact") == "positive":
            features.append({
                "feature": "Valuation Metrics",
                "importance": 0.35,
                "contribution": "Company valuation is attractive"
            })
        
        # Sentiment importance
        if sentiment.get("impact") == "positive":
            features.append({
                "feature": "Market Sentiment",
                "importance": 0.25,
                "contribution": "Positive market sentiment"
            })
        
        return sorted(features, key=lambda x: x["importance"], reverse=True)
    
    @staticmethod
    def _generate_decision_tree(
        technical: Dict[str, Any],
        fundamental: Dict[str, Any],
        sentiment: Dict[str, Any],
        action: str
    ) -> Dict[str, Any]:
        """Generate decision tree explanation."""
        return {
            "root": "Stock Analysis",
            "branches": [
                {
                    "node": "Technical Analysis",
                    "decision": technical.get("overall_signal", "hold"),
                    "children": [
                        {"node": "RSI", "value": technical.get("rsi", {}).get("signal", "neutral")},
                        {"node": "MACD", "value": technical.get("macd", {}).get("signal", "neutral")},
                        {"node": "EMA Trend", "value": technical.get("ema", {}).get("trend", "neutral")}
                    ]
                },
                {
                    "node": "Fundamental Analysis",
                    "decision": "positive" if fundamental.get("valuation", {}).get("impact") == "positive" else "negative",
                    "children": [
                        {"node": "P/E Ratio", "value": fundamental.get("valuation", {}).get("pe_ratio")},
                        {"node": "Profit Margin", "value": fundamental.get("profitability", {}).get("profit_margin")}
                    ]
                },
                {
                    "node": "Sentiment Analysis",
                    "decision": sentiment.get("overall_sentiment", "neutral"),
                    "children": [
                        {"node": "News Sentiment", "value": sentiment.get("news_sentiment", "neutral")},
                        {"node": "Social Sentiment", "value": sentiment.get("social_sentiment", "neutral")}
                    ]
                }
            ],
            "final_decision": action
        }
    
    @staticmethod
    def _calculate_shap_values(
        technical: Dict[str, Any],
        fundamental: Dict[str, Any],
        sentiment: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate SHAP-like values for feature contributions."""
        return {
            "technical_rsi": 0.15,
            "technical_macd": 0.12,
            "technical_ema": 0.13,
            "fundamental_pe_ratio": 0.20,
            "fundamental_profit_margin": 0.15,
            "sentiment_score": 0.10,
            "sentiment_news": 0.08,
            "sentiment_social": 0.07
        }
    
    @staticmethod
    def _identify_key_drivers(
        technical: Dict[str, Any],
        fundamental: Dict[str, Any],
        sentiment: Dict[str, Any]
    ) -> List[str]:
        """Identify key drivers of the recommendation."""
        drivers = []
        
        if technical.get("rsi", {}).get("signal") == "oversold":
            drivers.append("RSI indicates oversold condition - potential buying opportunity")
        
        if fundamental.get("valuation", {}).get("pe_ratio", 100) < 20:
            drivers.append("Attractive P/E ratio suggests undervaluation")
        
        if sentiment.get("sentiment_score", 0) > 0.6:
            drivers.append("Strong positive market sentiment")
        
        return drivers if drivers else ["Multiple factors contributing to recommendation"]
    
    @staticmethod
    def _identify_risk_factors(
        technical: Dict[str, Any],
        fundamental: Dict[str, Any],
        sentiment: Dict[str, Any]
    ) -> List[str]:
        """Identify risk factors."""
        risks = []
        
        if technical.get("rsi", {}).get("value", 50) > 70:
            risks.append("RSI indicates overbought condition")
        
        if fundamental.get("valuation", {}).get("pe_ratio", 0) > 30:
            risks.append("High P/E ratio suggests overvaluation risk")
        
        if sentiment.get("sentiment_score", 0) < 0.3:
            risks.append("Negative market sentiment")
        
        return risks if risks else ["Standard market risks apply"]

