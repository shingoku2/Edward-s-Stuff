import { useEffect } from "react";
import { listen } from "@tauri-apps/api/event";
import { useOmnixWS } from "@/hooks/useOmnixWS";
import { useAppStore } from "@/stores/appStore";
import { ParticleField } from "@/components/FX/ParticleField";
import { ScanLine } from "@/components/FX/ScanLine";
import { TitleBar } from "@/components/shared/TitleBar";
import { ChatPanel } from "@/components/Chat/ChatPanel";
import { GamePanel } from "@/components/Dashboard/GamePanel";
import { StatsPanel } from "@/components/Dashboard/StatsPanel";
import { OverlayPanel } from "@/components/Overlay/OverlayPanel";
import { SettingsModal } from "@/components/Settings/SettingsModal";

export default function App() {
  useOmnixWS();
  const { toggleOverlay } = useAppStore();

  useEffect(() => {
    const unlisten = listen("toggle-overlay", () => toggleOverlay());
    return () => {
      unlisten.then((f) => f());
    };
  }, [toggleOverlay]);

  return (
    <div className="relative w-screen h-screen bg-omnix-bg overflow-hidden font-body text-omnix-text">
      <ParticleField />
      <ScanLine />
      <div className="relative z-10 flex flex-col h-full">
        <TitleBar />
        <div className="flex-1 grid grid-cols-12 gap-3 p-3 overflow-hidden">
          <div className="col-span-4 flex flex-col min-h-0">
            <ChatPanel />
          </div>
          <div className="col-span-5 flex flex-col gap-3 min-h-0">
            <GamePanel />
          </div>
          <div className="col-span-3 flex flex-col gap-3 min-h-0">
            <StatsPanel />
          </div>
        </div>
      </div>
      <OverlayPanel />
      <SettingsModal />
    </div>
  );
}
