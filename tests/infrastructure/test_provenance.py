"""Tests for SignalProvenance and ProvenanceStore."""

import json
import tempfile
from datetime import datetime
from pathlib import Path

from shannon_insight.infrastructure.provenance import (
    ProvenanceStore,
    SignalProvenance,
    _serialize_value,
)
from shannon_insight.infrastructure.signals import Signal


class TestSignalProvenance:
    """Tests for the SignalProvenance dataclass."""

    def test_create_basic(self):
        """Basic creation with required fields."""
        prov = SignalProvenance(
            signal=Signal.PAGERANK,
            value=0.042,
            producer="StructuralAnalyzer",
            phase=0,
            timestamp=datetime(2026, 1, 15, 10, 30, 0),
            inputs=["in_degree", "out_degree"],
            formula="PR(v) = (1-d)/N + d * sum(PR(u)/out(u))",
            entity_path="src/main.py",
        )
        assert prov.signal == Signal.PAGERANK
        assert prov.value == 0.042
        assert prov.producer == "StructuralAnalyzer"
        assert prov.phase == 0
        assert prov.entity_path == "src/main.py"
        assert prov.inputs == ["in_degree", "out_degree"]
        assert prov.formula == "PR(v) = (1-d)/N + d * sum(PR(u)/out(u))"

    def test_create_without_formula(self):
        """Raw signals have no formula."""
        prov = SignalProvenance(
            signal=Signal.LINES,
            value=150,
            producer="scanning",
            phase=0,
            timestamp=datetime.now(),
            inputs=[],
            formula=None,
            entity_path="src/main.py",
        )
        assert prov.formula is None
        assert prov.inputs == []

    def test_to_dict(self):
        """Serialization to JSON-compatible dict."""
        ts = datetime(2026, 1, 15, 10, 30, 0)
        prov = SignalProvenance(
            signal=Signal.PAGERANK,
            value=0.042,
            producer="StructuralAnalyzer",
            phase=0,
            timestamp=ts,
            inputs=["in_degree", "out_degree"],
            formula="PR(v) = (1-d)/N + d * sum(PR(u)/out(u))",
            entity_path="src/main.py",
        )
        d = prov.to_dict()
        assert d["signal"] == "pagerank"
        assert d["value"] == 0.042
        assert d["producer"] == "StructuralAnalyzer"
        assert d["phase"] == 0
        assert d["timestamp"] == ts.isoformat()
        assert d["inputs"] == ["in_degree", "out_degree"]
        assert d["formula"] == "PR(v) = (1-d)/N + d * sum(PR(u)/out(u))"
        assert d["entity_path"] == "src/main.py"

        # Verify JSON-serializable
        json.dumps(d)

    def test_to_dict_with_complex_value(self):
        """Values that need serialization (e.g., dicts, enums)."""
        prov = SignalProvenance(
            signal=Signal.ROLE,
            value="model",
            producer="semantic",
            phase=2,
            timestamp=datetime.now(),
            inputs=[],
            formula=None,
            entity_path="src/model.py",
        )
        d = prov.to_dict()
        assert d["value"] == "model"

        # Verify JSON-serializable
        json.dumps(d)


class TestSerializeValue:
    """Tests for the _serialize_value helper."""

    def test_primitives(self):
        assert _serialize_value(42) == 42
        assert _serialize_value(3.14) == 3.14
        assert _serialize_value("hello") == "hello"
        assert _serialize_value(True) is True
        assert _serialize_value(None) is None

    def test_list(self):
        assert _serialize_value([1, 2, 3]) == [1, 2, 3]

    def test_dict(self):
        assert _serialize_value({"a": 1, "b": 2}) == {"a": 1, "b": 2}

    def test_nested(self):
        assert _serialize_value({"a": [1, {"b": 2}]}) == {"a": [1, {"b": 2}]}

    def test_non_serializable(self):
        """Non-serializable objects fall back to str."""
        result = _serialize_value(object())
        assert isinstance(result, str)


