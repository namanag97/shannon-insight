"""Tests for phase validation contracts.

Tests cover:
    - validate_after_scanning: empty store, file_syntax presence
    - validate_after_structural: graceful skip, orphan nodes, reverse adjacency
    - validate_signal_field: path coverage, tier validation, NaN/Inf detection
    - run_all_validations: collects errors without raising
    - PhaseValidationError: basic exception behavior
"""

import pytest

from shannon_insight.insights.store import AnalysisStore
from shannon_insight.insights.validation import (
    PhaseValidationError,
    run_all_validations,
    validate_after_scanning,
    validate_after_structural,
    validate_signal_field,
)
from shannon_insight.signals.models import FileSignals, SignalField


class MockFileSyntax:
    """Mock FileSyntax for testing."""

    def __init__(self, path: str):
        self.path = path


class MockGraph:
    """Mock graph for structural validation."""

    def __init__(self, nodes: set[str], adjacency: dict[str, list[str]] | None = None):
        self.all_nodes = nodes
        self.adjacency = adjacency or {}
        # Build reverse from adjacency
        self.reverse: dict[str, list[str]] = {}
        for src, targets in self.adjacency.items():
            for tgt in targets:
                if tgt not in self.reverse:
                    self.reverse[tgt] = []
                self.reverse[tgt].append(src)


class MockCodebaseAnalysis:
    """Mock codebase analysis."""

    def __init__(self, graph: MockGraph):
        self.graph = graph


# ── Scanning Validation ─────────────────────────────────────────────


class TestValidateAfterScanning:
    """Test validation after scanning phase."""

    def test_passes_with_files(self):
        """Passes when file_syntax has files."""
        store = AnalysisStore()
        store.file_syntax.set({"/a.py": MockFileSyntax("/a.py"), "/b.py": MockFileSyntax("/b.py")}, "parser")
        validate_after_scanning(store)  # Should not raise

    def test_fails_with_no_files(self):
        """Fails when scanner produced 0 files."""
        store = AnalysisStore()
        # file_syntax not set, or set to empty
        with pytest.raises(PhaseValidationError, match="produced 0 files"):
            validate_after_scanning(store)

    def test_fails_with_empty_file_syntax(self):
        """Fails when file_syntax is empty dict."""
        store = AnalysisStore()
        store.file_syntax.set({}, "parser")
        with pytest.raises(PhaseValidationError, match="produced 0 files"):
            validate_after_scanning(store)

    def test_passes_with_multiple_files(self):
        """Passes when file_syntax has multiple files."""
        store = AnalysisStore()
        store.file_syntax.set({
            "/a.py": MockFileSyntax("/a.py"),
            "/b.py": MockFileSyntax("/b.py"),
            "/c.py": MockFileSyntax("/c.py"),
        }, "parser")
        validate_after_scanning(store)  # Should not raise


# ── Structural Validation ────────────────────────────────────────────


