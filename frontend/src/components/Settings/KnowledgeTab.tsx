import { useEffect, useState } from "react";
import { get, del, post } from "@/lib/api";
import { NeonButton } from "@/components/shared/NeonButton";

interface Pack {
  id: string;
  name: string;
  game_profile_id: string;
}

export function KnowledgeTab() {
  const [packs, setPacks]       = useState<Pack[]>([]);
  const [source, setSource]     = useState("");
  const [gameId, setGameId]     = useState("");
  const [packName, setPackName] = useState("");
  const [loading, setLoading]   = useState(false);
  const [status, setStatus]     = useState("");

  const load = async () => {
    try {
      const d = await get<{ packs: Pack[] }>("/knowledge/packs");
      setPacks(d.packs ?? []);
    } catch {
      // backend may not be ready
    }
  };

  useEffect(() => { load(); }, []);

  const handleIngest = async () => {
    if (!source.trim() || !gameId.trim()) return;
    setLoading(true);
    try {
      await post("/knowledge/ingest", {
        source: source.trim(),
        game_profile_id: gameId.trim(),
        pack_name: packName.trim() || undefined,
      });
      setStatus("Ingested.");
      setSource(""); setGameId(""); setPackName("");
      load();
    } catch (e: unknown) {
      setStatus(`Error: ${e instanceof Error ? e.message : "unknown"}`);
    } finally {
      setLoading(false);
      setTimeout(() => setStatus(""), 3000);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await del(`/knowledge/packs/${id}`);
      load();
    } catch { /* ignore */ }
  };

  return (
    <div className="flex flex-col gap-6 max-w-lg">
      <div>
        <p className="font-display text-[9px] tracking-widest uppercase text-omnix-muted mb-3">
          Ingest New Source
        </p>
        <div className="flex flex-col gap-2">
          <input
            value={source}
            onChange={(e) => setSource(e.target.value)}
            placeholder="URL or file path"
            className="w-full bg-black/40 border border-omnix-border rounded-lg px-4 py-2.5 text-sm font-mono text-omnix-text focus:outline-none focus:border-omnix-cyan/60"
          />
          <input
            value={gameId}
            onChange={(e) => setGameId(e.target.value)}
            placeholder="Game profile ID"
            className="w-full bg-black/40 border border-omnix-border rounded-lg px-4 py-2.5 text-sm font-mono text-omnix-text focus:outline-none focus:border-omnix-cyan/60"
          />
          <input
            value={packName}
            onChange={(e) => setPackName(e.target.value)}
            placeholder="Pack name (optional)"
            className="w-full bg-black/40 border border-omnix-border rounded-lg px-4 py-2.5 text-sm font-mono text-omnix-text focus:outline-none focus:border-omnix-cyan/60"
          />
          <div className="flex items-center gap-3">
            <NeonButton onClick={handleIngest} disabled={loading}>
              {loading ? "Ingesting..." : "Ingest"}
            </NeonButton>
            {status && (
              <span className="font-display text-[9px] uppercase text-omnix-cyan">{status}</span>
            )}
          </div>
        </div>
      </div>

      <div>
        <p className="font-display text-[9px] tracking-widest uppercase text-omnix-muted mb-3">
          Knowledge Packs ({packs.length})
        </p>
        {packs.length === 0 ? (
          <p className="font-body text-sm text-omnix-muted/50">No packs installed.</p>
        ) : (
          <div className="flex flex-col gap-2">
            {packs.map((p) => (
              <div
                key={p.id}
                className="flex items-center justify-between px-3 py-2 rounded-lg border border-omnix-border bg-black/30"
              >
                <div>
                  <p className="font-body text-sm text-omnix-text">{p.name}</p>
                  <p className="font-mono text-[9px] text-omnix-muted">{p.game_profile_id}</p>
                </div>
                <NeonButton variant="danger" size="sm" onClick={() => handleDelete(p.id)}>
                  Delete
                </NeonButton>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
