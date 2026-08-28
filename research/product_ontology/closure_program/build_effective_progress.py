#!/usr/bin/env python3
# Generates the current B00-B20 effective portfolio projection from committed authority corpora.
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def J(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def L(p):
    return [json.loads(x) for x in (ROOT / p).read_text(encoding="utf-8").splitlines() if x.strip()]


def exists(p):
    return (ROOT / p).exists()


def main():
    master = L("research/product_ontology/closure_program/expanded-batches.jsonl")
    q = J("research/product_ontology/qualification_program/effective-summary.json")
    b04 = J(
        "research/analytics_landscape/product_families/effective-evidence-governance-summary.json"
    )
    b04_review = J(
        "research/analytics_landscape/product_families/effective-evidence-frontier-summary.json"
    )
    b05 = J(
        "research/product_ontology/dossier_readiness/product-boundary-falsification-summary.json"
    )
    b06 = J("research/product_ontology/qualification_program/contract-scope-summary.json")
    b07 = J("research/domain_atlas/industries/canonical-reference-auto-alias-summary.json")
    b07_current = (
        J("research/domain_atlas/industries/canonical-reference-current-method-summary.json")
        if exists(
            "research/domain_atlas/industries/canonical-reference-current-method-summary.json"
        )
        else {"candidate_records": 0, "candidate_occurrences": 0}
    )
    occ = J("research/domain_atlas/universes/source_systems/occurrence-registry-summary.json")
    dsg = J("research/domain_atlas/universes/data_shapes/effective-gap-summary.json")
    ctx_route = (
        J("research/domain_atlas/context_map/effective-gap-routing-summary.json")
        if exists("research/domain_atlas/context_map/effective-gap-routing-summary.json")
        else J("research/domain_atlas/context_map/manifest.json")
    )
    harness = J("research/product_ontology/qualification_program/harness-campaign-summary.json")
    program = J("research/product_ontology/closure_program/program-work-surfaces-summary.json")
    statuses = {}
    statuses["B00_TRUTH_CONVERGENCE"] = {
        "state": "STRUCTURALLY_DONE_MONITOR",
        "remaining": "future generated-corpus freshness/digest enforcement",
        "machine_addressable": True,
    }
    closure = json.loads(
        (ROOT / "research/product_ontology/closure_program/summary.json").read_text()
    )
    b01_unprepared = closure["source_authority_unprepared_family_count"]
    statuses["B01_SOURCE_AUTHORITY"] = {
        "state": "AUTHORITY_BLOCKED_RESEARCH_PREPARED_INDEPENDENT_VERIFICATION_REQUIRED"
        if b01_unprepared == 0
        else "RESEARCH_AND_AUTHORITY_BLOCKED",
        "remaining": {
            "prepared_awaiting_ratification": closure["source_authority_prepared_payload_count"],
            "unprepared_research_residual": b01_unprepared,
            "ratified": 0,
            "independently_verified": 0,
        },
        "machine_addressable": b01_unprepared > 0,
    }
    statuses["B02_SEMANTIC_OWNER_UNIQUENESS"] = {
        "state": "PARTIAL_RESEARCH_AUTHORITY_BLOCKED",
        "remaining": "8 legacy ambiguities research-adjudicated; global uniqueness proof and accountable ratification remain",
        "machine_addressable": True,
    }
    context_gap_count = ctx_route.get("gap_count", ctx_route.get("counts", {}).get("gaps"))
    statuses["B03_CONTEXT_MAP_RATIFICATION"] = {
        "state": "ROUTED_RESEARCH_AUTHORITY_AND_EVIDENCE_OPEN",
        "remaining": {
            "routed_context_gaps": context_gap_count,
            "unrouted": ctx_route.get("unrouted_gap_count", 0),
        },
        "machine_addressable": True,
    }
    statuses["B04_HORIZONTAL_EVIDENCE_GOVERNANCE"] = {
        "state": "MACHINE_ACTIVE",
        "remaining": {
            "unreviewed_weak_memberships": b04_review["open_weak_membership_claim_count"],
            "reviewed_rejected_memberships": b04_review["rejected_reviewed_claim_count"],
            "strong_exact_memberships": b04["strong_exact_product_membership_claim_count"],
            "strong_discovered_memberships": b04["discovered_strong_membership_claim_count"],
            "organization_identity_graphs": 232,
        },
        "machine_addressable": True,
    }
    statuses["B05_PRODUCT_BOUNDARY_FALSIFICATION"] = {
        "state": "STRUCTURAL_FALSIFICATION_DONE_EXTERNAL_EVIDENCE_OPEN",
        "remaining": {
            "independent_adoption": b05["retained_product_count"]
            - b05["product_specific_independent_adoption_evidence_complete_count"],
            "economic_exit": b05["retained_product_count"]
            - b05["product_specific_economic_exit_evidence_complete_count"],
            "ratification": b05["retained_product_count"] - b05["ratified_boundary_count"],
        },
        "machine_addressable": True,
    }
    statuses["B06_LIBRARY_CONTRACT_AUTHORITY"] = {
        "state": "STRUCTURAL_SCOPE_DONE_AUTHORITY_BLOCKED",
        "remaining": {
            "exact_semantic_scopes": b06["semantic_contract_scope_count"],
            "ratified": b06["ratified_contract_scope_count"],
        },
        "machine_addressable": False,
    }
    effective_b07 = max(
        0,
        b07["remaining_without_manual_or_machine_exact_candidate"]
        - b07_current.get("candidate_records", 0),
    )
    statuses["B07_INDUSTRY_CANONICAL_REFERENCE_CLOSURE"] = {
        "state": "MACHINE_ACTIVE_SEMANTIC_REVIEW",
        "remaining": {
            "unclassified_reference_rows": effective_b07,
            "machine_exact_candidates": b07["machine_exact_alias_candidate_records"]
            + b07_current.get("candidate_records", 0),
        },
        "machine_addressable": True,
    }
    statuses["B08_SOURCE_SYSTEM_AND_OCCURRENCE_CLOSURE"] = {
        "state": "MACHINE_ACTIVE",
        "remaining": {
            "retained_occurrences": occ["retained_occurrence_count"],
            "source_classes_with_occurrence": occ["source_class_count_with_retained_occurrence"],
            "source_classes_without_retained_occurrence": 171
            - occ["source_class_count_with_retained_occurrence"],
            "production_qualified_occurrences": occ["production_qualified_occurrence_count"],
        },
        "machine_addressable": True,
    }
    statuses["B09_DATA_SHAPE_OPERATION_TOTALITY"] = {
        "state": "MACHINE_ACTIVE",
        "remaining": {
            "historical_gaps": dsg["historical_gap_count"],
            "end_to_end_closed": dsg["end_to_end_closed_gap_count"],
            "current_dispositions_explicit": True,
        },
        "machine_addressable": True,
    }
    statuses["B10_IMPLEMENTATION_IDENTITY_AND_BUILD"] = {
        "state": "MACHINE_ACTIVE_FACTORED",
        "remaining": {
            "exact_contract_scopes": harness["semantic_contract_scope_count"],
            "harness_campaigns": harness["harness_campaign_count"],
            "qualification_verdicts": harness["qualification_verdicts_created"],
        },
        "machine_addressable": True,
    }
    statuses["B11_EXACT_SCOPE_CONFORMANCE_AND_INDEPENDENT_APPRAISAL"] = {
        "state": "MACHINE_ACTIVE_FACTORED_INDEPENDENCE_BLOCKED",
        "remaining": {
            "harness_campaigns": harness["harness_campaign_count"],
            "exact_scope_verdicts_required": harness["semantic_contract_scope_count"],
            "independent_appraisal_still_required": True,
        },
        "machine_addressable": True,
    }
    for bid in [
        "B12_SECOND_IMPLEMENTATION_PORTABILITY_EXIT",
        "B13_PHYSICAL_BINDING_SLO_SECURITY_COST",
        "B14_TWO_VERTICAL_EXECUTED_ACCEPTANCE",
        "B15_TWO_RELEASE_CHANGE_AND_RATIFICATION",
    ]:
        statuses[bid] = {
            "state": "DOWNSTREAM_PHYSICAL_OR_INDEPENDENT_EVIDENCE_BLOCKED",
            "remaining": "see qualification, provider-target and vertical-acceptance ledgers",
            "machine_addressable": False,
        }
    statuses["B16_OPEN_WORLD_COVERAGE_AND_NOVELTY"] = {
        "state": "MACHINE_ACTIVE",
        "remaining": {
            "coverage_coordinates": program["b16_coverage_coordinates"],
            "occupation_coordinates": program.get("b16_occupation_major_group_coordinates", 0),
            "profession_foundation_missing": program.get(
                "b16_missing_profession_foundation", False
            ),
            "accepted_novelty_runs": 0,
        },
        "machine_addressable": True,
    }
    statuses["B17_INTENT_TO_SOLUTION_SYNTHESIS"] = {
        "state": "MACHINE_ACTIVE_STRUCTURAL_SEEDS",
        "remaining": {
            "seeded_solution_challenges": program["b17_seeded_solution_challenges"],
            "accepted": 0,
        },
        "machine_addressable": True,
    }
    statuses["B18_APPLICATION_HUMAN_AUTHORITY_AND_EFFECT"] = {
        "state": "MACHINE_ACTIVE_UNEXECUTED",
        "remaining": program["b18_human_effect_obligations"],
        "machine_addressable": True,
    }
    statuses["B19_MULTI_PRODUCT_SYSTEM_ACCEPTANCE"] = {
        "state": "MACHINE_ACTIVE_REQUIRES_PHYSICAL_STACK",
        "remaining": program["b19_system_fault_obligations"],
        "machine_addressable": True,
    }
    statuses["B20_CONTINUOUS_VALIDITY_AND_DECOMMISSION"] = {
        "state": "MACHINE_ACTIVE_UNEXECUTED",
        "remaining": program["b20_invalidation_obligations"],
        "machine_addressable": True,
    }
    rows = []
    for b in master:
        s = statuses[b["batch_id"]]
        rows.append(
            {
                "batch_id": b["batch_id"],
                "depends_on": b.get("depends_on", []),
                "effective_state": s["state"],
                "remaining": s["remaining"],
                "machine_addressable_now": s["machine_addressable"],
                "exit_condition": b["exit_condition"],
                "completion_claim": False,
            }
        )
    (HERE / "effective-batch-progress.jsonl").write_text(
        "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8"
    )
    program_obligations = (
        program["b16_coverage_coordinates"]
        + program["b17_seeded_solution_challenges"]
        + program["b18_human_effect_obligations"]
        + program["b19_system_fault_obligations"]
        + program["b20_invalidation_obligations"]
    )
    summary = {
        "report_id": "effective_batched_closure_progress",
        "as_of": "2026-08-27",
        "batch_count": len(rows),
        "structurally_done_or_done_monitor_count": sum(
            "DONE" in r["effective_state"] for r in rows
        ),
        "machine_addressable_batch_count": sum(r["machine_addressable_now"] for r in rows),
        "authority_or_external_evidence_blocked_batch_count": sum(
            (
                "AUTHORITY_BLOCKED" in r["effective_state"]
                or "EVIDENCE_BLOCKED" in r["effective_state"]
                or "INDEPENDENCE_BLOCKED" in r["effective_state"]
            )
            for r in rows
        ),
        "effective_qualification_vacancies": q["effective_evidence_vacancy_count"],
        "program_level_obligation_count": program_obligations,
        "program_level_acceptance_results": program["program_gate_acceptance_results"],
        "largest_machine_queue": {
            "batch_id": "B07_INDUSTRY_CANONICAL_REFERENCE_CLOSURE",
            "count": effective_b07,
        },
        "retained_source_occurrences": occ["retained_occurrence_count"],
        "exact_contract_scopes": harness["semantic_contract_scope_count"],
        "qualification_harness_campaigns": harness["harness_campaign_count"],
        "completion_claim": False,
    }
    (HERE / "effective-progress-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
