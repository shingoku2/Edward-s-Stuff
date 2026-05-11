import { motion } from "framer-motion";
import { clsx } from "clsx";

interface NeonButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger" | "ghost";
  size?: "sm" | "md" | "lg";
  children: React.ReactNode;
}

const variants = {
  primary:   "border-omnix-cyan/70 text-omnix-cyan hover:bg-omnix-cyan hover:text-black hover:shadow-neon-cyan",
  secondary: "border-omnix-purple/50 text-omnix-purple hover:bg-omnix-purple hover:text-white hover:shadow-neon-purple",
  danger:    "border-omnix-red/50 text-omnix-red hover:bg-omnix-red hover:text-white",
  ghost:     "border-omnix-muted/30 text-omnix-muted hover:border-omnix-cyan/40 hover:text-omnix-text",
};

const sizes = {
  sm: "px-3 py-1.5 text-[9px] tracking-[0.2em]",
  md: "px-4 py-2.5 text-[10px] tracking-[0.2em]",
  lg: "px-6 py-3 text-[11px] tracking-[0.25em]",
};

export function NeonButton({
  variant = "primary",
  size = "md",
  className,
  children,
  ...props
}: NeonButtonProps) {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.97 }}
      className={clsx(
        "relative font-display uppercase border rounded-md transition-all duration-200",
        "disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer",
        variants[variant],
        sizes[size],
        className
      )}
      {...(props as React.ComponentProps<typeof motion.button>)}
    >
      {children}
    </motion.button>
  );
}
