"""Tests for the events module (schema + emitter)."""

import sys

sys.path.insert(0, "src")

from shannon_insight.events.emitter import snapshot_to_events
from shannon_insight.events.schema import (
    EdgeEvent,
    FileSignalEvent,
    FindingEvent,
    GlobalSignalEvent,
    ModuleSignalEvent,
    SnapshotEvent,
)
from shannon_insight.persistence.models import (
    EvidenceRecord,
    FindingRecord,
    TensorSnapshot,
)
from shannon_insight.signals.models import FileSignals, GlobalSignals, ModuleSignals

# ---------------------------------------------------------------------------
# SnapshotEvent
# ---------------------------------------------------------------------------


class TestSnapshotEvent:
    def test_defaults(self):
        e = SnapshotEvent(snapshot_id="abc123")
        assert e.snapshot_id == "abc123"
        assert e.schema_version == 2
        assert e.analyzers_ran == []
        assert e.file_count == 0

    def test_now_iso(self):
        ts = SnapshotEvent.now_iso()
        assert "T" in ts  # ISO-8601 has T separator
        assert "+" in ts or "Z" in ts or ts.endswith("+00:00")

    def test_full_construction(self):
        e = SnapshotEvent(
            snapshot_id="s1",
            timestamp="2025-01-01T00:00:00Z",
            commit_sha="abc123",
            analyzed_path="/tmp",
            tool_version="0.8.0",
            file_count=100,
            module_count=10,
            commits_analyzed=50,
            analyzers_ran=["structural", "temporal"],
            config_hash="hash123",
        )
        assert e.file_count == 100
        assert e.analyzers_ran == ["structural", "temporal"]


# ---------------------------------------------------------------------------
# FileSignalEvent
# ---------------------------------------------------------------------------


class TestFileSignalEvent:
    def test_defaults(self):
        e = FileSignalEvent(snapshot_id="s1", file_path="a.py")
        assert e.snapshot_id == "s1"
        assert e.file_path == "a.py"
        assert e.lines is None
        assert e.pagerank is None
        assert e.risk_score is None

    def test_to_dict(self):
        e = FileSignalEvent(
            snapshot_id="s1",
            file_path="a.py",
            lines=100,
            pagerank=0.05,
            cognitive_load=0.7,
        )
        d = e.to_dict()
        assert d["snapshot_id"] == "s1"
        assert d["file_path"] == "a.py"
        assert d["lines"] == 100
        assert d["pagerank"] == 0.05
        assert d["cognitive_load"] == 0.7
        # None values preserved
        assert d["betweenness"] is None

    def test_from_file_signals(self):
        fs = FileSignals(
            path="a.py",
            lines=100,
            function_count=5,
            pagerank=0.05,
            cognitive_load=0.7,
            risk_score=0.3,
            community=2,
            depth=3,
        )
        event = FileSignalEvent.from_file_signals("s1", "a.py", fs, delta_h=0.15)
        assert event.lines == 100
        assert event.function_count == 5
        assert event.pagerank == 0.05
        assert event.cognitive_load == 0.7
        assert event.risk_score == 0.3
        assert event.community == 2
        assert event.depth == 3
        assert event.delta_h == 0.15

    def test_from_file_signals_defaults_become_none(self):
        """Default/zero values should map to None to save storage."""
        fs = FileSignals(path="a.py")  # All defaults
        event = FileSignalEvent.from_file_signals("s1", "a.py", fs)
        assert event.lines is None  # lines=0 -> None
        assert event.role is None  # "UNKNOWN" -> None
        assert event.community is None  # -1 -> None
        assert event.depth is None  # -1 -> None
        assert event.churn_trajectory is None  # "DORMANT" -> None
        assert event.wiring_quality is None  # 1.0 -> None


# ---------------------------------------------------------------------------
# ModuleSignalEvent
# ---------------------------------------------------------------------------


