import type { Config } from "tailwindcss";

export default {
  darkMode: "class",
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0A0A0A",
        surface: {
          DEFAULT: "#141414",
          dim: "#101010",
          container: "#1A1A1A",
          high: "#222222",
          highest: "#2A2A2A",
        },
        border: {
          DEFAULT: "#262626",
          subtle: "#1F1F1F",
          strong: "#3D3D3D",
        },
        accent: {
          blue: "#3291FF",
          primary: "#A7C8FF",
          container: "#004788",
        },
        text: {
          primary: "#EBEBEB",
          secondary: "#A1A1AA",
          muted: "#8F8F8F",
          dim: "#52525B",
        },
        severity: {
          critical: "#FF453A",
          warning: "#FF9F0A",
          info: "#3291FF",
          success: "#34D399",
        },
      },
      fontFamily: {
        sans: ["var(--font-geist-sans)", "Inter", "system-ui", "sans-serif"],
        mono: ["var(--font-geist-mono)", "JetBrains Mono", "monospace"],
      },
      borderRadius: {
        sm: "4px",
        md: "8px",
        lg: "12px",
        xl: "16px",
      },
      animation: {
        "pulse-subtle": "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "spin-slow": "spin 3s linear infinite",
      },
    },
  },
  plugins: [],
} satisfies Config;
