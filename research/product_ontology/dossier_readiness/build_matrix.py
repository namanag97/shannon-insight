#!/usr/bin/env python3
"""Derive product-specific DDD and compiler-readiness gaps for retained products."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GLOBAL = ROOT / "research/product_ontology/global_boundary_research"
VERTICALS = ROOT / "research/product_ontology/composition_pilots/deterministic_verticals"
QUALIFICATION_SUBJECTS = ROOT / "research/product_ontology/qualification_program/library-qualification-subjects.jsonl"
QUALIFICATION_PROGRAMS = ROOT / "research/product_ontology/qualification_program/product-qualification-programs.jsonl"
P7 = ROOT / "research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p7_offer_binding_qualification"
P8 = ROOT / "research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p8_vertical_acceptance_tensor"
AS_OF = "2026-08-26"

DDD_FIELDS = [
    "domain_vision_statement",
    "subdomain_classification",
    "bounded_context_boundary",
    "ubiquitous_language_policy",
    "context_map",
    "anti_corruption_layers",
    "published_language",
    "value_objects",
    "entities",
    "aggregates",
    "aggregate_roots",
    "aggregate_invariants",
    "commands",
    "domain_events",
    "refusal_failure_catalog",
    "domain_services",
    "application_services",
    "repositories",
    "factories",
    "specifications",
    "state_machine",
    "policies_and_reactions",
    "sagas_and_process_managers",
    "read_models_and_projections",
    "integration_event_policy",
    "concurrency_and_idempotency",
    "time_model",
    "event_storming_swimlanes",
    "nonfunctional_laws",
]

LOCAL_PRODUCT_FIELDS = [
    "sovereign_question",
    "users",
    "harmed_parties",
    "jobs",
    "outcomes",
    "negative_mission",
    "lifecycle_states",
    "commands",
    "events",
    "invariants",
    "refusals",
    "automation_modality",
]

ADJUDICATION_RE = re.compile(
    r"^research/product_ontology/adjudications/(?P<bundle>[^/]+)/"
    r"boundary-decisions\.jsonl#(?P<decision>.+)$"
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def lines(rows: list[dict[str, Any]]) -> str:
    return "".join(canonical(row) + "\n" for row in rows)


def qualified_offer(row: dict[str, Any]) -> bool:
    status = str(row.get("status", ""))
    return bool(row.get("qualified_implementation_count", 0)) or (
        status.startswith("qualified") and "unqualified" not in status
    )


def portable_offer(row: dict[str, Any]) -> bool:
    return bool(row.get("portable") or row.get("portability_claim"))


def product_ref_matches(row: dict[str, Any], subject_ref: str) -> bool:
    return row.get("product_ref") == subject_ref or subject_ref in row.get("product_refs", [])


def derive() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    candidates = load_jsonl(GLOBAL / "product-archetypes.jsonl")
    retained = [
        row
        for row in candidates
        if row["boundary_evaluation"]["verdict"] in {"strong_product", "presumptive_product"}
    ]
    truth_by_candidate: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in load_jsonl(GLOBAL / "truth-applicability.jsonl"):
        truth_by_candidate[row["candidate_id"]].append(row)
    global_support = {
        "user_job_outcome": {
            row["candidate_id"] for row in load_jsonl(GLOBAL / "user-jobs-outcomes.jsonl")
        },
        "service_blueprint": {
            row["candidate_id"] for row in load_jsonl(GLOBAL / "service-blueprints.jsonl")
        },
        "lifecycle": {row["candidate_id"] for row in load_jsonl(GLOBAL / "lifecycle.jsonl")},
    }
    vertical_count: Counter[str] = Counter()
    for row in load_jsonl(VERTICALS / "vertical-compositions.jsonl"):
        for candidate_id in row["product_refs"]:
            vertical_count[candidate_id] += 1

    qualification_by_library = {
        row["abstract_library_ref"]: row for row in load_jsonl(QUALIFICATION_SUBJECTS)
    }

    readiness: list[dict[str, Any]] = []
    work: list[dict[str, Any]] = []
    compiler_gap_rebase: list[dict[str, Any]] = []
    for candidate in sorted(retained, key=lambda row: row["record_id"]):
        candidate_id = candidate["record_id"]
        ident = candidate_id.removeprefix("candidate.product.")
        evaluation = candidate["boundary_evaluation"]
        match = ADJUDICATION_RE.match(evaluation["adjudication_ref"])
        if not match:
            raise ValueError(f"{candidate_id}: malformed adjudication_ref")
        bundle = match.group("bundle")
        decision_id = match.group("decision")
        source_path = ROOT / f"research/product_ontology/adjudications/{bundle}/source.json"
        source = json.loads(source_path.read_text(encoding="utf-8"))
        decisions = {row["decision_id"]: row for row in source["boundary_decisions"]}
        decision = decisions[decision_id]
        subject_ref = decision["subject_ref"]
        artifact = next(
            (row for row in source.get("artifacts", []) if row.get("artifact_id") == subject_ref),
            {},
        )
        dossier = next(
            (row for row in source.get("ddd_dossiers", []) if row.get("product_ref") == subject_ref),
            None,
        )
        ddd = dossier.get("strategic_and_tactical_ddd", {}) if dossier else {}
        present_ddd = sorted(field for field in DDD_FIELDS if field in ddd and ddd[field] not in (None, [], {}))
        missing_ddd = sorted(set(DDD_FIELDS) - set(present_ddd))
        present_local = sorted(
            field for field in LOCAL_PRODUCT_FIELDS if artifact.get(field) not in (None, [], {})
        )

        libraries = source.get("libraries", [])
        requirements = source.get("requirements", [])
        maps = source.get("binding_maps", source.get("compiler_library_bindings", []))
        gaps = source.get("binding_gaps", [])
        semantic_gaps = source.get("semantic_gaps", [])
        offers = source.get("offers", [])
        product_libraries = [row for row in libraries if product_ref_matches(row, subject_ref)]
        product_requirements = [row for row in requirements if row.get("consumer_ref") == subject_ref]
        required_capabilities = sorted({row["capability_ref"] for row in product_requirements})
        provided_capabilities = sorted({ref for row in product_libraries for ref in row.get("provides", [])})
        local_artifacts = {row["artifact_id"]: row for row in source.get("artifacts", [])}
        product_owner_ref = artifact.get("semantic_owner_ref")
        internal_required_capabilities = sorted({
            row["capability_ref"]
            for row in product_requirements
            if (
                row["capability_ref"] in provided_capabilities
                or (
                    product_owner_ref is not None
                    and local_artifacts.get(row["capability_ref"], {}).get("semantic_owner_ref")
                    == product_owner_ref
                )
            )
        })
        imported_requirement_refs = sorted({
            row["capability_ref"]
            for row in product_requirements
            if row["capability_ref"] not in internal_required_capabilities
        })
        uncovered_capabilities = sorted(set(internal_required_capabilities) - set(provided_capabilities))
        product_maps = [row for row in maps if product_ref_matches(row, subject_ref)]
        product_gaps = [row for row in gaps if product_ref_matches(row, subject_ref)]
        product_semantic_gaps = [row for row in semantic_gaps if product_ref_matches(row, subject_ref)]
        qualified = sum(qualified_offer(row) for row in offers)
        portable = sum(portable_offer(row) for row in offers)
        structural_verticals = vertical_count[candidate_id]

        product_gap_resolutions = []
        for gap in product_gaps:
            abstract_refs = gap.get("abstract_library_refs") or [gap.get("abstract_library_ref")]
            matches = [qualification_by_library.get(ref) for ref in abstract_refs]
            contract_complete = bool(matches) and all(
                match is not None
                and set(match.get("contract", {}))
                >= {"types", "operations", "decisions", "invariants", "refusals", "dependencies"}
                for match in matches
            )
            if not contract_complete:
                continue
            for abstract_ref, match in zip(abstract_refs, matches):
                resolution = {
                    "record_id": f"rebase.{gap['gap_id']}",
                    "record_kind": "compiler_gap_research_rebase",
                    "source_gap_ref": gap["gap_id"],
                    "product_ref": subject_ref,
                    "abstract_library_ref": abstract_ref,
                    "qualification_subject_ref": match["subject_id"],
                    "contract_surface_present": sorted(match["contract"]),
                    "research_disposition": "EXACT_ABSTRACT_CONTRACT_PRESENT",
                    "remaining_gate": "CONCRETE_IMPLEMENTATION_AND_PROVIDER_QUALIFICATION",
                    "implementation_state": match["implementation_state"],
                    "qualified_implementation_refs": match["qualified_implementation_refs"],
                    "compiler_binding": "REFUSED_NO_QUALIFIED_OFFER",
                    "status": "RESEARCH_RESOLVED_DOWNSTREAM_GATED",
                    "completion_claim": False,
                }
                product_gap_resolutions.append(resolution)
                compiler_gap_rebase.append(resolution)
        unresolved_structural_gaps = {
            gap["gap_id"] for gap in product_gaps
        } - {row["source_gap_ref"] for row in product_gap_resolutions}

        if product_maps:
            mapping_status = "BLOCKED" if unresolved_structural_gaps or uncovered_capabilities else "STRUCTURALLY_MAPPED_UNQUALIFIED"
        else:
            mapping_status = "UNDETERMINED_PRODUCT_ATTRIBUTION"

        record = {
            "record_id": f"readiness.{ident}",
            "record_kind": "product_dossier_readiness",
            "as_of": AS_OF,
            "candidate_id": candidate_id,
            "name": candidate["name"],
            "family": candidate["family"],
            "boundary_verdict": evaluation["verdict"],
            "adjudication_bundle": bundle,
            "adjudication_decision_id": decision_id,
            "local_subject_ref": subject_ref,
            "boundary_adjudication": "PASS_EXACT_TRACE",
            "global_truth_profile": {
                "status": "PASS_STRUCTURAL" if len(truth_by_candidate[candidate_id]) == 110 else "MISSING",
                "truth_dimension_count": len(truth_by_candidate[candidate_id]),
                "warning": "Applicability coverage is not product-specific proof or acceptance.",
            },
            "global_generic_support": {
                name: candidate_id in refs for name, refs in global_support.items()
            },
            "local_product_field_coverage": {
                "present": present_local,
                "missing": sorted(set(LOCAL_PRODUCT_FIELDS) - set(present_local)),
                "present_count": len(present_local),
                "required_count": len(LOCAL_PRODUCT_FIELDS),
            },
            "product_specific_ddd": {
                "status": "COMPLETE_CANDIDATE_DOSSIER" if not missing_ddd else "MISSING_OR_INCOMPLETE",
                "dossier_ref": dossier.get("dossier_id") if dossier else None,
                "present_fields": present_ddd,
                "missing_fields": missing_ddd,
                "present_count": len(present_ddd),
                "required_count": len(DDD_FIELDS),
            },
            "library_and_compiler": {
                "bundle_library_count": len(libraries),
                "bundle_binding_map_count": len(maps),
                "explicit_product_library_count": len(product_libraries),
                "explicit_product_binding_map_count": len(product_maps),
                "explicit_product_binding_gap_count": len(product_gaps),
                "research_resolved_binding_gap_count": len(product_gap_resolutions),
                "open_structural_binding_gap_count": len(unresolved_structural_gaps),
                "implementation_binding_vacancy_count": len(product_gap_resolutions),
                "compiler_gap_rebase_refs": sorted(row["record_id"] for row in product_gap_resolutions),
                "explicit_product_semantic_gap_count": len(product_semantic_gaps),
                "declared_product_requirement_count": len(product_requirements),
                "required_capability_refs": required_capabilities,
                "internally_owned_required_capability_refs": internal_required_capabilities,
                "imported_product_provider_or_resource_requirement_refs": imported_requirement_refs,
                "provided_capability_refs": provided_capabilities,
                "uncovered_required_capability_refs": uncovered_capabilities,
                "uncovered_required_capability_count": len(uncovered_capabilities),
                "mapping_status": mapping_status,
                "attribution_warning": (
                    None
                    if product_libraries
                    else "Bundle-level libraries may exist, but no exact product_ref proves this product's complete decomposition."
                ),
            },
            "provider_readiness": {
                "observed_bundle_offer_count": len(offers),
                "qualified_offer_count": qualified,
                "portable_offer_count": portable,
                "status": "BLOCKED_NO_QUALIFIED_PORTABLE_OFFER" if not qualified or not portable else "EVIDENCED",
            },
            "vertical_proof": {
                "structural_composition_count": structural_verticals,
                "executed_acceptance_count": 0,
                "status": "STRUCTURAL_ONLY" if structural_verticals else "MISSING",
            },
            "ratification": "WITHHELD",
            "build_readiness": "NOT_BUILD_READY",
            "automation_law": {
                "default_posture": candidate["automation_modality"]["default_posture"],
                "deterministic_core_survives_removal": True,
                "generated_proposals_non_authoritative": True,
            },
        }
        readiness.append(record)

        def add_work(kind: str, statement: str, evidence_needed: list[str]) -> None:
            work.append(
                {
                    "record_id": f"work.{ident}.{kind}",
                    "record_kind": "product_closure_work_item",
                    "candidate_id": candidate_id,
                    "work_kind": kind,
                    "blocking": True,
                    "statement": statement,
                    "evidence_needed": evidence_needed,
                    "owner": "UNASSIGNED",
                    "status": "OPEN",
                }
            )

        if missing_ddd:
            add_work(
                "full_ddd_dossier",
                f"Create product-specific strategic/tactical DDD; {len(missing_ddd)} of {len(DDD_FIELDS)} required fields are absent.",
                ["complete 29-field dossier", "domain expert appraisal", "negative-twin review"],
            )
        if not product_libraries:
            add_work(
                "product_library_attribution",
                "Prove the exact product-to-library decomposition instead of relying on bundle-level proximity.",
                ["product_ref on every required library", "complete/non-overlapping ownership review"],
            )
        if not product_maps:
            add_work(
                "compiler_binding_map",
                "Map every product library to an exact compiler registry contract or a named blocking gap.",
                ["one map per product library", "typed gap for every missing exact contract"],
            )
        if unresolved_structural_gaps:
            add_work(
                "compiler_gap_closure",
                f"Close or explicitly retain {len(unresolved_structural_gaps)} exact product-specific compiler binding gaps.",
                ["semantic owner contribution", "law oracles", "independent conformance check"],
            )
        if uncovered_capabilities:
            add_work(
                "capability_decomposition_gap",
                f"Add exact owning libraries or narrow {len(uncovered_capabilities)} internally owned product capability requirements not provided by the attributed library set.",
                ["requirement-to-library coverage", "semantic owner", "invariants and refusals", "compiler map or typed gap"],
            )
        add_work(
            "provider_qualification",
            "Qualify at least one provider for execution and two independent implementations before portability is claimed.",
            ["current qualification receipts", "negative twins", "cross-provider differential", "exit drill"],
        )
        if structural_verticals < 2:
            add_work(
                "unrelated_vertical_generality",
                "Prove unchanged horizontal semantics in at least two unrelated enterprise verticals.",
                ["two structural compositions", "domain-owner acceptance criteria", "semantic diff"],
            )
        add_work(
            "executed_vertical_acceptance",
            "Execute product-specific vertical acceptance; structural composition alone is insufficient.",
            ["accepted source occurrence", "qualified provider", "runtime receipts", "domain-owner verdict"],
        )

    status_counts = Counter(row["product_specific_ddd"]["status"] for row in readiness)
    mapping_counts = Counter(row["library_and_compiler"]["mapping_status"] for row in readiness)
    summary = {
        "report_id": "retained_product_dossier_and_compiler_readiness",
        "as_of": AS_OF,
        "status": "CANDIDATE_GAP_MATRIX",
        "scope": "Every strong or presumptive product in the current finite global corpus.",
        "retained_product_count": len(readiness),
        "full_product_specific_ddd_count": sum(
            row["product_specific_ddd"]["status"] == "COMPLETE_CANDIDATE_DOSSIER"
            for row in readiness
        ),
        "missing_or_incomplete_ddd_count": sum(
            row["product_specific_ddd"]["status"] != "COMPLETE_CANDIDATE_DOSSIER"
            for row in readiness
        ),
        "explicit_product_library_attribution_count": sum(
            row["library_and_compiler"]["explicit_product_library_count"] > 0 for row in readiness
        ),
        "explicit_product_compiler_map_count": sum(
            row["library_and_compiler"]["explicit_product_binding_map_count"] > 0 for row in readiness
        ),
        "product_count_with_uncovered_required_capabilities": sum(
            row["library_and_compiler"]["uncovered_required_capability_count"] > 0
            for row in readiness
        ),
        "qualified_provider_product_count": sum(
            row["provider_readiness"]["qualified_offer_count"] > 0 for row in readiness
        ),
        "portable_provider_product_count": sum(
            row["provider_readiness"]["portable_offer_count"] > 0 for row in readiness
        ),
        "two_vertical_structural_product_count": sum(
            row["vertical_proof"]["structural_composition_count"] >= 2 for row in readiness
        ),
        "executed_vertical_acceptance_product_count": 0,
        "build_ready_product_count": 0,
        "open_work_item_count": len(work),
        "source_compiler_gap_count": sum(row["library_and_compiler"]["explicit_product_binding_gap_count"] for row in readiness),
        "research_resolved_compiler_gap_count": len(compiler_gap_rebase),
        "open_structural_compiler_gap_count": sum(row["library_and_compiler"]["open_structural_binding_gap_count"] for row in readiness),
        "implementation_binding_vacancy_count": len(compiler_gap_rebase),
        "ddd_status_counts": dict(sorted(status_counts.items())),
        "mapping_status_counts": dict(sorted(mapping_counts.items())),
        "laws": [
            "A boundary verdict is not a DDD dossier.",
            "A bundle-level library list is not an exact product decomposition.",
            "A compiler map is not provider qualification.",
            "Structural vertical composition is not executed domain acceptance.",
            "No model or agent may satisfy missing research, semantics, authority, qualification or acceptance evidence.",
        ],
    }
    return readiness, sorted(work, key=lambda row: row["record_id"]), sorted(compiler_gap_rebase, key=lambda row: row["record_id"]), summary


def build_closure_campaign(work: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Factor the flat product ledger onto reusable P7/P8 execution workstreams."""
    programs = {row["candidate_id"]: row for row in load_jsonl(QUALIFICATION_PROGRAMS)}
    profiles = load_jsonl(P7 / "qualification-profile-kernels.jsonl")
    p7_workstreams = load_jsonl(P7 / "conformance-context-workstreams.jsonl")
    p8_workstreams = load_jsonl(P8 / "acceptance-class-workstreams.jsonl")
    slot_dockets = load_jsonl(P8 / "product-vertical-slot-dockets.jsonl")

    profile_by_subject = {
        subject_ref: profile
        for profile in profiles
        for subject_ref in profile["subject_refs"]
    }
    p7_workstreams_by_subject: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for workstream in p7_workstreams:
        for subject_ref in workstream["subject_refs"]:
            p7_workstreams_by_subject[subject_ref].append(workstream)
    dockets_by_candidate: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for docket in slot_dockets:
        dockets_by_candidate[docket["candidate_ref"]].append(docket)

    projections: list[dict[str, Any]] = []
    for item in work:
        candidate_id = item["candidate_id"]
        if item["work_kind"] == "provider_qualification":
            subject_refs = programs[candidate_id]["library_subject_refs"]
            profile_rows = {profile_by_subject[ref]["profile_id"]: profile_by_subject[ref] for ref in subject_refs}
            workstream_rows = {
                row["workstream_id"]: row
                for ref in subject_refs
                for row in p7_workstreams_by_subject[ref]
            }
            projections.append({
                "record_id": f"projection.{item['record_id']}",
                "record_kind": "product_closure_workstream_projection",
                "work_item_ref": item["record_id"],
                "candidate_id": candidate_id,
                "work_kind": item["work_kind"],
                "subject_refs": sorted(subject_refs),
                "qualification_profile_refs": sorted(profile_rows),
                "shared_workstream_refs": sorted(workstream_rows),
                "exact_execution_refs": sorted({slot for row in profile_rows.values() for slot in row["implementation_slot_refs"]}),
                "execution_law": "Shared generators, oracles and evidence schemas may be built once; every exact scope and both independent implementation slots execute and receive separate verdicts.",
                "refusal_gate": "REFUSE_UNTIL_ALL_EXACT_SUBJECT_SCOPES_HAVE_TWO_CURRENT_INDEPENDENT_QUALIFICATION_RECEIPTS",
                "status": "ROUTED_EXECUTION_OPEN",
                "completion_claim": False,
            })
        elif item["work_kind"] == "unrelated_vertical_generality":
            dockets = dockets_by_candidate[candidate_id]
            projections.append({
                "record_id": f"projection.{item['record_id']}",
                "record_kind": "product_closure_workstream_projection",
                "work_item_ref": item["record_id"],
                "candidate_id": candidate_id,
                "work_kind": item["work_kind"],
                "subject_refs": [],
                "qualification_profile_refs": [],
                "shared_workstream_refs": ["campaign.product-readiness.vertical-slot-selection.v1"],
                "exact_execution_refs": sorted(row["docket_id"] for row in dockets),
                "execution_law": "Selection methodology is shared; each product retains two exact unrelated-vertical slots, a scope-equivalence proof and a named vertical authority.",
                "refusal_gate": "REFUSE_UNTIL_TWO_UNRELATED_STRUCTURAL_COMPOSITIONS_BIND_THE_EXACT_PRODUCT_SCOPE",
                "status": "ROUTED_EXECUTION_OPEN",
                "completion_claim": False,
            })
        elif item["work_kind"] == "executed_vertical_acceptance":
            dockets = dockets_by_candidate[candidate_id]
            applicable_workstreams = [row for row in p8_workstreams if candidate_id in row["candidate_refs"]]
            projections.append({
                "record_id": f"projection.{item['record_id']}",
                "record_kind": "product_closure_workstream_projection",
                "work_item_ref": item["record_id"],
                "candidate_id": candidate_id,
                "work_kind": item["work_kind"],
                "subject_refs": [],
                "qualification_profile_refs": [],
                "shared_workstream_refs": sorted(row["workstream_id"] for row in applicable_workstreams),
                "exact_execution_refs": sorted({ref for row in dockets for ref in row["acceptance_obligation_refs"]}),
                "execution_law": "Gate methods and evidence schemas are reusable; every product x unrelated-vertical slot x gate class executes under the same exact scope and receives a separate accountable verdict.",
                "refusal_gate": "REFUSE_UNTIL_BOTH_VERTICAL_SLOTS_HAVE_ALL_EIGHT_CURRENT_ACCEPTED_GATE_RECEIPTS",
                "status": "ROUTED_EXECUTION_OPEN",
                "completion_claim": False,
            })
        else:
            raise ValueError(f"unrouted closure work kind: {item['work_kind']}")

    provider_items = {row["candidate_id"]: row["work_item_ref"] for row in projections if row["work_kind"] == "provider_qualification"}
    acceptance_items = [row["work_item_ref"] for row in projections if row["work_kind"] == "executed_vertical_acceptance"]
    generality_items = [row["work_item_ref"] for row in projections if row["work_kind"] == "unrelated_vertical_generality"]
    campaigns: list[dict[str, Any]] = []
    for source in p7_workstreams:
        candidate_refs = sorted({
            candidate_id
            for candidate_id, program in programs.items()
            if set(program["library_subject_refs"]) & set(source["subject_refs"])
        })
        relevant_profiles = [
            row for row in profiles
            if set(row["subject_refs"]) & set(source["subject_refs"])
        ]
        campaigns.append({
            "campaign_id": source["workstream_id"],
            "record_kind": "product_readiness_reusable_campaign",
            "campaign_class": "QUALIFICATION_CONFORMANCE_METHOD",
            "source_workstream_ref": source["workstream_id"],
            "candidate_refs": candidate_refs,
            "product_work_item_refs": sorted(provider_items[ref] for ref in candidate_refs),
            "exact_profile_refs": sorted({row["profile_id"] for row in relevant_profiles}),
            "exact_execution_refs": sorted({slot for row in relevant_profiles for slot in row["implementation_slot_refs"]}),
            "depends_on_campaign_classes": ["RATIFIED_EXACT_CONTRACTS", "CONCRETE_IMPLEMENTATION_INTAKE"],
            "sharing_law": source["shared_assets_allowed"],
            "shared_verdict_forbidden": source["shared_verdict_forbidden"],
            "status": "OPEN_EXTERNAL_INPUTS_REQUIRED",
            "completion_claim": False,
        })
    campaigns.append({
        "campaign_id": "campaign.product-readiness.vertical-slot-selection.v1",
        "record_kind": "product_readiness_reusable_campaign",
        "campaign_class": "UNRELATED_VERTICAL_SLOT_SELECTION",
        "source_workstream_ref": None,
        "candidate_refs": sorted(row["candidate_id"] for row in projections if row["work_kind"] == "unrelated_vertical_generality"),
        "product_work_item_refs": sorted(generality_items),
        "exact_profile_refs": [],
        "exact_execution_refs": sorted(row["docket_id"] for candidate in dockets_by_candidate.values() for row in candidate if row["candidate_ref"] in {p["candidate_id"] for p in projections if p["work_kind"] == "unrelated_vertical_generality"}),
        "depends_on_campaign_classes": ["VERTICAL_DEMAND_SURFACE_AND_SCOPE_CENSUS"],
        "sharing_law": "Reuse unrelatedness and scope-equivalence tests; never share a product-specific vertical selection or acceptance verdict.",
        "shared_verdict_forbidden": True,
        "status": "OPEN_EXTERNAL_INPUTS_REQUIRED",
        "completion_claim": False,
    })
    for source in p8_workstreams:
        campaigns.append({
            "campaign_id": source["workstream_id"],
            "record_kind": "product_readiness_reusable_campaign",
            "campaign_class": "VERTICAL_ACCEPTANCE_GATE_METHOD",
            "source_workstream_ref": source["workstream_id"],
            "candidate_refs": source["candidate_refs"],
            "product_work_item_refs": sorted(acceptance_items),
            "exact_profile_refs": [],
            "exact_execution_refs": source["slot_obligation_refs"],
            "depends_on_campaign_classes": ["UNRELATED_VERTICAL_SLOT_SELECTION", "EXACT_SCOPE_IMPLEMENTATION_QUALIFICATION"],
            "sharing_law": source["sharing_law"],
            "shared_verdict_forbidden": True,
            "status": "OPEN_EXTERNAL_INPUTS_REQUIRED",
            "completion_claim": False,
        })

    dag = [
        {"stage": 1, "stage_id": "stage.product-readiness.authority-contracts-and-intake", "campaign_classes": ["RATIFIED_EXACT_CONTRACTS", "CONCRETE_IMPLEMENTATION_INTAKE", "VERTICAL_DEMAND_SURFACE_AND_SCOPE_CENSUS"], "exit_gate": "verified authority receipts, exact contract editions, implementation identities and candidate vertical scopes exist", "status": "OPEN", "completion_claim": False},
        {"stage": 2, "stage_id": "stage.product-readiness.shared-method-assets", "campaign_classes": ["QUALIFICATION_CONFORMANCE_METHOD", "UNRELATED_VERTICAL_SLOT_SELECTION"], "exit_gate": "shared deterministic generators, oracles, evidence schemas and exact slot selections exist without shared verdicts", "status": "OPEN", "completion_claim": False},
        {"stage": 3, "stage_id": "stage.product-readiness.exact-qualification", "campaign_classes": ["EXACT_SCOPE_IMPLEMENTATION_QUALIFICATION"], "exit_gate": "both independent implementation slots for every required product subject have current accepted qualification receipts", "status": "OPEN", "completion_claim": False},
        {"stage": 4, "stage_id": "stage.product-readiness.vertical-acceptance", "campaign_classes": ["VERTICAL_ACCEPTANCE_GATE_METHOD"], "exit_gate": "all eight gate classes pass in two unrelated vertical slots under named domain authorities", "status": "OPEN", "completion_claim": False},
        {"stage": 5, "stage_id": "stage.product-readiness.product-ratification", "campaign_classes": ["BUILD_READY_APPRAISAL_AND_RATIFICATION"], "exit_gate": "independent appraisal accepts completeness, portability, exit and residual-risk evidence", "status": "WITHHELD_DOWNSTREAM", "completion_claim": False},
    ]
    return sorted(projections, key=lambda row: row["record_id"]), sorted(campaigns, key=lambda row: row["campaign_id"]), dag


