#!/usr/bin/env python3
"""Validate the seven analytical-operation product adjudications and compiler maps."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
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
    require = lambda ok, message: None if ok else errors.append(message)
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
    require(Counter(row["record_kind"] for row in registry) == Counter(manifest["counts"]), "manifest count drift")
    ids = [(row["record_kind"], identity(row)) for row in registry]
    require(len(ids) == len(set(ids)), "duplicate record identity")

    evidence = {row["source_id"]: row for row in data["sources"]}
    artifacts = {row["artifact_id"]: row for row in data["artifacts"]}
    products = {ident: row for ident, row in artifacts.items() if row["kind"] == "product"}
    libraries = {row["library_id"]: row for row in data["libraries"]}
    capabilities = {ident for ident, row in artifacts.items() if row["kind"] == "capability"}
    require(len(evidence) == 64, "expected 64 audit sources")
    require(len(products) == 7, "expected seven products")
    require(len(libraries) == 88, "expected 88 library contracts")
    require(len(data["binding_maps"]) == 88, "every library requires one compiler map")
    require(len(data["ddd_dossiers"]) == 7, "every product requires one DDD dossier")
    require(manifest["derived"]["qualified_offers"] == 0 and manifest["derived"]["portable_offers"] == 0, "fabricated qualification or portability")

    required_product_fields = {"sovereign_question", "users", "harmed_parties", "jobs", "outcomes", "lifecycle_states", "commands", "events", "invariants", "refusals", "negative_mission", "automation_modality"}
    for ident, row in products.items():
        require(required_product_fields.issubset(row), f"{ident}: incomplete product DDD surface")
        for field in ("users", "harmed_parties", "jobs", "outcomes", "lifecycle_states", "commands", "events", "invariants", "refusals"):
            require(bool(row[field]), f"{ident}: empty {field}")
        require(len(row["lifecycle_states"]) >= 10, f"{ident}: state machine underdecomposed")
        require(len(row["commands"]) == len(row["events"]), f"{ident}: commands/events are not paired")
        modality = row["automation_modality"]
        require(modality["default"] == "DETERMINISTIC_CORE_ONLY", f"{ident}: ambient model/agent default")
        require("never replaces vocabulary" in modality["hard_work_law"], f"{ident}: hard-work law missing")

    decisions = {row["subject_ref"]: row for row in data["boundary_decisions"] if row["subject_ref"] in products}
    require(set(decisions) == set(products), "product decision coverage drift")
    for product_ref, row in decisions.items():
        require(row["disposition"] == "strong_product_candidate", f"{product_ref}: product disposition drift")
        split_test = row["split_test"]
        require(set(split_test) == set(AXES), f"{product_ref}: split-test axes incomplete")
        require(sum(value["score"] for value in split_test.values()) >= 17, f"{product_ref}: insufficient product-boundary score")

    required_ddd = {
        "domain_vision_statement", "subdomain_classification", "bounded_context_boundary", "ubiquitous_language_policy",
        "context_map", "anti_corruption_layers", "published_language", "value_objects", "entities", "aggregates",
        "aggregate_roots", "aggregate_invariants", "commands", "domain_events", "refusal_failure_catalog",
        "domain_services", "application_services", "repositories", "factories", "specifications", "state_machine",
        "policies_and_reactions", "sagas_and_process_managers", "read_models_and_projections", "integration_event_policy",
        "concurrency_and_idempotency", "time_model", "event_storming_swimlanes", "nonfunctional_laws",
    }
    dossier_products = set()
    for row in data["ddd_dossiers"]:
        dossier_products.add(row["product_ref"])
        require(row["product_ref"] in products, f"bad DDD product {row['product_ref']}")
        model = row["strategic_and_tactical_ddd"]
        require(required_ddd.issubset(model), f"{row['dossier_id']}: missing DDD concerns {sorted(required_ddd - set(model))}")
        for field in required_ddd - {"subdomain_classification", "ubiquitous_language_policy", "integration_event_policy"}:
            require(bool(model[field]), f"{row['dossier_id']}: empty DDD field {field}")
        require(set(model["aggregate_roots"]) == {aggregate["root"] for aggregate in model["aggregates"]}, f"{row['dossier_id']}: aggregate-root drift")
    require(dossier_products == set(products), "DDD dossier product coverage drift")

    ownership = {row["meaning_id"]: row for row in data["ownership"]}
    require(len(ownership) == len(libraries), "semantic ownership/library count drift")
    for ident, row in libraries.items():
        require(row["product_ref"] in products, f"{ident}: unknown product")
        require(row["owner_ref"] in artifacts and artifacts[row["owner_ref"]]["kind"] == "semantic_contract", f"{ident}: unknown semantic owner")
        require(set(row["provides"]).issubset(capabilities), f"{ident}: unknown capability")
        for field in ("types", "operations", "decisions", "invariants", "refusals"):
            require(bool(row[field]), f"{ident}: empty {field}")
        require("generated_or_agent_output_is_non_authoritative_until_typed_validated_and_accepted" in row["invariants"], f"{ident}: proposal authority law missing")
        require("removing_model_and_agent_extensions_preserves_the_deterministic_core_contract" in row["invariants"], f"{ident}: removal law missing")

    compiler_path = HERE.parents[2] / "domain_atlas/compiler/library_registry/library-contributions.jsonl"
    compiler_rows = {row["library_id"]: row for row in rows(compiler_path)}
    maps = {row["abstract_library_ref"]: row for row in data["binding_maps"]}
    gaps = {row["gap_id"]: row for row in data["binding_gaps"]}
    require(set(maps) == set(libraries), "compiler map coverage drift")
    used_gap_refs = set()
    for library_ref, row in maps.items():
        concrete = row["concrete_library_refs"]
        gap_ref = row.get("gap_ref")
        require(row["portable_offer"] is False, f"{library_ref}: fabricated portable offer")
        if concrete:
            require(gap_ref is None, f"{library_ref}: concrete map also has binding gap")
            require(row["compiler_disposition"] == "registry_contract_present_unqualified", f"{library_ref}: concrete disposition drift")
            require(all(ref in compiler_rows for ref in concrete), f"{library_ref}: unknown compiler contract")
        else:
            require(row["compiler_disposition"] == "missing_exact_compiler_library_contract", f"{library_ref}: missing disposition drift")
            require(gap_ref in gaps, f"{library_ref}: missing/unresolved binding gap")
            used_gap_refs.add(gap_ref)
    require(used_gap_refs == set(gaps), "orphan or unused binding gap")
    require(all(row["blocking"] for row in gaps.values()), "nonblocking compiler gap fabricated")
    require(len(gaps) == 28, "expected fourteen Dataset Curation and fourteen Image Analysis compiler gaps")

    requirements = {row["requirement_id"]: row for row in data["requirements"]}
    require(len(requirements) == len(libraries), "requirement/library count drift")
    require(all(row["status"] == "unbound" and row["minimum_qualified_offers"] == 2 for row in requirements.values()), "requirements are not fail-closed")
    require(all(row["status"] == "observed_unqualified" and row["qualified_implementation_count"] == 0 and not row["portable"] for row in data["offers"]), "provider qualification fabricated")
    for row in data["offers"]:
        require(row["provider_ref"] in artifacts and artifacts[row["provider_ref"]]["kind"] == "implementation", f"bad offer provider {row['offer_id']}")
        require(set(row["capability_refs"]).issubset(capabilities), f"bad offer capabilities {row['offer_id']}")
    for row in artifacts.values():
        require(all(ref in evidence for ref in row.get("evidence_refs", [])), f"{row['artifact_id']}: unresolved evidence")

    nodes = set(artifacts) | set(libraries)
    for row in data["relations"]:
        require(row["from_ref"] in nodes and row["to_ref"] in nodes, f"bad relation {row['relation_id']}")
    for row in data["crosswalks"]:
        require(all(ref in nodes for ref in row["canonical_refs"]), f"bad crosswalk {row['legacy_ref']}")
    expected_legacy = {"candidate.product.self_service_data_preparation", "candidate.product.annotation_operations", "candidate.product.dataset_curation_workbench", "candidate.product.document_processing_review", "candidate.product.image_analysis_workbench", "candidate.product.visual_inspection_operations", "candidate.product.signal_condition_diagnostics"}
    require(expected_legacy.issubset({row["legacy_ref"] for row in data["crosswalks"]}), "inventory promotion crosswalks incomplete")
    negative_ids = {row["test_id"] for row in data["negative_tests"]}
    require(len(negative_ids) >= 35, "negative-test floor")
    require({"negative.ao.ai_prefix", "negative.ao.agent_research", "negative.ao.deterministic_closed_form", "negative.ao.agent_effect"}.issubset(negative_ids), "critical automation negatives missing")
    require(len(data["semantic_gaps"]) >= 25 and all(row["blocking"] for row in data["semantic_gaps"]), "semantic gap floor")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "PASS analytical-operations adjudication: "
        f"{len(evidence)} sources; {len(products)} products; {len(data['ddd_dossiers'])} full DDD dossiers; "
        f"{len(libraries)} library contracts; {len(maps)} compiler maps; {len(gaps)} compiler gaps; "
        f"{len(data['offers'])} unqualified offers; {len(data['negative_tests'])} negative twins; "
        f"{len(data['semantic_gaps'])} semantic gaps; 0 qualified or portable offers"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
