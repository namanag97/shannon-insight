/**
 * Application entry point. Mounts the root App component.
 */

import { render } from "preact";
import { App } from "./components/core/App.jsx";

console.log("[shannon-insight] Starting application");
console.log("[shannon-insight] Document ready state:", document.readyState);

// Add global error handler
window.addEventListener("error", (e) => {
  console.error("[shannon-insight] Global error:", e.error || e.message);
});

window.addEventListener("unhandledrejection", (e) => {
  console.error("[shannon-insight] Unhandled promise rejection:", e.reason);
});

// Mount the app
try {
  console.log("[shannon-insight] Looking for mount point #app");
  const root = document.getElementById("app");
  if (!root) {
    console.error("[shannon-insight] Mount point #app not found!");
    console.error("[shannon-insight] document.body:", document.body);
    console.error("[shannon-insight] document.body.innerHTML:", document.body.innerHTML);
  } else {
    console.log("[shannon-insight] Mount point found, rendering...");
    render(<App />, root);
    console.log("[shannon-insight] App rendered successfully");
  }
} catch (err) {
  console.error("[shannon-insight] Fatal error during mount:", err);
  console.error("[shannon-insight] Stack:", err.stack);
}
