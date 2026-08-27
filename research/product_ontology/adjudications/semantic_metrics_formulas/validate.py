#!/usr/bin/env python3
"""Validate semantic metric/formula product boundaries and compiler projections."""

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
    require(len(evidence) >= 35, "source floor not met")
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
    require(products == {"product.semantic_metric_formula_service"}, "product set drift")
    decisions = {row["decision_id"]: row for row in data["boundary_decisions"]}
    product_decision = decisions.get("decision.smf.product")
    require(product_decision is not None, "product decision missing")
    if product_decision:
        require(product_decision["subject_ref"] in products, "bad product decision subject")
        require(set(product_decision["split_test"]) == set(AXES), "split axes")
        total = sum(cell["score"] for cell in product_decision["split_test"].values())
        require(product_decision["disposition"] == "strong_product_candidate" and 17 <= total <= 20, f"product score {total}")
    required_decisions = {
        "decision.smf.metric_store_bundle", "decision.smf.formula_engine",
        "decision.smf.registry_component", "decision.smf.query_component",
        "decision.smf.materialization_component", "decision.smf.definition_observation",
        "decision.smf.measure_metric_kpi", "decision.smf.agent_optional",
    }
    require(required_decisions.issubset(decisions), "critical decision missing")
    for ident, row in decisions.items():
        require(row["subject_ref"] in nodes, f"bad subject {ident}")
        require(all(ref in evidence for ref in row["evidence_refs"]), f"bad decision evidence {ident}")

    graph: dict[str, list[str]] = defaultdict(list)
    for ident, row in libraries.items():
        require(row.get("product_ref") == "product.semantic_metric_formula_service", f"library lacks exact product attribution {ident}")
        require(row["owner_ref"] in artifacts and artifacts[row["owner_ref"]]["kind"] == "semantic_contract", f"library owner {ident}")
        for field in ("provides", "types", "operations", "decisions", "invariants", "refusals"):
            require(bool(row.get(field)), f"empty {field} {ident}")
        require("generated_output_never_owns_metric_meaning_or_effect_authority" in row["invariants"], f"agent authority law absent {ident}")
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
        require(row["consumer_ref"] in products and row["capability_ref"] in artifacts and row["status"] == "unbound", f"bad requirement {row['requirement_id']}")
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
    require(len(libraries) == 24 and len(maps) == len(libraries), "24 libraries and one map per library required")
    require({row["abstract_library_ref"] for row in maps.values()} == set(libraries), "map coverage")
    for ident, row in maps.items():
        require(row.get("product_ref") == "product.semantic_metric_formula_service", f"map lacks exact product attribution {ident}")
        require(row["compiler_disposition"] == "structurally_projected_unqualified", f"bad map disposition {ident}")
        require(len(row["concrete_library_refs"]) == 1 and all(ref in concrete and ref.startswith("library.smf.") for ref in row["concrete_library_refs"]), f"unknown or non-SMF compiler library {ident}")
        require(row.get("gap_ref") is None and row["portable_offer"] is False, f"invalid map claim {ident}")
    require(not data["binding_gaps"], "structural binding gaps reappeared")
    require(len(data["semantic_gaps"]) >= 16 and all(row["blocking"] for row in data["semantic_gaps"]), "semantic gap set incomplete")
    require(all(row.get("product_ref") == "product.semantic_metric_formula_service" for row in data["semantic_gaps"]), "semantic gap lacks exact product attribution")

    dossiers = data["ddd_dossiers"]
    require(len(dossiers) == 1 and dossiers[0].get("product_ref") == "product.semantic_metric_formula_service", "exactly one product DDD dossier required")
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
    if dossiers:
        ddd = dossiers[0].get("strategic_and_tactical_ddd", {})
        require(required_ddd_fields <= set(ddd), "product DDD dossier lacks required strategic/tactical fields")
        require(all(ddd.get(field) not in (None, [], {}) for field in required_ddd_fields), "product DDD dossier contains empty required fields")
        require(dossiers[0].get("status") == "candidate_not_ratified", "DDD dossier prematurely ratified")

    negative_ids = {row["test_id"] for row in data["negative_tests"]}
    require(len(negative_ids) >= 40, "negative-twin floor")
    critical = {
        "negative.smf.definition_observation", "negative.smf.measure_metric",
        "negative.smf.join_relation", "negative.smf.additive_decomposable",
        "negative.smf.semantic_sql", "negative.smf.cache_policy",
        "negative.smf.telemetry_business", "negative.smf.agent_core",
        "negative.smf.agent_authority", "negative.smf.ai_prefix",
    }
    require(critical.issubset(negative_ids), "critical negative twins missing")
    laws = set(source.get("non_collapse_laws", []))
    require(any("removing all model/agent extensions" in law for law in laws), "deterministic-core removal law missing")
    require(manifest["derived"]["qualified_offers"] == 0 and manifest["derived"]["portable_offers"] == 0, "qualification fabricated")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"PASS semantic metric/formula adjudication: {len(evidence)} sources; {len(artifacts)} artifacts; {len(products)} product candidate; 1 full DDD dossier; {len(libraries)} library contracts; {len(data['ownership'])} owned meanings; {len(data['requirements'])} unbound requirements; {len(data['offers'])} unqualified offers; {len(maps)} compiler maps; {len(data['semantic_gaps'])} semantic gaps; {len(data['negative_tests'])} negative twins")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
