"""Tests for Phase 6 finders.

Tests all 14 new finders added in Phase 6:
- Batch 1: Structural (6 finders)
- Batch 2: Architecture (2 finders)
- Batch 3: Cross-dimensional (6 finders)
"""

import pytest

from shannon_insight.insights.models import compute_confidence
from shannon_insight.insights.store import AnalysisStore, Slot
from shannon_insight.signals.models import (
    FileSignals,
    GlobalSignals,
    ModuleSignals,
    SignalField,
)

# ============================================================================
# Test: compute_confidence helper
# ============================================================================


class TestComputeConfidence:
    """Test the margin-based confidence formula."""

    def test_high_is_bad_at_threshold(self):
        """Margin should be 0 at threshold."""
        conf = compute_confidence([("pagerank", 0.90, 0.90, "high_is_bad")])
        assert conf == 0.0

    def test_high_is_bad_above_threshold(self):
        """Margin should be > 0 above threshold."""
        conf = compute_confidence([("pagerank", 0.95, 0.90, "high_is_bad")])
        # margin = (0.95 - 0.90) / (1.0 - 0.90) = 0.5
        assert conf == pytest.approx(0.5)

    def test_high_is_good_at_threshold(self):
        """Margin should be 0 at threshold."""
        conf = compute_confidence([("bus_factor", 1.5, 1.5, "high_is_good")])
        assert conf == 0.0

    def test_high_is_good_below_threshold(self):
        """Margin should be > 0 below threshold."""
        conf = compute_confidence([("bus_factor", 0.75, 1.5, "high_is_good")])
        # margin = (1.5 - 0.75) / 1.5 = 0.5
        assert conf == pytest.approx(0.5)

    def test_multiple_conditions(self):
        """Should average margins across conditions."""
        conf = compute_confidence(
            [
                ("pagerank", 0.95, 0.90, "high_is_bad"),  # margin = 0.5
                ("bus_factor", 0.75, 1.5, "high_is_good"),  # margin = 0.5
            ]
        )
        assert conf == pytest.approx(0.5)

    def test_empty_conditions(self):
        """Should return 0 for empty conditions."""
        assert compute_confidence([]) == 0.0


# ============================================================================
# Test fixtures
# ============================================================================


@pytest.fixture
def basic_store() -> AnalysisStore:
    """Create a basic store with signal_field."""
    field = SignalField(tier="FULL")
    store = AnalysisStore(root_dir="/tmp")
    store.signal_field = Slot()
    store.signal_field.set(field, "test")
    return store


@pytest.fixture
def file_signal_factory():
    """Factory for creating FileSignals with defaults."""

    def _create(path: str, **kwargs) -> FileSignals:
        defaults = {
            "path": path,
            "role": "UTILITY",
            "total_changes": 100,  # Above median for hotspot filter
        }
        defaults.update(kwargs)
        return FileSignals(**defaults)

    return _create


# ============================================================================
# Batch 1: Structural Finders
# ============================================================================


class TestOrphanCodeFinder:
    """Test ORPHAN_CODE detection."""

    def test_detects_orphan_file(self, basic_store, file_signal_factory):
        """Should detect files with is_orphan=True."""
        from shannon_insight.insights.finders.orphan_code import OrphanCodeFinder

        field = basic_store.signal_field.value
        field.per_file["orphan.py"] = file_signal_factory(
            "orphan.py", is_orphan=True, in_degree=0, depth=-1
        )

        finder = OrphanCodeFinder()
        findings = finder.find(basic_store)

        assert len(findings) == 1
        assert findings[0].finding_type == "orphan_code"
        assert findings[0].files == ["orphan.py"]
        assert findings[0].severity == 0.55
        assert findings[0].scope == "FILE"

    def test_skips_non_orphan(self, basic_store, file_signal_factory):
        """Should not detect non-orphan files."""
        from shannon_insight.insights.finders.orphan_code import OrphanCodeFinder

        field = basic_store.signal_field.value
        field.per_file["connected.py"] = file_signal_factory(
            "connected.py", is_orphan=False, in_degree=5
        )

        finder = OrphanCodeFinder()
        findings = finder.find(basic_store)

        assert len(findings) == 0


