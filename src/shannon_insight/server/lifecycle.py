"""Server lifecycle management — startup, running, and graceful shutdown.

Coordinates:
- Signal handling (SIGINT, SIGTERM)
- Resource cleanup (WebSocket, watcher, PID file, threads)
- Rich terminal status display
- Graceful shutdown with timeout
"""

from __future__ import annotations

import atexit
import logging
import os
import signal
import threading
import webbrowser
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .process import (
    check_port_ownership,
    find_available_port,
    remove_pid_file,
    validate_existing_server,
    write_pid_file,
)
from .state import ServerState

logger = logging.getLogger(__name__)


class ShutdownManager:
    """Coordinates graceful shutdown of all server resources.

    Ensures cleanup happens exactly once, even if called from
    multiple signal handlers or atexit.
    """

    def __init__(
        self,
        project_root: str,
        console: Console,
    ) -> None:
        self.project_root = project_root
        self.console = console

        self._shutdown_lock = threading.Lock()
        self._shutdown_complete = False
        self._watcher: Any = None
        self._state: ServerState | None = None
        self._uvicorn_server: Any = None

    def register_watcher(self, watcher: Any) -> None:
        """Register the file watcher for cleanup."""
        self._watcher = watcher

    def register_state(self, state: ServerState) -> None:
        """Register the server state for cleanup."""
        self._state = state

    def register_uvicorn(self, server: Any) -> None:
        """Register the uvicorn server for shutdown."""
        self._uvicorn_server = server

    def shutdown(self) -> None:
        """Perform full shutdown. Safe to call multiple times."""
        with self._shutdown_lock:
            if self._shutdown_complete:
                return
            self._shutdown_complete = True

        self.console.print()  # Newline after ^C

        steps = []

        # 1. Close WebSocket connections
        if self._state is not None:
            with self._state._lock:
                listener_count = len(self._state._listeners)
            if listener_count > 0:
                self._state._listeners.clear()
                steps.append(
                    f"Closed WebSocket connections ({listener_count} client{'s' if listener_count != 1 else ''})"
                )
            else:
                steps.append("No active WebSocket connections")

        # 2. Stop file watcher
        if self._watcher is not None:
            self._watcher.stop()
            steps.append("Stopped file watcher thread")

        # 3. Signal uvicorn to stop
        if self._uvicorn_server is not None:
            self._uvicorn_server.should_exit = True
            steps.append("Signaled uvicorn to stop")

        # 4. Clean up PID file
        if remove_pid_file(self.project_root):
            steps.append("Cleaned up PID file")

        # 5. Clean up browser session marker (allows new tab on next start)
        browser_marker = Path(self.project_root) / ".shannon" / ".browser_session"
        try:
            if browser_marker.exists():
                browser_marker.unlink()
                steps.append("Cleared browser session marker")
        except OSError:
            pass

        # 6. Report active threads
        active = threading.active_count()
        if active > 1:
            thread_names = [
                t.name for t in threading.enumerate() if t != threading.current_thread()
            ]
            logger.debug("Active threads at shutdown: %s", thread_names)

        # Print shutdown summary
        for step in steps:
            self.console.print(f"  [green]OK[/green] {step}")

        self.console.print("  [green]OK[/green] Server stopped cleanly")
        self.console.print()


def _format_status_display(
    project_root: str,
    port: int,
    host: str,
    state: ServerState,
    recent_events: list[str],
) -> Panel:
    """Build the Rich panel showing live server status."""
    table = Table(show_header=False, show_edge=False, box=None, padding=(0, 1))
    table.add_column("key", style="bold", width=14)
    table.add_column("value")

    url = f"http://{host}:{port}"

    # Status
    table.add_row("Status:", "[green]Running[/green]")
    table.add_row("Project:", project_root)
    table.add_row("Port:", str(port))

    # Health and issues from current state
    current = state.get_state()
    if current is not None:
        health = current.get("health", "?")
        health_label = current.get("health_label", "")
        total_findings = sum(c["count"] for c in current.get("categories", {}).values())
        table.add_row("Health:", f"{health} ({health_label})")
        table.add_row("Issues:", f"{total_findings} findings")
    else:
        table.add_row("Health:", "[dim]analyzing...[/dim]")

    table.add_row("Dashboard:", f"[link={url}]{url}[/link]")

    # Add recent events
    if recent_events:
        table.add_row("", "")
        for event in recent_events[-5:]:  # Show last 5 events
            table.add_row("", f"[dim]{event}[/dim]")

    return Panel(
        table,
        title="[bold]Shannon Insight Server[/bold]",
        border_style="cyan",
    )


