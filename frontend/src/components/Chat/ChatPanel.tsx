import { useRef, useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAppStore } from "@/stores/appStore";
import { useOmnixWS } from "@/hooks/useOmnixWS";
import { Panel } from "@/components/shared/Panel";
import { NeonButton } from "@/components/shared/NeonButton";
import { ChatBubble } from "./ChatBubble";

export function ChatPanel() {
  const { messages, aiStatus, currentGame, addUserMessage, clearChat } = useAppStore();
  const { sendChat } = useOmnixWS();
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = () => {
    const text = input.trim();
    if (!text || aiStatus === "thinking") return;
    addUserMessage(text);
    sendChat(
      text,
      currentGame.id ? { game_id: currentGame.id, game_name: currentGame.name } : undefined
    );
    setInput("");
  };

  return (
    <Panel title="Neural Interface" className="flex flex-col h-full" animate={false}>
      <div className="flex items-center gap-2 px-4 pb-2">
        <div
          className={`w-1.5 h-1.5 rounded-full ${
            aiStatus === "thinking"
              ? "bg-omnix-cyan animate-pulse"
              : aiStatus === "error"
              ? "bg-omnix-red"
              : "bg-omnix-green"
          }`}
        />
        <span className="font-display text-[8px] tracking-widest uppercase text-omnix-muted">
          {aiStatus === "thinking" ? "Processing..." : aiStatus === "error" ? "Error" : "Standby"}
        </span>
        <button
          onClick={clearChat}
          className="ml-auto font-display text-[8px] uppercase text-omnix-muted/50 hover:text-omnix-muted"
        >
          Clear
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-2 py-2 flex flex-col gap-3">
        <AnimatePresence initial={false}>
          {messages.length === 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center justify-center h-full"
            >
              <div className="text-center">
                <div className="font-display text-omnix-cyan/30 text-4xl mb-2">◈</div>
                <p className="font-display text-[9px] tracking-[0.3em] uppercase text-omnix-muted/40">
                  Ask OMNIX anything
                </p>
              </div>
            </motion.div>
          )}
          {messages.map((msg) => (
            <ChatBubble
              key={msg.id}
              role={msg.role}
              content={msg.content}
              streaming={msg.streaming}
            />
          ))}
        </AnimatePresence>
        <div ref={bottomRef} />
      </div>

      <div className="flex gap-2 pt-3 border-t border-omnix-border">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
          placeholder="Ask OMNIX..."
          disabled={aiStatus === "thinking"}
          className="flex-1 bg-black/40 border border-omnix-border rounded-full px-4 py-2.5 text-[12px] font-body text-omnix-text placeholder:text-omnix-muted/40 focus:outline-none focus:border-omnix-cyan/60 transition-colors disabled:opacity-50"
        />
        <NeonButton onClick={handleSend} disabled={aiStatus === "thinking"} size="sm">
          ▶
        </NeonButton>
      </div>
    </Panel>
  );
}
