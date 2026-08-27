#!/usr/bin/env python3
"""Validate the commerce/services JSONL research pack without external packages."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ID = re.compile(r"^[a-z][a-z0-9]*(\.[a-z][a-z0-9_-]*)+$")
FILES = {
    "sources.jsonl": "source_evidence",
    "source-systems.jsonl": "source_system_need",
    "data-shapes.jsonl": "data_shape_need",
    "analytics-cases.jsonl": "analytical_case",
}
REQUIRED = {
    "source_evidence": {"record_id", "record_kind", "edition", "status", "title", "publisher", "source_kind", "url", "supports", "authority_scope", "limitations", "accessed_at"},
    "source_system_need": {"record_id", "record_kind", "edition", "status", "industry_id", "subindustry_ids", "source_class", "objects", "read_change_modes", "time_order_finality", "schema_semantics", "authority", "hazards", "evidence_refs"},
    "data_shape_need": {"record_id", "record_kind", "edition", "status", "industry_id", "subindustry_ids", "name", "modalities", "grain", "keys", "time_roles", "change_semantics", "uncertainty", "quality_provenance", "relationships", "evidence_refs"},
    "analytical_case": {"record_id", "record_kind", "edition", "status", "industry_id", "subindustry_ids", "name", "analytical_modes", "sovereign_question", "decision_or_action", "actors", "unit_of_analysis", "population", "grain", "time_model", "source_system_refs", "data_shape_refs", "method_refs", "operation_refs", "inputs", "outputs", "assumptions", "invariants", "failure_modes", "evidence_refs", "llm_dependency", "limitations"},
}
MANDATORY_MODES = {
    "operational", "diagnostic", "root_cause", "process", "bottleneck", "causal",
    "experimental", "forecasting", "anomaly", "optimization", "simulation", "pricing",
    "recommendation", "segmentation", "survival", "reliability", "spatial", "risk",
    "fraud", "text", "vision", "llm_optional",
}


def load_jsonl(name):
    rows = []
    with (ROOT / name).open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise AssertionError(f"{name}:{number}: invalid JSON: {error}") from error
    return rows


def assert_string_array(record_id, field, value):
    assert isinstance(value, list) and value, f"{record_id}: {field} must be a non-empty array"
    assert all(isinstance(item, str) and item for item in value), f"{record_id}: {field} contains non-string/empty item"
    assert len(value) == len(set(value)), f"{record_id}: {field} contains duplicates"


def main():
    by_file = {name: load_jsonl(name) for name in FILES}
    all_rows = [row for rows in by_file.values() for row in rows]
    ids = [row.get("record_id") for row in all_rows]
    assert len(ids) == len(set(ids)), "duplicate record_id across pack"

    for name, kind in FILES.items():
        for row in by_file[name]:
            rid = row.get("record_id")
            assert isinstance(rid, str) and ID.fullmatch(rid), f"{name}: invalid record_id {rid!r}"
            assert row.get("record_kind") == kind, f"{rid}: wrong record_kind"
            missing = REQUIRED[kind] - row.keys()
            assert not missing, f"{rid}: missing {sorted(missing)}"
            assert row.get("edition") == 1, f"{rid}: unexpected edition"
            for field, value in row.items():
                if isinstance(value, list):
                    assert_string_array(rid, field, value)

    sources = {row["record_id"]: row for row in by_file["sources.jsonl"]}
    systems = {row["record_id"]: row for row in by_file["source-systems.jsonl"]}
    shapes = {row["record_id"]: row for row in by_file["data-shapes.jsonl"]}
    cases = by_file["analytics-cases.jsonl"]

    assert len(sources) >= 25, f"only {len(sources)} evidence sources"
    assert all(row["status"] == "verified" for row in sources.values()), "unverified source in verified pack"
    assert all(row["url"].startswith("https://") for row in sources.values()), "non-HTTPS source URL"

    for row in list(systems.values()) + list(shapes.values()) + cases:
        unknown = set(row["evidence_refs"]) - sources.keys()
        assert not unknown, f"{row['record_id']}: unknown evidence refs {sorted(unknown)}"

    mode_counts = Counter()
    subindustry_counts = Counter()
    referenced_systems = Counter()
    referenced_shapes = Counter()
    for row in cases:
        unknown_systems = set(row["source_system_refs"]) - systems.keys()
        unknown_shapes = set(row["data_shape_refs"]) - shapes.keys()
        assert not unknown_systems, f"{row['record_id']}: unknown systems {sorted(unknown_systems)}"
        assert not unknown_shapes, f"{row['record_id']}: unknown shapes {sorted(unknown_shapes)}"
        assert row["sovereign_question"].rstrip().endswith("?"), f"{row['record_id']}: sovereign question is not interrogative"
        assert len(row["decision_or_action"]) >= 30, f"{row['record_id']}: decision/action too weak"
        assert len(row["failure_modes"]) >= 4, f"{row['record_id']}: insufficient failure modes"
        assert len(row["invariants"]) >= 3, f"{row['record_id']}: insufficient invariants"
        mode_counts.update(row["analytical_modes"])
        subindustry_counts.update(row["subindustry_ids"])
        referenced_systems.update(row["source_system_refs"])
        referenced_shapes.update(row["data_shape_refs"])
        if row["llm_dependency"] == "quarantined_optional":
            assert "commerce.system.llm_gateway" in row["source_system_refs"], f"{row['record_id']}: LLM not gateway-quarantined"
            assert "commerce.shape.llm_inference_receipt" in row["data_shape_refs"], f"{row['record_id']}: missing LLM receipt"
        else:
            assert row["llm_dependency"] == "none", f"{row['record_id']}: invalid LLM dependency"

    missing_modes = MANDATORY_MODES - mode_counts.keys()
    assert not missing_modes, f"missing analytical modes {sorted(missing_modes)}"
    assert min(subindustry_counts.values()) >= 20, f"thin subindustry coverage: {subindustry_counts}"
    assert not (systems.keys() - referenced_systems.keys()), f"unreferenced source systems: {sorted(systems.keys() - referenced_systems.keys())}"
    assert not (shapes.keys() - referenced_shapes.keys()), f"unreferenced data shapes: {sorted(shapes.keys() - referenced_shapes.keys())}"

    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    expected = {name: len(rows) for name, rows in by_file.items()}
    assert manifest["record_counts"] == expected, "manifest record counts are stale"

    print("PASS commerce/services industry research pack")
    print(f"  {len(cases)} analytical cases")
    print(f"  {len(systems)} source-system needs")
    print(f"  {len(shapes)} data-shape needs")
    print(f"  {len(sources)} authoritative sources")
    print(f"  {len(subindustry_counts)} subindustries; minimum {min(subindustry_counts.values())} cases each")
    print(f"  {len(mode_counts)} analytical modes; {mode_counts['root_cause']} RCA, {mode_counts['bottleneck']} bottleneck, {mode_counts['experimental']} experimental")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as error:
        print(f"FAIL {error}", file=sys.stderr)
        raise SystemExit(1)
