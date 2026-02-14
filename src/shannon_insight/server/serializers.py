"""API serialization layer - transforms domain models to consistent frontend contract.

This module provides a single source of truth for:
1. Data scale transformations (0-1 → 1-10 for health, etc.)
2. Evolution metrics computation (files/LOC/complexity over time)
3. Analysis metadata (what was analyzed, performance stats)

All transformations happen HERE, not scattered across the codebase.
"""

from __future__ import annotations

import os
from typing import Any

from ..persistence.database import HistoryDB
from ..persistence.models import TensorSnapshot
from ..persistence.queries import HistoryQuery


class DashboardSerializer:
    """Transforms domain models to API contract with consistent scales.

    Transformation rules:
    - Health scores: ALWAYS 1-10 scale (multiply raw 0-1 values by 10)
    - Risk scores: ALWAYS 0-1 scale (percentile / 100)
    - Percentiles: ALWAYS 0-100 (not 0-1)
    - Counts: ALWAYS integers
    - Ratios: ALWAYS 0-1 (frontend formats as %)
    """

    def __init__(self, db: HistoryDB):
        self.db = db
        self.query = HistoryQuery(db.conn)

    def serialize_health(self, snapshot: TensorSnapshot) -> dict[str, Any]:
        """Serialize health data with CONSISTENT 1-10 scale everywhere.

        Returns:
            {
                "score": 7.2,           # ALWAYS 1-10 scale
                "label": "Moderate",
                "verdict": "...",
                "trend": [
                    {"timestamp": "...", "score": 7.1, "finding_count": 50},
                    ...
                ]
            }
        """
        raw_health = snapshot.global_signals.get("codebase_health", 0.5)
        display_health = raw_health * 10  # Transform to 1-10 scale

        # Get trend (also multiply by 10 for consistency)
        health_points = self.query.codebase_health(last_n=20)
        trend = []
        for hp in health_points:
            raw = hp.metrics.get("codebase_health", 0.5)
            trend.append(
                {
                    "timestamp": hp.timestamp,
                    "score": round(raw * 10, 1),  # ALWAYS 1-10 scale
                    "finding_count": int(hp.metrics.get("active_findings", 0)),
                }
            )

        return {
            "score": round(display_health, 1),
            "label": self._health_label(display_health),
            "trend": trend,
        }

    def serialize_evolution(self) -> dict[str, Any]:
        """Compute codebase evolution metrics from snapshot history.

        Returns:
            {
                "file_count": [(timestamp, count), ...],
                "module_count": [...],
                "total_loc": [...],
                "avg_complexity": [...],
                "avg_risk": [...],
                "commits_analyzed": [...],
            }
        """
        cur = self.db.conn.cursor()

        # File count over time
        rows = cur.execute(
            """
            SELECT timestamp, file_count
            FROM snapshots
            ORDER BY timestamp ASC
        """
        ).fetchall()
        file_count_trend = [{"timestamp": r["timestamp"], "value": r["file_count"]} for r in rows]

        # Module count over time
        rows = cur.execute(
            """
            SELECT timestamp, module_count
            FROM snapshots
            ORDER BY timestamp ASC
        """
        ).fetchall()
        module_count_trend = [
            {"timestamp": r["timestamp"], "value": r["module_count"]} for r in rows
        ]

        # Total LOC over time (sum of all files' lines per snapshot)
        rows = cur.execute(
            """
            SELECT s.timestamp, SUM(sh.value) as total_loc
            FROM snapshots s
            JOIN signal_history sh ON s.id = sh.snapshot_id
            WHERE sh.signal_name = 'lines'
            GROUP BY s.id
            ORDER BY s.timestamp ASC
        """
        ).fetchall()
        total_loc_trend = [
            {"timestamp": r["timestamp"], "value": int(r["total_loc"] or 0)} for r in rows
        ]

        # Average complexity over time
        rows = cur.execute(
            """
            SELECT s.timestamp, AVG(sh.value) as avg_complexity
            FROM snapshots s
            JOIN signal_history sh ON s.id = sh.snapshot_id
            WHERE sh.signal_name = 'cognitive_load'
            GROUP BY s.id
            ORDER BY s.timestamp ASC
        """
        ).fetchall()
        avg_complexity_trend = [
            {"timestamp": r["timestamp"], "value": round(r["avg_complexity"] or 0, 1)} for r in rows
        ]

        # Average risk over time
        rows = cur.execute(
            """
            SELECT s.timestamp, AVG(sh.value) as avg_risk
            FROM snapshots s
            JOIN signal_history sh ON s.id = sh.snapshot_id
            WHERE sh.signal_name = 'risk_score'
            GROUP BY s.id
            ORDER BY s.timestamp ASC
        """
        ).fetchall()
        avg_risk_trend = [
            {"timestamp": r["timestamp"], "value": round(r["avg_risk"] or 0, 3)} for r in rows
        ]

        # Commits analyzed per snapshot
        rows = cur.execute(
            """
            SELECT timestamp, commits_analyzed
            FROM snapshots
            ORDER BY timestamp ASC
        """
        ).fetchall()
        commits_trend = [
            {"timestamp": r["timestamp"], "value": r["commits_analyzed"]} for r in rows
        ]

        return {
            "file_count": file_count_trend,
            "module_count": module_count_trend,
            "total_loc": total_loc_trend,
            "avg_complexity": avg_complexity_trend,
            "avg_risk": avg_risk_trend,
            "commits_analyzed": commits_trend,
        }

    def serialize_metadata(self, snapshot: TensorSnapshot) -> dict[str, Any]:
        """Serialize analysis metadata - what was analyzed and performance.

        Returns:
            {
                "files_scanned": 260,
                "modules_detected": 56,
                "commits_processed": 432,
                "analyzers_ran": ["structural", "temporal", ...],
                "snapshot_count": 81,
                "db_size_mb": 15.3,
            }
        """
        cur = self.db.conn.cursor()

        # Count snapshots
        snapshot_count = cur.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]

        # DB size
        db_size_bytes = os.path.getsize(self.db.db_path)
        db_size_mb = db_size_bytes / (1024 * 1024)

        return {
            "files_scanned": snapshot.file_count,
            "modules_detected": snapshot.module_count,
            "commits_processed": snapshot.commits_analyzed,
            "analyzers_ran": snapshot.analyzers_ran or [],
            "snapshot_count": snapshot_count,
            "db_size_mb": round(db_size_mb, 2),
        }

    def serialize_top_movers(self, metric: str = "risk_score", limit: int = 10) -> list[dict]:
        """Files with biggest metric changes - COMPARE TO BASELINE.

        Compares latest snapshot to the FIRST snapshot (baseline), not last 5.
        This shows actual evolution, not noise.

        Args:
            metric: Signal name to track (risk_score, cognitive_load, etc.)
            limit: Number of top movers to return

        Returns:
            [
                {"path": "...", "old_value": 0.3, "new_value": 0.7, "delta": +0.4},
                ...
            ]
        """
        cur = self.db.conn.cursor()

        # Get baseline snapshot (first one)
        baseline_row = cur.execute(
            "SELECT id FROM snapshots ORDER BY timestamp ASC LIMIT 1"
        ).fetchone()
        if not baseline_row:
            return []
        baseline_id = baseline_row[0]

        # Get latest snapshot
        latest_row = cur.execute(
            "SELECT id FROM snapshots ORDER BY timestamp DESC LIMIT 1"
        ).fetchone()
        if not latest_row:
            return []
        latest_id = latest_row[0]

        # Don't compare if it's the same snapshot
        if baseline_id == latest_id:
            return []

        # Compare metric values between baseline and latest
        rows = cur.execute(
            """
            SELECT
                latest.file_path,
                baseline.value as old_value,
                latest.value as new_value,
                latest.value - baseline.value as delta
            FROM signal_history latest
            JOIN signal_history baseline
                ON latest.file_path = baseline.file_path
                AND baseline.snapshot_id = ?
                AND baseline.signal_name = ?
            WHERE latest.snapshot_id = ?
                AND latest.signal_name = ?
            ORDER BY ABS(latest.value - baseline.value) DESC
            LIMIT ?
        """,
            (baseline_id, metric, latest_id, metric, limit),
        ).fetchall()

        return [
            {
                "path": r["file_path"],
                "old_value": round(r["old_value"], 3),
                "new_value": round(r["new_value"], 3),
                "delta": round(r["delta"], 3),
            }
            for r in rows
        ]

    def _health_label(self, score: float) -> str:
        """Map 1-10 health score to label."""
        if score >= 8:
            return "Healthy"
        if score >= 6:
            return "Moderate"
        if score >= 4:
            return "At Risk"
        return "Critical"
