// tailwind.config.js
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        schoolblue: '#1E3A8A', // Custom blue
        schoolgold: '#FFD700', // Custom gold
      },
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        geometrytheme: {
          primary: "#1E3A8A",   // school blue
          secondary: "#FFD700", // school gold
          accent: "#93C5FD",
          neutral: "#1F2937",   // darker neutral
          "base-100": "#111827", // dark gray for app background
          info: "#93C5FD",
          success: "#34D399",
          warning: "#FBBF24",
          error: "#F87171",
        },
      },
      "dark",
    ],
  },
};
