"""
=============================================================================
AI Hub - LangGraph Orchestrator
=============================================================================
The main workflow orchestrator using LangGraph StateGraph.

This file defines the multi-agent workflow:
1. User requests stock analysis
2. Three agents run IN SEQUENCE (to avoid state conflicts):
   - Technical Analysis Agent
   - Fundamental Analysis Agent
   - Sentiment Analysis Agent
3. Recommendation Agent synthesizes all outputs
4. Return final recommendation to user

LangGraph manages the state and flow between agents.
=============================================================================
"""

from typing import TypedDict, Annotated, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import operator
import structlog
from datetime import datetime

from agents.technical_agent import TechnicalAnalysisAgent
from agents.fundamental_agent import FundamentalAnalysisAgent
from agents.sentiment_agent import SentimentAnalysisAgent
from agents.recommendation_agent import RecommendationAgent

logger = structlog.get_logger()


# =============================================================================
# State Definition
# =============================================================================
class StockAnalysisState(TypedDict):
    """
    The shared state that flows through the agent graph.
    
    Each agent reads from and writes to this state.
    LangGraph manages state updates automatically.
    
    Attributes:
        symbol: Stock ticker symbol
        market: Market identifier
        company_name: Full company name
        user_risk_tolerance: User's risk profile
        
        # Agent outputs
        tech_analysis: Output from technical agent
        fund_analysis: Output from fundamental agent
        sent_analysis: Output from sentiment agent
        final_recommendation: Output from recommendation agent
        
        # Metadata
        started_at: When analysis started
        completed_at: When analysis completed
        errors: List of any errors encountered
    """
    # Input parameters
    symbol: str
    market: str
    company_name: Optional[str]
    user_risk_tolerance: str
    
    # Agent outputs (using shortened names to avoid LangGraph conflicts)
    tech_analysis: Optional[Dict[str, Any]]
    fund_analysis: Optional[Dict[str, Any]]
    sent_analysis: Optional[Dict[str, Any]]
    final_recommendation: Optional[Dict[str, Any]]
    
    # Metadata
    started_at: str
    completed_at: Optional[str]
    errors: Annotated[list, operator.add]  # Errors accumulate


# =============================================================================
# Agent Node Functions
# =============================================================================
# Each function represents a "node" in the LangGraph workflow


async def technical_analysis_node(state: StockAnalysisState) -> Dict[str, Any]:
    """
    Node that runs technical analysis.
    
    This function:
    1. Receives the current state
    2. Runs TechnicalAnalysisAgent
    3. Returns state update with tech_analysis populated
    
    Args:
        state: Current workflow state
    
    Returns:
        Dict with updates to merge into state
    """
    logger.info("running_technical_analysis_node", symbol=state["symbol"])
    
    try:
        agent = TechnicalAnalysisAgent()
        result = await agent.analyze(
            symbol=state["symbol"],
            market=state["market"]
        )
        
        return {"tech_analysis": result}
        
    except Exception as e:
        logger.error("technical_node_failed", symbol=state["symbol"], error=str(e))
        return {
            "tech_analysis": {
                "error": str(e),
                "agent": "TechnicalAnalyst"
            },
            "errors": [f"Technical analysis failed: {str(e)}"]
        }


async def fundamental_analysis_node(state: StockAnalysisState) -> Dict[str, Any]:
    """
    Node that runs fundamental analysis.
    
    Args:
        state: Current workflow state
    
    Returns:
        Dict with fund_analysis populated
    """
    logger.info("running_fundamental_analysis_node", symbol=state["symbol"])
    
    try:
        agent = FundamentalAnalysisAgent()
        result = await agent.analyze(
            symbol=state["symbol"],
            market=state["market"]
        )
        
        return {"fund_analysis": result}
        
    except Exception as e:
        logger.error("fundamental_node_failed", symbol=state["symbol"], error=str(e))
        return {
            "fund_analysis": {
                "error": str(e),
                "agent": "FundamentalAnalyst"
            },
            "errors": [f"Fundamental analysis failed: {str(e)}"]
        }


async def sentiment_analysis_node(state: StockAnalysisState) -> Dict[str, Any]:
    """
    Node that runs sentiment analysis.
    
    Args:
        state: Current workflow state
    
    Returns:
        Dict with sent_analysis populated
    """
    logger.info("running_sentiment_analysis_node", symbol=state["symbol"])
    
    try:
        # Get company name from state or use symbol
        company_name = state.get("company_name") or state["symbol"]
        
        agent = SentimentAnalysisAgent()
        result = await agent.analyze(
            symbol=state["symbol"],
            company_name=company_name
        )
        
        return {"sent_analysis": result}
        
    except Exception as e:
        logger.error("sentiment_node_failed", symbol=state["symbol"], error=str(e))
        return {
            "sent_analysis": {
                "error": str(e),
                "agent": "SentimentAnalyst"
            },
            "errors": [f"Sentiment analysis failed: {str(e)}"]
        }


