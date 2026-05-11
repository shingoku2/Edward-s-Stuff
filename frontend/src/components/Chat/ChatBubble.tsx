import { motion } from "framer-motion";
import { clsx } from "clsx";

interface ChatBubbleProps {
  role: "user" | "assistant";
  content: string;
  streaming?: boolean;
}

export function ChatBubble({ role, content, streaming }: ChatBubbleProps) {
  const isUser = role === "user";
  return (
    <motion.div
      initial={{ opacity: 0, x: isUser ? 8 : -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.2 }}
      className={clsx("flex flex-col gap-1 max-w-[92%]", isUser ? "ml-auto items-end" : "items-start")}
    >
      <span
        className={clsx(
          "font-display text-[8px] tracking-[0.25em] uppercase",
          isUser ? "text-omnix-pink" : "text-omnix-cyan"
        )}
      >
        {isUser ? "YOU" : "OMNIX"}
      </span>
      <div
        className={clsx(
          "relative px-3 py-2 rounded-lg text-[12px] font-body text-omnix-text leading-relaxed",
          isUser
            ? "bg-omnix-pink/10 border border-omnix-pink/30"
            : "bg-omnix-cyan/5 border border-omnix-border"
        )}
      >
        {content}
        {streaming && (
          <span className="inline-block w-1 h-3 ml-0.5 bg-omnix-cyan animate-pulse align-middle" />
        )}
      </div>
    </motion.div>
  );
}
