"""File watcher for live dashboard updates.

Watches for file changes and re-runs analysis using the api.analyze() function.
Pushes updates to connected WebSocket clients via ServerState.
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .state import ServerState

logger = logging.getLogger(__name__)


class FileWatcher:
    """Watches for file changes and triggers re-analysis.

    Uses polling (not inotify/fsevents) for cross-platform compatibility.
    Analysis runs in a background thread to not block the main server.
    """

    def __init__(
        self,
        root_dir: str,
        settings: Any,
        state: ServerState,
        poll_interval: float = 2.0,
    ) -> None:
        self.root_dir = str(Path(root_dir).resolve())
        self.settings = settings
        self.state = state
        self.poll_interval = poll_interval

        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._last_mtime: dict[str, float] = {}
        self._analyzing = False

    def start(self) -> None:
        """Start the file watcher thread."""
        if self._thread is not None and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()
        logger.info("File watcher started for %s", self.root_dir)

    def stop(self) -> None:
        """Stop the file watcher thread."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5.0)
            self._thread = None
        logger.info("File watcher stopped")

    def run_analysis(self) -> None:
        """Run analysis and update server state.

        This is the main analysis entry point. It uses api.analyze()
        which handles all the session/kernel setup correctly.
        """
        if self._analyzing:
            logger.debug("Analysis already in progress, skipping")
            return

        self._analyzing = True
        try:
            self.state.send_progress("Analyzing...", phase="analyze", percent=0.1)

            from ..api import analyze

            result, snapshot = analyze(
                path=self.root_dir,
                verbose=False,
                max_findings=100,
            )

            # Convert to dashboard state format
            dashboard_state = self._build_dashboard_state(result, snapshot)
            self.state.update(dashboard_state)
            self.state.send_progress("Complete", phase="done", percent=1.0)

            logger.info(
                "Analysis complete: %d files, %d findings",
                snapshot.file_count,
                len(result.findings),
            )

        except Exception as e:
            logger.exception("Analysis failed: %s", e)
            self.state.send_progress(f"Error: {e}", phase="error", percent=0.0)
        finally:
            self._analyzing = False

    def _watch_loop(self) -> None:
        """Main watch loop - polls for file changes."""
        while not self._stop_event.is_set():
            try:
                changed = self._check_for_changes()
                if changed:
                    logger.info("Files changed, re-analyzing...")
                    self.state.set_recent_changes(changed)
                    self.run_analysis()
            except Exception as e:
                logger.error("Watch loop error: %s", e)

            self._stop_event.wait(self.poll_interval)

    def _check_for_changes(self) -> list[str]:
        """Check for file modifications since last check."""
        changed: list[str] = []
        root = Path(self.root_dir)

        # Get current mtimes
        current_mtimes: dict[str, float] = {}
        try:
            for p in root.rglob("*"):
                if not p.is_file():
                    continue
                # Skip common non-source directories
                if any(
                    part in {".git", "node_modules", "__pycache__", ".venv", "venv"}
                    for part in p.parts
                ):
                    continue
                # Only watch source files
                if p.suffix.lower() not in {
                    ".py",
                    ".go",
                    ".ts",
                    ".tsx",
                    ".js",
                    ".jsx",
                    ".java",
                    ".rs",
                    ".rb",
                    ".c",
                    ".cpp",
                    ".h",
                    ".hpp",
                }:
                    continue

                try:
                    rel_path = str(p.relative_to(root))
                    current_mtimes[rel_path] = p.stat().st_mtime
                except OSError:
                    continue

        except Exception as e:
            logger.debug("Error scanning for changes: %s", e)
            return []

        # Compare with last mtimes
        for path, mtime in current_mtimes.items():
            if path not in self._last_mtime:
                changed.append(path)  # New file
            elif mtime > self._last_mtime[path]:
                changed.append(path)  # Modified file

        # Check for deleted files
        for path in self._last_mtime:
            if path not in current_mtimes:
                changed.append(path)  # Deleted file

        self._last_mtime = current_mtimes
        return changed

    def _build_dashboard_state(self, result, snapshot) -> dict:
        """Convert analysis result to dashboard state format.

        Uses the canonical build_dashboard_state() from server/api.py
        to ensure consistent data transformation (health scores, percentiles,
        file signals, module signals, etc.).

        Also auto-saves snapshots to .shannon/history.db for trend data.
        """
        from .api import build_dashboard_state

        # Auto-save snapshot to history database for trend data
        # This ensures .shannon/ is created on first run and trends work
        db_path = None
        try:
            from ..persistence import HistoryDB
            from ..persistence.writer import save_snapshot

            with HistoryDB(self.root_dir) as db:
                save_snapshot(db.conn, snapshot)
                db_path = str(db.db_path)
            logger.debug("Saved snapshot to %s", db_path)
        except Exception as e:
            logger.debug("Could not save snapshot to history: %s", e)
            # Fall back to checking if db exists
            shannon_dir = Path(self.root_dir) / ".shannon"
            if shannon_dir.exists():
                history_db = shannon_dir / "history.db"
                if history_db.exists():
                    db_path = str(history_db)

        return build_dashboard_state(result, snapshot, db_path=db_path)
