import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAppStore } from "@/stores/appStore";
import { useOmnixWS } from "@/hooks/useOmnixWS";
import { ChatBubble } from "@/components/Chat/ChatBubble";

export function OverlayPanel() {
  const { overlayVisible, messages, aiStatus, addUserMessage, currentGame } = useAppStore();
  const { sendChat } = useOmnixWS();
  const [input, setInput] = useState("");
  const [minimized, setMinimized] = useState(false);

  const handleSend = () => {
    const text = input.trim();
    if (!text || aiStatus === "thinking") return;
    addUserMessage(text);
    sendChat(text, currentGame.id ? { game_id: currentGame.id } : undefined);
    setInput("");
  };

  return (
    <AnimatePresence>
      {overlayVisible && (
        <motion.div
          initial={{ opacity: 0, scale: 0.92, x: 20 }}
          animate={{ opacity: 1, scale: 1, x: 0 }}
          exit={{ opacity: 0, scale: 0.92, x: 20 }}
          transition={{ type: "spring", stiffness: 300, damping: 28 }}
          className="fixed right-4 top-16 w-80 z-50 rounded-xl border border-omnix-cyan/40 bg-black/85 backdrop-blur-md shadow-neon-cyan overflow-hidden"
        >
          <div className="flex items-center justify-between px-3 py-2 border-b border-omnix-border">
            <span className="font-display text-[8px] tracking-[0.3em] text-omnix-cyan">
              OMNIX // OVERLAY
            </span>
            <button
              onClick={() => setMinimized(!minimized)}
              className="text-omnix-muted hover:text-omnix-text text-xs font-mono"
            >
              {minimized ? "▼" : "─"}
            </button>
          </div>

          <AnimatePresence>
            {!minimized && (
              <motion.div
                initial={{ height: 0 }}
                animate={{ height: "auto" }}
                exit={{ height: 0 }}
                className="overflow-hidden"
              >
                <div className="max-h-48 overflow-y-auto p-3 flex flex-col gap-2">
                  {messages.slice(-3).map((msg) => (
                    <ChatBubble
                      key={msg.id}
                      role={msg.role}
                      content={msg.content}
                      streaming={msg.streaming}
                    />
                  ))}
                </div>
                <div className="flex gap-1.5 p-3 border-t border-omnix-border">
                  <input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSend()}
                    placeholder="Ask OMNIX..."
                    className="flex-1 bg-black/60 border border-omnix-border rounded-full px-3 py-1.5 text-[11px] font-body text-omnix-text placeholder:text-omnix-muted/40 focus:outline-none focus:border-omnix-cyan/60"
                  />
                  <button
                    onClick={handleSend}
                    className="w-7 h-7 rounded-full border border-omnix-cyan/50 text-omnix-cyan font-mono text-xs hover:bg-omnix-cyan hover:text-black transition-colors"
                  >
                    ▶
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
