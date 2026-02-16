"""Phase 5 tests: Signal Fusion implementation.

Tests for:
1. Tier detection (ABSOLUTE/BAYESIAN/FULL)
2. Percentile formula (uses <=)
3. Risk score computation
4. Health score with instability=None guard
5. Laplacian Δh > 0 for bad file in good neighborhood
6. ABSOLUTE tier skips composites
7. Backward compat: Primitives.from_file_signals()
"""

from shannon_insight.insights.store_v2 import AnalysisStore
from shannon_insight.signals.composites import compute_composites
from shannon_insight.signals.display import to_display_scale
from shannon_insight.signals.fusion import FusionPipeline, _gini, build
from shannon_insight.signals.health_laplacian import (
    compute_health_laplacian,
    compute_raw_risk,
)
from shannon_insight.signals.models import (
    FileSignals,
    ModuleSignals,
    Primitives,
    SignalField,
)
from shannon_insight.signals.normalization import (
    _standard_percentile,
    effective_percentile,
    normalize,
)


class MockFileMetrics:
    """Mock FileMetrics for testing."""

    def __init__(
        self,
        path: str,
        lines: int = 100,
        functions: int = 5,
        structs: int = 1,
        nesting_depth: int = 2,
        imports: list = None,
        function_sizes: list = None,
    ):
        self.path = path
        self.lines = lines
        self.functions = functions
        self.structs = structs
        self.nesting_depth = nesting_depth
        self.imports = imports or []
        self.function_sizes = function_sizes or [10, 20, 30]


class MockFileAnalysis:
    """Mock FileAnalysis for testing."""

    def __init__(
        self,
        path: str,
        pagerank: float = 0.1,
        betweenness: float = 0.05,
        in_degree: int = 2,
        out_degree: int = 3,
        blast_radius_size: int = 10,
        depth: int = 1,
        is_orphan: bool = False,
        phantom_import_count: int = 0,
        community_id: int = 0,
        compression_ratio: float = 0.5,
        cognitive_load: float = 15.0,
    ):
        self.path = path
        self.pagerank = pagerank
        self.betweenness = betweenness
        self.in_degree = in_degree
        self.out_degree = out_degree
        self.blast_radius_size = blast_radius_size
        self.depth = depth
        self.is_orphan = is_orphan
        self.phantom_import_count = phantom_import_count
        self.community_id = community_id
        self.compression_ratio = compression_ratio
        self.cognitive_load = cognitive_load


class MockGraph:
    """Mock DependencyGraph for testing."""

    def __init__(self, adjacency: dict = None, reverse: dict = None):
        self.adjacency = adjacency or {}
        self.reverse = reverse or {}
        self.all_nodes = set(self.adjacency.keys()) | set(self.reverse.keys())


class MockStructural:
    """Mock CodebaseAnalysis for testing."""

    def __init__(self, files: dict = None, graph: MockGraph = None):
        self.files = files or {}
        self.graph = graph or MockGraph()
        self.modularity = 0.5
        self.cycle_count = 0
        self.graph_analysis = MockGraphAnalysis()


class MockGraphAnalysis:
    """Mock GraphAnalysis for testing."""

    def __init__(self):
        self.centrality_gini = 0.3
        self.spectral_gap = 0.1
        self.node_community = {}
        self.communities = []


