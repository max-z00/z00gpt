"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  API_BASE,
  Dataset,
  fetchDatasets,
  fetchRuns,
  uploadDataset,
} from "../../lib/api";
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip } from "recharts";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  table?: { columns: string[]; rows: Record<string, string>[] } | null;
  chart?: { type: string; x: string; y: string; data: Record<string, string>[] } | null;
};

type Run = {
  id: string;
  created_at: string;
  response: { message: string };
};

export default function ProjectPage() {
  const params = useParams<{ id: string }>();
  const projectId = params?.id as string;
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [runs, setRuns] = useState<Run[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    try {
      const [datasetsData, runsData] = await Promise.all([
        fetchDatasets(projectId),
        fetchRuns(projectId),
      ]);
      setDatasets(datasetsData);
      setRuns(runsData);
      if (datasetsData.length > 0 && !selectedDataset) {
        setSelectedDataset(datasetsData[0]);
      }
    } catch (err) {
      setError((err as Error).message);
    }
  };

  useEffect(() => {
    void load();
  }, [projectId]);

  const handleUpload = async (file: File) => {
    setStatus("Uploading dataset...");
    try {
      const dataset = await uploadDataset(projectId, file);
      setDatasets([dataset, ...datasets]);
      setSelectedDataset(dataset);
      setStatus(null);
    } catch (err) {
      setError((err as Error).message);
      setStatus(null);
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;
    const newMessage: ChatMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, newMessage]);
    setInput("");
    setStatus("Thinking...");
    const response = await fetch(`${API_BASE}/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        project_id: projectId,
        dataset_id: selectedDataset?.id ?? null,
        messages: [...messages, newMessage],
        settings: { provider: "ollama", model: "llama3.1:8b", temperature: 0.2 },
      }),
    });
    if (!response.body) {
      setError("No response body from server");
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let assistantMessage: ChatMessage = { role: "assistant", content: "" };

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";
      for (const line of lines) {
        if (line.startsWith("data:")) {
          const data = JSON.parse(line.replace("data:", "").trim());
          if (data.token) {
            assistantMessage = {
              ...assistantMessage,
              content: assistantMessage.content + data.token,
            };
            setMessages((prev) => [...prev.slice(0, -1), assistantMessage]);
            if (messages.length === 0 || messages[messages.length - 1].role !== "assistant") {
              setMessages((prev) => [...prev, assistantMessage]);
            }
          }
          if (data.message) {
            assistantMessage = {
              role: "assistant",
              content: data.message,
              table: data.table,
              chart: data.chart,
            };
            setMessages((prev) => [...prev, assistantMessage]);
            setStatus(null);
            void load();
          }
        }
      }
    }
  };

  const chartData = useMemo(() => {
    const latest = messages.findLast((message) => message.chart)?.chart;
    return latest?.data ?? [];
  }, [messages]);

  return (
    <div className="grid gap-6 lg:grid-cols-[220px_1fr_280px]">
      <aside className="space-y-4">
        <div className="card">
          <p className="label">Datasets</p>
          <div className="space-y-2">
            {datasets.length === 0 ? (
              <p className="text-xs text-slate-400">No datasets yet.</p>
            ) : (
              datasets.map((dataset) => (
                <button
                  key={dataset.id}
                  onClick={() => setSelectedDataset(dataset)}
                  className={`w-full rounded-lg border px-3 py-2 text-left text-xs transition ${
                    selectedDataset?.id === dataset.id
                      ? "border-indigo-400 bg-indigo-500/20 text-white"
                      : "border-slate-700 text-slate-300 hover:border-indigo-400"
                  }`}
                >
                  {dataset.filename}
                </button>
              ))
            )}
          </div>
          <label className="mt-4 block text-xs text-slate-400">
            Upload dataset
            <input
              type="file"
              className="mt-2 block w-full text-xs text-slate-300"
              onChange={(event) => {
                const file = event.target.files?.[0];
                if (file) void handleUpload(file);
              }}
            />
          </label>
        </div>
        <div className="card">
          <p className="label">Quick links</p>
          {selectedDataset ? (
            <Link
              className="text-sm text-indigo-300"
              href={`/projects/${projectId}/datasets/${selectedDataset.id}`}
            >
              View dataset preview
            </Link>
          ) : (
            <p className="text-xs text-slate-400">Select a dataset to preview.</p>
          )}
        </div>
      </aside>
      <section className="space-y-4">
        <div className="card">
          <p className="label">Chat</p>
          <div className="space-y-4">
            {messages.length === 0 ? (
              <p className="text-sm text-slate-400">
                Ask questions about your dataset, like “show average value by category”.
              </p>
            ) : (
              messages.map((message, index) => (
                <div key={index}>
                  <p className="text-xs uppercase text-slate-400">{message.role}</p>
                  <p className="text-sm text-slate-100">{message.content}</p>
                  {message.table ? (
                    <div className="mt-2 overflow-x-auto rounded-lg border border-slate-800">
                      <table className="w-full text-xs text-slate-200">
                        <thead className="bg-slate-900">
                          <tr>
                            {message.table.columns.map((col) => (
                              <th key={col} className="px-2 py-1 text-left font-medium">
                                {col}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {message.table.rows.map((row, rowIndex) => (
                            <tr key={rowIndex} className="border-t border-slate-800">
                              {message.table?.columns.map((col) => (
                                <td key={col} className="px-2 py-1">
                                  {String(row[col] ?? "")}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : null}
                  {message.chart ? (
                    <div className="mt-2 h-48 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={message.chart.data}>
                          <XAxis dataKey={message.chart.x} stroke="#94a3b8" />
                          <YAxis stroke="#94a3b8" />
                          <Tooltip />
                          <Bar dataKey={message.chart.y} fill="#6366f1" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  ) : null}
                </div>
              ))
            )}
          </div>
          <div className="mt-4 flex gap-2">
            <textarea
              className="input min-h-[60px]"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask about your data..."
            />
            <button className="button" onClick={sendMessage}>
              Send
            </button>
          </div>
          {status ? <p className="mt-2 text-xs text-slate-400">{status}</p> : null}
          {error ? <p className="mt-2 text-xs text-rose-400">{error}</p> : null}
        </div>
      </section>
      <aside className="space-y-4">
        <div className="card">
          <p className="label">Dataset profile</p>
          {selectedDataset ? (
            <div className="space-y-2 text-xs text-slate-300">
              <p>Rows: {(selectedDataset.profile as any).row_count}</p>
              <p>Columns: {(selectedDataset.profile as any).column_count}</p>
              <p>
                Missing: {(selectedDataset.profile as any).data_health?.missing_pct ?? 0}%
              </p>
              <p>
                Duplicates: {(selectedDataset.profile as any).data_health?.duplicate_pct ?? 0}%
              </p>
            </div>
          ) : (
            <p className="text-xs text-slate-400">Upload a dataset to see profiling.</p>
          )}
        </div>
        <div className="card">
          <p className="label">Recent runs</p>
          <div className="space-y-2 text-xs text-slate-300">
            {runs.length === 0 ? (
              <p>No runs yet.</p>
            ) : (
              runs.slice(0, 5).map((run) => (
                <div key={run.id}>
                  <p>{run.created_at}</p>
                  <p className="text-slate-400">{run.response?.message}</p>
                </div>
              ))
            )}
          </div>
        </div>
        <div className="card">
          <p className="label">Latest chart</p>
          {chartData.length === 0 ? (
            <p className="text-xs text-slate-400">Charts will appear here.</p>
          ) : (
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <XAxis dataKey={Object.keys(chartData[0] ?? {})[0]} stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip />
                  <Bar dataKey={Object.keys(chartData[0] ?? {})[1]} fill="#38bdf8" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </aside>
    </div>
  );
}
