"""Tests for server.api.build_dashboard_state."""

from __future__ import annotations

from shannon_insight.insights.models import Evidence, Finding, InsightResult, StoreSummary
from shannon_insight.persistence.models import TensorSnapshot
from shannon_insight.server.api import CATEGORY_MAP, build_dashboard_state


def _make_finding(
    finding_type: str = "high_risk_hub",
    severity: float = 0.85,
    files: list[str] | None = None,
) -> Finding:
    return Finding(
        finding_type=finding_type,
        severity=severity,
        title=f"Test {finding_type}",
        files=files or ["src/foo.py"],
        evidence=[
            Evidence(
                signal="pagerank",
                value=0.95,
                percentile=98.0,
                description="top 2%",
            )
        ],
        suggestion="Consider refactoring",
    )


def _make_snapshot(
    file_signals: dict | None = None,
    global_signals: dict | None = None,
) -> TensorSnapshot:
    return TensorSnapshot(
        file_count=10,
        module_count=3,
        commits_analyzed=100,
        timestamp="2024-01-01T00:00:00",
        commit_sha="abc123",
        file_signals=file_signals
        or {
            "src/foo.py": {
                "lines": 200,
                "risk_score": 0.7,
                "pagerank": 0.15,
                "blast_radius_size": 10,
                "total_changes": 30,
                "churn_cv": 1.2,
                "bus_factor": 2.0,
                "cognitive_load": 8.5,
                "file_health_score": 0.6,
                "role": "SERVICE",
                "is_orphan": False,
            },
        },
        global_signals=global_signals
        or {
            "codebase_health": 0.65,
            "modularity": 0.45,
        },
    )


class TestCategoryMap:
    """Verify all categories have expected finder types."""

    def test_all_categories_present(self):
        cats = set(CATEGORY_MAP.values())
        assert cats == {"incomplete", "fragile", "tangled", "team"}

    def test_hollow_code_is_incomplete(self):
        assert CATEGORY_MAP["hollow_code"] == "incomplete"

    def test_high_risk_hub_is_fragile(self):
        assert CATEGORY_MAP["high_risk_hub"] == "fragile"

    def test_layer_violation_is_tangled(self):
        assert CATEGORY_MAP["layer_violation"] == "tangled"

    def test_knowledge_silo_is_team(self):
        assert CATEGORY_MAP["knowledge_silo"] == "team"


class TestBuildDashboardState:
    """Test the full state builder."""

    def test_basic_structure(self):
        result = InsightResult(
            findings=[_make_finding()],
            store_summary=StoreSummary(total_files=10),
        )
        snapshot = _make_snapshot()

        state = build_dashboard_state(result, snapshot)

        assert "health" in state
        assert "health_label" in state
        assert "categories" in state
        assert "files" in state
        assert "global_signals" in state
        assert "concerns" in state
        assert state["file_count"] == 10
        assert state["commit_sha"] == "abc123"

    def test_health_score_mapped(self):
        result = InsightResult(findings=[], store_summary=StoreSummary())
        snapshot = _make_snapshot(global_signals={"codebase_health": 0.8})
        state = build_dashboard_state(result, snapshot)

        # display_score(0.8) = 0.8 * 9 + 1 = 8.2
        assert state["health"] == 8.2
        assert state["health_label"] == "Healthy"

    def test_categories_populated(self):
        findings = [
            _make_finding("high_risk_hub", severity=0.9),
            _make_finding("hollow_code", severity=0.7),
        ]
        result = InsightResult(
            findings=findings,
            store_summary=StoreSummary(),
        )
        snapshot = _make_snapshot()
        state = build_dashboard_state(result, snapshot)

        assert state["categories"]["fragile"]["count"] == 1
        assert state["categories"]["incomplete"]["count"] == 1
        assert state["categories"]["tangled"]["count"] == 0

    def test_file_signals_present(self):
        result = InsightResult(findings=[], store_summary=StoreSummary())
        snapshot = _make_snapshot()
        state = build_dashboard_state(result, snapshot)

        assert "src/foo.py" in state["files"]
        f = state["files"]["src/foo.py"]
        assert f["role"] == "SERVICE"
        assert f["lines"] == 200
        assert "risk_score" in f

    def test_focus_point_when_available(self):
        findings = [_make_finding("high_risk_hub", files=["src/foo.py"])]
        result = InsightResult(
            findings=findings,
            store_summary=StoreSummary(),
        )
        snapshot = _make_snapshot()
        state = build_dashboard_state(result, snapshot)

        # May or may not produce a focus depending on actionability
        # Just check the key exists
        assert "focus" in state

    def test_empty_analysis(self):
        result = InsightResult(findings=[], store_summary=StoreSummary())
        snapshot = TensorSnapshot()
        state = build_dashboard_state(result, snapshot)

        assert state["file_count"] == 0
        assert state["categories"]["incomplete"]["count"] == 0
        assert state["files"] == {}

    def test_findings_serialized(self):
        finding = _make_finding()
        result = InsightResult(
            findings=[finding],
            store_summary=StoreSummary(),
        )
        snapshot = _make_snapshot()
        state = build_dashboard_state(result, snapshot)

        cat = state["categories"]["fragile"]
        assert len(cat["findings"]) == 1
        f = cat["findings"][0]
        assert f["finding_type"] == "high_risk_hub"
        assert f["severity_label"] in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO")
        assert "evidence" in f
        assert len(f["evidence"]) == 1
        assert f["evidence"][0]["signal"] == "pagerank"

    def test_html_escaping_in_paths(self):
        """Paths with special chars should be escaped."""
        snapshot = _make_snapshot(
            file_signals={
                "src/<script>.py": {
                    "lines": 10,
                    "risk_score": 0.1,
                    "file_health_score": 0.9,
                    "role": "UNKNOWN",
                },
            }
        )
        result = InsightResult(findings=[], store_summary=StoreSummary())
        state = build_dashboard_state(result, snapshot)

        # The key should be HTML-escaped
        assert "src/&lt;script&gt;.py" in state["files"]
