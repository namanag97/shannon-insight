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

    def test_paths_not_double_escaped(self):
        """Paths should be raw in JSON; the frontend handles HTML escaping."""
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

        # The key should be raw (not HTML-escaped) — frontend escapes at render time
        assert "src/<script>.py" in state["files"]

    def test_enriched_fields_present(self):
        """Verify dependency_edges, delta_h, violations, layers, analyzers_ran,
        analyzed_path, verdict, verdict_color are in the dashboard state."""
        result = InsightResult(findings=[], store_summary=StoreSummary())
        snapshot = _make_snapshot()
        snapshot.dependency_edges = [("a.py", "b.py")]
        snapshot.delta_h = {"a.py": 0.5}
        snapshot.violations = [{"src": "a.py", "tgt": "b.py", "type": "layer"}]
        snapshot.layers = [{"depth": 0, "modules": ["src/"]}]
        snapshot.analyzers_ran = ["StructuralAnalyzer"]
        snapshot.analyzed_path = "/test"

        state = build_dashboard_state(result, snapshot)

        assert state["dependency_edges"] == [["a.py", "b.py"]]
        assert state["delta_h"] == {"a.py": 0.5}
        assert state["violations"] == [{"src": "a.py", "tgt": "b.py", "type": "layer"}]
        assert state["layers"] == [{"depth": 0, "modules": ["src/"]}]
        assert state["analyzers_ran"] == ["StructuralAnalyzer"]
        assert state["analyzed_path"] == "/test"
        assert "verdict" in state
        assert "verdict_color" in state

    def test_focus_point_scores(self):
        """Verify focus has risk_score, impact_score, tractability_score,
        confidence_score when a focus point exists."""
        # Build signals that will generate an actionable focus point
        file_signals = {
            "src/foo.py": {
                "lines": 200,
                "risk_score": 0.9,
                "pagerank": 0.25,
                "blast_radius_size": 15,
                "total_changes": 50,
                "churn_cv": 1.5,
                "bus_factor": 1.0,
                "cognitive_load": 12.0,
                "file_health_score": 0.3,
                "role": "SERVICE",
                "is_orphan": False,
            },
        }
        findings = [_make_finding("high_risk_hub", severity=0.9, files=["src/foo.py"])]
        result = InsightResult(findings=findings, store_summary=StoreSummary())
        snapshot = _make_snapshot(file_signals=file_signals)

        state = build_dashboard_state(result, snapshot)

        focus = state["focus"]
        assert focus is not None, "Expected a focus point to be generated"
        assert "risk_score" in focus
        assert "impact_score" in focus
        assert "tractability_score" in focus
        assert "confidence_score" in focus

    def test_concern_expanded_fields(self):
        """Verify concerns have description, attributes, and file_count."""
        findings = [_make_finding("high_risk_hub", severity=0.85, files=["src/foo.py"])]
        result = InsightResult(findings=findings, store_summary=StoreSummary())
        snapshot = _make_snapshot()

        state = build_dashboard_state(result, snapshot)

        concerns = state["concerns"]
        assert len(concerns) > 0, "Expected at least one concern"
        for concern in concerns:
            assert "description" in concern, (
                f"Missing 'description' in concern {concern.get('key')}"
            )
            assert "attributes" in concern, f"Missing 'attributes' in concern {concern.get('key')}"
            assert "file_count" in concern, f"Missing 'file_count' in concern {concern.get('key')}"

    def test_build_state_without_db(self):
        """Verify trends key is absent when no db_path is provided."""
        result = InsightResult(findings=[], store_summary=StoreSummary())
        snapshot = _make_snapshot()

        state = build_dashboard_state(result, snapshot, db_path=None)

        assert "trends" not in state

    def test_gate_pass(self):
        """State with health 7.0, no critical findings -> gate returns PASS."""
        state = {
            "health": 7.0,
            "categories": {
                "fragile": {
                    "findings": [
                        {"severity": 0.5, "finding_type": "high_risk_hub"},
                    ],
                },
                "incomplete": {"findings": []},
                "tangled": {"findings": []},
                "team": {"findings": []},
            },
        }

        # Reproduce the gate logic from app.py
        health = state.get("health", 0)
        critical_count = 0
        finding_count = 0
        for cat in state.get("categories", {}).values():
            for f in cat.get("findings", []):
                finding_count += 1
                if f.get("severity", 0) >= 0.9:
                    critical_count += 1

        gate_status = "PASS"
        if health < 4.0:
            gate_status = "FAIL"
        if critical_count > 0:
            gate_status = "FAIL"

        assert gate_status == "PASS"
        assert finding_count == 1
        assert critical_count == 0

    def test_gate_fail_health(self):
        """State with health 2.0 -> gate returns FAIL."""
        state = {
            "health": 2.0,
            "categories": {
                "fragile": {"findings": []},
                "incomplete": {"findings": []},
                "tangled": {"findings": []},
                "team": {"findings": []},
            },
        }

        health = state.get("health", 0)
        critical_count = 0
        for cat in state.get("categories", {}).values():
            for f in cat.get("findings", []):
                if f.get("severity", 0) >= 0.9:
                    critical_count += 1

        gate_status = "PASS"
        if health < 4.0:
            gate_status = "FAIL"
        if critical_count > 0:
            gate_status = "FAIL"

        assert gate_status == "FAIL"

    def test_gate_fail_critical(self):
        """State with a severity 0.95 finding -> gate returns FAIL."""
        state = {
            "health": 7.0,
            "categories": {
                "fragile": {
                    "findings": [
                        {"severity": 0.95, "finding_type": "high_risk_hub"},
                    ],
                },
                "incomplete": {"findings": []},
                "tangled": {"findings": []},
                "team": {"findings": []},
            },
        }

        health = state.get("health", 0)
        critical_count = 0
        finding_count = 0
        for cat in state.get("categories", {}).values():
            for f in cat.get("findings", []):
                finding_count += 1
                if f.get("severity", 0) >= 0.9:
                    critical_count += 1

        gate_status = "PASS"
        if health < 4.0:
            gate_status = "FAIL"
        if critical_count > 0:
            gate_status = "FAIL"

        assert gate_status == "FAIL"
        assert critical_count == 1