class TestHollowCodeFinder:
    """Test HOLLOW_CODE detection."""

    def test_detects_hollow_file(self, basic_store, file_signal_factory):
        """Should detect files with high stub_ratio and impl_gini."""
        from shannon_insight.insights.finders.hollow_code import HollowCodeFinder

        field = basic_store.signal_field.value
        field.per_file["hollow.py"] = file_signal_factory(
            "hollow.py",
            stub_ratio=0.7,  # > 0.5 threshold
            impl_gini=0.8,  # > 0.6 threshold
            function_count=10,
        )

        finder = HollowCodeFinder()
        findings = finder.find(basic_store)

        assert len(findings) == 1
        assert findings[0].finding_type == "hollow_code"
        assert findings[0].severity == 0.71

    def test_skips_implemented_file(self, basic_store, file_signal_factory):
        """Should not detect well-implemented files."""
        from shannon_insight.insights.finders.hollow_code import HollowCodeFinder

        field = basic_store.signal_field.value
        field.per_file["solid.py"] = file_signal_factory(
            "solid.py",
            stub_ratio=0.1,  # Below threshold
            impl_gini=0.3,  # Below threshold
            function_count=10,
        )

        finder = HollowCodeFinder()
        findings = finder.find(basic_store)

        assert len(findings) == 0


class TestPhantomImportsFinder:
    """Test PHANTOM_IMPORTS detection."""

    def test_detects_phantom_imports(self, basic_store, file_signal_factory):
        """Should detect files with unresolved imports."""
        from shannon_insight.insights.finders.phantom_imports import PhantomImportsFinder

        field = basic_store.signal_field.value
        field.per_file["bad.py"] = file_signal_factory(
            "bad.py",
            phantom_import_count=3,
            import_count=10,
        )

        finder = PhantomImportsFinder()
        findings = finder.find(basic_store)

        assert len(findings) == 1
        assert findings[0].finding_type == "phantom_imports"
        assert findings[0].severity >= 0.65

    def test_skips_clean_imports(self, basic_store, file_signal_factory):
        """Should not detect files with all imports resolved."""
        from shannon_insight.insights.finders.phantom_imports import PhantomImportsFinder

        field = basic_store.signal_field.value
        field.per_file["clean.py"] = file_signal_factory(
            "clean.py",
            phantom_import_count=0,
            import_count=10,
        )

        finder = PhantomImportsFinder()
        findings = finder.find(basic_store)

        assert len(findings) == 0


class TestFlatArchitectureFinder:
    """Test FLAT_ARCHITECTURE detection."""

    def test_detects_flat_architecture(self, basic_store, file_signal_factory):
        """Should detect codebase with no layering."""
        from shannon_insight.insights.finders.flat_architecture import (
            FlatArchitectureFinder,
        )

        field = basic_store.signal_field.value
        # All files at depth 0 or 1
        field.per_file["a.py"] = file_signal_factory("a.py", depth=0)
        field.per_file["b.py"] = file_signal_factory("b.py", depth=1)
        field.per_file["c.py"] = file_signal_factory("c.py", depth=1)
        field.global_signals = GlobalSignals(glue_deficit=0.7)  # > 0.5

        finder = FlatArchitectureFinder()
        findings = finder.find(basic_store)

        assert len(findings) == 1
        assert findings[0].finding_type == "flat_architecture"
        assert findings[0].scope == "CODEBASE"

    def test_skips_layered_architecture(self, basic_store, file_signal_factory):
        """Should not detect codebase with good layering."""
        from shannon_insight.insights.finders.flat_architecture import (
            FlatArchitectureFinder,
        )

        field = basic_store.signal_field.value
        # Files at various depths
        field.per_file["a.py"] = file_signal_factory("a.py", depth=0)
        field.per_file["b.py"] = file_signal_factory("b.py", depth=2)
        field.per_file["c.py"] = file_signal_factory("c.py", depth=3)
        field.global_signals = GlobalSignals(glue_deficit=0.3)

        finder = FlatArchitectureFinder()
        findings = finder.find(basic_store)

        assert len(findings) == 0


