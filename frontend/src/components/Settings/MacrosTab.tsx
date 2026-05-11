import { useEffect, useState } from "react";
import { get, del, post } from "@/lib/api";
import { NeonButton } from "@/components/shared/NeonButton";

interface MacroStep {
  type: string;
  key?: string;
  duration_ms?: number;
}

interface Macro {
  id: string;
  name: string;
  steps: MacroStep[];
}

export function MacrosTab() {
  const [macros, setMacros]   = useState<Macro[]>([]);
  const [running, setRunning] = useState<string | null>(null);

  const load = async () => {
    try {
      const d = await get<{ macros: Macro[] }>("/macros");
      setMacros(d.macros ?? []);
    } catch { /* backend may not be ready */ }
  };

  useEffect(() => { load(); }, []);

  const execute = async (id: string) => {
    setRunning(id);
    try {
      await post(`/macros/${id}/execute`, {});
    } catch { /* ignore */ }
    finally { setRunning(null); }
  };

  const remove = async (id: string) => {
    try {
      await del(`/macros/${id}`);
      load();
    } catch { /* ignore */ }
  };

  return (
    <div className="flex flex-col gap-4 max-w-lg">
      <p className="font-display text-[9px] tracking-widest uppercase text-omnix-muted">
        Macros ({macros.length})
      </p>
      {macros.length === 0 ? (
        <p className="font-body text-sm text-omnix-muted/50">
          No macros saved. Create macros via the V1 app or API.
        </p>
      ) : (
        macros.map((m) => (
          <div
            key={m.id}
            className="flex items-center justify-between px-3 py-2.5 rounded-lg border border-omnix-border bg-black/30"
          >
            <div>
              <p className="font-body text-sm text-omnix-text">{m.name}</p>
              <p className="font-mono text-[9px] text-omnix-muted">{m.steps.length} steps</p>
            </div>
            <div className="flex gap-2">
              <NeonButton
                variant="secondary"
                size="sm"
                onClick={() => execute(m.id)}
                disabled={running === m.id}
              >
                {running === m.id ? "Running..." : "Run"}
              </NeonButton>
              <NeonButton variant="danger" size="sm" onClick={() => remove(m.id)}>
                Delete
              </NeonButton>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
