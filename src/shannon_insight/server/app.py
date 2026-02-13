"""Starlette ASGI application for the live dashboard."""

from __future__ import annotations

import asyncio
import csv
import io
import json
import logging
from datetime import datetime, timezone
from typing import Any

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
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

    async def api_export_json(request: Request) -> Response:
        """Download full state as JSON."""
        data = state.get_state()
        if data is None:
            return JSONResponse({"status": "analyzing"}, status_code=202)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        body = json.dumps(data, indent=2)
        return Response(
            content=body,
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="shannon-insight-{ts}.json"',
            },
        )

    async def api_export_csv(request: Request) -> Response:
        """Download file table as CSV."""
        data = state.get_state()
        if data is None:
            return JSONResponse({"status": "analyzing"}, status_code=202)
        files = data.get("files", {})
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(
            [
                "path",
                "risk_score",
                "total_changes",
                "cognitive_load",
                "blast_radius",
                "finding_count",
                "role",
                "health",
                "lines",
            ]
        )
        for path, f in files.items():
            writer.writerow(
                [
                    path,
                    f.get("risk_score", 0),
                    f.get("total_changes", 0),
                    f.get("cognitive_load", 0),
                    f.get("blast_radius", 0),
                    f.get("finding_count", 0),
                    f.get("role", "UNKNOWN"),
                    f.get("health", 0),
                    f.get("lines", 0),
                ]
            )
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        return Response(
            content=buf.getvalue(),
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="shannon-insight-files-{ts}.csv"',
            },
        )

    async def api_gate(request: Request) -> JSONResponse:
        """Quality gate endpoint for CI integration."""
        data = state.get_state()
        if data is None:
            return JSONResponse(
                {"status": "PENDING", "reason": "Analysis in progress"},
                status_code=202,
            )
        health = data.get("health", 0)
        # Count critical findings (severity >= 0.9)
        critical_count = 0
        finding_count = 0
        categories = data.get("categories", {})
        for cat in categories.values():
            for f in cat.get("findings", []):
                finding_count += 1
                if f.get("severity", 0) >= 0.9:
                    critical_count += 1

        status = "PASS"
        reasons = []
        if health < 4.0:
            status = "FAIL"
            reasons.append(f"Health {health:.1f} below threshold 4.0")
        if critical_count > 0:
            status = "FAIL"
            reasons.append(
                f"{critical_count} critical finding{'s' if critical_count != 1 else ''} detected"
            )

        reason = "; ".join(reasons) if reasons else f"Health {health:.1f}, no critical issues"
        return JSONResponse(
            {
                "status": status,
                "health": round(health, 1),
                "critical_count": critical_count,
                "finding_count": finding_count,
                "reason": reason,
            }
        )

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
        Route("/api/export/json", api_export_json),
        Route("/api/export/csv", api_export_csv),
        Route("/api/gate", api_gate),
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

#progressBar {
  position: fixed; top: 0; left: 0; right: 0; height: 2px;
  z-index: 9999; background: transparent; pointer-events: none;
  opacity: 0; transition: opacity 0.2s;
}
#progressBar.active { opacity: 1; }
#progressFill {
  height: 100%; width: 30%; background: var(--accent);
  animation: progress-slide 1.8s ease-in-out infinite;
}
.progress-text {
  position: fixed; top: 4px; right: 20px; font-family: var(--mono);
  font-size: 10px; color: var(--accent); z-index: 9999; opacity: 0;
  transition: opacity 0.2s; pointer-events: none;
}
.progress-text.active { opacity: 1; }
@keyframes progress-slide {
  0% { transform: translateX(-100%); width: 30%; }
  50% { width: 60%; }
  100% { transform: translateX(400%); width: 30%; }
}

#reconnectBanner {
  position: fixed; top: 0; left: 0; right: 0; height: 28px;
  background: var(--surface); border-bottom: 1px solid var(--border);
  color: var(--text-secondary); font-size: 11px; font-family: var(--mono);
  display: flex; align-items: center; justify-content: center; gap: 6px;
  z-index: 9998; transform: translateY(-100%); transition: transform 0.2s;
}
#reconnectBanner.active { transform: translateY(0); }

.topbar {
  display: flex; align-items: center; height: 40px; padding: 0 20px;
  border-bottom: 1px solid var(--border); background: var(--surface); gap: 20px;
}
.topbar-brand {
  font-family: var(--mono); font-size: 12px; font-weight: 600;
  color: var(--text); letter-spacing: 0.5px; white-space: nowrap; user-select: none;
}
.topbar-brand span { color: var(--text-tertiary); font-weight: 400; }
.topbar-nav { display: flex; gap: 0; height: 100%; }
.topbar-nav a {
  display: flex; align-items: center; padding: 0 14px; font-size: 12px;
  font-weight: 500; color: var(--text-secondary); border-bottom: 2px solid transparent;
  transition: color 0.1s, border-color 0.1s; text-decoration: none; height: 100%;
}
.topbar-nav a:hover { color: var(--text); text-decoration: none; }
.topbar-nav a.active { color: var(--text); border-bottom-color: var(--accent); }
.topbar-right {
  margin-left: auto; display: flex; align-items: center; gap: 10px;
  font-size: 11px; font-family: var(--mono); color: var(--text-tertiary);
}
.export-dropdown {
  position: relative; display: inline-block;
}
.export-dropdown button {
  background: none; border: 1px solid var(--border); color: var(--text-secondary);
  font-family: var(--mono); font-size: 11px; padding: 2px 8px; cursor: pointer;
  border-radius: 3px;
}
.export-dropdown button:hover { color: var(--text); border-color: var(--text-tertiary); }
.export-dropdown-menu {
  display: none; position: absolute; right: 0; top: 100%; margin-top: 4px;
  background: var(--surface); border: 1px solid var(--border); z-index: 100;
  min-width: 120px;
}
.export-dropdown-menu.open { display: block; }
.export-dropdown-menu a {
  display: block; padding: 6px 12px; font-size: 11px; color: var(--text-secondary);
  text-decoration: none; font-family: var(--mono);
}
.export-dropdown-menu a:hover { background: var(--border); color: var(--text); text-decoration: none; }
.status-indicator {
  width: 6px; height: 6px; border-radius: 50%; background: var(--text-tertiary);
}
.status-indicator.connected { background: var(--green); }
.status-indicator.disconnected { background: var(--red); }
.status-indicator.analyzing { background: var(--yellow); animation: blink 1.2s infinite; }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

.main { max-width: 1280px; margin: 0 auto; padding: 20px 20px 40px; }
.screen { display: none; }
.screen.active { display: block; }

.verdict-banner {
  font-size: 12px; font-weight: 600; font-family: var(--mono);
  margin-bottom: 4px; letter-spacing: 0.3px;
}

.overview-top {
  display: flex; align-items: baseline; gap: 32px; padding: 20px 0 16px;
  border-bottom: 1px solid var(--border); margin-bottom: 20px;
}
.health-big {
  font-family: var(--mono); font-size: 48px; font-weight: 600;
  line-height: 1; letter-spacing: -2px;
}
.health-label { font-size: 11px; color: var(--text-secondary); margin-top: 2px; }
.stat-group { display: flex; gap: 24px; }
.stat-item { display: flex; flex-direction: column; }
.stat-value {
  font-family: var(--mono); font-size: 16px; font-weight: 500;
  color: var(--text); line-height: 1.2;
}
.stat-label { font-size: 11px; color: var(--text-tertiary); margin-top: 1px; }

.overview-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
@media (max-width: 860px) {
  .overview-cols { grid-template-columns: 1fr; }
  .overview-top { flex-wrap: wrap; gap: 16px; }
}
.section-title {
  font-size: 11px; font-weight: 600; color: var(--text-tertiary);
  text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 10px;
}

.cat-row {
  display: flex; align-items: center; gap: 12px; padding: 8px 0;
  border-bottom: 1px solid var(--border-subtle); cursor: pointer; transition: background 0.1s;
}
.cat-row:hover { background: var(--surface); margin: 0 -8px; padding: 8px 8px; }
.cat-row:last-child { border-bottom: none; }
.cat-name { font-size: 12px; font-weight: 500; color: var(--text); min-width: 80px; }
.cat-count { font-family: var(--mono); font-size: 14px; font-weight: 600; min-width: 28px; }
.cat-bar-track { flex: 1; height: 4px; background: var(--border); overflow: hidden; }
.cat-bar-fill { height: 100%; transition: width 0.4s; }

