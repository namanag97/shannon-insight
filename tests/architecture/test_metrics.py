"""Tests for Phase 4 Martin metrics computation."""

import pytest

from shannon_insight.architecture.metrics import (
    compute_abstractness,
    compute_coupling,
    compute_instability,
    compute_main_seq_distance,
    compute_role_consistency,
)
from shannon_insight.architecture.models import Module
from shannon_insight.graph.models import DependencyGraph


class TestComputeCoupling:
    """Test afferent/efferent coupling computation."""

    def test_isolated_module(self):
        # Module with no external edges
        mod = Module(path="isolated", files=["a.py", "b.py"])
        modules = {"isolated": mod}
        graph = DependencyGraph(
            adjacency={"a.py": ["b.py"], "b.py": []},
            reverse={"a.py": [], "b.py": ["a.py"]},
            all_nodes={"a.py", "b.py"},
        )
        ca, ce = compute_coupling(mod, modules, graph)
        assert ca == 0
        assert ce == 0

    def test_efferent_coupling(self):
        # Module A depends on Module B
        mod_a = Module(path="mod_a", files=["mod_a/x.py"])
        mod_b = Module(path="mod_b", files=["mod_b/y.py"])
        modules = {"mod_a": mod_a, "mod_b": mod_b}
        graph = DependencyGraph(
            adjacency={"mod_a/x.py": ["mod_b/y.py"], "mod_b/y.py": []},
            reverse={"mod_a/x.py": [], "mod_b/y.py": ["mod_a/x.py"]},
            all_nodes={"mod_a/x.py", "mod_b/y.py"},
        )
        ca_a, ce_a = compute_coupling(mod_a, modules, graph)
        ca_b, ce_b = compute_coupling(mod_b, modules, graph)
        # mod_a has 1 outgoing edge to mod_b
        assert ce_a == 1
        assert ca_a == 0
        # mod_b has 1 incoming edge from mod_a
        assert ca_b == 1
        assert ce_b == 0


class TestComputeInstability:
    """Test instability metric I = Ce / (Ca + Ce)."""

    def test_stable_module(self):
        # Many incoming, no outgoing -> I = 0
        i = compute_instability(ca=10, ce=0)
        assert i == 0.0

    def test_unstable_module(self):
        # No incoming, many outgoing -> I = 1
        i = compute_instability(ca=0, ce=10)
        assert i == 1.0

    def test_balanced_module(self):
        # Equal incoming and outgoing -> I = 0.5
        i = compute_instability(ca=5, ce=5)
        assert i == 0.5

    def test_isolated_module_none(self):
        # No coupling at all -> None (cannot measure)
        i = compute_instability(ca=0, ce=0)
        assert i is None


class TestComputeAbstractness:
    """Test abstractness metric A = abstract_symbols / total_symbols."""

    def test_concrete_module(self):
        # No abstract classes/methods -> A = 0
        # Mock: files without ABC/Protocol patterns
        a = compute_abstractness(
            class_count=5,
            abstract_class_count=0,
            protocol_count=0,
            abstract_method_count=0,
        )
        assert a == 0.0

    def test_fully_abstract_module(self):
        # All abstract -> A = 1
        a = compute_abstractness(
            class_count=3,
            abstract_class_count=3,
            protocol_count=0,
            abstract_method_count=0,
        )
        assert a == 1.0

    def test_mixed_module(self):
        # Some abstract
        a = compute_abstractness(
            class_count=4,
            abstract_class_count=2,
            protocol_count=0,
            abstract_method_count=0,
        )
        assert a == 0.5

    def test_no_classes_zero(self):
        # No classes at all
        a = compute_abstractness(
            class_count=0,
            abstract_class_count=0,
            protocol_count=0,
            abstract_method_count=0,
        )
        assert a == 0.0


class TestComputeMainSeqDistance:
    """Test main sequence distance D = |A + I - 1|."""

    def test_on_main_sequence(self):
        # A = 0.5, I = 0.5 -> D = 0
        d = compute_main_seq_distance(abstractness=0.5, instability=0.5)
        assert d == pytest.approx(0.0)

    def test_zone_of_pain(self):
        # A = 0, I = 0 (stable and concrete) -> D = 1
        d = compute_main_seq_distance(abstractness=0.0, instability=0.0)
        assert d == pytest.approx(1.0)

    def test_zone_of_uselessness(self):
        # A = 1, I = 1 (abstract and unstable) -> D = 1
        d = compute_main_seq_distance(abstractness=1.0, instability=1.0)
        assert d == pytest.approx(1.0)

    def test_none_instability(self):
        # Cannot compute without instability
        d = compute_main_seq_distance(abstractness=0.5, instability=None)
        assert d == 0.0


class TestComputeRoleConsistency:
    """Test role consistency = max(role_count) / total_files."""

    def test_all_same_role(self):
        roles = {"a.py": "UTILITY", "b.py": "UTILITY", "c.py": "UTILITY"}
        files = ["a.py", "b.py", "c.py"]
        consistency, dominant = compute_role_consistency(files, roles)
        assert consistency == 1.0
        assert dominant == "UTILITY"

    def test_mixed_roles(self):
        roles = {"a.py": "UTILITY", "b.py": "MODEL", "c.py": "UTILITY"}
        files = ["a.py", "b.py", "c.py"]
        consistency, dominant = compute_role_consistency(files, roles)
        assert consistency == pytest.approx(2 / 3)
        assert dominant == "UTILITY"

    def test_empty_files(self):
        consistency, dominant = compute_role_consistency([], {})
        assert consistency == 0.0
        assert dominant == "UNKNOWN"
