import type { Config } from "tailwindcss";

const config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        pharma: {
          ink: "#0f172a",
          muted: "#475569",
          line: "#d9e4df",
          panel: "#ffffff",
          wash: "#f6fbfa",
          bg: "#f6fbfa",
          teal: "#0f766e",
          emerald: "#10b981",
          mint: "#d1fae5",
          amber: "#f59e0b",
          slate: "#0f172a",
          red: "#ef4444"
        }
      },
      boxShadow: {
        panel: "0 18px 45px rgba(15, 118, 110, 0.08)",
        command: "0 24px 80px rgba(15, 23, 42, 0.12)",
        glow: "0 0 0 1px rgba(16, 185, 129, 0.16), 0 22px 70px rgba(15, 118, 110, 0.18)"
      }
    }
  },
  plugins: []
} satisfies Config;

export default config;
