/**
 * Top navigation bar with brand, screen tabs, export dropdown,
 * connection status, and metadata.
 */

import { useState, useEffect } from "preact/hooks";
import useStore from "../../state/store.js";
import { SCREENS } from "../../utils/constants.js";

const SCREEN_LABELS = {
  overview: "Overview",
  issues: "Issues",
  files: "Files",
  modules: "Modules",
  health: "Health",
};

export function Header() {
  const currentScreen = useStore((s) => s.currentScreen);
  const connectionStatus = useStore((s) => s.connectionStatus);
  const statusText = useStore((s) => s.statusText);
  const data = useStore((s) => s.data);
  const [exportOpen, setExportOpen] = useState(false);

  // Close export dropdown on outside click
  useEffect(() => {
    function handleClick(e) {
      if (!e.target.closest(".export-dropdown")) {
        setExportOpen(false);
      }
    }
    document.addEventListener("click", handleClick);
    return () => document.removeEventListener("click", handleClick);
  }, []);

  // Meta info
  const parts = [];
  if (data) {
    if (data.commit_sha) parts.push(data.commit_sha.slice(0, 7));
    if (data.timestamp) {
      try {
        parts.push(new Date(data.timestamp).toLocaleTimeString());
      } catch (e) {
        // ignore
      }
    }
  }

  return (
    <div class="topbar">
      <div class="topbar-brand">
        SHANNON<span> INSIGHT</span>
      </div>
      <nav class="topbar-nav" id="nav">
        {SCREENS.map((screen) => (
          <a
            key={screen}
            href={"#" + screen}
            data-screen={screen}
            class={currentScreen === screen ? "active" : ""}
            onClick={(e) => {
              e.preventDefault();
              location.hash = screen;
            }}
          >
            {SCREEN_LABELS[screen]}
          </a>
        ))}
      </nav>
      <div class="topbar-right">
        <div class="export-dropdown" id="exportDropdown">
          <button class="export-btn" onClick={() => setExportOpen(!exportOpen)}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            {" Export"}
          </button>
          <div class={`export-dropdown-menu${exportOpen ? " open" : ""}`}>
            <a href="/api/export/json">JSON</a>
            <a href="/api/export/csv">CSV</a>
          </div>
        </div>
        <div class={`status-indicator ${connectionStatus}`} />
        <span class="status-text">{statusText}</span>
        <span class="meta-info">{parts.join(" \u00b7 ")}</span>
      </div>
    </div>
  );
}
