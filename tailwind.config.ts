import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ["Cormorant Garamond", "Georgia", "serif"],
        body: ["Crimson Pro", "Georgia", "serif"],
        label: ["Cinzel", "Georgia", "serif"],
        sans: ["DM Sans", "Helvetica Neue", "sans-serif"],
        mono: ["JetBrains Mono", "Consolas", "monospace"],
        arabic: ["Amiri", "Traditional Arabic", "serif"],
      },
      colors: {
        ink: {
          DEFAULT: "#0C0A09",
          soft: "#2C2825",
          muted: "#6B6560",
          ghost: "#A09890",
        },
        bronze: {
          DEFAULT: "#8B6914",
          light: "#C49B30",
        },
        "green-scholar": {
          DEFAULT: "#1B6B45",
        },
        indigo: {
          DEFAULT: "#3B3F8C",
        },
        coral: {
          DEFAULT: "#8B3A2A",
        },
        surface: {
          DEFAULT: "#FAFAF8",
          warm: "#F5F2ED",
          deep: "#EDE8E0",
        },
        rule: {
          DEFAULT: "#D6D0C8",
          faint: "#E8E2DA",
        },
      },
      spacing: {
        18: "4.5rem",
        22: "5.5rem",
      },
      maxWidth: {
        article: "640px",
        content: "860px",
        layout: "1060px",
      },
      animation: {
        "fade-up": "fadeUp 0.8s cubic-bezier(0.16,1,0.3,1) both",
        "fade-in": "fadeIn 0.6s cubic-bezier(0.4,0,0.2,1) both",
      },
      keyframes: {
        fadeUp: {
          from: { opacity: "0", transform: "translateY(20px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        fadeIn: {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
