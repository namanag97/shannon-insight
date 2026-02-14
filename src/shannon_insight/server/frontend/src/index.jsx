/**
 * Application entry point. Mounts the root App component.
 */

import { render } from "preact";
import { App } from "./components/core/App.jsx";

// Global error handlers
window.addEventListener("error", (e) => {
  console.error("[shannon-insight] Global error:", e.error || e.message);
});

window.addEventListener("unhandledrejection", (e) => {
  console.error("[shannon-insight] Unhandled promise rejection:", e.reason);
});

// Mount the app
const root = document.getElementById("app");
if (root) {
  render(<App />, root);
} else {
  console.error("[shannon-insight] Mount point #app not found");
}
