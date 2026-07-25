/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        atelier: {
          bg: "#171417",
          panel: "#221E22",
          card: "#2B262B",
          line: "#423B42"
        },
        ink: "#F2EDE9",
        clay: "#C97B63",
        sage: "#8FA88C",
        gold: "#D4A857"
      },
      fontFamily: {
        display: ["Newsreader", "serif"],
        body: ["Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"]
      }
    },
  },
  plugins: [],
}

