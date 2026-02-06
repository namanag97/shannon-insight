"""Tests for the diff module."""

import sys

sys.path.insert(0, "src")

import pytest

from shannon_insight.persistence.diff_engine import diff_snapshots
from shannon_insight.persistence.models import FindingRecord, Snapshot


def _snap(
    commit=None,
    file_signals=None,
    codebase_signals=None,
    findings=None,
    edges=None,
    ts="2025-01-01T00:00:00Z",
):
    return Snapshot(
        tool_version="0.6.0",
        timestamp=ts,
        analyzed_path="/tmp",
        commit_sha=commit,
        file_count=len(file_signals or {}),
        file_signals=file_signals or {},
        codebase_signals=codebase_signals or {},
        findings=findings or [],
        dependency_edges=edges or [],
    )


def _finding(ftype, key, severity=0.5, files=None):
    return FindingRecord(ftype, key, severity, f"{ftype} finding", files or ["a.py"], [], "fix")


class TestDiffSnapshots:
    def test_new_finding(self):
        old = _snap(findings=[])
        new = _snap(findings=[_finding("god_file", "gf1")])
        diff = diff_snapshots(old, new)
        assert len(diff.new_findings) == 1
        assert diff.new_findings[0].identity_key == "gf1"

    def test_resolved_finding(self):
        old = _snap(findings=[_finding("god_file", "gf1")])
        new = _snap(findings=[])
        diff = diff_snapshots(old, new)
        assert len(diff.resolved_findings) == 1
        assert diff.resolved_findings[0].identity_key == "gf1"

    def test_worsened_severity(self):
        old = _snap(findings=[_finding("god_file", "gf1", severity=0.5)])
        new = _snap(findings=[_finding("god_file", "gf1", severity=0.8)])
        diff = diff_snapshots(old, new)
        assert len(diff.worsened_findings) == 1
        assert diff.worsened_findings[0].severity_delta == pytest.approx(0.3, abs=0.01)

    def test_improved_severity(self):
        old = _snap(findings=[_finding("god_file", "gf1", severity=0.8)])
        new = _snap(findings=[_finding("god_file", "gf1", severity=0.5)])
        diff = diff_snapshots(old, new)
        assert len(diff.improved_findings) == 1

    def test_file_delta_new(self):
        old = _snap(file_signals={})
        new = _snap(file_signals={"a.py": {"cognitive_load": 0.5}})
        diff = diff_snapshots(old, new)
        new_files = [fd for fd in diff.file_deltas if fd.status == "new"]
        assert len(new_files) == 1

    def test_file_delta_removed(self):
        old = _snap(file_signals={"a.py": {"cognitive_load": 0.5}})
        new = _snap(file_signals={})
        diff = diff_snapshots(old, new)
        removed = [fd for fd in diff.file_deltas if fd.status == "removed"]
        assert len(removed) == 1

    def test_metric_direction_cognitive_load(self):
        old = _snap(file_signals={"a.py": {"cognitive_load": 0.5}})
        new = _snap(file_signals={"a.py": {"cognitive_load": 0.8}})
        diff = diff_snapshots(old, new)
        changed = [fd for fd in diff.file_deltas if fd.status == "changed"]
        assert len(changed) == 1
        assert changed[0].metric_deltas["cognitive_load"].direction == "worse"

    def test_metric_direction_semantic_coherence(self):
        old = _snap(file_signals={"a.py": {"semantic_coherence": 0.5}})
        new = _snap(file_signals={"a.py": {"semantic_coherence": 0.8}})
        diff = diff_snapshots(old, new)
        changed = [fd for fd in diff.file_deltas if fd.status == "changed"]
        assert changed[0].metric_deltas["semantic_coherence"].direction == "better"

    def test_codebase_signal_diff(self):
        old = _snap(codebase_signals={"fiedler_value": 0.1, "cycle_count": 5.0})
        new = _snap(codebase_signals={"fiedler_value": 0.2, "cycle_count": 3.0})
        diff = diff_snapshots(old, new)
        assert diff.codebase_deltas["fiedler_value"].direction == "better"
        assert diff.codebase_deltas["cycle_count"].direction == "better"

    def test_with_renames(self):
        old = _snap(file_signals={"old.py": {"cognitive_load": 0.5}})
        new = _snap(file_signals={"new.py": {"cognitive_load": 0.6}})
        diff = diff_snapshots(old, new, renames={"old.py": "new.py"})
        changed = [fd for fd in diff.file_deltas if fd.status == "changed"]
        assert len(changed) == 1
        assert changed[0].filepath == "new.py"
