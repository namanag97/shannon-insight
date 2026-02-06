"""Tests for the diff engine module."""

import sys

sys.path.insert(0, "src")

from shannon_insight.persistence.diff_engine import (
    _classify_trend,
    _diff_signal_dicts,
    diff_snapshots,
    diff_tensor_snapshots,
)
from shannon_insight.persistence.diff_models import TensorSnapshotDiff
from shannon_insight.persistence.models import FindingRecord, Snapshot, TensorSnapshot


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


class TestTrendClassification:
    def test_lower_is_better_decrease_is_improving(self):
        assert _classify_trend("cognitive_load", -0.1) == "improving"

    def test_lower_is_better_increase_is_worsening(self):
        assert _classify_trend("cognitive_load", 0.1) == "worsening"

    def test_higher_is_better_increase_is_improving(self):
        assert _classify_trend("cohesion", 0.1) == "improving"

    def test_higher_is_better_decrease_is_worsening(self):
        assert _classify_trend("cohesion", -0.1) == "worsening"

    def test_neutral_is_stable(self):
        assert _classify_trend("lines", 100) == "stable"

    def test_small_delta_is_stable(self):
        assert _classify_trend("cognitive_load", 0.0001) == "stable"


class TestSignalDictDiff:
    def test_computes_deltas(self):
        old = {"cognitive_load": 0.5, "pagerank": 0.1}
        new = {"cognitive_load": 0.7, "pagerank": 0.15}
        deltas = _diff_signal_dicts(old, new, threshold=0.01)

        assert len(deltas) == 2
        cl_delta = next(d for d in deltas if d.signal_name == "cognitive_load")
        assert abs(cl_delta.delta - 0.2) < 0.001
        assert cl_delta.trend == "worsening"

    def test_skips_none_values(self):
        old = {"cognitive_load": 0.5, "missing": None}
        new = {"cognitive_load": 0.7, "missing": 0.3}
        deltas = _diff_signal_dicts(old, new)

        assert len(deltas) == 1
        assert deltas[0].signal_name == "cognitive_load"

    def test_skips_small_deltas(self):
        old = {"cognitive_load": 0.5}
        new = {"cognitive_load": 0.500001}
        deltas = _diff_signal_dicts(old, new, threshold=0.01)

        assert len(deltas) == 0


class TestTensorSnapshotDiff:
    def test_basic_diff(self):
        old = TensorSnapshot(
            tool_version="0.7.0",
            timestamp="2025-01-01T00:00:00Z",
            analyzed_path="/tmp",
            file_signals={"a.py": {"cognitive_load": 0.5}},
            global_signals={"modularity": 0.6},
        )
        new = TensorSnapshot(
            tool_version="0.7.0",
            timestamp="2025-01-02T00:00:00Z",
            analyzed_path="/tmp",
            file_signals={"a.py": {"cognitive_load": 0.7}},
            global_signals={"modularity": 0.7},
        )

        diff = diff_tensor_snapshots(old, new)

        assert isinstance(diff, TensorSnapshotDiff)
        assert diff.old_timestamp == "2025-01-01T00:00:00Z"
        assert diff.new_timestamp == "2025-01-02T00:00:00Z"

    def test_detects_file_additions(self):
        old = TensorSnapshot(
            tool_version="0.7.0",
            timestamp="2025-01-01T00:00:00Z",
            analyzed_path="/tmp",
            file_signals={"a.py": {}},
        )
        new = TensorSnapshot(
            tool_version="0.7.0",
            timestamp="2025-01-02T00:00:00Z",
            analyzed_path="/tmp",
            file_signals={"a.py": {}, "b.py": {}},
        )

        diff = diff_tensor_snapshots(old, new)
        assert "b.py" in diff.files_added
        assert len(diff.files_removed) == 0

    def test_detects_file_removals(self):
        old = TensorSnapshot(
            tool_version="0.7.0",
            timestamp="2025-01-01T00:00:00Z",
            analyzed_path="/tmp",
            file_signals={"a.py": {}, "b.py": {}},
        )
        new = TensorSnapshot(
            tool_version="0.7.0",
            timestamp="2025-01-02T00:00:00Z",
            analyzed_path="/tmp",
            file_signals={"a.py": {}},
        )

        diff = diff_tensor_snapshots(old, new)
        assert "b.py" in diff.files_removed
        assert len(diff.files_added) == 0

    def test_computes_signal_deltas(self):
        old = TensorSnapshot(
            tool_version="0.7.0",
            timestamp="2025-01-01T00:00:00Z",
            analyzed_path="/tmp",
            file_signals={"a.py": {"cognitive_load": 0.5, "cohesion": 0.8}},
        )
        new = TensorSnapshot(
            tool_version="0.7.0",
            timestamp="2025-01-02T00:00:00Z",
            analyzed_path="/tmp",
            file_signals={"a.py": {"cognitive_load": 0.7, "cohesion": 0.6}},
        )

        diff = diff_tensor_snapshots(old, new)
        assert "a.py" in diff.signal_deltas
        deltas = diff.signal_deltas["a.py"]
        assert len(deltas) == 2

    def test_classifies_worsening_files(self):
        old = TensorSnapshot(
            tool_version="0.7.0",
            timestamp="2025-01-01T00:00:00Z",
            analyzed_path="/tmp",
            file_signals={"a.py": {"cognitive_load": 0.3, "risk_score": 0.2}},
        )
        new = TensorSnapshot(
            tool_version="0.7.0",
            timestamp="2025-01-02T00:00:00Z",
            analyzed_path="/tmp",
            file_signals={"a.py": {"cognitive_load": 0.7, "risk_score": 0.8}},
        )

        diff = diff_tensor_snapshots(old, new)
        assert "a.py" in diff.worsening_files

    def test_classifies_improving_files(self):
        old = TensorSnapshot(
            tool_version="0.7.0",
            timestamp="2025-01-01T00:00:00Z",
            analyzed_path="/tmp",
            file_signals={"a.py": {"cognitive_load": 0.7, "risk_score": 0.8}},
        )
        new = TensorSnapshot(
            tool_version="0.7.0",
            timestamp="2025-01-02T00:00:00Z",
            analyzed_path="/tmp",
            file_signals={"a.py": {"cognitive_load": 0.3, "risk_score": 0.2}},
        )

        diff = diff_tensor_snapshots(old, new)
        assert "a.py" in diff.improving_files