class TestModuleSignalEvent:
    def test_defaults(self):
        e = ModuleSignalEvent(snapshot_id="s1", module_path="src/")
        assert e.cohesion is None
        assert e.instability is None

    def test_from_module_signals(self):
        ms = ModuleSignals(
            path="src/",
            cohesion=0.8,
            coupling=0.2,
            instability=0.4,
            health_score=7.5,
        )
        event = ModuleSignalEvent.from_module_signals("s1", "src/", ms)
        assert event.cohesion == 0.8
        assert event.coupling == 0.2
        assert event.instability == 0.4
        assert event.health_score == 7.5

    def test_none_instability_preserved(self):
        ms = ModuleSignals(path="src/", instability=None)
        event = ModuleSignalEvent.from_module_signals("s1", "src/", ms)
        assert event.instability is None


# ---------------------------------------------------------------------------
# GlobalSignalEvent
# ---------------------------------------------------------------------------


class TestGlobalSignalEvent:
    def test_defaults(self):
        e = GlobalSignalEvent(snapshot_id="s1")
        assert e.modularity is None
        assert e.codebase_health is None

    def test_from_global_signals(self):
        gs = GlobalSignals(
            modularity=0.6,
            fiedler_value=0.1,
            codebase_health=8.2,
            team_size=5,
        )
        event = GlobalSignalEvent.from_global_signals("s1", gs)
        assert event.modularity == 0.6
        assert event.fiedler_value == 0.1
        assert event.codebase_health == 8.2
        assert event.team_size == 5


# ---------------------------------------------------------------------------
# EdgeEvent
# ---------------------------------------------------------------------------


class TestEdgeEvent:
    def test_defaults(self):
        e = EdgeEvent(snapshot_id="s1", source="a.py", target="b.py", space="G1")
        assert e.weight == 1.0
        assert e.data is None

    def test_to_dict(self):
        e = EdgeEvent(
            snapshot_id="s1",
            source="a.py",
            target="b.py",
            space="G4",
            weight=0.8,
            data='{"co_change_count": 5}',
        )
        d = e.to_dict()
        assert d["space"] == "G4"
        assert d["weight"] == 0.8


# ---------------------------------------------------------------------------
# FindingEvent
# ---------------------------------------------------------------------------


class TestFindingEvent:
    def test_defaults(self):
        e = FindingEvent(
            snapshot_id="s1",
            finding_type="high_risk_hub",
            identity_key="abc123",
            severity=0.85,
            title="test",
        )
        assert e.confidence == 1.0
        assert e.effort == "MEDIUM"
        assert e.scope == "FILE"

    def test_to_dict_serializes_files(self):
        e = FindingEvent(
            snapshot_id="s1",
            finding_type="high_risk_hub",
            identity_key="abc123",
            severity=0.85,
            title="test",
            files=["a.py", "b.py"],
        )
        d = e.to_dict()
        assert d["files"] == '["a.py", "b.py"]'  # JSON string

    def test_from_finding_record(self):
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
            suggestion="split the file",
            confidence=0.75,
            effort="HIGH",
            scope="FILE",
        )
        event = FindingEvent.from_finding_record("s1", fr)
        assert event.finding_type == "high_risk_hub"
        assert event.identity_key == "abc123"
        assert event.severity == 0.85
        assert event.confidence == 0.75
        assert event.effort == "HIGH"
        assert "pagerank" in event.evidence


# ---------------------------------------------------------------------------
# Emitter: snapshot_to_events
# ---------------------------------------------------------------------------


