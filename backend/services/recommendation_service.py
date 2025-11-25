"""
=============================================================================
AI Hub - Stock Recommendation Service
=============================================================================
Deep market analysis service for recommending top stocks.

This service:
- Analyzes multiple stocks using the multi-agent AI system
- Ranks stocks based on comprehensive analysis
- Provides historical context and forecasts
- Generates detailed reasoning for each recommendation
=============================================================================
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
import structlog
import asyncio
import statistics

from agents.orchestrator import analyze_stock
from agents.market_recommendation_agent import MarketRecommendationAgent
from db.models import Stock, StockAnalysis, MarketType
from agents.tools.stock_price_tool import get_stock_price

logger = structlog.get_logger()


class RecommendationService:
    """Service for generating AI-powered stock recommendations."""
    
    # Popular stocks to analyze (can be expanded or made configurable)
    INDIA_NSE_STOCKS = [
        ("RELIANCE", "Reliance Industries Ltd"),
        ("TCS", "Tata Consultancy Services Ltd"),
        ("HDFCBANK", "HDFC Bank Ltd"),
        ("INFY", "Infosys Ltd"),
        ("ICICIBANK", "ICICI Bank Ltd"),
        ("HINDUNILVR", "Hindustan Unilever Ltd"),
        ("ITC", "ITC Ltd"),
        ("SBIN", "State Bank of India"),
        ("BHARTIARTL", "Bharti Airtel Ltd"),
        ("KOTAKBANK", "Kotak Mahindra Bank Ltd"),
        ("LT", "Larsen & Toubro Ltd"),
        ("AXISBANK", "Axis Bank Ltd"),
        ("ASIANPAINT", "Asian Paints Ltd"),
        ("MARUTI", "Maruti Suzuki India Ltd"),
        ("TITAN", "Titan Company Ltd"),
    ]
    
    US_STOCKS = [
        ("AAPL", "Apple Inc"),
        ("MSFT", "Microsoft Corporation"),
        ("GOOGL", "Alphabet Inc"),
        ("AMZN", "Amazon.com Inc"),
        ("TSLA", "Tesla Inc"),
        ("META", "Meta Platforms Inc"),
        ("NVDA", "NVIDIA Corporation"),
        ("JPM", "JPMorgan Chase & Co"),
        ("V", "Visa Inc"),
        ("JNJ", "Johnson & Johnson"),
    ]
    
    @staticmethod
    async def get_top_stocks(
        db: AsyncSession,
        market: str = "india_nse",
        period: str = "daily",
        limit: int = 5,
        user_risk_tolerance: str = "moderate"
    ) -> List[Dict[str, Any]]:
        """
        Get top recommended stocks based on deep AI analysis.
        
        Args:
            db: Database session
            market: Market identifier (india_nse, india_bse, us_nyse, us_nasdaq)
            period: Analysis period (daily or weekly)
            limit: Number of top stocks to return
            user_risk_tolerance: User's risk profile
        
        Returns:
            List of top stocks with detailed analysis and reasoning
        """
        logger.info(
            "top_stocks_analysis_started",
            market=market,
            period=period,
            limit=limit
        )
        
        # Select stocks to analyze based on market
        if market.startswith("india"):
            stocks_to_analyze = RecommendationService.INDIA_NSE_STOCKS
        else:
            stocks_to_analyze = RecommendationService.US_STOCKS
        
        # Analyze all stocks in parallel (with concurrency limit)
        analysis_tasks = []
        for symbol, company_name in stocks_to_analyze[:15]:  # Limit to 15 for performance
            task = RecommendationService._analyze_stock_for_recommendation(
                symbol=symbol,
                market=market,
                company_name=company_name,
                user_risk_tolerance=user_risk_tolerance,
                period=period
            )
            analysis_tasks.append(task)
        
        # Run analyses with concurrency limit (analyze 3 at a time)
        semaphore = asyncio.Semaphore(3)
        
        async def analyze_with_limit(task):
            async with semaphore:
                return await task
        
        results = await asyncio.gather(
            *[analyze_with_limit(task) for task in analysis_tasks],
            return_exceptions=True
        )
        
        # Filter out failed analyses and extract valid results
        valid_results = []
        failed_count = 0
        for result in results:
            if isinstance(result, Exception):
                logger.error("stock_analysis_failed_in_batch", error=str(result))
                failed_count += 1
                continue
            if result and result.get("score") is not None:
                valid_results.append(result)
            else:
                failed_count += 1
        
        logger.info(
            "stock_analysis_batch_completed",
            market=market,
            total=len(results),
            valid=len(valid_results),
            failed=failed_count
        )
        
        if not valid_results:
            logger.warning("no_valid_analyses_for_ranking", market=market, total_attempted=len(results))
            # Return empty list - let the API handle the 503 response
            return []
        
        # Use AI Market Recommendation Agent for intelligent comparative ranking
        # Note: MarketRecommendationAgent is used here (not in orchestrator) because:
        # - Orchestrator handles SINGLE stock analysis (Technical → Fundamental → Sentiment → Recommendation)
        # - MarketRecommendationAgent handles MULTIPLE stocks comparative ranking
        # - This is a higher-level operation that happens AFTER individual stock analyses
        # See backend/AGENT_ARCHITECTURE.md for detailed explanation
        try:
            logger.info("using_ai_market_recommendation_agent", stocks_count=len(valid_results))
            
            # Prepare stock analyses in format expected by agent
            # The agent expects the format from analyze_stock() output
            stock_analyses = []
            for result in valid_results:
                # Reconstruct analysis format matching analyze_stock output structure
                analysis_format = {
                    "symbol": result.get("symbol"),
                    "market": result.get("market"),
                    "final_recommendation": {
                        "action": result.get("recommendation", "hold"),
                        "confidence": result.get("confidence", 0),
                        "final_recommendation": result.get("recommendation", "hold")  # For compatibility
                    },
                    "analyses": {
                        "technical": {
                            "technical_details": result.get("technical_indicators", {}),
                            "indicators": result.get("technical_indicators", {}).get("indicators", {})
                        },
                        "fundamental": {
                            "fundamental_details": result.get("fundamental_metrics", {})
                        },
                        "sentiment": {
                            "sentiment_details": {
                                "overall_sentiment": "positive" if result.get("sentiment_score", 0.5) > 0.6 else 
                                                     "negative" if result.get("sentiment_score", 0.5) < 0.4 else "neutral",
                                "overall_sentiment_score": result.get("sentiment_score", 0.5)
                            }
                        }
                    }
                }
                stock_analyses.append(analysis_format)
            
            # Get AI-powered comparative ranking
            market_agent = MarketRecommendationAgent()
            ai_ranked = await market_agent.rank_stocks(
                stock_analyses=stock_analyses,
                market=market,
                period=period,
                user_risk_tolerance=user_risk_tolerance
            )
            
            # Merge AI rankings back with our detailed results
            result_map = {r.get("symbol"): r for r in valid_results}
            enhanced_results = []
            
            for ai_stock in ai_ranked:
                symbol = ai_stock.get("symbol")
                if symbol in result_map:
                    # Merge AI insights with our detailed data
                    enhanced = {
                        **result_map[symbol],
                        "score": ai_stock.get("enhanced_score", result_map[symbol].get("score", 0)),
                        "rank": ai_stock.get("rank", 999),
                        "ai_reasoning": ai_stock.get("ai_reasoning", result_map[symbol].get("reasoning", "")),
                        "market_context": ai_stock.get("market_context", ""),
                        "comparative_advantages": ai_stock.get("comparative_advantages", []),
                        "risk_factors": ai_stock.get("risk_factors", []),
                        "entry_strategy": ai_stock.get("entry_strategy", ""),
                        "time_horizon": ai_stock.get("time_horizon", "")
                    }
                    enhanced_results.append(enhanced)
            
            # Sort by AI rank
            enhanced_results.sort(key=lambda x: x.get("rank", 999))
            
            # Get top N stocks
            top_stocks = enhanced_results[:limit]
            
            logger.info(
                "ai_ranking_completed",
                market=market,
                period=period,
                stocks_analyzed=len(analysis_tasks),
                valid_results=len(valid_results),
                ai_ranked=len(enhanced_results),
                top_stocks_returned=len(top_stocks)
            )
            
            return top_stocks
            
        except Exception as e:
            logger.error("ai_market_ranking_failed", error=str(e), fallback="using_score_based_ranking")
            # Fallback to score-based ranking if AI ranking fails
            valid_results.sort(key=lambda x: x.get("score", 0), reverse=True)
            top_stocks = valid_results[:limit]
            
            logger.info(
                "top_stocks_analysis_completed_fallback",
                market=market,
                period=period,
                stocks_analyzed=len(analysis_tasks),
                valid_results=len(valid_results),
                top_stocks_returned=len(top_stocks)
            )
            
            return top_stocks
    
    @staticmethod
    async def _analyze_stock_for_recommendation(
        symbol: str,
        market: str,
        company_name: str,
        user_risk_tolerance: str,
        period: str
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze a single stock and prepare it for recommendation ranking.
        
        Returns:
            Dict with stock analysis and recommendation score
        """
        try:
            # Get current price and historical data
            # LangChain tool needs to be called with ainvoke and dict
            price_data = await get_stock_price.ainvoke({
                "symbol": symbol,
                "market": market,
                "period": "1y"
            })
            
            if not price_data or not price_data.get("current_price"):
                logger.warning("no_price_data", symbol=symbol)
                return None
            
            current_price = price_data["current_price"]
            
            # Extract historical prices from the data structure
            historical_data = price_data.get("historical_data", [])
            historical_prices = [item.get("close", current_price) for item in historical_data] if historical_data else [current_price]
            
            # If no historical data, create a simple list with current price
            if not historical_prices:
                historical_prices = [current_price]
            
            # Run deep AI analysis
            analysis_result = await analyze_stock(
                symbol=symbol,
                market=market,
                company_name=company_name,
                user_risk_tolerance=user_risk_tolerance
            )
            
            if not analysis_result or not analysis_result.get("final_recommendation"):
                logger.warning("no_analysis_result", symbol=symbol)
                return None
            
            final_rec = analysis_result.get("final_recommendation", {})
            tech_analysis = analysis_result.get("analyses", {}).get("technical", {})
            fund_analysis = analysis_result.get("analyses", {}).get("fundamental", {})
            sent_analysis = analysis_result.get("analyses", {}).get("sentiment", {})
            
            # Handle case where final_recommendation might have error
            # But still allow partial analysis if we have technical and sentiment data
            if not final_rec or "error" in final_rec:
                # Check if we have at least technical analysis
                if tech_analysis and not tech_analysis.get("error"):
                    logger.warning(
                        "analysis_result_has_error_but_continuing",
                        symbol=symbol,
                        error=final_rec.get("error", "Unknown error"),
                        has_technical=True,
                        has_fundamental=bool(fund_analysis and not fund_analysis.get("error")),
                        has_sentiment=bool(sent_analysis and not sent_analysis.get("error"))
                    )
                    # Create a minimal final_recommendation from technical analysis
                    tech_summary = tech_analysis.get("technical_details", {}).get("summary", {})
                    tech_signal = tech_summary.get("overall_signal", "hold")
                    tech_confidence = tech_summary.get("confidence", 50)
                    
                    final_rec = {
                        "action": tech_signal if tech_signal in ["buy", "sell", "hold"] else "hold",
                        "confidence": tech_confidence,
                        "risk_level": "medium",
                        "note": "Recommendation based on technical analysis only - fundamental data unavailable"
                    }
                else:
                    logger.warning("analysis_result_has_error_no_fallback", symbol=symbol, error=final_rec.get("error", "Unknown error"))
                    return None
            
            # Calculate recommendation score (0-100)
            score = RecommendationService._calculate_recommendation_score(
                final_rec=final_rec,
                tech_analysis=tech_analysis,
                fund_analysis=fund_analysis,
                sent_analysis=sent_analysis,
                price_data=price_data,
                period=period
            )
            
            # Only include stocks with positive recommendation
            # Lower threshold when using fallback data to ensure we return recommendations
            # Check if we're using fallback data (fundamental or price data)
            using_fallback = (
                fund_analysis and fund_analysis.get("data_source") == "fallback"
            ) or (
                price_data and price_data.get("data_source") == "fallback"
            )
            
            # Adjust threshold based on data quality
            min_score = 30 if using_fallback else 50
            
            if score < min_score:
                logger.debug(
                    "stock_filtered_by_score",
                    symbol=symbol,
                    score=score,
                    min_score=min_score,
                    using_fallback=using_fallback
                )
                return None
            
            # Generate detailed reasoning (will be enhanced by AI agent later)
            reasoning = RecommendationService._generate_reasoning(
                symbol=symbol,
                company_name=company_name,
                final_rec=final_rec,
                tech_analysis=tech_analysis,
                fund_analysis=fund_analysis,
                sent_analysis=sent_analysis,
                price_data=price_data,
                period=period
            )
            
            # Note: AI reasoning will be added by MarketRecommendationAgent
            
            # Calculate historical performance
            historical_performance = RecommendationService._calculate_historical_performance(
                historical_prices,
                period,
                current_price=current_price
            )
            
            # Generate forecast
            forecast = RecommendationService._generate_forecast(
                current_price=current_price,
                tech_analysis=tech_analysis,
                fund_analysis=fund_analysis,
                historical_performance=historical_performance
            )
            
            return {
                "symbol": symbol,
                "company_name": company_name,
                "market": market,
                "current_price": current_price,
                "score": score,
                "recommendation": final_rec.get("action", "hold"),
                "confidence": final_rec.get("confidence", 0),
                "reasoning": reasoning,
                "historical_performance": historical_performance,
                "forecast": forecast,
                "technical_indicators": tech_analysis.get("technical_details", {}),
                "fundamental_metrics": fund_analysis.get("fundamental_details", {}),
                "sentiment_score": sent_analysis.get("sentiment_details", {}).get("overall_sentiment_score", 0),
                "risk_level": final_rec.get("risk_level", "medium"),
                "price_history": historical_prices[-30:] if historical_prices else [],  # Last 30 days
                "analyzed_at": datetime.utcnow().isoformat(),
                # Fields that will be populated by MarketRecommendationAgent:
                "rank": None,
                "ai_reasoning": None,
                "market_context": None,
                "comparative_advantages": None,
                "risk_factors": None,
                "entry_strategy": None,
                "time_horizon": None
            }
            
        except Exception as e:
            logger.error("stock_recommendation_analysis_failed", symbol=symbol, error=str(e))
            return None
    
    @staticmethod
    def _calculate_recommendation_score(
        final_rec: Dict[str, Any],
        tech_analysis: Dict[str, Any],
        fund_analysis: Dict[str, Any],
        sent_analysis: Dict[str, Any],
        price_data: Dict[str, Any],
        period: str
    ) -> float:
        """
        Calculate a composite recommendation score (0-100).
        
        Higher score = better recommendation.
        """
        score = 0.0
        
        # Check if using fallback data - adjust scoring accordingly
        using_fallback = (
            fund_analysis and fund_analysis.get("data_source") == "fallback"
        ) or (
            price_data and price_data.get("data_source") == "fallback"
        )
        
        # Base recommendation score (0-40 points)
        action = final_rec.get("action", "hold")
        confidence = final_rec.get("confidence", 0) / 100.0
        
        if action == "strong_buy":
            score += 40 * confidence
        elif action == "buy":
            score += 30 * confidence
        elif action == "hold":
            # Give more points for hold when using fallback data
            score += (20 if using_fallback else 15) * confidence
        else:
            score += 0  # Sell recommendations get 0
        
        # Technical analysis score (0-25 points)
        tech_indicators = tech_analysis.get("technical_details", {}) if tech_analysis and not tech_analysis.get("error") else {}
        tech_summary = tech_indicators.get("summary", {})
        tech_signal = tech_summary.get("overall_signal", "hold")
        
        if tech_signal == "buy":
            score += 25
        elif tech_signal == "hold":
            # Give more points for hold when using fallback data
            score += (15 if using_fallback else 12)
        else:
            score += 5
        
        # Fundamental analysis score (0-20 points)
        # Handle missing fundamental data gracefully
        fund_details = fund_analysis.get("fundamental_details", {}) if fund_analysis and not fund_analysis.get("error") else {}
        pe_ratio = fund_details.get("valuation_metrics", {}).get("pe_ratio") if fund_details else None
        
        if pe_ratio:
            if 10 <= pe_ratio <= 25:  # Reasonable P/E range
                score += 20
            elif 5 <= pe_ratio < 10:
                score += 15
            elif 25 < pe_ratio <= 35:
                score += 10
            else:
                score += 5
        else:
            # If fundamental data is missing, give neutral score (10 points)
            # This allows analysis to continue with technical and sentiment data
            score += 10
        
        # Sentiment score (0-10 points)
        sent_details = sent_analysis.get("sentiment_details", {})
        sentiment_score = sent_details.get("overall_sentiment_score", 0)
        
        if sentiment_score > 0.6:
            score += 10
        elif sentiment_score > 0.4:
            score += 7
        elif sentiment_score > 0.2:
            score += 4
        else:
            score += 2
        
        # Price momentum (0-5 points)
        historical = price_data.get("historical_prices", [])
        if len(historical) >= 2:
            recent_change = ((historical[-1] - historical[-2]) / historical[-2]) * 100
            if recent_change > 2:
                score += 5
            elif recent_change > 0:
                score += 3
            else:
                score += 1
        
        return min(score, 100.0)  # Cap at 100
    
    @staticmethod
    def _generate_reasoning(
        symbol: str,
        company_name: str,
        final_rec: Dict[str, Any],
        tech_analysis: Dict[str, Any],
        fund_analysis: Dict[str, Any],
        sent_analysis: Dict[str, Any],
        price_data: Dict[str, Any],
        period: str
    ) -> str:
        """Generate detailed reasoning for the recommendation."""
        
        reasoning_parts = []
        
        # Recommendation summary
        action = final_rec.get("action", "hold")
        confidence = final_rec.get("confidence", 0)
        reasoning_parts.append(
            f"{company_name} ({symbol}) receives a {action.upper()} recommendation "
            f"with {confidence}% confidence."
        )
        
        # Technical analysis reasoning
        tech_indicators = tech_analysis.get("technical_details", {})
        tech_summary = tech_indicators.get("summary", {})
        tech_signal = tech_summary.get("overall_signal", "hold")
        bullish_indicators = tech_summary.get("bullish_indicators", 0)
        bearish_indicators = tech_summary.get("bearish_indicators", 0)
        
        reasoning_parts.append(
            f"Technical analysis shows a {tech_signal.upper()} signal with "
            f"{bullish_indicators} bullish and {bearish_indicators} bearish indicators."
        )
        
        # Fundamental analysis reasoning
        fund_details = fund_analysis.get("fundamental_details", {})
        pe_ratio = fund_details.get("valuation_metrics", {}).get("pe_ratio")
        
        if pe_ratio:
            reasoning_parts.append(
                f"Fundamental analysis indicates a P/E ratio of {pe_ratio:.2f}, "
                f"suggesting {'reasonable' if 10 <= pe_ratio <= 25 else 'valuation concerns'}."
            )
        
        # Sentiment reasoning
        sent_details = sent_analysis.get("sentiment_details", {})
        sentiment_score = sent_details.get("overall_sentiment_score", 0)
        
        if sentiment_score > 0.6:
            reasoning_parts.append("Market sentiment is strongly positive.")
        elif sentiment_score > 0.4:
            reasoning_parts.append("Market sentiment is moderately positive.")
        elif sentiment_score < 0.3:
            reasoning_parts.append("Market sentiment shows concerns.")
        
        # Price trend
        historical = price_data.get("historical_prices", [])
        if len(historical) >= 7:
            week_change = ((historical[-1] - historical[-7]) / historical[-7]) * 100
            if week_change > 5:
                reasoning_parts.append(f"Price has increased {week_change:.1f}% over the past week.")
            elif week_change < -5:
                reasoning_parts.append(f"Price has declined {week_change:.1f}% over the past week.")
        
        # Risk assessment
        risk_level = final_rec.get("risk_level", "medium")
        reasoning_parts.append(f"Risk assessment: {risk_level.upper()} risk level.")
        
        return " ".join(reasoning_parts)
    
    @staticmethod
    def _calculate_historical_performance(
        historical_prices: List[float],
        period: str,
        current_price: float = None
    ) -> Dict[str, Any]:
        """Calculate historical performance metrics."""
        
        # Use current_price if provided, otherwise use last historical price
        if not historical_prices or len(historical_prices) < 1:
            # If no historical prices, use current_price or default to 0
            current = current_price if current_price is not None else 0
            return {
                "current_price": current,
                "high_52w": current,
                "low_52w": current,
                "1d_change": 0,
                "7d_change": 0,
                "30d_change": 0,
                "90d_change": 0,
                "volatility": 0
            }
        
        current = current_price if current_price is not None else historical_prices[-1]
        
        # Calculate changes - ensure all required fields are always present
        changes = {
            "1d_change": 0,
            "7d_change": 0,
            "30d_change": 0,
            "90d_change": 0
        }
        periods = {"1d": 1, "7d": 7, "30d": 30, "90d": 90}
        
        for period_name, days in periods.items():
            # Calculate change from N days ago
            # historical_prices is a list where index -1 is most recent (current)
            # We want to compare with price from 'days' positions back
            if len(historical_prices) > days:
                # We have enough data points - get price from 'days' positions back
                past_price = historical_prices[-days-1]
                change = ((current - past_price) / past_price) * 100 if past_price > 0 else 0
                changes[f"{period_name}_change"] = round(change, 2)
            elif len(historical_prices) >= 2:
                # We have some data but not enough for the full period - use first available price
                past_price = historical_prices[0]
                change = ((current - past_price) / past_price) * 100 if past_price > 0 else 0
                changes[f"{period_name}_change"] = round(change, 2)
            # else: already initialized to 0 above
        
        # Calculate volatility (standard deviation of returns)
        returns = []
        for i in range(1, len(historical_prices)):
            if historical_prices[i-1] > 0:
                ret = ((historical_prices[i] - historical_prices[i-1]) / historical_prices[i-1]) * 100
                returns.append(ret)
        
        if returns and len(returns) > 1:
            volatility = statistics.stdev(returns)
        else:
            volatility = 0
        
        return {
            "current_price": current,
            "high_52w": max(historical_prices) if historical_prices else current,
            "low_52w": min(historical_prices) if historical_prices else current,
            **changes,
            "volatility": round(volatility, 2)
        }
    
    @staticmethod
    def _generate_forecast(
        current_price: float,
        tech_analysis: Dict[str, Any],
        fund_analysis: Dict[str, Any],
        historical_performance: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate price forecast based on analysis."""
        
        # Simple forecast based on trends
        avg_change = (
            historical_performance.get("7d_change", 0) * 0.3 +
            historical_performance.get("30d_change", 0) * 0.7
        ) / 100
        
        # Project 7-day and 30-day forecasts
        forecast_7d = current_price * (1 + avg_change * 7 / 30)
        forecast_30d = current_price * (1 + avg_change)
        
        # Confidence based on volatility
        volatility = historical_performance.get("volatility", 0)
        confidence = max(50, 100 - volatility * 2)  # Lower volatility = higher confidence
        
        return {
            "price_7d": round(forecast_7d, 2),
            "price_30d": round(forecast_30d, 2),
            "expected_change_7d": round((forecast_7d - current_price) / current_price * 100, 2),
            "expected_change_30d": round((forecast_30d - current_price) / current_price * 100, 2),
            "confidence": round(confidence, 1),
            "forecast_basis": "Technical and fundamental analysis with historical trend projection"
        }

