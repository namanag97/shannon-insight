/**
 * Keyboard shortcuts hook - handles global keyboard navigation.
 * Extracted from the monolithic keydown handler.
 */

import { useEffect } from "preact/hooks";
import useStore from "../state/store.js";
import { SCREENS } from "../utils/constants.js";

export function useKeyboard() {
  const navigate = useStore((s) => s.navigate);
  const currentScreen = useStore((s) => s.currentScreen);
  const currentFileDetail = useStore((s) => s.currentFileDetail);
  const moduleDetail = useStore((s) => s.moduleDetail);
  const selectedIndex = useStore((s) => s.selectedIndex);
  const setSelectedIndex = useStore((s) => s.setSelectedIndex);

  useEffect(() => {
    function handler(e) {
      const tag = (e.target.tagName || "").toLowerCase();
      if (tag === "input" || tag === "textarea" || tag === "select") {
        if (e.key === "Escape") e.target.blur();
        return;
      }

      // Keyboard shortcuts overlay
      const overlay = document.getElementById("kbdOverlay");
      if (e.key === "?") {
        if (overlay) overlay.classList.toggle("open");
        e.preventDefault();
        return;
      }
      if (overlay && overlay.classList.contains("open")) {
        if (e.key === "Escape") overlay.classList.remove("open");
        return;
      }

      // Escape: go back from detail views
      if (e.key === "Escape") {
        if (currentFileDetail) {
          location.hash = "files";
          e.preventDefault();
        } else if (moduleDetail) {
          location.hash = "modules";
          e.preventDefault();
        }
        return;
      }

      // Number keys: switch screens
      if (e.key >= "1" && e.key <= "5") {
        location.hash = SCREENS[parseInt(e.key) - 1];
        e.preventDefault();
        return;
      }

      // Slash: focus file search
      if (e.key === "/") {
        e.preventDefault();
        if (currentScreen !== "files") location.hash = "files";
        setTimeout(() => {
          const si = document.getElementById("fileSearchInput");
          if (si) si.focus();
        }, 100);
        return;
      }

      // j/k: navigate table rows
      if (e.key === "j" || e.key === "k") {
        const rows = document.querySelectorAll("#screen-" + currentScreen + " tbody tr");
        if (!rows.length) return;
        let idx = selectedIndex[currentScreen] || 0;
        if (e.key === "j") idx = Math.min(idx + 1, rows.length - 1);
        if (e.key === "k") idx = Math.max(idx - 1, 0);
        setSelectedIndex(currentScreen, idx);
        rows.forEach((r, i) => r.classList.toggle("kbd-selected", i === idx));
        rows[idx].scrollIntoView({ block: "nearest" });
        e.preventDefault();
        return;
      }

      // Enter: activate selected row
      if (e.key === "Enter") {
        const rows = document.querySelectorAll("#screen-" + currentScreen + " tbody tr.kbd-selected");
        if (rows.length) rows[0].click();
      }
    }

    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [currentScreen, currentFileDetail, moduleDetail, selectedIndex]);
}
