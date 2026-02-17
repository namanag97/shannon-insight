"""Tests for FactStore provenance integration."""

from shannon_insight.infrastructure.entities import EntityId, EntityType
from shannon_insight.infrastructure.signals import Signal
from shannon_insight.infrastructure.store import FactStore


class TestFactStoreProvenance:
    """Tests for provenance tracking in FactStore."""

    def test_provenance_disabled_by_default(self):
        """Provenance tracking is off by default."""
        store = FactStore(root="/tmp/test")
        assert not store.provenance_enabled
        assert store.provenance is None

    def test_provenance_enabled(self):
        """Provenance tracking can be enabled."""
        store = FactStore(root="/tmp/test", enable_provenance=True)
        assert store.provenance_enabled
        assert store.provenance is not None

    def test_set_signal_records_provenance(self):
        """set_signal records provenance when tracking is enabled."""
        store = FactStore(root="/tmp/test", enable_provenance=True)
        entity = EntityId(EntityType.FILE, "src/main.py")

        store.set_signal(
            entity,
            Signal.PAGERANK,
            0.042,
            producer="StructuralAnalyzer",
            inputs=["in_degree", "out_degree"],
            formula="PR(v) = (1-d)/N + d * sum(PR(u)/out(u))",
        )

        # Verify signal was set
        assert store.get_signal(entity, Signal.PAGERANK) == 0.042

        # Verify provenance was recorded
        prov = store.provenance.get_latest("src/main.py", Signal.PAGERANK)
        assert prov is not None
        assert prov.value == 0.042
        assert prov.producer == "StructuralAnalyzer"
        assert prov.inputs == ["in_degree", "out_degree"]
        assert prov.formula == "PR(v) = (1-d)/N + d * sum(PR(u)/out(u))"

    def test_set_signal_no_provenance_when_disabled(self):
        """set_signal does not record provenance when tracking is disabled."""
        store = FactStore(root="/tmp/test", enable_provenance=False)
        entity = EntityId(EntityType.FILE, "src/main.py")

        # Extra kwargs are ignored silently
        store.set_signal(
            entity,
            Signal.PAGERANK,
            0.042,
            producer="StructuralAnalyzer",
            inputs=["in_degree"],
        )

        assert store.get_signal(entity, Signal.PAGERANK) == 0.042
        # No provenance
        assert store.provenance is None

    def test_set_signal_default_producer(self):
        """Default producer is 'unknown' when not specified."""
        store = FactStore(root="/tmp/test", enable_provenance=True)
        entity = EntityId(EntityType.FILE, "src/main.py")

        store.set_signal(entity, Signal.LINES, 100)

        prov = store.provenance.get_latest("src/main.py", Signal.LINES)
        assert prov is not None
        assert prov.producer == "unknown"

    def test_explain_signal(self):
        """explain_signal returns human-readable explanation."""
        store = FactStore(root="/tmp/test", enable_provenance=True)
        entity = EntityId(EntityType.FILE, "src/main.py")

        store.set_signal(
            entity,
            Signal.PAGERANK,
            0.042,
            producer="StructuralAnalyzer",
            formula="PR(v) = (1-d)/N + d * sum(PR(u)/out(u))",
        )

        explanation = store.explain_signal(entity, Signal.PAGERANK)
        assert "pagerank = 0.042" in explanation
        assert "StructuralAnalyzer" in explanation
        assert "Formula:" in explanation

    def test_explain_signal_disabled(self):
        """explain_signal returns helpful message when tracking is disabled."""
        store = FactStore(root="/tmp/test", enable_provenance=False)
        entity = EntityId(EntityType.FILE, "src/main.py")

        explanation = store.explain_signal(entity, Signal.PAGERANK)
        assert "not enabled" in explanation
        assert "--trace" in explanation

    def test_trace_signal(self):
        """trace_signal returns dependency tree."""
        store = FactStore(root="/tmp/test", enable_provenance=True)
        entity = EntityId(EntityType.FILE, "src/main.py")

        store.set_signal(entity, Signal.IN_DEGREE, 5, producer="structural")
        store.set_signal(entity, Signal.OUT_DEGREE, 3, producer="structural")
        store.set_signal(
            entity,
            Signal.PAGERANK,
            0.042,
            producer="structural",
            inputs=["in_degree", "out_degree"],
        )

        trace = store.trace_signal(entity, Signal.PAGERANK)
        assert len(trace) == 3
        signals = [t.signal for t in trace]
        assert Signal.PAGERANK in signals
        assert Signal.IN_DEGREE in signals
        assert Signal.OUT_DEGREE in signals

    def test_trace_signal_disabled(self):
        """trace_signal returns empty list when tracking is disabled."""
        store = FactStore(root="/tmp/test", enable_provenance=False)
        entity = EntityId(EntityType.FILE, "src/main.py")

        trace = store.trace_signal(entity, Signal.PAGERANK)
        assert trace == []

    def test_backward_compatibility(self):
        """Existing code that calls set_signal without provenance args still works."""
        store = FactStore(root="/tmp/test")
        entity = EntityId(EntityType.FILE, "src/main.py")

        # Old-style call (no producer/inputs/formula)
        store.set_signal(entity, Signal.LINES, 100)
        assert store.get_signal(entity, Signal.LINES) == 100

    def test_provenance_with_multiple_entities(self):
        """Provenance is correctly keyed by entity."""
        store = FactStore(root="/tmp/test", enable_provenance=True)
        entity_a = EntityId(EntityType.FILE, "a.py")
        entity_b = EntityId(EntityType.FILE, "b.py")

        store.set_signal(entity_a, Signal.LINES, 100, producer="scanning")
        store.set_signal(entity_b, Signal.LINES, 200, producer="scanning")

        prov_a = store.provenance.get_latest("a.py", Signal.LINES)
        prov_b = store.provenance.get_latest("b.py", Signal.LINES)

        assert prov_a.value == 100
        assert prov_b.value == 200

    def test_provenance_record_count(self):
        """Track total records across multiple set_signal calls."""
        store = FactStore(root="/tmp/test", enable_provenance=True)
        entity = EntityId(EntityType.FILE, "src/main.py")

        store.set_signal(entity, Signal.LINES, 100, producer="scanning")
        store.set_signal(entity, Signal.FUNCTION_COUNT, 5, producer="scanning")
        store.set_signal(entity, Signal.PAGERANK, 0.04, producer="structural")

        assert store.provenance.record_count == 3
