"""SQLite-backed history database stored in .shannon/ at the project root."""

import sqlite3
from pathlib import Path
from typing import Optional

from ..logging_config import get_logger

logger = get_logger(__name__)

# Current schema version (bump when tables change).
_SCHEMA_VERSION = 1


class HistoryDB:
    """Manages the ``.shannon/history.db`` SQLite database.

    Usage::

        with HistoryDB("/path/to/project") as db:
            save_snapshot(db.conn, snapshot)
    """

    def __init__(self, project_root: str) -> None:
        self.db_dir: Path = Path(project_root) / ".shannon"
        self.db_path: Path = self.db_dir / "history.db"
        self._conn: Optional[sqlite3.Connection] = None

    @property
    def conn(self) -> sqlite3.Connection:
        """Return the active connection. Raises if not connected."""
        if self._conn is None:
            raise RuntimeError("HistoryDB is not connected. Use as context manager or call connect().")
        return self._conn

    # ── lifecycle ─────────────────────────────────────────────────

    def _ensure_dir(self) -> None:
        """Create .shannon/ and write a .gitignore so it stays untracked."""
        self.db_dir.mkdir(parents=True, exist_ok=True)
        gitignore = self.db_dir / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text("*\n")

    def connect(self) -> sqlite3.Connection:
        """Open (or create) the database and run migrations."""
        self._ensure_dir()
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.row_factory = sqlite3.Row
        self._conn = conn
        self._migrate()
        logger.debug("History DB connected at %s", self.db_path)
        return conn

    def close(self) -> None:
        """Close the connection if open."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "HistoryDB":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    # ── migration ─────────────────────────────────────────────────

    def _migrate(self) -> None:
        """Idempotently create / upgrade all tables."""
        c = self.conn

        # Schema version tracking table
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER NOT NULL
            )
            """
        )

        # Check current version
        row = c.execute("SELECT version FROM schema_version").fetchone()
        if row is None:
            c.execute(
                "INSERT INTO schema_version (version) VALUES (?)",
                (_SCHEMA_VERSION,),
            )

        # ── snapshots ────────────────────────────────────────────
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS snapshots (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                schema_version  INTEGER NOT NULL DEFAULT 1,
                tool_version    TEXT    NOT NULL,
                commit_sha      TEXT,
                timestamp       TEXT    NOT NULL,
                analyzed_path   TEXT    NOT NULL,
                file_count      INTEGER NOT NULL DEFAULT 0,
                module_count    INTEGER NOT NULL DEFAULT 0,
                commits_analyzed INTEGER NOT NULL DEFAULT 0,
                analyzers_ran   TEXT    NOT NULL DEFAULT '[]',
                config_hash     TEXT    NOT NULL DEFAULT ''
            )
            """
        )

        # ── file_signals ─────────────────────────────────────────
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS file_signals (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id INTEGER NOT NULL REFERENCES snapshots(id) ON DELETE CASCADE,
                file_path   TEXT    NOT NULL,
                signal_name TEXT    NOT NULL,
                value       REAL    NOT NULL
            )
            """
        )

        # ── codebase_signals ─────────────────────────────────────
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS codebase_signals (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id INTEGER NOT NULL REFERENCES snapshots(id) ON DELETE CASCADE,
                signal_name TEXT    NOT NULL,
                value       REAL    NOT NULL
            )
            """
        )

        # ── findings ─────────────────────────────────────────────
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS findings (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id  INTEGER NOT NULL REFERENCES snapshots(id) ON DELETE CASCADE,
                finding_type TEXT    NOT NULL,
                identity_key TEXT    NOT NULL,
                severity     REAL    NOT NULL,
                title        TEXT    NOT NULL,
                files        TEXT    NOT NULL DEFAULT '[]',
                evidence     TEXT    NOT NULL DEFAULT '[]',
                suggestion   TEXT    NOT NULL DEFAULT ''
            )
            """
        )

        # ── dependency_edges ─────────────────────────────────────
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS dependency_edges (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id INTEGER NOT NULL REFERENCES snapshots(id) ON DELETE CASCADE,
                src         TEXT    NOT NULL,
                dst         TEXT    NOT NULL
            )
            """
        )

        # ── baseline ──────────────────────────────────────────────
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS baseline (
                id          INTEGER PRIMARY KEY CHECK (id = 1),
                snapshot_id INTEGER NOT NULL REFERENCES snapshots(id)
            )
            """
        )

        # ── indexes ──────────────────────────────────────────────
        c.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_commit ON snapshots(commit_sha)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp ON snapshots(timestamp)")
        c.execute(
            "CREATE INDEX IF NOT EXISTS idx_file_signals_snapshot ON file_signals(snapshot_id)"
        )
        c.execute(
            "CREATE INDEX IF NOT EXISTS idx_file_signals_path ON file_signals(snapshot_id, file_path)"
        )
        c.execute(
            "CREATE INDEX IF NOT EXISTS idx_codebase_signals_snapshot ON codebase_signals(snapshot_id)"
        )
        c.execute("CREATE INDEX IF NOT EXISTS idx_findings_snapshot ON findings(snapshot_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_findings_identity ON findings(identity_key)")
        c.execute(
            "CREATE INDEX IF NOT EXISTS idx_dependency_edges_snapshot ON dependency_edges(snapshot_id)"
        )

        c.commit()

    # ── baseline management ────────────────────────────────────────

    def set_baseline(self, snapshot_id: int) -> None:
        """Set (or replace) the baseline snapshot.

        The baseline table uses ``id = 1`` with a CHECK constraint so there
        can only ever be a single row.

        Parameters
        ----------
        snapshot_id:
            The ``snapshots.id`` to pin as baseline.

        Raises
        ------
        ValueError
            If no snapshot with the given id exists.
        """
        # Verify the snapshot exists
        row = self.conn.execute("SELECT id FROM snapshots WHERE id = ?", (snapshot_id,)).fetchone()
        if row is None:
            raise ValueError(f"No snapshot with id={snapshot_id}")

        self.conn.execute(
            "INSERT OR REPLACE INTO baseline (id, snapshot_id) VALUES (1, ?)",
            (snapshot_id,),
        )
        self.conn.commit()
        logger.info("Baseline set to snapshot %d", snapshot_id)

    def get_baseline_snapshot_id(self) -> Optional[int]:
        """Return the baseline snapshot id, or ``None`` if unset."""
        row = self.conn.execute("SELECT snapshot_id FROM baseline WHERE id = 1").fetchone()
        if row is None:
            return None
        return int(row["snapshot_id"])

    def clear_baseline(self) -> None:
        """Remove the baseline if one is set."""
        self.conn.execute("DELETE FROM baseline")
        self.conn.commit()
        logger.info("Baseline cleared")
