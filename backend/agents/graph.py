"""Main LangGraph multi-agent orchestration graph for ResearchPilot AI.

Graph flow (one research session):
  supervisor
    ├─→ web_search ──────────────┐
    ├─→ news     ───────────────┤
    ├─→ tech     ───────────────┤
    └─→ financial ──────────────┘
              ↓  all four converge at
               critic
            ┌──┴──┐
        True ↓    ↓ False
         supervisor    synthesizer
                            │
                           END

The loop supervisor → specialist agents → critic is bounded by
iteration_count (critic_node enforces a hard stop at count >= 2).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from langgraph.graph import StateGraph, END

from backend.agents.state import ResearchState, create_initial_state
from backend.agents.supervisor import (
    supervisor_node,
    critic_node,
    synthesizer_node,
)
from backend.agents.specialized_agents import (
    web_search_agent_node,
    news_agent_node,
    tech_agent_node,
    financial_agent_node,
)
from backend.utils.pdf_generator import generate_pdf


def _build_graph() -> StateGraph:
    """Construct and return the compiled ResearchPilot StateGraph."""
    graph = StateGraph(ResearchState)

    # --- Nodes ---
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("web_search", web_search_agent_node)
    graph.add_node("news", news_agent_node)
    graph.add_node("tech", tech_agent_node)
    graph.add_node("financial", financial_agent_node)
    graph.add_node("critic", critic_node)
    graph.add_node("synthesizer", synthesizer_node)

    # --- Entry point ---
    graph.set_entry_point("supervisor")

    # --- Static edges: supervisor always fans out to all four specialist agents.
    #    The supervisor node's next_agents return value is informational only;
    #    routing is fixed to ensure all research dimensions are covered.
    graph.add_edge("supervisor", "web_search")
    graph.add_edge("supervisor", "news")
    graph.add_edge("supervisor", "tech")
    graph.add_edge("supervisor", "financial")

    # --- Static edges: specialist agents all feed into the critic ---
    graph.add_edge("web_search", "critic")
    graph.add_edge("news", "critic")
    graph.add_edge("tech", "critic")
    graph.add_edge("financial", "critic")

    # --- Conditional edge: critic decides loop or termination ---
    def critic_route(state: ResearchState) -> str:
        """Route back to supervisor if more research is needed, else to synthesizer."""
        return "supervisor" if state["needs_more_research"] else "synthesizer"

    graph.add_conditional_edges("critic", critic_route)
    graph.add_edge("synthesizer", END)

    return graph


# Compile once at module load — the graph is thread-safe for concurrent requests.
research_graph = _build_graph().compile()


def run_research(research_goal: str) -> dict:
    """Run one full research session and return the final intelligence report.

    Args:
        research_goal: The user question or topic to investigate.

    Returns:
        A dict with the report text and the path to the generated PDF.
    """
    initial_state = create_initial_state(research_goal)
    result: ResearchState = research_graph.invoke(initial_state)
    final_report = result["final_report"]
    pdf_path = generate_pdf(final_report, research_goal)
    return {"report": final_report, "pdf_path": pdf_path}


if __name__ == "__main__":
    result = run_research("What is Adobe's AI strategy and financial performance in 2026?")
    print(result["report"])
    print(f"\n✅ PDF saved at: {result['pdf_path']}")