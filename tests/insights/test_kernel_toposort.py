"""Tests for graphlib-based topological sorting of analyzers."""

import pytest

from shannon_insight.insights.kernel_toposort import (
    AnalyzerCycleError,
    SlotCollisionError,
    resolve_analyzer_order,
)


class MockAnalyzer:
    """Mock analyzer for testing."""

    def __init__(
        self,
        name: str,
        requires: set[str] | None = None,
        provides: set[str] | None = None,
        run_last: bool = False,
    ):
        self.name = name
        self.requires = requires or set()
        self.provides = provides or set()
        self.run_last = run_last
        self.api_version = "2.0"
        self.error_mode = "fail"
        self.deprecated = False
        self.deprecation_note = None

    def analyze(self, store):
        pass


class TestResolveAnalyzerOrder:
    """Test topological sorting of analyzers."""

    def test_empty_list(self):
        """Empty list returns empty."""
        result = resolve_analyzer_order([])
        assert result == []

    def test_single_analyzer(self):
        """Single analyzer returns itself."""
        a = MockAnalyzer("a")
        result = resolve_analyzer_order([a])
        assert result == [a]

    def test_independent_analyzers(self):
        """Independent analyzers can be in any order."""
        a = MockAnalyzer("a", provides={"slot_a"})
        b = MockAnalyzer("b", provides={"slot_b"})
        result = resolve_analyzer_order([a, b])
        # Both should be present
        assert set(result) == {a, b}

    def test_dependent_analyzers(self):
        """Dependent analyzer comes after dependency."""
        a = MockAnalyzer("a", provides={"structural"})
        b = MockAnalyzer("b", requires={"structural"}, provides={"temporal"})
        result = resolve_analyzer_order([b, a])  # Pass in wrong order
        # a must come before b
        assert result.index(a) < result.index(b)

    def test_chain_dependency(self):
        """Chain of dependencies: a -> b -> c."""
        a = MockAnalyzer("a", provides={"slot_a"})
        b = MockAnalyzer("b", requires={"slot_a"}, provides={"slot_b"})
        c = MockAnalyzer("c", requires={"slot_b"}, provides={"slot_c"})
        result = resolve_analyzer_order([c, a, b])  # Pass scrambled
        assert result.index(a) < result.index(b)
        assert result.index(b) < result.index(c)

    def test_diamond_dependency(self):
        """Diamond: a -> b, a -> c, b -> d, c -> d."""
        a = MockAnalyzer("a", provides={"slot_a"})
        b = MockAnalyzer("b", requires={"slot_a"}, provides={"slot_b"})
        c = MockAnalyzer("c", requires={"slot_a"}, provides={"slot_c"})
        d = MockAnalyzer("d", requires={"slot_b", "slot_c"}, provides={"slot_d"})
        result = resolve_analyzer_order([d, b, c, a])
        # a must be first, d must be last
        assert result[0] == a
        assert result[-1] == d
        # b and c can be in either order but both before d
        assert result.index(b) < result.index(d)
        assert result.index(c) < result.index(d)


class TestSlotCollision:
    """Test detection of slot collisions (duplicate providers)."""

    def test_same_slot_different_providers(self):
        """Two analyzers providing same slot raises error."""
        a = MockAnalyzer("a", provides={"structural"})
        b = MockAnalyzer("b", provides={"structural"})
        with pytest.raises(SlotCollisionError, match="structural.*provided by both"):
            resolve_analyzer_order([a, b])

    def test_same_analyzer_multiple_slots_ok(self):
        """One analyzer can provide multiple slots."""
        a = MockAnalyzer("a", provides={"slot_a", "slot_b", "slot_c"})
        result = resolve_analyzer_order([a])
        assert result == [a]


class TestCycleDetection:
    """Test detection of dependency cycles."""

    def test_direct_cycle(self):
        """A requires B, B requires A."""
        a = MockAnalyzer("a", requires={"slot_b"}, provides={"slot_a"})
        b = MockAnalyzer("b", requires={"slot_a"}, provides={"slot_b"})
        with pytest.raises(AnalyzerCycleError, match="cycle"):
            resolve_analyzer_order([a, b])

    def test_indirect_cycle(self):
        """A -> B -> C -> A."""
        a = MockAnalyzer("a", requires={"slot_c"}, provides={"slot_a"})
        b = MockAnalyzer("b", requires={"slot_a"}, provides={"slot_b"})
        c = MockAnalyzer("c", requires={"slot_b"}, provides={"slot_c"})
        with pytest.raises(AnalyzerCycleError, match="cycle"):
            resolve_analyzer_order([a, b, c])


class TestRunLastAnalyzers:
    """Test Wave 2 (run_last) analyzers."""

    def test_run_last_at_end(self):
        """run_last=True analyzers come after all others."""
        a = MockAnalyzer("a", provides={"slot_a"})
        fusion = MockAnalyzer("fusion", requires={"slot_a"}, run_last=True)
        result = resolve_analyzer_order([fusion, a])
        assert result[-1] == fusion

    def test_multiple_run_last(self):
        """Multiple run_last analyzers all come at end."""
        a = MockAnalyzer("a", provides={"slot_a"})
        b = MockAnalyzer("b", provides={"slot_b"})
        fusion1 = MockAnalyzer("fusion1", run_last=True)
        fusion2 = MockAnalyzer("fusion2", run_last=True)
        result = resolve_analyzer_order([fusion1, a, fusion2, b])
        # a and b should be before fusion1 and fusion2
        assert result.index(a) < result.index(fusion1)
        assert result.index(b) < result.index(fusion2)
        # Both fusion analyzers should be in the last positions
        assert fusion1 in result[-2:]
        assert fusion2 in result[-2:]

    def test_run_last_respects_dependencies(self):
        """run_last analyzers still respect their dependencies."""
        a = MockAnalyzer("a", provides={"slot_a"})
        b = MockAnalyzer("b", requires={"slot_a"}, provides={"slot_b"})
        fusion = MockAnalyzer("fusion", requires={"slot_b"}, run_last=True)
        result = resolve_analyzer_order([fusion, b, a])
        assert result == [a, b, fusion]


class TestUnresolvedRequirements:
    """Test handling of requirements that no one provides."""

    def test_unknown_requirement_allowed(self):
        """Analyzers can require slots that aren't provided.

        The kernel will skip them at runtime if requirements aren't met.
        This allows optional dependencies (e.g., temporal analyzer needs git).
        """
        a = MockAnalyzer("a", requires={"external_slot"})
        result = resolve_analyzer_order([a])
        assert result == [a]

    def test_partial_chain_allowed(self):
        """Can have partial chains with unmet requirements."""
        a = MockAnalyzer("a", requires={"missing"}, provides={"slot_a"})
        b = MockAnalyzer("b", requires={"slot_a"}, provides={"slot_b"})
        result = resolve_analyzer_order([b, a])
        # Order should still be a -> b based on slot_a dependency
        assert result.index(a) < result.index(b)