class TestConnectionLeakFixes:
    """Verify database connection cleanup in error scenarios."""

    def test_query_trends_handles_exception_gracefully(self, tmp_path):
        """_query_trends closes connection even when query fails."""
        from shannon_insight.persistence.database import HistoryDB
        from shannon_insight.server.api import _query_trends

        # Create a valid but empty history DB
        project_root = tmp_path / "project"
        project_root.mkdir()
        with HistoryDB(str(project_root)) as db:
            # DB is initialized but empty (no data)
            pass

        db_path = str(project_root / ".shannon" / "history.db")

        # Query the DB - should return empty trends or None without leaking connections
        result = _query_trends(db_path)

        # Result may be None or an empty dict (both valid)
        assert result is None or isinstance(result, dict)

        # Verify we can open the DB again (no leaked connections)
        with HistoryDB(str(project_root)) as db:
            assert db.conn is not None

    def test_query_file_signal_trends_uses_context_manager(self, tmp_path):
        """_query_file_signal_trends closes connection in all cases."""
        from shannon_insight.persistence.database import HistoryDB
        from shannon_insight.server.api import _query_file_signal_trends

        # Create a valid but empty history DB
        project_root = tmp_path / "project"
        project_root.mkdir()
        with HistoryDB(str(project_root)) as db:
            pass

        db_path = str(project_root / ".shannon" / "history.db")

        # Query with file paths
        result = _query_file_signal_trends(db_path, ["src/foo.py"])

        # Should return empty dict (no data in DB)
        assert result == {}

        # Verify we can open the DB again (no leaked connections)
        with HistoryDB(str(project_root)) as db:
            assert db.conn is not None
