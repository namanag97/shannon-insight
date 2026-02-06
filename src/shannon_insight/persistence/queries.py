"""History query helpers — trend, health, and persistent-finding queries.

These operate on the history.db created by the storage layer and provide
the data needed for the ``trend`` and ``health`` CLI commands.
"""

import json
import sqlite3
from dataclasses import dataclass
from typing import Dict, List, Optional


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
    metrics: Dict[str, float]


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

    def file_trend(self, filepath: str, metric: str, last_n: int = 20) -> List[TrendPoint]:
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

    def codebase_health(self, last_n: int = 20) -> List[HealthPoint]:
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
        finding_counts: Dict[int, int] = {r["snapshot_id"]: r["cnt"] for r in finding_rows}

        # 4. Group signals by snapshot.
        snap_metrics: Dict[int, Dict[str, float]] = {}
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
        result: List[HealthPoint] = []
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

    def persistent_findings(self, min_snapshots: int = 3) -> List[Dict]:
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
        snap_id_to_idx: Dict[int, int] = {sid: i for i, sid in enumerate(all_snap_ids)}

        result: List[Dict] = []
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

    def top_movers(self, last_n: int = 5, metric: str = "cognitive_load") -> List[Dict]:
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
        old_vals: Dict[str, float] = dict(
            self.conn.execute(
                """
                SELECT file_path, value FROM file_signals
                WHERE snapshot_id = ? AND signal_name = ?
                """,
                (oldest_id, metric),
            ).fetchall()
        )

        new_vals: Dict[str, float] = dict(
            self.conn.execute(
                """
                SELECT file_path, value FROM file_signals
                WHERE snapshot_id = ? AND signal_name = ?
                """,
                (newest_id, metric),
            ).fetchall()
        )

        # Compute deltas for files present in both snapshots.
        movers: List[Dict] = []
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


def _max_consecutive_run(indices: List[int]) -> int:
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