class TestEmitter:
    def _make_snapshot(self, **kwargs) -> TensorSnapshot:
        defaults = {
            "tool_version": "0.8.0",
            "timestamp": "2025-01-01T00:00:00Z",
            "analyzed_path": "/tmp",
        }
        defaults.update(kwargs)
        return TensorSnapshot(**defaults)

    def test_basic_snapshot(self):
        snap = self._make_snapshot(file_count=10, module_count=3)
        events = snapshot_to_events(snap, snapshot_id="test-001")

        assert events["snapshot"].snapshot_id == "test-001"
        assert events["snapshot"].file_count == 10
        assert events["file_signals"] == []
        assert events["module_signals"] == []
        assert events["edges"] == []
        assert events["findings"] == []

    def test_generates_id_if_missing(self):
        snap = self._make_snapshot()
        events = snapshot_to_events(snap)
        assert events["snapshot"].snapshot_id is not None
        assert len(events["snapshot"].snapshot_id) == 16

    def test_file_signals_converted(self):
        snap = self._make_snapshot(
            file_signals={
                "a.py": {"lines": 100, "pagerank": 0.05, "cognitive_load": 0.7},
                "b.py": {"lines": 50},
            }
        )
        events = snapshot_to_events(snap, snapshot_id="s1")

        assert len(events["file_signals"]) == 2
        a_event = next(e for e in events["file_signals"] if e.file_path == "a.py")
        assert a_event.lines == 100
        assert a_event.pagerank == 0.05

    def test_delta_h_attached(self):
        snap = self._make_snapshot(
            file_signals={"a.py": {"lines": 100}},
            delta_h={"a.py": 0.15},
        )
        events = snapshot_to_events(snap, snapshot_id="s1")

        a_event = events["file_signals"][0]
        assert a_event.delta_h == 0.15

    def test_module_signals_converted(self):
        snap = self._make_snapshot(
            module_signals={
                "src/": {"cohesion": 0.8, "instability": 0.4},
            }
        )
        events = snapshot_to_events(snap, snapshot_id="s1")

        assert len(events["module_signals"]) == 1
        assert events["module_signals"][0].cohesion == 0.8

    def test_global_signals_converted(self):
        snap = self._make_snapshot(
            global_signals={"modularity": 0.6, "codebase_health": 8.2},
        )
        events = snapshot_to_events(snap, snapshot_id="s1")
        gs = events["global_signals"]
        assert gs.modularity == 0.6
        assert gs.codebase_health == 8.2

    def test_edges_converted(self):
        snap = self._make_snapshot(
            dependency_edges=[("a.py", "b.py"), ("b.py", "c.py")],
        )
        events = snapshot_to_events(snap, snapshot_id="s1")

        assert len(events["edges"]) == 2
        assert all(e.space == "G1" for e in events["edges"])
        assert events["edges"][0].source == "a.py"
        assert events["edges"][0].target == "b.py"

    def test_findings_converted(self):
        fr = FindingRecord(
            finding_type="high_risk_hub",
            identity_key="abc123",
            severity=0.85,
            title="test",
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
        snap = self._make_snapshot(findings=[fr])
        events = snapshot_to_events(snap, snapshot_id="s1")

        assert len(events["findings"]) == 1
        fe = events["findings"][0]
        assert fe.finding_type == "high_risk_hub"
        assert fe.confidence == 0.75

    def test_full_roundtrip(self):
        """Test a realistic snapshot with data in all sections."""
        snap = self._make_snapshot(
            file_count=3,
            module_count=1,
            commits_analyzed=25,
            analyzers_ran=["structural", "temporal"],
            file_signals={
                "a.py": {
                    "lines": 100,
                    "pagerank": 0.05,
                    "cognitive_load": 0.7,
                    "risk_score": 0.3,
                    "percentiles": {"pagerank": 0.95},  # Should be skipped
                },
                "b.py": {"lines": 50, "pagerank": 0.01},
                "c.py": {"lines": 200},
            },
            module_signals={"src/": {"cohesion": 0.8}},
            global_signals={"modularity": 0.6},
            dependency_edges=[("a.py", "b.py")],
            delta_h={"a.py": 0.15},
        )
        events = snapshot_to_events(snap, snapshot_id="full-001")

        assert events["snapshot"].file_count == 3
        assert len(events["file_signals"]) == 3
        assert len(events["module_signals"]) == 1
        assert events["global_signals"].modularity == 0.6
        assert len(events["edges"]) == 1

        # Percentiles should NOT be present on file signal events
        a_event = next(e for e in events["file_signals"] if e.file_path == "a.py")
        d = a_event.to_dict()
        assert "percentiles" not in d
