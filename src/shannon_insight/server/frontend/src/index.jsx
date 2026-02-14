/**
 * Application entry point. Mounts the root App component.
 */

import { render } from "preact";
import { App } from "./components/core/App.jsx";

console.log("[shannon-insight] Mounting app to #app");
const root = document.getElementById("app");
if (!root) {
  console.error("[shannon-insight] Mount point #app not found!");
} else {
  render(<App />, root);
  console.log("[shannon-insight] App mounted successfully");
}
