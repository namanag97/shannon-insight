#!/usr/bin/env python3
"""Validate the manufacturing research pack and its internal references."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker


HERE = Path(__file__).resolve().parent
SCHEMA = HERE.parent / "schema" / "industry-research-record.schema.json"


def read_jsonl(name: str) -> list[dict]:
    path = HERE / name
    records: list[dict] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            record = json.loads(raw)
        except json.JSONDecodeError as error:
            raise AssertionError(f"{name}:{line_number}: invalid JSON: {error}") from error
        assert isinstance(record, dict), f"{name}:{line_number}: expected an object"
        records.append(record)
    return records


def check_schema(name: str, records: list[dict], validator: Draft202012Validator) -> None:
    for line_number, record in enumerate(records, 1):
        errors = sorted(validator.iter_errors(record), key=lambda item: list(item.path))
        if errors:
            details = "; ".join(error.message for error in errors[:4])
            raise AssertionError(f"{name}:{line_number}:{record.get('record_id')}: {details}")


def check_refs(label: str, record_id: str, refs: list[str], known: set[str]) -> None:
    missing = sorted(set(refs) - known)
    assert not missing, f"{label}:{record_id}: missing references {missing}"


def main() -> None:
    sources = read_jsonl("sources.jsonl")
    cases = read_jsonl("analytics-cases.jsonl")
    systems = read_jsonl("source-systems.jsonl")
    shapes = read_jsonl("data-shapes.jsonl")
    subindustries = read_jsonl("subindustries.jsonl")

    assert len(sources) >= 25, "at least 25 authoritative sources are required"
    assert len(cases) >= 100, "at least 100 situated analytical cases are required"
    assert len(systems) >= 30, "at least 30 source-system needs are required"
    assert len(shapes) >= 30, "at least 30 data-shape needs are required"
    assert len(subindustries) >= 35, "at least 35 manufacturing contexts are required"

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for name, records, expected_kind in (
        ("sources.jsonl", sources, "source_evidence"),
        ("analytics-cases.jsonl", cases, "analytical_case"),
        ("source-systems.jsonl", systems, "source_system_need"),
        ("data-shapes.jsonl", shapes, "data_shape_need"),
    ):
        assert all(record.get("record_kind") == expected_kind for record in records), name
        check_schema(name, records, validator)

    all_records = sources + cases + systems + shapes
    ids = [record["record_id"] for record in all_records]
    duplicates = sorted(record_id for record_id, count in Counter(ids).items() if count > 1)
    assert not duplicates, f"duplicate record ids: {duplicates}"

    source_ids = {record["record_id"] for record in sources}
    case_ids = {record["record_id"] for record in cases}
    system_ids = {record["record_id"] for record in systems}
    shape_ids = {record["record_id"] for record in shapes}
    subindustry_ids = {record["subindustry_id"] for record in subindustries}
    assert len(subindustry_ids) == len(subindustries), "duplicate subindustry ids"

    for source in sources:
        parsed = urlparse(source["url"])
        assert source["status"] == "verified", f"unverified source: {source['record_id']}"
        assert parsed.scheme == "https" and parsed.netloc, f"non-HTTPS source: {source['record_id']}"
        assert source["source_kind"] != "academic", (
            f"source pack promises primary/official evidence; isolate academic source {source['record_id']}"
        )

    for subindustry in subindustries:
        assert set(subindustry) == {
            "subindustry_id",
            "name",
            "operating_modes",
            "representative_processes",
            "distinguishing_analytics",
            "source_refs",
        }, f"unexpected subindustry registry shape: {subindustry.get('subindustry_id')}"
        check_refs("subindustry.evidence", subindustry["subindustry_id"], subindustry["source_refs"], source_ids)

    for case in cases:
        check_refs("case.system", case["record_id"], case["source_system_refs"], system_ids)
        check_refs("case.shape", case["record_id"], case["data_shape_refs"], shape_ids)
        check_refs("case.evidence", case["record_id"], case["evidence_refs"], source_ids)
        check_refs("case.subindustry", case["record_id"], case["subindustry_ids"], subindustry_ids)
        assert case["industry_id"] == "ind.manufacturing", case["record_id"]
        assert case["llm_dependency"] == "none", case["record_id"]
        assert len(case["method_refs"]) >= 2, f"method family too thin: {case['record_id']}"
        assert len(case["operation_refs"]) >= 2, f"operation chain too thin: {case['record_id']}"
        assert case["sovereign_question"].rstrip().endswith("?"), case["record_id"]

    for system in systems:
        check_refs("system.evidence", system["record_id"], system["evidence_refs"], source_ids)
        check_refs("system.subindustry", system["record_id"], system["subindustry_ids"], subindustry_ids)
    for shape in shapes:
        check_refs("shape.evidence", shape["record_id"], shape["evidence_refs"], source_ids)
        check_refs("shape.subindustry", shape["record_id"], shape["subindustry_ids"], subindustry_ids)

    represented = {item for case in cases for item in case["subindustry_ids"]}
    uncovered = sorted(subindustry_ids - represented)
    assert not uncovered, f"subindustries without an explicit case: {uncovered}"

    required_modes = {
        "diagnostic",
        "root_cause",
        "statistical_process_control",
        "constraint_analysis",
        "predictive",
        "optimization",
        "simulation",
        "conformance",
        "safety",
        "environmental",
        "process_control",
        "reliability",
    }
    modes = {mode for case in cases for mode in case["analytical_modes"]}
    assert not required_modes - modes, f"missing required modes: {sorted(required_modes - modes)}"

    pack_text = "\n".join((HERE / name).read_text(encoding="utf-8") for name in (
        "sources.jsonl",
        "analytics-cases.jsonl",
        "source-systems.jsonl",
        "data-shapes.jsonl",
        "subindustries.jsonl",
    ))
    forbidden_token = "C" + "C" + "R"
    assert forbidden_token not in pack_text, "banking risk acronym leaked into manufacturing records"

    publishers = {source["publisher"] for source in sources}
    print(
        json.dumps(
            {
                "analytical_cases": len(case_ids),
                "analytical_modes": len(modes),
                "data_shapes": len(shape_ids),
                "evidence_publishers": len(publishers),
                "source_system_needs": len(system_ids),
                "sources": len(source_ids),
                "subindustries": len(subindustry_ids),
                "validation": "passed",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