.focus-path { font-family: var(--mono); font-size: 13px; color: var(--accent); margin-bottom: 4px; }
.focus-why { font-size: 12px; color: var(--text-secondary); margin-bottom: 12px; line-height: 1.4; }
.focus-finding { display: flex; align-items: flex-start; gap: 8px; padding: 5px 0; }
.sev-dot { width: 6px; height: 6px; border-radius: 50%; margin-top: 5px; flex-shrink: 0; }
.sev-dot.critical { background: var(--red); }
.sev-dot.high { background: var(--orange); }
.sev-dot.medium { background: var(--yellow); }
.sev-dot.low { background: var(--accent); }
.sev-dot.info { background: var(--text-tertiary); }
.focus-finding-text { font-size: 12px; color: var(--text); line-height: 1.4; }
.focus-score-breakdown {
  font-family: var(--mono); font-size: 11px; color: var(--text-secondary);
  margin-bottom: 8px; display: flex; gap: 12px; flex-wrap: wrap;
}
.focus-score-breakdown span { white-space: nowrap; }

.effort-badge {
  display: inline-block; font-family: var(--mono); font-size: 10px;
  border: 1px solid var(--border); padding: 0 4px; border-radius: 2px;
  color: var(--text-secondary); vertical-align: middle; margin-left: 6px;
}
.finding-suggestion {
  font-size: 11px; color: var(--text-secondary); padding-left: 14px;
  margin-top: 2px;
}
.finding-suggestion::before { content: "\2192 "; }
.changed-badge {
  display: inline-block; font-family: var(--mono); font-size: 9px;
  background: rgba(59,130,246,0.15); color: var(--accent); padding: 0 4px;
  border-radius: 2px; margin-left: 6px; vertical-align: middle;
}

.issue-tabs {
  display: flex; gap: 0; border-bottom: 1px solid var(--border); margin-bottom: 16px;
}
.issue-tab {
  padding: 8px 16px; font-size: 12px; font-weight: 500; color: var(--text-secondary);
  background: none; border: none; border-bottom: 2px solid transparent;
  cursor: pointer; font-family: var(--sans); transition: color 0.1s;
}
.issue-tab:hover { color: var(--text); }
.issue-tab.active { color: var(--text); border-bottom-color: var(--accent); }
.issue-tab-count {
  font-family: var(--mono); font-size: 11px; color: var(--text-tertiary); margin-left: 6px;
}
.issue-tab.active .issue-tab-count { color: var(--text-secondary); }

.filter-bar {
  display: flex; align-items: center; gap: 8px; margin-bottom: 12px; flex-wrap: wrap;
}
.filter-chip {
  font-family: var(--mono); font-size: 10px; padding: 2px 8px;
  border: 1px solid var(--border); background: none; color: var(--text-secondary);
  cursor: pointer; border-radius: 3px; transition: all 0.1s;
}
.filter-chip:hover { border-color: var(--text-tertiary); }
.filter-chip.active { border-color: var(--accent); color: var(--accent); }
.search-input {
  flex: 1; min-width: 200px; background: var(--surface); border: 1px solid var(--border);
  color: var(--text); font-family: var(--mono); font-size: 11px; padding: 4px 8px;
  outline: none;
}
.search-input:focus { border-color: var(--accent); }
.sev-filter {
  font-family: var(--mono); font-size: 10px; padding: 2px 6px;
  border: 1px solid var(--border); background: none; color: var(--text-secondary);
  cursor: pointer; border-radius: 2px;
}
.sev-filter.active { border-color: var(--accent); color: var(--accent); }
.sort-select {
  background: var(--surface); border: 1px solid var(--border); color: var(--text-secondary);
  font-family: var(--mono); font-size: 10px; padding: 2px 4px; outline: none;
}
.treemap-toggle {
  display: inline-flex; gap: 0; border: 1px solid var(--border); border-radius: 3px; overflow: hidden;
}
.treemap-toggle button {
  background: none; border: none; color: var(--text-secondary); font-family: var(--mono);
  font-size: 10px; padding: 2px 8px; cursor: pointer;
}
.treemap-toggle button.active { background: var(--border); color: var(--text); }

.finding-row { padding: 12px 0; border-bottom: 1px solid var(--border-subtle); }
.finding-row:last-child { border-bottom: none; }
.finding-head { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.finding-type-label { font-size: 12px; font-weight: 600; color: var(--text); }
.finding-files {
  font-family: var(--mono); font-size: 11px; color: var(--accent);
  margin-bottom: 4px; line-height: 1.5;
}
.finding-files a { color: var(--accent); }
.finding-files a:hover { text-decoration: underline; }
.finding-evidence {
  font-family: var(--mono); font-size: 11px; color: var(--text-secondary); margin-bottom: 3px;
}
.finding-evidence strong { color: var(--text); font-weight: 500; }
.finding-evidence .pctl { color: var(--text-tertiary); }
.finding-interp { font-size: 11px; color: var(--text-tertiary); line-height: 1.4; }

.file-table, .module-table {
  width: 100%; border-collapse: collapse; font-size: 12px;
}
.file-table th, .module-table th {
  text-align: left; padding: 6px 10px; font-size: 11px; font-weight: 600;
  color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.5px;
  border-bottom: 1px solid var(--border); cursor: pointer; user-select: none; white-space: nowrap;
}
.file-table th:hover, .module-table th:hover { color: var(--text-secondary); }
.file-table th.num, .module-table th.num { text-align: right; }
.file-table th .sort-arrow, .module-table th .sort-arrow {
  font-size: 10px; margin-left: 3px; color: var(--accent);
}
.file-table td, .module-table td {
  padding: 5px 10px; border-bottom: 1px solid var(--border-subtle); vertical-align: middle;
}
.file-table tr, .module-table tr { cursor: pointer; transition: background 0.08s; }
.file-table tbody tr:hover, .module-table tbody tr:hover { background: var(--surface); }
.file-table .td-path, .module-table .td-path {
  font-family: var(--mono); font-size: 11px; max-width: 500px; overflow: hidden;
  text-overflow: ellipsis; white-space: nowrap; direction: rtl; text-align: left;
}
.file-table .td-path span, .module-table .td-path span { direction: ltr; unicode-bidi: bidi-override; }
.file-table .td-num, .module-table .td-num {
  font-family: var(--mono); font-size: 11px; text-align: right; white-space: nowrap;
}
.file-table .td-risk, .module-table .td-risk {
  font-family: var(--mono); font-size: 11px; text-align: right; white-space: nowrap; padding: 3px 10px;
}
.file-table .td-issues { font-family: var(--mono); font-size: 11px; text-align: right; }
.file-count-note {
  font-size: 11px; color: var(--text-tertiary); padding: 8px 10px; font-family: var(--mono);
}
.kbd-selected td { background: rgba(59,130,246,0.08) !important; }

.file-detail-back {
  font-size: 12px; color: var(--text-secondary); display: inline-block; margin-bottom: 12px;
}
.file-detail-back:hover { color: var(--accent); text-decoration: none; }
.file-detail-header {
  display: flex; align-items: baseline; gap: 12px; margin-bottom: 16px; flex-wrap: wrap;
}
.file-detail-path { font-family: var(--mono); font-size: 15px; font-weight: 500; color: var(--text); }
.file-detail-role {
  font-size: 11px; font-family: var(--mono); color: var(--text-secondary);
  border: 1px solid var(--border); padding: 1px 6px;
}
.file-detail-health { font-family: var(--mono); font-size: 20px; font-weight: 600; }
.file-detail-metrics {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px;
  background: var(--border); border: 1px solid var(--border); margin-bottom: 20px;
}
@media (max-width: 640px) {
  .file-detail-metrics { grid-template-columns: repeat(2, 1fr); }
}
.fdm-cell { background: var(--surface); padding: 10px 12px; }
.fdm-value { font-family: var(--mono); font-size: 16px; font-weight: 500; color: var(--text); }
.fdm-label { font-size: 11px; color: var(--text-tertiary); margin-top: 2px; }
.file-detail-section { margin-bottom: 20px; }
.file-detail-section-title {
  font-size: 11px; font-weight: 600; color: var(--text-tertiary);
  text-transform: uppercase; letter-spacing: 0.8px; padding-bottom: 8px;
  border-bottom: 1px solid var(--border); margin-bottom: 8px;
}
.signals-collapsible { cursor: pointer; user-select: none; }
.signals-collapsible::after { content: ' +'; color: var(--text-tertiary); }
.signals-collapsible.open::after { content: ' -'; }
.signals-grid { display: grid; grid-template-columns: 1fr 1fr; font-size: 11px; }
@media (max-width: 640px) { .signals-grid { grid-template-columns: 1fr; } }
.sig-row {
  display: flex; justify-content: space-between; padding: 3px 8px;
  border-bottom: 1px solid var(--border-subtle);
}
.sig-row:nth-child(odd) { background: rgba(20,20,20,0.5); }
.sig-name { color: var(--text-secondary); }
.sig-val { font-family: var(--mono); color: var(--text); }

.concern-row {
  display: flex; align-items: center; gap: 12px; padding: 8px 0;
  border-bottom: 1px solid var(--border-subtle);
}
.concern-row:last-child { border-bottom: none; }
.concern-name { font-size: 12px; font-weight: 500; color: var(--text); min-width: 110px; }
.concern-track { flex: 1; height: 4px; background: var(--border); overflow: hidden; }
.concern-fill { height: 100%; transition: width 0.5s; }
.concern-score {
  font-family: var(--mono); font-size: 12px; font-weight: 600; min-width: 32px; text-align: right;
}
.health-section { margin-bottom: 24px; }
.global-signals-table { width: 100%; border-collapse: collapse; }
.global-signals-table td {
  padding: 4px 10px; font-size: 11px; border-bottom: 1px solid var(--border-subtle);
}
.global-signals-table tr:nth-child(odd) { background: rgba(20,20,20,0.5); }
.global-signals-table .gs-name { color: var(--text-secondary); }
.global-signals-table .gs-val { font-family: var(--mono); text-align: right; color: var(--text); }

.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 60px 20px; color: var(--text-tertiary); font-size: 13px;
}
.empty-state-title {
  font-family: var(--mono); font-size: 14px; color: var(--text-secondary); margin-bottom: 4px;
}
.analyzing-dots::after { content: ''; animation: dots 1.5s steps(4, end) infinite; }
@keyframes dots {
  0% { content: ''; } 25% { content: '.'; } 50% { content: '..'; } 75% { content: '...'; }
}

