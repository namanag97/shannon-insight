#!/usr/bin/env python3
"""Validate structure, references and research gates for the data type/shape universe."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ERRORS: list[str] = []
WARNINGS: list[str] = []
try:
    import jsonschema as JSONSCHEMA
except ImportError:
    JSONSCHEMA = None
    WARNINGS.append("jsonschema is unavailable; structural reference gates still ran")


def fail(message: str) -> None:
    ERRORS.append(message)


def load_json(name: str):
    try:
        return json.loads((ROOT / name).read_text())
    except Exception as exc:  # pragma: no cover - reporting path
        fail(f"{name}: cannot parse JSON: {exc}")
        return {}


def load_jsonl(name: str) -> list[dict]:
    records = []
    try:
        for line_number, line in enumerate((ROOT / name).read_text().splitlines(), 1):
            if not line.strip():
                fail(f"{name}:{line_number}: blank JSONL line")
                continue
            try:
                value = json.loads(line)
            except Exception as exc:
                fail(f"{name}:{line_number}: invalid JSON: {exc}")
                continue
            if not isinstance(value, dict):
                fail(f"{name}:{line_number}: record is not an object")
                continue
            records.append(value)
    except Exception as exc:  # pragma: no cover - reporting path
        fail(f"{name}: cannot read: {exc}")
    return records


def unique(records: list[dict], field: str, file_name: str) -> dict[str, dict]:
    result = {}
    for index, record in enumerate(records, 1):
        value = record.get(field)
        if not isinstance(value, str) or not value:
            fail(f"{file_name}:{index}: missing/non-string {field}")
            continue
        if value in result:
            fail(f"{file_name}: duplicate {field} {value}")
        result[value] = record
    return result


def schema_validate(instance, schema_name: str, label: str) -> None:
    if JSONSCHEMA is None:
        return
    schema = load_json(f"schemas/{schema_name}")
    validator = JSONSCHEMA.Draft202012Validator(schema, format_checker=JSONSCHEMA.FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
    for error in errors:
        path = "/".join(str(part) for part in error.absolute_path) or "$"
        fail(f"{label}:{path}: {error.message}")


def require_evidence(record: dict, record_id: str, sources: dict[str, dict]) -> None:
    refs = record.get("evidence_refs")
    if not isinstance(refs, list) or not refs:
        fail(f"{record_id}: no evidence_refs")
        return
    for ref in refs:
        if ref not in sources:
            fail(f"{record_id}: unknown evidence ref {ref}")


def main() -> int:
    axes_document = load_json("classification-axes.json")
    gaps_document = load_json("coverage-gaps.json")
    coverage_document = load_json("coverage-report.json")
    sources_list = load_jsonl("sources.jsonl")
    types_list = load_jsonl("type-records.jsonl")
    shapes_list = load_jsonl("shape-records.jsonl")
    operations_list = load_jsonl("operation-totality-matrix.jsonl")
    contexts_list = load_jsonl("bounded-context-candidates.jsonl")
    crosswalks_list = load_jsonl("representation-crosswalks.jsonl")
    invalid_inferences_list = load_jsonl("invalid-inference-matrix.jsonl")

    sources = unique(sources_list, "source_id", "sources.jsonl")
    types = unique(types_list, "type_id", "type-records.jsonl")
    shapes = unique(shapes_list, "shape_id", "shape-records.jsonl")
    operations = unique(operations_list, "operation_id", "operation-totality-matrix.jsonl")
    contexts = unique(contexts_list, "context_id", "bounded-context-candidates.jsonl")
    crosswalks = unique(crosswalks_list, "crosswalk_id", "representation-crosswalks.jsonl")
    invalid_inferences = unique(invalid_inferences_list, "inference_id", "invalid-inference-matrix.jsonl")
    unique(operations_list, "matrix_id", "operation-totality-matrix.jsonl")

    schema_validate(axes_document, "classification-axes.schema.json", "classification-axes.json")
    schema_validate(gaps_document, "coverage-gaps.schema.json", "coverage-gaps.json")
    schema_validate(coverage_document, "coverage-report.schema.json", "coverage-report.json")
    for index, record in enumerate(sources_list, 1):
        schema_validate(record, "source-record.schema.json", f"sources.jsonl:{index}")
    for index, record in enumerate(types_list, 1):
        schema_validate(record, "type-record.schema.json", f"type-records.jsonl:{index}")
    for index, record in enumerate(shapes_list, 1):
        schema_validate(record, "shape-record.schema.json", f"shape-records.jsonl:{index}")
    for index, record in enumerate(operations_list, 1):
        schema_validate(record, "operation-totality-record.schema.json", f"operation-totality-matrix.jsonl:{index}")
    for index, record in enumerate(contexts_list, 1):
        schema_validate(record, "bounded-context-candidate.schema.json", f"bounded-context-candidates.jsonl:{index}")
    for index, record in enumerate(crosswalks_list, 1):
        schema_validate(record, "representation-crosswalk.schema.json", f"representation-crosswalks.jsonl:{index}")
    for index, record in enumerate(invalid_inferences_list, 1):
        schema_validate(record, "invalid-inference.schema.json", f"invalid-inference-matrix.jsonl:{index}")

    if len(sources) < 30:
        fail(f"primary evidence gate: expected >=30 sources, got {len(sources)}")
    if len({record.get("publisher") for record in sources_list}) < 20:
        fail("evidence diversity gate: expected >=20 distinct primary publishers")
    if any(not str(record.get("url", "")).startswith("https://") for record in sources_list):
        fail("all evidence URLs must use https")

    axes = axes_document.get("axes", []) if isinstance(axes_document, dict) else []
    axis_by_id = unique(axes, "axis_id", "classification-axes.json")
    required_axes = {
        "layer", "structure_degree", "modality", "dimensionality", "topology", "grain", "identity_scope", "key_model",
        "cardinality", "sparsity", "nesting", "ordering", "time_role", "change_model", "mutability",
        "finality", "uncertainty_form", "unit_dimension", "missingness_censoring", "schema_evolution",
        "provenance_role", "authority", "privacy_classification", "encoding", "layout", "access_pattern",
        "volume_class", "velocity", "latency_requirement", "locality", "compression", "encryption", "retention",
    }
    missing_axes = sorted(required_axes - set(axis_by_id))
    if missing_axes:
        fail(f"required classification axes absent: {missing_axes}")
    if len(axis_by_id) < 35:
        fail(f"axis depth gate: expected >=35 independent axes, got {len(axis_by_id)}")
    for axis_id, record in axis_by_id.items():
        values = record.get("values", [])
        if len(values) != len(set(values)):
            fail(f"axis {axis_id}: duplicate values")
        if not record.get("independence_rule"):
            fail(f"axis {axis_id}: missing independence rule")

    carriers = {type_id: record for type_id, record in types.items() if record.get("record_kind") == "carrier_type"}
    semantics = {type_id: record for type_id, record in types.items() if record.get("record_kind") == "semantic_value_type"}
    if len(carriers) < 25:
        fail(f"carrier seed gate: expected >=25, got {len(carriers)}")
    if len(semantics) < 60:
        fail(f"semantic seed gate: expected >=60, got {len(semantics)}")
    for type_id, record in types.items():
        if record.get("owner_context") not in contexts:
            fail(f"{type_id}: unknown owner context {record.get('owner_context')}")
        require_evidence(record, type_id, sources)
        for parent in record.get("parent_type_ids", []):
            if parent not in types:
                fail(f"{type_id}: unknown parent type {parent}")
        for carrier_id in record.get("allowed_carriers", []):
            if carrier_id not in carriers:
                fail(f"{type_id}: allowed carrier does not resolve to carrier record: {carrier_id}")
        for field in ["equality_laws", "order_laws", "arithmetic_laws", "invalid_inferences", "compiler_obligations"]:
            if not record.get(field):
                fail(f"{type_id}: missing non-empty {field}")
        if record.get("missingness", {}).get("null_is_reason") is not False:
            fail(f"{type_id}: null_is_reason must be false")
        if record.get("canonicalization", {}).get("digest_safe_without_profile") is not False:
            fail(f"{type_id}: unprofiled digest safety is forbidden")

    required_shape_families = {
        "container", "record", "document", "observation", "tabular", "cube", "array", "temporal", "change",
        "stream", "process", "graph", "spatial", "image", "signal", "media", "telemetry", "uncertainty",
        "optimization", "simulation", "model_artifact", "evidence", "schema",
        "message", "office_document", "configuration", "code", "binary_artifact", "archive", "package",
    }
    shape_family_counts = Counter(record.get("family") for record in shapes_list)
    missing_families = sorted(required_shape_families - set(shape_family_counts))
    if missing_families:
        fail(f"required shape families absent: {missing_families}")
    if len(shapes) < 100:
        fail(f"shape seed gate: expected >=100, got {len(shapes)}")
    required_deep_shapes = {
        "shape.table", "shape.record", "shape.tree_document", "shape.email_message", "shape.mime_entity",
        "shape.conversation_thread", "shape.pdf_document", "shape.word_processing_document",
        "shape.spreadsheet_workbook", "shape.presentation_document", "shape.html_document", "shape.epub_publication",
        "shape.configuration_document", "shape.source_code_file", "shape.abstract_syntax_tree",
        "shape.executable_binary", "shape.bytecode_module", "shape.archive", "shape.web_archive",
        "shape.container_image", "shape.geometry", "shape.coverage", "shape.spatial_tile_set", "shape.point_cloud",
        "shape.graph", "shape.hypergraph", "shape.regular_time_series",
        "shape.record_stream_file", "shape.object_centric_event_log",
        "shape.image", "shape.audio_track", "shape.video_track", "shape.dense_tensor", "shape.sampled_signal",
        "shape.probability_distribution", "shape.scenario_set", "shape.optimization_model", "shape.simulation_experiment",
        "shape.provenance_graph", "shape.evidence_bundle",
    }
    absent_deep_shapes = sorted(required_deep_shapes - set(shapes))
    if absent_deep_shapes:
        fail(f"explicit modality/shape coverage gate absent: {absent_deep_shapes}")
    for shape_id, record in shapes.items():
        if record.get("owner_context") not in contexts:
            fail(f"{shape_id}: unknown owner context {record.get('owner_context')}")
        require_evidence(record, shape_id, sources)
        for parent in record.get("parent_shape_ids", []):
            if parent not in shapes:
                fail(f"{shape_id}: unknown parent shape {parent}")
        for operation_id in record.get("valid_operations", []):
            if operation_id not in operations:
                fail(f"{shape_id}: operation has no totality matrix record: {operation_id}")
        for key in ["element_contract", "keys", "topology", "ordering", "time_semantics", "change_semantics"]:
            if not record.get(key):
                fail(f"{shape_id}: missing {key}")
        for key in ["constraints", "valid_operations", "invalid_operations", "representation_bindings", "information_loss_risks", "compiler_obligations"]:
            if not record.get(key):
                fail(f"{shape_id}: missing non-empty {key}")

    if len(operations) < 100:
        fail(f"operation totality gate: expected >=100 operation records, got {len(operations)}")
    for operation_id, record in operations.items():
        if record.get("owner_context") not in contexts:
            fail(f"{operation_id}: unknown owner context {record.get('owner_context')}")
        require_evidence(record, operation_id, sources)
        if not record.get("failure_modes"):
            fail(f"{operation_id}: missing failure modes")
        if record.get("totality") in {"partial", "conditional_total", "provider_dependent"} and not record.get("preconditions"):
            fail(f"{operation_id}: non-total operation has no preconditions")

    exact_owned_terms = defaultdict(list)
    for context_id, record in contexts.items():
        require_evidence(record, context_id, sources)
        for term in record.get("owns", []):
            exact_owned_terms[term.casefold()].append(context_id)
        for neighbor in record.get("neighbors", []):
            neighbor_id = neighbor.get("context_id")
            if neighbor_id not in contexts:
                fail(f"{context_id}: unknown neighbor {neighbor_id}")
        if not record.get("outside"):
            fail(f"{context_id}: no explicit outside boundary")
        if not record.get("invariants"):
            fail(f"{context_id}: no invariants")
    ownership_collisions = {term: owners for term, owners in exact_owned_terms.items() if len(owners) > 1}
    if ownership_collisions:
        fail(f"exact owned-term collisions require adjudication: {ownership_collisions}")

    known_records = set(types) | set(shapes)
    if len(crosswalks) < 50:
        fail(f"representation crosswalk gate: expected >=50, got {len(crosswalks)}")
    for crosswalk_id, record in crosswalks.items():
        if record.get("owner_context") not in contexts:
            fail(f"{crosswalk_id}: unknown owner context {record.get('owner_context')}")
        require_evidence(record, crosswalk_id, sources)
        for record_id in record.get("source_record_ids", []) + record.get("target_record_ids", []):
            if record_id not in known_records:
                fail(f"{crosswalk_id}: unknown source/target record {record_id}")
        if not record.get("prerequisites") or not record.get("preserved_semantics") or not record.get("lost_or_at_risk"):
            fail(f"{crosswalk_id}: crosswalk must expose prerequisites, preserved semantics and loss risks")
        if len(record.get("test_obligations", [])) < 4:
            fail(f"{crosswalk_id}: insufficient crosswalk test obligations")

    if len(invalid_inferences) < 60:
        fail(f"invalid inference gate: expected >=60, got {len(invalid_inferences)}")
    refusal_codes = set()
    for inference_id, record in invalid_inferences.items():
        if record.get("owner_context") not in contexts:
            fail(f"{inference_id}: unknown owner context {record.get('owner_context')}")
        require_evidence(record, inference_id, sources)
        for record_id in record.get("affected_records", []):
            if record_id not in known_records:
                fail(f"{inference_id}: unknown affected record {record_id}")
        code = record.get("refusal_code")
        if code in refusal_codes:
            fail(f"{inference_id}: duplicate refusal code {code}")
        refusal_codes.add(code)
        if not record.get("required_evidence"):
            fail(f"{inference_id}: no required evidence for otherwise-invalid conclusion")

    referenced_sources = {
        ref
        for collection in [types_list, shapes_list, operations_list, contexts_list, crosswalks_list, invalid_inferences_list]
        for record in collection
        for ref in record.get("evidence_refs", [])
    }
    if len(referenced_sources) < 30:
        fail(f"evidence use gate: only {len(referenced_sources)} distinct sources are referenced")
    unreferenced_sources = sorted(set(sources) - referenced_sources)
    if unreferenced_sources:
        WARNINGS.append(f"{len(unreferenced_sources)} indexed sources are not yet referenced by a candidate: {unreferenced_sources}")

    gaps = gaps_document.get("gaps", []) if isinstance(gaps_document, dict) else []
    if len(gaps) < 10:
        fail(f"honest gap gate: expected >=10 coverage gaps, got {len(gaps)}")
    unique(gaps, "gap_id", "coverage-gaps.json")
    if "open-world" not in str(gaps_document.get("completeness_claim", "")).casefold():
        fail("coverage-gaps completeness claim must state open-world posture")

    reported_counts = coverage_document.get("counts", {}) if isinstance(coverage_document, dict) else {}
    expected_counts = {
        "classification_axes": len(axis_by_id), "sources": len(sources), "carrier_types": len(carriers),
        "semantic_value_types": len(semantics), "logical_shapes": len(shapes),
        "operation_totality_records": len(operations), "representation_crosswalks": len(crosswalks),
        "invalid_inferences": len(invalid_inferences), "bounded_context_candidates": len(contexts),
        "coverage_gaps": len(gaps),
    }
    for count_name, count in expected_counts.items():
        if reported_counts.get(count_name) != count:
            fail(f"coverage-report {count_name}: reported {reported_counts.get(count_name)!r}, expected {count}")
    if coverage_document.get("shape_counts_by_family") != dict(sorted(shape_family_counts.items())):
        fail("coverage-report shape_counts_by_family does not match shape registry")

    forbidden_patterns = {
        "large language model": re.compile(r"large[ _-]?language[ _-]?model", re.I),
        "retrieval augmented generation": re.compile(r"retrieval[ _-]?augmented[ _-]?generation", re.I),
        "agent memory": re.compile(r"agent[ _-]?memory", re.I),
        "prompt semantics": re.compile(r"prompt[ _-]?(?:engineering|semantics|template)", re.I),
    }
    core_text = json.dumps([types_list, shapes_list, operations_list, contexts_list, crosswalks_list, invalid_inferences_list], ensure_ascii=False)
    for label, pattern in forbidden_patterns.items():
        if pattern.search(core_text):
            fail(f"forbidden core dependency detected: {label}")

    summary = {
        "axes": len(axis_by_id),
        "axis_values": sum(len(record.get("values", [])) for record in axes),
        "primary_sources": len(sources),
        "distinct_publishers": len({record.get("publisher") for record in sources_list}),
        "referenced_sources": len(referenced_sources),
        "carrier_types": len(carriers),
        "semantic_value_types": len(semantics),
        "shapes": len(shapes),
        "shape_families": dict(sorted(shape_family_counts.items())),
        "operation_totality_records": len(operations),
        "representation_crosswalks": len(crosswalks),
        "invalid_inferences": len(invalid_inferences),
        "bounded_context_candidates": len(contexts),
        "coverage_gaps": len(gaps),
        "warnings": WARNINGS,
        "errors": ERRORS,
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if ERRORS:
        print(f"FAIL data type/shape universe: {len(ERRORS)} error(s)", file=sys.stderr)
        return 1
    print("PASS data type/shape universe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
