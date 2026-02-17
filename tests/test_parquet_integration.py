"""Integration tests for the full Parquet pipeline.

Tests the complete flow:
TensorSnapshot -> emitter -> events -> writer -> Parquet files -> reader -> data

Also tests the CLI helper _save_parquet to verify the wiring works.
"""

import sys
import tempfile

sys.path.insert(0, "src")

import pytest

from shannon_insight.persistence.models import (
    EvidenceRecord,
    FindingRecord,
    TensorSnapshot,
)

# Guard: skip all tests if pyarrow is not installed
pytest.importorskip("pyarrow")

from shannon_insight.events.emitter import snapshot_to_events
from shannon_insight.storage.reader import ParquetReader
from shannon_insight.storage.writer import ParquetWriter


def _make_realistic_snapshot() -> TensorSnapshot:
    """Build a realistic TensorSnapshot with data in all sections."""
    return TensorSnapshot(
        schema_version=2,
        tool_version="0.8.0",
        commit_sha="abc123def456",
        timestamp="2025-06-15T12:00:00+00:00",
        analyzed_path="/home/user/my-project",
        file_count=5,
        module_count=2,
        commits_analyzed=100,
        analyzers_ran=["structural", "temporal", "spectral", "semantics"],
        config_hash="config-hash-abc",
        file_signals={
            "src/main.py": {
                "lines": 500,
                "function_count": 20,
                "class_count": 3,
                "max_nesting": 5,
                "pagerank": 0.15,
                "betweenness": 0.08,
                "cognitive_load": 0.7,
                "risk_score": 0.6,
                "total_changes": 45,
                "churn_trajectory": "CHURNING",
                "bus_factor": 2.0,
                "percentiles": {"pagerank": 95.0, "cognitive_load": 85.0},
            },
            "src/utils.py": {
                "lines": 200,
                "function_count": 10,
                "pagerank": 0.05,
                "cognitive_load": 0.3,
            },
            "src/models.py": {
                "lines": 150,
                "function_count": 5,
                "class_count": 4,
                "pagerank": 0.02,
            },
            "tests/test_main.py": {
                "lines": 300,
                "function_count": 15,
                "role": "TEST",
            },
            "README.md": {
                "lines": 50,
            },
        },
        module_signals={
            "src/": {
                "cohesion": 0.75,
                "coupling": 0.25,
                "instability": 0.45,
                "health_score": 7.2,
                "file_count": 3,
            },
            "tests/": {
                "cohesion": 0.9,
                "coupling": 0.1,
                "file_count": 1,
            },
        },
        global_signals={
            "modularity": 0.65,
            "fiedler_value": 0.12,
            "spectral_gap": 0.08,
            "cycle_count": 1,
            "codebase_health": 7.8,
        },
        findings=[
            FindingRecord(
                finding_type="high_risk_hub",
                identity_key="hub-main-py",
                severity=0.85,
                title="src/main.py is a high-risk hub",
                files=["src/main.py"],
                evidence=[
                    EvidenceRecord(
                        signal="pagerank",
                        value=0.15,
                        percentile=95.0,
                        description="top 5% by PageRank",
                    ),
                    EvidenceRecord(
                        signal="cognitive_load",
                        value=0.7,
                        percentile=85.0,
                        description="high cognitive load",
                    ),
                ],
                suggestion="Consider splitting src/main.py into smaller modules",
                confidence=0.75,
                effort="HIGH",
                scope="FILE",
            ),
            FindingRecord(
                finding_type="god_file",
                identity_key="god-main-py",
                severity=0.9,
                title="src/main.py is a god file",
                files=["src/main.py"],
                evidence=[],
                suggestion="Extract responsibilities into separate files",
            ),
        ],
        dependency_edges=[
            ("src/main.py", "src/utils.py"),
            ("src/main.py", "src/models.py"),
            ("tests/test_main.py", "src/main.py"),
        ],
        modules=["src/", "tests/"],
        layers=[{"depth": 0, "modules": ["src/"]}],
        violations=[],
        delta_h={"src/main.py": 0.22, "src/utils.py": 0.05},
    )


