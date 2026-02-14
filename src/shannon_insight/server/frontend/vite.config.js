import { defineConfig } from "vite";
import preact from "@preact/preset-vite";
import { resolve } from "path";

export default defineConfig({
  plugins: [preact()],
  build: {
    outDir: resolve(__dirname, "../static"),
    emptyOutDir: false,
    rollupOptions: {
      input: resolve(__dirname, "src/index.jsx"),
      output: {
        entryFileNames: "app.js",
        assetFileNames: "style.css",
      },
    },
  },
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8765",
      "/ws": { target: "ws://127.0.0.1:8765", ws: true },
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: [],
  },
});
