"""Tests for the history queries module."""
import sys
sys.path.insert(0, "src")

import tempfile
import pytest
from shannon_insight.snapshot.models import Snapshot, FindingRecord, EvidenceRecord
from shannon_insight.storage.database import HistoryDB
from shannon_insight.storage.writer import save_snapshot
from shannon_insight.storage.queries import HistoryQuery


def _snap(ts="2025-01-01T00:00:00Z", file_signals=None, codebase_signals=None, findings=None, commit=None):
    return Snapshot(
        tool_version="0.6.0", timestamp=ts, analyzed_path="/tmp",
        file_count=len(file_signals or {}), commit_sha=commit,
        file_signals=file_signals or {},
        codebase_signals=codebase_signals or {},
        findings=findings or [],
    )


def _finding(key, severity=0.5):
    return FindingRecord("god_file", key, severity, "title", ["a.py"], [], "fix")


class TestFileTrend:
    def test_returns_chronological(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                for i in range(5):
                    snap = _snap(
                        ts=f"2025-01-0{i+1}T00:00:00Z",
                        file_signals={"a.py": {"cognitive_load": 0.5 + i * 0.05}},
                    )
                    save_snapshot(db.conn, snap)
                query = HistoryQuery(db.conn)
                points = query.file_trend("a.py", "cognitive_load", last_n=5)

            assert len(points) == 5
            # Chronological order (oldest first)
            assert points[0].value < points[-1].value

    def test_empty_result(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                query = HistoryQuery(db.conn)
                points = query.file_trend("nonexistent.py", "cognitive_load")
            assert points == []


class TestCodebaseHealth:
    def test_returns_health_points(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                for i in range(3):
                    snap = _snap(
                        ts=f"2025-01-0{i+1}T00:00:00Z",
                        codebase_signals={"fiedler_value": 0.1 + i * 0.02},
                    )
                    save_snapshot(db.conn, snap)
                query = HistoryQuery(db.conn)
                points = query.codebase_health(last_n=3)

            assert len(points) == 3
            # Check chronological order
            assert points[0].timestamp < points[-1].timestamp


class TestPersistentFindings:
    def test_finds_persistent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                for i in range(5):
                    snap = _snap(
                        ts=f"2025-01-0{i+1}T00:00:00Z",
                        findings=[_finding("persistent_key", severity=0.7)],
                    )
                    save_snapshot(db.conn, snap)
                query = HistoryQuery(db.conn)
                chronic = query.persistent_findings(min_snapshots=3)

            assert len(chronic) >= 1
            assert chronic[0]["count"] >= 3

    def test_non_consecutive_excluded(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                # Finding appears in snapshots 1, 2, then disappears in 3, reappears in 4, 5
                for i in range(5):
                    findings = [] if i == 2 else [_finding("gap_key")]
                    snap = _snap(ts=f"2025-01-0{i+1}T00:00:00Z", findings=findings)
                    save_snapshot(db.conn, snap)
                query = HistoryQuery(db.conn)
                # max consecutive run is 2 (snapshots 1,2 or 4,5), not 3
                chronic = query.persistent_findings(min_snapshots=3)

            gap_items = [c for c in chronic if c["identity_key"] == "gap_key"]
            assert len(gap_items) == 0


class TestTopMovers:
    def test_finds_movers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                snap1 = _snap(
                    ts="2025-01-01T00:00:00Z",
                    file_signals={"a.py": {"cognitive_load": 0.3}, "b.py": {"cognitive_load": 0.5}},
                )
                snap2 = _snap(
                    ts="2025-01-02T00:00:00Z",
                    file_signals={"a.py": {"cognitive_load": 0.9}, "b.py": {"cognitive_load": 0.5}},
                )
                save_snapshot(db.conn, snap1)
                save_snapshot(db.conn, snap2)
                query = HistoryQuery(db.conn)
                movers = query.top_movers(last_n=2, metric="cognitive_load")

            assert len(movers) >= 1
            assert movers[0]["filepath"] == "a.py"
            assert movers[0]["abs_delta"] == pytest.approx(0.6, abs=0.01)
