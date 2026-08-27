#!/usr/bin/env python3
"""Validate the lakehouse product/capability/library adjudication bundle."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_bundle import HERE, OUTPUTS, SECTIONS, canonical_json, load_source, materialize
from enrich_source import (
    DDD_IMPORT_SPECS,
    PRODUCT_LIBRARIES,
    REPO,
    SPECS,
    record_digest,
    source_bytes as enriched_source_bytes,
)


ID = re.compile(r"^[a-z][a-z0-9_]*(?:[.-][a-z0-9_]+)+$")
AXES = {
    "user", "job", "adoption", "semantics", "authority",
    "lifecycle", "operation", "economics", "interface", "market_evidence",
}
LIBRARY_REGISTRY = HERE.parents[2] / "domain_atlas" / "compiler" / "library_registry"


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
        "binding_id", "binding_map_id", "gap_id", "dossier_id", "kind",
        "delegation_id",
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
    source_file_bytes = (HERE / "source.json").read_bytes()
    require(bool(source_file_bytes), "source.json is empty")
    require(source_file_bytes == enriched_source_bytes(), "source.json differs from deterministic lakehouse enrichment")
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
        record_identity = identity(row)
        valid_identity = (
            bool(re.fullmatch(r"^[a-z][a-z0-9_]*$", record_identity))
            if row.get("record_kind") == "artifact_kind_definition"
            else bool(ID.fullmatch(record_identity))
        )
        require(valid_identity, f"invalid identity: {record_identity}")
        require(row.get("edition") == source["edition"], f"edition mismatch: {identity(row)}")

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

    require(len(evidence) >= 15, "fewer than 15 scoped primary/official evidence records")
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
    allowed_effects = {"pure_no_io", "pure_effect_intents", "effectful_runtime"}
    graph: dict[str, list[str]] = defaultdict(list)
    for library_id, row in libraries.items():
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

    for node in sorted(list(graph)):
        visit(node)

    decisions = {row["decision_id"]: row for row in by_section["boundary_decisions"]}
    decisions_by_subject = defaultdict(list)
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
            disposition = row["disposition"]
            if disposition == "presumptive_product":
                require(13 <= total <= 16, f"presumptive product score outside 13-16: {decision_id}={total}")
            if disposition.startswith("strong_product_candidate"):
                require(17 <= total <= 20, f"strong product score outside 17-20: {decision_id}={total}")

    product_ids = {artifact_id for artifact_id, row in artifacts.items() if row["kind"] == "product"}
    require(all(decisions_by_subject[product_id] for product_id in product_ids), "a product lacks an explicit boundary decision")
    require(len(product_ids) == 6, "lakehouse slice must expose exactly six candidate product promises after adjudication")
    require("decision.lakehouse.table_state" in decisions, "missing table-state product-collapse adjudication")
    require("decision.lakehouse.control_plane" in decisions, "missing control-plane merge adjudication")
    require("decision.lakehouse.solution_pack" in decisions, "missing horizontal/vertical adjudication")

    retained_product_ids = set(SPECS)
    require(retained_product_ids <= product_ids, "retained lakehouse product closure set drift")
    product_truth_fields = {
        "sovereign_question", "users", "harmed_parties", "jobs", "outcomes",
        "negative_mission", "lifecycle_states", "commands", "events", "invariants",
        "refusals", "automation_modality",
    }
    for product_id in retained_product_ids:
        product = artifacts[product_id]
        require(
            all(product.get(field) not in (None, [], {}) for field in product_truth_fields),
            f"retained product lacks complete local truth fields: {product_id}",
        )
        modality = product.get("automation_modality", {})
        require(modality.get("default") == "DETERMINISTIC_CORE_ONLY", f"ambient model/agent default: {product_id}")
        require("hard_work_law" in modality, f"automation replaced domain work: {product_id}")

    ownership = {row["meaning_id"]: row for row in by_section["ownership"]}
    require(len(ownership) >= 20, "semantic ownership slice is too small")
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
        require(row["status"] == "unbound", f"requirement dishonestly bound: {row['requirement_id']}")
        require(row["minimum_qualified_offers"] >= 1, f"invalid offer minimum: {row['requirement_id']}")
    for row in by_section["offers"]:
        require(row["provider_ref"] in artifacts, f"unknown offer provider: {row['offer_id']}")
        for ref in row["capability_refs"]:
            require(ref in artifacts, f"unknown offered capability {ref}: {row['offer_id']}")
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
    require(crosswalk_by_legacy["product.analytical_table_management"]["disposition"] == "split", "legacy table product was not split")
    require(crosswalk_by_legacy["product.lakehouse_control_plane"]["disposition"] == "merge_into_experience_capability", "legacy control plane was not merged")
    require(
        crosswalk_by_legacy["product.ingestion_delivery_service"] == {
            "canonical_refs": ["product.ingestion_delivery"],
            "disposition": "completed_rename",
            "edition": source["edition"],
            "legacy_ref": "product.ingestion_delivery_service",
            "record_kind": "legacy_crosswalk",
        },
        "lakehouse ingestion alias is not an exact completed rename",
    )
    require("product.ingestion_delivery_service" not in node_ids, "retired ingestion alias remains a live ontology node")

    compiler_libraries = {
        row["library_id"]: row
        for row in load_jsonl(LIBRARY_REGISTRY / "library-contributions.jsonl")
    }
    compiler_requirements = {
        row["requirement_id"]: row
        for row in load_jsonl(LIBRARY_REGISTRY / "capability-requirements.jsonl")
    }
    compiler_offers = {
        row["offer_id"]: row
        for row in load_jsonl(LIBRARY_REGISTRY / "capability-offers.jsonl")
    }
    compiler_bindings = by_section["compiler_library_bindings"]
    require(len(compiler_bindings) == 14, "exact lakehouse compiler binding count drift")
    require(
        {row["local_library_ref"] for row in compiler_bindings}
        == set(libraries),
        "exact compiler projections must cover every lakehouse library",
    )
    for row in compiler_bindings:
        require(row["local_library_ref"] in libraries, f"binding has unknown local library: {row['binding_id']}")
        require(row["status"] == "structurally_mapped_unqualified", f"binding claims qualification: {row['binding_id']}")
        require(row["portability_claim"] is False, f"binding claims portability: {row['binding_id']}")
        require(bool(row["exact_library_refs"]), f"binding has no exact compiler library: {row['binding_id']}")
        require(
            len(row["exact_library_refs"]) == len(row["required_requirement_refs"]) == len(row["portable_offer_refs"]),
            f"binding cardinalities differ: {row['binding_id']}",
        )
        require(not any(ref.startswith("library.mae.") for ref in row["exact_library_refs"]), f"AI extension entered lakehouse core: {row['binding_id']}")
        for library_ref, requirement_ref, offer_ref in zip(
            row["exact_library_refs"], row["required_requirement_refs"], row["portable_offer_refs"]
        ):
            require(library_ref in compiler_libraries, f"unknown exact compiler library {library_ref}: {row['binding_id']}")
            require(requirement_ref in compiler_requirements, f"unknown compiler requirement {requirement_ref}: {row['binding_id']}")
            require(offer_ref in compiler_offers, f"unknown compiler offer {offer_ref}: {row['binding_id']}")
            if requirement_ref in compiler_requirements:
                require(compiler_requirements[requirement_ref]["subject_ref"] == library_ref, f"requirement/library mismatch: {row['binding_id']}")
            if offer_ref in compiler_offers:
                require(compiler_offers[offer_ref]["subject_ref"] == library_ref, f"offer/library mismatch: {row['binding_id']}")
                require(compiler_offers[offer_ref]["portable"] is False, f"unproved portable offer: {row['binding_id']}")
                require(compiler_offers[offer_ref]["observed_independent_qualified_implementations"] == 0, f"invented qualified implementation: {row['binding_id']}")
    maintenance_binding = next(row for row in compiler_bindings if row["local_library_ref"] == "library.maintenance_plan")
    require(
        set(maintenance_binding["exact_library_refs"]) == {
            "library.persistence.compaction_planner",
            "library.persistence.clustering_planner",
            "library.persistence.reachability_gc",
        },
        "maintenance plan did not decompose physical rewrites from destructive reachability policy",
    )

    maps = {row["binding_map_id"]: row for row in by_section["binding_maps"]}
    gaps = {row["gap_id"]: row for row in by_section["binding_gaps"]}
    require(len(maps) == len(libraries) == 14, "every lakehouse library needs exactly one normalized compiler map")
    require({row["abstract_library_ref"] for row in maps.values()} == set(libraries), "normalized compiler map coverage drift")
    require(not gaps, "lakehouse retains an exact compiler binding gap")
    compiler_binding_by_library = {row["local_library_ref"]: row for row in compiler_bindings}
    for map_id, row in maps.items():
        library_ref = row["abstract_library_ref"]
        library = libraries[library_ref]
        require(row.get("product_refs", []) == library.get("product_refs", []), f"map product attribution drift: {map_id}")
        require(row["portable_offer"] is False, f"normalized map claims portability: {map_id}")
        require(row["compiler_disposition"] == "structurally_projected_unqualified", f"unknown map disposition: {map_id}")
        require(row.get("gap_ref") is None and bool(row["concrete_library_refs"]), f"structural map incomplete: {map_id}")
        legacy = compiler_binding_by_library.get(library_ref)
        require(legacy is not None, f"normalized map lacks exact legacy projection: {map_id}")
        if legacy:
            require(row["concrete_library_refs"] == legacy["exact_library_refs"], f"exact library refs drift: {map_id}")
            require(row["required_requirement_refs"] == legacy["required_requirement_refs"], f"compiler requirement refs drift: {map_id}")
            require(row["portable_offer_refs"] == legacy["portable_offer_refs"], f"compiler offer refs drift: {map_id}")

    expected_product_libraries = {key: sorted(value) for key, value in PRODUCT_LIBRARIES.items()}
    observed_product_libraries = {
        library_id: sorted(row.get("product_refs", []))
        for library_id, row in libraries.items()
        if row.get("product_refs")
    }
    require(observed_product_libraries == expected_product_libraries, "lakehouse product-library attribution drift")

    requirements_by_product: dict[str, set[str]] = defaultdict(set)
    for row in by_section["requirements"]:
        if row["consumer_ref"] in retained_product_ids:
            requirements_by_product[row["consumer_ref"]].add(row["capability_ref"])
    provided_by_product: dict[str, set[str]] = defaultdict(set)
    for library in libraries.values():
        for product_ref in library.get("product_refs", []):
            provided_by_product[product_ref].update(library["provides"])
    expected_internal = {
        "product.managed_lakehouse_experience": {"capability.environment_reconciliation"},
        "product.catalog_service": {"capability.catalog_namespace_registry", "capability.catalog_commit_coordination", "capability.credential_vending"},
        "product.managed_table_maintenance": {"capability.table_maintenance_plan", "capability.table_compaction", "capability.table_clustering", "capability.table_snapshot_expiry"},
        "product.data_sharing_exchange": {"capability.data_sharing"},
    }
    for product_ref, expected in expected_internal.items():
        owner_ref = artifacts[product_ref]["semantic_owner_ref"]
        internal = {
            capability_ref for capability_ref in requirements_by_product[product_ref]
            if artifacts[capability_ref].get("semantic_owner_ref") == owner_ref
        }
        require(internal == expected, f"internal capability requirement boundary drift: {product_ref}")
        require(expected <= provided_by_product[product_ref], f"product library coverage gap: {product_ref}")

    dossiers = {row["product_ref"]: row for row in by_section["ddd_dossiers"]}
    require(set(dossiers) == retained_product_ids and len(dossiers) == 4, "the four retained lakehouse products need exact DDD dossiers")
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
        require(required_ddd_fields <= set(ddd), f"incomplete lakehouse DDD dossier: {product_ref}")
        require(all(ddd.get(field) not in (None, [], {}) for field in required_ddd_fields), f"empty lakehouse DDD field: {product_ref}")
        require(row.get("status") == "candidate_not_ratified", f"lakehouse DDD prematurely ratified: {product_ref}")
        boundary = ddd.get("bounded_context_boundary", {})
        require(bool(boundary.get("inside")) and bool(boundary.get("outside")), f"lakehouse boundary lacks positive/negative scope: {product_ref}")
        require(any("removing every model" in law for law in ddd.get("nonfunctional_laws", [])), f"model/agent removal law missing: {product_ref}")

    delegations = {row["imported_product_ref"]: row for row in by_section["ddd_delegations"]}
    imported_product_ids = product_ids - retained_product_ids
    require(set(delegations) == imported_product_ids == set(DDD_IMPORT_SPECS), "lakehouse imported-product DDD delegation coverage drift")
    for product_ref, delegation in delegations.items():
        spec = DDD_IMPORT_SPECS[product_ref]
        bundle_dir = REPO / "research/product_ontology/adjudications" / spec["bundle"]
        dossier_path = bundle_dir / "product-ddd-dossiers.jsonl"
        maps_path = bundle_dir / "product-library-binding-maps.jsonl"
        authoritative = next(row for row in load_jsonl(dossier_path) if row["dossier_id"] == spec["dossier_id"])
        binding_maps = sorted(
            (row for row in load_jsonl(maps_path) if product_ref in row.get("product_refs", [])),
            key=lambda row: row["binding_map_id"],
        )
        require(authoritative["product_ref"] == product_ref, f"delegated dossier owns another product: {product_ref}")
        require(delegation["authoritative_bundle"] == spec["bundle"], f"delegated bundle drift: {product_ref}")
        require(delegation["authoritative_dossier_ref"] == authoritative["dossier_id"], f"delegated dossier ref drift: {product_ref}")
        require(delegation["authoritative_dossier_digest"] == record_digest(authoritative), f"delegated dossier digest stale: {product_ref}")
        require(delegation["imported_binding_map_refs"] == [row["binding_map_id"] for row in binding_maps], f"delegated binding maps drift: {product_ref}")
        require(delegation["imported_binding_map_digests"] == [record_digest(row) for row in binding_maps], f"delegated binding map digests stale: {product_ref}")
        require(delegation["local_redefinition_forbidden"] is True, f"delegation permits local product redefinition: {product_ref}")
        require(delegation["status"] == "candidate_not_ratified" and not delegation["completion_claim"], f"delegation claims authority: {product_ref}")

    negative_ids = {row["test_id"] for row in by_section["negative_tests"]}
    required_negatives = {
        "negative.lakehouse.label_is_product", "negative.table_format_is_product",
        "negative.translation_is_lossless", "negative.lakehouse_is_solution_pack",
        "negative.ai_prefix",
    }
    require(required_negatives <= negative_ids, "missing constitutional negative tests")

    for subject, ref in all_evidence_refs:
        require(ref in evidence, f"unknown evidence {ref} referenced by {subject}")

    require(len([row for row in artifacts.values() if row["kind"] == "standard" and row["semantic_owner_ref"] == "semantic.analytical_table_state"]) >= 3, "fewer than three table-format standards retained")
    require(manifest["derived"]["portable_offers"] == 0, "manifest claims portable offers")
    require(manifest["derived"]["qualified_offers"] == 0, "manifest claims qualified offers")
    require(manifest["derived"]["unbound_requirements"] == len(by_section["requirements"]), "not every requirement remains honestly unbound")

    if errors:
        print(f"FAIL lakehouse adjudication: {len(errors)} error(s)")
        for error in errors[:100]:
            print(f"- {error}")
        if len(errors) > 100:
            print(f"- ... {len(errors) - 100} more")
        return 1

    print(
        "PASS lakehouse adjudication: "
        f"{len(evidence)} sources; {len(artifacts)} artifacts; {len(product_ids)} product candidates; "
        f"{len(libraries)} library contracts; 4 local DDD dossiers + 2 exact DDD delegations; {len(ownership)} owned meanings; "
        f"{len(by_section['requirements'])} unbound requirements; "
        f"{len(by_section['offers'])} unqualified offers; {len(maps)} compiler maps; "
        f"{len(gaps)} exact compiler gap; {len(compiler_bindings)} exact compiler library bindings; "
        f"{len(crosswalks)} legacy crosswalks"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
