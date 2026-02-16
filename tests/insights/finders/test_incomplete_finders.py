"""Tests for incomplete/duplicate finders."""

import pytest

from shannon_insight.insights.finders import (
    DuplicateIncompleteFinder,
    IncompleteImplementationFinder,
)
from shannon_insight.insights.store import AnalysisStore, Slot
from shannon_insight.signals.models import FileSignals, SignalField


@pytest.fixture
def store_with_signals():
    """Create a store with file signals and clone pairs."""
    from shannon_insight.graph.models import ClonePair

    field = SignalField(tier="ABSOLUTE")
    store = AnalysisStore(root_dir="/tmp")
    store.signal_field = Slot()
    store.signal_field.set(field, "test")

    # Add test files
    field.per_file["incomplete.py"] = FileSignals(
        path="incomplete.py",
        stub_ratio=0.6,
        phantom_import_count=3,
        broken_call_count=2,
        impl_gini=0.15,
        total_changes=1,
    )

    field.per_file["stub_file.py"] = FileSignals(
        path="stub_file.py",
        stub_ratio=0.8,  # Higher stub ratio
        phantom_import_count=1,  # Also has phantom imports to trigger
        broken_call_count=0,
        impl_gini=0.1,
        function_count=6,  # Needed for impl_gini check
        total_changes=0,
    )

    field.per_file["complete.py"] = FileSignals(
        path="complete.py",
        stub_ratio=0.0,
        phantom_import_count=0,
        broken_call_count=0,
        impl_gini=0.5,
        total_changes=20,
    )

    # Add clone pairs
    clone_pairs = [
        ClonePair(
            file_a="incomplete.py",
            file_b="stub_file.py",
            ncd=0.2,
            size_a=100,
            size_b=95,
        ),
        ClonePair(
            file_a="incomplete.py",
            file_b="complete.py",
            ncd=0.2,
            size_a=100,
            size_b=100,
        ),
    ]

    store.clone_pairs = Slot()
    store.clone_pairs.set(clone_pairs, "test")

    return store


class TestIncompleteImplementationFinder:
    """Tests for IncompleteImplementationFinder."""

    def test_detects_incomplete_implementation(self, store_with_signals):
        """Should detect files with phantom imports and high stub ratio."""
        finder = IncompleteImplementationFinder()
        findings = finder.find(store_with_signals)

        incomplete_files = [f for f in findings if "incomplete" in f.title.lower()]
        assert len(incomplete_files) >= 1

    def test_detects_stub_file(self, store_with_signals):
        """Should detect stub files."""
        finder = IncompleteImplementationFinder()
        findings = finder.find(store_with_signals)

        stub_files = [f for f in findings if "stub_file" in f.title.lower()]
        assert len(stub_files) >= 1

    def test_skips_complete_file(self, store_with_signals):
        """Should skip complete files."""
        finder = IncompleteImplementationFinder()
        findings = finder.find(store_with_signals)

        # Check that complete.py is not in findings
        complete_file_findings = [f for f in findings if "complete.py" in f.files]
        assert len(complete_file_findings) == 0

    def test_evidence_includes_phantom_imports(self, store_with_signals):
        """Should include phantom import count in evidence."""
        finder = IncompleteImplementationFinder()
        findings = finder.find(store_with_signals)

        incomplete = next((f for f in findings if "incomplete.py" in f.files[0]), None)
        assert incomplete is not None

        phantom_evidence = next(
            (e for e in incomplete.evidence if "phantom" in e.signal.lower()), None
        )
        assert phantom_evidence is not None
        assert phantom_evidence.value == 3.0


class TestDuplicateIncompleteFinder:
    """Tests for DuplicateIncompleteFinder."""

    def test_detects_duplicate_incomplete(self, store_with_signals):
        """Should detect duplicate incomplete files."""
        finder = DuplicateIncompleteFinder()
        findings = finder.find(store_with_signals)

        assert len(findings) >= 1

    def test_skips_complete_clone(self, store_with_signals):
        """Should skip clone pairs where one file is complete."""
        finder = DuplicateIncompleteFinder()
        findings = finder.find(store_with_signals)

        # Should only find the incomplete/incomplete clone
        incomplete_pairs = [
            f for f in findings if "incomplete.py" in f.files and "stub_file.py" in f.files
        ]
        assert len(incomplete_pairs) >= 1

        # Should not find incomplete/complete clone
        complete_pairs = [
            f for f in findings if "incomplete.py" in f.files and "complete.py" in f.files
        ]
        assert len(complete_pairs) == 0

    def test_evidence_includes_stub_ratio(self, store_with_signals):
        """Should include stub ratio in evidence."""
        finder = DuplicateIncompleteFinder()
        findings = finder.find(store_with_signals)

        assert len(findings) >= 1

        stub_evidence = [e for e in findings[0].evidence if "stub_ratio" in e.signal]
        assert len(stub_evidence) >= 2  # Should show both files
