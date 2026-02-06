"""Tests for Phase 4 architecture models."""

from shannon_insight.architecture.models import (
    Architecture,
    Layer,
    Module,
    Violation,
    ViolationType,
)


class TestModule:
    """Test Module model."""

    def test_default_values(self):
        mod = Module(path="src/pkg")
        assert mod.path == "src/pkg"
        assert mod.files == []
        assert mod.file_count == 0
        assert mod.afferent_coupling == 0
        assert mod.efferent_coupling == 0
        assert mod.instability is None  # Not computed yet
        assert mod.abstractness == 0.0
        assert mod.main_seq_distance == 0.0
        assert mod.layer == -1

    def test_instability_none_for_isolated(self):
        # Isolated module: Ca=Ce=0, instability should be None
        mod = Module(path="isolated", afferent_coupling=0, efferent_coupling=0)
        assert mod.instability is None

    def test_instability_explicit(self):
        mod = Module(path="unstable", instability=0.8)
        assert mod.instability == 0.8

    def test_martin_metrics(self):
        mod = Module(
            path="balanced",
            afferent_coupling=5,
            efferent_coupling=5,
            instability=0.5,
            abstractness=0.5,
            main_seq_distance=0.0,  # On the main sequence!
        )
        assert mod.instability == 0.5
        assert mod.abstractness == 0.5
        assert mod.main_seq_distance == 0.0


class TestLayer:
    """Test Layer model."""

    def test_default_values(self):
        layer = Layer(depth=0)
        assert layer.depth == 0
        assert layer.modules == []
        assert layer.label == ""

    def test_with_modules(self):
        layer = Layer(depth=2, modules=["src/core", "src/utils"], label="foundation")
        assert layer.depth == 2
        assert len(layer.modules) == 2
        assert layer.label == "foundation"


class TestViolation:
    """Test Violation model."""

    def test_backward_violation(self):
        v = Violation(
            source_module="src/foundation",
            target_module="src/entry",
            source_layer=0,
            target_layer=3,
            violation_type=ViolationType.BACKWARD,
            edge_count=2,
        )
        assert v.violation_type == ViolationType.BACKWARD
        assert v.edge_count == 2

    def test_skip_violation(self):
        v = Violation(
            source_module="src/entry",
            target_module="src/foundation",
            source_layer=3,
            target_layer=0,
            violation_type=ViolationType.SKIP,
        )
        assert v.violation_type == ViolationType.SKIP


class TestArchitecture:
    """Test Architecture model."""

    def test_default_values(self):
        arch = Architecture()
        assert arch.modules == {}
        assert arch.layers == []
        assert arch.violations == []
        assert arch.violation_rate == 0.0
        assert arch.has_layering is False
        assert arch.max_depth == 0
        assert arch.module_count == 0

    def test_with_layering(self):
        arch = Architecture(
            modules={"src/core": Module(path="src/core")},
            layers=[Layer(depth=0), Layer(depth=1)],
            has_layering=True,
            max_depth=1,
            module_count=1,
        )
        assert arch.has_layering is True
        assert arch.max_depth == 1
        assert arch.module_count == 1
