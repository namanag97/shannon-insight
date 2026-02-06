"""Tests for Phase 4 layer inference."""

import pytest

from shannon_insight.architecture.layers import (
    build_module_graph,
    detect_violations,
    infer_layers,
)
from shannon_insight.architecture.models import Module, ViolationType
from shannon_insight.graph.models import DependencyGraph


class TestBuildModuleGraph:
    """Test module graph construction from file-level edges."""

    def test_contracts_file_edges(self):
        modules = {
            "mod_a": Module(path="mod_a", files=["mod_a/x.py", "mod_a/y.py"]),
            "mod_b": Module(path="mod_b", files=["mod_b/z.py"]),
        }
        graph = DependencyGraph(
            adjacency={
                "mod_a/x.py": ["mod_b/z.py"],
                "mod_a/y.py": ["mod_b/z.py"],
                "mod_b/z.py": [],
            },
            all_nodes={"mod_a/x.py", "mod_a/y.py", "mod_b/z.py"},
        )
        module_graph = build_module_graph(modules, graph)
        # Two edges from mod_a to mod_b
        assert module_graph["mod_a"]["mod_b"] == 2
        assert "mod_a" not in module_graph.get("mod_b", {})

    def test_ignores_internal_edges(self):
        modules = {
            "mod_a": Module(path="mod_a", files=["mod_a/x.py", "mod_a/y.py"]),
        }
        graph = DependencyGraph(
            adjacency={"mod_a/x.py": ["mod_a/y.py"], "mod_a/y.py": []},
            all_nodes={"mod_a/x.py", "mod_a/y.py"},
        )
        module_graph = build_module_graph(modules, graph)
        # Internal edges should not appear
        assert "mod_a" not in module_graph.get("mod_a", {})


class TestInferLayers:
    """Test layer inference from module graph."""

    def test_linear_chain(self):
        # entry -> service -> core
        modules = {
            "entry": Module(path="entry", files=["entry/main.py"]),
            "service": Module(path="service", files=["service/api.py"]),
            "core": Module(path="core", files=["core/logic.py"]),
        }
        graph = DependencyGraph(
            adjacency={
                "entry/main.py": ["service/api.py"],
                "service/api.py": ["core/logic.py"],
                "core/logic.py": [],
            },
            all_nodes={"entry/main.py", "service/api.py", "core/logic.py"},
        )
        layers, violations = infer_layers(modules, graph)

        # Should have 3 layers
        assert len(layers) == 3
        # core is foundation (depth 0)
        assert modules["core"].layer == 0
        # service is middle
        assert modules["service"].layer == 1
        # entry is top
        assert modules["entry"].layer == 2
        # No violations in a clean DAG
        assert len(violations) == 0

    def test_isolated_module(self):
        # Module with no connections
        modules = {
            "main": Module(path="main", files=["main/app.py"]),
            "isolated": Module(path="isolated", files=["isolated/util.py"]),
        }
        graph = DependencyGraph(
            adjacency={"main/app.py": [], "isolated/util.py": []},
            all_nodes={"main/app.py", "isolated/util.py"},
        )
        layers, _ = infer_layers(modules, graph)
        # Both should be at layer 0 (no dependencies)
        assert modules["main"].layer == 0
        assert modules["isolated"].layer == 0

    def test_single_module(self):
        modules = {"only": Module(path="only", files=["only/code.py"])}
        graph = DependencyGraph(
            adjacency={"only/code.py": []},
            all_nodes={"only/code.py"},
        )
        layers, violations = infer_layers(modules, graph)
        assert len(layers) == 1
        assert modules["only"].layer == 0
        assert len(violations) == 0


class TestDetectViolations:
    """Test layer violation detection."""

    def test_backward_violation(self):
        # Lower layer imports upper layer
        modules = {
            "foundation": Module(path="foundation", files=["foundation/base.py"], layer=0),
            "entry": Module(path="entry", files=["entry/main.py"], layer=2),
        }
        # foundation imports entry (backward!)
        module_graph = {"foundation": {"entry": 1}}

        violations = detect_violations(modules, module_graph)
        assert len(violations) == 1
        assert violations[0].violation_type == ViolationType.BACKWARD
        assert violations[0].source_module == "foundation"
        assert violations[0].target_module == "entry"

    def test_skip_violation(self):
        # Layer 2 imports layer 0, skipping layer 1
        modules = {
            "core": Module(path="core", files=["core/base.py"], layer=0),
            "middle": Module(path="middle", files=["middle/svc.py"], layer=1),
            "top": Module(path="top", files=["top/app.py"], layer=2),
        }
        # top imports core directly, skipping middle
        module_graph = {"top": {"core": 1}}

        violations = detect_violations(modules, module_graph)
        assert len(violations) == 1
        assert violations[0].violation_type == ViolationType.SKIP
        assert violations[0].source_module == "top"
        assert violations[0].target_module == "core"

    def test_no_violation_adjacent(self):
        # Adjacent layer import is OK
        modules = {
            "layer0": Module(path="layer0", files=["l0/a.py"], layer=0),
            "layer1": Module(path="layer1", files=["l1/b.py"], layer=1),
        }
        module_graph = {"layer1": {"layer0": 1}}

        violations = detect_violations(modules, module_graph)
        assert len(violations) == 0
