import type { Config } from "tailwindcss";

const config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        pharma: {
          ink: "#1f2937",
          muted: "#6b7280",
          line: "#d9e4df",
          panel: "#ffffff",
          wash: "#f4faf7",
          teal: "#0f766e",
          emerald: "#059669",
          mint: "#dff7ed",
          amber: "#b45309"
        }
      },
      boxShadow: {
        panel: "0 18px 45px rgba(15, 118, 110, 0.08)"
      }
    }
  },
  plugins: []
} satisfies Config;

export default config;
