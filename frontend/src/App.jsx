import { useState } from "react";
import axios from "axios";
import AgentStatus from "./components/AgentStatus";
import ReportViewer from "./components/ReportViewer";

const INITIAL_AGENTS = [
  { name: "Supervisor Agent", status: "waiting", icon: "🎯" },
  { name: "Web Search Agent", status: "waiting", icon: "🔍" },
  { name: "News Agent", status: "waiting", icon: "📰" },
  { name: "Tech Strategy Agent", status: "waiting", icon: "⚙️" },
  { name: "Financial Agent", status: "waiting", icon: "💰" },
  { name: "Critic Agent", status: "waiting", icon: "🔍" },
  { name: "Synthesizer Agent", status: "waiting", icon: "📝" },
];

function setAgentStatuses(setAgents, updates) {
  setAgents((prev) =>
    prev.map((a) => (updates[a.name] ? { ...a, status: updates[a.name] } : a))
  );
}

export default function App() {
  const [researchGoal, setResearchGoal] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [report, setReport] = useState("");
  const [pdfUrl, setPdfUrl] = useState("");
  const [error, setError] = useState("");
  const [agents, setAgents] = useState(INITIAL_AGENTS);

  async function handleResearch() {
    setIsLoading(true);
    setError("");
    setReport("");
    setPdfUrl("");
    setAgents(INITIAL_AGENTS);

    const t1 = setTimeout(() => {
      setAgentStatuses(setAgents, {
        "Supervisor Agent": "complete",
        "Web Search Agent": "running",
        "News Agent": "running",
        "Tech Strategy Agent": "running",
        "Financial Agent": "running",
      });
    }, 1000);

    const t2 = setTimeout(() => {
      setAgentStatuses(setAgents, {
        "Web Search Agent": "complete",
        "News Agent": "complete",
        "Tech Strategy Agent": "complete",
        "Financial Agent": "complete",
        "Critic Agent": "running",
      });
    }, 8000);

    const t3 = setTimeout(() => {
      setAgentStatuses(setAgents, {
        "Critic Agent": "complete",
        "Synthesizer Agent": "running",
      });
    }, 12000);

    try {
      const res = await axios.post(
        "/api/research",
        { research_goal: researchGoal },
        { timeout: 300000 }
      );

      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);

      setAgentStatuses(setAgents, { "Synthesizer Agent": "complete" });
      setReport(res.data.result);
      setPdfUrl(res.data.pdf_url);
    } catch (err) {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);

      setError(err.response?.data?.detail ?? err.message ?? "Something went wrong.");
      setAgents((prev) =>
        prev.map((a) => (a.status === "running" ? { ...a, status: "error" } : a))
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="bg-gray-950 min-h-screen text-white">
      {/* Header */}
      <div className="text-center py-12 px-4">
        <h1 className="text-4xl font-extrabold tracking-tight mb-2">🤖 ResearchPilot AI</h1>
        <p className="text-gray-400 text-lg mb-3">Autonomous Multi-Agent Intelligence Research</p>
        <span className="inline-block bg-blue-700 text-blue-100 text-xs font-semibold px-3 py-1 rounded-full">
          Powered by Gemini + LangGraph
        </span>
      </div>

      {/* Input card */}
      <div className="max-w-3xl mx-auto px-4 mb-10">
        <div className="bg-gray-900 rounded-2xl p-6 shadow-xl">
          <textarea
            rows={4}
            value={researchGoal}
            onChange={(e) => setResearchGoal(e.target.value)}
            placeholder="Enter your research goal... e.g. What is Adobe's AI strategy in 2026?"
            className="w-full bg-gray-800 text-white border border-gray-600 rounded-xl p-4 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-gray-500 text-sm"
          />
          <button
            onClick={handleResearch}
            disabled={isLoading || !researchGoal.trim()}
            className="mt-4 w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white py-3 rounded-xl font-bold text-lg transition-colors"
          >
            {isLoading ? "⏳ Researching... (2-4 mins)" : "Generate Report 🚀"}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="max-w-3xl mx-auto px-4 mb-8">
          <div className="bg-red-900 border border-red-700 text-red-200 rounded-xl px-5 py-4 text-sm">
            <strong>Error:</strong> {error}
          </div>
        </div>
      )}

      {/* Two-column layout */}
      <div className="max-w-7xl mx-auto px-4 pb-16 grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AgentStatus agents={agents} isRunning={isLoading} />
        <ReportViewer report={report} pdfUrl={pdfUrl} isLoading={isLoading} />
      </div>
    </div>
  );
}