class TestValidateAfterStructural:
    """Test validation after structural analysis phase."""

    def test_passes_when_structural_not_available(self):
        """Passes when structural slot is not populated (graceful skip)."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]
        validate_after_structural(store)  # Should not raise

    def test_passes_with_consistent_graph(self):
        """Passes when graph nodes match scanned files."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py"), MockFileMetrics("/b.py")]
        graph = MockGraph({"/a.py", "/b.py"}, {"/a.py": ["/b.py"]})
        store.structural.set(MockCodebaseAnalysis(graph), "structural_analyzer")
        validate_after_structural(store)  # Should not raise

    def test_passes_with_empty_graph(self):
        """Passes when graph has no nodes (subset of file_metrics)."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]
        graph = MockGraph(set())
        store.structural.set(MockCodebaseAnalysis(graph), "structural_analyzer")
        validate_after_structural(store)  # Should not raise

    def test_fails_with_orphan_nodes(self):
        """Fails when graph has nodes not in scanned files."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]
        graph = MockGraph({"/a.py", "/orphan.py"})
        store.structural.set(MockCodebaseAnalysis(graph), "structural_analyzer")
        with pytest.raises(PhaseValidationError, match="nodes not in scanned files"):
            validate_after_structural(store)

    def test_fails_with_multiple_orphan_nodes(self):
        """Reports count of orphan nodes."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]
        graph = MockGraph({"/a.py", "/orphan1.py", "/orphan2.py", "/orphan3.py"})
        store.structural.set(MockCodebaseAnalysis(graph), "structural_analyzer")
        with pytest.raises(PhaseValidationError, match="3 nodes"):
            validate_after_structural(store)

    def test_fails_with_inconsistent_reverse(self):
        """Fails when reverse adjacency is inconsistent."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py"), MockFileMetrics("/b.py")]
        # Manually create inconsistent graph
        graph = MockGraph({"/a.py", "/b.py"})
        graph.adjacency = {"/a.py": ["/b.py"]}
        graph.reverse = {}  # Should have /b.py -> [/a.py]
        store.structural.set(MockCodebaseAnalysis(graph), "structural_analyzer")
        with pytest.raises(PhaseValidationError, match="reverse is inconsistent"):
            validate_after_structural(store)

    def test_passes_with_no_edges(self):
        """Passes when graph has nodes but no edges."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py"), MockFileMetrics("/b.py")]
        graph = MockGraph({"/a.py", "/b.py"}, {})
        store.structural.set(MockCodebaseAnalysis(graph), "structural_analyzer")
        validate_after_structural(store)  # Should not raise


# ── Signal Field Validation ──────────────────────────────────────────


class TestValidateSignalField:
    """Test validation after signal fusion phase."""

    def test_passes_when_signal_field_not_available(self):
        """Passes when signal_field slot is not populated."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]
        validate_signal_field(store)  # Should not raise

    def test_passes_with_matching_paths(self):
        """Passes when SignalField covers all scanned files."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py"), MockFileMetrics("/b.py")]
        sf = SignalField(
            per_file={
                "/a.py": FileSignals(path="/a.py"),
                "/b.py": FileSignals(path="/b.py"),
            }
        )
        store.signal_field.set(sf, "signal_fusion")
        validate_signal_field(store)  # Should not raise

    def test_fails_with_missing_paths(self):
        """Fails when SignalField is missing files."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py"), MockFileMetrics("/b.py")]
        sf = SignalField(per_file={"/a.py": FileSignals(path="/a.py")})
        store.signal_field.set(sf, "signal_fusion")
        with pytest.raises(PhaseValidationError, match="missing files"):
            validate_signal_field(store)

    def test_fails_with_extra_paths(self):
        """Fails when SignalField has extra files."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]
        sf = SignalField(
            per_file={
                "/a.py": FileSignals(path="/a.py"),
                "/extra.py": FileSignals(path="/extra.py"),
            }
        )
        store.signal_field.set(sf, "signal_fusion")
        with pytest.raises(PhaseValidationError, match="extra files"):
            validate_signal_field(store)

    def test_fails_with_invalid_tier(self):
        """Fails when tier is not a valid value."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]
        sf = SignalField(tier="INVALID", per_file={"/a.py": FileSignals(path="/a.py")})
        store.signal_field.set(sf, "signal_fusion")
        with pytest.raises(PhaseValidationError, match="tier.*not valid"):
            validate_signal_field(store)

    def test_passes_with_valid_tiers(self):
        """Passes with each valid tier value."""
        for tier in ("ABSOLUTE", "BAYESIAN", "FULL"):
            store = AnalysisStore()
            store.file_metrics = [MockFileMetrics("/a.py")]
            sf = SignalField(tier=tier, per_file={"/a.py": FileSignals(path="/a.py")})
            store.signal_field.set(sf, "signal_fusion")
            validate_signal_field(store)  # Should not raise

    def test_fails_with_nan_signal(self):
        """Fails when a signal has NaN value."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]
        fs = FileSignals(path="/a.py", pagerank=float("nan"))
        sf = SignalField(per_file={"/a.py": fs})
        store.signal_field.set(sf, "signal_fusion")
        with pytest.raises(PhaseValidationError, match="NaN/Inf detected.*pagerank"):
            validate_signal_field(store)

    def test_fails_with_inf_signal(self):
        """Fails when a signal has Inf value."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]
        fs = FileSignals(path="/a.py", cognitive_load=float("inf"))
        sf = SignalField(per_file={"/a.py": fs})
        store.signal_field.set(sf, "signal_fusion")
        with pytest.raises(PhaseValidationError, match="NaN/Inf detected.*cognitive_load"):
            validate_signal_field(store)

    def test_fails_with_negative_inf_signal(self):
        """Fails when a signal has -Inf value."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]
        fs = FileSignals(path="/a.py", risk_score=float("-inf"))
        sf = SignalField(per_file={"/a.py": fs})
        store.signal_field.set(sf, "signal_fusion")
        with pytest.raises(PhaseValidationError, match="NaN/Inf detected.*risk_score"):
            validate_signal_field(store)

    def test_fails_with_nan_percentile(self):
        """Fails when a percentile value is NaN."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]
        fs = FileSignals(path="/a.py", percentiles={"pagerank": float("nan")})
        sf = SignalField(per_file={"/a.py": fs})
        store.signal_field.set(sf, "signal_fusion")
        with pytest.raises(PhaseValidationError, match="NaN/Inf in percentile.*pagerank"):
            validate_signal_field(store)

    def test_fails_with_inf_percentile(self):
        """Fails when a percentile value is Inf."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]
        fs = FileSignals(path="/a.py", percentiles={"betweenness": float("inf")})
        sf = SignalField(per_file={"/a.py": fs})
        store.signal_field.set(sf, "signal_fusion")
        with pytest.raises(PhaseValidationError, match="NaN/Inf in percentile.*betweenness"):
            validate_signal_field(store)

    def test_passes_with_valid_numeric_signals(self):
        """Passes when all numeric signals are valid finite values."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]
        fs = FileSignals(
            path="/a.py",
            pagerank=0.05,
            betweenness=0.1,
            cognitive_load=15.0,
            risk_score=0.7,
            percentiles={"pagerank": 0.95, "betweenness": 0.8},
        )
        sf = SignalField(per_file={"/a.py": fs})
        store.signal_field.set(sf, "signal_fusion")
        validate_signal_field(store)  # Should not raise

    def test_passes_with_zero_values(self):
        """Passes when signals are zero (valid finite value)."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]
        fs = FileSignals(path="/a.py")  # All defaults are 0
        sf = SignalField(per_file={"/a.py": fs})
        store.signal_field.set(sf, "signal_fusion")
        validate_signal_field(store)  # Should not raise

    def test_nan_in_second_file_caught(self):
        """NaN in any file is caught, not just the first."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py"), MockFileMetrics("/b.py")]
        fs_a = FileSignals(path="/a.py")  # Valid
        fs_b = FileSignals(path="/b.py", raw_risk=float("nan"))  # NaN
        sf = SignalField(per_file={"/a.py": fs_a, "/b.py": fs_b})
        store.signal_field.set(sf, "signal_fusion")
        with pytest.raises(PhaseValidationError, match="NaN/Inf detected.*/b.py"):
            validate_signal_field(store)


