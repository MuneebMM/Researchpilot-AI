"""Tavily search tool wrapper for ResearchPilot AI."""

from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv
import os


load_dotenv()


def get_search_tool() -> TavilySearchResults:
    """Return a configured Tavily search tool.

    The tool is used by agent nodes to retrieve up-to-date web results
    during the research process. Results are limited to 5 entries per query.

    Returns:
        TavilySearchResults: A ready-to-use LangChain tool wrapped around
            the Tavily search API.
    """
    return TavilySearchResults(
        api_key=os.getenv("TAVILY_API_KEY"),
        max_results=5,
    )


if __name__ == "__main__":
    # Smoke test: verify the tool can be constructed and returns results.
    tool = get_search_tool()
    results = tool.invoke("Siemens AI strategy 2026")
    for result in results:
        print(result)