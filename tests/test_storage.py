"""Tests for the storage module (database, writer, reader)."""
import sys
sys.path.insert(0, "src")

import os
import tempfile
import pytest
from shannon_insight.snapshot.models import Snapshot, FindingRecord, EvidenceRecord
from shannon_insight.storage.database import HistoryDB
from shannon_insight.storage.writer import save_snapshot
from shannon_insight.storage.reader import load_snapshot, load_snapshot_by_commit, list_snapshots


def _make_snapshot(**kwargs):
    defaults = dict(
        tool_version="0.6.0", timestamp="2025-01-01T12:00:00Z",
        analyzed_path="/tmp/test", file_count=5, module_count=2,
        commits_analyzed=10, analyzers_ran=["structural"],
        config_hash="abcdef1234567890",
    )
    defaults.update(kwargs)
    return Snapshot(**defaults)


class TestHistoryDB:
    def test_creates_directory_and_gitignore(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                assert (db.db_dir / ".gitignore").exists()
                assert (db.db_dir / ".gitignore").read_text() == "*\n"
                assert db.db_path.exists()

    def test_context_manager(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                assert db.conn is not None
            assert db.conn is None  # closed after exit

    def test_migrate_idempotent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # First open
            with HistoryDB(tmpdir) as db:
                pass
            # Second open - should not fail
            with HistoryDB(tmpdir) as db:
                assert db.conn is not None


class TestWriterReader:
    def test_save_and_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            snap = _make_snapshot(
                file_signals={"a.py": {"pagerank": 0.5, "lines": 100.0}},
                codebase_signals={"fiedler_value": 0.123},
                findings=[
                    FindingRecord(
                        finding_type="high_risk_hub", identity_key="key1",
                        severity=0.85, title="test", files=["a.py"],
                        evidence=[EvidenceRecord("pagerank", 0.5, 95.0, "top 5%")],
                        suggestion="split it",
                    )
                ],
                dependency_edges=[("a.py", "b.py")],
                commit_sha="abc123",
            )
            with HistoryDB(tmpdir) as db:
                sid = save_snapshot(db.conn, snap)
                loaded = load_snapshot(db.conn, sid)

            assert loaded.tool_version == "0.6.0"
            assert loaded.file_count == 5
            assert loaded.commit_sha == "abc123"
            assert loaded.file_signals["a.py"]["pagerank"] == 0.5
            assert loaded.codebase_signals["fiedler_value"] == 0.123
            assert len(loaded.findings) == 1
            assert loaded.findings[0].finding_type == "high_risk_hub"
            assert loaded.findings[0].evidence[0].signal == "pagerank"
            assert len(loaded.dependency_edges) == 1
            assert loaded.dependency_edges[0] == ("a.py", "b.py")

    def test_load_snapshot_by_commit(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            snap = _make_snapshot(commit_sha="def456")
            with HistoryDB(tmpdir) as db:
                save_snapshot(db.conn, snap)
                loaded = load_snapshot_by_commit(db.conn, "def456")
                assert loaded is not None
                assert loaded.commit_sha == "def456"

                none_result = load_snapshot_by_commit(db.conn, "nonexistent")
                assert none_result is None

    def test_list_snapshots(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                for i in range(3):
                    snap = _make_snapshot(
                        timestamp=f"2025-01-0{i+1}T12:00:00Z",
                        file_count=i * 10 + 5,
                        findings=[FindingRecord("god_file", f"key{i}", 0.5, "f", ["a.py"], [], "s")] if i > 0 else [],
                    )
                    save_snapshot(db.conn, snap)
                rows = list_snapshots(db.conn)

            assert len(rows) == 3
            # Most recent first
            assert rows[0]["file_count"] == 25

    def test_concurrent_writes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                s1 = _make_snapshot(timestamp="2025-01-01T00:00:00Z")
                s2 = _make_snapshot(timestamp="2025-01-02T00:00:00Z")
                id1 = save_snapshot(db.conn, s1)
                id2 = save_snapshot(db.conn, s2)
                assert id1 != id2
                assert list_snapshots(db.conn).__len__() == 2

    def test_baseline_management(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                snap = _make_snapshot()
                sid = save_snapshot(db.conn, snap)

                assert db.get_baseline_snapshot_id() is None
                db.set_baseline(sid)
                assert db.get_baseline_snapshot_id() == sid
                db.clear_baseline()
                assert db.get_baseline_snapshot_id() is None
