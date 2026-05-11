/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        omnix: {
          bg:        "#020812",
          panel:     "#080f1e",
          border:    "rgba(34, 211, 238, 0.25)",
          cyan:      "#22d3ee",
          "cyan-dim":"rgba(34, 211, 238, 0.15)",
          purple:    "#a855f7",
          pink:      "#ec4899",
          green:     "#4ade80",
          red:       "#f87171",
          text:      "#e2e8f0",
          muted:     "#64748b",
        },
      },
      fontFamily: {
        display: ["'Orbitron'", "monospace"],
        body:    ["'Rajdhani'", "sans-serif"],
        mono:    ["'JetBrains Mono'", "monospace"],
      },
      animation: {
        "pulse-slow": "pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "scan":       "scan 3s linear infinite",
        "glow":       "glow 2s ease-in-out infinite alternate",
        "slide-up":   "slideUp 0.4s ease-out",
        "slide-in":   "slideIn 0.3s ease-out",
        "flicker":    "flicker 0.15s infinite",
      },
      keyframes: {
        scan:     { "0%": { transform: "translateY(-100%)" }, "100%": { transform: "translateY(100vh)" } },
        glow:     { "0%": { "text-shadow": "0 0 4px #22d3ee, 0 0 8px #22d3ee" }, "100%": { "text-shadow": "0 0 8px #22d3ee, 0 0 20px #22d3ee, 0 0 40px #22d3ee" } },
        slideUp:  { "0%": { opacity: "0", transform: "translateY(12px)" }, "100%": { opacity: "1", transform: "translateY(0)" } },
        slideIn:  { "0%": { opacity: "0", transform: "translateX(-8px)" }, "100%": { opacity: "1", transform: "translateX(0)" } },
        flicker:  { "0%, 100%": { opacity: "1" }, "50%": { opacity: "0.85" } },
      },
      boxShadow: {
        "neon-cyan":   "0 0 8px rgba(34, 211, 238, 0.4), 0 0 24px rgba(34, 211, 238, 0.15)",
        "neon-purple": "0 0 8px rgba(168, 85, 247, 0.4), 0 0 24px rgba(168, 85, 247, 0.15)",
        "neon-pink":   "0 0 8px rgba(236, 72, 153, 0.4), 0 0 24px rgba(236, 72, 153, 0.15)",
        "panel":       "0 4px 32px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(34, 211, 238, 0.1)",
      },
      backdropBlur: { xs: "2px" },
    },
  },
  plugins: [],
};
