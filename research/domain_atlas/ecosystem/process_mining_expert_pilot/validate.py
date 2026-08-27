#!/usr/bin/env python3
"""Independent structural, referential, constitutional, and coverage validator."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load_jsonl(name):
    records = []
    for line_no, line in enumerate((ROOT / name).read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise AssertionError(f"{name}:{line_no}: invalid JSON: {exc}") from exc
    return records


def unique(records, label):
    ids = [r["id"] for r in records]
    assert len(ids) == len(set(ids)), f"duplicate {label} ids"
    return set(ids)


def validate_schema(records, schema_name):
    try:
        import jsonschema
    except ImportError:
        return "jsonschema-not-installed; manual checks still executed"
    schema = json.loads((ROOT / "schemas" / schema_name).read_text())
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    errors = []
    for record in records:
        errors.extend(f"{record.get('id')}: {err.message}" for err in validator.iter_errors(record))
    assert not errors, "schema failures:\n" + "\n".join(errors[:30])
    return "pass"


def main():
    sources = load_jsonl("sources.jsonl")
    experts = load_jsonl("experts.jsonl")
    contributions = load_jsonl("contributions.jsonl")
    mappings = load_jsonl("canonical-mappings.jsonl")
    libraries = load_jsonl("library-boundaries.jsonl")
    reviews = load_jsonl("review-queue.jsonl")
    source_ids = unique(sources, "source")
    expert_ids = unique(experts, "expert")
    artifact_ids = unique(contributions, "artifact")
    unique(mappings, "mapping")
    unique(libraries, "library")
    review_ids = unique(reviews, "review")

    assert len(sources) >= 50, len(sources)
    assert sum(r["is_primary_evidence"] for r in sources) >= 50
    assert len(contributions) >= 80, len(contributions)
    assert len(mappings) >= 250, len(mappings)

    schema_status = {
        "sources": validate_schema(sources, "source.schema.json"),
        "experts": validate_schema(experts, "expert.schema.json"),
        "contributions": validate_schema(contributions, "contribution.schema.json"),
        "mappings": validate_schema(mappings, "mapping.schema.json"),
        "libraries": validate_schema(libraries, "library-boundary.schema.json"),
        "reviews": validate_schema(reviews, "review.schema.json"),
    }

    for record in contributions:
        assert set(record["primary_source_ids"]) <= source_ids, record["id"]
        assert record["authors_or_maintainers"] and record["bibliographic_authors"], record["id"]
        assert set(record["authors_or_maintainers"]) <= expert_ids, record["id"]
        assert {r["expert_id"] for r in record["expert_roles"]} == set(record["authors_or_maintainers"]), record["id"]
        assert len(record["problem_or_question"].strip()) >= 20, record["id"]
        assert record["formal_objects_or_types"] and record["operators"] and record["algorithms"]
        assert record["guarantees"] and record["assumptions"] and record["limitations_or_counterevidence"]
        assert record["exposed_decisions"]
    for record in experts:
        assert set(record["contribution_ids"]) <= artifact_ids, record["id"]
    for record in mappings:
        assert record["artifact_id"] in artifact_ids, record["id"]
        assert set(record["primary_source_ids"]) <= source_ids, record["id"]
        artifact_status = by_id(contributions)[record["artifact_id"]]["status"]
        if artifact_status == "excluded_ai_method":
            assert record["adjudication_status"] == "excluded_noncore_reference", record["id"]
        elif artifact_status == "reference_only_noncore":
            assert record["adjudication_status"] == "reference_only_no_binding", record["id"]
    for record in libraries:
        assert record["artifact_id"] in artifact_ids, record["id"]
        assert set(record["source_ids"]) <= source_ids, record["id"]
        assert by_id(contributions)[record["artifact_id"]]["status"] == "core_candidate", record["id"]
    for record in reviews:
        assert set(record["candidate_artifact_ids"]) <= artifact_ids, record["id"]
        assert set(record["source_ids"]) <= source_ids, record["id"]

    required_reviews = {"review.hoeg", "review.tekgm", "review.tekg_collision", "review.sa_ocel", "review.oced", "review.oced_pg", "review.expert_ownership"}
    assert required_reviews <= review_ids
    by_artifact = {r["id"]: r for r in contributions}
    assert by_artifact["art.hoeg.encoding"]["bibliographic_authors"] == ["Tim K. Smit", "Hajo A. Reijers", "Xixi Lu"]
    assert by_artifact["art.hoeg.predictor"]["status"] == "excluded_ai_method"
    assert by_artifact["art.tekg.model"]["bibliographic_authors"] == ["Shahrzad Khayatbashi", "Olaf Hartig", "Amin Jalali"]
    assert by_artifact["art.saocpm.state_semantics"]["bibliographic_authors"] == ["Dina Kretzschmann", "Alessandro Berti", "Wil M. P. van der Aalst"]
    assert DIRK_NOT_HOEG(by_artifact)

    required_distinctions = {
        "art.oced.core_metamodel", "art.oced.pg_base_ontology", "art.ocel2.metamodel",
        "art.ekg.model", "art.tekg.model", "art.hoeg.encoding", "art.saocpm.state_semantics",
    }
    assert required_distinctions <= artifact_ids
    assert len({by_artifact[r]["name"] for r in required_distinctions}) == len(required_distinctions)

    coverage_terms = {
        "process discovery": lambda r: "process_discovery" in r["bounded_context"] or "process discovery" in r["categories"],
        "conformance": lambda r: r["bounded_context"] == "conformance_checking",
        "diagnostics": lambda r: any("diagnostic" in c for c in r["categories"]),
        "performance": lambda r: "performance" in r["bounded_context"],
        "prediction": lambda r: r["bounded_context"] == "predictive_monitoring",
        "object-centric semantics": lambda r: "object-centric semantics" in r["categories"],
        "event-data standards": lambda r: r["bounded_context"] in {"event_data_standardization", "event_log_exchange"},
        "behavioral models": lambda r: r["bounded_context"] == "behavioral_model",
        "tooling": lambda r: r["artifact_kind"] in {"tool", "tool_platform", "library"},
    }
    missing = [name for name, pred in coverage_terms.items() if not any(pred(r) for r in contributions)]
    assert not missing, f"missing required analysis families: {missing}"

    forbidden_core = []
    for rec in contributions:
        combined = " ".join([rec["name"], *rec["categories"], *rec["algorithms"]]).lower()
        if any(term in combined for term in ["large language model", " llm", "graph neural network", "heterogeneous gnn"]):
            if rec["status"] == "core_candidate":
                forbidden_core.append(rec["id"])
    assert not forbidden_core, f"AI methods leaked into core: {forbidden_core}"

    manifest = json.loads((ROOT / "manifest.json").read_text())
    outputs = ["sources.jsonl", "experts.jsonl", "contributions.jsonl", "canonical-mappings.jsonl", "library-boundaries.jsonl", "review-queue.jsonl", "coverage-gaps.json"]
    digest = hashlib.sha256("".join((ROOT / name).read_text() for name in outputs).encode()).hexdigest()
    assert digest == manifest["content_sha256"], "manifest content digest mismatch; rebuild corpus"
    expected_counts = {
        "sources": len(sources), "primary_sources": sum(r["is_primary_evidence"] for r in sources),
        "experts": len(experts), "contributions": len(contributions), "canonical_mappings": len(mappings),
        "library_boundaries": len(libraries), "review_items": len(reviews),
    }
    assert expected_counts == manifest["record_counts"]
    result = {
        "status": "PASS",
        "counts": expected_counts,
        "mapping_kinds": dict(sorted(Counter(r["mapping_kind"] for r in mappings).items())),
        "schema": schema_status,
        "constitutional_negative_twin": "HOEG attribution mismatch caught",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


def DIRK_NOT_HOEG(by_artifact):
    """Named so a failing negative twin is obvious in validator output."""
    return "expert.dirk_fahland" not in by_artifact["art.hoeg.encoding"]["authors_or_maintainers"]


def by_id(records):
    return {record["id"]: record for record in records}


if __name__ == "__main__":
    try:
        main()
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise
