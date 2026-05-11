import { getCurrentWindow } from "@tauri-apps/api/window";
import { useAppStore } from "@/stores/appStore";

export function TitleBar() {
  const { toggleOverlay, setSettingsOpen } = useAppStore();
  const win = getCurrentWindow();

  return (
    <div
      data-tauri-drag-region
      className="flex items-center h-12 px-4 border-b border-omnix-border bg-omnix-panel/95 select-none"
    >
      <div className="flex items-center gap-3">
        <span className="font-display text-xl tracking-[0.35em] text-omnix-cyan animate-glow">OMNIX</span>
        <span className="font-display text-[8px] tracking-[0.4em] uppercase text-omnix-muted/60">
          // ALL-KNOWING
        </span>
      </div>
      <div className="flex-1" data-tauri-drag-region />
      <div className="flex items-center gap-2 mr-4">
        <button
          onClick={toggleOverlay}
          className="font-display text-[8px] tracking-widest uppercase text-omnix-muted hover:text-omnix-cyan transition-colors px-2 py-1"
        >
          Overlay
        </button>
        <button
          onClick={() => setSettingsOpen(true)}
          className="font-display text-[8px] tracking-widest uppercase text-omnix-muted hover:text-omnix-cyan transition-colors px-2 py-1"
        >
          Settings
        </button>
      </div>
      <div className="flex items-center gap-1.5">
        <button
          onClick={() => win.minimize()}
          className="w-3 h-3 rounded-full bg-omnix-muted/30 hover:bg-yellow-400 transition-colors"
        />
        <button
          onClick={() => win.hide()}
          className="w-3 h-3 rounded-full bg-omnix-muted/30 hover:bg-omnix-red transition-colors"
        />
      </div>
    </div>
  );
}