def output_payloads() -> dict[str, str]:
    readiness, work, compiler_gap_rebase, summary = derive()
    projections, campaigns, dag = build_closure_campaign(work)
    summary["closure_workstream_projection_count"] = len(projections)
    summary["reusable_campaign_count"] = len(campaigns)
    summary["campaign_stage_count"] = len(dag)
    payloads = {
        "product-readiness.jsonl": lines(readiness),
        "closure-work-items.jsonl": lines(work),
        "compiler-gap-rebase.jsonl": lines(compiler_gap_rebase),
        "closure-workstream-projection.jsonl": lines(projections),
        "reusable-closure-campaigns.jsonl": lines(campaigns),
        "closure-execution-dag.jsonl": lines(dag),
        "summary.json": json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    manifest = {
        "manifest_id": "retained_product_dossier_readiness_manifest",
        "as_of": AS_OF,
        "files": {
            name: {"sha256": digest(text), "bytes": len(text.encode("utf-8"))}
            for name, text in sorted(payloads.items())
        },
    }
    payloads["manifest.json"] = json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    return payloads


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payloads = output_payloads()
    mismatches = []
    for name, text in payloads.items():
        path = HERE / name
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                mismatches.append(name)
        else:
            path.write_text(text, encoding="utf-8")
    if mismatches:
        print("ERROR stale readiness outputs: " + ", ".join(mismatches))
        return 1
    print(("CHECK" if args.check else "BUILD") + " PASS: 8 deterministic readiness outputs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
