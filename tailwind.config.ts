import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/**/*.{ts,tsx,js,jsx,mdx}",
    "./app/**/*.{ts,tsx,js,jsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        main: ["Plus Jakarta Sans", "DM Sans", "-apple-system", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
        arabic: ["Amiri", "Noto Naskh Arabic", "serif"],
      },
      colors: {
        dash: {
          bg: "#F4F5F7",
          card: "#FFFFFF",
          ink: "#1A1D23",
          "ink-soft": "#4A4E57",
          "ink-muted": "#8B8F96",
          "ink-ghost": "#B8BBC2",
          border: "#E8EAED",
          lavender: "#8B7EC8",
          saffron: "#D4943A",
          opal: "#3D9E7C",
          cyan: "#3B8FD4",
          rose: "#C45E6A",
          gold: "#B8941F",
        },
      },
      borderRadius: {
        dash: "16px",
        "dash-sm": "10px",
      },
    },
  },
  plugins: [],
};

export default config;
