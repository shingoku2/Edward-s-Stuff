import { motion } from "framer-motion";
import { clsx } from "clsx";

interface PanelProps {
  title?: string;
  accent?: "cyan" | "purple" | "pink";
  className?: string;
  children: React.ReactNode;
  animate?: boolean;
}

const accentMap = {
  cyan:   "border-omnix-cyan/30 shadow-neon-cyan",
  purple: "border-omnix-purple/30 shadow-neon-purple",
  pink:   "border-omnix-pink/30 shadow-neon-pink",
};

export function Panel({ title, accent = "cyan", className, children, animate = true }: PanelProps) {
  const Wrapper = animate ? motion.div : "div";
  const props   = animate
    ? { initial: { opacity: 0, y: 8 }, animate: { opacity: 1, y: 0 }, transition: { duration: 0.3 } }
    : {};
  return (
    <Wrapper
      className={clsx(
        "relative rounded-xl border bg-omnix-panel/90 backdrop-blur-sm shadow-panel overflow-hidden",
        accentMap[accent],
        className
      )}
      {...(props as object)}
    >
      <span className="absolute top-0 left-0 w-3 h-3 border-t border-l border-omnix-cyan/60 rounded-tl-xl" />
      <span className="absolute top-0 right-0 w-3 h-3 border-t border-r border-omnix-cyan/60 rounded-tr-xl" />
      <span className="absolute bottom-0 left-0 w-3 h-3 border-b border-l border-omnix-cyan/60 rounded-bl-xl" />
      <span className="absolute bottom-0 right-0 w-3 h-3 border-b border-r border-omnix-cyan/60 rounded-br-xl" />
      {title && (
        <div className="px-4 pt-3 pb-2 border-b border-omnix-border">
          <span className="font-display text-[9px] tracking-[0.3em] uppercase text-omnix-cyan">{title}</span>
        </div>
      )}
      <div className="p-4">{children}</div>
    </Wrapper>
  );
}
