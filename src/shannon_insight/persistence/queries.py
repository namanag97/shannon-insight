"""History query helpers — trend, health, and persistent-finding queries.

These operate on the history.db created by the storage layer and provide
the data needed for the ``trend`` and ``health`` CLI commands.

V2 adds:
- get_signal_time_series(): query signal_history for a file/signal pair
- get_finding_history(): query finding_lifecycle for a finding's history
- get_chronic_findings(): query findings persisting 3+ snapshots
- update_finding_lifecycle(): update lifecycle state after a new snapshot
"""

import json
import sqlite3
from dataclasses import dataclass
from typing import Optional


@dataclass
class TrendPoint:
    """A single data point in a file-metric time series."""

    snapshot_id: int
    commit_sha: Optional[str]
    timestamp: str
    value: float


@dataclass
class HealthPoint:
    """A single codebase-level health snapshot."""

    snapshot_id: int
    timestamp: str
    metrics: dict[str, float]


class HistoryQuery:
    """Read-only queries against the history database.

    Parameters
    ----------
    conn:
        An open ``sqlite3.Connection`` with ``row_factory = sqlite3.Row``
        (as returned by ``HistoryDB.connect()``).
    """

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    # ── file-level trend ──────────────────────────────────────────────

    def file_trend(self, filepath: str, metric: str, last_n: int = 20) -> list[TrendPoint]:
        """Get the trend of *metric* for *filepath* over recent snapshots.

        Returns up to *last_n* points in **chronological** order (oldest
        first).
        """
        rows = self.conn.execute(
            """
            SELECT s.id, s.commit_sha, s.timestamp, fs.value
            FROM file_signals fs
            JOIN snapshots s ON s.id = fs.snapshot_id
            WHERE fs.file_path = ? AND fs.signal_name = ?
            ORDER BY s.timestamp DESC
            LIMIT ?
            """,
            (filepath, metric, last_n),
        ).fetchall()

        # Reverse so the list is chronological (oldest -> newest).
        return [
            TrendPoint(
                snapshot_id=r["id"],
                commit_sha=r["commit_sha"],
                timestamp=r["timestamp"],
                value=r["value"],
            )
            for r in reversed(rows)
        ]

    # ── codebase health trend ─────────────────────────────────────────

    def codebase_health(self, last_n: int = 20) -> list[HealthPoint]:
        """Get codebase-level metric trends over the last *last_n* snapshots.

        Each ``HealthPoint`` contains all codebase signals for that
        snapshot plus an ``active_findings`` count.

        Returns points in chronological order (oldest first).
        """
        # 1. Fetch the last N snapshot ids (newest first).
        snap_rows = self.conn.execute(
            "SELECT id, timestamp FROM snapshots ORDER BY timestamp DESC LIMIT ?",
            (last_n,),
        ).fetchall()

        if not snap_rows:
            return []

        snap_ids = [r["id"] for r in snap_rows]
        placeholders = ",".join("?" * len(snap_ids))

        # 2. Fetch all codebase signals for those snapshots.
        sig_rows = self.conn.execute(
            f"""
            SELECT snapshot_id, signal_name, value
            FROM codebase_signals
            WHERE snapshot_id IN ({placeholders})
            """,
            snap_ids,
        ).fetchall()

        # 3. Count findings per snapshot.
        finding_rows = self.conn.execute(
            f"""
            SELECT snapshot_id, COUNT(*) AS cnt
            FROM findings
            WHERE snapshot_id IN ({placeholders})
            GROUP BY snapshot_id
            """,
            snap_ids,
        ).fetchall()
        finding_counts: dict[int, int] = {r["snapshot_id"]: r["cnt"] for r in finding_rows}

        # 4. Group signals by snapshot.
        snap_metrics: dict[int, dict[str, float]] = {}
        for r in sig_rows:
            sid = r["snapshot_id"]
            if sid not in snap_metrics:
                snap_metrics[sid] = {}
            snap_metrics[sid][r["signal_name"]] = r["value"]

        # Inject the finding count as a virtual metric.
        for sid in snap_ids:
            if sid not in snap_metrics:
                snap_metrics[sid] = {}
            snap_metrics[sid]["active_findings"] = float(finding_counts.get(sid, 0))

        # 5. Build HealthPoints in chronological order.
        result: list[HealthPoint] = []
        for r in reversed(snap_rows):
            sid = r["id"]
            result.append(
                HealthPoint(
                    snapshot_id=sid,
                    timestamp=r["timestamp"],
                    metrics=snap_metrics.get(sid, {}),
                )
            )
        return result

    # ── persistent findings ───────────────────────────────────────────

    def persistent_findings(self, min_snapshots: int = 3) -> list[dict]:
        """Find findings that appear in *min_snapshots*+ **consecutive** snapshots.

        Returns a list of dicts with keys: ``identity_key``,
        ``finding_type``, ``title``, ``files``, ``severity``, ``count``.
        Ordered by descending persistence count.
        """
        rows = self.conn.execute(
            """
            SELECT f.identity_key, f.finding_type, f.title, f.files,
                   f.severity,
                   GROUP_CONCAT(f.snapshot_id) AS snap_ids,
                   COUNT(DISTINCT f.snapshot_id) AS appearance_count
            FROM findings f
            GROUP BY f.identity_key, f.finding_type
            HAVING COUNT(DISTINCT f.snapshot_id) >= ?
            ORDER BY appearance_count DESC
            """,
            (min_snapshots,),
        ).fetchall()

        # Build an ordered index of all snapshot ids so we can check
        # consecutiveness.
        all_snap_ids = [
            r["id"]
            for r in self.conn.execute("SELECT id FROM snapshots ORDER BY timestamp ASC").fetchall()
        ]
        snap_id_to_idx: dict[int, int] = {sid: i for i, sid in enumerate(all_snap_ids)}

        result: list[dict] = []
        for r in rows:
            snap_ids = sorted(int(s) for s in r["snap_ids"].split(","))
            indices = sorted(snap_id_to_idx.get(s, -1) for s in snap_ids)
            max_consecutive = _max_consecutive_run(indices)

            if max_consecutive >= min_snapshots:
                files = json.loads(r["files"])
                result.append(
                    {
                        "identity_key": r["identity_key"],
                        "finding_type": r["finding_type"],
                        "title": r["title"],
                        "files": files,
                        "severity": r["severity"],
                        "count": max_consecutive,
                    }
                )
        return result

    # ── top movers ────────────────────────────────────────────────────

    def top_movers(self, last_n: int = 5, metric: str = "cognitive_load") -> list[dict]:
        """Files with the largest *metric* changes over recent snapshots.

        Compares the oldest and newest of the last *last_n* snapshots and
        returns up to 10 files sorted by absolute delta.
        """
        snap_rows = self.conn.execute(
            "SELECT id, timestamp FROM snapshots ORDER BY timestamp DESC LIMIT ?",
            (last_n,),
        ).fetchall()

        if len(snap_rows) < 2:
            return []

        newest_id = snap_rows[0]["id"]
        oldest_id = snap_rows[-1]["id"]

        # Fetch metric values at both ends.
        old_vals: dict[str, float] = dict(
            self.conn.execute(
                """
                SELECT file_path, value FROM file_signals
                WHERE snapshot_id = ? AND signal_name = ?
                """,
                (oldest_id, metric),
            ).fetchall()
        )

        new_vals: dict[str, float] = dict(
            self.conn.execute(
                """
                SELECT file_path, value FROM file_signals
                WHERE snapshot_id = ? AND signal_name = ?
                """,
                (newest_id, metric),
            ).fetchall()
        )

        # Compute deltas for files present in both snapshots.
        movers: list[dict] = []
        for fp in set(old_vals) | set(new_vals):
            if fp in old_vals and fp in new_vals:
                delta = new_vals[fp] - old_vals[fp]
                movers.append(
                    {
                        "filepath": fp,
                        "old_value": old_vals[fp],
                        "new_value": new_vals[fp],
                        "delta": delta,
                        "abs_delta": abs(delta),
                    }
                )

        movers.sort(key=lambda x: x["abs_delta"], reverse=True)
        return movers[:10]