.kbd-hint {
  position: fixed; bottom: 12px; right: 16px; font-family: var(--mono);
  font-size: 10px; color: var(--text-tertiary); z-index: 50; user-select: none;
  cursor: pointer;
}
.kbd-hint:hover { color: var(--text-secondary); }
.kbd-overlay {
  display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.7); z-index: 9000; align-items: center; justify-content: center;
}
.kbd-overlay.open { display: flex; }
.kbd-overlay-panel {
  background: var(--surface); border: 1px solid var(--border); padding: 24px 32px;
  font-family: var(--mono); font-size: 12px; max-width: 400px; width: 90%;
}
.kbd-overlay-panel h3 {
  font-size: 13px; color: var(--text); margin-bottom: 12px; font-weight: 600;
}
.kbd-overlay-panel div {
  display: flex; justify-content: space-between; padding: 4px 0;
  color: var(--text-secondary);
}
.kbd-overlay-panel kbd {
  background: var(--bg); border: 1px solid var(--border); padding: 0 6px;
  color: var(--text); font-size: 11px;
}

.chronic-badge {
  display: inline-block; font-family: var(--mono); font-size: 9px;
  background: rgba(239,68,68,0.15); color: var(--red); padding: 0 4px;
  border-radius: 2px; margin-left: 6px; vertical-align: middle;
}
</style>
</head>
<body>

<div id="progressBar"><div id="progressFill"></div></div>
<div class="progress-text" id="progressText"></div>

<div id="reconnectBanner">
  <span style="width:6px;height:6px;border-radius:50%;background:var(--yellow)"></span>
  Reconnecting<span class="analyzing-dots"></span>
</div>

<div class="topbar">
  <div class="topbar-brand">SHANNON<span> INSIGHT</span></div>
  <nav class="topbar-nav" id="nav">
    <a href="#overview" data-screen="overview" class="active">Overview</a>
    <a href="#issues" data-screen="issues">Issues</a>
    <a href="#files" data-screen="files">Files</a>
    <a href="#modules" data-screen="modules">Modules</a>
    <a href="#health" data-screen="health">Health</a>
  </nav>
  <div class="topbar-right">
    <div class="export-dropdown" id="exportDropdown">
      <button onclick="document.querySelector('.export-dropdown-menu').classList.toggle('open')">Export</button>
      <div class="export-dropdown-menu">
        <a href="/api/export/json">JSON</a>
        <a href="/api/export/csv">CSV</a>
      </div>
    </div>
    <div class="status-indicator" id="statusDot"></div>
    <span id="statusText"></span>
    <span id="metaInfo"></span>
  </div>
</div>

<div class="main">
  <div class="screen active" id="screen-overview">
    <div class="overview-top">
      <div>
        <div class="verdict-banner" id="verdictBanner"></div>
        <div class="health-big" id="healthScore">--</div>
        <div class="health-label" id="healthLabel">Analyzing<span class="analyzing-dots"></span></div>
      </div>
      <div class="stat-group" id="overviewStats">
        <div class="stat-item"><div class="stat-value" id="statFiles">--</div><div class="stat-label">files</div></div>
        <div class="stat-item"><div class="stat-value" id="statModules">--</div><div class="stat-label">modules</div></div>
        <div class="stat-item"><div class="stat-value" id="statCommits">--</div><div class="stat-label">commits</div></div>
        <div class="stat-item"><div class="stat-value" id="statIssues">--</div><div class="stat-label">issues</div></div>
      </div>
    </div>
    <div class="overview-cols">
      <div>
        <div class="section-title">Issue Summary</div>
        <div id="categorySummary"></div>
        <div id="riskHistogram" style="margin-top:16px"></div>
      </div>
      <div>
        <div class="section-title">Focus Point</div>
        <div id="focusPoint"></div>
      </div>
    </div>
  </div>

  <div class="screen" id="screen-issues">
    <div class="filter-bar" id="issueFilterBar"></div>
    <div class="issue-tabs" id="issueTabs"></div>
    <div id="issueContent"></div>
  </div>

  <div class="screen" id="screen-files">
    <div id="fileListView"></div>
    <div id="fileDetailView" style="display:none"></div>
  </div>

  <div class="screen" id="screen-modules">
    <div id="moduleListView"></div>
    <div id="moduleDetailView" style="display:none"></div>
  </div>

  <div class="screen" id="screen-health">
    <div id="healthTrends"></div>
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

<div class="kbd-hint" id="kbdHint">? shortcuts</div>
<div class="kbd-overlay" id="kbdOverlay">
  <div class="kbd-overlay-panel">
    <h3>Keyboard Shortcuts</h3>
    <div><span>Switch tabs</span><kbd>1</kbd>-<kbd>5</kbd></div>
    <div><span>Search files</span><kbd>/</kbd></div>
    <div><span>Move selection</span><kbd>j</kbd> / <kbd>k</kbd></div>
    <div><span>Open selected</span><kbd>Enter</kbd></div>
    <div><span>Go back</span><kbd>Esc</kbd></div>
    <div><span>Toggle shortcuts</span><kbd>?</kbd></div>
  </div>
</div>

