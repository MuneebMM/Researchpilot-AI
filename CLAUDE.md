# ResearchPilot AI

**Project:** Autonomous multi-agent research system using LangGraph supervisor pattern. Takes a user research goal and returns a full intelligence report.

## Stack

| Concern | Technology |
|---|---|
| LLM | Gemini API via LangChain `ChatGoogleGenerativeAI` (model: `gemini-2.0-flash`) |
| Search | Tavily API |
| Backend | Python, FastAPI (async), LangGraph, LangChain |
| Frontend | React + Vite + TailwindCSS |
| Observability | LangSmith |
| Containerization | Docker Compose |

## Folder Layout

```
backend/
  agents/    → LangGraph agent nodes
  api/       → FastAPI routes
  tools/     → Tavily search tool wrapper
  utils/     → prompts, PDF generator, helpers
frontend/    → React app
reports/     → generated PDF/markdown outputs
```

## Rules

- Always load env vars with `python-dotenv`
- Never hardcode API keys
- All agents traced via LangSmith
- Use async FastAPI endpoints
- Gemini accessed via `langchain-google-genai` package