class TestProvenanceStore:
    """Tests for the ProvenanceStore."""

    def test_record_and_retrieve(self):
        """Record a provenance entry and retrieve it."""
        store = ProvenanceStore()
        prov = store.record(
            entity_path="src/main.py",
            signal=Signal.PAGERANK,
            value=0.042,
            producer="StructuralAnalyzer",
        )
        assert prov.signal == Signal.PAGERANK
        assert prov.value == 0.042
        assert prov.producer == "StructuralAnalyzer"
        assert prov.phase == 0  # default
        assert prov.entity_path == "src/main.py"

    def test_record_with_inputs_and_formula(self):
        """Record with full metadata."""
        store = ProvenanceStore()
        prov = store.record(
            entity_path="src/main.py",
            signal=Signal.BUS_FACTOR,
            value=2.0,
            producer="TemporalAnalyzer",
            inputs=["author_entropy"],
            formula="bus_factor = 2^H",
            phase=3,
        )
        assert prov.inputs == ["author_entropy"]
        assert prov.formula == "bus_factor = 2^H"
        assert prov.phase == 3

    def test_record_count(self):
        """Track total record count."""
        store = ProvenanceStore()
        assert store.record_count == 0

        store.record("a.py", Signal.LINES, 100, "scanning")
        assert store.record_count == 1

        store.record("b.py", Signal.LINES, 200, "scanning")
        assert store.record_count == 2

    def test_get_latest(self):
        """Get the most recent provenance for an entity+signal."""
        store = ProvenanceStore()
        store.record("a.py", Signal.LINES, 100, "scanning")
        store.record("a.py", Signal.LINES, 150, "scanning")  # overwrite

        latest = store.get_latest("a.py", Signal.LINES)
        assert latest is not None
        assert latest.value == 150

    def test_get_latest_returns_none(self):
        """Returns None for unrecorded signal."""
        store = ProvenanceStore()
        assert store.get_latest("a.py", Signal.LINES) is None

    def test_signals_for_entity(self):
        """Get all signals for an entity."""
        store = ProvenanceStore()
        store.record("a.py", Signal.LINES, 100, "scanning")
        store.record("a.py", Signal.FUNCTION_COUNT, 5, "scanning")
        store.record("b.py", Signal.LINES, 200, "scanning")

        signals = store.signals_for_entity("a.py")
        assert len(signals) == 2
        assert Signal.LINES in signals
        assert Signal.FUNCTION_COUNT in signals
        assert signals[Signal.LINES].value == 100
        assert signals[Signal.FUNCTION_COUNT].value == 5

    def test_explain_basic(self):
        """Human-readable explanation of a signal."""
        store = ProvenanceStore()
        store.record("src/main.py", Signal.LINES, 150, "scanning")

        explanation = store.explain("src/main.py", Signal.LINES)
        assert "lines = 150" in explanation
        assert "scanning" in explanation
        assert "phase 0" in explanation

    def test_explain_with_formula(self):
        """Explanation includes formula when present."""
        store = ProvenanceStore()
        store.record(
            "src/main.py",
            Signal.PAGERANK,
            0.042,
            "StructuralAnalyzer",
            formula="PR(v) = (1-d)/N + d * sum(PR(u)/out(u))",
        )

        explanation = store.explain("src/main.py", Signal.PAGERANK)
        assert "Formula:" in explanation
        assert "PR(v)" in explanation

    def test_explain_with_inputs(self):
        """Explanation includes input signals."""
        store = ProvenanceStore()
        store.record(
            "src/main.py",
            Signal.IN_DEGREE,
            5,
            "StructuralAnalyzer",
        )
        store.record(
            "src/main.py",
            Signal.OUT_DEGREE,
            3,
            "StructuralAnalyzer",
        )
        store.record(
            "src/main.py",
            Signal.PAGERANK,
            0.042,
            "StructuralAnalyzer",
            inputs=["in_degree", "out_degree"],
        )

        explanation = store.explain("src/main.py", Signal.PAGERANK)
        assert "Inputs: in_degree, out_degree" in explanation
        assert "in_degree = 5" in explanation
        assert "out_degree = 3" in explanation

    def test_explain_missing(self):
        """Explanation for unrecorded signal."""
        store = ProvenanceStore()
        explanation = store.explain("src/main.py", Signal.PAGERANK)
        assert "No provenance recorded" in explanation

    def test_trace_simple(self):
        """Trace a signal with no inputs."""
        store = ProvenanceStore()
        store.record("src/main.py", Signal.LINES, 150, "scanning")

        trace = store.trace("src/main.py", Signal.LINES)
        assert len(trace) == 1
        assert trace[0].signal == Signal.LINES

    def test_trace_with_dependencies(self):
        """Trace follows input dependencies."""
        store = ProvenanceStore()
        store.record("src/main.py", Signal.IN_DEGREE, 5, "StructuralAnalyzer")
        store.record("src/main.py", Signal.OUT_DEGREE, 3, "StructuralAnalyzer")
        store.record(
            "src/main.py",
            Signal.PAGERANK,
            0.042,
            "StructuralAnalyzer",
            inputs=["in_degree", "out_degree"],
        )

        trace = store.trace("src/main.py", Signal.PAGERANK)
        # Should include: in_degree, out_degree, pagerank (in dependency order)
        assert len(trace) == 3
        signal_names = [t.signal for t in trace]
        # Inputs should come before the signal
        assert signal_names.index(Signal.IN_DEGREE) < signal_names.index(Signal.PAGERANK)
        assert signal_names.index(Signal.OUT_DEGREE) < signal_names.index(Signal.PAGERANK)

    def test_trace_handles_cycles(self):
        """Trace doesn't infinite-loop on circular dependencies."""
        store = ProvenanceStore()
        # Create a cycle: A depends on B, B depends on A
        store.record(
            "src/main.py",
            Signal.IN_DEGREE,
            5,
            "test",
            inputs=["out_degree"],
        )
        store.record(
            "src/main.py",
            Signal.OUT_DEGREE,
            3,
            "test",
            inputs=["in_degree"],
        )

        # Should not hang
        trace = store.trace("src/main.py", Signal.IN_DEGREE)
        assert len(trace) == 2

    def test_trace_missing(self):
        """Trace returns empty list for unrecorded signal."""
        store = ProvenanceStore()
        trace = store.trace("src/main.py", Signal.PAGERANK)
        assert trace == []

    def test_export_session_log(self):
        """Export provenance to JSON Lines file."""
        store = ProvenanceStore()
        store.record("src/main.py", Signal.LINES, 150, "scanning")
        store.record("src/main.py", Signal.FUNCTION_COUNT, 5, "scanning")
        store.record("src/auth.py", Signal.LINES, 200, "scanning")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            path = f.name

        try:
            store.export_session_log(path)

            with open(path) as f:
                lines = f.readlines()

            assert len(lines) == 3

            # Each line is valid JSON
            for line in lines:
                record = json.loads(line)
                assert "signal" in record
                assert "value" in record
                assert "producer" in record
                assert "timestamp" in record
                assert "entity_path" in record

            # Check first record
            first = json.loads(lines[0])
            assert first["signal"] == "lines"
            assert first["value"] == 150
            assert first["producer"] == "scanning"
            assert first["entity_path"] == "src/main.py"
        finally:
            Path(path).unlink(missing_ok=True)

    def test_phase_tracking(self):
        """Phase is tracked per-record."""
        store = ProvenanceStore(phase=0)
        store.record("a.py", Signal.LINES, 100, "scanning")

        store.phase = 3
        store.record("a.py", Signal.TOTAL_CHANGES, 50, "temporal")

        records = store.all_records
        assert records[0].phase == 0
        assert records[1].phase == 3

    def test_phase_override(self):
        """Per-record phase override."""
        store = ProvenanceStore(phase=0)
        prov = store.record("a.py", Signal.TOTAL_CHANGES, 50, "temporal", phase=3)
        assert prov.phase == 3

    def test_all_records_order(self):
        """Records are returned in insertion order."""
        store = ProvenanceStore()
        store.record("a.py", Signal.LINES, 100, "scanning")
        store.record("b.py", Signal.LINES, 200, "scanning")
        store.record("a.py", Signal.FUNCTION_COUNT, 5, "scanning")

        records = store.all_records
        assert len(records) == 3
        assert records[0].entity_path == "a.py"
        assert records[0].signal == Signal.LINES
        assert records[1].entity_path == "b.py"
        assert records[2].signal == Signal.FUNCTION_COUNT

    def test_clear(self):
        """Clear all records."""
        store = ProvenanceStore()
        store.record("a.py", Signal.LINES, 100, "scanning")
        store.record("b.py", Signal.LINES, 200, "scanning")
        assert store.record_count == 2

        store.clear()
        assert store.record_count == 0
        assert store.all_records == []
        assert store.get_latest("a.py", Signal.LINES) is None

    def test_explain_with_non_signal_inputs(self):
        """Inputs that aren't valid Signal enum values are gracefully skipped."""
        store = ProvenanceStore()
        store.record(
            "src/main.py",
            Signal.PAGERANK,
            0.042,
            "StructuralAnalyzer",
            inputs=["custom_metric", "in_degree"],
        )
        store.record("src/main.py", Signal.IN_DEGREE, 5, "StructuralAnalyzer")

        explanation = store.explain("src/main.py", Signal.PAGERANK)
        assert "Inputs: custom_metric, in_degree" in explanation
        # in_degree should be resolved, custom_metric silently skipped
        assert "in_degree = 5" in explanation
