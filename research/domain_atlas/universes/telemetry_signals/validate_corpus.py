#!/usr/bin/env python3
"""Validate telemetry signal boundaries, identities and non-collapse laws."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import build_corpus


ROOT = Path(__file__).resolve().parent


def load(name: str) -> list[dict]:
    return [json.loads(line) for line in (ROOT / name).read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    data = {name: load(name) for name in build_corpus.FILES}
    for name, rows in data.items():
        assert manifest["files"][name]["records"] == len(rows)
        assert manifest["files"][name]["sha256"] == hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    assert len(data["sources.jsonl"]) >= 15
    assert len(data["bounded-contexts.jsonl"]) == 10
    decisions = data["decision-points.jsonl"]
    assert len(decisions) >= 55 and all(row["default"] is None and row["default_law"] == "forbidden" for row in decisions)
    libraries = data["library-contracts.jsonl"]
    assert len(libraries) == 10 and len({row["library_id"] for row in libraries}) == 10
    expected = {
        "library.telemetry.attribution_core", "library.telemetry.schema_conventions", "library.telemetry.trace_graph",
        "library.telemetry.metric_stream", "library.telemetry.log_event", "library.telemetry.profile_sample",
        "library.telemetry.propagation_context", "library.telemetry.observation_reduction",
        "library.telemetry.cross_signal_correlation", "library.telemetry.export_delivery",
    }
    assert {row["library_id"] for row in libraries} == expected
    decision_ids = {row["decision_id"] for row in decisions}
    for item in libraries:
        assert len(item["public_types"]) >= 10
        assert len(item["operations"]) == 4
        assert set(item["operation_refs"]) == {row["operation_ref"] for row in item["operations"]}
        assert set(item["decision_refs"]) <= decision_ids and item["decision_refs"]
        assert all(row["input_types"] and row["output_type"].startswith("Result<") for row in item["operations"])
    laws = " ".join(law for item in libraries for law in item["laws"]).lower()
    for phrase in ["not enterprise entity identity", "not business success", "not a business measure", "not automatically a domain event", "correlation does not imply causation", "durable storage", "unknown completion"]:
        assert phrase in laws, phrase
    profile = next(row for row in libraries if row["library_id"] == "library.telemetry.profile_sample")
    assert any("alpha" in law.lower() for law in profile["laws"])
    export = next(row for row in libraries if row["library_id"] == "library.telemetry.export_delivery")
    assert export["effect_boundary"] == "pure_effect_intents"
    compiler = data["compiler-contracts.jsonl"]
    assert len(compiler) == 30
    offers = [row for row in compiler if row["record_kind"] == "capability_offer"]
    assert len(offers) == 10 and all(row["qualified_implementation_count"] == 0 and not row["portable"] and not row["selectable"] for row in offers)
    assert len(data["negative-twins.jsonl"]) >= 14
    assert manifest["completion_claim"] is False and manifest["qualified_implementation_count"] == 0
    print(f"VALIDATION PASS telemetry signals: {len(libraries)} exact boundaries, {len(decisions)} no-default decisions, 0 qualified offers")


if __name__ == "__main__":
    main()
