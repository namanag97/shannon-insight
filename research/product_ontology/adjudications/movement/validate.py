#!/usr/bin/env python3
"""Validate the movement product/capability/library adjudication bundle."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_bundle import (
    HERE,
    MOVEMENT_OUTPUTS as OUTPUTS,
    MOVEMENT_SECTIONS as SECTIONS,
    load_source,
    movement_materialize as materialize,
)
from enrich_source import source_bytes as enriched_source_bytes


ID = re.compile(r"^[a-z][a-z0-9_]*(?:[.-][a-z0-9_]+)+$")
AXES = {
    "user", "job", "adoption", "semantics", "authority",
    "lifecycle", "operation", "economics", "interface", "market_evidence",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path.name}:{number}: record is not an object")
        rows.append(value)
    return rows


def identity(row: dict[str, Any]) -> str:
    for key in (
        "source_id", "artifact_id", "decision_id", "meaning_id", "library_id",
        "requirement_id", "offer_id", "relation_id", "legacy_ref", "test_id",
        "binding_map_id", "gap_id", "dossier_id", "kind",
    ):
        if key in row:
            return str(row[key])
    return "<missing>"


def main() -> int:
    errors: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    source = load_source()
    require((HERE / "source.json").read_bytes() == enriched_source_bytes(), "source.json differs from deterministic movement enrichment")
    expected_payloads, expected_manifest = materialize(source)
    manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
    metamodel = json.loads((HERE / "metamodel.json").read_text(encoding="utf-8"))

    require(manifest == expected_manifest, "manifest differs from deterministic source projection")
    for filename, expected in expected_payloads.items():
        path = HERE / filename
        require(path.is_file(), f"missing generated file: {filename}")
        if path.is_file():
            require(path.read_bytes() == expected, f"stale generated file: {filename}")
    for filename, expected_hash in manifest.get("file_sha256", {}).items():
        path = HERE / filename
        if path.is_file():
            require(hashlib.sha256(path.read_bytes()).hexdigest() == expected_hash, f"digest mismatch: {filename}")

    registry = load_jsonl(HERE / "registry.jsonl")
    kinds = Counter(row.get("record_kind") for row in registry)
    require(dict(sorted(kinds.items())) == manifest["counts"], "registry counts differ from manifest")
    pairs = [(row.get("record_kind"), identity(row)) for row in registry]
    require(len(pairs) == len(set(pairs)), "duplicate record kind/identity pair")
    for row in registry:
        ident = identity(row)
        valid = bool(re.fullmatch(r"^[a-z][a-z0-9_]*$", ident)) if row.get("record_kind") == "artifact_kind_definition" else bool(ID.fullmatch(ident))
        require(valid, f"invalid identity: {ident}")
        require(row.get("edition") == source["edition"], f"edition mismatch: {ident}")

    by_section = {section: load_jsonl(HERE / filename) for section, filename in OUTPUTS.items()}
    for section, (record_kind, identity_key) in SECTIONS.items():
        rows = by_section[section]
        require(all(row.get("record_kind") == record_kind for row in rows), f"wrong record kind in {section}")
        require([row[identity_key] for row in rows] == sorted(row[identity_key] for row in rows), f"unsorted partition: {section}")

    evidence = {row["source_id"]: row for row in by_section["sources"]}
    artifact_kinds = {row["kind"]: row for row in by_section["artifact_kinds"]}
    artifacts = {row["artifact_id"]: row for row in by_section["artifacts"]}
    libraries = {row["library_id"]: row for row in by_section["libraries"]}
    node_ids = set(artifacts) | set(libraries)
    all_evidence_refs: list[tuple[str, str]] = []

    require(len(evidence) >= 18, "fewer than 18 scoped primary/official evidence records")
    allowed_source_classes = {
        "primary_paper", "official_specification", "official_project_specification",
        "official_project_documentation", "official_product_documentation",
        "official_protocol_documentation", "official_industry_framework",
    }
    for source_id, row in evidence.items():
        require(row["source_class"] in allowed_source_classes, f"non-primary/official source class: {source_id}")
        require(row.get("claim") and row.get("scope_limit"), f"unscoped evidence: {source_id}")
        require(str(row.get("uri", "")).startswith("https://"), f"non-HTTPS evidence URI: {source_id}")
        require(bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", row.get("retrieved_at", ""))), f"bad retrieval date: {source_id}")

    require(set(artifact_kinds) == set(metamodel["artifact_kinds"]), "artifact kinds differ from metamodel")
    for artifact_id, row in artifacts.items():
        require(row["kind"] in artifact_kinds, f"unknown artifact kind: {artifact_id}")
        require(isinstance(row.get("adoption_unit"), bool) and isinstance(row.get("operated"), bool), f"missing identity flags: {artifact_id}")
        for ref in row.get("evidence_refs", []):
            all_evidence_refs.append((artifact_id, ref))
        if row["kind"] in {"architecture_pattern", "suite"}:
            require(row.get("semantic_owner_ref") is None, f"pattern/suite claims semantic ownership: {artifact_id}")
        if row["kind"] in {"capability", "semantic_contract", "standard", "interface", "resource_class"}:
            require(not row["adoption_unit"], f"sub-product artifact claims adoption identity: {artifact_id}")
        if row["kind"] in {"standard", "semantic_contract", "interface", "resource_class"}:
            require(not row["operated"], f"non-runtime contract claims operation: {artifact_id}")
        if row["kind"] == "implementation":
            require(row.get("semantic_owner_ref") is None, f"implementation claims semantic ownership: {artifact_id}")
        if row["kind"] == "product":
            require(row["adoption_unit"] and row["operated"], f"product lacks adoption/operation boundary: {artifact_id}")

    for artifact_id, row in artifacts.items():
        owner = row.get("semantic_owner_ref")
        if owner:
            require(owner in artifacts, f"missing semantic owner {owner} for {artifact_id}")
            if owner in artifacts:
                require(artifacts[owner]["kind"] in {"semantic_contract", "neighboring_product"}, f"invalid semantic owner kind for {artifact_id}: {owner}")

    allowed_library_classes = {
        "semantic_pure", "algorithm_pure", "policy_pure", "test_oracle",
        "effect_port_contract", "provider_adapter", "runtime_mechanism",
    }
    allowed_effects = {"pure_no_io", "pure_effect_intents", "pure_effect_proposals", "effectful_runtime"}
    graph: dict[str, list[str]] = defaultdict(list)
    for library_id, row in libraries.items():
        require(bool(row.get("product_refs")), f"library lacks product attribution: {library_id}")
        require(row["owner_ref"] in artifacts and artifacts[row["owner_ref"]]["kind"] == "semantic_contract", f"invalid library owner: {library_id}")
        require(row["class"] in allowed_library_classes, f"invalid library class: {library_id}")
        require(row["effect_boundary"] in allowed_effects, f"invalid effect boundary: {library_id}")
        for field in ("types", "operations", "decisions", "invariants", "refusals"):
            require(bool(row.get(field)), f"library {library_id} lacks {field}")
        for capability_ref in row["provides"]:
            require(capability_ref in artifacts and artifacts[capability_ref]["kind"] == "capability", f"library {library_id} provides unknown capability {capability_ref}")
        for dependency in row["dependencies"]:
            require(dependency in libraries, f"library {library_id} has unknown dependency {dependency}")
            graph[library_id].append(dependency)
        for ref in row["evidence_refs"]:
            all_evidence_refs.append((library_id, ref))

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            errors.append(f"library dependency cycle at {node}")
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

    decisions = {row["decision_id"]: row for row in by_section["boundary_decisions"]}
    decisions_by_subject: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for decision_id, row in decisions.items():
        require(row["subject_ref"] in node_ids, f"decision has unknown subject: {decision_id}")
        decisions_by_subject[row["subject_ref"]].append(row)
        require(bool(row.get("rationale")), f"decision lacks rationale: {decision_id}")
        for ref in row["evidence_refs"]:
            all_evidence_refs.append((decision_id, ref))
        if "split_test" in row:
            split = row["split_test"]
            require(set(split) == AXES, f"decision has incomplete split test: {decision_id}")
            total = 0
            for axis, result in split.items():
                require(result.get("score") in {0, 1, 2}, f"invalid {axis} score: {decision_id}")
                require(bool(result.get("evidence_refs")), f"unevidenced {axis} score: {decision_id}")
                total += result.get("score", 0)
                for ref in result.get("evidence_refs", []):
                    all_evidence_refs.append((decision_id, ref))
            if row["disposition"] == "presumptive_product":
                require(13 <= total <= 16, f"presumptive product score outside 13-16: {decision_id}={total}")
            if row["disposition"].startswith("strong_product_candidate"):
                require(17 <= total <= 20, f"strong product score outside 17-20: {decision_id}={total}")

    product_ids = {artifact_id for artifact_id, row in artifacts.items() if row["kind"] == "product"}
    require(all(decisions_by_subject[product_id] for product_id in product_ids), "a product lacks an explicit boundary decision")
    require(len(product_ids) == 8, "movement slice must expose exactly eight candidate product promises")
    required_products = {
        "product.source_connectivity_control", "product.source_replication_cdc",
        "product.ingestion_delivery", "product.pipeline_orchestration",
        "product.dataflow_execution", "product.batch_transform_build",
        "product.event_streaming", "product.operational_activation",
    }
    require(product_ids == required_products, "movement candidate product identity set drifted")
    for library_id, row in libraries.items():
        require(all(ref in product_ids for ref in row["product_refs"]), f"library has invalid product attribution: {library_id}")
    for decision_id in (
        "decision.movement.connector_sku", "decision.movement.exactly_once",
        "decision.movement.solution_pack", "decision.movement.ai_prefix",
    ):
        require(decision_id in decisions, f"missing constitutional decision {decision_id}")

    ownership = {row["meaning_id"]: row for row in by_section["ownership"]}
    require(len(ownership) >= 24, "semantic ownership slice is too small")
    for meaning_id, row in ownership.items():
        require(row["owner_ref"] in artifacts, f"meaning owner missing: {meaning_id}")
        require(bool(row.get("invariant")), f"meaning invariant missing: {meaning_id}")
        require(row["owner_ref"] not in row["must_not_be_owned_by"], f"owner appears in exclusion list: {meaning_id}")
        for ref in row["must_not_be_owned_by"]:
            require(ref in artifacts, f"unknown excluded owner {ref} for {meaning_id}")

    for row in by_section["relations"]:
        require(row["from_ref"] in node_ids, f"unknown relation source: {row['relation_id']}")
        require(row["to_ref"] in node_ids, f"unknown relation target: {row['relation_id']}")
        require(row["predicate"] in metamodel["relation_predicates"], f"unknown relation predicate: {row['relation_id']}")
        require(row["binding_phase"] in metamodel["binding_phases"], f"unknown binding phase: {row['relation_id']}")
        if row["predicate"] == "packages":
            require(artifacts[row["from_ref"]]["kind"] == "suite", f"only suite may package: {row['relation_id']}")

    for row in by_section["requirements"]:
        require(row["consumer_ref"] in node_ids, f"unknown requirement consumer: {row['requirement_id']}")
        require(row["capability_ref"] in artifacts, f"unknown required capability: {row['requirement_id']}")
        require(artifacts[row["capability_ref"]]["kind"] in {"capability", "neighboring_product"}, f"invalid requirement kind: {row['requirement_id']}")
        require(row["status"] == "unbound", f"requirement dishonestly bound: {row['requirement_id']}")
        require(row["minimum_qualified_offers"] >= 1, f"invalid offer minimum: {row['requirement_id']}")
    provided_by_product: dict[str, set[str]] = defaultdict(set)
    for row in libraries.values():
        for product_ref in row["product_refs"]:
            provided_by_product[product_ref].update(row["provides"])
    for product_ref in product_ids:
        required = {
            row["capability_ref"]
            for row in by_section["requirements"]
            if row["consumer_ref"] == product_ref
        }
        require(required <= provided_by_product[product_ref], f"uncovered product capabilities: {product_ref}:{sorted(required - provided_by_product[product_ref])}")
    for row in by_section["offers"]:
        require(row["provider_ref"] in artifacts, f"unknown offer provider: {row['offer_id']}")
        require(artifacts[row["provider_ref"]]["kind"] in {"implementation", "provider_class"}, f"invalid offer provider kind: {row['offer_id']}")
        for ref in row["capability_refs"]:
            require(ref in artifacts and artifacts[ref]["kind"] == "capability", f"unknown offered capability {ref}: {row['offer_id']}")
        require(row["qualified_implementation_count"] == 0, f"unverified offer promoted: {row['offer_id']}")
        require(row["portable"] is False, f"portable offer claimed without two qualifications: {row['offer_id']}")
        for ref in row["evidence_refs"]:
            all_evidence_refs.append((row["offer_id"], ref))

    crosswalks = by_section["crosswalks"]
    require(len({row["legacy_ref"] for row in crosswalks}) == len(crosswalks), "duplicate legacy crosswalk")
    for row in crosswalks:
        require(bool(row["canonical_refs"]), f"empty canonical crosswalk: {row['legacy_ref']}")
        for ref in row["canonical_refs"]:
            require(ref in node_ids, f"crosswalk target missing {ref}: {row['legacy_ref']}")
    crosswalk_by_legacy = {row["legacy_ref"]: row for row in crosswalks}
    require(crosswalk_by_legacy["candidate.product.connector_brand_sku"]["disposition"] == "merge_into_provider_offer", "connector SKU was not demoted")
    require("candidate.product.ingestion_delivery" in crosswalk_by_legacy, "missing ingestion global crosswalk")
    require("pattern.reverse_etl" in crosswalk_by_legacy, "missing activation pattern/product split")

    negative_ids = {row["test_id"] for row in by_section["negative_tests"]}
    required_negatives = {
        "negative.pipeline_is_product", "negative.connector_is_product",
        "negative.source_cursor_is_offset", "negative.task_success_is_delivery",
        "negative.checkpoint_is_exactly_once", "negative.activation_without_authority",
        "negative.pipeline_is_solution_pack", "negative.ai_pipeline",
    }
    require(required_negatives <= negative_ids, "missing constitutional negative tests")

    compiler_registry = HERE.parents[2] / "domain_atlas/compiler/library_registry/library-contributions.jsonl"
    compiler_libraries = {row["library_id"] for row in load_jsonl(compiler_registry)}
    maps = {row["binding_map_id"]: row for row in by_section["binding_maps"]}
    gaps = {row["gap_id"]: row for row in by_section["binding_gaps"]}
    require(len(maps) == len(libraries) == 18, "every movement library needs exactly one compiler map")
    require({row["abstract_library_ref"] for row in maps.values()} == set(libraries), "movement compiler map coverage drift")
    require(not gaps, "movement must have no unresolved exact compiler binding gap")
    require(
        maps["binding.movement.transform_manifest"]["concrete_library_refs"]
        == ["library.transform_definition.compiler", "library.transform_selection.closure"],
        "transform manifest must split into exact definition and selection contracts",
    )
    require(
        maps["binding.movement.materialization"]["concrete_library_refs"]
        == ["library.materialization.incremental_planner", "library.materialization.mutation_protocol", "library.transform_build.evidence"],
        "materialization must split into exact planning, mutation and evidence contracts",
    )
    require(
        maps["binding.movement.activation_mapping"]["concrete_library_refs"]
        == ["library.activation.destination_profile.compiler", "library.activation.mapping.compiler", "library.activation.mapping.evaluator"],
        "activation mapping must split into exact destination-profile, plan-compiler and pure evaluator contracts",
    )
    for map_id, row in maps.items():
        library = libraries[row["abstract_library_ref"]]
        require(row.get("product_refs") == library.get("product_refs"), f"map product attribution drift: {map_id}")
        require(row["portable_offer"] is False, f"map claims portability: {map_id}")
        if row["compiler_disposition"] == "missing_exact_compiler_library_contract":
            require(not row["concrete_library_refs"] and row.get("gap_ref") in gaps, f"missing map lacks exact gap: {map_id}")
        else:
            require(row["compiler_disposition"] == "structurally_projected_unqualified", f"unknown map disposition: {map_id}")
            require(bool(row["concrete_library_refs"]) and row.get("gap_ref") is None, f"structural map is incomplete: {map_id}")
            require(all(ref in compiler_libraries for ref in row["concrete_library_refs"]), f"map references unknown compiler library: {map_id}")

    dossiers = {row["product_ref"]: row for row in by_section["ddd_dossiers"]}
    require(set(dossiers) == product_ids and len(dossiers) == 8, "every movement product needs exactly one DDD dossier")
    required_ddd_fields = {
        "domain_vision_statement", "subdomain_classification", "bounded_context_boundary",
        "ubiquitous_language_policy", "context_map", "anti_corruption_layers",
        "published_language", "value_objects", "entities", "aggregates", "aggregate_roots",
        "aggregate_invariants", "commands", "domain_events", "refusal_failure_catalog",
        "domain_services", "application_services", "repositories", "factories",
        "specifications", "state_machine", "policies_and_reactions",
        "sagas_and_process_managers", "read_models_and_projections",
        "integration_event_policy", "concurrency_and_idempotency", "time_model",
        "event_storming_swimlanes", "nonfunctional_laws",
    }
    for product_ref, row in dossiers.items():
        ddd = row.get("strategic_and_tactical_ddd", {})
        require(required_ddd_fields <= set(ddd), f"incomplete movement DDD dossier: {product_ref}")
        require(all(ddd.get(field) not in (None, [], {}) for field in required_ddd_fields), f"empty movement DDD field: {product_ref}")
        require(row.get("status") == "candidate_not_ratified", f"movement DDD prematurely ratified: {product_ref}")

    for subject, ref in all_evidence_refs:
        require(ref in evidence, f"unknown evidence {ref} referenced by {subject}")

    require(manifest["derived"]["portable_offers"] == 0, "manifest claims portable offers")
    require(manifest["derived"]["qualified_offers"] == 0, "manifest claims qualified offers")
    require(manifest["derived"]["unbound_requirements"] == len(by_section["requirements"]), "not every requirement remains honestly unbound")

    if errors:
        print(f"FAIL movement adjudication: {len(errors)} error(s)")
        for error in errors[:100]:
            print(f"- {error}")
        if len(errors) > 100:
            print(f"- ... {len(errors) - 100} more")
        return 1

    print(
        "PASS movement adjudication: "
        f"{len(evidence)} sources; {len(artifacts)} artifacts; {len(product_ids)} product candidates; "
        f"{len(libraries)} library contracts; 8 full DDD dossiers; {len(ownership)} owned meanings; "
        f"{len(by_section['requirements'])} unbound requirements; "
        f"{len(by_section['offers'])} unqualified offers; {len(maps)} compiler maps; "
        f"{len(gaps)} exact compiler gaps; {len(crosswalks)} legacy crosswalks"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
