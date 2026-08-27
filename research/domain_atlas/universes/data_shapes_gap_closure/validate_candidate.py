#!/usr/bin/env python3
"""Deterministic semantic and referential validator for the candidate bundle."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load(name: str) -> list[dict]:
    path = HERE / name
    records = []
    for number, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise AssertionError(f"{name}:{number}: invalid JSON: {exc}") from exc
    return records


def unique(records: list[dict], key: str, name: str) -> set[str]:
    values = [record.get(key) for record in records]
    assert all(isinstance(value, str) and value for value in values), f"{name}: missing {key}"
    assert len(values) == len(set(values)), f"{name}: duplicate {key}"
    return set(values)


def validate_against_schema(filename: str, schema_filename: str, records: list[dict]) -> None:
    """Dependency-free enforcement of this corpus's generated structural schema contract."""
    schema = json.loads((HERE / "schemas" / schema_filename).read_text())
    required = set(schema["required"])
    allowed_types = {"string": str, "array": list, "object": dict, "boolean": bool, "null": type(None)}
    for line_number, record in enumerate(records, 1):
        assert required <= set(record), f"{filename}:{line_number}: schema-required fields missing"
        for field, rule in schema["properties"].items():
            if field not in record or "type" not in rule:
                continue
            names = rule["type"] if isinstance(rule["type"], list) else [rule["type"]]
            assert any(isinstance(record[field], allowed_types[name]) for name in names), f"{filename}:{line_number}: schema type mismatch for {field}"


