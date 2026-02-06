"""Tests for the snapshot module (models, identity, capture)."""

import sys

sys.path.insert(0, "src")

from shannon_insight.persistence.capture import (
    _serialize_file_signals,
    _serialize_global_signals,
    _serialize_module_signals,
)
from shannon_insight.persistence.identity import compute_identity_key
from shannon_insight.persistence.models import (
    FindingRecord,
    Snapshot,
    TensorSnapshot,
    snapshot_to_tensor,
)
from shannon_insight.signals.models import FileSignals, GlobalSignals, ModuleSignals


def _make_finding_record(**kwargs):
    defaults = {
        "finding_type": "high_risk_hub",
        "identity_key": "abc123",
        "severity": 0.85,
        "title": "test finding",
        "files": ["a.py"],
        "evidence": [],
        "suggestion": "fix it",
    }
    defaults.update(kwargs)
    return FindingRecord(**defaults)


class TestSnapshot:
    def test_snapshot_defaults(self):
        s = Snapshot(tool_version="0.6.0", timestamp="2025-01-01T00:00:00Z", analyzed_path="/tmp")
        assert s.schema_version == 1
        assert s.file_signals == {}
        assert s.codebase_signals == {}
        assert s.findings == []
        assert s.dependency_edges == []
        assert s.file_count == 0

    def test_snapshot_full_construction(self):
        s = Snapshot(
            tool_version="0.6.0",
            timestamp="2025-01-01T00:00:00Z",
            analyzed_path="/tmp",
            file_count=10,
            module_count=3,
            commits_analyzed=50,
            analyzers_ran=["structural", "temporal"],
            config_hash="abc123",
            file_signals={"a.py": {"cognitive_load": 0.5}},
            codebase_signals={"fiedler_value": 0.1},
            findings=[_make_finding_record()],
            dependency_edges=[("a.py", "b.py")],
        )
        assert s.file_count == 10
        assert len(s.findings) == 1
        assert s.file_signals["a.py"]["cognitive_load"] == 0.5


class TestFindingIdentity:
    def test_deterministic(self):
        k1 = compute_identity_key("high_risk_hub", ["a.py"])
        k2 = compute_identity_key("high_risk_hub", ["a.py"])
        assert k1 == k2
        assert len(k1) == 16

    def test_different_type_different_key(self):
        k1 = compute_identity_key("high_risk_hub", ["a.py"])
        k2 = compute_identity_key("god_file", ["a.py"])
        assert k1 != k2

    def test_high_risk_hub_uses_primary_file(self):
        k1 = compute_identity_key("high_risk_hub", ["a.py", "b.py"])
        k2 = compute_identity_key("high_risk_hub", ["a.py", "c.py"])
        assert k1 == k2  # same primary file

    def test_hidden_coupling_sorted(self):
        k1 = compute_identity_key("hidden_coupling", ["b.py", "a.py"])
        k2 = compute_identity_key("hidden_coupling", ["a.py", "b.py"])
        assert k1 == k2  # sorted pair

    def test_dead_dependency_sorted(self):
        k1 = compute_identity_key("dead_dependency", ["z.py", "a.py"])
        k2 = compute_identity_key("dead_dependency", ["a.py", "z.py"])
        assert k1 == k2

    def test_boundary_mismatch_uses_first(self):
        k1 = compute_identity_key("boundary_mismatch", ["dir/"])
        assert len(k1) == 16

    def test_god_file_uses_primary(self):
        k1 = compute_identity_key("god_file", ["x.py"])
        k2 = compute_identity_key("god_file", ["x.py"])
        assert k1 == k2

    def test_unstable_file_uses_primary(self):
        k1 = compute_identity_key("unstable_file", ["x.py"])
        assert len(k1) == 16

    def test_unknown_type_fallback(self):
        k1 = compute_identity_key("new_type", ["b.py", "a.py"])
        k2 = compute_identity_key("new_type", ["a.py", "b.py"])
        assert k1 == k2  # sorted fallback

    # Phase 6 finder types
    def test_orphan_code_uses_primary(self):
        k1 = compute_identity_key("orphan_code", ["x.py"])
        k2 = compute_identity_key("orphan_code", ["x.py", "y.py"])
        assert k1 == k2  # same primary file

    def test_copy_paste_clone_sorted(self):
        k1 = compute_identity_key("copy_paste_clone", ["b.py", "a.py"])
        k2 = compute_identity_key("copy_paste_clone", ["a.py", "b.py"])
        assert k1 == k2  # sorted pair

    def test_layer_violation_uses_module(self):
        k1 = compute_identity_key("layer_violation", ["src/module/"])
        assert len(k1) == 16

    def test_flat_architecture_codebase_scope(self):
        k1 = compute_identity_key("flat_architecture", [])
        k2 = compute_identity_key("flat_architecture", ["a.py", "b.py"])
        assert k1 == k2  # both use "codebase"

    def test_conway_violation_codebase_scope(self):
        k1 = compute_identity_key("conway_violation", [])
        k2 = compute_identity_key("conway_violation", ["x.py"])
        assert k1 == k2  # codebase scope

    # Phase 7 wrapper type
    def test_chronic_problem_uses_wrapped_key(self):
        base_key = compute_identity_key("high_risk_hub", ["a.py"])
        k1 = compute_identity_key("chronic_problem", ["a.py"], wrapped_key=base_key)
        k2 = compute_identity_key("chronic_problem", ["b.py"], wrapped_key=base_key)
        assert k1 == k2  # uses wrapped key, not files


