"""Tests for the change-scoped analysis module."""
import sys
sys.path.insert(0, "src")

import pytest
from shannon_insight.snapshot.models import Snapshot, FindingRecord, EvidenceRecord
from shannon_insight.diff.scope import compute_blast_radius, build_scoped_report


def _snap(file_signals=None, findings=None, edges=None):
    return Snapshot(
        tool_version="0.6.0", timestamp="2025-01-01T00:00:00Z", analyzed_path="/tmp",
        file_count=len(file_signals or {}),
        file_signals=file_signals or {},
        findings=findings or [],
        dependency_edges=edges or [],
    )


def _finding(ftype, key, severity=0.5, files=None):
    return FindingRecord(ftype, key, severity, f"{ftype} finding", files or ["a.py"], [], "fix")


class TestBlastRadius:
    def test_simple_chain(self):
        # a -> b -> c  (blast radius of c = {b, a})
        snap = _snap(edges=[("a.py", "b.py"), ("b.py", "c.py")])
        blast = compute_blast_radius(["c.py"], snap)
        assert set(blast) == {"a.py", "b.py"}

    def test_no_dependents(self):
        snap = _snap(edges=[("a.py", "b.py")])
        blast = compute_blast_radius(["a.py"], snap)
        assert blast == []

    def test_diamond(self):
        # a -> c, b -> c, d -> a, d -> b
        snap = _snap(edges=[("a.py", "c.py"), ("b.py", "c.py"), ("d.py", "a.py"), ("d.py", "b.py")])
        blast = compute_blast_radius(["c.py"], snap)
        assert set(blast) == {"a.py", "b.py", "d.py"}

    def test_changed_files_excluded(self):
        snap = _snap(edges=[("a.py", "b.py")])
        blast = compute_blast_radius(["b.py"], snap)
        assert "b.py" not in blast


class TestScopedReport:
    def test_filters_direct_findings(self):
        snap = _snap(
            file_signals={"a.py": {"cognitive_load": 0.5}, "b.py": {"cognitive_load": 0.3}},
            findings=[
                _finding("god_file", "gf1", files=["a.py"]),
                _finding("god_file", "gf2", files=["b.py"]),
            ],
        )
        report = build_scoped_report(["a.py"], snap)
        assert len(report.direct_findings) == 1
        assert report.direct_findings[0].identity_key == "gf1"

    def test_risk_level_low(self):
        snap = _snap(
            file_signals={"a.py": {"cognitive_load": 0.2}},
            findings=[],
        )
        report = build_scoped_report(["a.py"], snap)
        assert report.risk_level == "low"

    def test_risk_level_critical(self):
        snap = _snap(
            file_signals={"a.py": {"cognitive_load": 0.9}},
            findings=[_finding("high_risk_hub", "hrh1", severity=0.9, files=["a.py"])],
        )
        report = build_scoped_report(["a.py"], snap)
        assert report.risk_level == "critical"

    def test_blast_radius_findings(self):
        snap = _snap(
            file_signals={"a.py": {}, "b.py": {}},
            findings=[_finding("god_file", "gf1", files=["b.py"])],
            edges=[("b.py", "a.py")],
        )
        report = build_scoped_report(["a.py"], snap)
        # b.py is in blast radius of a.py, and has a finding
        assert len(report.blast_findings) == 1
