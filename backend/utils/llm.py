"""LLM configuration for ResearchPilot AI.

This module provides the primary LLM interface used by all LangGraph agent nodes.
Environment variables are loaded once at import time via python-dotenv.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage
from dotenv import load_dotenv
import os


# Load .env variables into the process environment on module import.
load_dotenv()


def get_llm(max_output_tokens: int | None = None) -> ChatGoogleGenerativeAI:
    """Return a configured ChatGoogleGenerativeAI instance.

    Uses temperature=0 for deterministic, reproducible agent behavior.
    The model name and API key are read from environment variables so
    no secrets are ever hardcoded.

    Args:
        max_output_tokens: Optional cap on generated tokens (faster responses).

    Returns:
        ChatGoogleGenerativeAI: A ready-to-use LLM instance.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY is not set. Check your .env file.")
    kwargs = {
        "model": os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite-preview"),
        "temperature": 0,
        "google_api_key": api_key,
        "request_timeout": 120,
    }
    if max_output_tokens:
        kwargs["max_output_tokens"] = max_output_tokens
    return ChatGoogleGenerativeAI(**kwargs)


if __name__ == "__main__":
    # Smoke test: verify the LLM can be constructed and responds.
    llm = get_llm()
    response: BaseMessage = llm.invoke("Say hello in one sentence")
    print(response.content)