#!/usr/bin/env python3
"""Structural, reference-integrity and coverage checks for this research pack."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ModuleNotFoundError:  # Keep the pack verifiable in an offline stdlib-only workspace.
    Draft202012Validator = None
    FormatChecker = None


ROOT = Path(__file__).resolve().parent
SCHEMA = ROOT.parent / "schema" / "industry-research-record.schema.json"


def load_jsonl(name: str) -> list[dict]:
    rows = []
    for line_no, text in enumerate((ROOT / name).read_text(encoding="utf-8").splitlines(), 1):
        try:
            rows.append(json.loads(text))
        except json.JSONDecodeError as exc:
            raise AssertionError(f"{name}:{line_no}: {exc}") from exc
    return rows


def validate_shared_contract_stdlib(rows: list[dict], schema: dict) -> list[str]:
    """Validate the shared contract subset used by the records without third-party packages."""
    def_names = {
        "analytical_case": "analyticalCase", "source_evidence": "sourceEvidence",
        "source_system_need": "sourceSystemNeed", "data_shape_need": "dataShapeNeed",
    }
    errors: list[str] = []
    id_pattern = re.compile(schema["$defs"]["id"]["pattern"])
    for row in rows:
        record_id = row.get("record_id", "<missing>")
        definition = schema["$defs"].get(def_names.get(row.get("record_kind"), ""))
        if definition is None:
            errors.append(f"{record_id}: unknown record_kind {row.get('record_kind')!r}")
            continue
        for required in definition["required"]:
            if required not in row:
                errors.append(f"{record_id}: missing required field {required}")
        for key, prop in definition.get("properties", {}).items():
            if key not in row:
                continue
            value = row[key]
            if "$ref" in prop:
                target = prop["$ref"].rsplit("/", 1)[-1]
                if target == "id" and (not isinstance(value, str) or not id_pattern.fullmatch(value)):
                    errors.append(f"{record_id}: {key} is not a valid id")
                if target == "strings" and (not isinstance(value, list) or any(not isinstance(x, str) for x in value) or len(value) != len(set(value))):
                    errors.append(f"{record_id}: {key} must be a unique string array")
            if "const" in prop and value != prop["const"]:
                errors.append(f"{record_id}: {key} must equal {prop['const']!r}")
            if "enum" in prop and value not in prop["enum"]:
                errors.append(f"{record_id}: {key} not in {prop['enum']}")
            if prop.get("type") == "integer" and (not isinstance(value, int) or value < prop.get("minimum", value)):
                errors.append(f"{record_id}: {key} must be an integer in range")
            if prop.get("type") == "string" and (not isinstance(value, str) or len(value) < prop.get("minLength", 0)):
                errors.append(f"{record_id}: {key} must be a nonempty string")
    return errors


def main() -> None:
    sources = load_jsonl("sources.jsonl")
    systems = load_jsonl("source-systems.jsonl")
    shapes = load_jsonl("data-shapes.jsonl")
    cases = load_jsonl("analytics-cases.jsonl")
    all_rows = sources + systems + shapes + cases

    schema = json.loads(SCHEMA.read_text())
    errors = []
    if Draft202012Validator is not None:
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        for row in all_rows:
            for error in validator.iter_errors(row):
                errors.append(f"{row.get('record_id')}: {error.message}")
    else:
        errors.extend(validate_shared_contract_stdlib(all_rows, schema))
    assert not errors, "Schema errors:\n" + "\n".join(errors[:30])

    ids = [row["record_id"] for row in all_rows]
    duplicates = [record_id for record_id, count in Counter(ids).items() if count > 1]
    assert not duplicates, f"duplicate record ids: {duplicates}"

    evidence_ids = {row["record_id"] for row in sources}
    system_ids = {row["record_id"] for row in systems}
    shape_ids = {row["record_id"] for row in shapes}
    for row in systems + shapes + cases:
        missing = set(row["evidence_refs"]) - evidence_ids
        assert not missing, f"{row['record_id']} unknown evidence refs: {sorted(missing)}"
    for row in cases:
        missing_systems = set(row["source_system_refs"]) - system_ids
        missing_shapes = set(row["data_shape_refs"]) - shape_ids
        assert not missing_systems, f"{row['record_id']} unknown source refs: {sorted(missing_systems)}"
        assert not missing_shapes, f"{row['record_id']} unknown shape refs: {sorted(missing_shapes)}"
        assert row["llm_dependency"] == "none", f"{row['record_id']} violates non-LLM core"
        assert len(row["analytical_modes"]) >= 2, f"{row['record_id']} is under-decomposed"

    assert len(sources) >= 25, "family must have at least 25 authoritative sources"
    assert len(cases) >= 100, "broad family pack must encode at least 100 decision cases"
    assert all(row["status"] == "verified" and row["verification"]["primary_source"] for row in sources)
    assert all(row["url"].startswith("https://") for row in sources)
    assert len({row["publisher"] for row in sources}) >= 12, "source authority diversity too low"

    expected_subindustries = {
        "health.provider.acute", "health.provider.ambulatory", "health.provider.emergency",
        "health.provider.behavioral", "health.provider.postacute", "health.provider.dental",
        "health.payer.commercial", "health.payer.public", "health.payer.value_based",
        "health.pharmacy.retail", "health.pharmacy.pbm", "health.public_health",
        "health.life_science.pharma_rd", "health.life_science.biotech", "health.life_science.trials",
        "health.life_science.manufacturing", "health.medtech", "health.diagnostics",
        "health.genomics", "health.blood_transplant", "health.digital",
    }
    represented = {sub for row in cases for sub in row["subindustry_ids"]}
    assert expected_subindustries <= represented, f"unrepresented subindustries: {sorted(expected_subindustries - represented)}"

    required_modes = {
        "descriptive", "diagnostic", "root_cause_analysis", "cause_contribution_ranking",
        "process_conformance", "bottleneck_analysis", "queuing_analysis", "forecasting",
        "nowcasting", "anomaly_detection", "change_point_detection", "causal_inference",
        "survival_analysis", "prediction", "optimization", "simulation",
        "statistical_process_control", "reliability_analysis", "safety_signal_detection",
        "network_analysis", "geospatial_analysis", "decision_analysis", "economic_evaluation",
        "reconciliation", "audit", "data_quality_assessment", "experimental_design", "dose_response",
    }
    represented_modes = {mode for row in cases for mode in row["analytical_modes"]}
    assert required_modes <= represented_modes, f"unrepresented modes: {sorted(required_modes - represented_modes)}"

    used_systems = {ref for row in cases for ref in row["source_system_refs"]}
    used_shapes = {ref for row in cases for ref in row["data_shape_refs"]}
    assert used_systems == system_ids, f"unused source systems: {sorted(system_ids - used_systems)}"
    assert used_shapes == shape_ids, f"unused data shapes: {sorted(shape_ids - used_shapes)}"

    manifest = json.loads((ROOT / "pack-manifest.json").read_text())
    expected_counts = {
        "subindustries": len(expected_subindustries), "sources": len(sources),
        "source_systems": len(systems), "data_shapes": len(shapes), "analytical_cases": len(cases),
    }
    assert manifest["counts"] == expected_counts, "manifest counts are stale"
    gaps = json.loads((ROOT / "coverage-gaps.json").read_text())
    assert len(gaps["known_gaps"]) >= 8 and gaps["status"] == "open_research"

    print("PASS health/life-sciences pack")
    print(json.dumps({**expected_counts, "analytical_modes": len(represented_modes), "publishers": len({s['publisher'] for s in sources}), "gaps": len(gaps['known_gaps'])}, sort_keys=True))


if __name__ == "__main__":
    main()
