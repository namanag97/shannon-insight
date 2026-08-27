#!/usr/bin/env python3
"""Validate the governance-semantics product adjudication bundle."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from build_bundle import HERE, OUTPUTS, SECTIONS, load_source, materialize
from enrich_source import PRODUCTS, source_bytes as enriched_source_bytes
from governance_product_enrichment import (
    DDD_FIELDS as GOVERNANCE_DDD_FIELDS,
    LIBRARY_SPECS as GOVERNANCE_LIBRARY_SPECS,
    PRODUCTS as GOVERNANCE_PRODUCTS,
    PRODUCT_FIELDS as GOVERNANCE_PRODUCT_FIELDS,
    local_library as governance_local_library,
)
from lineage_enrichment import (
    DDD_FIELDS as LINEAGE_DDD_FIELDS,
    LIBRARY_SPECS as LINEAGE_LIBRARY_SPECS,
    PRODUCT as LINEAGE_PRODUCT,
    PRODUCT_FIELDS as LINEAGE_PRODUCT_FIELDS,
)
from master_reference_split_enrichment import (
    MASTER_KEYS,
    MASTER_OWNER,
    MASTER_PRODUCT,
    OLD_OWNER,
    OLD_PRODUCT,
    REFERENCE_KEYS,
    REFERENCE_OWNER,
    REFERENCE_PRODUCT,
)


ID = re.compile(r"^[a-z][a-z0-9_]*(?:[.-][a-z0-9_]+)+$")
AXES = {"user", "job", "adoption", "semantics", "authority", "lifecycle", "operation", "economics", "interface", "market_evidence"}


def rows(name: str) -> list[dict]:
    return [json.loads(line) for line in (HERE / name).read_text(encoding="utf-8").splitlines() if line.strip()]


def rows_from(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def identity(row: dict) -> str:
    for key in ("source_id", "artifact_id", "decision_id", "meaning_id", "library_id", "requirement_id", "offer_id", "relation_id", "legacy_ref", "test_id", "binding_map_id", "gap_id", "dossier_id", "kind"):
        if key in row:
            return str(row[key])
    return "<missing>"


def main() -> int:
    errors: list[str] = []

    def require(ok: bool, message: str) -> None:
        if not ok:
            errors.append(message)

    source = load_source()
    require((HERE / "source.json").read_bytes() == enriched_source_bytes(), "source differs from canonical quality/reconciliation split enrichment")
    payloads, expected_manifest = materialize(source)
    manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
    metamodel = json.loads((HERE / "metamodel.json").read_text(encoding="utf-8"))
    require(manifest == expected_manifest, "manifest differs from deterministic projection")
    for filename, content in payloads.items():
        path = HERE / filename
        require(path.is_file() and path.read_bytes() == content, f"missing or stale {filename}")
    for filename, expected in manifest.get("file_sha256", {}).items():
        path = HERE / filename
        if path.is_file():
            require(hashlib.sha256(path.read_bytes()).hexdigest() == expected, f"digest mismatch {filename}")

    registry = rows("registry.jsonl")
    require(Counter(row["record_kind"] for row in registry) == Counter(manifest["counts"]), "manifest counts differ")
    keys = [(row["record_kind"], identity(row)) for row in registry]
    require(len(keys) == len(set(keys)), "duplicate record identity")
    for row in registry:
        ident = identity(row)
        require(bool(re.fullmatch(r"^[a-z][a-z0-9_]*$", ident) if row["record_kind"] == "artifact_kind_definition" else ID.fullmatch(ident)), f"invalid identity {ident}")

    data = {section: rows(filename) for section, filename in OUTPUTS.items()}
    evidence = {row["source_id"]: row for row in data["sources"]}
    artifacts = {row["artifact_id"]: row for row in data["artifacts"]}
    libraries = {row["library_id"]: row for row in data["libraries"]}
    nodes = set(artifacts) | set(libraries)
    require(len(evidence) >= 20, "fewer than twenty primary/official sources")
    require(all(row.get("claim") and row.get("scope_limit") and row.get("uri", "").startswith("https://") for row in evidence.values()), "unscoped evidence")

    kinds = {row["kind"] for row in data["artifact_kinds"]}
    require(kinds == set(metamodel["artifact_kinds"]), "artifact-kind drift")
    for ident, row in artifacts.items():
        require(row["kind"] in kinds, f"unknown kind {ident}")
        require(all(ref in evidence for ref in row.get("evidence_refs", [])), f"unresolved evidence {ident}")
        if row["kind"] == "product":
            require(row["adoption_unit"] and row["operated"], f"product boundary flags missing {ident}")
        if row["kind"] in {"suite", "architecture_pattern"}:
            require(row.get("semantic_owner_ref") is None, f"suite/pattern claims meaning {ident}")
        owner = row.get("semantic_owner_ref")
        if owner:
            require(owner in artifacts and artifacts[owner]["kind"] == "semantic_contract", f"bad semantic owner {ident}")

    product_ids = {ident for ident, row in artifacts.items() if row["kind"] == "product"}
    expected_products = {
        "product.metadata_discovery", "product.business_glossary", "product.ontology_knowledge_model",
        "product.schema_registry", "product.data_contract_registry", MASTER_PRODUCT,
        REFERENCE_PRODUCT,
        "product.lineage_provenance", "product.data_quality_operations",
        "product.reconciliation_control_operations", "product.data_use_policy",
        "product.data_product_publication", "product.data_marketplace",
    }
    require(product_ids == expected_products, "governance product identity set drifted")

    decisions = {row["decision_id"]: row for row in data["boundary_decisions"]}
    decided_products = set()
    for ident, row in decisions.items():
        require(row["subject_ref"] in nodes, f"unknown decision subject {ident}")
        require(all(ref in evidence for ref in row["evidence_refs"]), f"unresolved decision evidence {ident}")
        if row["subject_ref"] in product_ids:
            decided_products.add(row["subject_ref"])
            require(set(row.get("split_test", {})) == AXES, f"incomplete split test {ident}")
            total = sum(axis.get("score", -1) for axis in row["split_test"].values())
            require(all(axis.get("score") in {0, 1, 2} and axis.get("evidence_refs") for axis in row["split_test"].values()), f"invalid split evidence {ident}")
            if row["disposition"] == "presumptive_product":
                require(13 <= total <= 16, f"presumptive score out of range {ident}={total}")
            else:
                require(17 <= total <= 20, f"strong score out of range {ident}={total}")
    require(decided_products == product_ids, "not every product is adjudicated")
    for ident in ("decision.governance.catalog_word", "decision.governance.schema_contract_split", "decision.governance.glossary_ontology_split", "decision.governance.ai_prefix", "decision.governance.quality_reconciliation_split"):
        require(ident in decisions, f"missing constitutional decision {ident}")

    replacement_product_ids = set(PRODUCTS)
    governance_product_ids = (set(GOVERNANCE_PRODUCTS.values()) - {OLD_PRODUCT}) | {
        MASTER_PRODUCT, REFERENCE_PRODUCT,
    }
    fully_modelled_product_ids = replacement_product_ids | governance_product_ids | {LINEAGE_PRODUCT}
    product_truth_fields = {
        "sovereign_question", "users", "harmed_parties", "jobs", "outcomes", "negative_mission",
        "lifecycle_states", "commands", "events", "invariants", "refusals", "automation_modality",
    }
    require(product_truth_fields == LINEAGE_PRODUCT_FIELDS == GOVERNANCE_PRODUCT_FIELDS, "product truth-field contract drift")
    for product_id in fully_modelled_product_ids:
        product = artifacts[product_id]
        require(all(product.get(field) not in (None, [], {}) for field in product_truth_fields), f"modelled product truth incomplete {product_id}")
        require(product["automation_modality"]["default"] == "DETERMINISTIC_CORE_ONLY", f"ambient model/agent default {product_id}")
        require("hard_work_law" in product["automation_modality"], f"automation replaced domain work {product_id}")
    require(not (OLD_PRODUCT_REFS := ({"product.quality_reconciliation", "semantic.quality_reconciliation"} & set(artifacts))), f"obsolete combined quality product remains: {sorted(OLD_PRODUCT_REFS)}")
    require(not ({OLD_PRODUCT, OLD_OWNER} & set(artifacts)), "obsolete combined master/reference boundary remains")

    graph: dict[str, list[str]] = defaultdict(list)
    for ident, row in libraries.items():
        require(row["owner_ref"] in artifacts and artifacts[row["owner_ref"]]["kind"] == "semantic_contract", f"bad library owner {ident}")
        for field in ("types", "operations", "decisions", "invariants", "refusals", "provides"):
            require(bool(row.get(field)), f"empty {field} {ident}")
        for ref in row["provides"]:
            require(ref in artifacts and artifacts[ref]["kind"] == "capability", f"bad capability {ident}:{ref}")
        for ref in row["dependencies"]:
            require(ref in libraries, f"unknown dependency {ident}:{ref}")
            graph[ident].append(ref)
        require(all(ref in evidence for ref in row["evidence_refs"]), f"unresolved library evidence {ident}")
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(node: str) -> None:
        if node in visiting:
            errors.append(f"library cycle {node}")
            return
        if node in visited:
            return
        visiting.add(node)
        for dep in graph[node]:
            visit(dep)
        visiting.remove(node)
        visited.add(node)
    for node in list(graph):
        visit(node)

    for row in data["ownership"]:
        require(row["owner_ref"] in artifacts and artifacts[row["owner_ref"]]["kind"] == "semantic_contract", f"bad meaning owner {row['meaning_id']}")
        require(row.get("invariant"), f"missing meaning invariant {row['meaning_id']}")
        require(all(ref in artifacts for ref in row["must_not_be_owned_by"]), f"bad excluded owner {row['meaning_id']}")
    for row in data["requirements"]:
        require(row["consumer_ref"] in nodes and row["capability_ref"] in artifacts, f"bad requirement {row['requirement_id']}")
        require(row["status"] == "unbound" and row["minimum_qualified_offers"] >= 1, f"dishonest requirement binding {row['requirement_id']}")
    for row in data["offers"]:
        require(row["provider_ref"] in artifacts and artifacts[row["provider_ref"]]["kind"] == "implementation", f"bad offer provider {row['offer_id']}")
        require(row["qualified_implementation_count"] == 0 and row["portable"] is False, f"unverified offer promoted {row['offer_id']}")
        require(all(ref in artifacts and artifacts[ref]["kind"] == "capability" for ref in row["capability_refs"]), f"bad offered capability {row['offer_id']}")
    for row in data["relations"]:
        require(row["from_ref"] in nodes and row["to_ref"] in nodes, f"bad relation refs {row['relation_id']}")
        require(row["predicate"] in metamodel["relation_predicates"] and row["binding_phase"] in metamodel["binding_phases"], f"bad relation semantics {row['relation_id']}")
    for row in data["crosswalks"]:
        require(all(ref in nodes for ref in row["canonical_refs"]), f"bad crosswalk {row['legacy_ref']}")

    compiler_root = HERE.parents[2] / "domain_atlas/compiler/library_registry"
    compiler_libraries = {row["library_id"] for row in rows_from(compiler_root / "library-contributions.jsonl")}
    compiler_requirements = {row["requirement_id"] for row in rows_from(compiler_root / "capability-requirements.jsonl")}
    compiler_offers = {row["offer_id"]: row for row in rows_from(compiler_root / "capability-offers.jsonl")}
    maps = {row["binding_map_id"]: row for row in data["binding_maps"]}
    gaps = {row["gap_id"]: row for row in data["binding_gaps"]}
    selected_libraries = {library_id for library_id in libraries if library_id.startswith("library.governance_qor.")}
    lineage_libraries = {spec["library_id"] for spec in LINEAGE_LIBRARY_SPECS}
    governance_libraries = set()
    for spec in GOVERNANCE_LIBRARY_SPECS:
        library_ref = governance_local_library(spec["product"], spec["key"])
        if spec["key"] in MASTER_KEYS:
            library_ref = library_ref.replace("governance_master", "governance_master_data")
        elif spec["key"] in REFERENCE_KEYS:
            library_ref = library_ref.replace("governance_master", "governance_reference_data")
        governance_libraries.add(library_ref)
    qor_maps = {map_id: row for map_id, row in maps.items() if set(row.get("product_refs", [])) & replacement_product_ids}
    lineage_maps = {map_id: row for map_id, row in maps.items() if LINEAGE_PRODUCT in row.get("product_refs", [])}
    governance_maps = {map_id: row for map_id, row in maps.items() if set(row.get("product_refs", [])) & governance_product_ids}
    require(len(selected_libraries) == len(qor_maps) == 33, "quality/reconciliation exact library-map count drift")
    require({row["abstract_library_ref"] for row in qor_maps.values()} == selected_libraries, "quality/reconciliation map coverage drift")
    require(len(lineage_libraries) == len(lineage_maps) == 11, "lineage product library-map count drift")
    require({row["abstract_library_ref"] for row in lineage_maps.values()} == lineage_libraries, "lineage map coverage drift")
    require(all(row["compiler_disposition"] == "structurally_projected_unqualified" and row.get("gap_ref") is None for row in lineage_maps.values()), "lineage maps are not all exact structural projections")
    require(len(governance_libraries) == len(governance_maps) == len(GOVERNANCE_LIBRARY_SPECS) == 56, "nine-product governance library-map count drift")
    require({row["abstract_library_ref"] for row in governance_maps.values()} == governance_libraries, "nine-product governance map coverage drift")
    require(len(maps) == 100 and len(gaps) == 0, "governance compiler map/gap total drift")
    exact_governance_maps = {map_id: row for map_id, row in governance_maps.items() if row["compiler_disposition"] == "structurally_projected_unqualified"}
    blocked_governance_maps = {map_id: row for map_id, row in governance_maps.items() if row["compiler_disposition"] == "blocked_typed_gap"}
    require(len(exact_governance_maps) == 56 and len(blocked_governance_maps) == 0, "nine-product governance exact projection count drift")
    require({row["gap_ref"] for row in blocked_governance_maps.values()} == set(gaps), "nine-product governance gap coverage drift")
    require({product for row in exact_governance_maps.values() for product in row["product_refs"]} == governance_product_ids, "exact governance projections do not cover every governed product")
    for map_id, row in maps.items():
        require(row.get("product_refs") == libraries[row["abstract_library_ref"]].get("product_refs"), f"map/library product attribution drift {map_id}")
        require(row["portable_offer"] is False, f"map overclaims portability {map_id}")
        if row["compiler_disposition"] == "blocked_typed_gap":
            require(not row["concrete_library_refs"] and not row["required_requirement_refs"] and not row["portable_offer_refs"], f"gap map has concrete binding {map_id}")
            require(row.get("gap_ref") in gaps, f"gap map lacks exact gap {map_id}")
            for candidate_ref in row.get("candidate_projection_refs", []):
                require(candidate_ref in compiler_libraries, f"unknown candidate compiler projection {map_id}:{candidate_ref}")
            continue
        require(row["compiler_disposition"] == "structurally_projected_unqualified" and row.get("gap_ref") is None, f"bad compiler disposition {map_id}")
        require(len(row["concrete_library_refs"]) == len(row["required_requirement_refs"]) == len(row["portable_offer_refs"]) >= 1, f"map cardinality drift {map_id}")
        for concrete_ref, requirement_ref, offer_ref in zip(row["concrete_library_refs"], row["required_requirement_refs"], row["portable_offer_refs"], strict=True):
            require(concrete_ref in compiler_libraries, f"unknown compiler library {map_id}:{concrete_ref}")
            require(requirement_ref in compiler_requirements, f"unknown compiler requirement {map_id}:{requirement_ref}")
            offer = compiler_offers.get(offer_ref)
            require(offer is not None and offer["portable"] is False and offer["observed_independent_qualified_implementations"] == 0, f"map references unproved or missing offer {map_id}:{offer_ref}")

    dossiers = {row["product_ref"]: row for row in data["ddd_dossiers"]}
    require(set(dossiers) == fully_modelled_product_ids and len(dossiers) == len(fully_modelled_product_ids), "every governance product requires one exact DDD dossier")
    required_ddd_fields = {
        "domain_vision_statement", "subdomain_classification", "bounded_context_boundary",
        "ubiquitous_language_policy", "context_map", "anti_corruption_layers", "published_language",
        "value_objects", "entities", "aggregates", "aggregate_roots", "aggregate_invariants",
        "commands", "domain_events", "refusal_failure_catalog", "domain_services",
        "application_services", "repositories", "factories", "specifications", "state_machine",
        "policies_and_reactions", "sagas_and_process_managers", "read_models_and_projections",
        "integration_event_policy", "concurrency_and_idempotency", "time_model",
        "event_storming_swimlanes", "nonfunctional_laws",
    }
    require(required_ddd_fields == LINEAGE_DDD_FIELDS == GOVERNANCE_DDD_FIELDS, "DDD field contract drift")
    for product_ref, dossier in dossiers.items():
        ddd = dossier.get("strategic_and_tactical_ddd", {})
        require(required_ddd_fields == set(ddd) and all(ddd.get(field) not in (None, [], {}) for field in required_ddd_fields), f"incomplete product DDD {product_ref}")
        require(dossier.get("status") == "candidate_not_ratified", f"product DDD prematurely ratified {product_ref}")
        require(any("removing every" in law.lower() and ("model" in law.lower() or "agent" in law.lower()) for law in ddd["nonfunctional_laws"]), f"model/agent removal law missing {product_ref}")

    requirements_by_product: dict[str, set[str]] = defaultdict(set)
    provided_by_product: dict[str, set[str]] = defaultdict(set)
    for row in data["requirements"]:
        if row["consumer_ref"] in fully_modelled_product_ids:
            requirements_by_product[row["consumer_ref"]].add(row["capability_ref"])
    for library in libraries.values():
        for product_ref in library.get("product_refs", []):
            provided_by_product[product_ref].update(library["provides"])
    for product_ref in fully_modelled_product_ids:
        require(requirements_by_product[product_ref] == provided_by_product[product_ref], f"product requirement/library coverage drift {product_ref}")
        governance_floor = sum(1 for spec in GOVERNANCE_LIBRARY_SPECS if GOVERNANCE_PRODUCTS[spec["product"]] == product_ref)
        if product_ref == MASTER_PRODUCT:
            governance_floor = len(MASTER_KEYS)
        elif product_ref == REFERENCE_PRODUCT:
            governance_floor = len(REFERENCE_KEYS)
        floor = 25 if product_ref == "product.data_quality_operations" else 11 if product_ref == LINEAGE_PRODUCT else governance_floor or 9
        require(len(requirements_by_product[product_ref]) >= floor, f"product decomposition too shallow {product_ref}")

    negative_ids = {row["test_id"] for row in data["negative_tests"]}
    require("negative.ai_prefix" in negative_ids, "missing model/agent negative twin")
    require({
        "negative.master_reference.combined_lifecycle",
        "negative.master_reference.resolution_identity",
        "negative.master_reference.golden_truth",
        "negative.master_reference.code_concept",
        "negative.master_reference.crosswalk_equivalence",
    } <= negative_ids, "master/reference split negative twins incomplete")
    split_crosswalk = next((row for row in data["crosswalks"] if row["legacy_ref"] == "candidate.product.master_reference_data"), None)
    require(split_crosswalk is not None and split_crosswalk["disposition"] == "split_without_compatibility_alias" and set(split_crosswalk["canonical_refs"]) == {MASTER_PRODUCT, REFERENCE_PRODUCT}, "master/reference split crosswalk missing or lossy")
    require(len(negative_ids) >= 15, "negative-test surface too small")
    require(manifest["derived"]["portable_offers"] == 0 and manifest["derived"]["qualified_offers"] == 0, "unearned portability or qualification")
    require(manifest["derived"]["unbound_requirements"] == len(data["requirements"]), "requirements not explicitly unbound")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"PASS governance semantics adjudication: {len(evidence)} sources; {len(artifacts)} artifacts; {len(product_ids)} product candidates; {len(dossiers)} full product DDD dossiers; {len(libraries)} library contracts; {len(maps)} compiler maps ({len(maps)-len(gaps)} exact structural, {len(gaps)} typed gaps); {len(data['ownership'])} owned meanings; {len(data['requirements'])} unbound requirements; {len(data['offers'])} unqualified offers; {len(data['crosswalks'])} legacy crosswalks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
