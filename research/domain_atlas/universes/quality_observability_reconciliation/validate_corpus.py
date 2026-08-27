#!/usr/bin/env python3
"""Validate structure, references, coverage and deterministic regeneration."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import build_corpus


ROOT = Path(__file__).resolve().parent

FILE_SCHEMAS = {
    "sources.jsonl": "source",
    "bounded-context-candidates.jsonl": "bounded-context-candidate",
    "capabilities.jsonl": "capability",
    "typed-operations.jsonl": "typed-operation",
    "decision-points.jsonl": "decision-point",
    "invariants-refusals.jsonl": "invariant-refusal",
    "requirements.jsonl": "requirement",
    "offer-templates.jsonl": "offer-template",
    "compiler-mappings.jsonl": "compiler-mapping",
    "library-boundary-candidates.jsonl": "library-boundary",
    "cross-plane-mappings.jsonl": "cross-plane-mapping",
    "semantic-distinctions.jsonl": "semantic-distinction",
    "innovations.jsonl": "innovation",
    "gaps.jsonl": "gap",
}

ID_FIELDS = {
    "sources.jsonl": "source_id",
    "bounded-context-candidates.jsonl": "context_id",
    "capabilities.jsonl": "capability_id",
    "typed-operations.jsonl": "operation_id",
    "decision-points.jsonl": "decision_id",
    "invariants-refusals.jsonl": "guard_id",
    "requirements.jsonl": "requirement_id",
    "offer-templates.jsonl": "offer_id",
    "compiler-mappings.jsonl": "mapping_id",
    "library-boundary-candidates.jsonl": "library_id",
    "cross-plane-mappings.jsonl": "mapping_id",
    "semantic-distinctions.jsonl": "distinction_id",
    "innovations.jsonl": "innovation_id",
    "gaps.jsonl": "gap_id",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as error:
                fail(f"{path.name}:{line_number}: invalid JSON: {error}")
            if not isinstance(value, dict):
                fail(f"{path.name}:{line_number}: record must be an object")
            records.append(value)
    return records


def type_matches(type_name: str, value: Any) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "null": value is None,
    }[type_name]


def validate_schema(schema: dict[str, Any], value: Any, location: str) -> None:
    """Validate the intentionally small JSON-Schema vocabulary used by this corpus."""
    if "const" in schema and value != schema["const"]:
        fail(f"{location}: expected constant {schema['const']!r}, got {value!r}")
    if "enum" in schema and value not in schema["enum"]:
        fail(f"{location}: {value!r} not in enum {schema['enum']!r}")
    declared_type = schema.get("type")
    if declared_type is not None and not type_matches(declared_type, value):
        fail(f"{location}: expected {declared_type}, got {type(value).__name__}")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            fail(f"{location}: shorter than minLength")
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            fail(f"{location}: does not match {schema['pattern']!r}")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            fail(f"{location}: below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            fail(f"{location}: above maximum")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            fail(f"{location}: fewer than minItems")
        if schema.get("uniqueItems"):
            normalized = [json.dumps(item, sort_keys=True) for item in value]
            if len(normalized) != len(set(normalized)):
                fail(f"{location}: duplicate array items")
        if "items" in schema:
            for index, item in enumerate(value):
                validate_schema(schema["items"], item, f"{location}[{index}]")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                fail(f"{location}: missing required property {key!r}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extras = set(value) - set(properties)
            if extras:
                fail(f"{location}: unexpected properties {sorted(extras)}")
        for key, child_schema in properties.items():
            if key in value:
                validate_schema(child_schema, value[key], f"{location}.{key}")


def exact_set(actual: set[str], expected: set[str], label: str) -> None:
    if actual != expected:
        fail(f"{label}: missing={sorted(expected - actual)} extra={sorted(actual - expected)}")


def refs_exist(refs: list[str], valid: set[str], location: str) -> None:
    missing = set(refs) - valid
    if missing:
        fail(f"{location}: unresolved references {sorted(missing)}")


def main() -> int:
    errors: list[str] = []
    try:
        rendered = build_corpus.render()
        for path, expected in sorted(rendered.items()):
            if not path.exists():
                fail(f"missing generated file: {path.relative_to(ROOT)}")
            actual = path.read_text(encoding="utf-8")
            if actual != expected:
                fail(f"generated drift: run build_corpus.py for {path.relative_to(ROOT)}")

        schema_values = build_corpus.schemas()
        records_by_file: dict[str, list[dict[str, Any]]] = {}
        for filename, schema_name in FILE_SCHEMAS.items():
            records = load_jsonl(ROOT / filename)
            if not records:
                fail(f"{filename}: registry must not be empty")
            records_by_file[filename] = records
            schema = schema_values[schema_name]
            for index, record in enumerate(records, 1):
                validate_schema(schema, record, f"{filename}:{index}")
            id_field = ID_FIELDS[filename]
            ids = [record[id_field] for record in records]
            if len(ids) != len(set(ids)):
                fail(f"{filename}: duplicate {id_field}")

        sources = records_by_file["sources.jsonl"]
        contexts = records_by_file["bounded-context-candidates.jsonl"]
        capabilities = records_by_file["capabilities.jsonl"]
        operations = records_by_file["typed-operations.jsonl"]
        decisions = records_by_file["decision-points.jsonl"]
        guards = records_by_file["invariants-refusals.jsonl"]
        requirements = records_by_file["requirements.jsonl"]
        offers = records_by_file["offer-templates.jsonl"]
        compiler_mappings = records_by_file["compiler-mappings.jsonl"]
        libraries = records_by_file["library-boundary-candidates.jsonl"]
        cross_planes = records_by_file["cross-plane-mappings.jsonl"]
        distinctions = records_by_file["semantic-distinctions.jsonl"]
        innovations = records_by_file["innovations.jsonl"]
        gaps = records_by_file["gaps.jsonl"]

        if len(contexts) < 25:
            fail(f"bounded-context minimum not met: {len(contexts)} < 25")
        if len(capabilities) + len(operations) < 120:
            fail(f"capability/operation minimum not met: {len(capabilities) + len(operations)} < 120")
        if len(operations) < 120:
            fail(f"typed-operation depth minimum not met: {len(operations)} < 120")
        if len(sources) < 40:
            fail(f"source minimum not met: {len(sources)} < 40")
        if len(innovations) < 20:
            fail(f"innovation minimum not met: {len(innovations)} < 20")
        if len(gaps) < 20:
            fail(f"gap depth minimum not met: {len(gaps)} < 20")

        authority_counts = Counter(item["evidence_role"] for item in sources)
        required_roles = {"normative_authority", "open_specification", "regulatory_authority", "original_research", "implementation_evidence"}
        exact_set(set(authority_counts), required_roles, "evidence-role coverage")
        if sum(authority_counts[role] for role in ("normative_authority", "open_specification", "regulatory_authority")) < 25:
            fail("fewer than 25 normative/open/regulatory primary sources")
        if authority_counts["original_research"] < 8:
            fail("fewer than 8 original research sources")
        if authority_counts["implementation_evidence"] < 15:
            fail("fewer than 15 official implementation sources")
        source_kinds = {item["source_kind"] for item in sources}
        if not {"standard", "specification", "official_oss_docs", "research_paper"}.issubset(source_kinds):
            fail("source-kind coverage must include standards, specifications, OSS docs and research papers")

        source_ids = {item["source_id"] for item in sources}
        context_ids = {item["context_id"] for item in contexts}
        capability_ids = {item["capability_id"] for item in capabilities}
        operation_ids = {item["operation_id"] for item in operations}
        decision_ids = {item["decision_id"] for item in decisions}
        guard_ids = {item["guard_id"] for item in guards}
        requirement_ids = {item["requirement_id"] for item in requirements}
        offer_ids = {item["offer_id"] for item in offers}
        cross_plane_ids = {item["mapping_id"] for item in cross_planes}

        for record in contexts:
            refs_exist(record["source_refs"], source_ids, record["context_id"])
            refs_exist(record["capability_refs"], capability_ids, record["context_id"])
            refs_exist(record["operation_refs"], operation_ids, record["context_id"])
            refs_exist(record["decision_refs"], decision_ids, record["context_id"])
            refs_exist([record["invariant_ref"]], guard_ids, record["context_id"])
            refs_exist([record["cross_plane_ref"]], cross_plane_ids, record["context_id"])

        context_to_ops = {item["context_id"]: set(item["operation_refs"]) for item in contexts}
        context_to_caps = {item["context_id"]: set(item["capability_refs"]) for item in contexts}
        for record in capabilities:
            refs_exist([record["owner_context"]], context_ids, record["capability_id"])
            refs_exist(record["operation_refs"], operation_ids, record["capability_id"])
            if not set(record["operation_refs"]).issubset(context_to_ops[record["owner_context"]]):
                fail(f"{record['capability_id']}: operation owned by different context")
            refs_exist(record["source_refs"], source_ids, record["capability_id"])

        for record in operations:
            refs_exist([record["owner_context"]], context_ids, record["operation_id"])
            refs_exist([record["capability_ref"]], capability_ids, record["operation_id"])
            if record["capability_ref"] not in context_to_caps[record["owner_context"]]:
                fail(f"{record['operation_id']}: capability owned by different context")
            refs_exist(record["source_refs"], source_ids, record["operation_id"])
            signature = record["signature"]
            if set(signature) != {"inputs", "output"} or not signature["inputs"] or not isinstance(signature["output"], dict):
                fail(f"{record['operation_id']}: malformed typed signature")

        for record in decisions:
            refs_exist([record["owner_context"]], context_ids, record["decision_id"])
            refs_exist(record["affects_operations"], operation_ids, record["decision_id"])
            refs_exist(record["source_refs"], source_ids, record["decision_id"])

        for record in guards:
            refs_exist([record["owner_context"]], context_ids, record["guard_id"])
            refs_exist(record["source_refs"], source_ids, record["guard_id"])
            codes = [item["code"] for item in record["refusals"]]
            if len(codes) != len(set(codes)):
                fail(f"{record['guard_id']}: duplicate refusal code")

        for record in requirements:
            refs_exist([record["owner_context"]], context_ids, record["requirement_id"])
            refs_exist(record["required_capabilities"], capability_ids, record["requirement_id"])
            refs_exist(record["required_decisions"], decision_ids, record["requirement_id"])
            refs_exist(record["source_refs"], source_ids, record["requirement_id"])

        for record in offers:
            refs_exist([record["owner_context"]], context_ids, record["offer_id"])
            refs_exist(record["offered_capabilities"], capability_ids, record["offer_id"])
            profile_ops = [item["operation_ref"] for item in record["operation_profiles"]]
            refs_exist(profile_ops, operation_ids, record["offer_id"])
            exact_set(set(profile_ops), context_to_ops[record["owner_context"]], f"{record['offer_id']} operation profiles")
            refs_exist(record["source_refs"], source_ids, record["offer_id"])

        if len(compiler_mappings) != len(operations):
            fail("compiler mappings must be total over typed operations")
        mapped_ops = {item["operation_ref"] for item in compiler_mappings}
        exact_set(mapped_ops, operation_ids, "compiler operation totality")
        for record in compiler_mappings:
            refs_exist([record["requirement_ref"]], requirement_ids, record["mapping_id"])
            refs_exist([record["offer_template_ref"]], offer_ids, record["mapping_id"])
            refs_exist(record["source_refs"], source_ids, record["mapping_id"])

        if len(libraries) != len(contexts):
            fail("each context must have exactly one candidate library boundary")
        for record in libraries:
            refs_exist([record["owner_context"]], context_ids, record["library_id"])
            pure = set(record["pure_operation_refs"])
            effect = set(record["effect_operation_refs"])
            if pure & effect:
                fail(f"{record['library_id']}: pure/effect operation overlap")
            exact_set(pure | effect, context_to_ops[record["owner_context"]], f"{record['library_id']} operation partition")
            refs_exist(record["source_refs"], source_ids, record["library_id"])

        expected_planes = {"type_shape", "pipeline", "lineage", "governance", "semantic", "runtime", "industry"}
        if len(cross_planes) != len(contexts):
            fail("each context must have a cross-plane mapping")
        for record in cross_planes:
            refs_exist([record["context_ref"]], context_ids, record["mapping_id"])
            exact_set({item["plane"] for item in record["plane_bindings"]}, expected_planes, f"{record['mapping_id']} planes")
            refs_exist(record["source_refs"], source_ids, record["mapping_id"])

        required_distinctions = {
            "qor.distinction.validity_vs_quality",
            "qor.distinction.quality_vs_fitness",
            "qor.distinction.conformance_vs_observability",
            "qor.distinction.observability_vs_reconciliation",
            "qor.distinction.detection_vs_adjudication",
            "qor.distinction.adjudication_vs_correction",
            "qor.distinction.declared_vs_observed_contract",
            "qor.distinction.source_vs_accounting_truth",
            "qor.distinction.accounting_vs_control_truth",
        }
        distinction_ids = {item["distinction_id"] for item in distinctions}
        if not required_distinctions.issubset(distinction_ids):
            fail(f"missing sovereign distinctions: {sorted(required_distinctions - distinction_ids)}")

        for record in innovations:
            if not 2021 <= record["year"] <= 2026:
                fail(f"{record['innovation_id']}: year outside 2021-2026")
            refs_exist(record["source_refs"], source_ids, record["innovation_id"])

        evidence_consumers = contexts + capabilities + operations + decisions + guards + requirements + offers + compiler_mappings + libraries + cross_planes + innovations
        used_source_ids = {source_ref for record in evidence_consumers for source_ref in record.get("source_refs", [])}
        exact_set(used_source_ids, source_ids, "evidence source utilization")

        if not any(item["gap_id"] == "qor.gap.independent_review" for item in gaps):
            fail("independent-review gap must remain explicit")
        if not any(item["gap_id"] == "qor.gap.enumeration_saturation" for item in gaps):
            fail("enumeration-saturation gap must remain explicit")
        if any(item.get("status") in {"adjudicated", "canonical", "complete"} for records in records_by_file.values() for item in records):
            fail("candidate corpus contains falsely adjudicated status")

        core_text = " ".join(json.dumps(item, sort_keys=True).lower() for item in contexts + capabilities + operations + decisions + requirements + offers + compiler_mappings + libraries)
        forbidden = ("large language model", "generative-ai", "prompt-based", "agentic")
        found = [term for term in forbidden if term in core_text]
        if found:
            fail(f"forbidden core method dependency: {found}")

        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        actual_counts = {name.removesuffix(".jsonl").replace("-", "_"): len(records) for name, records in records_by_file.items()}
        actual_counts["capability_operation_candidates"] = len(capabilities) + len(operations)
        if manifest["counts"] != actual_counts:
            fail(f"manifest counts drift: expected {actual_counts}, got {manifest['counts']}")
        if manifest["completion_claim"] is not False:
            fail("manifest must not claim completion")

        print("VALID quality/observability/reconciliation corpus")
        print(json.dumps({
            "bounded_context_candidates": len(contexts),
            "capabilities": len(capabilities),
            "typed_operations": len(operations),
            "capability_operation_candidates": len(capabilities) + len(operations),
            "decision_points": len(decisions),
            "invariant_refusal_sets": len(guards),
            "requirements": len(requirements),
            "offer_templates": len(offers),
            "compiler_mappings": len(compiler_mappings),
            "library_boundaries": len(libraries),
            "cross_plane_mappings": len(cross_planes),
            "semantic_distinctions": len(distinctions),
            "primary_sources": len(sources),
            "source_roles": dict(sorted(authority_counts.items())),
            "recent_innovations_2021_2026": len(innovations),
            "explicit_gaps": len(gaps),
        }, indent=2, sort_keys=True))
    except AssertionError as error:
        errors.append(str(error))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