class TestFullPipeline:
    """End-to-end: TensorSnapshot -> events -> Parquet -> read back."""

    def test_realistic_roundtrip(self):
        snapshot = _make_realistic_snapshot()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Emit events
            events = snapshot_to_events(snapshot, snapshot_id="integration-001")

            # Write to Parquet
            writer = ParquetWriter(tmpdir)
            paths = writer.write_events(events)

            # Verify files created
            assert "snapshots" in paths
            assert "file_signals" in paths
            assert "module_signals" in paths
            assert "global_signals" in paths
            assert "edges" in paths
            assert "findings" in paths

            # Read back
            reader = ParquetReader(tmpdir)
            assert reader.available

            # Check snapshots
            snaps = reader.list_snapshots()
            assert len(snaps) == 1
            s = snaps[0]
            assert s["snapshot_id"] == "integration-001"
            assert s["file_count"] == 5
            assert s["module_count"] == 2
            assert s["commit_sha"] == "abc123def456"
            assert "structural" in s["analyzers_ran"]

            # Check file signals
            fs = reader.read_file_signals("integration-001")
            assert len(fs) == 5
            assert fs["src/main.py"]["lines"] == 500
            assert fs["src/main.py"]["pagerank"] == 0.15
            assert fs["src/main.py"]["cognitive_load"] == 0.7
            assert fs["src/main.py"]["total_changes"] == 45
            assert fs["src/main.py"]["delta_h"] == 0.22
            # Percentiles should NOT be in the output (computed on read)
            assert "percentiles" not in fs["src/main.py"]
            assert fs["src/utils.py"]["lines"] == 200

            # Check module signals
            ms = reader.read_module_signals("integration-001")
            assert len(ms) == 2
            assert ms["src/"]["cohesion"] == 0.75
            assert ms["src/"]["instability"] == 0.45
            assert ms["tests/"]["cohesion"] == 0.9

            # Check global signals
            gs = reader.read_global_signals("integration-001")
            assert gs["modularity"] == 0.65
            assert gs["fiedler_value"] == 0.12
            assert gs["codebase_health"] == 7.8

            # Check edges
            edges = reader.read_edges("integration-001")
            assert len(edges) == 3
            edge_pairs = {(e["source"], e["target"]) for e in edges}
            assert ("src/main.py", "src/utils.py") in edge_pairs
            assert ("tests/test_main.py", "src/main.py") in edge_pairs

            # Check findings
            findings = reader.read_findings("integration-001")
            assert len(findings) == 2

            hub_finding = next(f for f in findings if f["finding_type"] == "high_risk_hub")
            assert hub_finding["severity"] == 0.85
            assert hub_finding["files"] == ["src/main.py"]
            assert len(hub_finding["evidence"]) == 2
            assert hub_finding["evidence"][0]["signal"] == "pagerank"
            assert hub_finding["confidence"] == 0.75
            assert hub_finding["effort"] == "HIGH"

            god_finding = next(f for f in findings if f["finding_type"] == "god_file")
            assert god_finding["severity"] == 0.9

    def test_multi_snapshot_accumulation(self):
        """Verify that multiple snapshots accumulate correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = ParquetWriter(tmpdir)

            # First snapshot
            snap1 = TensorSnapshot(
                tool_version="0.8.0",
                timestamp="2025-01-01T00:00:00+00:00",
                analyzed_path="/tmp",
                file_count=3,
                file_signals={"a.py": {"lines": 100}},
                global_signals={"modularity": 0.5},
            )
            events1 = snapshot_to_events(snap1, snapshot_id="snap-001")
            writer.write_events(events1)

            # Second snapshot (next day)
            snap2 = TensorSnapshot(
                tool_version="0.8.0",
                timestamp="2025-01-02T00:00:00+00:00",
                analyzed_path="/tmp",
                file_count=5,
                file_signals={"a.py": {"lines": 120}, "b.py": {"lines": 50}},
                global_signals={"modularity": 0.6},
            )
            events2 = snapshot_to_events(snap2, snapshot_id="snap-002")
            writer.write_events(events2)

            # Read back both
            reader = ParquetReader(tmpdir)
            snaps = reader.list_snapshots()
            assert len(snaps) == 2

            # Each snapshot should have its own data
            fs1 = reader.read_file_signals("snap-001")
            assert len(fs1) == 1
            assert fs1["a.py"]["lines"] == 100

            fs2 = reader.read_file_signals("snap-002")
            assert len(fs2) == 2
            assert fs2["a.py"]["lines"] == 120
            assert fs2["b.py"]["lines"] == 50

            # Global signals independent
            gs1 = reader.read_global_signals("snap-001")
            assert gs1["modularity"] == 0.5

            gs2 = reader.read_global_signals("snap-002")
            assert gs2["modularity"] == 0.6

    def test_empty_snapshot(self):
        """Edge case: snapshot with no data except metadata."""
        snap = TensorSnapshot(
            tool_version="0.8.0",
            timestamp="2025-01-01T00:00:00Z",
            analyzed_path="/tmp",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            events = snapshot_to_events(snap, snapshot_id="empty-001")
            writer = ParquetWriter(tmpdir)
            paths = writer.write_events(events)

            # Only snapshot and global_signals should be written
            assert "snapshots" in paths
            assert "global_signals" in paths
            assert "file_signals" not in paths
            assert "edges" not in paths
            assert "findings" not in paths

            reader = ParquetReader(tmpdir)
            snaps = reader.list_snapshots()
            assert len(snaps) == 1
            assert snaps[0]["file_count"] == 0

    @pytest.mark.skip(reason="_save_parquet helper not yet implemented in CLI")
    def test_cli_save_parquet_helper(self):
        """Test the _save_parquet CLI helper directly."""
        import logging

        from shannon_insight.cli.analyze import _save_parquet

        snap = TensorSnapshot(
            tool_version="0.8.0",
            timestamp="2025-01-01T00:00:00Z",
            analyzed_path="/tmp",
            file_count=2,
            file_signals={
                "a.py": {"lines": 100},
                "b.py": {"lines": 50},
            },
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            test_logger = logging.getLogger("test_parquet_integration")
            _save_parquet(tmpdir, snap, test_logger)

            reader = ParquetReader(tmpdir)
            assert reader.available
            snaps = reader.list_snapshots()
            assert len(snaps) == 1
