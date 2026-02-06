"""Tests for the snapshot module (models, identity, capture)."""

import sys

sys.path.insert(0, "src")

from shannon_insight.persistence.identity import compute_identity_key
from shannon_insight.persistence.models import FindingRecord, Snapshot


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
