import { motion, AnimatePresence } from "framer-motion";
import { useAppStore } from "@/stores/appStore";
import { Panel } from "@/components/shared/Panel";

export function GamePanel() {
  const { currentGame } = useAppStore();
  const active = Boolean(currentGame.name);

  return (
    <Panel title="Game Intelligence" accent={active ? "cyan" : "purple"} className="h-full">
      <AnimatePresence mode="wait">
        {active ? (
          <motion.div
            key={currentGame.id ?? "game"}
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.96 }}
            className="flex flex-col items-center gap-4 py-4"
          >
            <div className="text-center">
              <p className="font-display text-[8px] tracking-[0.4em] uppercase text-omnix-muted mb-1">
                Active Session
              </p>
              <h2 className="font-display text-2xl tracking-wider text-omnix-text animate-glow">
                {currentGame.name?.toUpperCase()}
              </h2>
            </div>
            <div className="relative w-20 h-20 flex items-center justify-center">
              <div className="absolute inset-0 rounded-full border-2 border-omnix-cyan/40 animate-ping" />
              <div className="absolute inset-2 rounded-full border border-omnix-cyan/30 animate-pulse-slow" />
              <span className="font-display text-omnix-cyan text-2xl">◈</span>
            </div>
            <p className="font-body text-sm text-omnix-muted text-center">
              OMNIX is active. Ask for strategies, builds, or tips.
            </p>
          </motion.div>
        ) : (
          <motion.div
            key="standby"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex flex-col items-center justify-center gap-3 py-8"
          >
            <div className="w-16 h-16 rounded-full border border-omnix-muted/20 flex items-center justify-center">
              <span className="font-display text-omnix-muted/30 text-xl">○</span>
            </div>
            <p className="font-display text-[9px] tracking-[0.3em] uppercase text-omnix-muted/40">
              No Game Detected
            </p>
            <p className="font-body text-xs text-omnix-muted/30 text-center">Launch a game to begin</p>
          </motion.div>
        )}
      </AnimatePresence>
    </Panel>
  );
}