# ── Utility ──────────────────────────────────────────────────────────────


def _max_consecutive_run(indices: list[int]) -> int:
    """Return the length of the longest run of consecutive integers."""
    if not indices:
        return 0
    max_run = 1
    current_run = 1
    for i in range(1, len(indices)):
        if indices[i] == indices[i - 1] + 1:
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 1
    return max_run


# ══════════════════════════════════════════════════════════════════════════
# V2 Query Functions (Phase 7)
# ══════════════════════════════════════════════════════════════════════════


@dataclass
class SignalTimePoint:
    """A single data point in a signal time series."""

    snapshot_id: int
    timestamp: str
    value: float
    percentile: Optional[float] = None


@dataclass
class FindingLifecycleInfo:
    """Lifecycle information for a finding."""

    identity_key: str
    finding_type: str
    first_seen_snapshot: int
    last_seen_snapshot: int
    persistence_count: int
    current_status: str  # "active" | "resolved"
    severity: float


@dataclass
class ChronicFindingInfo:
    """Extended lifecycle info for chronic findings, includes files and title."""

    identity_key: str
    finding_type: str
    first_seen_snapshot: int
    last_seen_snapshot: int
    persistence_count: int
    current_status: str
    severity: float
    files: list[str]  # Actual file paths from the most recent finding
    title: str  # Original finding title


