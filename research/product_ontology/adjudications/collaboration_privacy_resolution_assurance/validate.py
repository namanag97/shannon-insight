#!/usr/bin/env python3
"""Validate product boundaries and deterministic compiler/library projections."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from build_bundle import HERE, OUTPUTS, load_source, materialize
from source_model import AXES, SOURCE, source_bytes
from product_ddd_enrichment import AUTOMATION, DDD_FIELDS


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
            for field in ("sovereign_question", "users", "harmed_parties", "jobs", "outcomes", "lifecycle_states", "commands", "events", "invariants", "refusals", "negative_mission", "automation_modality"):
                require(bool(row.get(field)), f"product {ident} missing {field}")
            require(row.get("automation_modality") == AUTOMATION, f"automation doctrine drift {ident}")
        if row["kind"] in {"suite", "architecture_pattern"}:
            require(owner is None, f"pattern/suite owns meaning {ident}")

    expected_products = {
        "product.controlled_data_collaboration",
        "product.privacy_rights_retention",
        "product.entity_resolution",
        "product.assurance_case_appraisal",
    }
    products = {ident for ident, row in artifacts.items() if row["kind"] == "product"}
    require(products == expected_products, "product set drift")
    decisions = {row["decision_id"]: row for row in data["boundary_decisions"]}
    for key in ("collaboration", "privacy", "resolution", "assurance"):
        decision = decisions.get(f"decision.cpra.{key}.product")
        require(decision is not None, f"missing {key} product decision")
        if decision:
            require(decision["subject_ref"] in products, f"bad {key} product subject")
            require(set(decision["split_test"]) == set(AXES), f"{key} split axes")
            total = sum(cell["score"] for cell in decision["split_test"].values())
            require(decision["disposition"] == "strong_product_candidate" and 17 <= total <= 20, f"{key} score {total}")
    required_decisions = {
        "decision.cpra.unified_governance", "decision.cpra.clean_room_pattern",
        "decision.cpra.tee_component", "decision.cpra.match_method", "decision.cpra.agent_optional",
    }
    require(required_decisions.issubset(decisions), "critical boundary decision missing")
    for ident, row in decisions.items():
        require(row["subject_ref"] in nodes, f"bad subject {ident}")
        require(all(ref in evidence for ref in row["evidence_refs"]), f"bad decision evidence {ident}")

    graph: dict[str, list[str]] = defaultdict(list)
    product_library_counts = Counter()
    for ident, row in libraries.items():
        require(row["product_ref"] in products, f"bad product ref {ident}")
        product_library_counts[row["product_ref"]] += 1
        require(row["owner_ref"] in artifacts and artifacts[row["owner_ref"]]["kind"] == "semantic_contract", f"library owner {ident}")
        for field in ("provides", "types", "operations", "decisions", "invariants", "refusals"):
            require(bool(row.get(field)), f"empty {field} {ident}")
        require("generated_or_agent_output_is_non_authoritative_until_typed_validated_and_accepted" in row["invariants"], f"agent authority law absent {ident}")
        require("removing_model_and_agent_extensions_preserves_the_deterministic_core_contract" in row["invariants"], f"agent removal law absent {ident}")
        for ref in row["provides"]:
            require(ref in artifacts and artifacts[ref]["kind"] == "capability", f"bad capability {ident}:{ref}")
        for ref in row["dependencies"]:
            require(ref in libraries, f"bad dependency {ident}:{ref}")
            graph[ident].append(ref)
    require(len(libraries) >= 50 and all(product_library_counts[product] >= 12 for product in products), "library decomposition floor")

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
        require(row["provider_ref"] in artifacts and artifacts[row["provider_ref"]]["kind"] == "implementation", f"bad offer provider {row['offer_id']}")
        require(row["qualified_implementation_count"] == 0 and row["portable"] is False, f"fabricated qualification {row['offer_id']}")
        require(all(ref in artifacts and artifacts[ref]["kind"] == "capability" for ref in row["capability_refs"]), f"bad offer capability {row['offer_id']}")
    for row in data["relations"]:
        require(row["from_ref"] in nodes and row["to_ref"] in nodes, f"bad relation {row['relation_id']}")
    for row in data["crosswalks"]:
        require(all(ref in nodes for ref in row["canonical_refs"]), f"bad crosswalk {row['legacy_ref']}")

    compiler_path = HERE.parents[2] / "domain_atlas/compiler/library_registry/library-contributions.jsonl"
    concrete = {row["library_id"]: row for row in rows(compiler_path)}
    maps = {row["binding_map_id"]: row for row in data["binding_maps"]}
    require(len(maps) == len(libraries), "one compiler map per library required")
    require({row["abstract_library_ref"] for row in maps.values()} == set(libraries), "map coverage")
    for ident, row in maps.items():
        require(row["product_ref"] in products, f"bad map product {ident}")
        require(row["compiler_disposition"] == "structurally_projected_unqualified", f"bad map disposition {ident}")
        # An abstract product seam may intentionally be implemented by a closed
        # composition of independently owned libraries.  Requiring exactly one
        # concrete library would recreate the coarse, shared-owner boundary that
        # the registry has retired.  Non-empty, exact, resolvable composition is
        # the invariant here; qualification remains a separate gate below.
        require(row["concrete_library_refs"] and all(ref in concrete for ref in row["concrete_library_refs"]), f"unknown compiler library {ident}")
        require(row.get("gap_ref") is None and row["portable_offer"] is False, f"invalid map claim {ident}")
    require(not data["binding_gaps"], "structural binding gaps reappeared")
    require(len(data["semantic_gaps"]) >= 20 and all(row["blocking"] for row in data["semantic_gaps"]), "semantic gap set incomplete")

    dossiers = {row["product_ref"]: row for row in data["ddd_dossiers"]}
    require(set(dossiers) == products, "one full DDD dossier per product required")
    for product_ref, dossier in dossiers.items():
        ddd = dossier.get("strategic_and_tactical_ddd", {})
        require(set(ddd) == DDD_FIELDS, f"DDD field coverage drift {product_ref}")
        require(all(ddd.get(field) not in (None, [], {}) for field in DDD_FIELDS), f"empty DDD field {product_ref}")
        require(dossier.get("status") == "candidate_not_ratified", f"DDD status overstated {product_ref}")

    negative_ids = {row["test_id"] for row in data["negative_tests"]}
    require(len(negative_ids) >= 50, "negative-twin floor")
    critical = {
        "negative.cpra.collab_tee", "negative.cpra.collab_query_success",
        "negative.cpra.privacy_approval", "negative.cpra.privacy_backup",
        "negative.cpra.resolution_score", "negative.cpra.resolution_model",
        "negative.cpra.assurance_automation", "negative.cpra.assurance_approval",
        "negative.cpra.agent_required", "negative.cpra.ai_prefix",
    }
    require(critical.issubset(negative_ids), "critical negative twins missing")
    laws = set(source.get("non_collapse_laws", []))
    require(any("removing all model and agent extensions" in law for law in laws), "deterministic-core removal law missing")
    require(any("probabilistic linkage and predictive ML" in law for law in laws), "predictive-method classification law missing")
    require(manifest["derived"]["qualified_offers"] == 0 and manifest["derived"]["portable_offers"] == 0, "qualification fabricated")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "PASS collaboration/privacy/resolution/assurance adjudication: "
        f"{len(evidence)} sources; {len(artifacts)} artifacts; {len(products)} products; "
        f"4 full product DDD dossiers; {len(libraries)} library contracts; {len(data['requirements'])} unbound requirements; "
        f"{len(data['offers'])} unqualified offers; {len(maps)} compiler maps; "
        f"{len(data['semantic_gaps'])} semantic gaps; {len(data['negative_tests'])} negative twins"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
