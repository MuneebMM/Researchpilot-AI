const statusConfig = {
  waiting: { label: "Waiting", classes: "bg-gray-700 text-gray-300" },
  running: { label: "Running...", classes: "bg-blue-600 text-blue-100 animate-pulse" },
  complete: { label: "Complete ✓", classes: "bg-green-700 text-green-100" },
  error: { label: "Error", classes: "bg-red-700 text-red-100" },
};

export default function AgentStatus({ agents = [], isRunning = false }) {
  return (
    <div className="bg-gray-900 rounded-xl p-5 text-white shadow-lg">
      {isRunning && (
        <div className="mb-4 h-1.5 w-full rounded-full bg-gray-700 overflow-hidden">
          <div className="h-full w-full bg-blue-500 animate-pulse rounded-full" />
        </div>
      )}

      <h2 className="text-lg font-semibold mb-4 text-gray-100">⚡ Agent Activity</h2>

      <ul className="space-y-2">
        {agents.map((agent) => {
          const { label, classes } = statusConfig[agent.status] ?? statusConfig.waiting;
          return (
            <li
              key={agent.name}
              className="flex items-center justify-between bg-gray-800 rounded-lg px-4 py-2.5"
            >
              <span className="flex items-center gap-2 text-sm text-gray-200">
                <span>{agent.icon}</span>
                <span>{agent.name}</span>
              </span>
              <span className={`text-xs font-medium px-2.5 py-0.5 rounded-full ${classes}`}>
                {label}
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
