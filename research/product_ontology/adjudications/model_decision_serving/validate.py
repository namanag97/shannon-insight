#!/usr/bin/env python3
"""Validate model/feature/inference/decision product adjudication."""

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

    evidence = {r["source_id"]: r for r in data["sources"]}
    artifacts = {r["artifact_id"]: r for r in data["artifacts"]}
    libraries = {r["library_id"]: r for r in data["libraries"]}
    nodes = set(artifacts) | set(libraries)
    require(len(evidence) >= 35, "source floor not met")
    require(all(r.get("claim") and r.get("scope_limit") and r.get("uri", "").startswith("https://") for r in evidence.values()), "unscoped evidence")
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
    expected_products = {"product.model_lifecycle", "product.feature_platform", "product.online_inference", "product.model_assurance", "product.decision_automation", "product.optional_model_extension"}
    require(products == expected_products, "product set drift")
    product_fields = {
        "sovereign_question", "users", "harmed_parties", "jobs", "outcomes", "negative_mission",
        "lifecycle_states", "commands", "events", "invariants", "refusals", "automation_modality",
    }
    for product in products:
        require(all(artifacts[product].get(field) not in (None, [], {}) for field in product_fields), f"incomplete product truth {product}")
    decisions = {r["decision_id"]: r for r in data["boundary_decisions"]}
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
    for ident in {"decision.model.vector_feature_split", "decision.model.registry_component", "decision.model.training_runtime", "decision.model.batch_scoring", "decision.model.prediction_decision", "decision.model.agent_authority"}:
        require(ident in decisions, f"missing decision {ident}")

    graph: dict[str, list[str]] = defaultdict(list)
    for ident, row in libraries.items():
        require(row["owner_ref"] in artifacts and artifacts[row["owner_ref"]]["kind"] == "semantic_contract", f"library owner {ident}")
        for field in ("provides", "types", "operations", "decisions", "invariants", "refusals"):
            require(bool(row.get(field)), f"empty {field} {ident}")
        for ref in row["provides"]:
            require(ref in artifacts and artifacts[ref]["kind"] == "capability", f"bad capability {ident}:{ref}")
        for ref in row["dependencies"]:
            require(ref in libraries, f"bad dependency {ident}:{ref}")
            graph[ident].append(ref)
        if ident != "library.model.batch_scoring_composition":
            require(len(row.get("product_refs", [])) == 1 and row["product_refs"][0] in products, f"missing product attribution {ident}")
        else:
            require(not row.get("product_refs"), "batch composition incorrectly attributed to product")
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
    for row in data["relations"]:
        require(row["from_ref"] in nodes and row["to_ref"] in nodes, f"bad relation {row['relation_id']}")
    for row in data["crosswalks"]:
        require(all(ref in nodes for ref in row["canonical_refs"]), f"bad crosswalk {row['legacy_ref']}")

    compiler_path = HERE.parents[2] / "domain_atlas/compiler/library_registry/library-contributions.jsonl"
    concrete = {r["library_id"]: r for r in rows(compiler_path)}
    maps = {r["binding_map_id"]: r for r in data["binding_maps"]}
    gaps = {r["gap_id"]: r for r in data["binding_gaps"]}
    require(len(maps) == len(libraries), "one map per library required")
    require({r["abstract_library_ref"] for r in maps.values()} == set(libraries), "map coverage")
    for ident, row in maps.items():
        require(all(ref in concrete for ref in row["concrete_library_refs"]), f"unknown compiler library {ident}")
        if row["compiler_disposition"] == "blocked_typed_gap":
            require(row.get("gap_ref") in gaps and not row["concrete_library_refs"], f"invalid gap map {ident}")
        else:
            require(row["compiler_disposition"] == "structurally_projected_unqualified" and row["concrete_library_refs"], f"invalid projected map {ident}")
        require(row["portable_offer"] is False, f"portable map {ident}")
        local = row["abstract_library_ref"]
        if local != "library.model.batch_scoring_composition":
            require(row.get("product_refs") == libraries[local].get("product_refs"), f"binding product attribution drift {ident}")
    require(not gaps, "model/decision slice must have no unresolved exact compiler binding gaps")
    for ident, row in gaps.items():
        local = row["abstract_library_ref"]
        require(row.get("product_refs") == libraries[local].get("product_refs"), f"gap product attribution drift {ident}")

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

    negative_ids = {r["test_id"] for r in data["negative_tests"]}
    require(len(negative_ids) >= 30, "negative-twin floor")
    require({"negative.prediction_decision", "negative.decision_authority", "negative.agent_core", "negative.ai_prefix", "negative.feature_vector"}.issubset(negative_ids), "critical negative twins missing")
    require(manifest["derived"]["qualified_offers"] == 0 and manifest["derived"]["portable_offers"] == 0, "qualification fabricated")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"PASS model/decision adjudication: {len(evidence)} sources; {len(artifacts)} artifacts; {len(products)} product candidates; {len(libraries)} library contracts; {len(data['ownership'])} owned meanings; {len(data['requirements'])} unbound requirements; {len(data['offers'])} unqualified offers; {len(maps)} compiler binding maps; {len(gaps)} typed binding gaps; {len(data['crosswalks'])} legacy crosswalks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