<script>
(function() {
  "use strict";

  var DATA = null;
  var currentScreen = "overview";
  var currentFileDetail = null;
  var issueTab = "incomplete";
  var fileSortKey = "risk_score";
  var fileSortAsc = false;
  var fileSearch = "";
  var fileFilters = new Set();
  var issueSortKey = "severity_desc";
  var issueSeverityFilter = new Set(["critical","high","medium","low","info"]);
  var selectedIndex = {};
  var moduleDetail = null;
  var moduleSortKey = "health";
  var moduleSortAsc = true;
  var fileViewMode = "table";

  var SIGNAL_LABELS = {
    lines:"Lines of code",function_count:"Functions",class_count:"Classes/Structs",
    max_nesting:"Max nesting depth",cognitive_load:"Cognitive load",
    pagerank:"PageRank centrality",betweenness:"Betweenness centrality",
    in_degree:"Files that import this",out_degree:"Files this imports",
    blast_radius_size:"Blast radius",depth:"DAG depth",
    stub_ratio:"Stub/empty functions",is_orphan:"Is orphan",
    phantom_import_count:"Missing imports",compression_ratio:"Compression ratio",
    semantic_coherence:"Semantic coherence",
    total_changes:"Total commits",churn_trajectory:"Churn trend",
    churn_cv:"Churn volatility",bus_factor:"Bus factor",
    author_entropy:"Author diversity",fix_ratio:"Bugfix ratio",
    change_entropy:"Change distribution",
    risk_score:"Risk score",wiring_quality:"Wiring quality",
    file_health_score:"File health",raw_risk:"Raw risk"
  };

  var SIGNAL_CATEGORIES = [
    {key:"size",name:"Size & Complexity",signals:["lines","function_count","class_count","max_nesting","cognitive_load"]},
    {key:"structure",name:"Graph Position",signals:["pagerank","betweenness","in_degree","out_degree","blast_radius_size","depth"]},
    {key:"health",name:"Code Health",signals:["stub_ratio","is_orphan","phantom_import_count","compression_ratio","semantic_coherence"]},
    {key:"temporal",name:"Change History",signals:["total_changes","churn_trajectory","churn_cv","bus_factor","fix_ratio","change_entropy"]},
    {key:"team",name:"Team Context",signals:["author_entropy","bus_factor"]},
    {key:"risk",name:"Computed Risk",signals:["risk_score","wiring_quality","file_health_score","raw_risk"]}
  ];

  var SIGNAL_POLARITY = {
    risk_score:true,raw_risk:true,churn_cv:true,cognitive_load:true,
    max_nesting:true,stub_ratio:true,phantom_import_count:true,
    fix_ratio:true,blast_radius_size:true,
    wiring_quality:false,file_health_score:false,semantic_coherence:false,
    bus_factor:false,compression_ratio:false,
    pagerank:null,betweenness:null,in_degree:null,out_degree:null,
    depth:null,lines:null,function_count:null,class_count:null,
    total_changes:null,author_entropy:null
  };

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

  function polarColor(key, val) {
    var p = SIGNAL_POLARITY[key];
    if (p === true) return val > 0.5 ? "var(--red)" : val > 0.2 ? "var(--orange)" : "var(--text)";
    if (p === false) return val > 0.7 ? "var(--green)" : val < 0.3 ? "var(--orange)" : "var(--text)";
    return "var(--accent)";
  }

  function fmtSigVal(key, val) {
    if (val == null) return "--";
    if (typeof val === "boolean") return val ? "Yes" : "No";
    if (typeof val !== "number") return String(val);
    if (key === "stub_ratio" || key === "fix_ratio" || key === "compression_ratio" || key === "semantic_coherence")
      return (val * 100).toFixed(1) + "%";
    if (key === "risk_score" || key === "raw_risk" || key === "wiring_quality" || key === "file_health_score")
      return val.toFixed(3);
    if (key === "pagerank" || key === "betweenness" || key === "churn_cv" || key === "author_entropy" || key === "change_entropy" || key === "churn_trajectory")
      return val.toFixed(4);
    if (Number.isInteger(val)) return String(val);
    return val.toFixed(2);
  }

  function renderSparkline(values, w, h, color) {
    if (!values || values.length < 2) return "";
    var mn = Infinity, mx = -Infinity;
    for (var i = 0; i < values.length; i++) {
      if (values[i] < mn) mn = values[i];
      if (values[i] > mx) mx = values[i];
    }
    var range = mx - mn || 1;
    var pts = [];
    for (var i = 0; i < values.length; i++) {
      var x = (i / (values.length - 1)) * w;
      var y = h - ((values[i] - mn) / range) * (h - 2) - 1;
      pts.push(x.toFixed(1) + "," + y.toFixed(1));
    }
    var line = pts.join(" ");
    var fill = pts.join(" ") + " " + w + "," + h + " 0," + h;
    return '<svg width="' + w + '" height="' + h + '" style="vertical-align:middle">' +
      '<polyline points="' + fill + '" fill="' + color + '" opacity="0.1" />' +
      '<polyline points="' + line + '" fill="none" stroke="' + color + '" stroke-width="1.5" /></svg>';
  }

  function squarify(items, x, y, w, h) {
    if (!items.length) return [];
    if (items.length === 1) {
      items[0].x = x; items[0].y = y; items[0].w = w; items[0].h = h;
      return items;
    }
    var total = 0;
    for (var i = 0; i < items.length; i++) total += items[i].area;
    if (total <= 0) return items;
    var vertical = w >= h;
    var side = vertical ? h : w;
    var sum = 0, best = Infinity, split = 1;
    for (var i = 0; i < items.length - 1; i++) {
      sum += items[i].area;
      var frac = sum / total;
      var strip = vertical ? w * frac : h * frac;
      if (strip <= 0) continue;
      var worst = 0;
      var rowSum = 0;
      for (var j = 0; j <= i; j++) rowSum += items[j].area;
      for (var j = 0; j <= i; j++) {
        var rh = (items[j].area / rowSum) * side;
        var asp = rh > 0 ? Math.max(strip / rh, rh / strip) : Infinity;
        if (asp > worst) worst = asp;
      }
      if (worst < best) { best = worst; split = i + 1; }
    }
    var leftSum = 0;
    for (var i = 0; i < split; i++) leftSum += items[i].area;
    var frac = leftSum / total;
    var left = items.slice(0, split);
    var right = items.slice(split);
    if (vertical) {
      var lw = w * frac;
      var off = y;
      for (var i = 0; i < left.length; i++) {
        var ih = leftSum > 0 ? (left[i].area / leftSum) * h : 0;
        left[i].x = x; left[i].y = off; left[i].w = lw; left[i].h = ih;
        off += ih;
      }
      squarify(right, x + lw, y, w - lw, h);
    } else {
      var lh = h * frac;
      var off = x;
      for (var i = 0; i < left.length; i++) {
        var iw = leftSum > 0 ? (left[i].area / leftSum) * w : 0;
        left[i].x = off; left[i].y = y; left[i].w = iw; left[i].h = lh;
        off += iw;
      }
      squarify(right, x, y + lh, w, h - lh);
    }
    return items;
  }

  function polarToXY(cx, cy, radius, angleIdx, total, score) {
    var angle = (Math.PI * 2 * angleIdx / total) - Math.PI / 2;
    var r = radius * Math.min(score / 10, 1);
    return { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) };
  }

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
    if (screen === "modules" && detail) {
      moduleDetail = detail;
      showModuleDetail(detail);
    } else if (screen === "modules") {
      moduleDetail = null;
      renderModules();
    }
  }

  $("#nav").addEventListener("click", function(e) {
    var a = e.target.closest("a[data-screen]");
    if (!a) return;
    e.preventDefault();
    location.hash = a.dataset.screen;
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

  document.addEventListener("click", function(e) {
    if (!e.target.closest(".export-dropdown")) {
      var m = $(".export-dropdown-menu");
      if (m) m.classList.remove("open");
    }
  });

  function renderOverview() {
    if (!DATA) return;
    var score = DATA.health;
    var color = hColor(score);
    var el = $("#healthScore");
    el.textContent = score.toFixed(1);
    el.style.color = color;

    var vb = $("#verdictBanner");
    if (DATA.verdict) {
      vb.textContent = DATA.verdict;
      vb.style.color = DATA.verdict_color || color;
    } else {
      vb.textContent = "";
    }

    var lbl = $("#healthLabel");
    lbl.textContent = DATA.health_label || "";
    lbl.style.color = "var(--text-secondary)";

    $("#statFiles").textContent = fmtN(DATA.file_count);
    $("#statModules").textContent = fmtN(DATA.module_count);
    $("#statCommits").textContent = fmtN(DATA.commits_analyzed);
    var totalIssues = 0;
    var cats = DATA.categories || {};
    for (var k in cats) totalIssues += cats[k].count;
    $("#statIssues").textContent = fmtN(totalIssues);

    var catOrder = ["incomplete","fragile","tangled","team"];
    var catLabels = {incomplete:"Incomplete",fragile:"Fragile",tangled:"Tangled",team:"Team"};
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
    if (DATA.recent_changes) {
      catHtml += '<div style="margin-top:8px;font-size:11px;color:var(--accent);font-family:var(--mono)">' +
        DATA.recent_changes.length + ' files changed</div>';
    }
    if (DATA.changes) {
      var newF = DATA.changes.new_findings || 0;
      var resF = DATA.changes.resolved_findings || 0;
      if (newF || resF) {
        catHtml += '<div style="font-size:11px;color:var(--text-secondary);font-family:var(--mono);margin-top:4px">';
        if (newF) catHtml += '<span style="color:var(--red)">+' + newF + ' new</span> ';
        if (resF) catHtml += '<span style="color:var(--green)">' + resF + ' resolved</span>';
        catHtml += '</div>';
      }
    }
    var catContainer = $("#categorySummary");
    catContainer.innerHTML = catHtml;
    catContainer.onclick = function(e) {
      var row = e.target.closest(".cat-row");
      if (!row) return;
      issueTab = row.dataset.cat;
      location.hash = "issues";
    };

    // Risk histogram
    var histDiv = $("#riskHistogram");
    if (DATA.files) {
      var bins = [0,0,0,0,0];
      var binLabels = ["0-0.2","0.2-0.4","0.4-0.6","0.6-0.8","0.8-1.0"];
      var binColors = ["var(--green)","var(--yellow)","var(--yellow)","var(--orange)","var(--red)"];
      for (var p in DATA.files) {
        var rs = DATA.files[p].risk_score || 0;
        var bi = Math.min(Math.floor(rs * 5), 4);
        bins[bi]++;
      }
      var maxBin = Math.max.apply(null, bins) || 1;
      var hSvg = '<div class="section-title" style="margin-top:8px">Risk Distribution</div>';
      hSvg += '<svg width="100%" height="80" viewBox="0 0 300 80" preserveAspectRatio="none">';
      for (var i = 0; i < 5; i++) {
        var bw = (bins[i] / maxBin) * 240;
        var by = i * 16;
        hSvg += '<rect x="50" y="' + by + '" width="' + bw + '" height="13" fill="' + binColors[i] + '" opacity="0.7" />';
        hSvg += '<text x="0" y="' + (by + 10) + '" fill="' + "var(--text-tertiary)" + '" font-size="8" font-family="var(--mono)">' + binLabels[i] + '</text>';
        hSvg += '<text x="' + (55 + bw) + '" y="' + (by + 10) + '" fill="' + "var(--text-secondary)" + '" font-size="8" font-family="var(--mono)">' + bins[i] + '</text>';
      }
      hSvg += '</svg>';
      histDiv.innerHTML = hSvg;
    }

    // Focus point
    var fp = $("#focusPoint");
    if (DATA.focus) {
      var f = DATA.focus;
      var html = '<div class="focus-path"><a href="#files/' + encodeURIComponent(f.path) + '">' + esc(f.path) + '</a></div>';
      if (f.risk_score != null || f.impact_score != null) {
        html += '<div class="focus-score-breakdown">';
        if (f.risk_score != null) html += '<span>risk:' + fmtF(f.risk_score,3) + '</span>';
        if (f.impact_score != null) html += '<span>impact:' + fmtF(f.impact_score,3) + '</span>';
        if (f.tractability_score != null) html += '<span>tract:' + fmtF(f.tractability_score,3) + '</span>';
        if (f.confidence_score != null) html += '<span>conf:' + fmtF(f.confidence_score,2) + '</span>';
        html += '</div>';
      }
      html += '<div class="focus-why">' + esc(f.why) + '</div>';
      var findings = f.findings || [];
      for (var j = 0; j < Math.min(findings.length, 3); j++) {
        var fi = findings[j];
        var sk = sevKey(fi.severity);
        html += '<div class="focus-finding"><div class="sev-dot ' + sk + '"></div>' +
          '<div class="focus-finding-text">' + esc(fi.label) + '</div></div>';
      }
      if (f.alternatives && f.alternatives.length > 0) {
        html += '<div style="margin-top:10px;font-size:11px;color:var(--text-tertiary)">Also consider:</div>';
        for (var a = 0; a < Math.min(f.alternatives.length, 3); a++) {
          var alt = f.alternatives[a];
          html += '<div style="font-family:var(--mono);font-size:11px;padding:2px 0">' +
            '<a href="#files/' + encodeURIComponent(alt.path) + '" style="color:var(--text-secondary)">' + esc(alt.path) + '</a>';
          if (alt.why) html += ' <span style="color:var(--text-tertiary)">' + esc(alt.why) + '</span>';
          html += '</div>';
        }
      }
      fp.innerHTML = html;
    } else {
      fp.innerHTML = '<div style="color:var(--text-tertiary);font-size:12px;padding:8px 0">No actionable focus point identified.</div>';
    }
  }

  function renderIssues() {
    if (!DATA) return;
    var cats = DATA.categories || {};
    var order = ["incomplete","fragile","tangled","team"];
    var labels = {incomplete:"Incomplete",fragile:"Fragile",tangled:"Tangled",team:"Team"};
    if (!cats[issueTab]) issueTab = order[0];

    // Filter bar
    var fbHtml = '<select class="sort-select" id="issueSortSel">' +
      '<option value="severity_desc"' + (issueSortKey === "severity_desc" ? " selected" : "") + '>Severity (high first)</option>' +
      '<option value="severity_asc"' + (issueSortKey === "severity_asc" ? " selected" : "") + '>Severity (low first)</option>' +
      '<option value="effort_asc"' + (issueSortKey === "effort_asc" ? " selected" : "") + '>Effort (low first)</option>' +
      '<option value="file_count"' + (issueSortKey === "file_count" ? " selected" : "") + '>File count</option></select> ';
    var sevLevels = ["critical","high","medium","low","info"];
    for (var i = 0; i < sevLevels.length; i++) {
      var sl = sevLevels[i];
      fbHtml += '<button class="sev-filter' + (issueSeverityFilter.has(sl) ? " active" : "") + '" data-sev="' + sl + '">' + sl.toUpperCase() + '</button> ';
    }
    $("#issueFilterBar").innerHTML = fbHtml;
    var sortSel = $("#issueSortSel");
    if (sortSel) sortSel.onchange = function() { issueSortKey = this.value; renderIssues(); };
    $$("#issueFilterBar .sev-filter").forEach(function(btn) {
      btn.onclick = function() {
        var s = btn.dataset.sev;
        if (issueSeverityFilter.has(s)) issueSeverityFilter.delete(s); else issueSeverityFilter.add(s);
        renderIssues();
      };
    });

    var tabsHtml = "";
    for (var i = 0; i < order.length; i++) {
      var key = order[i];
      var cat = cats[key];
      if (!cat) continue;
      tabsHtml += '<button class="issue-tab' + (issueTab === key ? ' active' : '') + '" data-tab="' + key + '">' +
        esc(labels[key] || key) + '<span class="issue-tab-count">' + cat.count + '</span></button>';
    }
    $("#issueTabs").innerHTML = tabsHtml;

    var cat = cats[issueTab];
    if (!cat || cat.count === 0) {
      $("#issueContent").innerHTML = '<div class="empty-state"><div class="empty-state-title">No ' + esc(labels[issueTab] || issueTab) + ' issues</div></div>';
    } else {
      var findings = (cat.findings || []).slice();
      // Filter by severity
      findings = findings.filter(function(f) { return issueSeverityFilter.has(sevKey(f.severity)); });
      // Sort
      var chronicSet = (DATA.trends && DATA.trends.chronic) ? new Set(DATA.trends.chronic.map(function(c){return c.id||c.label})) : new Set();
      if (issueSortKey === "severity_desc") findings.sort(function(a,b){ return b.severity - a.severity; });
      else if (issueSortKey === "severity_asc") findings.sort(function(a,b){ return a.severity - b.severity; });
      else if (issueSortKey === "effort_asc") {
        var eo = {LOW:0,MEDIUM:1,HIGH:2};
        findings.sort(function(a,b){ return (eo[a.effort]||1) - (eo[b.effort]||1); });
      } else if (issueSortKey === "file_count") findings.sort(function(a,b){ return (b.files?b.files.length:0) - (a.files?a.files.length:0); });

      var html = "";
      for (var j = 0; j < findings.length; j++) {
        var f = findings[j];
        var sk = sevKey(f.severity);
        var opStyle = f.confidence != null && f.confidence < 0.5 ? ' style="opacity:0.6"' : '';
        html += '<div class="finding-row"' + opStyle + '>';
        html += '<div class="finding-head"><div class="sev-dot ' + sk + '"></div>';
        html += '<span class="finding-type-label">' + esc(f.label) + '</span>';
        if (f.effort) html += '<span class="effort-badge">' + esc(f.effort) + '</span>';
        if (chronicSet.has(f.id || f.label)) html += '<span class="chronic-badge">CHRONIC</span>';
        html += '</div>';
        if (f.files && f.files.length) {
          html += '<div class="finding-files">';
          for (var fi = 0; fi < f.files.length; fi++) {
            if (fi > 0) html += ', ';
            html += '<a href="#files/' + encodeURIComponent(f.files[fi]) + '">' + esc(f.files[fi]) + '</a>';
          }
          html += '</div>';
        }
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
        if (f.interpretation) html += '<div class="finding-interp">' + esc(f.interpretation) + '</div>';
        if (f.suggestion) html += '<div class="finding-suggestion">' + esc(f.suggestion) + '</div>';
        html += '</div>';
      }
      $("#issueContent").innerHTML = html;
    }

    $("#issueTabs").onclick = function(e) {
      var btn = e.target.closest(".issue-tab");
      if (!btn) return;
      issueTab = btn.dataset.tab;
      renderIssues();
    };
  }

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
    for (var p in DATA.files) entries.push([p, DATA.files[p]]);
    var totalCount = entries.length;
    var changedSet = DATA.recent_changes ? new Set(DATA.recent_changes) : new Set();

    // Apply search
    if (fileSearch) {
      var q = fileSearch.toLowerCase();
      entries = entries.filter(function(e) { return e[0].toLowerCase().indexOf(q) !== -1; });
    }
    // Apply filters
    if (fileFilters.has("has_issues")) entries = entries.filter(function(e){ return (e[1].finding_count||0) > 0; });
    if (fileFilters.has("orphans")) entries = entries.filter(function(e){ return e[1].signals && e[1].signals.is_orphan; });
    var roleFilters = [];
    fileFilters.forEach(function(f) { if (["MODEL","SERVICE","ENTRY_POINT","TEST"].indexOf(f) !== -1) roleFilters.push(f); });
    if (roleFilters.length > 0) {
      var rs = new Set(roleFilters);
      entries = entries.filter(function(e){ return rs.has(e[1].role); });
    }

    // Sort
    entries.sort(function(a, b) {
      if (fileSortKey === "path") return fileSortAsc ? a[0].localeCompare(b[0]) : b[0].localeCompare(a[0]);
      var va = a[1][fileSortKey] != null ? a[1][fileSortKey] : 0;
      var vb = b[1][fileSortKey] != null ? b[1][fileSortKey] : 0;
      return fileSortAsc ? va - vb : vb - va;
    });

    // Filter bar
    var fbHtml = '<div class="filter-bar">';
    fbHtml += '<input class="search-input" type="text" id="fileSearchInput" placeholder="Search files..." value="' + esc(fileSearch) + '" />';
    var chips = [["has_issues","Has Issues"],["orphans","Orphans"],["MODEL","Model"],["SERVICE","Service"],["ENTRY_POINT","Entry Point"],["TEST","Test"]];
    for (var i = 0; i < chips.length; i++) {
      fbHtml += '<button class="filter-chip' + (fileFilters.has(chips[i][0]) ? " active" : "") + '" data-filter="' + chips[i][0] + '">' + chips[i][1] + '</button>';
    }
    fbHtml += '<div class="treemap-toggle"><button class="' + (fileViewMode === "table" ? "active" : "") + '" data-mode="table">Table</button>';
    fbHtml += '<button class="' + (fileViewMode === "treemap" ? "active" : "") + '" data-mode="treemap">Treemap</button></div>';
    fbHtml += '</div>';
    fbHtml += '<div style="font-size:11px;color:var(--text-tertiary);font-family:var(--mono);margin-bottom:8px">Showing ' + entries.length + ' of ' + totalCount + ' files</div>';

    if (fileViewMode === "treemap") {
      var tmItems = [];
      for (var i = 0; i < Math.min(entries.length, 300); i++) {
        var area = Math.max((entries[i][1].lines || 1), 1);
        tmItems.push({path:entries[i][0], area:area, color_value:entries[i][1].risk_score || 0});
      }
      tmItems.sort(function(a,b){return b.area - a.area;});
      var tmW = 800, tmH = 500;
      squarify(tmItems, 0, 0, tmW, tmH);
      var svg = '<svg viewBox="0 0 ' + tmW + ' ' + tmH + '" width="100%" style="max-height:500px;cursor:pointer" id="treemapSvg">';
      for (var i = 0; i < tmItems.length; i++) {
        var t = tmItems[i];
        if (!t.w || !t.h || t.w < 1 || t.h < 1) continue;
        var rc = hColor(10 - t.color_value * 10);
        svg += '<rect x="' + t.x.toFixed(1) + '" y="' + t.y.toFixed(1) + '" width="' + t.w.toFixed(1) + '" height="' + t.h.toFixed(1) + '" fill="' + rc + '" opacity="0.6" stroke="var(--bg)" stroke-width="1" data-path="' + esc(t.path) + '"><title>' + esc(t.path) + ' (' + Math.round(t.area) + ' lines, risk ' + t.color_value.toFixed(3) + ')</title></rect>';
        if (t.w > 60 && t.h > 14) {
          var name = t.path.split("/").pop();
          svg += '<text x="' + (t.x + 3).toFixed(1) + '" y="' + (t.y + 11).toFixed(1) + '" font-size="9" font-family="var(--mono)" fill="var(--text)" pointer-events="none">' + esc(name.slice(0,Math.floor(t.w/6))) + '</text>';
        }
      }
      svg += '</svg>';
      listView.innerHTML = fbHtml + svg;
      var tmSvg = $("#treemapSvg");
      if (tmSvg) tmSvg.onclick = function(e) {
        var rect = e.target.closest("rect[data-path]");
        if (rect) location.hash = "files/" + encodeURIComponent(rect.dataset.path);
      };
    } else {
      var cols = [
        {key:"path",label:"File",cls:"td-path"},
        {key:"risk_score",label:"Risk",cls:"td-risk"},
        {key:"total_changes",label:"Churn",cls:"td-num"},
        {key:"cognitive_load",label:"Complexity",cls:"td-num"},
        {key:"blast_radius",label:"Blast R.",cls:"td-num"},
        {key:"finding_count",label:"Issues",cls:"td-issues"},
      ];
      var html = fbHtml + '<table class="file-table"><thead><tr>';
      for (var c = 0; c < cols.length; c++) {
        var col = cols[c];
        var arrow = fileSortKey === col.key ? (fileSortAsc ? '<span class="sort-arrow">&#9650;</span>' : '<span class="sort-arrow">&#9660;</span>') : '';
        var thCls = col.key !== "path" ? ' class="num"' : '';
        html += '<th' + thCls + ' data-sort="' + col.key + '">' + col.label + arrow + '</th>';
      }
      html += '</tr></thead><tbody>';
      var limit = Math.min(entries.length, 200);
      var sel = selectedIndex["files"] || 0;
      for (var r = 0; r < limit; r++) {
        var path = entries[r][0];
        var f = entries[r][1];
        var riskColor = hColor(10 - (f.risk_score || 0) * 10);
        html += '<tr data-path="' + esc(path) + '"' + (r === sel ? ' class="kbd-selected"' : '') + '>';
        html += '<td class="td-path" title="' + esc(path) + '"><span>' + esc(path) + '</span>';
        if (changedSet.has(path)) html += '<span class="changed-badge">changed</span>';
        html += '</td>';
        var riskStyle = (f.risk_score || 0) > 0.05 ? 'color:' + riskColor : '';
        html += '<td class="td-risk" style="' + riskStyle + '">' + fmtF(f.risk_score, 3) + '</td>';
        html += '<td class="td-num">' + (f.total_changes || 0) + '</td>';
        html += '<td class="td-num">' + fmtF(f.cognitive_load, 1) + '</td>';
        html += '<td class="td-num">' + (f.blast_radius || 0) + '</td>';
        html += '<td class="td-issues">' + (f.finding_count || 0) + '</td>';
        html += '</tr>';
      }
      html += '</tbody></table>';
      if (entries.length > 200) html += '<div class="file-count-note">Showing 200 of ' + entries.length + ' files (filtered)</div>';
      listView.innerHTML = html;

      var thead = listView.querySelector("thead");
      if (thead) thead.onclick = function(e) {
        var th = e.target.closest("th[data-sort]");
        if (!th) return;
        var key = th.dataset.sort;
        if (fileSortKey === key) fileSortAsc = !fileSortAsc;
        else { fileSortKey = key; fileSortAsc = key === "path"; }
        showFileList();
      };
      listView.querySelectorAll("tbody tr[data-path]").forEach(function(row) {
        row.onclick = function() { location.hash = "files/" + encodeURIComponent(row.dataset.path); };
      });
    }

    // Bind filter bar events
    var si = $("#fileSearchInput");
    if (si) {
      si.oninput = function() { fileSearch = si.value; showFileList(); };
      si.onkeydown = function(e) { if (e.key === "Escape") { si.blur(); } };
    }
    $$("#fileListView .filter-chip").forEach(function(chip) {
      chip.onclick = function() {
        var f = chip.dataset.filter;
        if (fileFilters.has(f)) fileFilters.delete(f); else fileFilters.add(f);
        showFileList();
      };
    });
    $$("#fileListView .treemap-toggle button").forEach(function(btn) {
      btn.onclick = function() { fileViewMode = btn.dataset.mode; showFileList(); };
    });
  }

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
    html += '<div class="file-detail-header">';
    html += '<span class="file-detail-path">' + esc(path) + '</span>';
    if (f.role && f.role !== "UNKNOWN") html += '<span class="file-detail-role">' + esc(f.role) + '</span>';
    html += '<span class="file-detail-health" style="color:' + color + '">' + fmtF(f.health, 1) + '</span>';
    html += '</div>';

    var metrics = [
      ["Lines", f.lines], ["Functions", f.signals ? f.signals.function_count : null],
      ["Risk Score", fmtF(f.risk_score, 3)], ["PageRank", fmtF(f.pagerank, 4)],
      ["Churn", f.total_changes], ["Bus Factor", fmtF(f.bus_factor, 1)],
      ["Blast Radius", f.blast_radius], ["Cognitive Load", fmtF(f.cognitive_load, 1)],
    ];
    html += '<div class="file-detail-metrics">';
    for (var m = 0; m < metrics.length; m++) {
      html += '<div class="fdm-cell"><div class="fdm-value">' + (metrics[m][1] != null ? metrics[m][1] : "--") + '</div>' +
        '<div class="fdm-label">' + metrics[m][0] + '</div></div>';
    }
    html += '</div>';

    // File findings
    var fileFindings = [];
    var cats = DATA.categories || {};
    for (var ck in cats) {
      var catFindings = cats[ck].findings || [];
      for (var fi = 0; fi < catFindings.length; fi++) {
        if (catFindings[fi].files && catFindings[fi].files.indexOf(path) !== -1) fileFindings.push(catFindings[fi]);
      }
    }
    if (fileFindings.length > 0) {
      html += '<div class="file-detail-section"><div class="file-detail-section-title">Issues (' + fileFindings.length + ')</div>';
      for (var j = 0; j < fileFindings.length; j++) {
        var ff = fileFindings[j];
        var sk = sevKey(ff.severity);
        html += '<div class="finding-row"><div class="finding-head"><div class="sev-dot ' + sk + '"></div>' +
          '<span class="finding-type-label">' + esc(ff.label) + '</span>';
        if (ff.effort) html += '<span class="effort-badge">' + esc(ff.effort) + '</span>';
        html += '</div>';
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
        if (ff.interpretation) html += '<div class="finding-interp">' + esc(ff.interpretation) + '</div>';
        if (ff.suggestion) html += '<div class="finding-suggestion">' + esc(ff.suggestion) + '</div>';
        html += '</div>';
      }
      html += '</div>';
    }

    // Signals grouped by category
    var sigs = f.signals || {};
    var sigKeys = Object.keys(sigs);
    if (sigKeys.length > 0) {
      html += '<div class="file-detail-section">';
      for (var ci = 0; ci < SIGNAL_CATEGORIES.length; ci++) {
        var cat = SIGNAL_CATEGORIES[ci];
        var catSigs = cat.signals.filter(function(s) { return sigs[s] != null; });
        if (!catSigs.length) continue;
        html += '<div class="file-detail-section-title signals-collapsible sig-cat-toggle" data-cat="' + cat.key + '">' + esc(cat.name) + ' (' + catSigs.length + ')</div>';
        html += '<div class="signals-grid sig-cat-grid" data-cat="' + cat.key + '" style="display:none">';
        for (var s = 0; s < catSigs.length; s++) {
          var sk2 = catSigs[s];
          var sv = sigs[sk2];
          var label = SIGNAL_LABELS[sk2] || sk2.replace(/_/g, ' ');
          var display = fmtSigVal(sk2, sv);
          var valColor = typeof sv === "number" ? polarColor(sk2, sv) : "var(--text)";
          var sparkHtml = "";
          if (f.trends && f.trends[sk2]) sparkHtml = " " + renderSparkline(f.trends[sk2], 48, 14, valColor);
          html += '<div class="sig-row"><span class="sig-name">' + esc(label) + '</span>' +
            '<span class="sig-val" style="color:' + valColor + '">' + esc(display) + sparkHtml + '</span></div>';
        }
        html += '</div>';
      }
      // Uncategorized
      var catted = new Set();
      SIGNAL_CATEGORIES.forEach(function(c){c.signals.forEach(function(s){catted.add(s);});});
      var uncatSigs = sigKeys.filter(function(s){return !catted.has(s) && sigs[s] != null;}).sort();
      if (uncatSigs.length) {
        html += '<div class="file-detail-section-title signals-collapsible sig-cat-toggle" data-cat="other">Other (' + uncatSigs.length + ')</div>';
        html += '<div class="signals-grid sig-cat-grid" data-cat="other" style="display:none">';
        for (var s = 0; s < uncatSigs.length; s++) {
          var sk2 = uncatSigs[s];
          var sv = sigs[sk2];
          var display = typeof sv === "number" ? (Number.isInteger(sv) ? String(sv) : sv.toFixed(4)) : String(sv);
          html += '<div class="sig-row"><span class="sig-name">' + esc(sk2.replace(/_/g, ' ')) + '</span>' +
            '<span class="sig-val">' + esc(display) + '</span></div>';
        }
        html += '</div>';
      }
      html += '</div>';
    }

    detailView.innerHTML = html;
    detailView.querySelectorAll(".sig-cat-toggle").forEach(function(toggle) {
      toggle.onclick = function() {
        var cat = toggle.dataset.cat;
        var grid = detailView.querySelector('.sig-cat-grid[data-cat="' + cat + '"]');
        if (!grid) return;
        var open = grid.style.display !== "none";
        grid.style.display = open ? "none" : "grid";
        toggle.classList.toggle("open", !open);
      };
    });
  }

  function renderModules() {
    var listView = $("#moduleListView");
    var detailView = $("#moduleDetailView");
    listView.style.display = "block";
    detailView.style.display = "none";
    if (!DATA || !DATA.modules) {
      listView.innerHTML = '<div class="empty-state"><div class="empty-state-title">No module data</div></div>';
      return;
    }
    var modules = DATA.modules;
    var entries = [];
    for (var p in modules) entries.push([p, modules[p]]);

    entries.sort(function(a, b) {
      if (moduleSortKey === "path") return moduleSortAsc ? a[0].localeCompare(b[0]) : b[0].localeCompare(a[0]);
      var va = a[1][moduleSortKey] != null ? a[1][moduleSortKey] : 0;
      var vb = b[1][moduleSortKey] != null ? b[1][moduleSortKey] : 0;
      return moduleSortAsc ? va - vb : vb - va;
    });

    var cols = [
      {key:"path",label:"Module",cls:"td-path"},
      {key:"health",label:"Health",cls:"td-risk"},
      {key:"instability",label:"Instability",cls:"td-num"},
      {key:"abstractness",label:"Abstractness",cls:"td-num"},
      {key:"file_count",label:"Files",cls:"td-num"},
      {key:"velocity",label:"Velocity",cls:"td-num"},
    ];
    var html = '<table class="module-table"><thead><tr>';
    for (var c = 0; c < cols.length; c++) {
      var col = cols[c];
      var arrow = moduleSortKey === col.key ? (moduleSortAsc ? '<span class="sort-arrow">&#9650;</span>' : '<span class="sort-arrow">&#9660;</span>') : '';
      var thCls = col.key !== "path" ? ' class="num"' : '';
      html += '<th' + thCls + ' data-sort="' + col.key + '">' + col.label + arrow + '</th>';
    }
    html += '</tr></thead><tbody>';
    for (var r = 0; r < entries.length; r++) {
      var p = entries[r][0];
      var m = entries[r][1];
      var hc = hColor(m.health || 5);
      html += '<tr data-mod="' + esc(p) + '">';
      html += '<td class="td-path"><span>' + esc(p) + '</span></td>';
      html += '<td class="td-risk" style="color:' + hc + '">' + fmtF(m.health, 1) + '</td>';
      html += '<td class="td-num">' + fmtF(m.instability, 2) + '</td>';
      html += '<td class="td-num">' + fmtF(m.abstractness, 2) + '</td>';
      html += '<td class="td-num">' + (m.file_count || 0) + '</td>';
      html += '<td class="td-num">' + fmtF(m.velocity, 1) + '</td>';
      html += '</tr>';
    }
    html += '</tbody></table>';
    listView.innerHTML = html;

    var thead = listView.querySelector("thead");
    if (thead) thead.onclick = function(e) {
      var th = e.target.closest("th[data-sort]");
      if (!th) return;
      var key = th.dataset.sort;
      if (moduleSortKey === key) moduleSortAsc = !moduleSortAsc;
      else { moduleSortKey = key; moduleSortAsc = key === "path"; }
      renderModules();
    };
    listView.querySelectorAll("tbody tr[data-mod]").forEach(function(row) {
      row.onclick = function() { location.hash = "modules/" + encodeURIComponent(row.dataset.mod); };
    });
  }

  function showModuleDetail(path) {
    var listView = $("#moduleListView");
    var detailView = $("#moduleDetailView");
    listView.style.display = "none";
    detailView.style.display = "block";
    if (!DATA || !DATA.modules || !DATA.modules[path]) {
      detailView.innerHTML = '<a class="file-detail-back" href="#modules">&larr; Modules</a>' +
        '<div class="empty-state"><div class="empty-state-title">Module not found</div><div>' + esc(path) + '</div></div>';
      return;
    }
    var m = DATA.modules[path];
    var color = hColor(m.health || 5);
    var html = '<a class="file-detail-back" href="#modules">&larr; Modules</a>';
    html += '<div class="file-detail-header">';
    html += '<span class="file-detail-path">' + esc(path) + '</span>';
    html += '<span class="file-detail-health" style="color:' + color + '">' + fmtF(m.health, 1) + '</span>';
    html += '</div>';
    html += '<div class="file-detail-metrics">';
    var stats = [["Files",m.file_count],["Instability",fmtF(m.instability,2)],["Abstractness",fmtF(m.abstractness,2)],["Velocity",fmtF(m.velocity,1)]];
    for (var i = 0; i < stats.length; i++) {
      html += '<div class="fdm-cell"><div class="fdm-value">' + (stats[i][1] != null ? stats[i][1] : "--") + '</div><div class="fdm-label">' + stats[i][0] + '</div></div>';
    }
    html += '</div>';
    if (m.files && m.files.length) {
      html += '<div class="file-detail-section"><div class="file-detail-section-title">Files (' + m.files.length + ')</div>';
      for (var i = 0; i < m.files.length; i++) {
        html += '<div style="font-family:var(--mono);font-size:11px;padding:2px 0"><a href="#files/' + encodeURIComponent(m.files[i]) + '">' + esc(m.files[i]) + '</a></div>';
      }
      html += '</div>';
    }
    if (m.violations && m.violations.length) {
      html += '<div class="file-detail-section"><div class="file-detail-section-title">Violations (' + m.violations.length + ')</div>';
      for (var i = 0; i < m.violations.length; i++) {
        html += '<div style="font-size:11px;color:var(--orange);padding:2px 0">' + esc(m.violations[i]) + '</div>';
      }
      html += '</div>';
    }
    detailView.innerHTML = html;
  }

  function renderHealth() {
    if (!DATA) return;
    var trendsHtml = "";

    // Trend chart
    if (DATA.trends && DATA.trends.health) {
      var vals = DATA.trends.health;
      var tw = 600, th = 200;
      trendsHtml += '<div class="health-section"><div class="section-title">Health Trend</div>';
      trendsHtml += renderSparkline(vals, tw, th, "var(--accent)");
      trendsHtml += '</div>';
    }
    // Top movers
    if (DATA.trends && DATA.trends.movers) {
      var movers = DATA.trends.movers;
      trendsHtml += '<div class="health-section"><div class="section-title">Top Movers</div>';
      for (var i = 0; i < movers.length; i++) {
        var m = movers[i];
        var dc = m.delta > 0 ? "var(--red)" : "var(--green)";
        var ds = m.delta > 0 ? "+" + m.delta.toFixed(3) : m.delta.toFixed(3);
        trendsHtml += '<div style="font-family:var(--mono);font-size:11px;padding:3px 0">' +
          '<a href="#files/' + encodeURIComponent(m.path) + '">' + esc(m.path) + '</a> ' +
          '<span style="color:' + dc + '">' + ds + '</span></div>';
      }
      trendsHtml += '</div>';
    }
    // Chronic
    if (DATA.trends && DATA.trends.chronic && DATA.trends.chronic.length) {
      var chronic = DATA.trends.chronic;
      trendsHtml += '<div class="health-section"><div class="section-title">Chronic Findings</div>';
      for (var i = 0; i < chronic.length; i++) {
        trendsHtml += '<div style="font-size:11px;padding:3px 0;color:var(--orange)">' + esc(chronic[i].label || chronic[i].id) +
          ' <span style="color:var(--text-tertiary)">(' + (chronic[i].snapshots || '?') + ' snapshots)</span></div>';
      }
      trendsHtml += '</div>';
    }
    $("#healthTrends").innerHTML = trendsHtml;

    // Radar chart for concerns
    var concerns = DATA.concerns || [];
    if (concerns.length >= 3) {
      var cx = 150, cy = 150, radius = 120;
      var n = concerns.length;
      var svg = '<svg width="300" height="300" viewBox="0 0 300 300">';
      // Grid rings
      for (var ring = 2; ring <= 10; ring += 2) {
        var pts = [];
        for (var i = 0; i < n; i++) {
          var p = polarToXY(cx, cy, radius, i, n, ring);
          pts.push(p.x.toFixed(1) + "," + p.y.toFixed(1));
        }
        svg += '<polygon points="' + pts.join(" ") + '" fill="none" stroke="var(--border)" stroke-width="0.5" />';
      }
      // Axes
      for (var i = 0; i < n; i++) {
        var p = polarToXY(cx, cy, radius, i, n, 10);
        svg += '<line x1="' + cx + '" y1="' + cy + '" x2="' + p.x.toFixed(1) + '" y2="' + p.y.toFixed(1) + '" stroke="var(--border)" stroke-width="0.5" />';
        var lp = polarToXY(cx, cy, radius + 16, i, n, 10);
        svg += '<text x="' + lp.x.toFixed(1) + '" y="' + lp.y.toFixed(1) + '" text-anchor="middle" font-size="9" font-family="var(--mono)" fill="var(--text-secondary)">' + esc(concerns[i].name) + '</text>';
      }
      // Data polygon
      var dataPts = [];
      for (var i = 0; i < n; i++) {
        var p = polarToXY(cx, cy, radius, i, n, concerns[i].score);
        dataPts.push(p.x.toFixed(1) + "," + p.y.toFixed(1));
      }
      svg += '<polygon points="' + dataPts.join(" ") + '" fill="var(--accent)" fill-opacity="0.15" stroke="var(--accent)" stroke-width="1.5" />';
      for (var i = 0; i < n; i++) {
        var p = polarToXY(cx, cy, radius, i, n, concerns[i].score);
        svg += '<circle cx="' + p.x.toFixed(1) + '" cy="' + p.y.toFixed(1) + '" r="3" fill="var(--accent)" />';
      }
      svg += '</svg>';
      $("#concernBars").innerHTML = svg;
    } else {
      // Fallback to bars
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
    }

    // Global signals
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

  function render() {
    renderOverview();
    if (currentScreen === "issues") renderIssues();
    if (currentScreen === "health") renderHealth();
    if (currentScreen === "files") {
      if (currentFileDetail) showFileDetail(currentFileDetail);
      else showFileList();
    }
    if (currentScreen === "modules") {
      if (moduleDetail) showModuleDetail(moduleDetail);
      else renderModules();
    }
    if (DATA) {
      var parts = [];
      if (DATA.commit_sha) parts.push(DATA.commit_sha.slice(0, 7));
      if (DATA.timestamp) {
        try { parts.push(new Date(DATA.timestamp).toLocaleTimeString()); } catch(e) {}
      }
      $("#metaInfo").textContent = parts.join(" \u00b7 ");
    }
  }

  // Keyboard navigation
  document.addEventListener("keydown", function(e) {
    var tag = (e.target.tagName || "").toLowerCase();
    if (tag === "input" || tag === "textarea" || tag === "select") {
      if (e.key === "Escape") e.target.blur();
      return;
    }
    var overlay = $("#kbdOverlay");
    if (e.key === "?") { overlay.classList.toggle("open"); e.preventDefault(); return; }
    if (overlay.classList.contains("open")) { if (e.key === "Escape") overlay.classList.remove("open"); return; }
    if (e.key === "Escape") {
      if (currentFileDetail) { location.hash = "files"; e.preventDefault(); }
      else if (moduleDetail) { location.hash = "modules"; e.preventDefault(); }
      return;
    }
    var screens = ["overview","issues","files","modules","health"];
    if (e.key >= "1" && e.key <= "5") { location.hash = screens[parseInt(e.key) - 1]; e.preventDefault(); return; }
    if (e.key === "/") {
      e.preventDefault();
      if (currentScreen !== "files") location.hash = "files";
      setTimeout(function() { var si = $("#fileSearchInput"); if (si) si.focus(); }, 100);
      return;
    }
    if (e.key === "j" || e.key === "k") {
      var rows = $$("#screen-" + currentScreen + " tbody tr");
      if (!rows.length) return;
      var idx = selectedIndex[currentScreen] || 0;
      if (e.key === "j") idx = Math.min(idx + 1, rows.length - 1);
      if (e.key === "k") idx = Math.max(idx - 1, 0);
      selectedIndex[currentScreen] = idx;
      rows.forEach(function(r, i) { r.classList.toggle("kbd-selected", i === idx); });
      rows[idx].scrollIntoView({block:"nearest"});
      e.preventDefault();
      return;
    }
    if (e.key === "Enter") {
      var rows = $$("#screen-" + currentScreen + " tbody tr.kbd-selected");
      if (rows.length) rows[0].click();
      return;
    }
  });
  $("#kbdHint").onclick = function() { $("#kbdOverlay").classList.toggle("open"); };
  $("#kbdOverlay").onclick = function(e) { if (e.target === this) this.classList.remove("open"); };

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
          showProgress(msg);
        } else if (msg.type === "error") {
          setStatus("disconnected", "error");
          hideProgress();
        }
      } catch(err) { console.error("ws parse:", err); }
    };
    ws.onclose = function() {
      setStatus("disconnected", "");
      $("#reconnectBanner").classList.add("active");
      setTimeout(function() { retryDelay = Math.min(retryDelay * 1.5, 15000); connect(); }, retryDelay);
    };
    ws.onerror = function() { setStatus("disconnected", ""); };
  }

  function setStatus(cls, text) {
    $("#statusDot").className = "status-indicator " + cls;
    $("#statusText").textContent = text;
  }

  function showProgress(msg) {
    var bar = $("#progressBar");
    var fill = $("#progressFill");
    var pt = $("#progressText");
    bar.classList.add("active");
    if (msg.percent != null) {
      fill.style.animation = "none";
      fill.style.width = (msg.percent * 100) + "%";
      pt.textContent = Math.round(msg.percent * 100) + "%";
      pt.classList.add("active");
    } else {
      fill.style.animation = "";
      fill.style.width = "";
      pt.textContent = "";
      pt.classList.remove("active");
    }
  }

  function hideProgress() {
    $("#progressBar").classList.remove("active");
    var pt = $("#progressText");
    pt.textContent = "";
    pt.classList.remove("active");
  }

  fetch("/api/state").then(function(r) { return r.json(); }).then(function(data) {
    if (data && data.health != null) { DATA = data; render(); }
  }).catch(function() {});

  connect();

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
