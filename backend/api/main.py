"""FastAPI application for ResearchPilot AI."""

import os
from glob import glob

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.agents.graph import run_research


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
    pdf_path: str = Field(..., description="Absolute path to the generated PDF.")
    pdf_url: str = Field(..., description="URL path for downloading the PDF.")


@app.get("/health")
def health_check() -> dict[str, str]:
    """Confirm the service is running."""
    return {"status": "ok"}


@app.get("/reports/{filename}")
async def get_report(filename: str):
    """Serve a generated PDF report."""
    file_path = f"reports/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=filename,
    )


@app.get("/api/reports")
def list_reports() -> list[dict]:
    """List all generated reports in the reports/ directory."""
    pattern = "reports/research_report_*.pdf"
    files = sorted(glob(pattern), reverse=True)
    reports = []
    for f in files:
        reports.append({"filename": os.path.basename(f), "path": f})
    return reports


@app.post("/api/research", response_model=ResearchResponse)
def research_endpoint(request: ResearchRequest) -> ResearchResponse:
    """Run the full multi-agent research pipeline and return the intelligence report."""
    try:
        result = run_research(request.research_goal)
    except EnvironmentError as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research pipeline failed: {e}")

    report_text = result["report"]
    pdf_path = result.get("pdf_path", "")
    pdf_url = f"/reports/{os.path.basename(pdf_path)}" if pdf_path else ""
    return ResearchResponse(
        result=report_text,
        status="success",
        pdf_path=pdf_path,
        pdf_url=pdf_url,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.api.main:app", host="0.0.0.0", port=8000, reload=True)