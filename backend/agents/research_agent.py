"""Single-researcher LangGraph agent for ResearchPilot AI.

Phase 1: One agent with a search tool. LangSmith tracing is active so all
graph runs are visible in the LangSmith dashboard.

Uses the standard ReAct pattern: LLM decides to call a tool → ToolNode
executes it → LLM synthesises the final answer.
"""

import os
import sys
from pathlib import Path

# Ensure the project root is on sys.path so 'backend' is importable whether
# this file is run directly or via `python -m`.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from typing import TypedDict

from backend.utils.llm import get_llm

# LangSmith tracing — keys are already in .env.
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")


class AgentState(TypedDict):
    """State carried through the graph nodes."""

    messages: list[BaseMessage]
    research_goal: str
    max_results: int


def should_continue(state: AgentState) -> str:
    """Route to 'action' if the last message has tool calls, else END."""
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "action"
    return END


def researcher_node(state: AgentState) -> AgentState:
    """Call the LLM with the full message history and search tool bound."""
    llm = get_llm()
    # Instantiate the tool fresh each turn so max_results from state is respected.
    search_tool = TavilySearchResults(
        api_key=os.getenv("TAVILY_API_KEY"),
        max_results=state["max_results"],
    )

    llm_with_tools = llm.bind_tools([search_tool])

    system_msg = (
        "You are a research assistant. Use the search tool to find "
        "up-to-date information, then synthesise a clear, concise answer."
    )

    # Build a clean message list: system prompt + full conversation history.
    # Ensure the list always starts with a HumanMessage so Gemini always
    # sees a valid first content turn.
    if state["messages"]:
        messages: list[BaseMessage] = [HumanMessage(content=system_msg)] + state["messages"]
    else:
        # First turn: use the research goal as the opening HumanMessage.
        messages = [
            HumanMessage(content=system_msg),
            HumanMessage(content=state["research_goal"]),
        ]

    response: BaseMessage = llm_with_tools.invoke(messages)
    state["messages"] = state["messages"] + [response]
    return state


def build_graph(max_results: int = 5) -> StateGraph:
    """Assemble and return the researcher StateGraph with ReAct routing."""
    search_tool = TavilySearchResults(
        api_key=os.getenv("TAVILY_API_KEY"),
        max_results=max_results,
    )

    graph = StateGraph(AgentState)
    graph.add_node("researcher", researcher_node)
    graph.add_node("action", ToolNode([search_tool]))
    graph.set_entry_point("researcher")
    graph.add_conditional_edges("researcher", should_continue)
    graph.add_edge("action", "researcher")
    return graph


if __name__ == "__main__":
    research_goal = "What is Adobe's current AI strategy in 2026?"

    app = build_graph(max_results=5).compile()

    initial_state: AgentState = {
        "messages": [HumanMessage(content=research_goal)],
        "research_goal": research_goal,
        "max_results": 5,
    }

    final_state = app.invoke(initial_state)
    for msg in final_state["messages"]:
        print(msg.content)
        print("---")