"""Tests for the formatters package (legacy formatters).

These test the old AnomalyReport-based formatters which are kept for
backward compatibility but not used by the current CLI.
"""

import json

from shannon_insight.config import default_settings
from shannon_insight.formatters.csv_formatter import CsvFormatter
from shannon_insight.formatters.github_formatter import GithubFormatter
from shannon_insight.formatters.json_formatter import JsonFormatter
from shannon_insight.formatters.quiet_formatter import QuietFormatter
from shannon_insight.models import (
    AnalysisContext,
    AnomalyReport,
    Primitives,
)


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


class TestGithubFormatter:
    def test_format_reports(self):
        fmt = GithubFormatter()
        ctx = _make_context()
        reports = [_make_report()]
        result = fmt.format(reports, ctx)
        assert "::warning" in result or "::error" in result
