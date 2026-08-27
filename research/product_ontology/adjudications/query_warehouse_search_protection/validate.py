#!/usr/bin/env python3
"""Validate query, warehouse, search, cache, recovery and archive boundaries."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from build_bundle import HERE, OUTPUTS, load_source, materialize
from source_model import AXES, SOURCE, source_bytes


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def identity(row: dict) -> str:
    for key in ("source_id", "artifact_id", "decision_id", "meaning_id", "library_id", "requirement_id", "offer_id", "relation_id", "legacy_ref", "test_id", "binding_map_id", "gap_id", "dossier_id", "kind"):
        if key in row:
            return str(row[key])
    return "<missing>"


def main() -> int:
    errors: list[str] = []
    require = lambda ok, msg: None if ok else errors.append(msg)
    require(SOURCE.is_file() and SOURCE.read_bytes() == source_bytes(), "source.json differs from source_model.py")
    source = load_source()
    payloads, expected_manifest = materialize(source)
    manifest = json.loads((HERE / "manifest.json").read_text())
    require(manifest == expected_manifest, "manifest projection drift")
    for filename, content in payloads.items():
        require((HERE / filename).is_file() and (HERE / filename).read_bytes() == content, f"stale {filename}")
    for filename, digest in manifest.get("file_sha256", {}).items():
        if (HERE / filename).is_file():
            require(hashlib.sha256((HERE / filename).read_bytes()).hexdigest() == digest, f"digest mismatch {filename}")
    data = {section: rows(HERE / filename) for section, filename in OUTPUTS.items()}
    registry = rows(HERE / "registry.jsonl")
    require(Counter(row["record_kind"] for row in registry) == Counter(manifest["counts"]), "manifest counts differ")
    keys = [(row["record_kind"], identity(row)) for row in registry]
    require(len(keys) == len(set(keys)), "duplicate identity")

    evidence = {row["source_id"]: row for row in data["sources"]}
    artifacts = {row["artifact_id"]: row for row in data["artifacts"]}
    libraries = {row["library_id"]: row for row in data["libraries"]}
    nodes = set(artifacts) | set(libraries)
    require(len(evidence) >= 45, "source floor not met")
    require(all(row.get("claim") and row.get("scope_limit") and row.get("uri", "").startswith("https://") for row in evidence.values()), "unscoped evidence")
    for ident, row in artifacts.items():
        require(all(ref in evidence for ref in row.get("evidence_refs", [])), f"bad evidence {ident}")
        owner = row.get("semantic_owner_ref")
        if owner:
            require(owner in artifacts and artifacts[owner]["kind"] == "semantic_contract", f"bad owner {ident}")
        if row["kind"] == "product":
            require(row["adoption_unit"] and row["operated"], f"product flags {ident}")
        if row["kind"] in {"suite", "architecture_pattern"}:
            require(owner is None, f"pattern/suite owns meaning {ident}")

    products = {ident for ident, row in artifacts.items() if row["kind"] == "product"}
    expected_products = {
        "product.query_execution_service",
        "product.managed_warehouse_experience",
        "product.virtual_data_access",
        "product.search_index_service",
        "product.data_protection_recovery",
        "product.digital_preservation_archive",
    }
    require(products == expected_products, "product set drift")
    product_fields = {
        "sovereign_question", "users", "harmed_parties", "jobs", "outcomes", "negative_mission",
        "lifecycle_states", "commands", "events", "invariants", "refusals", "automation_modality",
    }
    for product in products:
        require(all(artifacts[product].get(field) not in (None, [], {}) for field in product_fields), f"incomplete product truth {product}")
    decisions = {row["decision_id"]: row for row in data["boundary_decisions"]}
    decided: set[str] = set()
    for ident, row in decisions.items():
        require(row["subject_ref"] in nodes, f"bad subject {ident}")
        require(all(ref in evidence for ref in row["evidence_refs"]), f"bad decision evidence {ident}")
        if row["subject_ref"] in products:
            decided.add(row["subject_ref"])
            require(set(row["split_test"]) == set(AXES), f"split axes {ident}")
            total = sum(cell["score"] for cell in row["split_test"].values())
            require(all(cell["score"] in {0, 1, 2} and cell["evidence_refs"] for cell in row["split_test"].values()), f"split cells {ident}")
            if row["disposition"] == "strong_product_candidate":
                require(17 <= total <= 20, f"strong score {ident}:{total}")
            else:
                require(row["disposition"] == "presumptive_product" and 13 <= total <= 16, f"presumptive score {ident}:{total}")
    require(decided == products, "unadjudicated product")
    critical_decisions = {
        "decision.federation.capability",
        "decision.operational.profile",
        "decision.cache.mechanism",
        "decision.vector.search",
        "decision.protection.archive_split",
        "decision.snapshot.mechanism",
        "decision.replication.mechanism",
        "decision.query.component_product",
        "decision.agent.optional",
    }
    require(critical_decisions.issubset(decisions), "critical boundary decision missing")

    graph: dict[str, list[str]] = defaultdict(list)
    for ident, row in libraries.items():
        require(row["owner_ref"] in artifacts and artifacts[row["owner_ref"]]["kind"] == "semantic_contract", f"library owner {ident}")
        for field in ("provides", "types", "operations", "decisions", "invariants", "refusals"):
            require(bool(row.get(field)), f"empty {field} {ident}")
        require("agent_or_model_output_is_never_semantic_authority" not in row["invariants"], f"ambient AI law leaked into deterministic library {ident}")
        require(len(row.get("product_refs", [])) == 1 and row["product_refs"][0] in products, f"missing product attribution {ident}")
        for ref in row["provides"]:
            require(ref in artifacts and artifacts[ref]["kind"] == "capability", f"bad capability {ident}:{ref}")
        for ref in row["dependencies"]:
            require(ref in libraries, f"bad dependency {ident}:{ref}")
            graph[ident].append(ref)
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

    for node in libraries:
        visit(node)

    for row in data["ownership"]:
        require(row["owner_ref"] in artifacts and artifacts[row["owner_ref"]]["kind"] == "semantic_contract", f"bad ownership {row['meaning_id']}")
    for row in data["requirements"]:
        require(row["consumer_ref"] in nodes and row["capability_ref"] in artifacts and row["status"] == "unbound", f"bad requirement {row['requirement_id']}")
    for row in data["offers"]:
        require(row["provider_ref"] in artifacts and artifacts[row["provider_ref"]]["kind"] == "implementation" and row["qualified_implementation_count"] == 0 and row["portable"] is False, f"bad offer {row['offer_id']}")
        require(all(ref in artifacts and artifacts[ref]["kind"] == "capability" for ref in row["capability_refs"]), f"bad offer capability {row['offer_id']}")
    for row in data["relations"]:
        require(row["from_ref"] in nodes and row["to_ref"] in nodes, f"bad relation {row['relation_id']}")
    for row in data["crosswalks"]:
        require(all(ref in nodes for ref in row["canonical_refs"]), f"bad crosswalk {row['legacy_ref']}")

    compiler_path = HERE.parents[2] / "domain_atlas/compiler/library_registry/library-contributions.jsonl"
    concrete = {row["library_id"]: row for row in rows(compiler_path)}
    maps = {row["binding_map_id"]: row for row in data["binding_maps"]}
    gaps = {row["gap_id"]: row for row in data["binding_gaps"]}
    require(len(maps) == len(libraries), "one map per library required")
    require({row["abstract_library_ref"] for row in maps.values()} == set(libraries), "map coverage")
    for ident, row in maps.items():
        require(all(ref in concrete for ref in row["concrete_library_refs"]), f"unknown compiler library {ident}")
        if row["compiler_disposition"] == "blocked_typed_gap":
            require(row.get("gap_ref") in gaps and not row["concrete_library_refs"], f"invalid gap map {ident}")
        else:
            require(row["compiler_disposition"] == "structurally_projected_unqualified" and row["concrete_library_refs"], f"invalid projected map {ident}")
        require(row["portable_offer"] is False, f"portable map {ident}")
        require(row.get("product_refs") == libraries[row["abstract_library_ref"]].get("product_refs"), f"map product attribution drift {ident}")
    expected_gaps: set[str] = set()
    require(set(gaps) == expected_gaps, "typed gap set drift")
    for ident, row in gaps.items():
        require(row.get("product_refs") == libraries[row["abstract_library_ref"]].get("product_refs"), f"gap product attribution drift {ident}")
    recovery_map = maps.get("binding.recovery.objectives", {})
    require(recovery_map.get("concrete_library_refs") == ["library.persistence.recovery_objectives"], "recovery objective contract projection missing")
    cache_fill_map = maps.get("binding.cache.stampede", {})
    require(cache_fill_map.get("concrete_library_refs") == ["library.persistence.cache_fill_coordination"], "cache fill coordination projection missing")
    virtual_relation_map = maps.get("binding.virtual.relation", {})
    require(virtual_relation_map.get("concrete_library_refs") == ["library.persistence.virtual_relation_identity"], "virtual relation identity projection missing")
    virtual_lifecycle_map = maps.get("binding.virtual.lifecycle", {})
    require(virtual_lifecycle_map.get("concrete_library_refs") == ["library.persistence.virtual_relation_lifecycle"], "virtual relation lifecycle projection missing")
    search_mutation_map = maps.get("binding.search.mutation", {})
    require(search_mutation_map.get("concrete_library_refs") == ["library.persistence.index_mutation"], "index mutation contract projection missing")
    search_visibility_map = maps.get("binding.search.visibility_cut", {})
    require(search_visibility_map.get("concrete_library_refs") == ["library.persistence.search_visibility"], "search visibility contract projection missing")
    global_laws = set(source["non_collapse_laws"])
    require(any("optional agent or model output" in law for law in global_laws), "global optional-extension authority law missing")
    require(any("removing every optional model/agent extension" in law for law in global_laws), "global extension-removal law missing")

    ddd_fields = {
        "domain_vision_statement", "subdomain_classification", "bounded_context_boundary",
        "ubiquitous_language_policy", "context_map", "anti_corruption_layers", "published_language",
        "value_objects", "entities", "aggregates", "aggregate_roots", "aggregate_invariants",
        "commands", "domain_events", "refusal_failure_catalog", "domain_services",
        "application_services", "repositories", "factories", "specifications", "state_machine",
        "policies_and_reactions", "sagas_and_process_managers", "read_models_and_projections",
        "integration_event_policy", "concurrency_and_idempotency", "time_model",
        "event_storming_swimlanes", "nonfunctional_laws",
    }
    dossiers = {row["product_ref"]: row for row in data["ddd_dossiers"]}
    require(set(dossiers) == products, "one product DDD per product required")
    for product, row in dossiers.items():
        ddd = row.get("strategic_and_tactical_ddd", {})
        require(set(ddd) == ddd_fields and all(ddd[field] not in (None, [], {}) for field in ddd_fields), f"incomplete DDD {product}")

    negative_ids = {row["test_id"] for row in data["negative_tests"]}
    require(len(negative_ids) >= 40, "negative-twin floor")
    critical_negatives = {
        "negative.federation_product", "negative.operational_product", "negative.vector_feature",
        "negative.cache_truth", "negative.snapshot_backup", "negative.backup_restorable",
        "negative.wal_archive", "negative.worm_archive", "negative.agent_core",
        "negative.agent_authority", "negative.ai_prefix",
    }
    require(critical_negatives.issubset(negative_ids), "critical negative twins missing")
    laws = set(source.get("non_collapse_laws", []))
    require(any("removing every optional model/agent extension" in law for law in laws), "deterministic-core removal law missing")
    require(manifest["derived"]["qualified_offers"] == 0 and manifest["derived"]["portable_offers"] == 0, "qualification fabricated")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"PASS query/warehouse/search/protection adjudication: {len(evidence)} sources; {len(artifacts)} artifacts; {len(products)} product candidates; {len(libraries)} library contracts; {len(data['ownership'])} owned meanings; {len(data['requirements'])} unbound requirements; {len(data['offers'])} unqualified offers; {len(maps)} compiler binding maps; {len(gaps)} typed binding gaps; {len(data['negative_tests'])} negative twins")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
