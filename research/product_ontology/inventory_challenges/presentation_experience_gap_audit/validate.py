#!/usr/bin/env python3
"""Validate lossless coverage and fail-closed claims in the presentation audit."""

from __future__ import annotations

import hashlib
import json

from build_bundle import FILES, HERE, INPUTS, build, load_jsonl, outputs


def main() -> int:
    errors: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    expected = outputs()
    for name, text in expected.items():
        path = HERE / name
        require(path.is_file() and path.read_text() == text, f"stale {name}")

    manifest = json.loads((HERE / "manifest.json").read_text())
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        require(len(data) == claim["bytes"], f"byte count mismatch {name}")
        require(hashlib.sha256(data).hexdigest() == claim["sha256"], f"hash mismatch {name}")

    snapshot = json.loads((HERE / "input-snapshot.json").read_text())
    claims = {row["role"]: row for row in snapshot["files"]}
    require(set(claims) == set(INPUTS), "input snapshot roles drift")
    for role, path in INPUTS.items():
        data = path.read_bytes()
        require(claims[role]["sha256"] == hashlib.sha256(data).hexdigest(), f"input hash stale {role}")

    built = build()
    sources = built["evidence"]
    axes = built["semantic_axes"]
    artifacts = built["artifact_kinds"]
    results = built["result_kinds"]
    hypotheses = built["product_hypotheses"]
    libraries = built["library_hypotheses"]
    laws = built["noncollapse_laws"]
    obligations = built["artifact_axis_obligations"]
    cells = built["compatibility_cells"]
    gaps = built["open_gaps"]
    split_adjudications = built["split_adjudications"]
    allocations = built["split_library_allocations"]
    migration = built["split_migration_steps"]
    dossiers = built["split_ddd_dossiers"]
    frontier = built["frontier_crosswalk"]
    frontier_laws = built["frontier_laws"]
    vacancy_adjudications = built["vacancy_adjudications"]
    vacancy_ownership = built["vacancy_ownership"]
    vacancy_libraries = built["vacancy_library_seams"]
    vacancy_laws = built["vacancy_laws"]
    vacancy_wiring = built["vacancy_compiler_wiring"]
    vacancy_dossiers = built["vacancy_ddd_dossiers"]
    summary = built["summary"]

    require(len(sources) >= 64, "primary/official source floor not met")
    require(len({row["source_id"] for row in sources}) == len(sources), "duplicate source id")
    require(all(row["bounded_claim"] and row["authority_limit"] for row in sources), "unbounded evidence claim")
    evidence_ids = {row["source_id"] for row in sources}
    require(len(axes) == 16, "presentation semantic axes drift")
    require(len(artifacts) >= 35, "artifact ontology underdecomposed")
    require(len(results) >= 21, "analytical result ontology underdecomposed")
    require(len(hypotheses) >= 12, "product hypothesis frontier underdecomposed")
    require(len(libraries) >= 45, "library frontier underdecomposed")
    require(len(laws) >= 30, "non-collapse law floor not met")
    require(len(obligations) == len(artifacts) * len(axes), "artifact-axis tensor is not lossless")
    require(len(cells) == len(artifacts) * len(results), "result-artifact tensor is not lossless")
    require(len({row["obligation_id"] for row in obligations}) == len(obligations), "duplicate axis obligation")
    require(len({row["cell_id"] for row in cells}) == len(cells), "duplicate compatibility cell")
    require(all(row["decision"] == "UNRATIFIED" and row["exact_contract_ref"] is None for row in obligations), "artifact-axis authority fabricated")
    require(all(row["status"] == "UNRATIFIED" and row["profile_ref"] is None for row in cells), "compatibility profile fabricated")
    require(all(row["ratification"] == "WITHHELD" for row in hypotheses), "product ratification fabricated")
    require(all(len(row["evidence_refs"]) >= 3 and set(row["evidence_refs"]) <= evidence_ids for row in hypotheses), "product hypothesis evidence is weak or unresolved")
    require(all(len(row["evidence_refs"]) >= 2 and set(row["evidence_refs"]) <= evidence_ids for row in artifacts), "artifact evidence is weak or unresolved")
    require(all(row["evidence_refs"] and set(row["evidence_refs"]) <= evidence_ids for row in libraries), "library evidence is missing or unresolved")
    require(all(not row["unresolved_retained_product_refs"] for row in hypotheses), "product hypothesis references unknown retained products")
    require(all(row["compiler_binding"].startswith("REFUSED") for row in libraries), "compiler binding bypassed")
    require(all(row["blocking_for_promotion_or_compilation"] and row["status"] in {"OPEN", "RESEARCH_RESOLVED_DOWNSTREAM_GATES_OPEN"} for row in gaps), "gap closed without downstream evidence")
    resolved_gap_subjects = {row["subject_ref"] for row in gaps if row["status"] == "RESEARCH_RESOLVED_DOWNSTREAM_GATES_OPEN"}
    require(resolved_gap_subjects == {"hypothesis.presentation.interactive_exploration", "hypothesis.presentation.formal_reporting", "hypothesis.presentation.alerting"}, "research-resolved gap projection drift")
    require(all(row.get("research_disposition", "").startswith("RESEARCH_ADJUDICATED_") and row["evidence_needed"] for row in gaps if row["status"] == "RESEARCH_RESOLVED_DOWNSTREAM_GATES_OPEN"), "resolved research gap lost downstream gates")
    require(summary["ratified_products"] == summary["ratified_contracts"] == summary["qualified_implementations"] == 0, "physical or semantic proof fabricated")
    require(summary["completion_claim"] is False and summary["status"].endswith("INCOMPLETE"), "audit overclaims completion")
    require({row["name"] for row in artifacts} >= {"dashboard", "paginated_report", "regulatory_report", "notebook", "spreadsheet_workbook", "map_view", "graph_view", "waveform_view", "volume_3d_view", "embedded_view", "alert_occurrence", "accessible_equivalent"}, "critical presentation artifacts missing")
    require({row["name"] for row in results} >= {"forecast", "causal_effect", "optimization_solution", "simulation_ensemble", "process_model", "geospatial_feature", "image_inspection", "signal_window_spectrum", "scientific_mesh_volume"}, "critical analytical results missing")
    require({row["law_id"] for row in laws} >= {"law.presentation.dashboard_alert", "law.presentation.selection_decision", "law.presentation.embed_authority", "law.presentation.render_conformance"}, "critical non-collapse laws missing")
    require(len(split_adjudications) == 3, "split adjudication cardinality drift")
    split = [row for row in split_adjudications if row["record_kind"] == "presentation_product_split_adjudication"]
    candidates = [row for row in split_adjudications if row["record_kind"] == "presentation_product_boundary_adjudication"]
    require(len(split) == 1 and split[0]["source_product_ref"] == "product.bi_reporting", "BI reporting source split missing")
    require(len(candidates) == 2, "two target product adjudications required")
    require(all(row["score_total"] == 20 and row["verdict"] == "STRONG_PRODUCT" for row in candidates), "split targets did not pass the ten-axis test")
    require(all(set(row["split_test"]) == {"user", "job", "adoption", "semantics", "authority", "lifecycle", "operation", "economics", "interface", "market_evidence"} for row in candidates), "split-test axes incomplete")
    require(all(all(axis["score"] == 2 and set(axis["evidence_refs"]) <= evidence_ids for axis in row["split_test"].values()) for row in candidates), "split-test evidence unresolved")
    require(all(row["ratification"] == "WITHHELD" for row in split_adjudications), "split was falsely ratified")
    require(len(allocations) == 20 and len({row["allocation_id"] for row in allocations}) == 20, "library allocation is incomplete or duplicated")
    require({row["library_ref"] for row in allocations} >= {"library.presentation.interaction_state", "library.presentation.selection_algebra", "library.presentation.report_run", "library.presentation.publication_lifecycle", "library.consumption.alert_state"}, "critical split libraries missing")
    require(all(row["status"] == "PROPOSED_UNRATIFIED" for row in allocations), "library ownership fabricated")
    require(len(migration) == 8 and [row["order"] for row in migration] == list(range(1, 9)), "hard-cut migration plan is not total and ordered")
    require(all(row["status"] == "PLANNED_NOT_EXECUTED" for row in migration), "migration execution fabricated")
    require(any(row["phase"] == "HARD_CUT" and "compatibility alias" in row["requirement"] for row in migration), "no-alias hard cut missing")
    require(len(dossiers) == 2 and {row["product_ref"] for row in dossiers} == {"product.interactive_analytics_exploration", "product.formal_reporting_publication"}, "candidate DDD dossiers missing")
    required_ddd = {"domain_vision_statement", "subdomain_classification", "bounded_context_boundary", "ubiquitous_language_policy", "context_map", "anti_corruption_layers", "published_language", "value_objects", "entities", "aggregates", "aggregate_roots", "aggregate_invariants", "commands", "domain_events", "refusal_failure_catalog", "domain_services", "application_services", "repositories", "factories", "specifications", "state_machine", "policies_and_reactions", "sagas_and_process_managers", "read_models_and_projections", "integration_event_policy", "concurrency_and_idempotency", "time_model", "event_storming_swimlanes", "nonfunctional_laws"}
    require(all(set(row["strategic_and_tactical_ddd"]) == required_ddd for row in dossiers), "candidate DDD dossier field coverage drift")
    require(all(row["status"] == "COMPLETE_CANDIDATE_NOT_RATIFIED" and row["completion_claim"] is False for row in dossiers), "candidate DDD dossier overclaims authority")
    require(summary["boundary_split_adjudications"] == 1 and summary["strong_candidate_products"] == 2, "split summary drift")
    retained_refs = {row["local_subject_ref"] for row in load_jsonl(INPUTS["retained_products"])}
    require(len(frontier) == 38 and [row["frontier_id"] for row in frontier] == [f"H{i:02d}" for i in range(1, 39)], "external frontier is not losslessly represented")
    require(all(set(row["retained_product_refs"]) <= retained_refs for row in frontier), "frontier crosswalk references unknown retained products")
    require(all(row["adjudicated_ontology_level"] and row["disposition"] and row["bounded_finding"] for row in frontier), "frontier row lacks typed disposition")
    require({row["disposition"] for row in frontier} >= {"COVERED", "SPLIT_CANDIDATE", "DO_NOT_PROMOTE_AS_ONE_PRODUCT", "RESOLVED_DEFER_PRODUCT_PROMOTION", "RESOLVED_RETIRE_COMPOSITE", "COVERED_DO_NOT_COLLAPSE"}, "frontier dispositions collapsed")
    require(sum(row["disposition"] == "GENUINE_RESEARCH_VACANCY" for row in frontier) == 0, "adjudicated frontier vacancy remained open")
    require(len(frontier_laws) == 5 and {row["law"] for row in frontier_laws} >= {"analytical_method_family != operated_product", "product_cluster != bounded_context", "shared_intermediate_representation != product", "machine_or_library != product"}, "frontier ontology-level laws incomplete")
    require(summary["external_frontier_rows_adjudicated"] == 38 and summary["frontier_genuine_research_vacancies"] == 0, "frontier summary drift")
    require(len(vacancy_adjudications) == 3, "vacancy adjudication cardinality drift")
    by_subject = {row["subject_ref"]: row for row in vacancy_adjudications}
    content_decision = by_subject["hypothesis.presentation.analytical_content_collaboration"]
    notification_decision = by_subject["external.product.notification_orchestration_delivery"]
    composite_decision = by_subject["candidate.product.alert_subscription"]
    require(content_decision["score_total"] == 14 and content_decision["verdict"] == "DEFER_PRODUCT_PROMOTION_RETAIN_SHARED_CONTROL_PLANE_AND_LIBRARIES", "content collaboration boundary overpromoted or underexplained")
    require(notification_decision["score_total"] == 20 and notification_decision["verdict"] == "STRONG_EXTERNAL_HORIZONTAL_PRODUCT" and notification_decision["analytics_posture"] == "IMPORTED_NEIGHBOR_NOT_ANALYTICS_OWNED", "notification product boundary incorrect")
    require(composite_decision["verdict"] == "RETIRE_COMPOSITE_AND_REALLOCATE_MEANINGS", "alert/subscription composite not retired")
    require(all(row["ratification"] == "WITHHELD" for row in vacancy_adjudications), "vacancy boundary authority fabricated")
    require(all(set(row["split_test"]) == {"user", "job", "adoption", "semantics", "authority", "lifecycle", "operation", "economics", "interface", "market_evidence"} for row in [content_decision, notification_decision]), "vacancy split test incomplete")
    require(all(all(set(axis["evidence_refs"]) <= evidence_ids for axis in row["split_test"].values()) for row in [content_decision, notification_decision]), "vacancy split evidence unresolved")
    require(len(vacancy_ownership) == 22 and len({row["meaning"] for row in vacancy_ownership}) == 22, "vacancy meaning ownership incomplete")
    require({row["proposed_owner"] for row in vacancy_ownership} >= {"PRODUCING_ANALYTICAL_PRODUCT", "CONTENT_PRODUCER_PRODUCT", "EXTERNAL_NOTIFICATION_PRODUCT", "IMPORTED_INCIDENT_OR_CASE_WORKFLOW", "SHARED_CONTENT_CONTROL_PLANE"}, "critical vacancy owners missing")
    require(len(vacancy_libraries) == 28 and len({row["library_ref"] for row in vacancy_libraries}) == 28, "vacancy library seams incomplete")
    require(all(len(row["required_contract_surface"]) == 13 and row["status"] == "CANDIDATE_UNRATIFIED" for row in vacancy_libraries), "vacancy library contract surfaces incomplete")
    require(len(vacancy_laws) == 20 and {row["law"] for row in vacancy_laws} >= {"alert_occurrence != notification_delivery_attempt", "delivery_outcome != human_acknowledgment", "content_container != analytical_artifact", "collaboration_review != product_specific_approval"}, "vacancy non-collapse laws incomplete")
    require(len(vacancy_wiring) == 6 and {row["effect"] for row in vacancy_wiring} >= {"PURE_INTENT_CONSTRUCTION", "PURE_PLAN", "EXTERNAL_COMMUNICATION_EFFECT", "EVIDENCE_REDUCTION", "PURE_EXPORT_CONSTRUCTION"}, "vacancy compiler wiring incomplete")
    require(all(row["input"] and row["output"] and row["refusals"] for row in vacancy_wiring), "compiler transform is partial")
    require(len(vacancy_dossiers) == 1 and vacancy_dossiers[0]["product_ref"] == "external.product.notification_orchestration_delivery", "external notification DDD missing")
    require(set(vacancy_dossiers[0]["strategic_and_tactical_ddd"]) == required_ddd, "external notification DDD coverage drift")
    require(vacancy_dossiers[0]["status"] == "COMPLETE_CANDIDATE_NOT_RATIFIED" and vacancy_dossiers[0]["completion_claim"] is False, "external notification DDD overclaims completion")
    require(summary["vacancy_boundary_adjudications"] == 3 and summary["vacancy_meaning_allocations"] == 22 and summary["vacancy_library_seams"] == 28 and summary["vacancy_compiler_transforms"] == 6, "vacancy summary drift")
    require(summary["research_resolved_downstream_gated_gaps"] == 3 and summary["unresolved_research_gaps"] == len(gaps) - 3, "gap summary does not distinguish research from downstream work")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "PASS presentation-experience gap audit: "
        f"{len(sources)} sources; {len(artifacts)} artifacts x {len(results)} result kinds = {len(cells)} compatibility cells; "
        f"{len(obligations)} artifact-axis obligations; {len(hypotheses)} product hypotheses; "
        f"{len(libraries)} library seams; {len(laws)} non-collapse laws; {summary['unresolved_research_gaps']} unresolved research gaps + {summary['research_resolved_downstream_gated_gaps']} downstream-gated resolutions; "
        f"1 adjudicated split, 2 strong candidate products, {len(allocations)} allocated libraries; "
        f"38 external frontier rows typed with 0 open research vacancies; "
        f"3 vacancy adjudications, {len(vacancy_ownership)} meaning allocations, {len(vacancy_libraries)} library seams; "
        "0 ratified products/contracts/implementations"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
