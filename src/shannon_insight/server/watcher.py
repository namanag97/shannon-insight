"""Debounced file watcher that re-runs analysis on source changes."""

from __future__ import annotations

import logging
import threading
from pathlib import Path

from ..config import AnalysisSettings
from ..insights.kernel import InsightKernel
from .api import build_dashboard_state
from .state import ServerState

logger = logging.getLogger(__name__)

# Extensions to watch for changes
WATCHED_EXTENSIONS = frozenset(
    {
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
    }
)

# Debounce: wait this long after last change before re-analyzing
DEBOUNCE_SECONDS = 2.0

# Cooldown: minimum gap between analysis runs
COOLDOWN_SECONDS = 1.0


class FileWatcher:
    """Watches source files and triggers re-analysis on changes.

    Uses ``watchfiles`` (Rust-backed) for efficient file monitoring.
    Runs the kernel in a background thread to avoid blocking the ASGI server.
    """

    def __init__(
        self,
        root_dir: str,
        settings: AnalysisSettings,
        state: ServerState,
        max_findings: int = 50,
    ) -> None:
        self.root_dir = str(Path(root_dir).resolve())
        self.settings = settings
        self.state = state
        self.max_findings = max_findings

        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._analyzing = False

    def start(self) -> None:
        """Start the watcher thread."""
        self._thread = threading.Thread(
            target=self._watch_loop,
            name="shannon-watcher",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        """Signal the watcher to stop."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5)

    def run_analysis(self) -> None:
        """Run one analysis cycle and update state.

        Can be called directly for the initial run.
        """
        self._analyzing = True
        try:
            self.state.send_progress("Scanning files...", phase="scan")

            kernel = InsightKernel(
                root_dir=self.root_dir,
                settings=self.settings,
            )

            def on_progress(msg: str) -> None:
                self.state.send_progress(msg, phase="analyze")

            result, snapshot = kernel.run(
                max_findings=self.max_findings,
                on_progress=on_progress,
            )

            dashboard_state = build_dashboard_state(result, snapshot)
            self.state.update(dashboard_state)

            logger.info(
                "Analysis complete: %d files, %d findings",
                snapshot.file_count,
                len(result.findings),
            )
        except Exception:
            logger.exception("Analysis failed")
            self.state.send_progress("Analysis failed", phase="error")
        finally:
            self._analyzing = False

    def _watch_loop(self) -> None:
        """Background thread: watch files, debounce changes, re-analyze."""
        try:
            from watchfiles import watch
        except ImportError:
            logger.error("watchfiles not installed; file watching disabled")
            return

        logger.info("Watching %s for changes", self.root_dir)

        for changes in watch(
            self.root_dir,
            stop_event=self._stop_event,
            debounce=int(DEBOUNCE_SECONDS * 1000),
            rust_timeout=5000,
            watch_filter=_SourceFilter(),
        ):
            if self._stop_event.is_set():
                break

            if self._analyzing:
                logger.debug("Skipping changes during active analysis")
                continue

            changed_files = [path for _change, path in changes]
            logger.info(
                "Detected %d changed file(s), re-analyzing...",
                len(changed_files),
            )

            self.run_analysis()

            # Cooldown to avoid rapid re-triggers
            if not self._stop_event.wait(COOLDOWN_SECONDS):
                pass  # Normal: timeout expired, continue watching


class _SourceFilter:
    """watchfiles filter: only watch source code files, ignore common noise."""

    def __call__(self, change: int, path: str) -> bool:
        p = Path(path)

        # Skip hidden directories and common noise
        parts = p.parts
        for part in parts:
            if part.startswith(".") or part in (
                "node_modules",
                "__pycache__",
                ".git",
                "venv",
                ".venv",
                "env",
                ".env",
                "dist",
                "build",
                ".tox",
                ".mypy_cache",
                ".pytest_cache",
                ".ruff_cache",
                ".shannon",
            ):
                return False

        # Only watch known source extensions
        return p.suffix in WATCHED_EXTENSIONS