class TestNamingDriftFinder:
    """Test NAMING_DRIFT detection."""

    def test_detects_naming_drift(self, basic_store, file_signal_factory):
        """Should detect files with mismatched names."""
        from shannon_insight.insights.finders.naming_drift import NamingDriftFinder

        field = basic_store.signal_field.value
        field.per_file["utils.py"] = file_signal_factory(
            "utils.py",
            naming_drift=0.85,  # > 0.7 threshold
            concept_count=5,
        )

        finder = NamingDriftFinder()
        findings = finder.find(basic_store)

        assert len(findings) == 1
        assert findings[0].finding_type == "naming_drift"
        assert findings[0].severity == 0.45

    def test_skips_well_named(self, basic_store, file_signal_factory):
        """Should not detect well-named files."""
        from shannon_insight.insights.finders.naming_drift import NamingDriftFinder

        field = basic_store.signal_field.value
        field.per_file["auth.py"] = file_signal_factory(
            "auth.py",
            naming_drift=0.3,  # Below threshold
        )

        finder = NamingDriftFinder()
        findings = finder.find(basic_store)

        assert len(findings) == 0


# ============================================================================
# Batch 2: Architecture Finders
# ============================================================================


class TestZoneOfPainFinder:
    """Test ZONE_OF_PAIN detection."""

    def test_detects_zone_of_pain(self, basic_store):
        """Should detect modules with low A and low I."""
        from shannon_insight.insights.finders.zone_of_pain import ZoneOfPainFinder

        field = basic_store.signal_field.value
        field.per_module["core/"] = ModuleSignals(
            path="core/",
            abstractness=0.1,  # < 0.3 (concrete)
            instability=0.1,  # < 0.3 (stable) - hard to change
        )

        # Need architecture slot for finder to run
        basic_store.architecture = Slot()
        basic_store.architecture.set(object(), "test")

        finder = ZoneOfPainFinder()
        findings = finder.find(basic_store)

        assert len(findings) == 1
        assert findings[0].finding_type == "zone_of_pain"
        assert findings[0].scope == "MODULE"

    def test_skips_isolated_module(self, basic_store):
        """Should skip modules with instability=None."""
        from shannon_insight.insights.finders.zone_of_pain import ZoneOfPainFinder

        field = basic_store.signal_field.value
        field.per_module["isolated/"] = ModuleSignals(
            path="isolated/",
            abstractness=0.1,
            instability=None,  # Isolated module
        )

        basic_store.architecture = Slot()
        basic_store.architecture.set(object(), "test")

        finder = ZoneOfPainFinder()
        findings = finder.find(basic_store)

        assert len(findings) == 0  # Skipped due to None guard


# ============================================================================
# Batch 3: Cross-Dimensional Finders
# ============================================================================


