#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
rows = [
    json.loads(x)
    for x in (HERE / "master-batches.jsonl").read_text(encoding="utf-8").splitlines()
    if x.strip()
]
summary = json.loads((HERE / "master-summary.json").read_text(encoding="utf-8"))
readiness = json.loads(
    (ROOT / "research/product_ontology/dossier_readiness/summary.json").read_text(encoding="utf-8")
)
qualification = json.loads(
    (ROOT / "research/product_ontology/qualification_program/effective-summary.json").read_text(
        encoding="utf-8"
    )
)
industries = json.loads(
    (ROOT / "research/domain_atlas/industries/integration-audit.json").read_text(encoding="utf-8")
)
industry_effective = json.loads(
    (
        ROOT / "research/domain_atlas/industries/canonical-reference-effective-summary.json"
    ).read_text(encoding="utf-8")
)
industry_review = json.loads(
    (
        ROOT / "research/domain_atlas/industries/canonical-reference-machine-review-summary.json"
    ).read_text(encoding="utf-8")
)
industry_candidates = json.loads(
    (
        ROOT / "research/domain_atlas/industries/canonical-reference-auto-alias-summary.json"
    ).read_text(encoding="utf-8")
)
industry_residuals = json.loads(
    (ROOT / "research/domain_atlas/industries/canonical-reference-residual-summary.json").read_text(
        encoding="utf-8"
    )
)
context_map = json.loads(
    (ROOT / "research/domain_atlas/context_map/manifest.json").read_text(encoding="utf-8")
)
source_systems = json.loads(
    (ROOT / "research/domain_atlas/universes/source_systems/coverage-report.json").read_text(
        encoding="utf-8"
    )
)
data_shapes = json.loads(
    (ROOT / "research/domain_atlas/universes/data_shapes/coverage-report.json").read_text(
        encoding="utf-8"
    )
)
providers = json.loads(
    (ROOT / "research/domain_atlas/compiler/provider_target_registry/manifest.json").read_text(
        encoding="utf-8"
    )
)
evidence_governance = json.loads(
    (
        ROOT / "research/analytics_landscape/product_families/evidence-governance-summary.json"
    ).read_text(encoding="utf-8")
)
effective_evidence_governance = json.loads(
    (
        ROOT
        / "research/analytics_landscape/product_families/effective-evidence-governance-summary.json"
    ).read_text(encoding="utf-8")
)
reviewed_evidence_frontier = json.loads(
    (
        ROOT
        / "research/analytics_landscape/product_families/effective-evidence-frontier-summary.json"
    ).read_text(encoding="utf-8")
)
boundary_falsification = json.loads(
    (
        ROOT
        / "research/product_ontology/dossier_readiness/product-boundary-falsification-summary.json"
    ).read_text(encoding="utf-8")
)
contract_scopes = json.loads(
    (
        ROOT / "research/product_ontology/qualification_program/contract-scope-summary.json"
    ).read_text(encoding="utf-8")
)
canonical_refs = json.loads(
    (
        ROOT / "research/domain_atlas/industries/canonical-reference-effective-summary.json"
    ).read_text(encoding="utf-8")
)
source_occurrences = json.loads(
    (
        ROOT / "research/domain_atlas/universes/source_systems/occurrence-registry-summary.json"
    ).read_text(encoding="utf-8")
)
source_topology = json.loads(
    (
        ROOT / "research/domain_atlas/universes/source_systems/source-acquisition-topology.json"
    ).read_text(encoding="utf-8")
)
source_reference_chain = json.loads(
    (
        ROOT
        / "research/domain_atlas/universes/source_systems/source-acquisition-reference-summary.json"
    ).read_text(encoding="utf-8")
)
effective_shape_gaps = json.loads(
    (ROOT / "research/domain_atlas/universes/data_shapes/effective-gap-summary.json").read_text(
        encoding="utf-8"
    )
)
synthesis = json.loads(
    (ROOT / "research/product_ontology/solution_synthesis_architecture/summary.json").read_text(
        encoding="utf-8"
    )
)
human_work = json.loads(
    (
        ROOT / "research/domain_atlas/universes/human_work_review_adjudication/manifest.json"
    ).read_text(encoding="utf-8")
)
effect_boundary = json.loads(
    (
        ROOT
        / "research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/effect_boundary_coordinate_ontology/summary.json"
    ).read_text(encoding="utf-8")
)
vertical_acceptance = json.loads(
    (
        ROOT
        / "research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p8_vertical_acceptance_tensor/summary.json"
    ).read_text(encoding="utf-8")
)
change_intelligence = json.loads(
    (ROOT / "research/domain_atlas/ecosystem/change_intelligence/manifest.json").read_text(
        encoding="utf-8"
    )
)
coverage_planes = [
    json.loads(x)
    for x in (ROOT / "research/domain_atlas/coverage-planes.jsonl")
    .read_text(encoding="utf-8")
    .splitlines()
    if x.strip()
]

assert len(rows) == 21 == summary["batch_count"]
ids = [r["batch_id"] for r in rows]
assert ids == [f"B{i:02d}_" + ids[i].split("_", 1)[1] for i in range(21)]
assert len(set(ids)) == len(ids)
known = set(ids)
seen = set()
for row in rows:
    assert set(row["depends_on"]) <= known
    assert set(row["depends_on"]) <= seen, f"{row['batch_id']} is not dependency ordered"
    assert row["exit_condition"] and row["authority_refs"] and row["scope"]
    assert row["status"] not in {"CLOSED", "SATISFIED"}
    seen.add(row["batch_id"])