class TestTensorSnapshot:
    def test_tensor_snapshot_defaults(self):
        ts = TensorSnapshot(
            tool_version="0.7.0", timestamp="2025-01-01T00:00:00Z", analyzed_path="/tmp"
        )
        assert ts.schema_version == 2
        assert ts.file_signals == {}
        assert ts.module_signals == {}
        assert ts.global_signals == {}
        assert ts.findings == []
        assert ts.modules == []
        assert ts.layers == []
        assert ts.violations == []
        assert ts.delta_h == {}

    def test_tensor_snapshot_full_construction(self):
        ts = TensorSnapshot(
            tool_version="0.7.0",
            timestamp="2025-01-01T00:00:00Z",
            analyzed_path="/tmp",
            file_count=10,
            module_count=3,
            file_signals={"a.py": {"cognitive_load": 0.5, "risk_score": 0.7}},
            module_signals={"src/": {"cohesion": 0.8, "instability": 0.3}},
            global_signals={"modularity": 0.6, "codebase_health": 8.5},
            modules=["src/", "tests/"],
            layers=[{"depth": 0, "modules": ["src/"]}],
            violations=[{"src": "tests/", "tgt": "src/", "type": "layer"}],
            delta_h={"a.py": 0.15},
        )
        assert ts.file_count == 10
        assert ts.file_signals["a.py"]["risk_score"] == 0.7
        assert ts.module_signals["src/"]["instability"] == 0.3
        assert ts.global_signals["codebase_health"] == 8.5
        assert len(ts.modules) == 2
        assert len(ts.violations) == 1

    def test_finding_record_has_v2_fields(self):
        fr = FindingRecord(
            finding_type="high_risk_hub",
            identity_key="abc123",
            severity=0.85,
            title="test",
            files=["a.py"],
            evidence=[],
            suggestion="fix it",
            confidence=0.75,
            effort="HIGH",
            scope="FILE",
        )
        assert fr.confidence == 0.75
        assert fr.effort == "HIGH"
        assert fr.scope == "FILE"


class TestSnapshotConversion:
    def test_v1_to_tensor_basic(self):
        v1 = Snapshot(
            tool_version="0.6.0",
            timestamp="2025-01-01T00:00:00Z",
            analyzed_path="/tmp",
            file_count=5,
        )
        ts = snapshot_to_tensor(v1)
        assert ts.schema_version == 2
        assert ts.tool_version == "0.6.0"
        assert ts.file_count == 5
        assert ts.module_signals == {}
        assert ts.modules == []

    def test_v1_to_tensor_preserves_file_signals(self):
        v1 = Snapshot(
            tool_version="0.6.0",
            timestamp="2025-01-01T00:00:00Z",
            analyzed_path="/tmp",
            file_signals={"a.py": {"cognitive_load": 0.5}},
        )
        ts = snapshot_to_tensor(v1)
        assert ts.file_signals["a.py"]["cognitive_load"] == 0.5

    def test_v1_to_tensor_maps_codebase_to_global(self):
        v1 = Snapshot(
            tool_version="0.6.0",
            timestamp="2025-01-01T00:00:00Z",
            analyzed_path="/tmp",
            codebase_signals={"fiedler_value": 0.1, "modularity": 0.5},
        )
        ts = snapshot_to_tensor(v1)
        assert ts.global_signals["fiedler_value"] == 0.1
        assert ts.global_signals["modularity"] == 0.5

    def test_v1_to_tensor_preserves_findings(self):
        fr = FindingRecord(
            finding_type="test",
            identity_key="x",
            severity=0.5,
            title="t",
            files=["a.py"],
            evidence=[],
            suggestion="s",
        )
        v1 = Snapshot(
            tool_version="0.6.0",
            timestamp="2025-01-01T00:00:00Z",
            analyzed_path="/tmp",
            findings=[fr],
        )
        ts = snapshot_to_tensor(v1)
        assert len(ts.findings) == 1
        assert ts.findings[0].finding_type == "test"


class TestSignalSerialization:
    def test_serialize_file_signals(self):
        """Test FileSignals serialization."""
        fs = FileSignals(
            path="a.py",
            lines=100,
            function_count=5,
            cognitive_load=0.5,
            risk_score=0.3,
            percentiles={"cognitive_load": 0.75, "risk_score": 0.85},
        )
        result = _serialize_file_signals(fs)

        assert result["lines"] == 100
        assert result["function_count"] == 5
        assert result["cognitive_load"] == 0.5
        assert result["risk_score"] == 0.3
        assert result["percentiles"]["cognitive_load"] == 0.75
        assert "path" not in result  # path should not be serialized

    def test_serialize_module_signals(self):
        """Test ModuleSignals serialization."""
        ms = ModuleSignals(
            path="src/",
            cohesion=0.8,
            coupling=0.2,
            instability=0.4,
            health_score=7.5,
        )
        result = _serialize_module_signals(ms)

        assert result["cohesion"] == 0.8
        assert result["coupling"] == 0.2
        assert result["instability"] == 0.4
        assert result["health_score"] == 7.5
        assert "path" not in result

    def test_serialize_module_signals_none_instability(self):
        """Test that None instability is preserved."""
        ms = ModuleSignals(
            path="src/",
            cohesion=0.8,
            instability=None,
        )
        result = _serialize_module_signals(ms)
        assert "instability" not in result  # None values should be omitted

    def test_serialize_global_signals(self):
        """Test GlobalSignals serialization."""
        gs = GlobalSignals(
            modularity=0.6,
            fiedler_value=0.1,
            codebase_health=8.2,
            team_size=5,
        )
        result = _serialize_global_signals(gs)

        assert result["modularity"] == 0.6
        assert result["fiedler_value"] == 0.1
        assert result["codebase_health"] == 8.2
        assert result["team_size"] == 5