def main() -> None:
    if "--no-build" not in sys.argv:
        subprocess.run([sys.executable, str(HERE / "build_candidate.py")], check=True)

    sources = load("sources.jsonl")
    contexts = load("context-candidates.jsonl")
    constructs = load("shape-type-candidates.jsonl")
    operations = load("operation-totality.jsonl")
    inferences = load("invalid-inferences.jsonl")
    adjudications = load("canonical-adjudications.jsonl")
    crosswalks = load("representation-crosswalks.jsonl")
    requirements = load("compiler-requirements.jsonl")
    libraries = load("library-boundaries.jsonl")
    qualifications = load("provider-qualifications.jsonl")
    innovations = load("innovations-2021-2026.jsonl")
    gaps = load("gaps.jsonl")

    for filename, schema_filename, records in [
        ("sources.jsonl", "source.schema.json", sources),
        ("context-candidates.jsonl", "context.schema.json", contexts),
        ("shape-type-candidates.jsonl", "construct.schema.json", constructs),
        ("operation-totality.jsonl", "operation.schema.json", operations),
        ("representation-crosswalks.jsonl", "crosswalk.schema.json", crosswalks),
        ("library-boundaries.jsonl", "compiler-library.schema.json", libraries),
    ]:
        validate_against_schema(filename, schema_filename, records)

    source_ids = unique(sources, "source_id", "sources")
    context_ids = unique(contexts, "context_id", "contexts")
    construct_ids = unique(constructs, "construct_id", "constructs")
    unique(operations, "operation_cell_id", "operations")
    unique(inferences, "inference_id", "inferences")
    unique(adjudications, "adjudication_id", "adjudications")
    unique(crosswalks, "crosswalk_id", "crosswalks")
    unique(requirements, "requirement_id", "requirements")
    unique(libraries, "library_id", "libraries")
    unique(qualifications, "qualification_id", "qualifications")
    unique(innovations, "innovation_id", "innovations")
    unique(gaps, "gap_id", "gaps")

    assert len(sources) >= 90, "fewer than 90 primary standards/specifications"
    assert len(contexts) >= 30, "fewer than 30 bounded-context candidates"
    assert len(constructs) + len(crosswalks) >= 100, "fewer than 100 shape/type/crosswalk records"
    assert len(libraries) >= 25, "fewer than 25 library boundaries"
    assert len(qualifications) >= 25, "fewer than 25 provider/library qualification requirements"
    assert len(innovations) >= 20, "fewer than 20 innovation signals"
    assert all(2021 <= int(i["year"]) <= 2026 for i in innovations)
    assert all(i.get("non_llm") is True for i in innovations), "AI/LLM signal leaked into non-LLM innovation corpus"

    primary_authorities = {"normative", "authoritative_primary", "normative_or_primary_official"}
    assert sum(s.get("authority") in primary_authorities for s in sources) >= 90
    assert all(str(s.get("url", "")).startswith("https://") for s in sources)

    for collection_name, collection in [
        ("contexts", contexts), ("constructs", constructs), ("operations", operations),
        ("inferences", inferences), ("adjudications", adjudications),
        ("crosswalks", crosswalks), ("requirements", requirements),
        ("libraries", libraries), ("qualifications", qualifications), ("innovations", innovations),
    ]:
        for record in collection:
            unknown = set(record.get("evidence_refs", [])) - source_ids
            assert not unknown, f"{collection_name}: unknown evidence refs {sorted(unknown)}"

    required_construct_fields = {
        "carrier_or_binding", "logical_shape", "semantic_qualifiers", "identity_semantics",
        "time_semantics", "order_semantics", "topology_semantics", "change_semantics",
        "uncertainty_semantics", "security_semantics",
    }
    for record in constructs:
        assert record["owner_context"] in context_ids
        assert required_construct_fields <= set(record), f"construct missing semantic axes: {record['construct_id']}"
        assert record.get("status") == "candidate_not_canonical"

    for record in operations:
        assert record["owner_context"] in context_ids
        assert set(record.get("input_constructs", [])) <= construct_ids
        assert record.get("totality") in {"partial", "conditional_total", "total", "provider_dependent"}
        assert len(record.get("refusal_codes", [])) >= 3

    for record in adjudications:
        assert record["candidate_id"] in construct_ids
        assert record["name_equivalence_used"] is False
        assert record["automatic_merge_allowed"] is False
        assert record["status"] == "open_manual_adjudication"

    for record in crosswalks:
        assert record["target_construct_id"] in construct_ids
        assert record["round_trip"] in {"conditional", "partial", "lossless", "lossy", "none"}
        assert record["not_preserved_or_not_proven"], f"crosswalk lacks non-preservation declaration: {record['crosswalk_id']}"
        assert record["status"] == "candidate_unqualified_until_conformance_fixtures"

    exact_terms = {"GeoParquet", "FITS", "OpenEXR", "glTF", "IFC", "STEP AP242", "CMS", "COSE", "VCF", "FHIR", "ISO 20022", "FIX"}
    names = " ".join(c["source_representation"] for c in crosswalks)
    missing_terms = {term for term in exact_terms if term not in names}
    assert not missing_terms, f"required exact representation crosswalks missing: {sorted(missing_terms)}"

    for record in qualifications:
        assert record["status"] == "unexecuted_requirement"
        assert "provider" in record["subject_kind"]
        assert len(record["required_fixtures"]) >= 6

    forbidden = ["unstructured data type", "format proves semantics", "provider name proves support"]
    corpus = " ".join((HERE / name).read_text().lower() for name in [
        "shape-type-candidates.jsonl", "representation-crosswalks.jsonl", "compiler-requirements.jsonl"
    ])
    assert not any(term in corpus for term in forbidden)

    report = json.loads((HERE / "coverage-report.json").read_text())
    assert report["status"] == "candidate_gap_closure_not_completeness_claim"
    assert json.loads((HERE / "manifest.json").read_text())["completeness_claim"] is False

    print(
        "PASS data-shape gap closure candidate: "
        f"{len(sources)} sources, {len(contexts)} contexts, {len(constructs)} constructs, "
        f"{len(operations)} operation cells, {len(crosswalks)} crosswalks, "
        f"{len(libraries)} libraries, {len(qualifications)} unexecuted qualifications, "
        f"{len(innovations)} innovations, {len(gaps)} open gaps"
    )


if __name__ == "__main__":
    main()
