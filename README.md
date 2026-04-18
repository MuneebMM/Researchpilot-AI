# 🤖 ResearchPilot AI

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![LangGraph](https://img.shields.io/badge/LangGraph-0.3-1C3C3C)
![React](https://img.shields.io/badge/React-18-61DAFB)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
![License](https://img.shields.io/badge/License-MIT-green)

> Autonomous multi-agent AI system that researches any topic and generates boardroom-ready intelligence reports using the LangGraph supervisor pattern with specialized sub-agents.

![Demo](docs/demo.gif)

> _Demo GIF coming soon._

---

## 📚 Table of Contents

- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [🛠️ Tech Stack](#️-tech-stack)
- [🚀 Quick Start](#-quick-start)
- [⚙️ Environment Variables](#️-environment-variables)
- [📁 Project Structure](#-project-structure)
- [🤖 Agent Architecture](#-agent-architecture)
- [📊 LangSmith Observability](#-langsmith-observability)
- [🗺️ Roadmap](#️-roadmap)
- [👤 Author](#-author)
- [📄 License](#-license)

---

## ✨ Features

- 🤖 **Multi-agent supervisor architecture** powered by LangGraph
- 🔍 **Real-time web research** via the Tavily API
- 📰 **Specialized sub-agents** — Web Search, News, Tech Strategy, and Financial
- 🔁 **Self-correcting critic loop** with a hard iteration guard against infinite loops
- 📄 **Professional PDF report generation** with WeasyPrint / xhtml2pdf
- ⚡ **FastAPI async backend** with health checks and CORS support
- 🎨 **React + Vite + TailwindCSS** dark-theme frontend
- 📊 **Full agent observability** via LangSmith traces
- 🐳 **One-command Docker Compose** deployment (backend + frontend + nginx)
- 🔐 **Environment-based secrets management** — no keys in source

---

## 🏗️ Architecture

```
                   User Research Goal
                          ↓
                  [FastAPI Backend]
                          ↓
              [LangGraph Supervisor Agent]
                          │
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
  🔍 Web Search      📰 News Agent     ⚙️ Tech Agent     💰 Financial Agent
     → Tavily           → Tavily          → Tavily            → Tavily
        │                 │                 │                   │
        └─────────────────┴─────────────────┴───────────────────┘
                                  ↓
                          [Critic Agent]  ── needs more? ──▶ loop back (max 3x)
                                  ↓
                        [Synthesizer Agent]
                                  ↓
                      📄 PDF + Markdown Report
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | Google Gemini 3.1 Flash-Lite (via `langchain-google-genai`) |
| **Agent Framework** | LangGraph (StateGraph supervisor pattern) |
| **Backend** | FastAPI (async), Python 3.12, Uvicorn |
| **Frontend** | React 18, Vite, TailwindCSS, Axios |
| **Search** | Tavily API |
| **PDF Generation** | markdown2 + xhtml2pdf + WeasyPrint |
| **Observability** | LangSmith |
| **Containerization** | Docker Compose, nginx (as reverse proxy) |

---

## 🚀 Quick Start

### Option A — Docker (Recommended)

```bash
git clone https://github.com/MuneebMM/researchpilot-ai
cd researchpilot-ai
cp .env.example .env
# Add your API keys to .env
docker compose up
# Open http://localhost:3000
```

### Option B — Local Development

```bash
# Clone & set up Python environment
git clone https://github.com/MuneebMM/researchpilot-ai
cd researchpilot-ai
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install frontend deps
cd frontend && npm install && cd ..

# Add your API keys to .env (copy from .env.example)

# Run backend (terminal 1)
uvicorn backend.api.main:app --reload --port 8000

# Run frontend (terminal 2)
cd frontend && npm run dev
```

Open [http://localhost:5173](http://localhost:5173) (Vite dev server) or [http://localhost:3000](http://localhost:3000) (Docker).

---

## ⚙️ Environment Variables

Create a `.env` file in the project root:

```env
# Google Gemini API key — get one at https://aistudio.google.com
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.1-flash-lite-preview

# Tavily search API key — get one at https://tavily.com
TAVILY_API_KEY=your_tavily_api_key_here

# LangSmith API key for agent observability — https://smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=researchpilot-ai
```

---

## 📁 Project Structure

```
researchpilot-ai/
├── backend/
│   ├── agents/                 # LangGraph agent nodes
│   │   ├── graph.py            # Main StateGraph orchestration
│   │   ├── state.py            # Shared ResearchState TypedDict
│   │   ├── supervisor.py       # Supervisor, critic & synthesizer nodes
│   │   └── specialized_agents.py   # Web/News/Tech/Financial agents
│   ├── api/
│   │   └── main.py             # FastAPI app + routes
│   ├── tools/
│   │   └── search.py           # Tavily search wrapper
│   ├── utils/
│   │   ├── llm.py              # Gemini LLM factory
│   │   ├── prompts.py          # System prompts for every agent
│   │   └── pdf_generator.py    # Markdown → styled PDF
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AgentStatus.jsx     # Live agent activity panel
│   │   │   └── ReportViewer.jsx    # Markdown report + PDF download
│   │   └── App.jsx                 # Main application
│   ├── Dockerfile
│   └── nginx.conf                  # Reverse-proxy config for /api
├── reports/                        # Generated PDF reports (gitignored)
├── docker-compose.yml              # Full-stack orchestration
├── requirements.txt                # Python dependencies
└── .env.example                    # Template for required env vars
```

---

## 🤖 Agent Architecture

### 🎯 Supervisor Agent
Analyses the research goal and decides which specialist agents to activate. Acts as the orchestrator and routes control to the correct downstream nodes.

### 🔍 Web Search Agent
Performs broad factual web research via Tavily. Focuses on official sources, company websites, and authoritative publications, returning a clean summary.

### 📰 News Agent
Pulls the latest news, press releases, and media coverage for the research goal. Summarises key themes and overall sentiment from recent events.

### ⚙️ Tech Strategy Agent
Investigates technology stack, AI initiatives, patents, and innovation strategy. Prioritises technical depth and strategic implications relevant to leadership.

### 💰 Financial Agent
Collects financial performance, market position, revenue, and investment activity. Emphasises quantitative facts, numbers, and observable trends.

### 🔁 Critic Agent
Reviews all gathered intelligence and decides whether another round of research is needed. A hard iteration guard (max 3) prevents infinite research loops.

### 📝 Synthesizer Agent
Compiles all findings into a concise, boardroom-ready intelligence report. Outputs structured markdown with executive summary, findings, risks, and conclusion.

---

## 📊 LangSmith Observability

Every agent invocation — LLM calls, tool calls, state transitions, retries — is automatically traced and recorded in LangSmith. This gives full visibility into what each agent did, how long it took, what tokens it used, and where errors occurred.

![LangSmith](docs/langsmith.png)

---

## 🗺️ Roadmap

- [x] Multi-agent supervisor architecture
- [x] Real-time web search integration
- [x] PDF report generation
- [x] React frontend with live agent status
- [x] Docker Compose deployment
- [ ] WebSocket streaming for real-time agent updates
- [ ] Redis caching for repeated research goals
- [ ] User authentication & per-user history
- [ ] Report history dashboard
- [ ] Multi-language support
- [ ] Export to Notion / Google Docs

---

## 👤 Author

**Built by Muneeb** — AI Engineer

- 🌐 GitHub: [@MuneebMM](https://github.com/MuneebMM)
- 💼 LinkedIn: _your linkedin_
- 📧 Email: muneebmm27@gmail.com

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
