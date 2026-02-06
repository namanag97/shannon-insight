"""Tests for FusionPipeline skeleton.

This tests the Phase 0 skeleton structure. Full implementation is Phase 5.
"""

from shannon_insight.insights.store_v2 import AnalysisStore
from shannon_insight.signals.fusion import (
    FusionPipeline,
    SignalField,
    _Collected,
    _Composited,
    _ModuleTemporal,
    _Normalized,
    _RawRisked,
    build,
)


class MockFileMetrics:
    """Mock file metrics."""

    def __init__(self, path: str):
        self.path = path
        self.lines = 100
        self.functions = 5
        self.structs = 1
        self.nesting_depth = 2
        self.imports = []
        self.function_sizes = [10, 20, 30]


class TestFusionPipelineStructure:
    """Test FusionPipeline typestate structure."""

    def test_pipeline_creates_signal_field(self):
        """Pipeline creates SignalField."""
        store = AnalysisStore()
        pipeline = FusionPipeline(store)
        assert isinstance(pipeline.field, SignalField)

    def test_step1_returns_collected(self):
        """step1_collect returns _Collected."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]
        pipeline = FusionPipeline(store)
        result = pipeline.step1_collect()
        assert isinstance(result, _Collected)

    def test_step2_returns_raw_risked(self):
        """step2_raw_risk returns _RawRisked."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]
        collected = FusionPipeline(store).step1_collect()
        result = collected.step2_raw_risk()
        assert isinstance(result, _RawRisked)

    def test_step3_returns_normalized(self):
        """step3_normalize returns _Normalized."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]
        raw_risked = FusionPipeline(store).step1_collect().step2_raw_risk()
        result = raw_risked.step3_normalize()
        assert isinstance(result, _Normalized)

    def test_step4_returns_module_temporal(self):
        """step4_module_temporal returns _ModuleTemporal."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]
        normalized = FusionPipeline(store).step1_collect().step2_raw_risk().step3_normalize()
        result = normalized.step4_module_temporal()
        assert isinstance(result, _ModuleTemporal)

    def test_step5_returns_composited(self):
        """step5_composites returns _Composited."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]
        module_temporal = (
            FusionPipeline(store)
            .step1_collect()
            .step2_raw_risk()
            .step3_normalize()
            .step4_module_temporal()
        )
        result = module_temporal.step5_composites()
        assert isinstance(result, _Composited)

    def test_step6_returns_signal_field(self):
        """step6_laplacian returns SignalField."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]
        composited = (
            FusionPipeline(store)
            .step1_collect()
            .step2_raw_risk()
            .step3_normalize()
            .step4_module_temporal()
            .step5_composites()
        )
        result = composited.step6_laplacian()
        assert isinstance(result, SignalField)


class TestBuildFunction:
    """Test build() convenience function."""

    def test_build_returns_signal_field(self):
        """build() returns SignalField."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]
        result = build(store)
        assert isinstance(result, SignalField)

    def test_build_chains_all_steps(self):
        """build() chains all 6 steps correctly."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]
        field = build(store)
        # Should have the standard attributes
        assert hasattr(field, "tier")
        assert hasattr(field, "per_file")
        assert hasattr(field, "per_module")
        assert hasattr(field, "global_signals")


class TestSignalField:
    """Test SignalField data structure."""

    def test_signal_field_attributes(self):
        """SignalField has required attributes."""
        field = SignalField()
        assert hasattr(field, "tier")
        assert hasattr(field, "per_file")
        assert hasattr(field, "per_module")
        assert hasattr(field, "global_signals")
        assert hasattr(field, "delta_h")

    def test_signal_field_default_tier(self):
        """SignalField defaults to FULL tier."""
        field = SignalField()
        assert field.tier == "FULL"

    def test_signal_field_per_file_dict(self):
        """per_file is a dict."""
        field = SignalField()
        assert isinstance(field.per_file, dict)


class TestOrderEnforcement:
    """Test that typestate pattern enforces ordering."""

    def test_cannot_skip_steps(self):
        """Cannot call step5 on _Collected (must go through steps 2,3,4)."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]
        collected = FusionPipeline(store).step1_collect()

        # _Collected only has step2_raw_risk
        assert hasattr(collected, "step2_raw_risk")
        assert not hasattr(collected, "step5_composites")
        assert not hasattr(collected, "step6_laplacian")

    def test_each_stage_has_only_next_step(self):
        """Each stage only exposes the next step in the chain."""
        store = AnalysisStore()
        store.file_metrics = [MockFileMetrics("/a.py")]

        # _Collected -> step2_raw_risk
        collected = FusionPipeline(store).step1_collect()
        assert hasattr(collected, "step2_raw_risk")

        # _RawRisked -> step3_normalize
        raw_risked = collected.step2_raw_risk()
        assert hasattr(raw_risked, "step3_normalize")

        # _Normalized -> step4_module_temporal
        normalized = raw_risked.step3_normalize()
        assert hasattr(normalized, "step4_module_temporal")

        # _ModuleTemporal -> step5_composites
        module_temporal = normalized.step4_module_temporal()
        assert hasattr(module_temporal, "step5_composites")

        # _Composited -> step6_laplacian
        composited = module_temporal.step5_composites()
        assert hasattr(composited, "step6_laplacian")
