"use client";
import React, { useState, useEffect, useRef, useCallback } from "react";

interface Agent {
  id: string;
  role: string;
  status: string;
  progress: number;
  energy: number;
}

interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
}

interface GraphData {
  nodes: { id: string }[];
  links: { source: string; target: string; type: string }[];
}

const STATUS_COLOR: Record<string, string> = {
  STANDBY: "text-cyan-700 border-cyan-700",
  WORKING: "text-green-400 border-green-400",
  IDLE: "text-gray-500 border-gray-500",
  ERROR: "text-red-400 border-red-400",
};

function AgentCard({ agent }: { agent: Agent }) {
  const color = STATUS_COLOR[agent.status] || "text-cyan-700 border-cyan-700";
  return (
    <div className="border border-cyan-900 rounded p-3 bg-black/40 mb-3">
      <div className="flex justify-between items-start mb-1">
        <p className="text-xs font-mono text-cyan-300 leading-tight">{agent.role}</p>
        <span className={`text-[10px] font-mono border px-1 rounded ${color}`}>{agent.status}</span>
      </div>
      <div className="w-full h-1 bg-cyan-950 rounded mt-2">
        <div
          className="h-full bg-cyan-400 rounded transition-all duration-500"
          style={{ width: `${agent.progress}%`, boxShadow: "0 0 6px #22d3ee" }}
        />
      </div>
      <div className="flex justify-between mt-1">
        <span className="text-[10px] text-cyan-700 font-mono">PROGRESS</span>
        <span className="text-[10px] text-cyan-400 font-mono">{agent.progress}%</span>
      </div>
    </div>
  );
}

