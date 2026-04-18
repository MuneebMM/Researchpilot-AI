"""Supervisor, critic, and synthesizer agent nodes.

These three nodes drive the high-level orchestration loop:
  supervisor → specialist agents → critic → (loop if needed) → synthesizer
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.state import ResearchState
from backend.utils.llm import get_llm
from backend.utils.prompts import (
    SUPERVISOR_PROMPT,
    CRITIC_PROMPT,
    SYNTHESIZER_PROMPT,
)


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

VALID_AGENTS = ["web_search", "news", "tech", "financial"]


def supervisor_node(state: ResearchState) -> dict:
    """Analyse the research goal and decide which specialist agents to activate."""
    print("🎯 Supervisor Agent running...")
    llm = get_llm()

    # Override prompt inline to force the LLM to return exact, valid agent names.
    override_prompt = (
        "You are a research supervisor. Your job is to decide which specialist "
        "agents to activate based on the research goal.\n"
        "The only valid agent names are: web_search, news, tech, financial\n"
        "You must return ONLY this exact JSON with no other text:\n"
        '{"next_agents": ["web_search", "news", "tech", "financial"]}'
    )

    messages = [
        SystemMessage(content=override_prompt),
        HumanMessage(content=f"Research goal: {state['research_goal']}"),
    ]

    try:
        response = llm.invoke(messages)
        content = response.content if hasattr(response, "content") else str(response)
        parsed = json.loads(content)
        raw_agents: list = list(parsed.get("next_agents", []))
        validated = [a for a in raw_agents if a in VALID_AGENTS]
        next_agents = validated if validated else VALID_AGENTS[:]
    except json.JSONDecodeError:
        print("⚠️  Supervisor JSON parse failed — defaulting to all agents")
        next_agents = VALID_AGENTS[:]
    except Exception as e:
        print(f"⚠️  Supervisor LLM error: {e} — defaulting to all agents")
        next_agents = VALID_AGENTS[:]

    return {"current_agent": "supervisor", "next_agents": next_agents}


def critic_node(state: ResearchState) -> dict:
    """Review all gathered research and decide whether more is needed."""
    print("🔍 Critic Agent reviewing research...")
    llm = get_llm()

    # Compile every result set into one context string for the critic.
    compiled = _compile_results(state)

    messages = [
        SystemMessage(content=CRITIC_PROMPT),
        HumanMessage(content=f"Research goal: {state['research_goal']}\n\n{compiled}"),
    ]

    try:
        raw = llm.invoke(messages)
        content = raw.content if hasattr(raw, "content") else str(raw)
        parsed = json.loads(content)
        needs_more = bool(parsed.get("needs_more_research", False))
        feedback = str(parsed.get("feedback", ""))
    except json.JSONDecodeError:
        print("⚠️  Critic JSON parse failed — proceeding to synthesis")
        needs_more = False
        feedback = f"Critic JSON parse failed — proceeding to synthesis. Raw: {content[:200]}"
    except Exception as e:
        print(f"⚠️  Critic LLM error: {e} — proceeding to synthesis")
        needs_more = False
        feedback = f"Critic LLM error: {e}"

    # Hard guard: after 3 full iterations the loop terminates regardless.
    if state["iteration_count"] >= 3:
        needs_more = False
        feedback = "Maximum iteration count reached. Finalising report."

    return {
        "critic_feedback": feedback,
        "needs_more_research": needs_more,
        "iteration_count": state["iteration_count"] + 1,
    }


SYNTHESIZER_MAX_INPUT_CHARS_PER_SECTION = 4000
SYNTHESIZER_MAX_OUTPUT_TOKENS = 2048


def synthesizer_node(state: ResearchState) -> dict:
    """Produce the final intelligence report from all research findings."""
    print("📝 Synthesizer Agent writing report...")
    llm = get_llm(max_output_tokens=SYNTHESIZER_MAX_OUTPUT_TOKENS)

    compiled = _compile_results(state, max_chars_per_section=SYNTHESIZER_MAX_INPUT_CHARS_PER_SECTION)

    messages = [
        SystemMessage(content=SYNTHESIZER_PROMPT),
        HumanMessage(
            content=f"Research goal: {state['research_goal']}\n\n{compiled}"
        ),
    ]

    try:
        response = llm.invoke(messages)
        report = response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        print(f"⚠️  Synthesizer LLM error: {e}")
        report = f"Report synthesis failed due to an error: {e}\n\nRaw research data:\n\n{compiled}"

    return {"final_report": report}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _compile_results(state: ResearchState, max_chars_per_section: int | None = None) -> str:
    """Concatenate all result lists into a single human-readable string.

    If max_chars_per_section is set, each section is truncated to that many chars
    to keep the synthesizer's input bounded (faster inference).
    """
    sections = []

    def add(label: str, key: str) -> None:
        items = state.get(key)
        if not items:
            return
        body = _join(items)
        if max_chars_per_section and len(body) > max_chars_per_section:
            body = body[:max_chars_per_section] + "\n...[truncated]"
        sections.append(f"=== {label} ===\n{body}")

    add("Web Search Results", "search_results")
    add("News & Media", "news_results")
    add("Technology & AI Strategy", "tech_results")
    add("Financial Overview", "financial_results")

    return "\n\n".join(sections) if sections else "No research results gathered yet."


def _join(items: list) -> str:
    """Flatten a list of result strings, filtering out non-string artefacts."""
    return "\n---\n".join(
        i.content if hasattr(i, "content") else str(i) for i in items if i
    )