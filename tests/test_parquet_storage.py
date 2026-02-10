"""Tests for the Parquet storage writer and reader."""

import sys
import tempfile

sys.path.insert(0, "src")

import pytest

from shannon_insight.events.emitter import snapshot_to_events
from shannon_insight.persistence.models import (
    EvidenceRecord,
    FindingRecord,
    TensorSnapshot,
)

# Guard: skip all tests if pyarrow is not installed
pytest.importorskip("pyarrow")

from shannon_insight.storage.reader import ParquetReader
from shannon_insight.storage.writer import ParquetWriter

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_snapshot(**kwargs) -> TensorSnapshot:
    defaults = {
        "tool_version": "0.8.0",
        "timestamp": "2025-01-01T00:00:00Z",
        "analyzed_path": "/tmp/test-project",
    }
    defaults.update(kwargs)
    return TensorSnapshot(**defaults)


def _make_events(snapshot_id: str = "test-001", **kwargs) -> dict:
    snap = _make_snapshot(**kwargs)
    return snapshot_to_events(snap, snapshot_id=snapshot_id)


# ---------------------------------------------------------------------------
# ParquetWriter
# ---------------------------------------------------------------------------


class TestParquetWriter:
    def test_creates_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ParquetWriter(tmpdir)
            events = _make_events()
            writer.write_events(events)

            parquet_dir = writer.parquet_dir
            assert parquet_dir.exists()
            assert (parquet_dir / "snapshots.parquet").exists()

    def test_creates_gitignore(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ParquetWriter(tmpdir)
            events = _make_events()
            writer.write_events(events)

            gitignore = writer.parquet_dir.parent / ".gitignore"
            assert gitignore.exists()
            assert gitignore.read_text().strip() == "*"

    def test_writes_snapshot_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ParquetWriter(tmpdir)
            events = _make_events(
                snapshot_id="snap-001",
                file_count=10,
                module_count=3,
            )
            paths = writer.write_events(events)

            assert "snapshots" in paths
            import pyarrow.parquet as pq

            table = pq.read_table(str(paths["snapshots"]))
            assert table.num_rows == 1
            row = table.to_pylist()[0]
            assert row["snapshot_id"] == "snap-001"
            assert row["file_count"] == 10

    def test_writes_file_signals(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ParquetWriter(tmpdir)
            events = _make_events(
                file_signals={
                    "a.py": {"lines": 100, "pagerank": 0.05},
                    "b.py": {"lines": 50},
                }
            )
            paths = writer.write_events(events)

            assert "file_signals" in paths
            import pyarrow.parquet as pq

            table = pq.read_table(str(paths["file_signals"]))
            assert table.num_rows == 2

    def test_writes_edges(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ParquetWriter(tmpdir)
            events = _make_events(dependency_edges=[("a.py", "b.py"), ("b.py", "c.py")])
            paths = writer.write_events(events)

            assert "edges" in paths
            import pyarrow.parquet as pq

            table = pq.read_table(str(paths["edges"]))
            assert table.num_rows == 2
            rows = table.to_pylist()
            assert rows[0]["space"] == "G1"

    def test_writes_findings(self):
        fr = FindingRecord(
            finding_type="high_risk_hub",
            identity_key="abc123",
            severity=0.85,
            title="test finding",
            files=["a.py"],
            evidence=[
                EvidenceRecord(
                    signal="pagerank",
                    value=0.95,
                    percentile=99.0,
                    description="top 1%",
                )
            ],
            suggestion="fix it",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ParquetWriter(tmpdir)
            events = _make_events(findings=[fr])
            paths = writer.write_events(events)

            assert "findings" in paths
            import pyarrow.parquet as pq

            table = pq.read_table(str(paths["findings"]))
            assert table.num_rows == 1

    def test_appends_to_existing(self):
        """Verify that writing a second snapshot appends to existing files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ParquetWriter(tmpdir)

            # First snapshot
            events1 = _make_events(snapshot_id="snap-001", file_count=5)
            writer.write_events(events1)

            # Second snapshot
            events2 = _make_events(snapshot_id="snap-002", file_count=10)
            writer.write_events(events2)

            import pyarrow.parquet as pq

            table = pq.read_table(str(writer.parquet_dir / "snapshots.parquet"))
            assert table.num_rows == 2
            rows = table.to_pylist()
            ids = {r["snapshot_id"] for r in rows}
            assert ids == {"snap-001", "snap-002"}

    def test_skips_empty_tables(self):
        """No file_signals file created when there are no file signals."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ParquetWriter(tmpdir)
            events = _make_events()  # No file signals
            paths = writer.write_events(events)

            assert "file_signals" not in paths
            assert not (writer.parquet_dir / "file_signals.parquet").exists()


# ---------------------------------------------------------------------------
# ParquetReader
# ---------------------------------------------------------------------------


class TestParquetReader:
    def test_not_available_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            reader = ParquetReader(tmpdir)
            assert not reader.available

    def test_available_after_write(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ParquetWriter(tmpdir)
            events = _make_events()
            writer.write_events(events)

            reader = ParquetReader(tmpdir)
            assert reader.available

    def test_list_snapshots(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ParquetWriter(tmpdir)
            writer.write_events(
                _make_events(
                    snapshot_id="snap-001",
                    file_count=10,
                )
            )
            writer.write_events(
                _make_events(
                    snapshot_id="snap-002",
                    file_count=20,
                )
            )

            reader = ParquetReader(tmpdir)
            snapshots = reader.list_snapshots()
            assert len(snapshots) == 2
            # Both should be returned
            ids = {s["snapshot_id"] for s in snapshots}
            assert ids == {"snap-001", "snap-002"}

    def test_list_snapshots_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            reader = ParquetReader(tmpdir)
            assert reader.list_snapshots() == []

    def test_read_file_signals(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ParquetWriter(tmpdir)
            events = _make_events(
                snapshot_id="snap-001",
                file_signals={
                    "a.py": {"lines": 100, "pagerank": 0.05},
                    "b.py": {"lines": 50},
                },
            )
            writer.write_events(events)

            reader = ParquetReader(tmpdir)
            file_sigs = reader.read_file_signals("snap-001")

            assert "a.py" in file_sigs
            assert file_sigs["a.py"]["lines"] == 100
            assert file_sigs["a.py"]["pagerank"] == 0.05
            assert "b.py" in file_sigs

    def test_read_file_signals_filters_by_snapshot(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ParquetWriter(tmpdir)
            writer.write_events(
                _make_events(
                    snapshot_id="snap-001",
                    file_signals={"a.py": {"lines": 100}},
                )
            )
            writer.write_events(
                _make_events(
                    snapshot_id="snap-002",
                    file_signals={"b.py": {"lines": 200}},
                )
            )

            reader = ParquetReader(tmpdir)

            sigs1 = reader.read_file_signals("snap-001")
            assert "a.py" in sigs1
            assert "b.py" not in sigs1

            sigs2 = reader.read_file_signals("snap-002")
            assert "b.py" in sigs2
            assert "a.py" not in sigs2

    def test_read_module_signals(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ParquetWriter(tmpdir)
            events = _make_events(
                snapshot_id="snap-001",
                module_signals={"src/": {"cohesion": 0.8, "instability": 0.4}},
            )
            writer.write_events(events)

            reader = ParquetReader(tmpdir)
            mod_sigs = reader.read_module_signals("snap-001")

            assert "src/" in mod_sigs
            assert mod_sigs["src/"]["cohesion"] == 0.8

    def test_read_global_signals(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ParquetWriter(tmpdir)
            events = _make_events(
                snapshot_id="snap-001",
                global_signals={"modularity": 0.6, "codebase_health": 8.2},
            )
            writer.write_events(events)

            reader = ParquetReader(tmpdir)
            gs = reader.read_global_signals("snap-001")

            assert gs["modularity"] == 0.6
            assert gs["codebase_health"] == 8.2

    def test_read_edges(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ParquetWriter(tmpdir)
            events = _make_events(
                snapshot_id="snap-001",
                dependency_edges=[("a.py", "b.py"), ("b.py", "c.py")],
            )
            writer.write_events(events)

            reader = ParquetReader(tmpdir)
            edges = reader.read_edges("snap-001")

            assert len(edges) == 2
            assert edges[0]["source"] == "a.py"
            assert edges[0]["space"] == "G1"

    def test_read_edges_filter_space(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ParquetWriter(tmpdir)
            events = _make_events(
                snapshot_id="snap-001",
                dependency_edges=[("a.py", "b.py")],
            )
            writer.write_events(events)

            reader = ParquetReader(tmpdir)

            # G1 edges should be found
            g1_edges = reader.read_edges("snap-001", space="G1")
            assert len(g1_edges) == 1

            # G4 edges should not exist
            g4_edges = reader.read_edges("snap-001", space="G4")
            assert len(g4_edges) == 0

    def test_read_findings(self):
        fr = FindingRecord(
            finding_type="high_risk_hub",
            identity_key="abc123",
            severity=0.85,
            title="test finding",
            files=["a.py"],
            evidence=[
                EvidenceRecord(
                    signal="pagerank",
                    value=0.95,
                    percentile=99.0,
                    description="top 1%",
                )
            ],
            suggestion="fix it",
            confidence=0.75,
            effort="HIGH",
            scope="FILE",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ParquetWriter(tmpdir)
            events = _make_events(snapshot_id="snap-001", findings=[fr])
            writer.write_events(events)

            reader = ParquetReader(tmpdir)
            findings = reader.read_findings("snap-001")

            assert len(findings) == 1
            f = findings[0]
            assert f["finding_type"] == "high_risk_hub"
            assert f["severity"] == 0.85
            assert f["files"] == ["a.py"]
            assert len(f["evidence"]) == 1
            assert f["evidence"][0]["signal"] == "pagerank"
            assert f["confidence"] == 0.75

    def test_read_nonexistent_snapshot(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ParquetWriter(tmpdir)
            events = _make_events(snapshot_id="snap-001")
            writer.write_events(events)

            reader = ParquetReader(tmpdir)
            file_sigs = reader.read_file_signals("nonexistent")
            assert file_sigs == {}

    def test_full_roundtrip(self):
        """Write a full snapshot and read everything back."""
        fr = FindingRecord(
            finding_type="god_file",
            identity_key="def456",
            severity=0.9,
            title="big file",
            files=["huge.py"],
            evidence=[],
            suggestion="split it",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ParquetWriter(tmpdir)
            events = _make_events(
                snapshot_id="roundtrip-001",
                file_count=3,
                module_count=1,
                file_signals={
                    "a.py": {"lines": 100, "pagerank": 0.05, "cognitive_load": 0.7},
                    "b.py": {"lines": 50},
                    "c.py": {"lines": 200, "risk_score": 0.8},
                },
                module_signals={"src/": {"cohesion": 0.8}},
                global_signals={"modularity": 0.6},
                dependency_edges=[("a.py", "b.py")],
                findings=[fr],
                delta_h={"a.py": 0.15},
            )
            writer.write_events(events)

            reader = ParquetReader(tmpdir)

            # Snapshots
            snaps = reader.list_snapshots()
            assert len(snaps) == 1
            assert snaps[0]["snapshot_id"] == "roundtrip-001"
            assert snaps[0]["file_count"] == 3

            # File signals
            fs = reader.read_file_signals("roundtrip-001")
            assert len(fs) == 3
            assert fs["a.py"]["lines"] == 100
            assert fs["a.py"]["pagerank"] == 0.05
            # delta_h should be present
            assert fs["a.py"]["delta_h"] == 0.15

            # Module signals
            ms = reader.read_module_signals("roundtrip-001")
            assert "src/" in ms
            assert ms["src/"]["cohesion"] == 0.8

            # Global signals
            gs = reader.read_global_signals("roundtrip-001")
            assert gs["modularity"] == 0.6

            # Edges
            edges = reader.read_edges("roundtrip-001")
            assert len(edges) == 1
            assert edges[0]["source"] == "a.py"

            # Findings
            findings = reader.read_findings("roundtrip-001")
            assert len(findings) == 1
            assert findings[0]["finding_type"] == "god_file"
