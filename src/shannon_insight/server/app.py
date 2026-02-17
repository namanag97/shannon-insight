"""Starlette ASGI application for the live dashboard."""

from __future__ import annotations

import asyncio
import csv
import io
import json
import logging
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.routing import Mount, Route, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket, WebSocketDisconnect

from .state import ServerState

if TYPE_CHECKING:
    from .watcher import FileWatcher

from ..persistence.database import HistoryDB
from .serializers import DashboardSerializer

logger = logging.getLogger(__name__)

_PKG_DIR = Path(__file__).parent
_STATIC_DIR = _PKG_DIR / "static"
_TEMPLATE_DIR = _PKG_DIR / "templates"

# Cache template HTML at import time
_TEMPLATE_HTML: str | None = None


def _get_html() -> str:
    """Load the dashboard HTML template (cached after first read)."""
    global _TEMPLATE_HTML  # noqa: PLW0603
    if _TEMPLATE_HTML is None:
        _TEMPLATE_HTML = (_TEMPLATE_DIR / "index.html").read_text()
    return _TEMPLATE_HTML


def create_app(state: ServerState, watcher: FileWatcher | None = None) -> Starlette:
    """Build the Starlette application wired to *state*.

    Args:
        state: The shared server state for dashboard data
        watcher: Optional file watcher for triggering refresh
    """

    async def homepage(request: Request) -> HTMLResponse:
        return HTMLResponse(_get_html())

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
        queue: asyncio.Queue[Any] = asyncio.Queue(maxsize=32)
        state.add_listener(queue)
        ping_task = asyncio.create_task(_ping_loop(websocket))
        try:
            # Send current state immediately if available
            current = state.get_state()
            if current is not None:
                await websocket.send_json({"type": "complete", "state": current})

            while True:
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=60)
                except asyncio.TimeoutError:
                    # Send ping on timeout, keep connection alive
                    await websocket.send_json({"type": "ping"})
                    continue
                # All messages now have type wrapper (progress, complete, etc.)
                if isinstance(msg, dict) and "type" in msg:
                    await websocket.send_json(msg)
                else:
                    # Legacy fallback for raw state (shouldn't happen)
                    await websocket.send_json({"type": "complete", "state": msg})
        except (WebSocketDisconnect, asyncio.CancelledError):
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

    async def api_refresh(request: Request) -> JSONResponse:
        """Force a full re-analysis. POST /api/refresh"""
        if request.method != "POST":
            return JSONResponse(
                {"error": "Method not allowed. Use POST."},
                status_code=405,
            )
        if watcher is None:
            return JSONResponse(
                {"error": "Refresh not available (no watcher configured)"},
                status_code=503,
            )

        # Run analysis in background thread to not block the request
        def _do_refresh():
            try:
                watcher.run_analysis()
            except Exception as exc:
                logger.error("Refresh failed: %s", exc)

        threading.Thread(target=_do_refresh, daemon=True).start()
        return JSONResponse({"status": "refresh_started"})

    # ── History API endpoints ───────────────────────────────────────────

    def _get_analyzed_path() -> str | None:
        """Get analyzed path from current state."""
        current = state.get_state()
        if current is None:
            return None
        return current.get("analyzed_path")

    async def api_history_snapshots(request: Request) -> JSONResponse:
        """List historical snapshots with health scores."""
        analyzed_path = _get_analyzed_path()
        if not analyzed_path:
            return JSONResponse({"error": "No analysis available"}, status_code=404)
        limit = int(request.query_params.get("limit", 50))
        try:
            with HistoryDB(analyzed_path) as db:
                serializer = DashboardSerializer(db)
                data = serializer.serialize_snapshot_list(limit=limit)
            return JSONResponse(data)
        except Exception as e:
            logger.warning(f"History snapshots query failed: {e}")
            return JSONResponse({"error": "No history available"}, status_code=404)

    async def api_history_signal(request: Request) -> JSONResponse:
        """Get signal evolution over time."""
        signal_type = request.path_params["signal_type"]  # file, module, global
        signal_path = request.path_params.get("signal_path", "")
        signal_name = request.path_params["signal_name"]
        limit = int(request.query_params.get("limit", 50))

        # Handle URL-encoded paths
        from urllib.parse import unquote

        signal_path = unquote(signal_path)

        analyzed_path = _get_analyzed_path()
        if not analyzed_path:
            return JSONResponse({"error": "No analysis available"}, status_code=404)
        try:
            with HistoryDB(analyzed_path) as db:
                serializer = DashboardSerializer(db)
                data = serializer.serialize_signal_evolution(
                    entity_type=signal_type,
                    entity_path=signal_path,
                    signal_name=signal_name,
                    limit=limit,
                )
            return JSONResponse(data)
        except Exception as e:
            logger.warning(f"History signal query failed: {e}")
            return JSONResponse({"error": str(e)}, status_code=404)

    async def api_history_findings(request: Request) -> JSONResponse:
        """Get finding lifecycle summary."""
        analyzed_path = _get_analyzed_path()
        if not analyzed_path:
            return JSONResponse({"error": "No analysis available"}, status_code=404)
        limit = int(request.query_params.get("limit", 50))
        try:
            with HistoryDB(analyzed_path) as db:
                serializer = DashboardSerializer(db)
                data = serializer.serialize_finding_lifecycle(limit=limit)
            return JSONResponse(data)
        except Exception as e:
            logger.warning(f"History findings query failed: {e}")
            return JSONResponse({"error": "No history available"}, status_code=404)

    async def api_history_snapshot_detail(request: Request) -> JSONResponse:
        """Get full snapshot detail by ID."""
        snapshot_id = int(request.path_params["snapshot_id"])
        try:
            with HistoryDB(str(state.analyzed_path)) as db:
                serializer = DashboardSerializer(db)
                data = serializer.serialize_snapshot_detail(snapshot_id)
            if data is None:
                return JSONResponse({"error": "Snapshot not found"}, status_code=404)
            return JSONResponse(data)
        except Exception as e:
            logger.warning(f"History snapshot detail query failed: {e}")
            return JSONResponse({"error": str(e)}, status_code=404)

    routes = [
        Route("/", homepage),
        Route("/api/state", api_state),
        Route("/api/refresh", api_refresh, methods=["POST"]),
        Route("/api/export/json", api_export_json),
        Route("/api/export/csv", api_export_csv),
        Route("/api/gate", api_gate),
        # History API
        Route("/api/history/snapshots", api_history_snapshots),
        Route("/api/history/findings", api_history_findings),
        Route("/api/history/snapshot/{snapshot_id:int}", api_history_snapshot_detail),
        Route("/api/history/signal/{signal_type}/{signal_name}", api_history_signal),
        Route(
            "/api/history/signal/{signal_type}/{signal_path:path}/{signal_name}", api_history_signal
        ),
        WebSocketRoute("/ws", websocket_endpoint),
        Mount("/static", app=StaticFiles(directory=str(_STATIC_DIR)), name="static"),
    ]

    return Starlette(routes=routes)