async def recommendation_node(state: StockAnalysisState) -> Dict[str, Any]:
    """
    Node that synthesizes all analyses into final recommendation.
    
    This node WAITS for all three analysis nodes to complete,
    then synthesizes their outputs.
    
    Args:
        state: Current workflow state (with all analyses complete)
    
    Returns:
        Dict with final_recommendation and completed_at
    """
    logger.info("running_recommendation_node", symbol=state["symbol"])
    
    try:
        agent = RecommendationAgent()
        result = await agent.synthesize(
            symbol=state["symbol"],
            technical_analysis=state["tech_analysis"],
            fundamental_analysis=state["fund_analysis"],
            sentiment_analysis=state["sent_analysis"],
            user_risk_tolerance=state.get("user_risk_tolerance", "moderate")
        )
        
        return {
            "final_recommendation": result,
            "completed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("recommendation_node_failed", symbol=state["symbol"], error=str(e))
        return {
            "final_recommendation": {
                "error": str(e),
                "agent": "RecommendationSynthesizer"
            },
            "errors": [f"Recommendation synthesis failed: {str(e)}"],
            "completed_at": datetime.utcnow().isoformat()
        }


# =============================================================================
# Graph Construction
# =============================================================================
def create_stock_analysis_graph():
    """
    Create the LangGraph StateGraph for stock analysis.
    
    Graph structure:
    
        START
          |
          v
    [Technical]
          |
          v
    [Fundamental]
          |
          v
    [Sentiment]
          |
          v
    [Recommendation]
          |
          v
        END
    
    Agents run sequentially to avoid state key conflicts.
    Each agent waits for the previous one to complete.
    
    Returns:
        Compiled LangGraph that can be invoked
    """
    
    # Create the graph
    workflow = StateGraph(StockAnalysisState)
    
    # Add nodes (each agent is a node)
    workflow.add_node("technical", technical_analysis_node)
    workflow.add_node("fundamental", fundamental_analysis_node)
    workflow.add_node("sentiment", sentiment_analysis_node)
    workflow.add_node("recommendation", recommendation_node)
    
    # Define edges (sequential workflow to avoid conflicts)
    workflow.set_entry_point("technical")
    workflow.add_edge("technical", "fundamental")
    workflow.add_edge("fundamental", "sentiment")
    workflow.add_edge("sentiment", "recommendation")
    workflow.add_edge("recommendation", END)
    
    # Compile the graph with memory (for debugging/tracing)
    memory = MemorySaver()
    compiled_graph = workflow.compile(checkpointer=memory)
    
    logger.info("stock_analysis_graph_created")
    
    return compiled_graph


# =============================================================================
# High-Level Interface
# =============================================================================
async def analyze_stock(
    symbol: str,
    market: str = "india_nse",
    company_name: Optional[str] = None,
    user_risk_tolerance: str = "moderate"
) -> Dict[str, Any]:
    """
    High-level function to analyze a stock using the multi-agent workflow.
    
    This is the main entry point for stock analysis.
    Call this from your FastAPI endpoints.
    
    Args:
        symbol: Stock ticker symbol (e.g., "RELIANCE", "AAPL")
        market: Market identifier (india_nse, india_bse, us_nyse, us_nasdaq)
        company_name: Full company name (optional, improves sentiment analysis)
        user_risk_tolerance: User's risk profile (conservative, moderate, aggressive)
    
    Returns:
        Dict containing:
        - final_recommendation: The synthesized recommendation
        - technical_analysis: Technical analysis details
        - fundamental_analysis: Fundamental analysis details
        - sentiment_analysis: Sentiment analysis details
        - metadata: Timestamps, errors, etc.
    
    Example:
        result = await analyze_stock("RELIANCE", "india_nse", "Reliance Industries")
        print(result["final_recommendation"]["action"])  # "buy"
        print(result["final_recommendation"]["confidence"])  # 78
    """
    logger.info(
        "stock_analysis_requested",
        symbol=symbol,
        market=market,
        risk_tolerance=user_risk_tolerance
    )
    
    # Create the graph
    graph = create_stock_analysis_graph()
    
    # Initialize state
    initial_state: StockAnalysisState = {
        "symbol": symbol,
        "market": market,
        "company_name": company_name,
        "user_risk_tolerance": user_risk_tolerance,
        "tech_analysis": None,
        "fund_analysis": None,
        "sent_analysis": None,
        "final_recommendation": None,
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "errors": []
    }
    
    # Run the graph
    # This executes all nodes in the defined order
    final_state = await graph.ainvoke(
        initial_state,
        config={"configurable": {"thread_id": f"{symbol}_{datetime.utcnow().timestamp()}"}}
    )
    
    # Log completion
    logger.info(
        "stock_analysis_completed",
        symbol=symbol,
        duration_seconds=(
            (datetime.fromisoformat(final_state["completed_at"]) - 
             datetime.fromisoformat(final_state["started_at"])).total_seconds()
            if final_state.get("completed_at") else None
        ),
        errors=len(final_state.get("errors", []))
    )
    
    # Return the complete final state
    return {
        "symbol": final_state["symbol"],
        "market": final_state["market"],
        "final_recommendation": final_state.get("final_recommendation"),
        "analyses": {
            "technical": final_state.get("tech_analysis"),
            "fundamental": final_state.get("fund_analysis"),
            "sentiment": final_state.get("sent_analysis")
        },
        "metadata": {
            "started_at": final_state["started_at"],
            "completed_at": final_state.get("completed_at"),
            "errors": final_state.get("errors", []),
            "user_risk_tolerance": final_state["user_risk_tolerance"]
        }
    }
