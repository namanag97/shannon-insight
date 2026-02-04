"""Tests for baseline and diff mode (Phase 4)."""

import json
import tempfile
import pytest
from pathlib import Path

from shannon_insight.models import (
    AnomalyReport, Primitives, DiffReport,
)
from shannon_insight.baseline import save_baseline, load_baseline, diff_reports


def _make_report(file="test.go", score=1.5, confidence=0.6):
    prims = Primitives(
        structural_entropy=0.7,
        network_centrality=0.5,
        churn_volatility=0.3,
        semantic_coherence=0.4,
        cognitive_load=0.6,
    )
    norm = Primitives(
        structural_entropy=1.2,
        network_centrality=0.8,
        churn_volatility=-0.5,
        semantic_coherence=-1.0,
        cognitive_load=1.5,
    )
    return AnomalyReport(
        file=file,
        overall_score=score,
        confidence=confidence,
        primitives=prims,
        normalized_primitives=norm,
        anomaly_flags=["high_cognitive_load"],
        root_causes=["High cognitive load"],
        recommendations=["Split file into smaller modules"],
    )


class TestSaveAndLoadBaseline:
    def test_roundtrip(self):
        reports = [_make_report("a.go", 1.0), _make_report("b.go", 2.5)]

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        save_baseline(reports, path)
        loaded = load_baseline(path)

        assert len(loaded) == 2
        assert loaded["a.go"] == pytest.approx(1.0)
        assert loaded["b.go"] == pytest.approx(2.5)

    def test_load_missing_file(self):
        loaded = load_baseline("/nonexistent/path.json")
        assert loaded == {}


class TestDiffReports:
    def test_new_file(self):
        reports = [_make_report("new.go", 1.0)]
        baseline = {}  # nothing in baseline
        diffs = diff_reports(reports, baseline)
        assert len(diffs) == 1
        assert diffs[0].status == "new"
        assert diffs[0].previous_score is None

    def test_regressed_file(self):
        reports = [_make_report("a.go", 2.0)]
        baseline = {"a.go": 1.0}
        diffs = diff_reports(reports, baseline)
        assert len(diffs) == 1
        assert diffs[0].status == "regressed"
        assert diffs[0].score_delta == pytest.approx(1.0)

    def test_improved_file(self):
        reports = [_make_report("a.go", 0.5)]
        baseline = {"a.go": 1.5}
        diffs = diff_reports(reports, baseline)
        assert len(diffs) == 1
        assert diffs[0].status == "improved"
        assert diffs[0].score_delta == pytest.approx(-1.0)

    def test_changed_files_filter(self):
        reports = [_make_report("a.go", 2.0), _make_report("b.go", 1.0)]
        baseline = {"a.go": 1.0, "b.go": 1.0}
        diffs = diff_reports(reports, baseline, changed_files={"a.go"})
        assert len(diffs) == 1
        assert diffs[0].file == "a.go"

    def test_sort_order(self):
        reports = [
            _make_report("improved.go", 0.5),
            _make_report("regressed.go", 3.0),
            _make_report("new.go", 1.0),
        ]
        baseline = {"improved.go": 1.5, "regressed.go": 1.0}
        diffs = diff_reports(reports, baseline)
        statuses = [d.status for d in diffs]
        assert statuses == ["regressed", "new", "improved"]
