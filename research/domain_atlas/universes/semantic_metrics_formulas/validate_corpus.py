#!/usr/bin/env python3
"""Validate semantic metrics/formulas corpus structure, references and boundary laws."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent
BUILD_PATH = ROOT / "build_corpus.py"


def fail(message: str) -> None:
    raise AssertionError(message)


def load_builder() -> Any:
    spec = importlib.util.spec_from_file_location("semantic_metrics_formulas_builder", BUILD_PATH)
    if spec is None or spec.loader is None:
        fail("unable to load deterministic builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"invalid JSON {path}: {error}")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    text = path.read_text(encoding="utf-8")
    if text and not text.endswith("\n"):
        fail(f"JSONL must end with newline: {path.name}")
    for line_number, line in enumerate(text.splitlines(), 1):
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            fail(f"invalid JSONL {path.name}:{line_number}: {error}")
        if not isinstance(row, dict):
            fail(f"JSONL row must be an object: {path.name}:{line_number}")
        rows.append(row)
    return rows


def validate_schema_shape(schema: dict[str, Any], path: Path) -> None:
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        fail(f"unexpected schema dialect: {path.name}")
    if schema.get("type") != "object" or not isinstance(schema.get("required"), list):
        fail(f"schema missing object/required contract: {path.name}")
    properties = schema.get("properties", {})
    for field in schema["required"]:
        if field not in properties:
            fail(f"required field {field!r} has no property schema in {path.name}")


def validate_rows_against_required(rows: Iterable[dict[str, Any]], schema: dict[str, Any], filename: str) -> None:
    required = schema["required"]
    for index, row in enumerate(rows, 1):
        missing = [field for field in required if field not in row]
        if missing:
            fail(f"{filename}:{index} missing required fields {missing}")
        if row.get("edition", 0) < 1:
            fail(f"{filename}:{index} has non-positive edition")


def collect_key_values(value: Any, key_name: str) -> list[Any]:
    found: list[Any] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == key_name:
                found.append(child)
            found.extend(collect_key_values(child, key_name))
    elif isinstance(value, list):
        for child in value:
            found.extend(collect_key_values(child, key_name))
    return found


def assert_unique(rows: list[dict[str, Any]], id_field: str, filename: str) -> None:
    ids = [row[id_field] for row in rows]
    duplicates = sorted(item for item, count in Counter(ids).items() if count > 1)
    if duplicates:
        fail(f"duplicate IDs in {filename}: {duplicates[:5]}")


def walk_formula_calls(value: Any) -> list[str]:
    calls: list[str] = []
    if isinstance(value, dict):
        if isinstance(value.get("call"), str):
            calls.append(value["call"])
        for child in value.values():
            calls.extend(walk_formula_calls(child))
    elif isinstance(value, list):
        for child in value:
            calls.extend(walk_formula_calls(child))
    return calls


def main() -> None:
    builder = load_builder()

    # Generated output must be byte-content equivalent to the in-memory deterministic builder.
    loaded: dict[str, list[dict[str, Any]]] = {}
    for filename, expected in builder.OUTPUTS.items():
        path = ROOT / filename
        if not path.exists():
            fail(f"missing generated output {filename}")
        actual = load_jsonl(path)
        if actual != expected:
            fail(f"generated output is stale or nondeterministic: {filename}; rerun build_corpus.py")
        loaded[filename] = actual

    schemas: dict[str, dict[str, Any]] = {}
    for filename, expected in builder.SCHEMAS.items():
        path = ROOT / "schemas" / filename
        if not path.exists():
            fail(f"missing schema {filename}")
        actual = load_json(path)
        if actual != expected:
            fail(f"schema is stale or nondeterministic: {filename}")
        validate_schema_shape(actual, path)
        schemas[filename] = actual

    file_schema_ids = {
        "sources.jsonl": ("source.schema.json", "source_id"),
        "bounded-context-candidates.jsonl": ("bounded-context-candidate.schema.json", "context_id"),
        "semantic-records.jsonl": ("semantic-record.schema.json", "record_id"),
        "ubiquitous-language.jsonl": ("ubiquitous-language.schema.json", "term_id"),
        "invariants-refusals.jsonl": ("invariant-refusal.schema.json", "law_id"),
        "lifecycles.jsonl": ("lifecycle.schema.json", "lifecycle_id"),
        "compiler-mappings.jsonl": ("compiler-mapping.schema.json", "mapping_id"),
        "library-boundaries.jsonl": ("library-boundary.schema.json", "library_id"),
        "innovations-2021-2026.jsonl": ("innovation.schema.json", "innovation_id"),
        "vertical-examples.jsonl": ("vertical-example.schema.json", "example_id"),
        "gaps.jsonl": ("gap.schema.json", "gap_id"),
        "context-relations.jsonl": ("context-relation.schema.json", "relation_id"),
        "evidence.jsonl": ("evidence.schema.json", "evidence_id"),
    }
    for filename, (schema_name, id_field) in file_schema_ids.items():
        rows = loaded[filename]
        validate_rows_against_required(rows, schemas[schema_name], filename)
        assert_unique(rows, id_field, filename)

    sources = loaded["sources.jsonl"]
    contexts = loaded["bounded-context-candidates.jsonl"]
    records = loaded["semantic-records.jsonl"]
    terms = loaded["ubiquitous-language.jsonl"]
    laws = loaded["invariants-refusals.jsonl"]
    innovations = loaded["innovations-2021-2026.jsonl"]
    examples = loaded["vertical-examples.jsonl"]
    libraries = loaded["library-boundaries.jsonl"]

    if len(sources) < 60:
        fail(f"need at least 60 sources, found {len(sources)}")
    authoritative_kinds = {
        "standard", "recommendation", "candidate_recommendation", "official_spec", "official_guide",
        "official_registry", "official_methodology", "official_vocabulary", "official_standard",
        "official_docs", "official_implementation", "official_implementation_spec", "standard_catalog", "primary_paper",
    }
    authoritative_count = sum(source["source_kind"] in authoritative_kinds for source in sources)
    if authoritative_count < 60:
        fail(f"need at least 60 primary/official sources, found {authoritative_count}")
    for source in sources:
        if not source["url"].startswith("https://"):
            fail(f"non-HTTPS evidence URL: {source['source_id']}")
        if not source["supports_topics"]:
            fail(f"source has no claim scope: {source['source_id']}")

    if len(contexts) < 45:
        fail(f"need at least 45 context candidates, found {len(contexts)}")
    required_context_locals = {
        "analytical_entity", "fact_role", "event_semantics", "observation_assertion", "grain_population",
        "measure_definition", "dimension_definition", "member_code_list", "hierarchy_rollup",
        "semantic_relationship", "join_path", "fanout_safety", "formula_ast", "semantic_type_system",
        "operator_registry", "function_registry", "variable_parameter", "formula_definition", "formula_binding",
        "formula_evaluation", "partiality_missingness", "unit_quantity", "currency_valuation", "ratio_rate_index",
        "aggregation_algebra", "reaggregation", "additivity_posture", "decomposable_state", "population_cohort",
        "filter_predicate", "metric_definition", "kpi_target", "benchmark_reference", "calendar_time",
        "fiscal_period", "bitemporal_interpretation", "asof_cut", "validity_finality", "uncertainty",
        "semantic_model", "model_publication", "metric_governance", "semantic_query", "query_validation",
        "semantic_lowering", "materialization", "semantic_cache", "observation_receipt", "disclosure",
        "access_purpose", "lifecycle_version", "compatibility_migration",
    }
    context_locals = {context["context_id"].split(".")[-1] for context in contexts}
    missing_contexts = sorted(required_context_locals - context_locals)
    if missing_contexts:
        fail(f"missing horizontal semantic contexts: {missing_contexts}")
    if len(records) < 200:
        fail(f"need at least 200 semantic records, found {len(records)}")
    if len(innovations) < 20:
        fail(f"need at least 20 innovations, found {len(innovations)}")
    if len(examples) != 2:
        fail(f"need exactly two unrelated vertical examples, found {len(examples)}")

    kind_counts = Counter(record["record_kind"] for record in records)
    minimum_kinds = {
        "semantic_type": 30, "formula_ast_node": 20, "formula_operator": 15, "formula_function": 40, "aggregation": 25,
        "join_law": 20, "time_semantic": 20, "operation": 60, "decision_point": 40,
    }
    for kind, minimum in minimum_kinds.items():
        if kind_counts[kind] < minimum:
            fail(f"semantic record kind {kind} needs {minimum}, found {kind_counts[kind]}")

    source_ids = {source["source_id"] for source in sources}
    context_ids = {context["context_id"] for context in contexts}
    for filename, rows in loaded.items():
        for row in rows:
            for group in collect_key_values(row, "evidence_refs"):
                if not isinstance(group, list):
                    fail(f"evidence_refs must be list in {filename}")
                unknown = sorted(set(group) - source_ids)
                if unknown:
                    fail(f"unknown evidence refs in {filename}: {unknown}")
            for key in ("owner_context_ref", "upstream_context_ref", "downstream_context_ref"):
                for ref in collect_key_values(row, key):
                    if ref not in context_ids:
                        fail(f"unknown {key} {ref!r} in {filename}")
            for ref in collect_key_values(row, "source_ref"):
                if ref not in source_ids:
                    fail(f"unknown source_ref {ref!r} in {filename}")

    required_terms = {
        "business_term", "dimension_member", "observation", "fact", "measure", "metric", "kpi",
        "formula_definition", "formula_binding", "formula_evaluation", "null", "absent", "zero",
        "event_time", "valid_time", "recording_time", "query_time", "relationship", "join",
        "additive", "decomposable", "target", "metric_observation", "unit_conversion",
        "currency_valuation", "semantic_cache_equivalence", "governed_metric", "dashboard_tile",
    }
    present_terms = {term["term_id"].split(".")[-1] for term in terms}
    missing_terms = sorted(required_terms - present_terms)
    if missing_terms:
        fail(f"missing required ubiquitous-language distinctions: {missing_terms}")
    for term in terms:
        if not term["distinguish_from"]:
            fail(f"term lacks homonym/false-twin distinctions: {term['term_id']}")

    law_kinds = Counter(law["law_kind"] for law in laws)
    for kind in ("invariant", "algebra_law", "proof_obligation", "refusal"):
        if law_kinds[kind] < 5:
            fail(f"insufficient {kind} records: {law_kinds[kind]}")
    required_law_fragments = ["fanout", "bitemporal", "uncertainty", "cache", "currency", "partiality", "reaggregation"]
    law_ids = "\n".join(law["law_id"] for law in laws)
    for fragment in required_law_fragments:
        if fragment not in law_ids:
            fail(f"missing law family {fragment}")

    function_names = {record["record_id"].split(".")[-1] for record in records if record["record_kind"] == "formula_function"}
    for example in examples:
        calls = walk_formula_calls(example["metric"]["formula_ast"])
        unknown = sorted(set(calls) - function_names)
        if unknown:
            fail(f"vertical example has unregistered formula calls: {example['example_id']} {unknown}")
        if example["engine_profile"] != "generic_semantic_metric_compiler":
            fail(f"vertical example contains a specialized engine branch: {example['example_id']}")
        if "generic" not in example["branch_independence"].lower():
            fail(f"vertical example does not state branch independence: {example['example_id']}")
    if examples[0]["vertical_label"] == examples[1]["vertical_label"]:
        fail("vertical examples are not unrelated")

    if any(not 2021 <= item["year"] <= 2026 for item in innovations):
        fail("innovation year outside 2021-2026")
    if any("candidate" not in item["status"] for item in innovations):
        fail("innovation status must remain candid about qualification")

    pure_libraries = [item for item in libraries if item["boundary_kind"] == "pure"]
    effectful_libraries = [item for item in libraries if item["boundary_kind"] == "effectful"]
    if len(pure_libraries) < 10 or len(effectful_libraries) < 5:
        fail("pure/effectful library boundaries are underrepresented")
    for item in pure_libraries:
        forbidden = " ".join(item["forbidden_dependencies"])
        if not any(token in forbidden for token in ("registry", "clock", "network", "storage", "access", "store", "lookup", "execution", "provider")):
            fail(f"pure boundary does not exclude an effect channel: {item['library_id']}")

    banned_semantic_tokens = re.compile(r"\b(llm|rag|prompt|agent_memory|generative_model)\b", re.IGNORECASE)
    semantic_payload = "\n".join(
        json.dumps(row, sort_keys=True)
        for filename, rows in loaded.items()
        if filename not in {"sources.jsonl", "innovations-2021-2026.jsonl"}
        for row in rows
    )
    if banned_semantic_tokens.search(semantic_payload):
        fail("excluded language-generation semantics leaked into the meaning-layer records")

    manifest = load_json(ROOT / "manifest.json")
    report = load_json(ROOT / "coverage-report.json")
    expected_counts = {name: len(rows) for name, rows in loaded.items()}
    if manifest.get("counts") != expected_counts or report.get("counts") != expected_counts:
        fail("manifest or coverage report counts are stale")
    expected_kind_counts = dict(sorted(kind_counts.items()))
    if manifest.get("semantic_record_kinds") != expected_kind_counts or report.get("semantic_record_kinds") != expected_kind_counts:
        fail("manifest or coverage report kind counts are stale")
    if manifest.get("completion_claim") is not False:
        fail("open-world research corpus must not claim completion")

    summary = {
        "status": "valid", "sources": len(sources), "authoritative_primary_or_official_sources": authoritative_count,
        "contexts": len(contexts), "semantic_records": len(records), "semantic_record_kinds": expected_kind_counts,
        "terms": len(terms), "laws": len(laws), "context_relations": len(loaded["context-relations.jsonl"]),
        "compiler_mappings": len(loaded["compiler-mappings.jsonl"]), "libraries": len(libraries),
        "evidence_assertions": len(loaded["evidence.jsonl"]), "innovations": len(innovations),
        "vertical_examples": len(examples), "gaps": len(loaded["gaps.jsonl"]), "schemas": len(schemas),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except AssertionError as error:
        print(f"INVALID: {error}", file=sys.stderr)
        raise SystemExit(1)
