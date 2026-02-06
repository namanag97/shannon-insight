"""Tests for phase validation contracts."""

import pytest

from shannon_insight.insights.store_v2 import AnalysisStore
from shannon_insight.insights.validation import (
    PhaseValidationError,
    validate_after_scanning,
    validate_after_structural,
    validate_signal_field,
)


class MockFileMetrics:
    """Mock file metrics."""

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


class TestValidateAfterScanning:
    """Test validation after scanning phase."""

    def test_passes_with_files(self):
        """Passes when file_metrics has files."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py"), MockFileMetrics("/b.py")]
        validate_after_scanning(store)  # Should not raise

    def test_fails_with_no_files(self):
        """Fails when scanner produced 0 files."""
        store = AnalysisStore()
        store.file_metrics = []
        with pytest.raises(PhaseValidationError, match="produced 0 files"):
            validate_after_scanning(store)

    def test_passes_with_file_syntax_subset(self):
        """Passes when file_syntax is subset of file_metrics."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py"), MockFileMetrics("/b.py")]
        store.file_syntax.set({"/a.py": object()}, "parser")  # b.py missing is OK
        validate_after_scanning(store)  # Should not raise

    def test_fails_with_extra_file_syntax(self):
        """Fails when file_syntax has paths not in file_metrics."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]
        store.file_syntax.set({"/a.py": object(), "/extra.py": object()}, "parser")
        with pytest.raises(PhaseValidationError, match="not in file_metrics"):
            validate_after_scanning(store)


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

    def test_fails_with_orphan_nodes(self):
        """Fails when graph has nodes not in scanned files."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]
        graph = MockGraph({"/a.py", "/orphan.py"})
        store.structural.set(MockCodebaseAnalysis(graph), "structural_analyzer")
        with pytest.raises(PhaseValidationError, match="nodes not in scanned files"):
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

        class MockSignalField:
            per_file = {"/a.py": object(), "/b.py": object()}

        store.signal_field.set(MockSignalField(), "signal_fusion")
        validate_signal_field(store)  # Should not raise

    def test_fails_with_missing_paths(self):
        """Fails when SignalField is missing files."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py"), MockFileMetrics("/b.py")]

        class MockSignalField:
            per_file = {"/a.py": object()}  # Missing /b.py

        store.signal_field.set(MockSignalField(), "signal_fusion")
        with pytest.raises(PhaseValidationError, match="missing files"):
            validate_signal_field(store)

    def test_fails_with_extra_paths(self):
        """Fails when SignalField has extra files."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]

        class MockSignalField:
            per_file = {"/a.py": object(), "/extra.py": object()}

        store.signal_field.set(MockSignalField(), "signal_fusion")
        with pytest.raises(PhaseValidationError, match="extra files"):
            validate_signal_field(store)


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
