/**
 * Central store using Zustand. Replaces all 13 global variables
 * from the original app.js with a single immutable state tree.
 *
 * State shape:
 *   data        - Dashboard data from server (null until first load)
 *   navigation  - Current screen, detail views
 *   files       - File list sorting, filtering, view mode
 *   issues      - Issue tab, sort, severity filter
 *   modules     - Module sorting, detail
 *   ui          - Keyboard selection indices, connection status
 *
 * Persistence:
 *   UI preferences (sorts, filters, view modes) are saved to localStorage
 *   and restored on page reload.
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import { SEVERITY_LEVELS } from "../utils/constants.js";

// Helper to update hash when navigating
function updateHash(screen, detail) {
  const hash = detail ? `${screen}/${encodeURIComponent(detail)}` : screen;
  if (location.hash !== `#${hash}`) {
    history.replaceState(null, "", `#${hash}`);
  }
}

const useStore = create(
  persist(
    (set, get) => ({
  // ── Server data ─────────────────────────────────────────
  data: null,

  // ── Navigation ──────────────────────────────────────────
  currentScreen: "overview",
  currentFileDetail: null,
  moduleDetail: null,

  // ── File list state ─────────────────────────────────────
  fileSortKey: "risk_score",
  fileSortAsc: false,
  fileSearch: "",
  fileFilters: new Set(),
  fileViewMode: "table",

  // ── Issue list state ────────────────────────────────────
  issueTab: "incomplete",
  issueSortKey: "severity_desc",
  issueSeverityFilter: new Set(SEVERITY_LEVELS),

  // ── Module list state ───────────────────────────────────
  moduleSortKey: "health_score",
  moduleSortAsc: true,

  // ── Churn explorer state ────────────────────────────────
  churnTrajectoryFilter: "all",
  churnSortKey: "total_changes",
  churnSortAsc: false,

  // ── Signal inspector state ─────────────────────────────
  inspectedSignal: "risk_score",

  // ── UI state ────────────────────────────────────────────
  selectedIndex: {},
  connectionStatus: "disconnected",
  statusText: "",
  progressActive: false,
  progressPercent: null,
  progressMessage: "",
  reconnectActive: false,

  // ── Actions ─────────────────────────────────────────────

  setData: (data) => set({ data }),

  navigate: (screen, detail) => {
    const updates = { currentScreen: screen };
    if (screen === "files") {
      updates.currentFileDetail = detail || null;
    } else if (screen === "modules") {
      updates.moduleDetail = detail || null;
    }
    set(updates);
  },

  // File actions
  setFileSortKey: (key) => {
    const state = get();
    if (state.fileSortKey === key) {
      set({ fileSortAsc: !state.fileSortAsc });
    } else {
      set({ fileSortKey: key, fileSortAsc: key === "path" });
    }
  },

  setFileSearch: (query) => set({ fileSearch: query }),

  toggleFileFilter: (filter) => {
    const state = get();
    const next = new Set(state.fileFilters);
    if (next.has(filter)) next.delete(filter);
    else next.add(filter);
    set({ fileFilters: next });
  },

  setFileViewMode: (mode) => set({ fileViewMode: mode }),

  // Issue actions
  setIssueTab: (tab) => set({ issueTab: tab }),

  setIssueSortKey: (key) => set({ issueSortKey: key }),

  toggleIssueSeverity: (sev) => {
    const state = get();
    const next = new Set(state.issueSeverityFilter);
    if (next.has(sev)) next.delete(sev);
    else next.add(sev);
    set({ issueSeverityFilter: next });
  },

  // Module actions
  setModuleSortKey: (key) => {
    const state = get();
    if (state.moduleSortKey === key) {
      set({ moduleSortAsc: !state.moduleSortAsc });
    } else {
      set({ moduleSortKey: key, moduleSortAsc: key === "path" });
    }
  },

  // Churn actions
  setChurnTrajectoryFilter: (filter) => set({ churnTrajectoryFilter: filter }),
  setChurnSortKey: (key) => {
    const state = get();
    if (state.churnSortKey === key) {
      set({ churnSortAsc: !state.churnSortAsc });
    } else {
      set({ churnSortKey: key, churnSortAsc: key === "path" });
    }
  },

  // Signal inspector actions
  setInspectedSignal: (signal) => set({ inspectedSignal: signal }),

  // UI actions
  setSelectedIndex: (screen, index) => {
    const state = get();
    set({ selectedIndex: { ...state.selectedIndex, [screen]: index } });
  },

  setConnectionStatus: (status, text) =>
    set({ connectionStatus: status, statusText: text || "" }),

  setProgress: (active, percent, message) =>
    set({ progressActive: active, progressPercent: percent, progressMessage: message || "" }),

  setReconnectActive: (active) => set({ reconnectActive: active }),
}));

export default useStore;
