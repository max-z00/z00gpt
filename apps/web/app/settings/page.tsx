"use client";

import { useState } from "react";

export default function SettingsPage() {
  const [provider, setProvider] = useState("ollama");
  const [model, setModel] = useState("llama3.1:8b");
  const [temperature, setTemperature] = useState(0.2);
  const [status, setStatus] = useState<string | null>(null);

  const testConnection = async () => {
    setStatus("Testing connection...");
    try {
      const response = await fetch("http://localhost:11434/api/tags");
      if (!response.ok) throw new Error("Ollama not reachable");
      setStatus("Connection successful.");
    } catch (err) {
      setStatus((err as Error).message);
    }
  };

  return (
    <div className="card space-y-6">
      <div>
        <p className="label">LLM settings</p>
        <h1 className="text-2xl font-semibold">Model connection</h1>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <label className="text-xs text-slate-400">
          Provider
          <select
            className="input mt-2"
            value={provider}
            onChange={(event) => setProvider(event.target.value)}
          >
            <option value="ollama">Ollama</option>
            <option value="llamacpp">llama.cpp</option>
          </select>
        </label>
        <label className="text-xs text-slate-400">
          Model
          <input
            className="input mt-2"
            value={model}
            onChange={(event) => setModel(event.target.value)}
          />
        </label>
        <label className="text-xs text-slate-400">
          Temperature
          <input
            className="input mt-2"
            type="number"
            step="0.1"
            value={temperature}
            onChange={(event) => setTemperature(Number(event.target.value))}
          />
        </label>
      </div>
      <button className="button-secondary" onClick={testConnection}>
        Test connection
      </button>
      {status ? <p className="text-xs text-slate-400">{status}</p> : null}
    </div>
  );
}
