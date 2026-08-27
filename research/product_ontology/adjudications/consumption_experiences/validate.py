#!/usr/bin/env python3
"""Validate the consumption-experience product adjudication."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from build_bundle import HERE, OUTPUTS, load_source, materialize
from source_model import SOURCE, source_bytes


ID = re.compile(r"^[a-z][a-z0-9_]*(?:[.-][a-z0-9_]+)+$")
AXES = {"user", "job", "adoption", "semantics", "authority", "lifecycle", "operation", "economics", "interface", "market_evidence"}


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def identity(row: dict) -> str:
    for key in ("source_id", "artifact_id", "decision_id", "meaning_id", "library_id", "requirement_id", "offer_id", "relation_id", "legacy_ref", "test_id", "binding_map_id", "gap_id", "dossier_id", "kind"):
        if key in row:
            return str(row[key])
    return "<missing>"


def main() -> int:
    errors: list[str] = []
    require = lambda ok, message: None if ok else errors.append(message)
    require(SOURCE.is_file() and SOURCE.read_bytes() == source_bytes(), "source.json differs from canonical source_model.py")
    source = load_source()
    payloads, expected_manifest = materialize(source)
    manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
    require(manifest == expected_manifest, "manifest differs from deterministic projection")
    for filename, content in payloads.items():
        require((HERE / filename).is_file() and (HERE / filename).read_bytes() == content, f"missing or stale {filename}")
    for filename, digest in manifest.get("file_sha256", {}).items():
        if (HERE / filename).is_file():
            require(hashlib.sha256((HERE / filename).read_bytes()).hexdigest() == digest, f"digest mismatch {filename}")

    data = {section: rows(HERE / filename) for section, filename in OUTPUTS.items()}
    registry = rows(HERE / "registry.jsonl")
    require(Counter(row["record_kind"] for row in registry) == Counter(manifest["counts"]), "manifest counts differ")
    keys = [(row["record_kind"], identity(row)) for row in registry]
    require(len(keys) == len(set(keys)), "duplicate record identity")
    for row in registry:
        ident = identity(row)
        if row["record_kind"] != "artifact_kind_definition":
            require(bool(ID.fullmatch(ident)), f"invalid identity {ident}")

    evidence = {row["source_id"]: row for row in data["sources"]}
    artifacts = {row["artifact_id"]: row for row in data["artifacts"]}
    libraries = {row["library_id"]: row for row in data["libraries"]}
    nodes = set(artifacts) | set(libraries)
    require(len(evidence) >= 25, "fewer than 25 primary/official/research sources")
    require(all(row.get("claim") and row.get("scope_limit") and row.get("uri", "").startswith("https://") for row in evidence.values()), "unscoped evidence")
    for ident, row in artifacts.items():
        require(all(ref in evidence for ref in row.get("evidence_refs", [])), f"unresolved evidence {ident}")
        owner = row.get("semantic_owner_ref")
        if owner:
            require(owner in artifacts and artifacts[owner]["kind"] == "semantic_contract", f"invalid owner {ident}:{owner}")
        if row["kind"] == "product":
            require(row["adoption_unit"] and row["operated"], f"product flags missing {ident}")
        if row["kind"] in {"suite", "architecture_pattern"}:
            require(owner is None, f"suite/pattern claims meaning {ident}")

    products = {ident for ident, row in artifacts.items() if row["kind"] == "product"}
    require(products == {"product.bi_reporting", "product.embedded_analytics", "product.analytical_notebook"}, "product identity set drifted")
    decided: set[str] = set()
    decisions = {row["decision_id"]: row for row in data["boundary_decisions"]}
    for ident, row in decisions.items():
        require(row["subject_ref"] in nodes, f"unknown decision subject {ident}")
        require(all(ref in evidence for ref in row["evidence_refs"]), f"unknown decision evidence {ident}")
        if row["subject_ref"] in products:
            decided.add(row["subject_ref"])
            require(set(row["split_test"]) == AXES, f"incomplete split test {ident}")
            total = sum(cell["score"] for cell in row["split_test"].values())
            require(all(cell["score"] in {0, 1, 2} and cell["evidence_refs"] for cell in row["split_test"].values()), f"invalid split cells {ident}")
            if row["disposition"] == "strong_product_candidate":
                require(17 <= total <= 20, f"strong score out of range {ident}:{total}")
            else:
                require(13 <= total <= 16, f"presumptive score out of range {ident}:{total}")
    require(decided == products, "not every product is adjudicated")
    for ident in {"decision.consumption.visual_runtime", "decision.consumption.dashboard_widget", "decision.consumption.alert_subscription", "decision.consumption.spreadsheet_governance", "decision.consumption.ai_prefix"}:
        require(ident in decisions, f"missing boundary decision {ident}")

    graph: dict[str, list[str]] = defaultdict(list)
    for ident, row in libraries.items():
        require(bool(row.get("product_refs")) and all(ref in products for ref in row["product_refs"]), f"bad product attribution {ident}")
        require(row["owner_ref"] in artifacts and artifacts[row["owner_ref"]]["kind"] == "semantic_contract", f"bad library owner {ident}")
        for field in ("provides", "types", "operations", "decisions", "invariants", "refusals"):
            require(bool(row.get(field)), f"empty {field} {ident}")
        for ref in row["provides"]:
            require(ref in artifacts and artifacts[ref]["kind"] == "capability", f"bad capability {ident}:{ref}")
        for ref in row["dependencies"]:
            require(ref in libraries, f"unknown dependency {ident}:{ref}")
            graph[ident].append(ref)
        require(all(ref in evidence for ref in row["evidence_refs"]), f"bad library evidence {ident}")
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
        require(row.get("invariant"), f"missing invariant {row['meaning_id']}")
        require(all(ref in artifacts for ref in row["must_not_be_owned_by"]), f"bad excluded owner {row['meaning_id']}")
    for row in data["requirements"]:
        require(row["consumer_ref"] in nodes and row["capability_ref"] in artifacts, f"bad requirement {row['requirement_id']}")
        require(row["status"] == "unbound" and row["minimum_qualified_offers"] >= 1, f"dishonest binding {row['requirement_id']}")
    for row in data["offers"]:
        require(row["provider_ref"] in artifacts and artifacts[row["provider_ref"]]["kind"] == "implementation", f"bad provider {row['offer_id']}")
        require(row["qualified_implementation_count"] == 0 and row["portable"] is False, f"unearned offer {row['offer_id']}")
        require(all(ref in artifacts and artifacts[ref]["kind"] == "capability" for ref in row["capability_refs"]), f"bad offered capability {row['offer_id']}")
    for row in data["relations"]:
        require(row["from_ref"] in nodes and row["to_ref"] in nodes, f"bad relation {row['relation_id']}")
    for row in data["crosswalks"]:
        require(all(ref in nodes for ref in row["canonical_refs"]), f"bad crosswalk {row['legacy_ref']}")

    compiler_registry = HERE.parents[2] / "domain_atlas/compiler/library_registry/library-contributions.jsonl"
    concrete = {row["library_id"]: row for row in rows(compiler_registry)}
    maps = {row["binding_map_id"]: row for row in data["binding_maps"]}
    require(len(maps) == len(libraries) == 14, "every local library needs one compiler map")
    require({row["abstract_library_ref"] for row in maps.values()} == set(libraries), "binding-map coverage drift")
    for ident, row in maps.items():
        require(row.get("product_refs") == libraries[row["abstract_library_ref"]].get("product_refs"), f"map product attribution drift {ident}")
        require(all(ref in concrete for ref in row["concrete_library_refs"]), f"unknown compiler library {ident}")
        require(row["portable_offer"] is False and row["compiler_disposition"] == "structurally_projected_unqualified", f"dishonest map {ident}")
    require(not data["binding_gaps"], "unexpected structural binding gap")

    dossiers = {row["product_ref"]: row for row in data["ddd_dossiers"]}
    require(set(dossiers) == products, "exact DDD dossier required for every consumption product")
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
    for product_ref, dossier in dossiers.items():
        ddd = dossier.get("strategic_and_tactical_ddd", {})
        require(set(ddd) == required_ddd_fields, f"DDD dossier lacks exact strategic/tactical fields {product_ref}")
        require(all(ddd.get(field) not in (None, [], {}) for field in required_ddd_fields), f"DDD dossier contains empty required fields {product_ref}")
        require(dossier.get("status") == "candidate_not_ratified", f"dossier prematurely ratified {product_ref}")
    bi_libraries = {ident for ident,row in libraries.items() if "product.bi_reporting" in row.get("product_refs", [])}
    require("library.consumption.report_definition" in bi_libraries, "BI report authoring library missing")
    require("capability.author_report" in libraries["library.consumption.report_definition"]["provides"], "BI authoring capability remains uncovered")

    negative_ids = {row["test_id"] for row in data["negative_tests"]}
    require({"negative.ai_prefix", "negative.agent_authority", "negative.notebook_kernel", "negative.visual_runtime_product"}.issubset(negative_ids), "constitutional negative twin missing")
    require(len(negative_ids) >= 18, "negative-test surface too small")
    require(manifest["derived"]["portable_offers"] == 0 and manifest["derived"]["qualified_offers"] == 0, "qualification fabricated")
    require(manifest["derived"]["unbound_requirements"] == len(data["requirements"]), "requirement binding fabricated")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "PASS consumption-experience adjudication: "
        f"{len(evidence)} sources; {len(artifacts)} artifacts; {len(products)} product candidates; 3 full product DDD dossiers; "
        f"{len(libraries)} library contracts; {len(data['ownership'])} owned meanings; "
        f"{len(data['requirements'])} unbound requirements; {len(data['offers'])} unqualified offers; "
        f"{len(maps)} compiler binding maps; 0 structural binding gaps; {len(data['crosswalks'])} legacy crosswalks"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
