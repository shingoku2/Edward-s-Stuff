import { useEffect, useState } from "react";
import { get, post } from "@/lib/api";
import { NeonButton } from "@/components/shared/NeonButton";

export function AIConfigTab() {
  const [host, setHost]     = useState("http://localhost:11434");
  const [model, setModel]   = useState("llama3");
  const [models, setModels] = useState<string[]>([]);
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState("");

  useEffect(() => {
    get<{ ollama_host: string; ollama_model: string }>("/config").then((cfg) => {
      setHost(cfg.ollama_host);
      setModel(cfg.ollama_model);
    });
    fetchModels();
  }, []);

  const fetchModels = async () => {
    const d = await get<{ models: string[] }>("/ollama/models");
    setModels(d.models);
  };

  const save = async () => {
    setSaving(true);
    try {
      await post("/config/ollama", { host, model });
      setStatus("Saved.");
    } catch {
      setStatus("Failed to save.");
    } finally {
      setSaving(false);
      setTimeout(() => setStatus(""), 2000);
    }
  };

  return (
    <div className="flex flex-col gap-6 max-w-lg">
      <div>
        <label className="block font-display text-[9px] tracking-widest uppercase text-omnix-muted mb-2">
          Ollama Host
        </label>
        <input
          value={host}
          onChange={(e) => setHost(e.target.value)}
          className="w-full bg-black/40 border border-omnix-border rounded-lg px-4 py-2.5 text-sm font-mono text-omnix-text focus:outline-none focus:border-omnix-cyan/60"
        />
      </div>
      <div>
        <label className="block font-display text-[9px] tracking-widest uppercase text-omnix-muted mb-2">
          Model
        </label>
        {models.length > 0 ? (
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="w-full bg-black/40 border border-omnix-border rounded-lg px-4 py-2.5 text-sm font-mono text-omnix-text focus:outline-none focus:border-omnix-cyan/60"
          >
            {models.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        ) : (
          <input
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="w-full bg-black/40 border border-omnix-border rounded-lg px-4 py-2.5 text-sm font-mono text-omnix-text focus:outline-none focus:border-omnix-cyan/60"
          />
        )}
        <button
          onClick={fetchModels}
          className="mt-1 font-display text-[8px] uppercase text-omnix-muted/50 hover:text-omnix-muted"
        >
          Refresh models
        </button>
      </div>
      <div className="flex items-center gap-3">
        <NeonButton onClick={save} disabled={saving}>
          {saving ? "Saving..." : "Save Configuration"}
        </NeonButton>
        {status && (
          <span className="font-display text-[9px] uppercase text-omnix-cyan">{status}</span>
        )}
      </div>
    </div>
  );
}
