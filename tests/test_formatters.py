"""Tests for the formatters package (Phase 2)."""

import json
import pytest

from shannon_insight.models import (
    AnomalyReport, Primitives, AnalysisContext, DiffReport,
)
from shannon_insight.formatters import (
    get_formatter,
    RichFormatter,
    JsonFormatter,
    CsvFormatter,
    QuietFormatter,
    DiffFormatter,
    GithubFormatter,
)
from shannon_insight.config import default_settings


def _make_report(file="test.go", score=1.5, confidence=0.6):
    """Create a minimal AnomalyReport for testing."""
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


def _make_context():
    return AnalysisContext(
        total_files_scanned=10,
        detected_languages=["go", "python"],
        settings=default_settings,
        top_n=5,
    )


class TestGetFormatter:
    def test_known_formatters(self):
        for name in ("rich", "json", "csv", "quiet", "github"):
            fmt = get_formatter(name)
            assert fmt is not None

    def test_unknown_formatter(self):
        with pytest.raises(ValueError, match="Unknown formatter"):
            get_formatter("xml")


class TestJsonFormatter:
    def test_format_returns_valid_json(self):
        fmt = JsonFormatter()
        ctx = _make_context()
        reports = [_make_report(), _make_report("other.go", 2.0, 0.8)]
        result = fmt.format(reports, ctx)
        data = json.loads(result)
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["file"] == "test.go"


class TestCsvFormatter:
    def test_format_returns_csv(self):
        fmt = CsvFormatter()
        ctx = _make_context()
        reports = [_make_report()]
        result = fmt.format(reports, ctx)
        lines = result.strip().split("\n")
        assert len(lines) == 2  # header + 1 row
        assert "test.go" in lines[1]


class TestQuietFormatter:
    def test_format_returns_file_paths(self):
        fmt = QuietFormatter()
        ctx = _make_context()
        reports = [_make_report("a.go"), _make_report("b.go")]
        result = fmt.format(reports, ctx)
        assert result == "a.go\nb.go"


class TestDiffFormatter:
    def test_renders_diffs(self, capsys):
        fmt = DiffFormatter()
        ctx = _make_context()
        report = _make_report()
        diffs = [
            DiffReport(file="test.go", status="regressed", current=report,
                       previous_score=1.0, score_delta=0.5),
            DiffReport(file="new.go", status="new", current=report),
        ]
        fmt.render(diffs, ctx)
        # DiffFormatter prints to stderr via rich console — just ensure no crash


class TestGithubFormatter:
    def test_format_reports(self):
        fmt = GithubFormatter()
        ctx = _make_context()
        reports = [_make_report()]
        result = fmt.format(reports, ctx)
        assert "::warning" in result or "::error" in result

    def test_format_diffs(self):
        fmt = GithubFormatter()
        ctx = _make_context()
        report = _make_report()
        diffs = [
            DiffReport(file="test.go", status="regressed", current=report,
                       previous_score=1.0, score_delta=0.5),
        ]
        result = fmt.format(diffs, ctx)
        assert "regressed" in result
        assert "Score Deltas" in result or "Shannon Insight Diff" in result