class TestKnowledgeSiloFinder:
    """Test KNOWLEDGE_SILO detection."""

    def test_detects_knowledge_silo(self, basic_store, file_signal_factory):
        """Should detect high-centrality single-owner files."""
        from shannon_insight.insights.finders.knowledge_silo import KnowledgeSiloFinder

        field = basic_store.signal_field.value
        field.tier = "FULL"  # Needs percentiles
        field.global_signals.team_size = 3  # Needs team > 1

        # Add a cold file to establish median (median = 50, so 100 is above)
        cold = file_signal_factory("cold.py", total_changes=10, bus_factor=3.0)
        field.per_file["cold.py"] = cold

        # File with high centrality but low bus factor
        fs = file_signal_factory(
            "critical.py",
            bus_factor=1.2,  # <= 1.5 threshold
            pagerank=0.15,
            total_changes=100,  # Above median
        )
        fs.percentiles = {"pagerank": 0.85}  # > 0.75 threshold
        field.per_file["critical.py"] = fs

        finder = KnowledgeSiloFinder()
        findings = finder.find(basic_store)

        assert len(findings) == 1
        assert findings[0].finding_type == "knowledge_silo"
        assert findings[0].severity == 0.70

    def test_skips_solo_project(self, basic_store, file_signal_factory):
        """Should skip for solo projects (team_size=1)."""
        from shannon_insight.insights.finders.knowledge_silo import KnowledgeSiloFinder

        field = basic_store.signal_field.value
        field.tier = "FULL"
        field.global_signals.team_size = 1  # Solo project

        fs = file_signal_factory("critical.py", bus_factor=1.0, total_changes=100)
        fs.percentiles = {"pagerank": 0.90}
        field.per_file["critical.py"] = fs

        finder = KnowledgeSiloFinder()
        findings = finder.find(basic_store)

        assert len(findings) == 0  # Skipped for solo project

    def test_skips_in_absolute_tier(self, basic_store, file_signal_factory):
        """Should skip in ABSOLUTE tier (needs percentiles)."""
        from shannon_insight.insights.finders.knowledge_silo import KnowledgeSiloFinder

        field = basic_store.signal_field.value
        field.tier = "ABSOLUTE"

        fs = file_signal_factory("critical.py", bus_factor=1.0)
        fs.percentiles = {"pagerank": 0.90}
        field.per_file["critical.py"] = fs

        finder = KnowledgeSiloFinder()
        findings = finder.find(basic_store)

        assert len(findings) == 0  # Skipped in ABSOLUTE tier


class TestWeakLinkFinder:
    """Test WEAK_LINK detection."""

    def test_detects_weak_link(self, basic_store, file_signal_factory):
        """Should detect files with high delta_h."""
        from shannon_insight.insights.finders.weak_link import WeakLinkFinder

        field = basic_store.signal_field.value
        field.tier = "FULL"

        # Add a cold file to establish median
        cold = file_signal_factory("cold.py", total_changes=10)
        field.per_file["cold.py"] = cold

        fs = file_signal_factory(
            "weak.py",
            raw_risk=0.8,
            risk_score=0.8,
            total_changes=100,  # Above median
        )
        field.per_file["weak.py"] = fs
        field.delta_h = {"weak.py": 0.55}  # > 0.4 threshold

        finder = WeakLinkFinder()
        findings = finder.find(basic_store)

        assert len(findings) == 1
        assert findings[0].finding_type == "weak_link"
        assert findings[0].severity >= 0.75

    def test_skips_healthy_file(self, basic_store, file_signal_factory):
        """Should not detect files with low delta_h."""
        from shannon_insight.insights.finders.weak_link import WeakLinkFinder

        field = basic_store.signal_field.value
        field.tier = "FULL"

        fs = file_signal_factory("healthy.py", raw_risk=0.2, total_changes=100)
        field.per_file["healthy.py"] = fs
        field.delta_h = {"healthy.py": 0.1}  # Below threshold

        finder = WeakLinkFinder()
        findings = finder.find(basic_store)

        assert len(findings) == 0