# ── run_all_validations ──────────────────────────────────────────────


class TestRunAllValidations:
    """Test the error-collecting validation runner."""

    def test_returns_empty_for_valid_store(self):
        """Returns empty list when all validations pass."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]
        errors = run_all_validations(store)
        assert errors == []

    def test_collects_scanning_error(self):
        """Collects scanning validation error."""
        store = AnalysisStore()
        store.file_metrics = []  # Will fail scanning validation
        errors = run_all_validations(store)
        assert len(errors) == 1
        assert "produced 0 files" in errors[0]

    def test_collects_multiple_errors(self):
        """Collects errors from multiple validators."""
        store = AnalysisStore()
        store.file_metrics = []  # Will fail scanning validation
        # Structural won't fail (graceful skip when not available)
        # Signal field won't fail (graceful skip when not available)
        errors = run_all_validations(store)
        assert len(errors) >= 1

    def test_does_not_raise(self):
        """run_all_validations never raises, it collects."""
        store = AnalysisStore()
        store.file_metrics = []
        # Should not raise, should return errors
        errors = run_all_validations(store)
        assert isinstance(errors, list)


# ── PhaseValidationError ─────────────────────────────────────────────


class TestPhaseValidationError:
    """Test the error class."""

    def test_error_message(self):
        """Error includes message."""
        err = PhaseValidationError("Test message")
        assert "Test message" in str(err)

    def test_is_exception(self):
        """PhaseValidationError is a valid Exception."""
        err = PhaseValidationError("test")
        assert isinstance(err, Exception)

    def test_can_be_caught_as_exception(self):
        """Can be caught as a generic Exception."""
        with pytest.raises(Exception, match="contract violated"):
            raise PhaseValidationError("contract violated")

    def test_str_representation(self):
        """String representation includes the message."""
        err = PhaseValidationError("Scanner produced 0 files")
        assert str(err) == "Scanner produced 0 files"
