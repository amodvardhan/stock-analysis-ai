"""
=============================================================================
AI Hub - LangGraph Multi-Agent System
=============================================================================
This package contains all AI agents for stock market intelligence.

Agent Architecture:
- Each agent is a specialized expert (technical, fundamental, sentiment, etc.)
- Agents communicate through a shared state graph
- Orchestrator agent coordinates all specialist agents
- All agents use LangGraph for stateful, production-ready workflows

For beginners:
- Think of agents as AI team members, each with a specific job
- They work together to analyze stocks comprehensively
- LangGraph manages their workflow and state
=============================================================================
"""

from .orchestrator import create_stock_analysis_graph
from .tools import (
    get_stock_price,
    calculate_technical_indicators,
    get_fundamental_data,
    analyze_sentiment,
    search_similar_patterns,
)

__all__ = [
    "create_stock_analysis_graph",
    "get_stock_price",
    "calculate_technical_indicators",
    "get_fundamental_data",
    "analyze_sentiment",
    "search_similar_patterns",
]
