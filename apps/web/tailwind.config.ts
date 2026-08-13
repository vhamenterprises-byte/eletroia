import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        panel: "#111827",
        status: {
          verde: "#16a34a",
          amarelo: "#ca8a04",
          vermelho: "#dc2626",
          azul: "#2563eb",
        },
      },
    },
  },
  plugins: [],
};
export default config;