class TestTierDetection:
    """Test tier detection based on file count."""

    def test_absolute_tier_under_15_files(self):
        """< 15 files -> ABSOLUTE tier."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics(f"/f{i}.py") for i in range(10)]
        pipeline = FusionPipeline(store)
        assert pipeline.field.tier == "ABSOLUTE"

    def test_bayesian_tier_15_to_49_files(self):
        """15-49 files -> BAYESIAN tier."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics(f"/f{i}.py") for i in range(30)]
        pipeline = FusionPipeline(store)
        assert pipeline.field.tier == "BAYESIAN"

    def test_full_tier_50_plus_files(self):
        """50+ files -> FULL tier."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics(f"/f{i}.py") for i in range(60)]
        pipeline = FusionPipeline(store)
        assert pipeline.field.tier == "FULL"

    def test_boundary_14_is_absolute(self):
        """14 files is still ABSOLUTE."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics(f"/f{i}.py") for i in range(14)]
        pipeline = FusionPipeline(store)
        assert pipeline.field.tier == "ABSOLUTE"

    def test_boundary_15_is_bayesian(self):
        """15 files is BAYESIAN."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics(f"/f{i}.py") for i in range(15)]
        pipeline = FusionPipeline(store)
        assert pipeline.field.tier == "BAYESIAN"

    def test_boundary_49_is_bayesian(self):
        """49 files is still BAYESIAN."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics(f"/f{i}.py") for i in range(49)]
        pipeline = FusionPipeline(store)
        assert pipeline.field.tier == "BAYESIAN"

    def test_boundary_50_is_full(self):
        """50 files is FULL."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics(f"/f{i}.py") for i in range(50)]
        pipeline = FusionPipeline(store)
        assert pipeline.field.tier == "FULL"


class TestPercentileFormula:
    """Test percentile computation (FM-4 prevention)."""

    def test_percentile_uses_less_than_or_equal(self):
        """Percentile formula uses <= not <."""
        # Values: [1, 2, 3, 4, 5]
        # For value 3: count of values <= 3 is 3
        # pctl = (3/5) * 100 = 60.0
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        pctl = _standard_percentile(3.0, values)
        assert pctl == 60.0

    def test_percentile_minimum_value(self):
        """Minimum value has non-zero percentile."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        pctl = _standard_percentile(1.0, values)
        assert pctl == 20.0  # (1/5) * 100

    def test_percentile_maximum_value(self):
        """Maximum value has 100.0 percentile."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        pctl = _standard_percentile(5.0, values)
        assert pctl == 100.0

    def test_percentile_empty_list(self):
        """Empty list returns 0.0."""
        pctl = _standard_percentile(5.0, [])
        assert pctl == 0.0

    def test_percentile_all_same_values(self):
        """All same values gives 100.0 percentile."""
        values = [3.0, 3.0, 3.0, 3.0]
        pctl = _standard_percentile(3.0, values)
        assert pctl == 100.0


class TestEffectivePercentile:
    """Test percentile floor for small absolute values."""

    def test_pagerank_below_floor_returns_zero(self):
        """Pagerank below 0.001 returns 0.0 percentile."""
        pctl = effective_percentile("pagerank", 0.0005, 0.9)
        assert pctl == 0.0

    def test_pagerank_above_floor_unchanged(self):
        """Pagerank above 0.001 keeps original percentile."""
        pctl = effective_percentile("pagerank", 0.01, 0.9)
        assert pctl == 0.9

    def test_blast_radius_below_floor(self):
        """Blast radius below 2 returns 0.0."""
        pctl = effective_percentile("blast_radius_size", 1, 0.8)
        assert pctl == 0.0

    def test_cognitive_load_below_floor(self):
        """Cognitive load below 3 returns 0.0."""
        pctl = effective_percentile("cognitive_load", 2.0, 0.7)
        assert pctl == 0.0

    def test_unknown_signal_unchanged(self):
        """Unknown signal name passes through unchanged."""
        pctl = effective_percentile("custom_signal", 1.0, 0.5)
        assert pctl == 0.5


class TestRiskScoreComputation:
    """Test risk_score composite computation."""

    def test_risk_score_low_for_safe_file(self):
        """Safe file (low metrics) has low risk score."""
        field = SignalField(tier="FULL")
        fs = FileSignals(
            path="/safe.py",
            churn_trajectory="DORMANT",
            bus_factor=3.0,
        )
        fs.percentiles = {
            "pagerank": 0.1,
            "blast_radius_size": 0.1,
            "cognitive_load": 0.1,
        }
        field.per_file["/safe.py"] = fs

        compute_composites(field)

        # Low percentiles + stable + high bus factor = low risk
        assert fs.risk_score < 0.4

    def test_risk_score_high_for_risky_file(self):
        """Risky file (high metrics, churning, active) has high risk score."""
        field = SignalField(tier="FULL")
        fs = FileSignals(
            path="/risky.py",
            churn_trajectory="CHURNING",
            bus_factor=1.0,
            total_changes=50,  # Must have change activity for non-zero risk
        )
        fs.percentiles = {
            "pagerank": 0.95,
            "blast_radius_size": 0.95,
            "cognitive_load": 0.95,
        }
        field.per_file["/risky.py"] = fs

        compute_composites(field)

        # High percentiles + churning + single author + active = high risk
        assert fs.risk_score > 0.7

    def test_risk_score_zero_for_inactive_file(self):
        """Inactive file (no changes) always has zero risk score."""
        field = SignalField(tier="FULL")
        fs = FileSignals(
            path="/inactive.py",
            churn_trajectory="DORMANT",
            bus_factor=1.0,
            total_changes=0,  # No changes = no risk
        )
        fs.percentiles = {
            "pagerank": 0.95,
            "blast_radius_size": 0.95,
            "cognitive_load": 0.95,
        }
        field.per_file["/inactive.py"] = fs

        compute_composites(field)

        # No changes = zero risk, regardless of how central/complex
        assert fs.risk_score == 0.0

    def test_instability_factor_churning(self):
        """CHURNING trajectory gives churn_factor of 1.0."""
        field = SignalField(tier="FULL")
        fs = FileSignals(
            path="/a.py",
            churn_trajectory="CHURNING",
            bus_factor=1.0,
            total_changes=50,  # Active file
        )
        fs.percentiles = {"pagerank": 0.5, "blast_radius_size": 0.5, "cognitive_load": 0.5}
        field.per_file["/a.py"] = fs

        compute_composites(field)

        # With churn_factor=1.0 (CHURNING), risk uses full multiplier
        assert fs.risk_score > 0.0

    def test_instability_factor_dormant(self):
        """DORMANT trajectory gives churn_factor of 0.3."""
        field = SignalField(tier="FULL")
        fs = FileSignals(
            path="/a.py",
            churn_trajectory="DORMANT",
            bus_factor=1.0,
            total_changes=50,  # Active file
        )
        fs.percentiles = {"pagerank": 0.5, "blast_radius_size": 0.5, "cognitive_load": 0.5}
        field.per_file["/a.py"] = fs

        compute_composites(field)

        # With churn_factor=0.3 (DORMANT), risk uses reduced multiplier
        # Multiplicative: 0.5 * 0.5 * 0.3 * (1 + 0.67) = 0.125
        assert fs.risk_score < 0.3


class TestHealthScoreInstabilityGuard:
    """Test health_score with instability=None guard (FM-2)."""

    def test_health_score_with_valid_instability(self):
        """Health score computed normally when instability is not None."""
        field = SignalField(tier="FULL")
        ms = ModuleSignals(
            path="/module",
            cohesion=0.8,
            coupling=0.2,
            instability=0.5,
            main_seq_distance=0.1,
            boundary_alignment=0.9,
            role_consistency=0.85,
        )
        field.per_module["/module"] = ms

        compute_composites(field)

        # Health score should be computed with all 6 terms
        assert 0.0 <= ms.health_score <= 1.0
        assert ms.health_score > 0.5  # Good metrics = good health

    def test_health_score_with_none_instability(self):
        """Health score computed with redistributed weights when instability=None."""
        field = SignalField(tier="FULL")
        ms = ModuleSignals(
            path="/module",
            cohesion=0.8,
            coupling=0.2,
            instability=None,  # Isolated module
            main_seq_distance=0.0,  # Not used
            boundary_alignment=0.9,
            role_consistency=0.85,
        )
        field.per_module["/module"] = ms

        compute_composites(field)

        # Should NOT crash (FM-2 prevention)
        # Health score computed with 5 terms (scale by 1.25)
        assert 0.0 <= ms.health_score <= 1.0
        assert ms.health_score > 0.5  # Still good health

    def test_health_score_no_crash_on_none(self):
        """Ensure no TypeError when instability is None."""
        field = SignalField(tier="FULL")
        ms = ModuleSignals(path="/mod", instability=None)
        field.per_module["/mod"] = ms

        # This should not raise TypeError
        compute_composites(field)

        assert isinstance(ms.health_score, float)


class TestHealthLaplacian:
    """Test health Laplacian computation."""

    def test_laplacian_positive_for_bad_in_good_neighborhood(self):
        """Δh > 0 for file with high risk surrounded by healthy files."""
        field = SignalField(tier="FULL")

        # Bad file
        bad = FileSignals(path="/bad.py", raw_risk=0.8)
        field.per_file["/bad.py"] = bad

        # Good neighbors
        for i in range(3):
            good = FileSignals(path=f"/good{i}.py", raw_risk=0.2)
            field.per_file[f"/good{i}.py"] = good

        # Graph: bad imports all goods
        graph = MockGraph(
            adjacency={"/bad.py": ["/good0.py", "/good1.py", "/good2.py"]},
            reverse={
                "/good0.py": ["/bad.py"],
                "/good1.py": ["/bad.py"],
                "/good2.py": ["/bad.py"],
            },
        )

        delta_h = compute_health_laplacian(field, graph)

        # Bad file: 0.8 - mean(0.2, 0.2, 0.2) = 0.8 - 0.2 = 0.6
        assert delta_h["/bad.py"] > 0.4

    def test_laplacian_negative_for_good_in_bad_neighborhood(self):
        """Δh < 0 for healthy file surrounded by risky files."""
        field = SignalField(tier="FULL")

        # Good file
        good = FileSignals(path="/good.py", raw_risk=0.2)
        field.per_file["/good.py"] = good

        # Bad neighbors
        for i in range(3):
            bad = FileSignals(path=f"/bad{i}.py", raw_risk=0.8)
            field.per_file[f"/bad{i}.py"] = bad

        graph = MockGraph(
            adjacency={"/good.py": ["/bad0.py", "/bad1.py", "/bad2.py"]},
            reverse={
                "/bad0.py": ["/good.py"],
                "/bad1.py": ["/good.py"],
                "/bad2.py": ["/good.py"],
            },
        )

        delta_h = compute_health_laplacian(field, graph)

        # Good file: 0.2 - mean(0.8, 0.8, 0.8) = 0.2 - 0.8 = -0.6
        assert delta_h["/good.py"] < -0.4

    def test_laplacian_zero_for_orphan(self):
        """Δh = 0.0 for orphan file (no neighbors)."""
        field = SignalField(tier="FULL")
        orphan = FileSignals(path="/orphan.py", raw_risk=0.5)
        field.per_file["/orphan.py"] = orphan

        graph = MockGraph()  # Empty graph

        delta_h = compute_health_laplacian(field, graph)

        assert delta_h["/orphan.py"] == 0.0


class TestAbsoluteTierSkipsComposites:
    """Test that ABSOLUTE tier skips composite computation."""

    def test_absolute_tier_no_percentiles(self):
        """ABSOLUTE tier does not compute percentiles."""
        field = SignalField(tier="ABSOLUTE")
        fs = FileSignals(path="/a.py", pagerank=0.1, cognitive_load=20.0)
        field.per_file["/a.py"] = fs

        normalize(field)

        # Percentiles dict should be empty
        assert fs.percentiles == {}

    def test_absolute_tier_no_composites(self):
        """ABSOLUTE tier does not compute composites."""
        field = SignalField(tier="ABSOLUTE")
        fs = FileSignals(path="/a.py")
        fs.percentiles = {}  # No percentiles
        field.per_file["/a.py"] = fs

        # Default values
        original_risk = fs.risk_score
        original_wiring = fs.wiring_quality

        compute_composites(field)

        # Values should be unchanged (composites not computed)
        assert fs.risk_score == original_risk
        assert fs.wiring_quality == original_wiring


class TestBackwardCompatibility:
    """Test backward compatibility with Primitives class."""

    def test_primitives_from_file_signals(self):
        """Primitives.from_file_signals() produces correct mapping."""
        fs = FileSignals(
            path="/test.py",
            compression_ratio=0.65,
            pagerank=0.12,
            churn_cv=0.45,
            semantic_coherence=0.78,
            cognitive_load=25.5,
        )

        prims = Primitives.from_file_signals(fs)

        assert prims.structural_entropy == 0.65
        assert prims.network_centrality == 0.12
        assert prims.churn_volatility == 0.45
        assert prims.semantic_coherence == 0.78
        assert prims.cognitive_load == 25.5

    def test_primitives_to_dict_roundtrip(self):
        """Primitives can roundtrip through dict."""
        original = Primitives(
            structural_entropy=0.5,
            network_centrality=0.3,
            churn_volatility=0.2,
            semantic_coherence=0.8,
            cognitive_load=15.0,
        )

        d = original.to_dict()
        restored = Primitives.from_dict(d)

        assert restored == original


class TestDisplayScale:
    """Test display scale conversion."""

    def test_display_scale_basic(self):
        """Basic conversion: 0.64 -> 6.4."""
        assert to_display_scale(0.64) == 6.4

    def test_display_scale_floor(self):
        """Values below 0.1 floor at 1.0."""
        assert to_display_scale(0.05) == 1.0
        assert to_display_scale(0.0) == 1.0

    def test_display_scale_max(self):
        """Value 1.0 -> 10.0."""
        assert to_display_scale(1.0) == 10.0

    def test_display_scale_clamp_high(self):
        """Values > 1.0 clamped to 10.0."""
        assert to_display_scale(1.5) == 10.0

    def test_display_scale_clamp_low(self):
        """Values < 0.0 clamped to 1.0."""
        assert to_display_scale(-0.5) == 1.0

    def test_display_scale_rounding(self):
        """Rounding to 1 decimal place."""
        assert to_display_scale(0.555) == 5.6
        assert to_display_scale(0.554) == 5.5


class TestGiniCoefficient:
    """Test Gini coefficient computation."""

    def test_gini_equal_distribution(self):
        """Equal values give Gini = 0."""
        values = [10.0, 10.0, 10.0, 10.0]
        assert abs(_gini(values)) < 0.001

    def test_gini_unequal_distribution(self):
        """Unequal values give positive Gini."""
        values = [1.0, 1.0, 1.0, 100.0]
        gini = _gini(values)
        assert gini > 0.5

    def test_gini_empty_list(self):
        """Empty list returns 0."""
        assert _gini([]) == 0.0

    def test_gini_single_value(self):
        """Single value returns 0."""
        assert _gini([5.0]) == 0.0

    def test_gini_all_zeros(self):
        """All zeros returns 0."""
        assert _gini([0.0, 0.0, 0.0]) == 0.0


class TestRawRiskComputation:
    """Test raw_risk pre-percentile computation."""

    def test_raw_risk_computation(self):
        """Raw risk computed correctly from max-normalized signals."""
        fs = FileSignals(
            path="/test.py",
            pagerank=0.5,
            blast_radius_size=25,
            cognitive_load=50.0,
            churn_trajectory="CHURNING",
            bus_factor=1.0,
        )

        # Max values
        max_pr = 1.0
        max_blast = 50.0
        max_cog = 100.0
        max_bf = 2.0

        raw = compute_raw_risk(fs, max_pr, max_blast, max_cog, max_bf)

        # 0.25 * 0.5 + 0.20 * 0.5 + 0.20 * 0.5 + 0.20 * 1.0 + 0.15 * 0.5
        # = 0.125 + 0.1 + 0.1 + 0.2 + 0.075 = 0.6
        assert abs(raw - 0.6) < 0.01

    def test_raw_risk_division_by_zero_guard(self):
        """Raw risk handles zero max values."""
        fs = FileSignals(path="/test.py")

        # All max values are 0
        raw = compute_raw_risk(fs, 0.0, 0.0, 0.0, 0.0)

        # Should not crash, returns a value
        assert isinstance(raw, float)
        assert 0.0 <= raw <= 1.0


class TestBuildFunction:
    """Test the build() convenience function."""

    def test_build_returns_signal_field(self):
        """build() returns SignalField with all attributes."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]

        field = build(store, _make_session(store))

        assert isinstance(field, SignalField)
        assert "/a.py" in field.per_file
        assert hasattr(field, "tier")
        assert hasattr(field, "delta_h")
        assert hasattr(field, "global_signals")

    def test_build_collects_scanning_signals(self):
        """build() collects signals from file_metrics."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py", lines=200, functions=10)]

        field = build(store, _make_session(store))

        fs = field.per_file["/a.py"]
        assert fs.lines == 200
        assert fs.function_count == 10

    def test_build_computes_raw_risk(self):
        """build() computes raw_risk for all files."""
        store = AnalysisStore()
        store.file_metrics = [
            MockFileMetrics("/a.py"),
            MockFileMetrics("/b.py"),
        ]

        field = build(store, _make_session(store))

        # raw_risk should be computed (may be 0 if no graph data)
        for fs in field.per_file.values():
            assert hasattr(fs, "raw_risk")
            assert isinstance(fs.raw_risk, float)


class TestWiringQuality:
    """Test wiring_quality composite computation."""

    def test_wiring_quality_perfect_file(self):
        """Well-connected, non-orphan file has high wiring quality."""
        field = SignalField(tier="FULL")
        fs = FileSignals(
            path="/good.py",
            is_orphan=False,
            stub_ratio=0.0,
            phantom_import_count=0,
            import_count=5,
            broken_call_count=0,
            in_degree=3,
            out_degree=2,
        )
        field.per_file["/good.py"] = fs

        compute_composites(field)

        assert fs.wiring_quality == 1.0

    def test_wiring_quality_orphan_penalty(self):
        """Orphan file has reduced wiring quality."""
        field = SignalField(tier="FULL")
        fs = FileSignals(
            path="/orphan.py",
            is_orphan=True,
            stub_ratio=0.0,
            phantom_import_count=0,
            import_count=1,
        )
        field.per_file["/orphan.py"] = fs

        compute_composites(field)

        # 0.30 penalty for orphan
        assert fs.wiring_quality == 0.7

    def test_wiring_quality_stub_penalty(self):
        """High stub ratio reduces wiring quality."""
        field = SignalField(tier="FULL")
        fs = FileSignals(
            path="/stub.py",
            is_orphan=False,
            stub_ratio=1.0,  # All stubs
            phantom_import_count=0,
            import_count=1,
        )
        field.per_file["/stub.py"] = fs

        compute_composites(field)

        # 0.25 penalty for full stub_ratio
        assert fs.wiring_quality == 0.75


class TestModuleSignalsCollection:
    """Test module signals collection from architecture."""

    def test_module_signals_from_architecture(self):
        """Module signals collected from architecture slot."""
        from shannon_insight.architecture.models import Architecture, Module

        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/mod/a.py")]

        # Create architecture with a module
        arch = Architecture()
        mod = Module(
            path="/mod",
            files=["/mod/a.py"],
            file_count=1,
            cohesion=0.8,
            coupling=0.2,
            instability=0.4,
            abstractness=0.3,
            main_seq_distance=0.1,
            boundary_alignment=0.9,
            role_consistency=0.85,
        )
        arch.modules["/mod"] = mod

        store.architecture.set(arch, "test")

        field = build(store, _make_session(store))

        assert "/mod" in field.per_module
        ms = field.per_module["/mod"]
        assert ms.cohesion == 0.8
        assert ms.coupling == 0.2
        assert ms.instability == 0.4


class TestGlobalSignalsCollection:
    """Test global signals collection."""

    def test_orphan_ratio_computation(self):
        """orphan_ratio computed correctly."""
        store = AnalysisStore()
        store.file_metrics = [
            MockFileMetrics("/a.py"),
            MockFileMetrics("/b.py"),
            MockFileMetrics("/c.py"),
            MockFileMetrics("/d.py"),
        ]

        # Mock structural with some orphans
        structural = MockStructural()
        structural.files = {
            "/a.py": MockFileAnalysis("/a.py", is_orphan=True),
            "/b.py": MockFileAnalysis("/b.py", is_orphan=True),
            "/c.py": MockFileAnalysis("/c.py", is_orphan=False),
            "/d.py": MockFileAnalysis("/d.py", is_orphan=False),
        }
        store.structural.set(structural, "test")

        field = build(store, _make_session(store))

        # 2 orphans out of 4 files = 0.5
        assert field.global_signals.orphan_ratio == 0.5
