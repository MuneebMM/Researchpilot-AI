"""Specialized research agent nodes for the ResearchPilot multi-agent system.

Each node follows a two-step pattern:
  1. Invoke Tavily search directly with a query built from the research goal.
  2. Feed the raw search results to the LLM with the relevant system prompt
     to produce a clean synthesised summary.
"""

import sys
from pathlib import Path

# Ensure project root is on the Python path for all imports.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.state import ResearchState
from backend.utils.llm import get_llm
from backend.tools.search import get_search_tool
from backend.utils.prompts import (
    WEB_SEARCH_PROMPT,
    NEWS_PROMPT,
    TECH_PROMPT,
    FINANCIAL_PROMPT,
)


# ---------------------------------------------------------------------------
# Agent nodes
# ---------------------------------------------------------------------------

def web_search_agent_node(state: ResearchState) -> dict:
    """Search the web for factual, up-to-date information on the research goal."""
    print("🔍 Web Search Agent running...")
    try:
        search_tool = get_search_tool()
        raw_results = search_tool.invoke({"query": state["research_goal"]})
        results_text = _format_results(raw_results)

        llm = get_llm()
        messages = [
            SystemMessage(content=WEB_SEARCH_PROMPT),
            HumanMessage(
                content=f"Research Goal: {state['research_goal']}\n\nSearch Results:\n{results_text}"
            ),
        ]
        response = llm.invoke(messages)
        summary = response.content if hasattr(response, "content") else str(response)
        return {"search_results": [summary], "current_agent": "web_search"}
    except Exception as e:
        print(f"⚠️  Web Search Agent error: {str(e)}")
        return {"search_results": [], "current_agent": "web_search"}


def news_agent_node(state: ResearchState) -> dict:
    """Find and analyse the latest news and media coverage on the research goal."""
    print("📰 News Agent running...")
    try:
        query = f"{state['research_goal']} latest news 2026"
        search_tool = get_search_tool()
        raw_results = search_tool.invoke({"query": query})
        results_text = _format_results(raw_results)

        llm = get_llm()
        messages = [
            SystemMessage(content=NEWS_PROMPT),
            HumanMessage(content=f"Research Goal: {state['research_goal']}\n\nSearch Results:\n{results_text}"),
        ]
        response = llm.invoke(messages)
        summary = response.content if hasattr(response, "content") else str(response)
        return {"news_results": [summary], "current_agent": "news"}
    except Exception as e:
        print(f"⚠️  News Agent error: {str(e)}")
        return {"news_results": [], "current_agent": "news"}


def tech_agent_node(state: ResearchState) -> dict:
    """Research technology stack, AI initiatives, and innovation strategy."""
    print("⚙️  Tech Agent running...")
    try:
        query = f"{state['research_goal']} AI technology strategy"
        search_tool = get_search_tool()
        raw_results = search_tool.invoke({"query": query})
        results_text = _format_results(raw_results)

        llm = get_llm()
        messages = [
            SystemMessage(content=TECH_PROMPT),
            HumanMessage(content=f"Research Goal: {state['research_goal']}\n\nSearch Results:\n{results_text}"),
        ]
        response = llm.invoke(messages)
        summary = response.content if hasattr(response, "content") else str(response)
        return {"tech_results": [summary], "current_agent": "tech"}
    except Exception as e:
        print(f"⚠️  Tech Agent error: {str(e)}")
        return {"tech_results": [], "current_agent": "tech"}


def financial_agent_node(state: ResearchState) -> dict:
    """Find financial performance data, revenue figures, and investment activity."""
    print("💰 Financial Agent running...")
    try:
        query = f"{state['research_goal']} financial performance revenue 2026"
        search_tool = get_search_tool()
        raw_results = search_tool.invoke({"query": query})
        results_text = _format_results(raw_results)

        llm = get_llm()
        messages = [
            SystemMessage(content=FINANCIAL_PROMPT),
            HumanMessage(content=f"Research Goal: {state['research_goal']}\n\nSearch Results:\n{results_text}"),
        ]
        response = llm.invoke(messages)
        summary = response.content if hasattr(response, "content") else str(response)
        return {"financial_results": [summary], "current_agent": "financial"}
    except Exception as e:
        print(f"⚠️  Financial Agent error: {str(e)}")
        return {"financial_results": [], "current_agent": "financial"}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _format_results(raw_results) -> str:
    """Convert a raw Tavily search result list into a readable string."""
    if isinstance(raw_results, list):
        return "\n".join(
            f"Source: {r.get('url', 'N/A')}\nContent: {r.get('content', '')}"
            for r in raw_results
        )
    return str(raw_results)