"""FastAPI application for ResearchPilot AI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.agents.research_agent import build_graph, AgentState
from langchain_core.messages import HumanMessage


app = FastAPI(title="ResearchPilot AI")

# CORS middleware — allows all origins for local frontend development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResearchRequest(BaseModel):
    """Request payload for a research task."""

    research_goal: str = Field(..., description="The research question or topic to investigate.")
    max_results: int = Field(default=5, ge=1, le=20, description="Maximum number of search results.")


class ResearchResponse(BaseModel):
    """Response payload after a research task completes."""

    result: str = Field(..., description="The synthesised research findings.")
    status: str = Field(..., description="One of: 'success', 'error'.")


@app.get("/health")
def health_check() -> dict[str, str]:
    """Confirm the service is running."""
    return {"status": "ok"}


@app.post("/api/research", response_model=ResearchResponse)
def research_endpoint(request: ResearchRequest) -> ResearchResponse:
    """Run the researcher agent and return a synthesised intelligence report."""
    # Compile the graph per request so max_results is always respected.
    graph = build_graph(max_results=request.max_results).compile()

    initial_state: AgentState = {
        "messages": [HumanMessage(content=request.research_goal)],
        "research_goal": request.research_goal,
        "max_results": request.max_results,
    }

    final_state = graph.invoke(initial_state)
    final_text = final_state["messages"][-1].content

    return ResearchResponse(result=final_text, status="success")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.api.main:app", host="0.0.0.0", port=8000, reload=True)