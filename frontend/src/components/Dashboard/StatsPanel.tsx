import { useEffect } from "react";
import { get } from "@/lib/api";
import { useAppStore } from "@/stores/appStore";
import { Panel } from "@/components/shared/Panel";

function StatBar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="flex flex-col gap-1">
      <div className="flex justify-between">
        <span className="font-display text-[8px] tracking-widest uppercase text-omnix-muted">{label}</span>
        <span className="font-mono text-[10px] text-omnix-text">{value.toFixed(1)}%</span>
      </div>
      <div className="h-1 bg-black/60 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${color}`}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}

export function StatsPanel() {
  const { cpu, ram, setStats } = useAppStore();

  useEffect(() => {
    const poll = async () => {
      try {
        const d = await get<{ cpu: number; ram: number }>("/stats/system");
        setStats(d.cpu, d.ram);
      } catch {
        // silently fail — backend may not be ready yet
      }
    };
    poll();
    const id = setInterval(poll, 1500);
    return () => clearInterval(id);
  }, [setStats]);

  return (
    <Panel title="System Telemetry" accent="purple" className="h-full">
      <div className="flex flex-col gap-4">
        <StatBar label="CPU" value={cpu} color="bg-omnix-cyan" />
        <StatBar label="RAM" value={ram} color="bg-omnix-purple" />
      </div>
    </Panel>
  );
}
