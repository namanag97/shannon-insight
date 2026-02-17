"""Session log management with automatic cleanup.

Manages session logs in `.shannon/logs/session_<timestamp>.json`. Provides:
    - Auto-cleanup on startup (delete logs older than retention period)
    - atexit handler for graceful cleanup
    - SIGTERM/SIGINT handlers for interrupted cleanup
    - Config-driven retention (`log_retention_hours`)

Usage:
    from shannon_insight.infrastructure.session_log import SessionLogManager

    manager = SessionLogManager(root="/path/to/project", retention_hours=24)
    manager.install_handlers()  # Register atexit + signal handlers

    # During analysis...
    log_path = manager.current_log_path

    # After analysis...
    manager.write_log(provenance_store)

    # On next startup, old logs are cleaned automatically.
"""

from __future__ import annotations

import atexit
import json
import logging
import signal as signal_module
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from shannon_insight.infrastructure.provenance import ProvenanceStore

logger = logging.getLogger(__name__)

# Default retention period
DEFAULT_RETENTION_HOURS = 24

# Log directory name under .shannon
LOG_DIR_NAME = "logs"


class SessionLogManager:
    """Manages session log files with automatic cleanup.

    Session logs are stored as JSON Lines files in `.shannon/logs/`.
    Old logs are automatically cleaned up based on retention policy.

    Attributes:
        root: Project root directory path.
        retention_hours: How long to keep logs (default: 24 hours).
        session_id: Unique identifier for this session (timestamp-based).
    """

    def __init__(
        self,
        root: str | Path,
        retention_hours: int = DEFAULT_RETENTION_HOURS,
    ) -> None:
        """Initialize session log manager.

        Args:
            root: Project root directory (where .shannon/ lives).
            retention_hours: Hours to retain logs before cleanup.
        """
        self.root = Path(root)
        self.retention_hours = retention_hours
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._log_dir = self.root / ".shannon" / LOG_DIR_NAME
        self._handlers_installed = False
        self._original_sigterm = None
        self._original_sigint = None
        self._cleanup_done = False

    @property
    def log_dir(self) -> Path:
        """Directory where session logs are stored."""
        return self._log_dir

    @property
    def current_log_path(self) -> Path:
        """Path for this session's log file."""
        return self._log_dir / f"session_{self.session_id}.jsonl"

    def ensure_log_dir(self) -> None:
        """Create the log directory if it doesn't exist."""
        self._log_dir.mkdir(parents=True, exist_ok=True)

    def cleanup_old_logs(self) -> int:
        """Delete session logs older than the retention period.

        Returns:
            Number of log files deleted.
        """
        if not self._log_dir.exists():
            return 0

        cutoff = datetime.now() - timedelta(hours=self.retention_hours)
        deleted = 0

        for log_file in self._log_dir.glob("session_*.jsonl"):
            try:
                # Parse timestamp from filename: session_YYYYMMDD_HHMMSS.jsonl
                stem = log_file.stem  # session_YYYYMMDD_HHMMSS
                ts_str = stem[len("session_") :]
                file_time = datetime.strptime(ts_str, "%Y%m%d_%H%M%S")

                if file_time < cutoff:
                    log_file.unlink()
                    deleted += 1
                    logger.debug(f"Cleaned up old session log: {log_file.name}")
            except (ValueError, OSError) as e:
                # Can't parse timestamp or can't delete - skip
                logger.debug(f"Skipping log cleanup for {log_file.name}: {e}")

        if deleted > 0:
            logger.debug(f"Cleaned up {deleted} old session log(s)")

        return deleted

    def write_log(self, provenance: ProvenanceStore) -> Path | None:
        """Write provenance records to the session log file.

        Args:
            provenance: ProvenanceStore with records to export.

        Returns:
            Path to the written log file, or None if no records to write.
        """
        if provenance.record_count == 0:
            return None

        self.ensure_log_dir()
        log_path = self.current_log_path

        provenance.export_session_log(str(log_path))
        logger.debug(f"Session log written: {log_path.name} ({provenance.record_count} records)")

        return log_path

    def install_handlers(self) -> None:
        """Install atexit and signal handlers for cleanup.

        Registers:
        - atexit handler for normal Python exit
        - SIGTERM handler for process termination
        - SIGINT handler for Ctrl+C (if not already handled)

        Safe to call multiple times (idempotent).
        """
        if self._handlers_installed:
            return

        # Register atexit handler
        atexit.register(self._atexit_cleanup)

        # Register signal handlers (save originals for chaining)
        try:
            self._original_sigterm = signal_module.signal(
                signal_module.SIGTERM, self._signal_cleanup
            )
        except (OSError, ValueError):
            # Can't set signal handler (e.g., not main thread)
            pass

        try:
            self._original_sigint = signal_module.signal(signal_module.SIGINT, self._signal_cleanup)
        except (OSError, ValueError):
            pass

        self._handlers_installed = True
        logger.debug("Session log cleanup handlers installed")

    def uninstall_handlers(self) -> None:
        """Remove signal handlers and atexit registration.

        Restores original signal handlers. Useful for testing.
        """
        if not self._handlers_installed:
            return

        # Restore original signal handlers
        try:
            if self._original_sigterm is not None:
                signal_module.signal(signal_module.SIGTERM, self._original_sigterm)
        except (OSError, ValueError):
            pass

        try:
            if self._original_sigint is not None:
                signal_module.signal(signal_module.SIGINT, self._original_sigint)
        except (OSError, ValueError):
            pass

        # Can't unregister atexit, but we track _cleanup_done
        self._handlers_installed = False

    def _atexit_cleanup(self) -> None:
        """Cleanup handler called on normal exit."""
        if self._cleanup_done:
            return
        self._cleanup_done = True

        try:
            self.cleanup_old_logs()
        except Exception:
            # Don't let cleanup errors prevent exit
            pass

    def _signal_cleanup(self, signum: int, frame: Any) -> None:
        """Cleanup handler called on SIGTERM/SIGINT."""
        if not self._cleanup_done:
            self._cleanup_done = True
            try:
                self.cleanup_old_logs()
            except Exception:
                pass

        # Chain to original handler
        if signum == signal_module.SIGTERM and self._original_sigterm:
            if callable(self._original_sigterm):
                self._original_sigterm(signum, frame)
        elif signum == signal_module.SIGINT and self._original_sigint:
            if callable(self._original_sigint):
                self._original_sigint(signum, frame)
            else:
                # Default SIGINT behavior: raise KeyboardInterrupt
                raise KeyboardInterrupt

    def list_logs(self) -> list[Path]:
        """List all session log files, newest first.

        Returns:
            List of Path objects for session log files.
        """
        if not self._log_dir.exists():
            return []

        logs = sorted(
            self._log_dir.glob("session_*.jsonl"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        return logs

    def read_log(self, log_path: Path) -> list[dict]:
        """Read a session log file.

        Args:
            log_path: Path to the JSON Lines log file.

        Returns:
            List of provenance record dicts.
        """
        records = []
        with open(log_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records
