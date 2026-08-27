#!/usr/bin/env python3
"""Validate schema, references, minimum evidence, and finance-specific coverage gates."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

try:
    import jsonschema
except ImportError as exc:  # pragma: no cover - invocation documents dependency
    raise SystemExit("jsonschema is required; run: uv run --with jsonschema validate_pack.py") from exc


ROOT = Path(__file__).resolve().parent
SCHEMA = ROOT.parent / "schema" / "industry-research-record.schema.json"
FILES = {
    "analytical_case": ROOT / "analytics-cases.jsonl",
    "source_evidence": ROOT / "sources.jsonl",
    "source_system_need": ROOT / "source-systems.jsonl",
    "data_shape_need": ROOT / "data-shapes.jsonl",
}


def load(path: Path) -> list[dict]:
    records = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise AssertionError(f"{path.name}:{line_no}: {exc}") from exc
    return records


def main() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    records_by_kind = {kind: load(path) for kind, path in FILES.items()}
    all_records = [record for records in records_by_kind.values() for record in records]

    seen: dict[str, str] = {}
    for record in all_records:
        jsonschema.validate(record, schema)
        rid = record["record_id"]
        if rid in seen:
            raise AssertionError(f"duplicate record id {rid} in {seen[rid]} and {record['record_kind']}")
        seen[rid] = record["record_kind"]

    cases = records_by_kind["analytical_case"]
    sources = records_by_kind["source_evidence"]
    systems = records_by_kind["source_system_need"]
    shapes = records_by_kind["data_shape_need"]
    source_ids = {s["record_id"] for s in sources}
    system_ids = {s["record_id"] for s in systems}
    shape_ids = {s["record_id"] for s in shapes}

    assert len(sources) >= 25, f"only {len(sources)} sources"
    assert len({s["publisher"] for s in sources}) >= 20, "insufficient publisher diversity"
    assert sum(s["source_kind"] in {"standard", "regulator", "official_statistics", "official_implementation"} for s in sources) >= 50
    assert len(cases) >= 250, f"only {len(cases)} analytical cases"
    assert len(systems) >= 35
    assert len(shapes) >= 35

    allowed_modes = {
        "descriptive", "diagnostic", "root_cause_analysis", "anomaly_detection", "predictive",
        "forecasting", "causal_inference", "experimental", "process_mining", "conformance_checking",
        "bottleneck_analysis", "optimization", "simulation", "stress_testing", "surveillance",
        "reconciliation", "decision_control", "valuation",
    }
    required_modes = {
        "diagnostic", "root_cause_analysis", "anomaly_detection", "predictive", "forecasting",
        "causal_inference", "experimental", "process_mining", "conformance_checking",
        "bottleneck_analysis", "optimization", "simulation", "stress_testing", "surveillance",
        "reconciliation", "decision_control", "valuation",
    }
    observed_modes: Counter[str] = Counter()
    observed_subindustries: Counter[str] = Counter()
    for case in cases:
        assert case["llm_dependency"] == "none", case["record_id"]
        assert len(case["analytical_modes"]) >= 2, case["record_id"]
        unknown = set(case["analytical_modes"]) - allowed_modes
        assert not unknown, f"{case['record_id']} unknown modes {sorted(unknown)}"
        observed_modes.update(case["analytical_modes"])
        observed_subindustries.update(case["subindustry_ids"])
        assert case["evidence_refs"], case["record_id"]
        assert set(case["evidence_refs"]) <= source_ids, (case["record_id"], set(case["evidence_refs"]) - source_ids)
        assert set(case["source_system_refs"]) <= system_ids, (case["record_id"], set(case["source_system_refs"]) - system_ids)
        assert set(case["data_shape_refs"]) <= shape_ids, (case["record_id"], set(case["data_shape_refs"]) - shape_ids)
        assert case["sovereign_question"].endswith("?"), case["record_id"]
        assert not case["name"].lower().endswith(" kpi"), case["record_id"]

    assert required_modes <= set(observed_modes), sorted(required_modes - set(observed_modes))
    required_prefixes = {
        "banking.", "payments.", "lending.", "capitalmarkets.", "assetmanagement.", "wealth.",
        "insurance.", "fintech.", "marketinfrastructure.", "compliance.",
    }
    missing_prefixes = [prefix for prefix in required_prefixes if not any(s.startswith(prefix) for s in observed_subindustries)]
    assert not missing_prefixes, f"missing subindustry prefixes {missing_prefixes}"

    for system in systems:
        assert set(system["evidence_refs"]) <= source_ids, (system["record_id"], set(system["evidence_refs"]) - source_ids)
    for shape in shapes:
        assert set(shape["evidence_refs"]) <= source_ids, (shape["record_id"], set(shape["evidence_refs"]) - source_ids)

    ccr_cases = [c for c in cases if c["record_id"].startswith("fin.case.ccr.")]
    assert len(ccr_cases) >= 20, f"only {len(ccr_cases)} CCR cases"
    ccr_text = json.dumps(ccr_cases).lower()
    required_ccr_terms = [
        "connected", "netting set", "collateral", "margin", "current exposure", "pfe", "ead",
        "cva", "wrong-way", "concentration", "largest-counterparty default", "intraday", "limit",
        "close-out", "legal enforceability",
    ]
    missing_ccr = [term for term in required_ccr_terms if term not in ccr_text]
    assert not missing_ccr, f"missing CCR terms {missing_ccr}"

    print("PASS finance/insurance industry pack")
    print(f"  {len(sources)} evidence sources from {len({s['publisher'] for s in sources})} publishers")
    print(f"  {len(systems)} source-system capability needs")
    print(f"  {len(shapes)} data-shape needs")
    print(f"  {len(cases)} analytical cases across {len(observed_subindustries)} subindustry labels")
    print(f"  {len(ccr_cases)} explicit counterparty-credit-risk cases")
    print("  modes " + ", ".join(f"{name}={count}" for name, count in sorted(observed_modes.items())))


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, jsonschema.ValidationError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