class TestBugAttractorFinder:
    """Test BUG_ATTRACTOR detection."""

    def test_detects_bug_attractor(self, basic_store, file_signal_factory):
        """Should detect central files with high fix ratio."""
        from shannon_insight.insights.finders.bug_attractor import BugAttractorFinder

        field = basic_store.signal_field.value
        field.tier = "FULL"

        # Add a cold file to establish median
        cold = file_signal_factory("cold.py", total_changes=10)
        field.per_file["cold.py"] = cold

        fs = file_signal_factory(
            "buggy.py",
            fix_ratio=0.5,  # > 0.4 threshold
            pagerank=0.1,
            total_changes=100,  # Above median
            blast_radius_size=20,
        )
        fs.percentiles = {"pagerank": 0.85, "fix_ratio": 0.90}
        field.per_file["buggy.py"] = fs

        finder = BugAttractorFinder()
        findings = finder.find(basic_store)

        assert len(findings) == 1
        assert findings[0].finding_type == "bug_attractor"
        assert findings[0].severity == 0.70


# ============================================================================
# Integration Tests
# ============================================================================


class TestFinderIntegration:
    """Integration tests for all finders."""

    def test_all_finders_registered(self):
        """All Phase 6 finders should be registered."""
        from shannon_insight.insights.finders import get_default_finders

        finders = get_default_finders()
        finder_names = {f.name for f in finders}

        # Phase 6 finders
        expected_new = {
            "orphan_code",
            "hollow_code",
            "phantom_imports",
            "copy_paste_clone",
            "flat_architecture",
            "naming_drift",
            "layer_violation",
            "zone_of_pain",
            "knowledge_silo",
            "conway_violation",
            "review_blindspot",
            "weak_link",
            "bug_attractor",
            "accidental_coupling",
        }

        # Check all new finders are registered
        missing = expected_new - finder_names
        assert not missing, f"Missing finders: {missing}"

    def test_finder_count(self):
        """Should have 26 finders total (6 old + 14 phase6 + 4 smart temporal + 2 incomplete/dead)."""
        from shannon_insight.insights.finders import get_default_finders

        finders = get_default_finders()
        assert len(finders) == 26

    def test_all_finders_have_name(self):
        """All finders should have a name attribute."""
        from shannon_insight.insights.finders import get_default_finders

        finders = get_default_finders()
        for finder in finders:
            assert hasattr(finder, "name")
            assert finder.name  # Not empty

    def test_all_finders_have_find_method(self):
        """All finders should have a find method."""
        from shannon_insight.insights.finders import get_default_finders

        finders = get_default_finders()
        for finder in finders:
            assert hasattr(finder, "find")
            assert callable(finder.find)

    def test_new_finders_return_empty_on_missing_store(self):
        """New Phase 6 finders should return empty list if store is missing data."""
        # Only test new Phase 6 finders (old ones use v1 store API)
        from shannon_insight.insights.finders.bug_attractor import BugAttractorFinder
        from shannon_insight.insights.finders.flat_architecture import FlatArchitectureFinder
        from shannon_insight.insights.finders.hollow_code import HollowCodeFinder
        from shannon_insight.insights.finders.knowledge_silo import KnowledgeSiloFinder
        from shannon_insight.insights.finders.layer_violation import LayerViolationFinder
        from shannon_insight.insights.finders.naming_drift import NamingDriftFinder
        from shannon_insight.insights.finders.orphan_code import OrphanCodeFinder
        from shannon_insight.insights.finders.phantom_imports import PhantomImportsFinder
        from shannon_insight.insights.finders.weak_link import WeakLinkFinder
        from shannon_insight.insights.finders.zone_of_pain import ZoneOfPainFinder

        new_finders = [
            OrphanCodeFinder(),
            HollowCodeFinder(),
            PhantomImportsFinder(),
            FlatArchitectureFinder(),
            NamingDriftFinder(),
            LayerViolationFinder(),
            ZoneOfPainFinder(),
            KnowledgeSiloFinder(),
            WeakLinkFinder(),
            BugAttractorFinder(),
        ]

        empty_store = AnalysisStore(root_dir="/tmp")

        for finder in new_finders:
            findings = finder.find(empty_store)
            assert isinstance(findings, list)
            assert len(findings) == 0  # All return empty due to missing signal_field
