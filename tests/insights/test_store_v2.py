"""Tests for v2 AnalysisStore with Slot[T] wrapper."""

from collections import Counter

import pytest

from shannon_insight.infrastructure.entities import EntityId, EntityType
from shannon_insight.infrastructure.relations import RelationType
from shannon_insight.infrastructure.signals import Signal
from shannon_insight.insights.store_v2 import AnalysisStore, Slot
from shannon_insight.scanning.models import FileMetrics


class TestSlot:
    """Test Slot[T] generic wrapper."""

    def test_initially_unavailable(self):
        """New slot is not available."""
        slot: Slot[str] = Slot()
        assert slot.available is False

    def test_set_makes_available(self):
        """Setting a value makes slot available."""
        slot: Slot[str] = Slot()
        slot.set("hello", "test_producer")
        assert slot.available is True

    def test_value_property(self):
        """Can get value after setting."""
        slot: Slot[int] = Slot()
        slot.set(42, "test_producer")
        assert slot.value == 42

    def test_value_raises_when_unavailable(self):
        """Accessing value when unavailable raises LookupError."""
        slot: Slot[str] = Slot()
        with pytest.raises(LookupError, match="Slot not populated"):
            _ = slot.value

    def test_value_error_includes_message(self):
        """Error includes the error message if set."""
        slot: Slot[str] = Slot()
        slot.set_error("Git not installed", "temporal_analyzer")
        with pytest.raises(LookupError, match="Git not installed"):
            _ = slot.value

    def test_get_with_default(self):
        """get() returns default when unavailable."""
        slot: Slot[int] = Slot()
        assert slot.get(default=0) == 0
        assert slot.get() is None

    def test_get_returns_value_when_available(self):
        """get() returns value when available."""
        slot: Slot[int] = Slot()
        slot.set(42, "producer")
        assert slot.get(default=0) == 42

    def test_produced_by_tracked(self):
        """Provenance is tracked."""
        slot: Slot[str] = Slot()
        slot.set("data", "graph/algorithms")
        assert slot.produced_by == "graph/algorithms"

    def test_error_tracking(self):
        """Error and producer tracked when set_error called."""
        slot: Slot[str] = Slot()
        slot.set_error("Timeout during computation", "clone_detector")
        assert slot.available is False
        assert slot.error == "Timeout during computation"
        assert slot.produced_by == "clone_detector"


class TestAnalysisStore:
    """Test AnalysisStore with typed Slot fields."""

    def test_has_all_required_slots(self):
        """Store has all slots from spec."""
        store = AnalysisStore()

        # Check all slots exist
        assert hasattr(store, "file_syntax")
        assert hasattr(store, "structural")
        assert hasattr(store, "git_history")
        assert hasattr(store, "churn")
        assert hasattr(store, "cochange")
        assert hasattr(store, "semantics")
        assert hasattr(store, "roles")
        assert hasattr(store, "spectral")
        assert hasattr(store, "clone_pairs")
        assert hasattr(store, "author_distances")
        assert hasattr(store, "architecture")
        assert hasattr(store, "signal_field")

    def test_slots_are_slot_instances(self):
        """All optional fields are Slot instances."""
        store = AnalysisStore()

        assert isinstance(store.file_syntax, Slot)
        assert isinstance(store.structural, Slot)
        assert isinstance(store.git_history, Slot)
        assert isinstance(store.churn, Slot)
        assert isinstance(store.semantics, Slot)
        assert isinstance(store.signal_field, Slot)

    def test_available_initially_contains_files(self):
        """available() initially just contains 'files'."""
        store = AnalysisStore()
        assert "files" in store.available

    def test_available_tracks_populated_slots(self):
        """available() includes slot names when populated."""
        store = AnalysisStore()

        # Initially only files
        avail = store.available
        assert "structural" not in avail

        # After setting structural
        store.structural.set(object(), "structural_analyzer")
        avail = store.available
        assert "structural" in avail

    def test_root_dir_and_file_metrics(self):
        """root_dir and file_metrics are always available."""
        store = AnalysisStore(root_dir="/foo/bar")
        assert store.root_dir == "/foo/bar"
        assert store.file_metrics == []

    def test_file_metrics_mutable(self):
        """Can add file metrics."""
        store = AnalysisStore()
        store.file_metrics.append("file1")
        store.file_metrics.append("file2")
        assert len(store.file_metrics) == 2

    def test_multiple_slots_available(self):
        """Multiple slots can be populated."""
        store = AnalysisStore()
        store.structural.set(object(), "a")
        store.git_history.set(object(), "b")
        store.semantics.set(object(), "c")

        avail = store.available
        assert "structural" in avail
        assert "git_history" in avail
        assert "semantics" in avail

    def test_slot_value_access_pattern(self):
        """Demonstrate safe access pattern."""
        store = AnalysisStore()

        # WRONG pattern - would crash
        # graph = store.structural.value  # LookupError

        # RIGHT pattern - check first
        if store.structural.available:
            graph = store.structural.value
        else:
            graph = None

        assert graph is None

        # After setting
        store.structural.set({"test": "data"}, "producer")
        if store.structural.available:
            graph = store.structural.value
            assert graph == {"test": "data"}


class TestSlotErrorMessages:
    """Test that error messages are informative."""

    def test_unpopulated_slot_message(self):
        """Unpopulated slot gives basic message."""
        slot: Slot[str] = Slot()
        try:
            _ = slot.value
        except LookupError as e:
            assert "Slot not populated" in str(e)

    def test_slot_with_error_message(self):
        """Slot with error gives detailed message."""
        slot: Slot[str] = Slot()
        slot.set_error("Git binary not found in PATH", "temporal/git_extractor")
        try:
            _ = slot.value
        except LookupError as e:
            msg = str(e)
            assert "not populated" in msg.lower() or "Git binary" in msg
