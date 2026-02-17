"""Tests for FusionPipeline skeleton.

This tests the Phase 0 skeleton structure. Full implementation is Phase 5.
"""

from shannon_insight.config import AnalysisConfig
from shannon_insight.environment import Environment
from shannon_insight.insights.store import AnalysisStore
from shannon_insight.scanning.syntax import FileSyntax, FunctionDef
from shannon_insight.session import AnalysisSession, Tier
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


def _make_session(store):
    """Helper to create a test session."""
    config = AnalysisConfig()
    file_count = len(store.file_syntax.get({}))
    env = Environment(
        root=store.root_dir or ".",
        file_count=file_count,
        is_git_repo=False,
    )
    return AnalysisSession(config=config, env=env)


def _make_file_syntax(path: str) -> FileSyntax:
    """Helper to create a FileSyntax for testing."""
    functions = [
        FunctionDef(
            "f1", [], body_tokens=10, signature_tokens=3, nesting_depth=1, start_line=1, end_line=3
        ),
        FunctionDef(
            "f2", [], body_tokens=20, signature_tokens=5, nesting_depth=2, start_line=5, end_line=10
        ),
        FunctionDef(
            "f3",
            [],
            body_tokens=30,
            signature_tokens=8,
            nesting_depth=1,
            start_line=12,
            end_line=20,
        ),
    ]
    return FileSyntax(
        path=path,
        functions=functions,
        classes=[],
        imports=[],
        language="python",
        has_main_guard=False,
        mtime=0.0,
        _lines=100,
        _tokens=200,
        _complexity=5.0,
    )


class TestFusionPipelineStructure:
    """Test FusionPipeline typestate structure."""

    def test_pipeline_creates_signal_field(self):
        """Pipeline creates SignalField."""
        store = AnalysisStore()
        pipeline = FusionPipeline(store, _make_session(store))
        assert isinstance(pipeline.field, SignalField)

    def test_step1_returns_collected(self):
        """step1_collect returns _Collected."""
        store = AnalysisStore()
        file_syntax = {"/a.py": _make_file_syntax("/a.py")}
        store.file_syntax.set(file_syntax, produced_by="test")
        pipeline = FusionPipeline(store, _make_session(store))
        result = pipeline.step1_collect()
        assert isinstance(result, _Collected)

    def test_step2_returns_raw_risked(self):
        """step2_raw_risk returns _RawRisked."""
        store = AnalysisStore()
        file_syntax = {"/a.py": _make_file_syntax("/a.py")}
        store.file_syntax.set(file_syntax, produced_by="test")
        collected = FusionPipeline(store, _make_session(store)).step1_collect()
        result = collected.step2_raw_risk()
        assert isinstance(result, _RawRisked)

    def test_step3_returns_normalized(self):
        """step3_normalize returns _Normalized."""
        store = AnalysisStore()
        file_syntax = {"/a.py": _make_file_syntax("/a.py")}
        store.file_syntax.set(file_syntax, produced_by="test")
        raw_risked = FusionPipeline(store, _make_session(store)).step1_collect().step2_raw_risk()
        result = raw_risked.step3_normalize()
        assert isinstance(result, _Normalized)

    def test_step4_returns_module_temporal(self):
        """step4_module_temporal returns _ModuleTemporal."""
        store = AnalysisStore()
        file_syntax = {"/a.py": _make_file_syntax("/a.py")}
        store.file_syntax.set(file_syntax, produced_by="test")
        normalized = (
            FusionPipeline(store, _make_session(store))
            .step1_collect()
            .step2_raw_risk()
            .step3_normalize()
        )
        result = normalized.step4_module_temporal()
        assert isinstance(result, _ModuleTemporal)

    def test_step5_returns_composited(self):
        """step5_composites returns _Composited."""
        store = AnalysisStore()
        file_syntax = {"/a.py": _make_file_syntax("/a.py")}
        store.file_syntax.set(file_syntax, produced_by="test")
        module_temporal = (
            FusionPipeline(store, _make_session(store))
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
        file_syntax = {"/a.py": _make_file_syntax("/a.py")}
        store.file_syntax.set(file_syntax, produced_by="test")
        composited = (
            FusionPipeline(store, _make_session(store))
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
        file_syntax = {"/a.py": _make_file_syntax("/a.py")}
        store.file_syntax.set(file_syntax, produced_by="test")
        result = build(store, _make_session(store))
        assert isinstance(result, SignalField)

    def test_build_chains_all_steps(self):
        """build() chains all 6 steps correctly."""
        store = AnalysisStore()
        file_syntax = {"/a.py": _make_file_syntax("/a.py")}
        store.file_syntax.set(file_syntax, produced_by="test")
        field = build(store, _make_session(store))
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
        assert field.tier == Tier.FULL

    def test_signal_field_per_file_dict(self):
        """per_file is a dict."""
        field = SignalField()
        assert isinstance(field.per_file, dict)


class TestOrderEnforcement:
    """Test that typestate pattern enforces ordering."""

    def test_cannot_skip_steps(self):
        """Cannot call step5 on _Collected (must go through steps 2,3,4)."""
        store = AnalysisStore()
        file_syntax = {"/a.py": _make_file_syntax("/a.py")}
        store.file_syntax.set(file_syntax, produced_by="test")
        collected = FusionPipeline(store, _make_session(store)).step1_collect()

        # _Collected only has step2_raw_risk
        assert hasattr(collected, "step2_raw_risk")
        assert not hasattr(collected, "step5_composites")
        assert not hasattr(collected, "step6_laplacian")

    def test_each_stage_has_only_next_step(self):
        """Each stage only exposes the next step in the chain."""
        store = AnalysisStore()
        file_syntax = {"/a.py": _make_file_syntax("/a.py")}
        store.file_syntax.set(file_syntax, produced_by="test")

        # _Collected -> step2_raw_risk
        collected = FusionPipeline(store, _make_session(store)).step1_collect()
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