def get_signal_time_series(
    conn: sqlite3.Connection,
    file_path: str,
    signal_name: str,
    limit: int = 20,
) -> list[SignalTimePoint]:
    """Return time series of a signal for a file.

    Queries signal_history table for (timestamp, value, percentile) pairs.

    Parameters
    ----------
    conn:
        Open database connection.
    file_path:
        The file path to query.
    signal_name:
        The signal name (e.g., "cognitive_load").
    limit:
        Maximum number of points to return (default 20).

    Returns
    -------
    list[SignalTimePoint]
        Points in chronological order (oldest first).
    """
    rows = conn.execute(
        """
        SELECT sh.snapshot_id, s.timestamp, sh.value, sh.percentile
        FROM signal_history sh
        JOIN snapshots s ON s.id = sh.snapshot_id
        WHERE sh.file_path = ? AND sh.signal_name = ?
        ORDER BY s.timestamp DESC
        LIMIT ?
        """,
        (file_path, signal_name, limit),
    ).fetchall()

    # Reverse for chronological order
    return [
        SignalTimePoint(
            snapshot_id=r["snapshot_id"],
            timestamp=r["timestamp"],
            value=r["value"],
            percentile=r["percentile"],
        )
        for r in reversed(rows)
    ]


def get_module_signal_time_series(
    conn: sqlite3.Connection,
    module_path: str,
    signal_name: str,
    limit: int = 20,
) -> list[SignalTimePoint]:
    """Return time series of a signal for a module.

    Parameters
    ----------
    conn:
        Open database connection.
    module_path:
        The module path to query.
    signal_name:
        The signal name (e.g., "cohesion").
    limit:
        Maximum number of points to return.

    Returns
    -------
    list[SignalTimePoint]
        Points in chronological order (oldest first).
    """
    rows = conn.execute(
        """
        SELECT msh.snapshot_id, s.timestamp, msh.value
        FROM module_signal_history msh
        JOIN snapshots s ON s.id = msh.snapshot_id
        WHERE msh.module_path = ? AND msh.signal_name = ?
        ORDER BY s.timestamp DESC
        LIMIT ?
        """,
        (module_path, signal_name, limit),
    ).fetchall()

    return [
        SignalTimePoint(
            snapshot_id=r["snapshot_id"],
            timestamp=r["timestamp"],
            value=r["value"],
        )
        for r in reversed(rows)
    ]


def get_global_signal_time_series(
    conn: sqlite3.Connection,
    signal_name: str,
    limit: int = 20,
) -> list[SignalTimePoint]:
    """Return time series of a global signal.

    Parameters
    ----------
    conn:
        Open database connection.
    signal_name:
        The signal name (e.g., "codebase_health").
    limit:
        Maximum number of points to return.

    Returns
    -------
    list[SignalTimePoint]
        Points in chronological order (oldest first).
    """
    rows = conn.execute(
        """
        SELECT gsh.snapshot_id, s.timestamp, gsh.value
        FROM global_signal_history gsh
        JOIN snapshots s ON s.id = gsh.snapshot_id
        WHERE gsh.signal_name = ?
        ORDER BY s.timestamp DESC
        LIMIT ?
        """,
        (signal_name, limit),
    ).fetchall()

    return [
        SignalTimePoint(
            snapshot_id=r["snapshot_id"],
            timestamp=r["timestamp"],
            value=r["value"],
        )
        for r in reversed(rows)
    ]


def get_finding_history(
    conn: sqlite3.Connection,
    identity_key: str,
) -> Optional[FindingLifecycleInfo]:
    """Return lifecycle data for a finding.

    Parameters
    ----------
    conn:
        Open database connection.
    identity_key:
        The finding's identity key.

    Returns
    -------
    FindingLifecycleInfo or None
        Lifecycle data if found, None otherwise.
    """
    row = conn.execute(
        """
        SELECT identity_key, finding_type, first_seen_snapshot, last_seen_snapshot,
               persistence_count, current_status, severity
        FROM finding_lifecycle
        WHERE identity_key = ?
        """,
        (identity_key,),
    ).fetchone()

    if row is None:
        return None

    return FindingLifecycleInfo(
        identity_key=row["identity_key"],
        finding_type=row["finding_type"],
        first_seen_snapshot=row["first_seen_snapshot"],
        last_seen_snapshot=row["last_seen_snapshot"],
        persistence_count=row["persistence_count"],
        current_status=row["current_status"],
        severity=row["severity"],
    )


