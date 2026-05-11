import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { useAppStore } from "@/stores/appStore";
import { AIConfigTab } from "./AIConfigTab";
import { KnowledgeTab } from "./KnowledgeTab";
import { MacrosTab } from "./MacrosTab";
import { LicenseTab } from "./LicenseTab";

const TABS = ["AI Config", "Knowledge", "Macros", "License"] as const;
type Tab = typeof TABS[number];

export function SettingsModal() {
  const { settingsOpen, setSettingsOpen } = useAppStore();
  const [activeTab, setActiveTab] = useState<Tab>("AI Config");

  return (
    <AnimatePresence>
      {settingsOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm z-40"
            onClick={() => setSettingsOpen(false)}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.94 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.94 }}
            transition={{ type: "spring", stiffness: 280, damping: 26 }}
            className="fixed inset-8 z-50 rounded-xl border border-omnix-cyan/30 bg-omnix-panel shadow-neon-cyan overflow-hidden flex flex-col"
          >
            <div className="flex items-center justify-between px-6 py-4 border-b border-omnix-border">
              <span className="font-display text-sm tracking-[0.3em] uppercase text-omnix-cyan">
                System Configuration
              </span>
              <button
                onClick={() => setSettingsOpen(false)}
                className="text-omnix-muted hover:text-omnix-red transition-colors font-mono"
              >
                ✕
              </button>
            </div>

            <div className="flex flex-1 overflow-hidden">
              <div className="w-40 border-r border-omnix-border p-3 flex flex-col gap-1">
                {TABS.map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`text-left px-3 py-2 rounded-lg font-display text-[9px] tracking-widest uppercase transition-all ${
                      activeTab === tab
                        ? "bg-omnix-cyan/15 text-omnix-cyan border border-omnix-cyan/30"
                        : "text-omnix-muted hover:text-omnix-text"
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              <div className="flex-1 overflow-y-auto p-6">
                {activeTab === "AI Config"  && <AIConfigTab />}
                {activeTab === "Knowledge"  && <KnowledgeTab />}
                {activeTab === "Macros"     && <MacrosTab />}
                {activeTab === "License"    && <LicenseTab />}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
