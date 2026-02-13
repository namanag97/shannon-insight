"""Starlette ASGI application for the live dashboard."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route, WebSocketRoute
from starlette.websockets import WebSocket, WebSocketDisconnect

from .state import ServerState

logger = logging.getLogger(__name__)


def create_app(state: ServerState) -> Starlette:
    """Build the Starlette application wired to *state*."""

    async def homepage(request: Request) -> HTMLResponse:
        return HTMLResponse(_DASHBOARD_HTML)

    async def api_state(request: Request) -> JSONResponse:
        data = state.get_state()
        if data is None:
            return JSONResponse({"status": "analyzing"}, status_code=202)
        return JSONResponse(data)

    async def websocket_endpoint(websocket: WebSocket) -> None:
        await websocket.accept()
        queue: asyncio.Queue[Any] = asyncio.Queue(maxsize=8)
        state.add_listener(queue)
        ping_task = asyncio.create_task(_ping_loop(websocket))
        try:
            # Send current state immediately if available
            current = state.get_state()
            if current is not None:
                await websocket.send_json({"type": "complete", "state": current})

            while True:
                msg = await asyncio.wait_for(queue.get(), timeout=60)
                if isinstance(msg, dict) and "type" in msg:
                    # Progress message
                    await websocket.send_json(msg)
                else:
                    # Full state update
                    await websocket.send_json({"type": "complete", "state": msg})
        except (WebSocketDisconnect, asyncio.CancelledError):
            pass
        except asyncio.TimeoutError:
            # Send ping on timeout, keep connection alive
            try:
                await websocket.send_json({"type": "ping"})
            except Exception:
                pass
        except Exception as exc:
            logger.debug(f"WebSocket error: {exc}")
        finally:
            ping_task.cancel()
            state.remove_listener(queue)
            try:
                await websocket.close()
            except Exception:
                pass

    async def _ping_loop(websocket: WebSocket) -> None:
        """Send keepalive pings every 30 seconds."""
        try:
            while True:
                await asyncio.sleep(30)
                await websocket.send_json({"type": "ping"})
        except (asyncio.CancelledError, Exception):
            pass

    routes = [
        Route("/", homepage),
        Route("/api/state", api_state),
        WebSocketRoute("/ws", websocket_endpoint),
    ]

    return Starlette(routes=routes)


# ══════════════════════════════════════════════════════════════════════════════
# Embedded Dashboard HTML
# ══════════════════════════════════════════════════════════════════════════════

_DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Shannon Insight</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
/* ── Reset & Variables ─────────────────────────────── */
:root {
  --bg: #0a0a0a;
  --surface: #141414;
  --border: #1e1e1e;
  --border-subtle: #181818;
  --text: #d4d4d4;
  --text-secondary: #737373;
  --text-tertiary: #525252;
  --green: #22c55e;
  --yellow: #eab308;
  --orange: #f97316;
  --red: #ef4444;
  --accent: #3b82f6;
  --mono: 'JetBrains Mono', 'Fira Code', 'SF Mono', monospace;
  --sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
html { font-size: 13px; }
body {
  font-family: var(--sans);
  background: var(--bg);
  color: var(--text);
  line-height: 1.45;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
::selection { background: rgba(59,130,246,0.25); }

/* ── Progress Bar (YouTube-style thin top bar) ─────── */
#progressBar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  z-index: 9999;
  background: transparent;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.2s;
}
#progressBar.active { opacity: 1; }
#progressFill {
  height: 100%;
  width: 30%;
  background: var(--accent);
  animation: progress-slide 1.8s ease-in-out infinite;
}
@keyframes progress-slide {
  0% { transform: translateX(-100%); width: 30%; }
  50% { width: 60%; }
  100% { transform: translateX(400%); width: 30%; }
}

/* ── Reconnect Banner ──────────────────────────────── */
#reconnectBanner {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 28px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  color: var(--text-secondary);
  font-size: 11px;
  font-family: var(--mono);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  z-index: 9998;
  transform: translateY(-100%);
  transition: transform 0.2s;
}
#reconnectBanner.active { transform: translateY(0); }

/* ── Top Bar ───────────────────────────────────────── */
.topbar {
  display: flex;
  align-items: center;
  height: 40px;
  padding: 0 20px;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
  gap: 20px;
}
.topbar-brand {
  font-family: var(--mono);
  font-size: 12px;
  font-weight: 600;
  color: var(--text);
  letter-spacing: 0.5px;
  white-space: nowrap;
  user-select: none;
}
.topbar-brand span { color: var(--text-tertiary); font-weight: 400; }
.topbar-nav {
  display: flex;
  gap: 0;
  height: 100%;
}
.topbar-nav a {
  display: flex;
  align-items: center;
  padding: 0 14px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  border-bottom: 2px solid transparent;
  transition: color 0.1s, border-color 0.1s;
  text-decoration: none;
  height: 100%;
}
.topbar-nav a:hover { color: var(--text); text-decoration: none; }
.topbar-nav a.active {
  color: var(--text);
  border-bottom-color: var(--accent);
}
.topbar-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 11px;
  font-family: var(--mono);
  color: var(--text-tertiary);
}
.status-indicator {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-tertiary);
}
.status-indicator.connected { background: var(--green); }
.status-indicator.disconnected { background: var(--red); }
.status-indicator.analyzing {
  background: var(--yellow);
  animation: blink 1.2s infinite;
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

/* ── Main Container ────────────────────────────────── */
.main {
  max-width: 1280px;
  margin: 0 auto;
  padding: 20px 20px 40px;
}
.screen { display: none; }
.screen.active { display: block; }

/* ── Overview: Top Stats Row ───────────────────────── */
.overview-top {
  display: flex;
  align-items: baseline;
  gap: 32px;
  padding: 20px 0 16px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 20px;
}
.health-big {
  font-family: var(--mono);
  font-size: 48px;
  font-weight: 600;
  line-height: 1;
  letter-spacing: -2px;
}
.health-label {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 2px;
}
.stat-group {
  display: flex;
  gap: 24px;
}
.stat-item {
  display: flex;
  flex-direction: column;
}
.stat-value {
  font-family: var(--mono);
  font-size: 16px;
  font-weight: 500;
  color: var(--text);
  line-height: 1.2;
}
.stat-label {
  font-size: 11px;
  color: var(--text-tertiary);
  margin-top: 1px;
}

/* ── Overview: Two-Column Layout ───────────────────── */
.overview-cols {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}
@media (max-width: 860px) {
  .overview-cols { grid-template-columns: 1fr; }
  .overview-top { flex-wrap: wrap; gap: 16px; }
}
.section-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 10px;
}

/* ── Overview: Category Rows ───────────────────────── */
.cat-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-subtle);
  cursor: pointer;
  transition: background 0.1s;
}
.cat-row:hover { background: var(--surface); margin: 0 -8px; padding: 8px 8px; }
.cat-row:last-child { border-bottom: none; }
.cat-name {
  font-size: 12px;
  font-weight: 500;
  color: var(--text);
  min-width: 80px;
}
.cat-count {
  font-family: var(--mono);
  font-size: 14px;
  font-weight: 600;
  min-width: 28px;
}
.cat-bar-track {
  flex: 1;
  height: 4px;
  background: var(--border);
  overflow: hidden;
}
.cat-bar-fill {
  height: 100%;
  transition: width 0.4s;
}

/* ── Overview: Focus Point ─────────────────────────── */
.focus-path {
  font-family: var(--mono);
  font-size: 13px;
  color: var(--accent);
  margin-bottom: 4px;
}
.focus-why {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 12px;
  line-height: 1.4;
}
.focus-finding {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 5px 0;
}
.sev-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-top: 5px;
  flex-shrink: 0;
}
.sev-dot.critical { background: var(--red); }
.sev-dot.high { background: var(--orange); }
.sev-dot.medium { background: var(--yellow); }
.sev-dot.low { background: var(--accent); }
.sev-dot.info { background: var(--text-tertiary); }
.focus-finding-text {
  font-size: 12px;
  color: var(--text);
  line-height: 1.4;
}

/* ── Issues Screen ─────────────────────────────────── */
.issue-tabs {
  display: flex;
  gap: 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 16px;
}
.issue-tab {
  padding: 8px 16px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-family: var(--sans);
  transition: color 0.1s;
}
.issue-tab:hover { color: var(--text); }
.issue-tab.active {
  color: var(--text);
  border-bottom-color: var(--accent);
}
.issue-tab-count {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--text-tertiary);
  margin-left: 6px;
}
.issue-tab.active .issue-tab-count { color: var(--text-secondary); }

/* ── Issue Finding Row ─────────────────────────────── */
.finding-row {
  padding: 12px 0;
  border-bottom: 1px solid var(--border-subtle);
}
.finding-row:last-child { border-bottom: none; }
.finding-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}
.finding-type-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text);
}
.finding-files {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--accent);
  margin-bottom: 4px;
  line-height: 1.5;
}
.finding-files a { color: var(--accent); }
.finding-files a:hover { text-decoration: underline; }
.finding-evidence {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--text-secondary);
  margin-bottom: 3px;
}
.finding-evidence strong {
  color: var(--text);
  font-weight: 500;
}
.finding-evidence .pctl {
  color: var(--text-tertiary);
}
.finding-interp {
  font-size: 11px;
  color: var(--text-tertiary);
  line-height: 1.4;
}

/* ── Files Screen: Table ───────────────────────────── */
.file-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}
.file-table th {
  text-align: left;
  padding: 6px 10px;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}
.file-table th:hover { color: var(--text-secondary); }
.file-table th.num { text-align: right; }
.file-table th .sort-arrow {
  font-size: 10px;
  margin-left: 3px;
  color: var(--accent);
}
.file-table td {
  padding: 5px 10px;
  border-bottom: 1px solid var(--border-subtle);
  vertical-align: middle;
}
.file-table tr { cursor: pointer; transition: background 0.08s; }
.file-table tbody tr:hover { background: var(--surface); }
.file-table .td-path {
  font-family: var(--mono);
  font-size: 11px;
  max-width: 500px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  direction: rtl;
  text-align: left;
}
.file-table .td-path span { direction: ltr; unicode-bidi: bidi-override; }
.file-table .td-num {
  font-family: var(--mono);
  font-size: 11px;
  text-align: right;
  white-space: nowrap;
}
.file-table .td-risk {
  font-family: var(--mono);
  font-size: 11px;
  text-align: right;
  white-space: nowrap;
  padding: 3px 10px;
}
.file-table .td-issues {
  font-family: var(--mono);
  font-size: 11px;
  text-align: right;
}
.file-count-note {
  font-size: 11px;
  color: var(--text-tertiary);
  padding: 8px 10px;
  font-family: var(--mono);
}

/* ── File Detail View ──────────────────────────────── */
.file-detail-back {
  font-size: 12px;
  color: var(--text-secondary);
  display: inline-block;
  margin-bottom: 12px;
}
.file-detail-back:hover { color: var(--accent); text-decoration: none; }
.file-detail-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.file-detail-path {
  font-family: var(--mono);
  font-size: 15px;
  font-weight: 500;
  color: var(--text);
}
.file-detail-role {
  font-size: 11px;
  font-family: var(--mono);
  color: var(--text-secondary);
  border: 1px solid var(--border);
  padding: 1px 6px;
}
.file-detail-health {
  font-family: var(--mono);
  font-size: 20px;
  font-weight: 600;
}
.file-detail-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1px;
  background: var(--border);
  border: 1px solid var(--border);
  margin-bottom: 20px;
}
@media (max-width: 640px) {
  .file-detail-metrics { grid-template-columns: repeat(2, 1fr); }
}
.fdm-cell {
  background: var(--surface);
  padding: 10px 12px;
}
.fdm-value {
  font-family: var(--mono);
  font-size: 16px;
  font-weight: 500;
  color: var(--text);
}
.fdm-label {
  font-size: 11px;
  color: var(--text-tertiary);
  margin-top: 2px;
}
.file-detail-section {
  margin-bottom: 20px;
}
.file-detail-section-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 8px;
}
.signals-collapsible {
  cursor: pointer;
  user-select: none;
}
.signals-collapsible::after {
  content: ' +';
  color: var(--text-tertiary);
}
.signals-collapsible.open::after {
  content: ' -';
}
.signals-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  font-size: 11px;
}
@media (max-width: 640px) {
  .signals-grid { grid-template-columns: 1fr; }
}
.sig-row {
  display: flex;
  justify-content: space-between;
  padding: 3px 8px;
  border-bottom: 1px solid var(--border-subtle);
}
.sig-row:nth-child(odd) { background: rgba(20,20,20,0.5); }
.sig-name { color: var(--text-secondary); }
.sig-val {
  font-family: var(--mono);
  color: var(--text);
}

/* ── Health Screen ─────────────────────────────────── */
.concern-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-subtle);
}
.concern-row:last-child { border-bottom: none; }
.concern-name {
  font-size: 12px;
  font-weight: 500;
  color: var(--text);
  min-width: 110px;
}
.concern-track {
  flex: 1;
  height: 4px;
  background: var(--border);
  overflow: hidden;
}
.concern-fill {
  height: 100%;
  transition: width 0.5s;
}
.concern-score {
  font-family: var(--mono);
  font-size: 12px;
  font-weight: 600;
  min-width: 32px;
  text-align: right;
}
.health-section {
  margin-bottom: 24px;
}
.global-signals-table {
  width: 100%;
  border-collapse: collapse;
}
.global-signals-table td {
  padding: 4px 10px;
  font-size: 11px;
  border-bottom: 1px solid var(--border-subtle);
}
.global-signals-table tr:nth-child(odd) { background: rgba(20,20,20,0.5); }
.global-signals-table .gs-name { color: var(--text-secondary); }
.global-signals-table .gs-val {
  font-family: var(--mono);
  text-align: right;
  color: var(--text);
}

/* ── Empty State ───────────────────────────────────── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-tertiary);
  font-size: 13px;
}
.empty-state-title {
  font-family: var(--mono);
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}
.analyzing-dots::after {
  content: '';
  animation: dots 1.5s steps(4, end) infinite;
}
@keyframes dots {
  0% { content: ''; }
  25% { content: '.'; }
  50% { content: '..'; }
  75% { content: '...'; }
}
</style>
</head>
<body>

<!-- Progress bar: thin line at very top -->
<div id="progressBar"><div id="progressFill"></div></div>

<!-- Reconnect banner -->
<div id="reconnectBanner">
  <span style="width:6px;height:6px;border-radius:50%;background:var(--yellow)"></span>
  Reconnecting<span class="analyzing-dots"></span>
</div>

<!-- Top bar -->
<div class="topbar">
  <div class="topbar-brand">SHANNON<span> INSIGHT</span></div>
  <nav class="topbar-nav" id="nav">
    <a href="#overview" data-screen="overview" class="active">Overview</a>
    <a href="#issues" data-screen="issues">Issues</a>
    <a href="#files" data-screen="files">Files</a>
    <a href="#health" data-screen="health">Health</a>
  </nav>
  <div class="topbar-right">
    <div class="status-indicator" id="statusDot"></div>
    <span id="statusText"></span>
    <span id="metaInfo"></span>
  </div>
</div>

<div class="main">

  <!-- ── OVERVIEW ────────────────────────────────── -->
  <div class="screen active" id="screen-overview">
    <div class="overview-top">
      <div>
        <div class="health-big" id="healthScore">--</div>
        <div class="health-label" id="healthLabel">Analyzing<span class="analyzing-dots"></span></div>
      </div>
      <div class="stat-group" id="overviewStats">
        <div class="stat-item">
          <div class="stat-value" id="statFiles">--</div>
          <div class="stat-label">files</div>
        </div>
        <div class="stat-item">
          <div class="stat-value" id="statModules">--</div>
          <div class="stat-label">modules</div>
        </div>
        <div class="stat-item">
          <div class="stat-value" id="statCommits">--</div>
          <div class="stat-label">commits</div>
        </div>
        <div class="stat-item">
          <div class="stat-value" id="statIssues">--</div>
          <div class="stat-label">issues</div>
        </div>
      </div>
    </div>

    <div class="overview-cols">
      <div>
        <div class="section-title">Issue Summary</div>
        <div id="categorySummary"></div>
      </div>
      <div>
        <div class="section-title">Focus Point</div>
        <div id="focusPoint"></div>
      </div>
    </div>
  </div>

  <!-- ── ISSUES ──────────────────────────────────── -->
  <div class="screen" id="screen-issues">
    <div class="issue-tabs" id="issueTabs"></div>
    <div id="issueContent"></div>
  </div>

  <!-- ── FILES ───────────────────────────────────── -->
  <div class="screen" id="screen-files">
    <div id="fileListView"></div>
    <div id="fileDetailView" style="display:none"></div>
  </div>

  <!-- ── HEALTH ──────────────────────────────────── -->
  <div class="screen" id="screen-health">
    <div class="health-section">
      <div class="section-title">Health Dimensions</div>
      <div id="concernBars"></div>
    </div>
    <div class="health-section">
      <div class="section-title">Global Signals</div>
      <table class="global-signals-table" id="globalSignalsTable"><tbody></tbody></table>
    </div>
  </div>

</div>

<script>
(function() {
  "use strict";

  // ── State ───────────────────────────────────────
  var DATA = null;
  var currentScreen = "overview";
  var currentFileDetail = null;
  var issueTab = "incomplete";
  var fileSortKey = "risk_score";
  var fileSortAsc = false;

  // ── DOM helpers ─────────────────────────────────
  function $(sel) { return document.querySelector(sel); }
  function $$(sel) { return document.querySelectorAll(sel); }

  function esc(s) {
    if (!s) return "";
    var d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  }

  function fmtN(n) {
    if (n == null) return "--";
    if (n >= 1000) return (n / 1000).toFixed(1) + "k";
    return String(n);
  }

  function fmtF(n, d) {
    if (n == null) return "--";
    return n.toFixed(d != null ? d : 2);
  }

  // ── Color logic (score 0-10) ────────────────────
  function hColor(score) {
    if (score >= 8) return "var(--green)";
    if (score >= 6) return "var(--yellow)";
    if (score >= 4) return "var(--orange)";
    return "var(--red)";
  }

  function sevKey(sev) {
    if (sev >= 0.9) return "critical";
    if (sev >= 0.8) return "high";
    if (sev >= 0.6) return "medium";
    if (sev >= 0.4) return "low";
    return "info";
  }

  // ── Routing ─────────────────────────────────────
  function navigate(screen, detail) {
    currentScreen = screen;
    $$(".screen").forEach(function(s) { s.classList.remove("active"); });
    var el = $("#screen-" + screen);
    if (el) el.classList.add("active");
    $$(".topbar-nav a").forEach(function(a) {
      a.classList.toggle("active", a.dataset.screen === screen);
    });
    if (screen === "files" && detail) {
      currentFileDetail = detail;
      showFileDetail(detail);
    } else if (screen === "files") {
      currentFileDetail = null;
      showFileList();
    }
    if (screen === "issues") renderIssues();
    if (screen === "health") renderHealth();
  }

  $("#nav").addEventListener("click", function(e) {
    var a = e.target.closest("a[data-screen]");
    if (!a) return;
    e.preventDefault();
    var screen = a.dataset.screen;
    location.hash = screen;
  });

  window.addEventListener("hashchange", function() {
    var h = location.hash.slice(1) || "overview";
    var slashIdx = h.indexOf("/");
    if (slashIdx > -1) {
      navigate(h.slice(0, slashIdx), decodeURIComponent(h.slice(slashIdx + 1)));
    } else {
      navigate(h);
    }
  });

  // ── Render Overview ─────────────────────────────
  function renderOverview() {
    if (!DATA) return;

    // Health score
    var score = DATA.health;
    var color = hColor(score);
    var el = $("#healthScore");
    el.textContent = score.toFixed(1);
    el.style.color = color;
    var lbl = $("#healthLabel");
    lbl.textContent = DATA.health_label || "";
    lbl.style.color = "var(--text-secondary)";

    // Stats
    $("#statFiles").textContent = fmtN(DATA.file_count);
    $("#statModules").textContent = fmtN(DATA.module_count);
    $("#statCommits").textContent = fmtN(DATA.commits_analyzed);
    var totalIssues = 0;
    var cats = DATA.categories || {};
    for (var k in cats) totalIssues += cats[k].count;
    $("#statIssues").textContent = fmtN(totalIssues);

    // Category summary
    var catOrder = ["incomplete", "fragile", "tangled", "team"];
    var catLabels = {incomplete: "Incomplete", fragile: "Fragile", tangled: "Tangled", team: "Team"};
    var maxCount = 1;
    for (var i = 0; i < catOrder.length; i++) {
      var c = cats[catOrder[i]];
      if (c && c.count > maxCount) maxCount = c.count;
    }
    var catHtml = "";
    for (var i = 0; i < catOrder.length; i++) {
      var key = catOrder[i];
      var cat = cats[key];
      if (!cat) continue;
      var pct = maxCount > 0 ? (cat.count / maxCount) * 100 : 0;
      var barColor = cat.high_count > 0 ? "var(--orange)" : (cat.count > 0 ? "var(--yellow)" : "var(--border)");
      catHtml += '<div class="cat-row" data-cat="' + key + '">' +
        '<span class="cat-name">' + esc(catLabels[key] || key) + '</span>' +
        '<span class="cat-count" style="color:' + (cat.count > 0 ? "var(--text)" : "var(--text-tertiary)") + '">' + cat.count + '</span>' +
        '<div class="cat-bar-track"><div class="cat-bar-fill" style="width:' + pct + '%;background:' + barColor + '"></div></div>' +
        '</div>';
    }
    var catContainer = $("#categorySummary");
    catContainer.innerHTML = catHtml;
    catContainer.onclick = function(e) {
      var row = e.target.closest(".cat-row");
      if (!row) return;
      issueTab = row.dataset.cat;
      location.hash = "issues";
    };

    // Focus point
    var fp = $("#focusPoint");
    if (DATA.focus) {
      var f = DATA.focus;
      var html = '<div class="focus-path"><a href="#files/' + encodeURIComponent(f.path) + '">' + esc(f.path) + '</a></div>';
      html += '<div class="focus-why">' + esc(f.why) + '</div>';
      var findings = f.findings || [];
      for (var j = 0; j < Math.min(findings.length, 3); j++) {
        var fi = findings[j];
        var sk = sevKey(fi.severity);
        html += '<div class="focus-finding"><div class="sev-dot ' + sk + '"></div>' +
          '<div class="focus-finding-text">' + esc(fi.label) + '</div></div>';
      }
      // Alternatives
      if (f.alternatives && f.alternatives.length > 0) {
        html += '<div style="margin-top:10px;font-size:11px;color:var(--text-tertiary)">Also consider:</div>';
        for (var a = 0; a < Math.min(f.alternatives.length, 3); a++) {
          var alt = f.alternatives[a];
          html += '<div style="font-family:var(--mono);font-size:11px;padding:2px 0">' +
            '<a href="#files/' + encodeURIComponent(alt.path) + '" style="color:var(--text-secondary)">' + esc(alt.path) + '</a></div>';
        }
      }
      fp.innerHTML = html;
    } else {
      fp.innerHTML = '<div style="color:var(--text-tertiary);font-size:12px;padding:8px 0">No actionable focus point identified.</div>';
    }
  }

  // ── Render Issues ───────────────────────────────
  function renderIssues() {
    if (!DATA) return;
    var cats = DATA.categories || {};
    var order = ["incomplete", "fragile", "tangled", "team"];
    var labels = {incomplete: "Incomplete", fragile: "Fragile", tangled: "Tangled", team: "Team"};

    // If issueTab is not valid, pick the first non-empty or first
    if (!cats[issueTab]) issueTab = order[0];

    // Tabs
    var tabsHtml = "";
    for (var i = 0; i < order.length; i++) {
      var key = order[i];
      var cat = cats[key];
      if (!cat) continue;
      tabsHtml += '<button class="issue-tab' + (issueTab === key ? ' active' : '') + '" data-tab="' + key + '">' +
        esc(labels[key] || key) +
        '<span class="issue-tab-count">' + cat.count + '</span></button>';
    }
    $("#issueTabs").innerHTML = tabsHtml;

    // Content
    var cat = cats[issueTab];
    if (!cat || cat.count === 0) {
      $("#issueContent").innerHTML = '<div class="empty-state"><div class="empty-state-title">No ' + esc(labels[issueTab] || issueTab) + ' issues</div></div>';
    } else {
      var html = "";
      var findings = cat.findings || [];
      for (var j = 0; j < findings.length; j++) {
        var f = findings[j];
        var sk = sevKey(f.severity);
        html += '<div class="finding-row">';
        html += '<div class="finding-head"><div class="sev-dot ' + sk + '"></div>';
        html += '<span class="finding-type-label">' + esc(f.label) + '</span></div>';

        // Files
        if (f.files && f.files.length) {
          html += '<div class="finding-files">';
          for (var fi = 0; fi < f.files.length; fi++) {
            if (fi > 0) html += ', ';
            html += '<a href="#files/' + encodeURIComponent(f.files[fi]) + '">' + esc(f.files[fi]) + '</a>';
          }
          html += '</div>';
        }

        // Evidence
        if (f.evidence && f.evidence.length) {
          html += '<div class="finding-evidence">';
          for (var ei = 0; ei < Math.min(f.evidence.length, 4); ei++) {
            var ev = f.evidence[ei];
            var sigName = ev.signal.replace(/_/g, ' ');
            var valStr = typeof ev.value === "number" ? (Number.isInteger(ev.value) ? String(ev.value) : ev.value.toFixed(2)) : String(ev.value);
            html += sigName + ': <strong>' + esc(valStr) + '</strong>';
            if (ev.percentile) html += ' <span class="pctl">(' + Math.round(ev.percentile) + 'th pctl)</span>';
            if (ei < Math.min(f.evidence.length, 4) - 1) html += '&nbsp;&nbsp;&nbsp;';
          }
          html += '</div>';
        }

        // Interpretation
        if (f.interpretation) {
          html += '<div class="finding-interp">' + esc(f.interpretation) + '</div>';
        }
        html += '</div>';
      }
      $("#issueContent").innerHTML = html;
    }

    // Tab click
    $("#issueTabs").onclick = function(e) {
      var btn = e.target.closest(".issue-tab");
      if (!btn) return;
      issueTab = btn.dataset.tab;
      renderIssues();
    };
  }

  // ── Render Files List ───────────────────────────
  function showFileList() {
    var listView = $("#fileListView");
    var detailView = $("#fileDetailView");
    listView.style.display = "block";
    detailView.style.display = "none";
    if (!DATA || !DATA.files) {
      listView.innerHTML = '<div class="empty-state"><div class="empty-state-title">No file data</div></div>';
      return;
    }

    var entries = [];
    for (var p in DATA.files) {
      entries.push([p, DATA.files[p]]);
    }

    // Sort
    entries.sort(function(a, b) {
      if (fileSortKey === "path") {
        return fileSortAsc ? a[0].localeCompare(b[0]) : b[0].localeCompare(a[0]);
      }
      var va = a[1][fileSortKey] != null ? a[1][fileSortKey] : 0;
      var vb = b[1][fileSortKey] != null ? b[1][fileSortKey] : 0;
      return fileSortAsc ? va - vb : vb - va;
    });

    var cols = [
      {key: "path", label: "File", cls: "td-path"},
      {key: "risk_score", label: "Risk", cls: "td-risk"},
      {key: "total_changes", label: "Churn", cls: "td-num"},
      {key: "cognitive_load", label: "Complexity", cls: "td-num"},
      {key: "blast_radius", label: "Blast R.", cls: "td-num"},
      {key: "finding_count", label: "Issues", cls: "td-issues"},
    ];

    var html = '<table class="file-table"><thead><tr>';
    for (var c = 0; c < cols.length; c++) {
      var col = cols[c];
      var arrow = fileSortKey === col.key ? (fileSortAsc ? '<span class="sort-arrow">&#9650;</span>' : '<span class="sort-arrow">&#9660;</span>') : '';
      var thCls = col.key !== "path" ? ' class="num"' : '';
      html += '<th' + thCls + ' data-sort="' + col.key + '">' + col.label + arrow + '</th>';
    }
    html += '</tr></thead><tbody>';

    var limit = Math.min(entries.length, 200);
    for (var r = 0; r < limit; r++) {
      var path = entries[r][0];
      var f = entries[r][1];
      var riskColor = hColor(10 - (f.risk_score || 0) * 10);
      var riskBg = (f.risk_score || 0) > 0.05 ? riskColor.replace('var(', '').replace(')', '') : '';

      html += '<tr data-path="' + esc(path) + '">';
      html += '<td class="td-path" title="' + esc(path) + '"><span>' + esc(path) + '</span></td>';

      // Risk cell with subtle background tint
      var riskStyle = '';
      if ((f.risk_score || 0) > 0.05) {
        riskStyle = 'color:' + riskColor;
      }
      html += '<td class="td-risk" style="' + riskStyle + '">' + fmtF(f.risk_score, 3) + '</td>';
      html += '<td class="td-num">' + (f.total_changes || 0) + '</td>';
      html += '<td class="td-num">' + fmtF(f.cognitive_load, 1) + '</td>';
      html += '<td class="td-num">' + (f.blast_radius || 0) + '</td>';
      html += '<td class="td-issues">' + (f.finding_count || 0) + '</td>';
      html += '</tr>';
    }
    html += '</tbody></table>';

    if (entries.length > 200) {
      html += '<div class="file-count-note">Showing 200 of ' + entries.length + ' files</div>';
    }

    listView.innerHTML = html;

    // Sort click on headers
    var thead = listView.querySelector("thead");
    if (thead) {
      thead.onclick = function(e) {
        var th = e.target.closest("th[data-sort]");
        if (!th) return;
        var key = th.dataset.sort;
        if (fileSortKey === key) {
          fileSortAsc = !fileSortAsc;
        } else {
          fileSortKey = key;
          fileSortAsc = key === "path";
        }
        showFileList();
      };
    }

    // Row click -> detail
    var rows = listView.querySelectorAll("tbody tr[data-path]");
    rows.forEach(function(row) {
      row.onclick = function() {
        location.hash = "files/" + encodeURIComponent(row.dataset.path);
      };
    });
  }

  // ── Render File Detail ──────────────────────────
  function showFileDetail(path) {
    var listView = $("#fileListView");
    var detailView = $("#fileDetailView");
    listView.style.display = "none";
    detailView.style.display = "block";

    if (!DATA || !DATA.files || !DATA.files[path]) {
      detailView.innerHTML = '<a class="file-detail-back" href="#files">&larr; Files</a>' +
        '<div class="empty-state"><div class="empty-state-title">File not found</div><div>' + esc(path) + '</div></div>';
      return;
    }

    var f = DATA.files[path];
    var color = hColor(f.health);

    var html = '<a class="file-detail-back" href="#files">&larr; Files</a>';

    // Header
    html += '<div class="file-detail-header">';
    html += '<span class="file-detail-path">' + esc(path) + '</span>';
    if (f.role && f.role !== "UNKNOWN") {
      html += '<span class="file-detail-role">' + esc(f.role) + '</span>';
    }
    html += '<span class="file-detail-health" style="color:' + color + '">' + fmtF(f.health, 1) + '</span>';
    html += '</div>';

    // Metric grid
    var metrics = [
      ["Lines", f.lines],
      ["Functions", f.signals ? f.signals.function_count : null],
      ["Risk Score", fmtF(f.risk_score, 3)],
      ["PageRank", fmtF(f.pagerank, 4)],
      ["Churn", f.total_changes],
      ["Bus Factor", fmtF(f.bus_factor, 1)],
      ["Blast Radius", f.blast_radius],
      ["Cognitive Load", fmtF(f.cognitive_load, 1)],
    ];
    html += '<div class="file-detail-metrics">';
    for (var m = 0; m < metrics.length; m++) {
      html += '<div class="fdm-cell"><div class="fdm-value">' + (metrics[m][1] != null ? metrics[m][1] : "--") + '</div>' +
        '<div class="fdm-label">' + metrics[m][0] + '</div></div>';
    }
    html += '</div>';

    // Findings on this file
    var fileFindings = [];
    var cats = DATA.categories || {};
    for (var ck in cats) {
      var catFindings = cats[ck].findings || [];
      for (var fi = 0; fi < catFindings.length; fi++) {
        if (catFindings[fi].files && catFindings[fi].files.indexOf(path) !== -1) {
          fileFindings.push(catFindings[fi]);
        }
      }
    }
    if (fileFindings.length > 0) {
      html += '<div class="file-detail-section"><div class="file-detail-section-title">Issues (' + fileFindings.length + ')</div>';
      for (var j = 0; j < fileFindings.length; j++) {
        var ff = fileFindings[j];
        var sk = sevKey(ff.severity);
        html += '<div class="finding-row"><div class="finding-head"><div class="sev-dot ' + sk + '"></div>' +
          '<span class="finding-type-label">' + esc(ff.label) + '</span></div>';
        if (ff.evidence && ff.evidence.length) {
          html += '<div class="finding-evidence">';
          for (var ei = 0; ei < Math.min(ff.evidence.length, 3); ei++) {
            var ev = ff.evidence[ei];
            var sigName = ev.signal.replace(/_/g, ' ');
            var valStr = typeof ev.value === "number" ? (Number.isInteger(ev.value) ? String(ev.value) : ev.value.toFixed(2)) : String(ev.value);
            html += sigName + ': <strong>' + esc(valStr) + '</strong>';
            if (ev.percentile) html += ' <span class="pctl">(' + Math.round(ev.percentile) + 'th pctl)</span>';
            if (ei < Math.min(ff.evidence.length, 3) - 1) html += '&nbsp;&nbsp;&nbsp;';
          }
          html += '</div>';
        }
        if (ff.interpretation) {
          html += '<div class="finding-interp">' + esc(ff.interpretation) + '</div>';
        }
        html += '</div>';
      }
      html += '</div>';
    }

    // All signals (collapsible)
    var sigs = f.signals || {};
    var sigKeys = Object.keys(sigs).sort();
    if (sigKeys.length > 0) {
      html += '<div class="file-detail-section">';
      html += '<div class="file-detail-section-title signals-collapsible" id="toggleSignals">All Signals (' + sigKeys.length + ')</div>';
      html += '<div class="signals-grid" id="signalsGrid" style="display:none">';
      for (var s = 0; s < sigKeys.length; s++) {
        var sk2 = sigKeys[s];
        var sv = sigs[sk2];
        if (sv == null) continue;
        var display = typeof sv === "number" ? (Number.isInteger(sv) ? String(sv) : sv.toFixed(4)) : String(sv);
        html += '<div class="sig-row"><span class="sig-name">' + esc(sk2.replace(/_/g, ' ')) + '</span>' +
          '<span class="sig-val">' + esc(display) + '</span></div>';
      }
      html += '</div></div>';
    }

    detailView.innerHTML = html;

    // Toggle signals
    var toggleBtn = document.getElementById("toggleSignals");
    var grid = document.getElementById("signalsGrid");
    if (toggleBtn && grid) {
      toggleBtn.onclick = function() {
        var open = grid.style.display !== "none";
        grid.style.display = open ? "none" : "grid";
        toggleBtn.classList.toggle("open", !open);
      };
    }
  }

  // ── Render Health ───────────────────────────────
  function renderHealth() {
    if (!DATA) return;

    // Concern bars
    var concerns = DATA.concerns || [];
    var barsHtml = "";
    for (var i = 0; i < concerns.length; i++) {
      var c = concerns[i];
      var pct = (c.score / 10) * 100;
      var color = hColor(c.score);
      barsHtml += '<div class="concern-row">' +
        '<span class="concern-name">' + esc(c.name) + '</span>' +
        '<div class="concern-track"><div class="concern-fill" style="width:' + pct + '%;background:' + color + '"></div></div>' +
        '<span class="concern-score" style="color:' + color + '">' + c.score.toFixed(1) + '</span></div>';
    }
    $("#concernBars").innerHTML = barsHtml;

    // Global signals table
    var gs = DATA.global_signals || {};
    var keys = Object.keys(gs).sort();
    var tbody = $("#globalSignalsTable tbody");
    var rows = "";
    for (var k = 0; k < keys.length; k++) {
      var key = keys[k];
      var v = gs[key];
      if (v == null) continue;
      var display = typeof v === "number" ? (Number.isInteger(v) ? String(v) : v.toFixed(4)) : String(v);
      rows += '<tr><td class="gs-name">' + esc(key.replace(/_/g, ' ')) + '</td>' +
        '<td class="gs-val">' + esc(display) + '</td></tr>';
    }
    tbody.innerHTML = rows;
  }

  // ── Master Render ───────────────────────────────
  function render() {
    renderOverview();
    if (currentScreen === "issues") renderIssues();
    if (currentScreen === "health") renderHealth();
    if (currentScreen === "files") {
      if (currentFileDetail) showFileDetail(currentFileDetail);
      else showFileList();
    }

    // Meta info
    if (DATA) {
      var parts = [];
      if (DATA.commit_sha) parts.push(DATA.commit_sha.slice(0, 7));
      if (DATA.timestamp) {
        try { parts.push(new Date(DATA.timestamp).toLocaleTimeString()); } catch(e) {}
      }
      $("#metaInfo").textContent = parts.join(" \u00b7 ");
    }
  }

  // ── WebSocket ───────────────────────────────────
  var ws = null;
  var retryDelay = 1000;

  function connect() {
    var proto = location.protocol === "https:" ? "wss:" : "ws:";
    ws = new WebSocket(proto + "//" + location.host + "/ws");

    ws.onopen = function() {
      retryDelay = 1000;
      $("#reconnectBanner").classList.remove("active");
      setStatus("connected", "");
    };

    ws.onmessage = function(e) {
      try {
        var msg = JSON.parse(e.data);
        if (msg.type === "complete") {
          DATA = msg.state;
          setStatus("connected", "");
          hideProgress();
          render();
        } else if (msg.type === "progress") {
          setStatus("analyzing", msg.message || "analyzing");
          showProgress(msg.message || "");
        } else if (msg.type === "error") {
          setStatus("disconnected", "error");
          hideProgress();
        }
      } catch(err) {
        console.error("ws parse:", err);
      }
    };

    ws.onclose = function() {
      setStatus("disconnected", "");
      $("#reconnectBanner").classList.add("active");
      setTimeout(function() {
        retryDelay = Math.min(retryDelay * 1.5, 15000);
        connect();
      }, retryDelay);
    };

    ws.onerror = function() {
      setStatus("disconnected", "");
    };
  }

  function setStatus(cls, text) {
    var dot = $("#statusDot");
    dot.className = "status-indicator " + cls;
    $("#statusText").textContent = text;
  }

  function showProgress(text) {
    $("#progressBar").classList.add("active");
  }

  function hideProgress() {
    $("#progressBar").classList.remove("active");
  }

  // ── Init ────────────────────────────────────────
  fetch("/api/state").then(function(r) { return r.json(); }).then(function(data) {
    if (data && data.health != null) {
      DATA = data;
      render();
    }
  }).catch(function() {});

  connect();

  // Handle initial hash
  var initHash = location.hash.slice(1) || "overview";
  var slashIdx = initHash.indexOf("/");
  if (slashIdx > -1) {
    navigate(initHash.slice(0, slashIdx), decodeURIComponent(initHash.slice(slashIdx + 1)));
  } else {
    navigate(initHash);
  }
})();
</script>
</body>
</html>"""
