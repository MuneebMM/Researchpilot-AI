"""Shared LangGraph state for the ResearchPilot multi-agent system."""

from typing import Annotated, TypedDict
import operator


class ResearchState(TypedDict):
    """Persistent state carried through all agent nodes in the graph.

    Fields annotated with `Annotated[..., operator.add]` are merged (appended
    for lists) rather than overwritten on each node update.
    """

    research_goal: str
    """The original user-provided research objective."""

    messages: Annotated[list[object], operator.add]
    """Full accumulated message history across all agents."""

    search_results: Annotated[list[object], operator.add]
    """Raw web search results."""

    news_results: Annotated[list[object], operator.add]
    """Raw news/search results."""

    tech_results: Annotated[list[object], operator.add]
    """Raw technology / AI strategy search results."""

    financial_results: Annotated[list[object], operator.add]
    """Raw financial / earnings report search results."""

    critic_feedback: str
    """Feedback from the critic agent directing further research or approval."""

    needs_more_research: bool
    """Flag set by the critic; when True the supervisor loops back for more data."""

    final_report: str
    """The synthesised final intelligence report (set at graph termination)."""

    current_agent: Annotated[str, operator.add]
    """Name of the agent node currently executing (accumulates all updates)."""

    next_agents: list[str]
    """List of agent names the supervisor has selected for the next wave."""

    iteration_count: int
    """Number of research loops completed; guards against infinite loops."""


def create_initial_state(research_goal: str) -> ResearchState:
    """Return a fresh ResearchState initialised for a new research session."""
    return ResearchState(
        research_goal=research_goal,
        messages=[],
        search_results=[],
        news_results=[],
        tech_results=[],
        financial_results=[],
        critic_feedback="",
        needs_more_research=False,
        final_report="",
        current_agent="supervisor",
        next_agents=[],
        iteration_count=0,
    )