def get_chronic_findings(
    conn: sqlite3.Connection,
    min_persistence: int = 3,
    max_findings: int = 10,
) -> list[ChronicFindingInfo]:
    """Return findings persisting across min_persistence+ snapshots.

    Joins with findings table to get the actual files and title from the
    most recent occurrence of each chronic finding.

    Parameters
    ----------
    conn:
        Open database connection.
    min_persistence:
        Minimum number of snapshots a finding must persist (default 3).
    max_findings:
        Maximum number of findings to return (default 10).

    Returns
    -------
    list[ChronicFindingInfo]
        Chronic findings ordered by persistence count (descending),
        including file paths and title from the most recent snapshot.
    """
    # Join finding_lifecycle with findings to get files and title
    # Use last_seen_snapshot to get the most recent occurrence
    rows = conn.execute(
        """
        SELECT fl.identity_key, fl.finding_type, fl.first_seen_snapshot,
               fl.last_seen_snapshot, fl.persistence_count, fl.current_status,
               fl.severity, f.files, f.title
        FROM finding_lifecycle fl
        JOIN findings f ON f.identity_key = fl.identity_key
                       AND f.snapshot_id = fl.last_seen_snapshot
        WHERE fl.persistence_count >= ? AND fl.current_status = 'active'
        ORDER BY fl.persistence_count DESC, fl.severity DESC
        LIMIT ?
        """,
        (min_persistence, max_findings),
    ).fetchall()

    result = []
    for r in rows:
        # Parse files JSON
        files_raw = r["files"]
        if isinstance(files_raw, str):
            files = json.loads(files_raw)
        else:
            files = list(files_raw) if files_raw else []

        result.append(
            ChronicFindingInfo(
                identity_key=r["identity_key"],
                finding_type=r["finding_type"],
                first_seen_snapshot=r["first_seen_snapshot"],
                last_seen_snapshot=r["last_seen_snapshot"],
                persistence_count=r["persistence_count"],
                current_status=r["current_status"],
                severity=r["severity"],
                files=files,
                title=r["title"],
            )
        )
    return result


def update_finding_lifecycle(
    conn: sqlite3.Connection,
    identity_key: str,
    finding_type: str,
    severity: float,
    snapshot_id: int,
    is_present: bool,
) -> None:
    """Update finding lifecycle state after a new snapshot.

    Parameters
    ----------
    conn:
        Open database connection.
    identity_key:
        The finding's identity key.
    finding_type:
        The finding type (e.g., "high_risk_hub").
    severity:
        Current severity value.
    snapshot_id:
        The current snapshot ID.
    is_present:
        True if finding is in current snapshot, False if resolved.
    """
    existing = conn.execute(
        "SELECT * FROM finding_lifecycle WHERE identity_key = ?",
        (identity_key,),
    ).fetchone()

    if existing is None:
        if is_present:
            # New finding
            conn.execute(
                """
                INSERT INTO finding_lifecycle
                    (identity_key, first_seen_snapshot, last_seen_snapshot,
                     persistence_count, current_status, finding_type, severity)
                VALUES (?, ?, ?, 1, 'active', ?, ?)
                """,
                (identity_key, snapshot_id, snapshot_id, finding_type, severity),
            )
    else:
        if is_present:
            # Persisting or regression
            conn.execute(
                """
                UPDATE finding_lifecycle
                SET last_seen_snapshot = ?,
                    persistence_count = persistence_count + 1,
                    current_status = 'active',
                    severity = ?
                WHERE identity_key = ?
                """,
                (snapshot_id, severity, identity_key),
            )
        else:
            # Resolved
            conn.execute(
                """
                UPDATE finding_lifecycle
                SET current_status = 'resolved'
                WHERE identity_key = ?
                """,
                (identity_key,),
            )


def get_finding_lifecycle_map(conn: sqlite3.Connection) -> dict[str, dict]:
    """Return a dict of all finding lifecycle data for diff operations.

    Returns
    -------
    dict[str, dict]
        Mapping of identity_key -> lifecycle data dict.
    """
    rows = conn.execute(
        """
        SELECT identity_key, finding_type, first_seen_snapshot, last_seen_snapshot,
               persistence_count, current_status, severity
        FROM finding_lifecycle
        """
    ).fetchall()

    return {
        r["identity_key"]: {
            "finding_type": r["finding_type"],
            "first_seen_snapshot": r["first_seen_snapshot"],
            "last_seen_snapshot": r["last_seen_snapshot"],
            "persistence_count": r["persistence_count"],
            "current_status": r["current_status"],
            "severity": r["severity"],
        }
        for r in rows
    }
