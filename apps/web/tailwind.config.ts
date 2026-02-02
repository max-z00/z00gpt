import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: "#0f172a",
        surfaceLight: "#f8fafc",
      },
    },
  },
  plugins: [],
};

export default config;