function LogPanel({ logs }: { logs: LogEntry[] }) {
  const bottomRef = useRef<HTMLDivElement>(null);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [logs]);

  const levelColor: Record<string, string> = {
    INFO: "text-cyan-400", SUCCESS: "text-green-400",
    WARNING: "text-yellow-400", ERROR: "text-red-400",
  };

  return (
    <div className="flex-1 overflow-y-auto font-mono text-xs space-y-1 pr-1" style={{ maxHeight: "260px" }}>
      {logs.length === 0 && (
        <p className="text-cyan-900 text-center mt-4">Awaiting transmissions...</p>
      )}
      {logs.map((log, i) => (
        <div key={i} className="flex gap-2">
          <span className="text-cyan-900 shrink-0">
            {log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : "--:--"}
          </span>
          <span className={`shrink-0 ${levelColor[log.level] || "text-cyan-400"}`}>[{log.level}]</span>
          <span className="text-cyan-300 break-all">{log.message}</span>
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
}

export default function FridayHUD() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
  const [command, setCommand] = useState("");
  const [intelLevel, setIntelLevel] = useState(1000);
  const [missionCount, setMissionCount] = useState(0);
  const [coreStatus, setCoreStatus] = useState("INITIALIZING");
  const [commandStatus, setCommandStatus] = useState("");
  const wsRef = useRef<WebSocket | null>(null);

  // Fetch full state on mount + every 10s
  const fetchState = useCallback(async () => {
    try {
      const res = await fetch("http://localhost:8000/state");
      if (!res.ok) return;
      const data = await res.json();
      setAgents(data.agents || []);
      setLogs(data.logs || []);
      setIntelLevel(data.intel_level || 1000);
      setMissionCount(data.mission_count || 0);
      setCoreStatus(data.status || "ONLINE");
      if (data.knowledge_graph) setGraphData(data.knowledge_graph);
    } catch {
      setCoreStatus("API OFFLINE");
    }
  }, []);

  useEffect(() => {
    fetchState();
    const interval = setInterval(fetchState, 10000);
    return () => clearInterval(interval);
  }, [fetchState]);

  // WebSocket for real-time updates
  useEffect(() => {
    const connect = () => {
      const ws = new WebSocket("ws://localhost:8000/ws/hud");
      wsRef.current = ws;

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === "INIT") {
            setAgents(msg.payload.agents || []);
            setIntelLevel(msg.payload.intel_level || 1000);
          } else if (msg.type === "LOG") {
            setLogs((prev) => [...prev.slice(-99), msg.payload]);
          } else if (msg.type === "AGENT_UPDATE") {
            setAgents((prev) =>
              prev.map((a) =>
                a.role === msg.payload.name
                  ? { ...a, status: msg.payload.status, progress: msg.payload.progress }
                  : a
              )
            );
          } else if (msg.type === "CORE_UPGRADE") {
            setIntelLevel(msg.payload.intel_level);
          }
        } catch {}
      };

      ws.onclose = () => {
        setTimeout(connect, 3000); // Auto-reconnect
      };
    };
    connect();
    return () => wsRef.current?.close();
  }, []);

  const sendCommand = async () => {
    if (!command.trim()) return;
    setCommandStatus("Transmitting...");
    try {
      const res = await fetch("http://localhost:8000/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command }),
      });
      if (res.ok) {
        setCommandStatus("Command received. Mission initiated.");
        setLogs((prev) => [
          ...prev,
          { timestamp: new Date().toISOString(), level: "INFO", message: `COMMAND: ${command}` },
        ]);
        setMissionCount((c) => c + 1);
      } else {
        setCommandStatus("Transmission failed.");
      }
    } catch {
      setCommandStatus("API offline — command not sent.");
    }
    setCommand("");
    setTimeout(() => setCommandStatus(""), 3000);
  };

  return (
    <main className="bg-black text-cyan-400 min-h-screen overflow-hidden flex flex-col">
      {/* Header */}
      <header className="p-5 border-b border-cyan-900 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tighter font-mono">
            FRIDAY OS <span className="text-xs text-cyan-700">OS-1.0-ALIVE</span>
          </h1>
          <p className="text-xs text-cyan-700 font-mono mt-0.5">Autonomous Data Intelligence Agency</p>
        </div>
        <div className="flex gap-4 text-xs font-mono">
          <div className="border border-cyan-800 px-3 py-1.5 rounded">
            <span className="text-cyan-700">MISSIONS </span>
            <span className="text-cyan-300">{missionCount}</span>
          </div>
          <div className="border border-cyan-800 px-3 py-1.5 rounded">
            <span className="text-cyan-700">INTEL LVL </span>
            <span className="text-cyan-300">{intelLevel}</span>
          </div>
          <div
            className={`px-3 py-1.5 border rounded animate-pulse font-mono text-xs ${
              coreStatus === "ONLINE" ? "border-green-700 text-green-400" : "border-red-700 text-red-400"
            }`}
          >
            CORE: {coreStatus}
          </div>
        </div>
      </header>

      {/* Main 3-column layout */}
      <div className="flex-1 flex p-4 gap-4 overflow-hidden">
        {/* Left: Agent Cards */}
        <section className="w-64 flex flex-col border border-cyan-900 rounded-lg p-3 bg-black/30">
          <h2 className="text-xs font-mono text-cyan-600 uppercase tracking-widest mb-3 pb-2 border-b border-cyan-900">
            Neural Units ({agents.length})
          </h2>
          <div className="flex-1 overflow-y-auto pr-1">
            {agents.length === 0 ? (
              <p className="text-cyan-900 text-xs text-center mt-6">Initializing workforce...</p>
            ) : (
              agents.map((agent) => <AgentCard key={agent.id} agent={agent} />)
            )}
          </div>
        </section>

        {/* Center: Live log feed */}
        <section className="flex-1 flex flex-col border border-cyan-900 rounded-lg p-4 bg-black/30">
          <h2 className="text-xs font-mono text-cyan-600 uppercase tracking-widest mb-3 pb-2 border-b border-cyan-900">
            Mission Log Feed
          </h2>
          <LogPanel logs={logs} />

          {/* Knowledge graph summary */}
          <div className="mt-4 border-t border-cyan-900 pt-3">
            <p className="text-xs font-mono text-cyan-700 uppercase tracking-widest mb-2">Knowledge Graph</p>
            <div className="flex gap-4 text-xs font-mono">
              <span className="text-cyan-300">{graphData.nodes.length} nodes</span>
              <span className="text-cyan-700">|</span>
              <span className="text-cyan-300">{graphData.links.length} links</span>
            </div>
            {graphData.nodes.slice(0, 5).map((n) => (
              <span key={n.id} className="inline-block text-[10px] border border-cyan-900 text-cyan-700 px-2 py-0.5 rounded mr-1 mt-1">
                {n.id}
              </span>
            ))}
          </div>
        </section>

        {/* Right: Metrics */}
        <section className="w-52 flex flex-col gap-3">
          {[
            { label: "Agents Online", value: agents.filter((a) => a.status !== "STANDBY").length },
            { label: "Active Missions", value: missionCount },
            { label: "Intel Level", value: intelLevel },
            { label: "Workforce Size", value: agents.length },
          ].map((m) => (
            <div key={m.label} className="border border-cyan-900 rounded-lg p-3 bg-black/40">
              <p className="text-[10px] font-mono text-cyan-700 uppercase">{m.label}</p>
              <p className="text-3xl font-mono font-bold text-cyan-300 mt-1">{m.value}</p>
            </div>
          ))}

          <div className="border border-cyan-900 rounded-lg p-3 bg-black/40 mt-auto">
            <p className="text-[10px] font-mono text-cyan-700 uppercase mb-2">System Health</p>
            {["CPU", "RAM", "DB"].map((metric, i) => {
              const vals = [42, 67, 31];
              return (
                <div key={metric} className="mb-2">
                  <div className="flex justify-between text-[10px] font-mono mb-0.5">
                    <span className="text-cyan-700">{metric}</span>
                    <span className="text-cyan-400">{vals[i]}%</span>
                  </div>
                  <div className="h-1 bg-cyan-950 rounded">
                    <div className="h-full bg-cyan-500 rounded" style={{ width: `${vals[i]}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      </div>

      {/* Footer: Command input — fully wired */}
      <footer className="border-t border-cyan-900 p-4">
        <div className="flex gap-3 max-w-4xl mx-auto">
          <input
            type="text"
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendCommand()}
            placeholder="TRANSMIT COMMAND TO FRIDAY CEO..."
            className="flex-1 bg-transparent border-b-2 border-cyan-700 py-3 px-2 text-lg font-mono focus:outline-none focus:border-cyan-400 text-cyan-300 placeholder:text-cyan-900"
          />
          <button
            onClick={sendCommand}
            className="px-6 py-3 border border-cyan-600 text-cyan-400 font-mono text-sm rounded hover:bg-cyan-900/30 transition-colors"
          >
            TRANSMIT
          </button>
        </div>
        {commandStatus && (
          <p className="text-center text-xs font-mono text-cyan-600 mt-2">{commandStatus}</p>
        )}
      </footer>
    </main>
  );
}
