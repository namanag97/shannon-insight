#!/usr/bin/env python3
"""Offline structural and governance validator for the library registry."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


HERE = Path(__file__).resolve().parent
ATLAS = HERE.parents[1]
UNIVERSES = ATLAS / "universes"

KIND_TO_DEF = {
    "library_contribution": "libraryContribution",
    "library_family": "libraryFamily",
    "library_design_context": "libraryDesignContext",
    "implementation_artifact": "implementationArtifact",
    "package_artifact": "packageArtifact",
    "build_artifact": "buildArtifact",
    "deployed_service": "deployedService",
    "product": "product",
    "context_to_library": "contextLink",
    "operation_to_library": "operationLink",
    "kernel_to_library": "kernelLink",
    "dependency_edge": "dependencyEdge",
    "capability_requirement": "capabilityRequirement",
    "capability_offer": "capabilityOffer",
    "registry_decision": "registryDecision",
    "evidence_source": "evidenceSource",
    "innovation": "innovation",
    "typed_gap": "typedGap",
    "review_issue": "reviewIssue",
    "local_crosswalk": "localCrosswalk",
    "artifact_kind_definition": "artifactKindDefinition",
}

ID_KEYS = ("library_id", "family_id", "context_id", "implementation_id", "package_id", "build_id", "service_id", "product_id", "link_id", "edge_id", "requirement_id", "offer_id", "decision_id", "source_id", "innovation_id", "gap_id", "review_id", "crosswalk_id", "kind_id")


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path.name}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{path.name}:{line_number}: record is not an object")
        rows.append(value)
    return rows


def record_identity(record: dict[str, Any]) -> str:
    for key in ID_KEYS:
        if key in record:
            return str(record[key])
    return "<missing-id>"


def resolve(schema: dict[str, Any], node: dict[str, Any]) -> dict[str, Any]:
    seen = set()
    while "$ref" in node:
        ref = node["$ref"]
        if ref in seen or not ref.startswith("#/$defs/"):
            return node
        seen.add(ref)
        node = schema["$defs"][ref.rsplit("/", 1)[-1]]
    return node


def type_ok(expected: str, value: Any) -> bool:
    return {
        "object": lambda: isinstance(value, dict),
        "array": lambda: isinstance(value, list),
        "string": lambda: isinstance(value, str),
        "integer": lambda: isinstance(value, int) and not isinstance(value, bool),
        "number": lambda: isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": lambda: isinstance(value, bool),
        "null": lambda: value is None,
    }[expected]()


def validate_schema_value(schema: dict[str, Any], node: dict[str, Any], value: Any, path: str, out: Validation) -> None:
    node = resolve(schema, node)
    expected = node.get("type")
    if expected:
        choices = expected if isinstance(expected, list) else [expected]
        if not any(type_ok(choice, value) for choice in choices):
            out.errors.append(f"{path}: expected {choices}, got {type(value).__name__}")
            return
    if "const" in node and value != node["const"]:
        out.errors.append(f"{path}: expected const {node['const']!r}")
    if "enum" in node and value not in node["enum"]:
        out.errors.append(f"{path}: {value!r} not in enum")
    if isinstance(value, str):
        if "pattern" in node and not re.search(node["pattern"], value):
            out.errors.append(f"{path}: {value!r} does not match {node['pattern']!r}")
        if len(value) < node.get("minLength", 0):
            out.errors.append(f"{path}: string shorter than minLength")
        if node.get("format") == "uri" and not urlparse(value).scheme:
            out.errors.append(f"{path}: URI has no scheme")
        if node.get("format") == "date" and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            out.errors.append(f"{path}: invalid date")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in node and value < node["minimum"]:
            out.errors.append(f"{path}: below minimum")
        if "maximum" in node and value > node["maximum"]:
            out.errors.append(f"{path}: above maximum")
    if isinstance(value, list):
        if len(value) < node.get("minItems", 0):
            out.errors.append(f"{path}: too few items")
        if "maxItems" in node and len(value) > node["maxItems"]:
            out.errors.append(f"{path}: too many items")
        if node.get("uniqueItems"):
            rendered = [json.dumps(item, sort_keys=True) for item in value]
            if len(rendered) != len(set(rendered)):
                out.errors.append(f"{path}: duplicate array item")
        if "items" in node:
            for index, item in enumerate(value):
                validate_schema_value(schema, node["items"], item, f"{path}[{index}]", out)
    if isinstance(value, dict):
        required = node.get("required", [])
        for key in required:
            if key not in value:
                out.errors.append(f"{path}: missing required property {key}")
        properties = node.get("properties", {})
        if node.get("additionalProperties") is False:
            for key in value:
                if key not in properties:
                    out.errors.append(f"{path}: unexpected property {key}")
        for key, child in properties.items():
            if key in value:
                validate_schema_value(schema, child, value[key], f"{path}.{key}", out)


def schema_validation(schema: dict[str, Any], records: list[dict[str, Any]], out: Validation) -> None:
    out.require(schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", "schema must use JSON Schema Draft 2020-12")
    for index, record in enumerate(records, 1):
        kind = record.get("record_kind")
        out.require(kind in KIND_TO_DEF, f"registry line {index}: unknown record_kind {kind!r}")
        if kind in KIND_TO_DEF:
            validate_schema_value(schema, schema["$defs"][KIND_TO_DEF[kind]], record, f"registry:{index}:{kind}", out)


def validate_manifest(manifest: dict[str, Any], out: Validation) -> None:
    for filename, expected in manifest["file_sha256"].items():
        path = HERE / filename
        out.require(path.is_file(), f"manifest file missing: {filename}")
        if path.is_file():
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            out.require(actual == expected, f"manifest digest mismatch: {filename}")
    for item in manifest["compiler_input_inventory"]:
        path = ATLAS.parent.parent / item["path"]
        out.require(path.is_file(), f"compiler input missing: {item['path']}")
        if path.is_file():
            out.require(hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"], f"compiler input changed: {item['path']}")
        out.require(item["source_schema_is_canonical"] is False, f"legacy compiler schema incorrectly marked canonical: {item['path']}")
    current_paths = {path for path in UNIVERSES.rglob("library-*") if path.is_file()}
    current_paths.update(path for path in UNIVERSES.rglob("libraries.jsonl") if path.is_file())
    current = sorted(current_paths, key=lambda p: p.as_posix())
    inventory = {row["path"]: row for row in manifest["source_inventory"]}
    out.require(len(current) == len(inventory), "source inventory does not cover every current universe library output")
    for path in current:
        relative = path.relative_to(ATLAS.parent.parent).as_posix()
        out.require(relative in inventory, f"un-crosswalked universe candidate file: {relative}")
        if relative in inventory:
            item = inventory[relative]
            if path.suffix == ".jsonl":
                rows = load_jsonl(path)
                out.require(len(rows) == item["records"], f"source record count changed: {relative}")
                out.require(item["candidate_records"] == len(rows), f"candidate record count missing: {relative}")
            else:
                out.require(item["candidate_records"] == 0, f"non-candidate artifact counted as candidates: {relative}")
            out.require(item["source_schema_is_canonical"] is False, f"source artifact incorrectly marked canonical: {relative}")
            out.require(hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"], f"source digest changed: {relative}")


def validate_registry(records: list[dict[str, Any]], manifest: dict[str, Any], out: Validation) -> dict[str, int]:
    counts = Counter(record["record_kind"] for record in records)
    out.require(dict(sorted(counts.items())) == manifest["counts"], "manifest counts differ from unified registry")
    identities = [(record["record_kind"], record_identity(record)) for record in records]
    duplicate_identities = [key for key, count in Counter(identities).items() if count > 1]
    out.require(not duplicate_identities, f"duplicate kind/identity pairs: {duplicate_identities[:10]}")

    by_kind: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_kind[record["record_kind"]].append(record)
    libraries = {row["library_id"]: row for row in by_kind["library_contribution"]}
    families = {row["family_id"]: row for row in by_kind["library_family"]}
    contexts = {row["context_id"]: row for row in by_kind["library_design_context"]}
    requirements = {row["requirement_id"]: row for row in by_kind["capability_requirement"]}
    offers = {row["offer_id"]: row for row in by_kind["capability_offer"]}
    crosswalks = by_kind["local_crosswalk"]
    reviews = {row["review_id"]: row for row in by_kind["review_issue"]}

    gates = manifest["quality_gates"]
    out.require(counts["evidence_source"] >= gates["authoritative_primary_or_official_sources_minimum"], "fewer than 50 primary/official sources")
    out.require(counts["library_design_context"] >= gates["library_design_contexts_minimum"], "fewer than 30 library design contexts")
    out.require(counts["library_contribution"] + counts["typed_gap"] >= gates["normalized_contributions_or_typed_gaps_minimum"], "fewer than 180 contributions or typed gaps")
    out.require(counts["registry_decision"] >= gates["registry_decisions_minimum"], "fewer than 25 decisions")
    out.require(counts["innovation"] >= gates["non_llm_innovations_2021_2026_minimum"], "fewer than 20 innovations")

    authoritative_source_kinds = {"official_project", "official_specification", "standards_body", "primary_architecture_source", "official_project_rfc", "primary_paper"}
    authoritative_source_count = sum(row["source_kind"] in authoritative_source_kinds for row in by_kind["evidence_source"])
    out.require(authoritative_source_count >= gates["authoritative_primary_or_official_sources_minimum"], "fewer than 50 sources classified primary/official")
    out.require(authoritative_source_count == len(by_kind["evidence_source"]), "evidence registry contains a source outside primary/official classifications")
    source_domains = {urlparse(row["uri"]).netloc for row in by_kind["evidence_source"]}
    out.require("wikipedia.org" not in source_domains, "secondary encyclopedia source is forbidden")
    for item in by_kind["innovation"]:
        out.require(item["non_llm"] is True, f"innovation not marked non-LLM: {item['innovation_id']}")
        out.require(2021 <= item["year"] <= 2026, f"innovation outside 2021-2026: {item['innovation_id']}")
        out.require(bool(item["evidence_refs"]), f"innovation lacks evidence: {item['innovation_id']}")

    for library_id, item in libraries.items():
        out.require(item["family_ref"] in families, f"{library_id}: family_ref missing")
        out.require(len(item["semantic_owners"]) == 1, f"{library_id}: must have exactly one semantic owner")
        owner = item["semantic_owners"][0]["context_ref"]
        out.require(owner in contexts, f"{library_id}: owner context missing")
        api = item["api_contract"]
        out.require(bool(api["types"]), f"{library_id}: no exact public types")
        out.require(bool(api["traits"]), f"{library_id}: no exact public traits")
        out.require(bool(api["operations"]), f"{library_id}: no exact operations")
        has_api_placeholder = any(part.get("origin") != "source_projection" for key in ("types", "traits", "operations") for part in api[key])
        gap_kinds = {gap["gap_kind"] for gap in item["gaps"]}
        missing_dependency_refs = [
            ref for ref in item["feature_dependency_graph"]["dependency_refs"] if ref not in libraries
        ]
        out.require(
            not missing_dependency_refs or "dependency_identity_unresolved" in gap_kinds,
            f"{library_id}: dangling dependency lacks a typed gap",
        )
        if owner == "context.registry.unresolved":
            out.require(item["status"] == "rejected_unresolved_owner", f"{library_id}: missing owner must reject boundary")
            out.require("semantic_owner_missing" in gap_kinds, f"{library_id}: missing owner lacks typed gap")
        else:
            out.require(item["status"] != "rejected_unresolved_owner", f"{library_id}: resolved owner has rejected-owner status")
        out.require(not has_api_placeholder or "exact_api_contract_missing" in gap_kinds, f"{library_id}: API placeholder lacks typed gap")
        for operation in api["operations"]:
            for key in ("operation_ref", "input_types", "output_type", "purity", "refusal_types"):
                out.require(bool(operation.get(key)), f"{library_id}: operation missing {key}")
        boundary = item["effects"]["boundary"]
        out.require(boundary in {"pure_no_io", "pure_effect_intents", "effectful_runtime", "ffi_boundary", "generated_boundary", "unresolved_refuse"}, f"{library_id}: invalid effect boundary")
        if boundary == "pure_no_io":
            out.require(not item["effects"]["receipts"], f"{library_id}: pure_no_io must not emit runtime receipts")
        if boundary == "unresolved_refuse" or item["library_class"] == "candidate_unclassified":
            out.require("library_class_or_effect_boundary_missing" in gap_kinds, f"{library_id}: unresolved class/effect lacks typed gap")
        out.require(item["bounds"]["time"] and item["bounds"]["state"] and item["bounds"]["resources"], f"{library_id}: incomplete finite bounds")
        out.require(item["boundaries"]["abi"] and item["boundaries"]["serialization"] and item["boundaries"]["dtos"] and item["boundaries"]["anti_corruption"], f"{library_id}: incomplete ABI/DTO/ACL boundary")
        out.require(item["supply_chain"]["advisory_policy"] and item["supply_chain"]["sbom"] and item["supply_chain"]["reproducibility"], f"{library_id}: incomplete supply-chain contract")
        for key in ("oracles", "fixtures", "fuzz", "model_tests", "property_tests", "differential_tests"):
            out.require(bool(item["conformance"][key]), f"{library_id}: conformance class {key} missing")
        out.require(item["conformance"]["portable_offer"] is False, f"{library_id}: portable offer claimed without bound implementations")
        required_ref = f"requirement.{library_id.removeprefix('library.')}.implementation"
        offer_ref = f"offer.{library_id.removeprefix('library.')}.portable"
        out.require(required_ref in requirements, f"{library_id}: requirement record missing")
        out.require(offer_ref in offers, f"{library_id}: offer record missing")

    graph_validator = libraries.get("library.pipeline.graph_validator", {})
    graph_adjudication = graph_validator.get("scope", {}).get("boundary_adjudication", {})
    out.require(
        graph_adjudication.get("disposition") == "explicit_coexistence"
        and set(graph_adjudication.get("subject_refs", [])) == {"library.pipeline.graph_algebra", "library.pipeline.graph_validator"}
        and graph_adjudication.get("no_compatibility_alias") is True,
        "graph algebra/validator coexistence adjudication was lost during normalization",
    )
    graph_review = reviews.get("review.duplicate-boundary.ppl.graph_topology", {})
    out.require(
        graph_review.get("status") == "adjudicated_explicit_coexistence"
        and set(graph_review.get("candidate_refs", [])) == {"library.pipeline.graph_algebra", "library.pipeline.graph_validator"},
        "graph topology duplicate review is not closed by exact coexistence adjudication",
    )

    out.require(
        all(item["semantic_owners"][0]["context_ref"] != "context.registry.unresolved" for item in libraries.values()),
        "one or more normalized contributions still lack a semantic owner",
    )
    out.require(
        all(item["library_class"] != "candidate_unclassified" and item["effects"]["boundary"] != "unresolved_refuse" for item in libraries.values()),
        "one or more normalized contributions still lack an explicit class/effect boundary",
    )
    out.require(
        all(
            ref in libraries
            for item in libraries.values()
            for ref in item["feature_dependency_graph"]["dependency_refs"]
        ),
        "one or more normalized contributions still has an unresolved dependency identity",
    )

    portable_min = gates["portable_offer_requires_independent_implementations"]
    for offer_id, item in offers.items():
        observed = item["observed_independent_qualified_implementations"]
        out.require(item["minimum_independent_qualified_implementations"] >= portable_min, f"{offer_id}: portable minimum below two")
        if item["portable"]:
            out.require(observed >= portable_min, f"{offer_id}: portable with too few implementations")
            out.require(len(set(item["implementation_refs"])) >= portable_min, f"{offer_id}: portable with too few implementation refs")
        else:
            out.require(observed < portable_min or item["status"] != "portable", f"{offer_id}: contradictory portability status")

    for row in by_kind["context_to_library"]:
        out.require(row["context_ref"] in contexts, f"{row['link_id']}: missing context")
        out.require(row["library_ref"] in libraries, f"{row['link_id']}: missing library")
    for kind in ("operation_to_library", "kernel_to_library"):
        for row in by_kind[kind]:
            out.require(row["library_ref"] in libraries, f"{row['link_id']}: missing library")
    for row in by_kind["dependency_edge"]:
        out.require(row["from_ref"] in libraries and row["to_ref"] in libraries, f"{row['edge_id']}: dependency endpoint missing")
        out.require(row["from_ref"] != row["to_ref"], f"{row['edge_id']}: self dependency")

    source_record_count = sum(item["candidate_records"] for item in manifest["source_inventory"])
    out.require(len(crosswalks) == source_record_count, "crosswalk count does not equal all source candidate records")
    out.require(len({row["source_locator"] for row in crosswalks}) == len(crosswalks), "duplicate source locator in crosswalk")
    for row in crosswalks:
        out.require(row["normalized_library_ref"] in libraries, f"{row['crosswalk_id']}: normalized target missing")
        out.require(row["mapping_status"] == "normalized_without_adjudication", f"{row['crosswalk_id']}: dishonest mapping status")

    # Partition files are materialized views and must exactly equal the unified registry slice.
    from generate_registry import PARTITIONS, canonical_line
    for kind, filename in PARTITIONS.items():
        expected = [record for record in records if record["record_kind"] == kind]
        actual = load_jsonl(HERE / filename)
        out.require([canonical_line(x) for x in actual] == [canonical_line(x) for x in expected], f"partition differs from registry: {filename}")

    # Candidate dependency graph must be acyclic.
    graph: dict[str, list[str]] = defaultdict(list)
    for row in by_kind["dependency_edge"]:
        graph[row["from_ref"]].append(row["to_ref"])
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(node: str) -> None:
        if node in visiting:
            out.errors.append(f"dependency cycle at {node}")
            return
        if node in visited:
            return
        visiting.add(node)
        for child in graph[node]:
            visit(child)
        visiting.remove(node)
        visited.add(node)
    for node in sorted(graph):
        visit(node)

    return dict(sorted(counts.items()))


def main() -> int:
    out = Validation()
    try:
        schema = json.loads((HERE / "library-registry.schema.json").read_text(encoding="utf-8"))
        manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
        records = load_jsonl(HERE / "registry.jsonl")
        validate_manifest(manifest, out)
        schema_validation(schema, records, out)
        counts = validate_registry(records, manifest, out)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        out.errors.append(str(exc))
        counts = {}
    if out.errors:
        print(f"FAIL: {len(out.errors)} validation error(s)")
        for error in out.errors[:100]:
            print(f"- {error}")
        if len(out.errors) > 100:
            print(f"- ... {len(out.errors) - 100} more")
        return 1
    summary = {
        "status": "PASS",
        "counts": counts,
        "derived": {
            "contributions_or_typed_gaps": counts["library_contribution"] + counts["typed_gap"],
            "portable_offers": sum(1 for row in records if row["record_kind"] == "capability_offer" and row["portable"]),
            "source_candidate_crosswalk_coverage": counts["local_crosswalk"],
            "unresolved_semantic_owners": sum(
                row["semantic_owners"][0]["context_ref"] == "context.registry.unresolved"
                for row in records if row["record_kind"] == "library_contribution"
            ),
            "unresolved_class_effect_boundaries": sum(
                row["library_class"] == "candidate_unclassified" or row["effects"]["boundary"] == "unresolved_refuse"
                for row in records if row["record_kind"] == "library_contribution"
            ),
            "ambiguous_semantic_owner_gaps": sum(
                gap["gap_kind"] == "ambiguous_semantic_owner"
                for row in records if row["record_kind"] == "library_contribution" for gap in row["gaps"]
            ),
            "unresolved_dependency_identity_gaps": sum(
                gap["gap_kind"] == "dependency_identity_unresolved"
                for row in records if row["record_kind"] == "library_contribution" for gap in row["gaps"]
            ),
            "exact_api_contract_gaps": sum(
                gap["gap_kind"] == "exact_api_contract_missing"
                for row in records if row["record_kind"] == "library_contribution" for gap in row["gaps"]
            ),
        },
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
