#!/usr/bin/env python3
"""Dependency-free structural and semantic validator for the codegen/build atlas."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import build_atlas


ROOT = Path(__file__).resolve().parent


ID_FIELDS = {
    "sources.jsonl": "source_id",
    "bounded-context-candidates.jsonl": "context_id",
    "capabilities.jsonl": "capability_id",
    "typed-operations.jsonl": "operation_id",
    "decision-points.jsonl": "decision_id",
    "compiler-passes.jsonl": "pass_id",
    "artifacts.jsonl": "artifact_id",
    "generation-requirements.jsonl": "requirement_id",
    "backend-offer-templates.jsonl": "offer_id",
    "compatibility-invalidation-laws.jsonl": "law_id",
    "library-toolchain-boundaries.jsonl": "boundary_id",
    "proof-receipt-contracts.jsonl": "receipt_contract_id",
    "innovations-2021-2026.jsonl": "innovation_id",
    "gaps.jsonl": "gap_id",
    "examples/negative-failures.jsonl": "failure_id",
}


class InvalidAtlas(Exception):
    pass


def fail(message: str) -> None:
    raise InvalidAtlas(message)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            fail(f"{path.name}:{line_number}: blank JSONL line")
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            fail(f"{path.name}:{line_number}: {error}")
        if not isinstance(value, dict):
            fail(f"{path.name}:{line_number}: record must be an object")
        values.append(value)
    return values


def type_matches(expected: str, value: Any) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
    }[expected]


def validate_schema(schema: dict[str, Any], value: Any, location: str) -> None:
    if "const" in schema and value != schema["const"]:
        fail(f"{location}: expected constant {schema['const']!r}, got {value!r}")
    if "enum" in schema and value not in schema["enum"]:
        fail(f"{location}: value {value!r} not in {schema['enum']!r}")
    if "type" in schema and not type_matches(schema["type"], value):
        fail(f"{location}: expected {schema['type']}, got {type(value).__name__}")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            fail(f"{location}: shorter than minLength")
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            fail(f"{location}: does not match {schema['pattern']!r}")
    if isinstance(value, int) and not isinstance(value, bool):
        if value < schema.get("minimum", value):
            fail(f"{location}: below minimum")
        if value > schema.get("maximum", value):
            fail(f"{location}: above maximum")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            fail(f"{location}: fewer than minItems")
        if schema.get("uniqueItems"):
            keys = [json.dumps(item, sort_keys=True) for item in value]
            if len(keys) != len(set(keys)):
                fail(f"{location}: duplicate items")
        for index, item in enumerate(value):
            if "items" in schema:
                validate_schema(schema["items"], item, f"{location}[{index}]")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                fail(f"{location}: missing {key!r}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extras = set(value) - set(properties)
            if extras:
                fail(f"{location}: unexpected properties {sorted(extras)}")
        for key, child in properties.items():
            if key in value:
                validate_schema(child, value[key], f"{location}.{key}")


def refs(values: list[str], valid: set[str], location: str) -> None:
    missing = set(values) - valid
    if missing:
        fail(f"{location}: unresolved references {sorted(missing)}")


def one_per_context(records: list[dict[str, Any]], field: str, context_ids: set[str], label: str) -> None:
    counts = Counter(item[field] for item in records)
    if set(counts) != context_ids or any(count != 1 for count in counts.values()):
        fail(f"{label}: expected exactly one record per context")


def main() -> int:
    try:
        expected_files = build_atlas.render()
        for path, expected in sorted(expected_files.items()):
            if not path.exists():
                fail(f"missing generated file {path.relative_to(ROOT)}")
            if path.read_text(encoding="utf-8") != expected:
                fail(f"generated drift in {path.relative_to(ROOT)}; run build_atlas.py")

        schema_values = build_atlas.schemas()
        records: dict[str, list[dict[str, Any]]] = {}
        for filename, schema_name in build_atlas.FILE_SCHEMAS.items():
            values = load_jsonl(ROOT / filename)
            if not values:
                fail(f"{filename}: registry must not be empty")
            schema = schema_values[schema_name]
            for line_number, value in enumerate(values, 1):
                validate_schema(schema, value, f"{filename}:{line_number}")
            id_field = ID_FIELDS[filename]
            ids = [value[id_field] for value in values]
            if len(ids) != len(set(ids)):
                fail(f"{filename}: duplicate {id_field}")
            records[filename] = values

        sources = records["sources.jsonl"]
        contexts = records["bounded-context-candidates.jsonl"]
        capabilities = records["capabilities.jsonl"]
        operations = records["typed-operations.jsonl"]
        decisions = records["decision-points.jsonl"]
        passes = records["compiler-passes.jsonl"]
        artifacts = records["artifacts.jsonl"]
        requirements = records["generation-requirements.jsonl"]
        offers = records["backend-offer-templates.jsonl"]
        laws = records["compatibility-invalidation-laws.jsonl"]
        boundaries = records["library-toolchain-boundaries.jsonl"]
        receipts = records["proof-receipt-contracts.jsonl"]
        innovations = records["innovations-2021-2026.jsonl"]
        gaps = records["gaps.jsonl"]
        failures = records["examples/negative-failures.jsonl"]

        principal_count = len(capabilities) + len(operations) + len(decisions) + len(passes) + len(artifacts)
        minimums = {"contexts": 40, "sources": 60, "principal": 200, "innovations": 20, "failures": 5}
        actuals = {"contexts": len(contexts), "sources": len(sources), "principal": principal_count, "innovations": len(innovations), "failures": len(failures)}
        for label, minimum in minimums.items():
            if actuals[label] < minimum:
                fail(f"{label}: {actuals[label]} < required {minimum}")
        if len(receipts) < 20 or len(gaps) < 20 or len(laws) < 20:
            fail("receipt, gap and law registries must each contain at least 20 records")

        source_ids = {item["source_id"] for item in sources}
        context_ids = {item["context_id"] for item in contexts}
        capability_ids = {item["capability_id"] for item in capabilities}
        operation_ids = {item["operation_id"] for item in operations}
        decision_ids = {item["decision_id"] for item in decisions}
        pass_ids = {item["pass_id"] for item in passes}
        artifact_ids = {item["artifact_id"] for item in artifacts}

        authority_counts = Counter(item["authority_class"] for item in sources)
        if authority_counts["open_specification"] < 25 or authority_counts["official_documentation"] < 25 or authority_counts["original_research"] < 5:
            fail(f"source authority diversity too shallow: {dict(authority_counts)}")
        if any(not item["primary_or_official"] for item in sources):
            fail("all sources must be primary research, specifications, or official project documentation")

        for context in contexts:
            if context["status"] != build_atlas.STATUS:
                fail(f"{context['context_id']}: context status is not candidate")
            refs(context["source_refs"], source_ids, context["context_id"])
            refs(context["capability_refs"], capability_ids, context["context_id"])
            refs(context["operation_refs"], operation_ids, context["context_id"])
            refs([context["decision_ref"]], decision_ids, context["context_id"])
            refs([context["pass_ref"]], pass_ids, context["context_id"])
            refs([context["artifact_ref"]], artifact_ids, context["context_id"])
            if len(context["capability_refs"]) != 2 or len(context["operation_refs"]) != 2:
                fail(f"{context['context_id']}: expected two capabilities and operations")

        for capability in capabilities:
            refs([capability["owner_context"]], context_ids, capability["capability_id"])
            refs([capability["operation_ref"]], operation_ids, capability["capability_id"])
            refs(capability["source_refs"], source_ids, capability["capability_id"])
        for operation in operations:
            refs([operation["owner_context"]], context_ids, operation["operation_id"])
            refs([operation["capability_ref"]], capability_ids, operation["operation_id"])
            refs(operation["source_refs"], source_ids, operation["operation_id"])
        for decision in decisions:
            refs([decision["owner_context"]], context_ids, decision["decision_id"])
            refs(decision["affects"], operation_ids | pass_ids | artifact_ids, decision["decision_id"])
            refs(decision["source_refs"], source_ids, decision["decision_id"])
            if not decision["no_default"]:
                fail(f"{decision['decision_id']}: hidden defaults forbidden")
        for compiler_pass in passes:
            refs([compiler_pass["owner_context"]], context_ids, compiler_pass["pass_id"])
            refs(compiler_pass["decision_refs"], decision_ids, compiler_pass["pass_id"])
            refs(compiler_pass["source_refs"], source_ids, compiler_pass["pass_id"])
        for artifact in artifacts:
            refs([artifact["owner_context"]], context_ids, artifact["artifact_id"])
            refs(artifact["provenance_inputs"], pass_ids | decision_ids, artifact["artifact_id"])
            refs(artifact["source_refs"], source_ids, artifact["artifact_id"])

        one_per_context(decisions, "owner_context", context_ids, "decisions")
        one_per_context(passes, "owner_context", context_ids, "passes")
        one_per_context(artifacts, "owner_context", context_ids, "artifacts")
        one_per_context(requirements, "owner_context", context_ids, "requirements")
        one_per_context(offers, "owner_context", context_ids, "offers")
        one_per_context(boundaries, "owner_context", context_ids, "boundaries")

        for requirement in requirements:
            refs(requirement["required_capabilities"], capability_ids, requirement["requirement_id"])
            refs(requirement["required_operations"], operation_ids, requirement["requirement_id"])
            refs(requirement["required_decisions"], decision_ids, requirement["requirement_id"])
            refs(requirement["source_refs"], source_ids, requirement["requirement_id"])
        for offer in offers:
            refs(offer["offered_capabilities"], capability_ids, offer["offer_id"])
            refs(offer["source_refs"], source_ids, offer["offer_id"])
            if "not evidence" not in offer["non_claim"]:
                fail(f"{offer['offer_id']}: offer must deny provider qualification")
        for boundary in boundaries:
            refs(boundary["source_refs"], source_ids, boundary["boundary_id"])
            if not any("undeclared network" == item for item in boundary["forbidden_ambient_effects"]):
                fail(f"{boundary['boundary_id']}: missing ambient network prohibition")
        for law in laws:
            refs(law["source_refs"], source_ids, law["law_id"])
        for innovation in innovations:
            refs(innovation["source_refs"], source_ids, innovation["innovation_id"])
            if innovation["year"] < 2021 or innovation["year"] > 2026 or not innovation["non_llm"]:
                fail(f"{innovation['innovation_id']}: innovation range/exclusion failure")
        for failure in failures:
            refs([failure["context_ref"]], context_ids, failure["failure_id"])

        required_laws = {
            "cgb.law.lowering-vs-codegen",
            "cgb.law.template-vs-generated-source",
            "cgb.law.generated-source-vs-binary",
            "cgb.law.package-vs-manifest",
            "cgb.law.manifest-vs-occurrence",
            "cgb.law.resolution-vs-execution",
            "cgb.law.reproducibility-vs-conformance",
            "cgb.law.sbom-vs-provenance",
            "cgb.law.signature-vs-truth",
            "cgb.law.rollback-artifact-vs-state",
        }
        law_ids = {item["law_id"] for item in laws}
        if not required_laws.issubset(law_ids):
            fail(f"missing sovereign distinction laws: {sorted(required_laws - law_ids)}")
        law_types = Counter(item["law_type"] for item in laws)
        if any(law_types[kind] < 5 for kind in ["non_collapse", "compatibility", "invalidation"]):
            fail(f"law type coverage too shallow: {dict(law_types)}")

        required_gaps = {"cgb.gap.enumeration-saturation", "cgb.gap.boundary-adjudication", "cgb.gap.source-freshness", "cgb.gap.bootstrap-trust"}
        gap_ids = {item["gap_id"] for item in gaps}
        if not required_gaps.issubset(gap_ids):
            fail(f"missing honest gaps: {sorted(required_gaps - gap_ids)}")

        receipt_ids = {item["receipt_contract_id"] for item in receipts}
        for example_name in ["native-rust-service.json", "wasi-component.json"]:
            example = json.loads((ROOT / "examples" / example_name).read_text(encoding="utf-8"))
            if example["status"] != build_atlas.STATUS:
                fail(f"{example_name}: example status must remain candidate")
            refs(example["selected_passes"], pass_ids, example_name)
            refs(example["evidence"], receipt_ids, example_name)
            if len(example["artifacts"]) < 4 or len(example["explicit_non_equivalences"]) < 3:
                fail(f"{example_name}: example depth insufficient")

        disk_manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        if disk_manifest["completion_claim"] is not False or disk_manifest["llm_or_generative_codegen_in_scope"] is not False:
            fail("manifest must deny completion and exclude LLM/generative codegen")
        if disk_manifest["principal_record_count"] != principal_count:
            fail("manifest principal record count mismatch")

        print("codegen/build atlas validation: PASS")
        print(f"contexts={len(contexts)}")
        print(f"capabilities={len(capabilities)}")
        print(f"typed_operations={len(operations)}")
        print(f"decisions={len(decisions)}")
        print(f"compiler_passes={len(passes)}")
        print(f"artifacts={len(artifacts)}")
        print(f"principal_records={principal_count}")
        print(f"requirements={len(requirements)}")
        print(f"offer_templates={len(offers)}")
        print(f"laws={len(laws)}")
        print(f"library_toolchain_boundaries={len(boundaries)}")
        print(f"proof_receipt_contracts={len(receipts)}")
        print(f"sources={len(sources)} authority={dict(sorted(authority_counts.items()))}")
        print(f"innovations={len(innovations)} gaps={len(gaps)} negative_failures={len(failures)}")
        return 0
    except (InvalidAtlas, OSError, KeyError, TypeError, ValueError) as error:
        print(f"codegen/build atlas validation: FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