cases = sum(p["cases"] for p in industries["packs"])
assert cases == 1613 == summary["industry_analytical_case_count"]
assert summary["retained_product_count"] == readiness["retained_product_count"] == 66
assert (
    summary["library_subject_count"] == qualification["library_qualification_subject_count"] == 539
)
assert (
    summary["effective_evidence_vacancy_count"]
    == qualification["effective_evidence_vacancy_count"]
    == 912
)
assert (
    summary["industry_canonical_reference_raw_queue_count"]
    == industries["canonical_reference_review_queue_records"]
    == industry_effective["raw_queue_records"]
    == 4169
)
assert (
    summary["industry_canonical_reference_unclassified_count"]
    == industry_residuals["unclassified_reference_count_after_typing"]
    == 0
)
assert (
    summary["industry_canonical_reference_typed_residual_gap_count"]
    == industry_residuals["typed_residual_gap_count"]
)
assert (
    summary["industry_canonical_reference_ledger_disposition_count"]
    == industry_effective["ledger_disposition_records"]
    == 4029
)
assert (
    summary["industry_canonical_reference_research_resolved_count"]
    == industry_effective["ledger_research_resolved_candidate_records"]
    == 439
)
assert (
    summary["industry_canonical_reference_machine_review_candidate_count"]
    == industry_review["source_candidate_records"]
    == 137
)
assert summary["context_count"] == context_map["counts"]["contexts"] == 144
assert summary["source_system_class_count"] == source_systems["class_records"] == 171
assert summary["data_shape_logical_count"] == data_shapes["counts"]["logical_shapes"] == 177
assert summary["provider_offer_seed_count"] == providers["counts"]["concrete_offers"] == 59
assert summary["program_level_gate_count"] == 5
assert summary["final_product_gate"] == "B15_TWO_RELEASE_CHANGE_AND_RATIFICATION"
assert summary["final_program_gate"] == "B20_CONTINUOUS_VALIDITY_AND_DECOMMISSION"
assert summary["completion_claim"] is False
assert (
    rows[4]["current"]["organization_family_membership_claims"]
    == effective_evidence_governance["effective_membership_claim_count"]
)
assert (
    rows[4]["current"]["unreviewed_weak_membership_claims"]
    == reviewed_evidence_frontier["open_weak_membership_claim_count"]
)
assert (
    rows[4]["current"]["reviewed_rejected_membership_claims"]
    == reviewed_evidence_frontier["rejected_reviewed_claim_count"]
)
assert (
    rows[4]["current"]["strong_exact_membership_claims"]
    == effective_evidence_governance["strong_exact_product_membership_claim_count"]
)
assert (
    rows[4]["current"]["strong_discovered_membership_claims"]
    == effective_evidence_governance["discovered_strong_membership_claim_count"]
)
assert (
    rows[5]["current"]["falsification_contracts"]
    == boundary_falsification["falsification_contract_count"]
)
assert (
    rows[6]["current"]["exact_semantic_contract_scopes"]
    == contract_scopes["semantic_contract_scope_count"]
)
assert rows[7]["current"]["ledger_dispositions"] == industry_effective["ledger_disposition_records"]
assert rows[8]["current"]["retained_occurrences"] == source_occurrences["retained_occurrence_count"]
assert (
    rows[8]["current"]["source_acquisition_identity_stages"] == len(source_topology["nodes"]) == 7
)
assert (
    rows[8]["current"]["complete_reference_chains"]
    == source_reference_chain["governed_data_cuts"]
    == 1
)
assert (
    rows[9]["current"]["end_to_end_closed_gaps"]
    == effective_shape_gaps["end_to_end_closed_gap_count"]
)
assert (
    rows[7]["current"]["typed_residual_gap_records"]
    == industry_residuals["typed_residual_gap_count"]
)
assert rows[7]["current"]["unclassified_reference_records"] == 0
assert rows[7]["current"]["semantic_ratifications"] == 0
assert rows[7]["current"]["machine_review_batches"] == industry_review["review_batch_count"] == 31
assert (
    rows[7]["current"]["machine_exact_alias_candidate_occurrences"]
    == industry_review["source_candidate_occurrences"]
    == 644
)
assert (
    rows[14]["current"]["nominal_gate_obligations"]
    == qualification["retained_product_count"] * 2 * 8
    == 1056
)
assert rows[16]["current"]["coverage_planes"] == len(coverage_planes)
assert rows[17]["current"]["ir_stages"] == synthesis["ir_stages"]
assert (
    rows[18]["current"]["human_work_decision_points"]
    == human_work["files"]["decision-points.jsonl"]["records"]
)
assert rows[18]["current"]["effect_boundary_routes"] == effect_boundary["target_member_routes"]
assert (
    rows[19]["current"]["structural_composition_pilots"]
    == vertical_acceptance["pilot_structural_compositions"]
)
assert (
    rows[20]["current"]["verified_change_events"]
    == change_intelligence["counts"]["verified-change-events"]
)
print(
    "PASS master closure frontier: 21 dependency-ordered batches (16 product/library + 5 program-level); live counts agree with authority summaries"
)