class TestFindingLifecycle:
    def test_new_findings(self):
        old = TensorSnapshot(
            tool_version="0.7.0",
            timestamp="2025-01-01T00:00:00Z",
            analyzed_path="/tmp",
            findings=[],
        )
        new = TensorSnapshot(
            tool_version="0.7.0",
            timestamp="2025-01-02T00:00:00Z",
            analyzed_path="/tmp",
            findings=[_make_finding_record(identity_key="new1")],
        )

        diff = diff_tensor_snapshots(old, new)
        assert len(diff.new_findings) == 1
        assert diff.finding_deltas[0].status == "new"

    def test_resolved_findings(self):
        old = TensorSnapshot(
            tool_version="0.7.0",
            timestamp="2025-01-01T00:00:00Z",
            analyzed_path="/tmp",
            findings=[_make_finding_record(identity_key="old1")],
        )
        new = TensorSnapshot(
            tool_version="0.7.0",
            timestamp="2025-01-02T00:00:00Z",
            analyzed_path="/tmp",
            findings=[],
        )

        diff = diff_tensor_snapshots(old, new)
        assert len(diff.resolved_findings) == 1
        assert diff.finding_deltas[0].status == "resolved"

    def test_persisting_findings(self):
        finding = _make_finding_record(identity_key="persist1")
        old = TensorSnapshot(
            tool_version="0.7.0",
            timestamp="2025-01-01T00:00:00Z",
            analyzed_path="/tmp",
            findings=[finding],
        )
        new = TensorSnapshot(
            tool_version="0.7.0",
            timestamp="2025-01-02T00:00:00Z",
            analyzed_path="/tmp",
            findings=[finding],
        )

        diff = diff_tensor_snapshots(old, new)
        assert len(diff.new_findings) == 0
        assert len(diff.resolved_findings) == 0
        persisting = [d for d in diff.finding_deltas if d.status == "persisting"]
        assert len(persisting) == 1

    def test_debt_velocity_positive(self):
        """More new findings than resolved = positive debt velocity."""
        old = TensorSnapshot(
            tool_version="0.7.0",
            timestamp="2025-01-01T00:00:00Z",
            analyzed_path="/tmp",
            findings=[_make_finding_record(identity_key="resolved1")],
        )
        new = TensorSnapshot(
            tool_version="0.7.0",
            timestamp="2025-01-02T00:00:00Z",
            analyzed_path="/tmp",
            findings=[
                _make_finding_record(identity_key="new1"),
                _make_finding_record(identity_key="new2"),
            ],
        )

        diff = diff_tensor_snapshots(old, new)
        assert diff.debt_velocity == 1  # 2 new - 1 resolved

    def test_debt_velocity_negative(self):
        """More resolved than new = negative debt velocity (good!)."""
        old = TensorSnapshot(
            tool_version="0.7.0",
            timestamp="2025-01-01T00:00:00Z",
            analyzed_path="/tmp",
            findings=[
                _make_finding_record(identity_key="resolved1"),
                _make_finding_record(identity_key="resolved2"),
            ],
        )
        new = TensorSnapshot(
            tool_version="0.7.0",
            timestamp="2025-01-02T00:00:00Z",
            analyzed_path="/tmp",
            findings=[_make_finding_record(identity_key="new1")],
        )

        diff = diff_tensor_snapshots(old, new)
        assert diff.debt_velocity == -1  # 1 new - 2 resolved

    def test_regression_detection(self):
        """Finding that was resolved but comes back is a regression."""
        finding = _make_finding_record(identity_key="regress1")
        old = TensorSnapshot(
            tool_version="0.7.0",
            timestamp="2025-01-01T00:00:00Z",
            analyzed_path="/tmp",
            findings=[],
        )
        new = TensorSnapshot(
            tool_version="0.7.0",
            timestamp="2025-01-02T00:00:00Z",
            analyzed_path="/tmp",
            findings=[finding],
        )

        # Simulate finding_lifecycle data showing this was previously resolved
        lifecycle = {"regress1": {"current_status": "resolved", "persistence_count": 2}}
        diff = diff_tensor_snapshots(old, new, finding_lifecycle=lifecycle)

        regressions = [d for d in diff.finding_deltas if d.status == "regression"]
        assert len(regressions) == 1
        assert regressions[0].persistence_count == 3  # 2 + 1


class TestV1SnapshotDiff:
    def test_basic_v1_diff(self):
        """Test that V1 diff still works."""
        old = Snapshot(
            tool_version="0.6.0",
            timestamp="2025-01-01T00:00:00Z",
            analyzed_path="/tmp",
            file_signals={"a.py": {"cognitive_load": 0.5}},
        )
        new = Snapshot(
            tool_version="0.6.0",
            timestamp="2025-01-02T00:00:00Z",
            analyzed_path="/tmp",
            file_signals={"a.py": {"cognitive_load": 0.7}},
        )

        diff = diff_snapshots(old, new)
        assert diff.old_timestamp == "2025-01-01T00:00:00Z"
        assert len(diff.file_deltas) > 0