def launch_server(
    root_dir: str,
    settings,
    console: Console,
    host: str = "127.0.0.1",
    port: int = 8765,
    no_browser: bool = False,
    verbose: bool = False,
) -> None:
    """Full server lifecycle: startup, serve, shutdown.

    This is the main entry point for the server. It:
    1. Checks for existing servers (same/different project)
    2. Finds an available port
    3. Runs initial analysis
    4. Starts the ASGI server
    5. Handles shutdown gracefully
    """
    import uvicorn

    from .app import create_app
    from .watcher import FileWatcher

    project_root = str(Path(root_dir).resolve())

    # ── Step 1: Check for existing server ─────────────────────────
    existing = validate_existing_server(project_root, host)
    if existing is not None:
        # Server already running for THIS project - just show URL, don't open browser
        # (avoids opening new tabs on every reconnect)
        url = f"http://{host}:{existing.port}"
        console.print(
            f"[bold]Dashboard[/bold] -> [link={url}]{url}[/link] [dim](already running, PID {existing.pid})[/dim]"
        )
        console.print("[dim]Tip: Server is already running. Navigate to the URL above.[/dim]")
        return

    # ── Step 2: Find available port ───────────────────────────────
    ownership = check_port_ownership(host, port, project_root)

    if ownership == "available":
        actual_port = port
    elif ownership == "same_project":
        # Should have been caught above, but handle gracefully
        actual_port = port
    else:
        # Port in use by something else - find next available
        try:
            actual_port = find_available_port(host, port, project_root=project_root)
            if actual_port != port:
                console.print(f"[yellow]Port {port} in use, using {actual_port} instead[/yellow]")
        except RuntimeError as exc:
            console.print(f"[red]{exc}[/red]")
            return

    # ── Step 3: Setup shutdown manager ────────────────────────────
    shutdown_mgr = ShutdownManager(project_root, console)

    # ── Step 4: Create state and watcher ──────────────────────────
    state = ServerState()
    watcher = FileWatcher(root_dir=project_root, settings=settings, state=state)
    shutdown_mgr.register_watcher(watcher)
    shutdown_mgr.register_state(state)

    # ── Step 5: Write PID file ────────────────────────────────────
    try:
        write_pid_file(project_root, actual_port)
    except OSError as exc:
        console.print(f"[yellow]Warning: Could not write PID file: {exc}[/yellow]")

    # Register atexit cleanup as safety net (catches kill -9 aftermath on next run)
    atexit.register(lambda: _atexit_cleanup(project_root))

    # ── Step 6: Run initial analysis ──────────────────────────────
    console.print(f"[bold]Analyzing[/bold] {project_root}")
    with console.status("[cyan]Running initial analysis..."):
        watcher.run_analysis()

    initial = state.get_state()
    if initial:
        health = initial.get("health", "?")
        health_label = initial.get("health_label", "")
        n_issues = sum(c["count"] for c in initial.get("categories", {}).values())
        console.print(
            f"[green]Ready[/green] -- health {health} ({health_label}), {n_issues} issue(s)"
        )
    else:
        console.print("[yellow]Analysis produced no results[/yellow]")

    # ── Step 7: Start file watcher ────────────────────────────────
    watcher.start()

    # ── Step 8: Open browser ──────────────────────────────────────
    url = f"http://{host}:{actual_port}"
    if not no_browser:
        # Check if browser was already opened for this URL this session
        # This prevents duplicate tabs when server restarts quickly
        browser_marker = Path(project_root) / ".shannon" / ".browser_session"
        should_open = True
        try:
            if browser_marker.exists():
                marker_url = browser_marker.read_text().strip()
                if marker_url == url:
                    # Same URL already opened - browser tab likely still exists
                    should_open = False
                    logger.debug("Browser already opened for %s, skipping", url)
        except OSError:
            pass

        if should_open:
            # Write marker before opening (in case open() blocks)
            try:
                browser_marker.parent.mkdir(parents=True, exist_ok=True)
                browser_marker.write_text(url)
            except OSError:
                pass
            threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    # ── Step 9: Display status ────────────────────────────────────
    console.print()
    console.print(f"[bold]Dashboard[/bold] -> [link={url}]{url}[/link]")
    console.print(f"[dim]Project:  {project_root}[/dim]")
    console.print(f"[dim]PID:      {os.getpid()}[/dim]")
    console.print("[dim]Watching for changes... (Ctrl+C to stop)[/dim]")
    console.print()

    # ── Step 10: Start ASGI server ────────────────────────────────
    asgi_app = create_app(state)

    config = uvicorn.Config(
        asgi_app,
        host=host,
        port=actual_port,
        log_level="warning" if not verbose else "info",
    )
    server = uvicorn.Server(config)
    shutdown_mgr.register_uvicorn(server)

    # Install signal handlers BEFORE server.run()
    # uvicorn installs its own, but we want to intercept first
    _original_sigint = signal.getsignal(signal.SIGINT)
    _original_sigterm = signal.getsignal(signal.SIGTERM)

    def _signal_handler(signum, frame):
        """Handle SIGINT/SIGTERM for graceful shutdown."""
        sig_name = "SIGINT" if signum == signal.SIGINT else "SIGTERM"
        logger.info("Received %s, initiating shutdown...", sig_name)
        console.print(f"\n[yellow]Received {sig_name}, stopping server...[/yellow]")
        server.should_exit = True

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    try:
        server.run()
    except SystemExit:
        pass
    except Exception as exc:
        logger.exception("Server error: %s", exc)
        console.print(f"[red]Server error:[/red] {exc}")
    finally:
        # Restore original signal handlers
        try:
            signal.signal(signal.SIGINT, _original_sigint)
            signal.signal(signal.SIGTERM, _original_sigterm)
        except (OSError, ValueError):
            pass  # May fail if not in main thread

        shutdown_mgr.shutdown()


def _atexit_cleanup(project_root: str) -> None:
    """Safety-net cleanup registered with atexit.

    Handles the case where the process exits without going through
    the normal shutdown path (e.g. unhandled exception).
    """
    try:
        remove_pid_file(project_root)
    except Exception:
        pass  # Best effort - we're exiting anyway
