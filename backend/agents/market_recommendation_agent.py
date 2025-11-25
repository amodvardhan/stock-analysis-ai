"""
=============================================================================
AI Hub - Market Recommendation Agent
=============================================================================
High-level AI agent for market-wide stock recommendations.

This agent:
- Analyzes multiple stocks comparatively
- Understands market trends and sector performance
- Ranks stocks using deep AI reasoning
- Provides market-wide insights and context
- Generates sophisticated comparative analysis

This is different from the single-stock RecommendationAgent which synthesizes
analyses for one stock. This agent works at the market level.
=============================================================================
"""

from typing import List, Dict, Any, Optional
from langchain_core.runnables import RunnableConfig
import structlog
import json

from agents.base_agent import BaseAgent

logger = structlog.get_logger()


class MarketRecommendationAgent(BaseAgent):
    """
    AI agent that performs market-wide comparative analysis and ranking.
    
    This agent:
    1. Receives multiple stock analyses
    2. Performs comparative analysis using LLM
    3. Ranks stocks based on deep market understanding
    4. Provides market context and trends
    5. Generates sophisticated reasoning for each recommendation
    """
    
    def __init__(self):
        """Initialize market recommendation agent."""
        super().__init__(
            name="MarketRecommendationAgent",
            system_prompt="""You are an expert financial market analyst specializing in comparative stock analysis and market-wide recommendations.

Your expertise includes:
- Deep understanding of market trends and sector performance
- Comparative analysis across multiple stocks
- Risk-adjusted return evaluation
- Market timing and entry/exit strategies
- Portfolio optimization insights

When analyzing stocks:
1. Consider market conditions and sector trends
2. Compare stocks relative to each other, not just individually
3. Factor in market volatility and risk-adjusted returns
4. Consider correlation and diversification benefits
5. Evaluate both short-term momentum and long-term fundamentals
6. Provide clear, actionable rankings with detailed reasoning

Be thorough, analytical, and provide deep insights that help investors make informed decisions.
Focus on accuracy and risk management, as real money is involved.""",
            model="gpt-4o",
            temperature=0.1  # Lower temperature for more consistent, analytical responses
        )
    
    async def rank_stocks(
        self,
        stock_analyses: List[Dict[str, Any]],
        market: str,
        period: str,
        user_risk_tolerance: str = "moderate",
        config: RunnableConfig | None = None
    ) -> List[Dict[str, Any]]:
        """
        Rank and analyze multiple stocks using deep AI comparative analysis.
        
        Args:
            stock_analyses: List of stock analysis results (from analyze_stock)
            market: Market identifier
            period: Analysis period (daily/weekly)
            user_risk_tolerance: User's risk profile
            config: Optional LangChain config
        
        Returns:
            List of ranked stocks with enhanced recommendations and reasoning
        """
        logger.info(
            "market_recommendation_ranking_started",
            stocks_count=len(stock_analyses),
            market=market,
            period=period
        )
        
        try:
            # Prepare analysis summary for LLM
            analysis_summary = self._prepare_analysis_summary(stock_analyses)
            
            # Generate comparative analysis prompt
            prompt = self._build_comparative_analysis_prompt(
                analysis_summary,
                market,
                period,
                user_risk_tolerance
            )
            
            # Get LLM comparative analysis using the chain
            llm_response = await self.chain.ainvoke(
                {"input": prompt},
                config=config
            )
            
            # Parse LLM response
            ranked_stocks = self._parse_llm_ranking(llm_response, stock_analyses)
            
            # Enhance with market context
            enhanced_rankings = self._enhance_with_market_context(
                ranked_stocks,
                market,
                period
            )
            
            logger.info(
                "market_recommendation_ranking_completed",
                stocks_ranked=len(enhanced_rankings)
            )
            
            return enhanced_rankings
            
        except Exception as e:
            logger.error("market_recommendation_ranking_failed", error=str(e))
            # Fallback to simple scoring-based ranking
            return self._fallback_ranking(stock_analyses)
    
    def _prepare_analysis_summary(self, stock_analyses: List[Dict[str, Any]]) -> str:
        """Prepare a summary of all stock analyses for LLM."""
        summaries = []
        
        for analysis in stock_analyses:
            symbol = analysis.get("symbol", "UNKNOWN")
            final_rec = analysis.get("final_recommendation", {})
            tech = analysis.get("analyses", {}).get("technical", {})
            fund = analysis.get("analyses", {}).get("fundamental", {})
            sent = analysis.get("analyses", {}).get("sentiment", {})
            
            # Extract key metrics
            current_price = tech.get("technical_details", {}).get("indicators", {}).get("ema", {}).get("current_price", 0)
            tech_signal = tech.get("technical_details", {}).get("summary", {}).get("overall_signal", "hold")
            confidence = final_rec.get("confidence", 0)
            action = final_rec.get("action", "hold")
            
            summary = f"""
Stock: {symbol}
- Current Price: {current_price}
- AI Recommendation: {action.upper()} (Confidence: {confidence}%)
- Technical Signal: {tech_signal.upper()}
- Key Technical Indicators: {self._extract_tech_summary(tech)}
- Fundamental Status: {self._extract_fund_summary(fund)}
- Sentiment: {self._extract_sentiment_summary(sent)}
"""
            summaries.append(summary)
        
        return "\n".join(summaries)
    
    def _extract_tech_summary(self, tech_analysis: Dict[str, Any]) -> str:
        """Extract key technical indicators summary."""
        if not tech_analysis or "error" in tech_analysis:
            return "Data unavailable"
        
        indicators = tech_analysis.get("technical_details", {}).get("indicators", {})
        summary = indicators.get("summary", {})
        
        bullish = summary.get("bullish_indicators", 0)
        bearish = summary.get("bearish_indicators", 0)
        confidence = summary.get("confidence", 0)
        
        return f"{bullish} bullish, {bearish} bearish indicators (Confidence: {confidence}%)"
    
    def _extract_fund_summary(self, fund_analysis: Dict[str, Any]) -> str:
        """Extract fundamental analysis summary."""
        if not fund_analysis or "error" in fund_analysis:
            return "Analysis unavailable"
        
        details = fund_analysis.get("fundamental_details", {})
        valuation = details.get("valuation_metrics", {})
        pe_ratio = valuation.get("pe_ratio")
        
        if pe_ratio:
            if pe_ratio < 15:
                return f"Undervalued (P/E: {pe_ratio:.1f})"
            elif pe_ratio > 30:
                return f"Overvalued (P/E: {pe_ratio:.1f})"
            else:
                return f"Fairly valued (P/E: {pe_ratio:.1f})"
        
        return "Valuation data unavailable"
    
    def _extract_sentiment_summary(self, sent_analysis: Dict[str, Any]) -> str:
        """Extract sentiment analysis summary."""
        if not sent_analysis or "error" in sent_analysis:
            return "Neutral"
        
        details = sent_analysis.get("sentiment_details", {})
        overall = details.get("overall_sentiment", "neutral")
        score = details.get("overall_sentiment_score", 0.5)
        
        return f"{overall.upper()} (Score: {score:.2f})"
    
    def _build_comparative_analysis_prompt(
        self,
        analysis_summary: str,
        market: str,
        period: str,
        risk_tolerance: str
    ) -> str:
        """Build prompt for LLM comparative analysis."""
        
        return f"""You are analyzing {len(analysis_summary.split('Stock:')) - 1} stocks in the {market.upper()} market for {period} recommendations.

Here are the detailed analyses for each stock:

{analysis_summary}

Your task:
1. Rank these stocks from BEST to WORST investment opportunity for {period} period
2. Consider: technical momentum, fundamental strength, sentiment, risk-adjusted returns, market conditions
3. For each stock, provide:
   - Rank (1 = best, higher = worse)
   - Enhanced recommendation score (0-100)
   - Detailed reasoning explaining WHY this stock ranks where it does
   - Market context and comparative advantages/disadvantages
   - Risk factors specific to this stock
   - Entry timing and strategy recommendations

User's risk tolerance: {risk_tolerance.upper()}

IMPORTANT:
- Be thorough and analytical
- Consider market trends and sector performance
- Factor in correlation and diversification
- Provide specific, actionable insights
- Real money is involved - accuracy is critical

Respond in JSON format:
{{
  "rankings": [
    {{
      "symbol": "SYMBOL",
      "rank": 1,
      "enhanced_score": 95,
      "reasoning": "Detailed explanation...",
      "market_context": "Market-wide insights...",
      "comparative_advantages": ["Advantage 1", "Advantage 2"],
      "risk_factors": ["Risk 1", "Risk 2"],
      "entry_strategy": "When and how to enter",
      "time_horizon": "Recommended holding period"
    }}
  ],
  "market_overview": "Overall market conditions and trends",
  "sector_insights": "Sector-specific observations"
}}"""
    
    def _parse_llm_ranking(
        self,
        llm_response: Any,
        stock_analyses: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Parse LLM response and merge with stock analyses."""
        
        try:
            # Extract content from LLM response
            # The chain returns a message object with content attribute
            if hasattr(llm_response, 'content'):
                content = llm_response.content
            elif isinstance(llm_response, str):
                content = llm_response
            else:
                # Try to get content from message object
                content = str(llm_response)
                if hasattr(llm_response, 'content'):
                    content = llm_response.content
            
            # Try to extract JSON from response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                parsed = json.loads(json_str)
            else:
                # Fallback: try to parse entire content
                parsed = json.loads(content)
            
            rankings = parsed.get("rankings", [])
            
            # Create a map of symbol to analysis
            analysis_map = {a.get("symbol"): a for a in stock_analyses}
            
            # Merge LLM rankings with original analyses
            enhanced_stocks = []
            for ranking in rankings:
                symbol = ranking.get("symbol")
                if symbol in analysis_map:
                    enhanced = {
                        **analysis_map[symbol],
                        "enhanced_score": ranking.get("enhanced_score", 0),
                        "ai_reasoning": ranking.get("reasoning", ""),
                        "market_context": ranking.get("market_context", ""),
                        "comparative_advantages": ranking.get("comparative_advantages", []),
                        "risk_factors": ranking.get("risk_factors", []),
                        "entry_strategy": ranking.get("entry_strategy", ""),
                        "time_horizon": ranking.get("time_horizon", ""),
                        "rank": ranking.get("rank", 999)
                    }
                    enhanced_stocks.append(enhanced)
            
            # Sort by rank
            enhanced_stocks.sort(key=lambda x: x.get("rank", 999))
            
            return enhanced_stocks
            
        except Exception as e:
            logger.error("llm_ranking_parse_failed", error=str(e))
            # Fallback to simple ranking
            return self._fallback_ranking(stock_analyses)
    
    def _enhance_with_market_context(
        self,
        ranked_stocks: List[Dict[str, Any]],
        market: str,
        period: str
    ) -> List[Dict[str, Any]]:
        """Add market-wide context to rankings."""
        
        # Add market metadata
        for stock in ranked_stocks:
            stock["market_analysis"] = {
                "market": market,
                "period": period,
                "analysis_type": "comparative_market_analysis",
                "ranking_method": "ai_powered_comparative_analysis"
            }
        
        return ranked_stocks
    
    def _fallback_ranking(self, stock_analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fallback ranking when LLM analysis fails."""
        
        logger.warning("using_fallback_ranking", stocks_count=len(stock_analyses))
        
        # Simple score-based ranking
        scored_stocks = []
        for analysis in stock_analyses:
            final_rec = analysis.get("final_recommendation", {})
            confidence = final_rec.get("confidence", 0)
            action = final_rec.get("action", "hold")
            
            # Simple scoring
            if action == "buy":
                score = confidence
            elif action == "hold":
                score = confidence * 0.5
            else:
                score = 0
            
            scored_stocks.append({
                **analysis,
                "enhanced_score": score,
                "ai_reasoning": f"Based on {action.upper()} recommendation with {confidence}% confidence",
                "rank": 0  # Will be set after sorting
            })
        
        # Sort by score
        scored_stocks.sort(key=lambda x: x.get("enhanced_score", 0), reverse=True)
        
        # Assign ranks
        for i, stock in enumerate(scored_stocks):
            stock["rank"] = i + 1
        
        return scored_stocks

