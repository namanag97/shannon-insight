#!/usr/bin/env python3
"""Compile heterogeneous open work into a batched semantic gap topology."""
from __future__ import annotations

import collections
import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
RESEARCH = SEM.parents[4]
QUALIFICATION = RESEARCH / "product_ontology/qualification_program"
CONTRACT_GENERATION = SEM.parent
AS_OF = "2026-08-27"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


ONTOLOGY = {
    "ontology_id": "ontology.semantic-gap-control.v1",
    "edition": 1,
    "as_of": AS_OF,
    "question": "What is unknown, missing, ambiguous, conflicting or unproved; where does it live; what does it block; and what exact evidence and authority can close it?",
    "non_collapse_laws": [
        "missing structure is not missing domain coverage",
        "evidence presence is not evidence sufficiency",
        "candidate semantics are not owner-ratified semantics",
        "a specified contract is not an implemented contract",
        "one passing implementation is not portability",
        "validation is not source authority",
        "closing a parent gap does not close library-local residuals",
    ],
    "classification_axes": [
        {"axis": "defect_kind", "values": ["MISSING", "UNKNOWN", "AMBIGUOUS", "CONFLICTING", "UNBOUND", "UNRATIFIED", "UNIMPLEMENTED", "UNQUALIFIED", "STALE"]},
        {"axis": "locus", "values": ["SOURCE_CORPUS", "SEMANTIC_FOUNDATION", "FAMILY_AXIS_MODULE", "PUBLIC_SYMBOL", "LIBRARY_CONTRACT", "COMPILER_BINDING", "IMPLEMENTATION", "QUALIFICATION"]},
        {"axis": "scope_grain", "values": ["SYMBOL", "OPERATION", "LIBRARY", "FAMILY_AXIS", "FAMILY", "PRODUCT", "VERTICAL", "GLOBAL"]},
        {"axis": "epistemic_state", "values": ["DISCOVERY", "CANDIDATE", "CONTESTED", "DECISION_READY", "RATIFIED", "OBSERVED"]},
        {"axis": "closure_operation", "values": ["REPAIR_STRUCTURE", "RESEARCH", "ADJUDICATE", "RATIFY", "SPECIFY", "IMPLEMENT", "QUALIFY", "PROPAGATE"]},
        {"axis": "closure_authority", "values": ["CORPUS_MAINTAINER", "SEMANTIC_OWNER", "FAMILY_OWNER", "LIBRARY_OWNER", "IMPLEMENTER", "INDEPENDENT_APPRAISER", "PRODUCT_ACCEPTANCE_OWNER"]},
        {"axis": "evidence_kind", "values": ["PRIMARY_SOURCE", "CONFLICT_APPRAISAL", "OWNER_DECISION", "EXACT_SCHEMA", "EXECUTABLE_ORACLE", "IMPLEMENTATION_RECEIPT", "INDEPENDENT_DIFFERENTIAL", "PRODUCT_ACCEPTANCE"]},
        {"axis": "dependency_role", "values": ["ROOT_CAUSE", "BLOCKER", "RESIDUAL", "DUPLICATE", "REFINEMENT", "DOWNSTREAM_SYMPTOM"]},
        {"axis": "blast_radius", "values": ["LOCAL", "FAMILY", "CROSS_FAMILY", "GLOBAL_COMPILER"]},
        {"axis": "lifecycle", "values": ["OPEN", "DECOMPOSED", "EVIDENCE_READY", "DECISION_READY", "DECIDED", "IMPLEMENTED", "QUALIFIED", "CLOSED", "REOPENED"]},
        {"axis": "reuse_layer", "values": ["SOURCE_CONCEPT_SCHEME", "GLOBAL_CONSTITUTION", "SHARED_PRIMITIVE", "CONTRACT_ARCHETYPE", "FAMILY_PROFILE", "CONTEXT_PROFILE", "LIBRARY_INSTANCE", "IMPLEMENTATION_OFFER", "PRODUCT_ASSEMBLY", "VERTICAL_SOLUTION_PACK"]},
        {"axis": "decision_shape", "values": ["GLOBAL_LAW", "SHARED_CARRIER", "STRUCTURAL_OBLIGATION", "FAMILY_DEFAULT", "EXCEPTION_CLUSTER", "LOCAL_RESIDUAL", "EXACT_CONTRACT", "PROVIDER_OFFER", "QUALIFICATION_GATE", "PRODUCT_ACCEPTANCE"]},
        {"axis": "propagation_mode", "values": ["IMPORT_EXACT", "INHERIT_OBLIGATIONS", "PROFILE", "COMPOSE", "MAP_WITH_LOSS", "OVERRIDE_WITH_EVIDENCE", "NO_PROPAGATION"]},
        {"axis": "adjudication_outcome", "values": ["IMPORT_AS_IS", "IMPORT_QUALIFIED", "SPECIALIZE", "COMPOSE", "RETAIN_LOCAL", "SPLIT", "MERGE", "RENAME", "REPLACE", "RETIRE", "BLOCK"]},
        {"axis": "closure_gate", "values": ["STRUCTURE_READY", "SOURCE_AUTHORITY_RATIFIED", "SEMANTICS_RATIFIED", "EXACT_CONTRACT_VALID", "IMPLEMENTATION_PROVED", "PORTABILITY_QUALIFIED", "PRODUCT_ACCEPTED", "VERTICAL_ACCEPTED"]},
    ],
    "semantic_axis_ref": "../semantic-axis-ontology.json",
}

PROGRAMS = [
    ("P00", "source-structure", [], "REPAIR_STRUCTURE", "CORPUS_MAINTAINER", "Make generated schemas, manifests, explicit gaps and deterministic validators trustworthy."),
    ("P01", "source-authority", ["P00"], "ADJUDICATE", "FAMILY_OWNER", "Decide which upstream schema and records may supply candidate contract inputs."),
    ("P02", "shared-symbol-ownership", ["P01"], "ADJUDICATE", "SEMANTIC_OWNER", "Resolve repeated public symbols into shared imports, qualified homonyms or rejected duplicates."),
    ("P03", "family-axis-evidence", ["P01"], "RESEARCH", "FAMILY_OWNER", "Produce bounded evidence once per family-axis instead of once per library."),
    ("P04", "applicability-ratification", ["P02", "P03"], "RATIFY", "LIBRARY_OWNER", "Ratify clustered axis applicability and isolate only true library-local exceptions."),
    ("P05", "exact-contract-specification", ["P02", "P04"], "SPECIFY", "LIBRARY_OWNER", "Lower shared modules plus local residual decisions into exact public contracts."),
    ("P06", "implementation", ["P05"], "IMPLEMENT", "IMPLEMENTER", "Implement exact contracts without inventing unresolved semantic defaults."),
    ("P07", "qualification-and-product-acceptance", ["P06"], "QUALIFY", "INDEPENDENT_APPRAISER", "Require executable laws, independent differentials and product-specific acceptance."),
]


def program_rows() -> list[dict[str, Any]]:
    return [{"record_kind": "gap_closure_program", "program_id": pid, "name": name, "depends_on_program_refs": deps, "closure_operation": op, "owner_role": owner, "outcome": outcome, "status": "OPEN", "completion_claim": False} for pid, name, deps, op, owner, outcome in PROGRAMS]


def cluster(
    kind: str,
    key: str,
    program: str,
    atoms: int,
    families: list[str],
    axes: list[str],
    defect: str,
    locus: str,
    scope: str,
    evidence: list[str],
    blocked: list[str],
    *,
    affected: list[str] | None = None,
    reuse_layer: str,
    decision_shape: str,
    propagation_mode: str,
) -> dict[str, Any]:
    affected_refs = sorted(set(affected or families))
    return {
        "record_kind": "semantic_gap_cluster",
        "cluster_id": f"gap-cluster.{kind}.{key}",
        "gap_kind": kind,
        "program_ref": program,
        "atom_count": atoms,
        "family_refs": sorted(set(families)),
        "affected_scope_refs": affected_refs,
        "semantic_axes": sorted(set(axes)),
        "defect_kind": defect,
        "locus": locus,
        "scope_grain": scope,
        "reuse_layer": reuse_layer,
        "decision_shape": decision_shape,
        "propagation_mode": propagation_mode,
        "required_evidence_kinds": evidence,
        "blocked_outputs": blocked,
        "fanout_score": max(1, atoms) * max(1, len(affected_refs)),
        "lifecycle": "DECOMPOSED",
        "canonical_gaps_closed": 0,
        "status": "OPEN_BATCHABLE_CLUSTER",
    }


METHOD_SIGNATURE_FIELDS = (
    "program_ref",
    "gap_kind",
    "defect_kind",
    "locus",
    "scope_grain",
    "reuse_layer",
    "decision_shape",
    "propagation_mode",
    "required_evidence_kinds",
)


def closure_method_kernels(clusters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Factor reusable closure mechanics without sharing semantic conclusions."""
    programs = {row["program_id"]: row for row in program_rows()}
    grouped: dict[str, tuple[dict[str, Any], list[dict[str, Any]]]] = {}
    for row in clusters:
        signature = {field: row[field] for field in METHOD_SIGNATURE_FIELDS}
        key = canonical(signature)
        grouped.setdefault(key, (signature, []))[1].append(row)

    kernels = []
    for signature_key, (signature, members) in sorted(grouped.items()):
        digest = hashlib.sha256(signature_key.encode()).hexdigest()[:16]
        program = programs[signature["program_ref"]]
        kernels.append({
            "record_kind": "semantic_gap_closure_method_kernel",
            "method_kernel_id": f"method.semantic-gap.{signature['program_ref'].lower()}.{signature['gap_kind']}.{digest}",
            "signature": signature,
            "closure_operation": program["closure_operation"],
            "closure_authority": program["owner_role"],
            "member_cluster_refs": sorted(row["cluster_id"] for row in members),
            "member_cluster_count": len(members),
            "represented_atom_count": sum(row["atom_count"] for row in members),
            "semantic_axis_refs": sorted({axis for row in members for axis in row["semantic_axes"]}),
            "family_refs": sorted({family for row in members for family in row["family_refs"]}),
            "affected_scope_count": len({ref for row in members for ref in row["affected_scope_refs"]}),
            "shareable_assets": [
                "question_and_review_protocol",
                "evidence_and_receipt_schema",
                "validator_or_conformance_harness_generator",
                "negative_test_pattern",
            ],
            "non_shareable_decisions": [
                "semantic_identity_or_meaning",
                "owner_or_authority_receipt",
                "family_or_library_applicability",
                "implementation_or_provider_verdict",
                "product_or_vertical_acceptance",
            ],
            "canonical_gaps_closed": 0,
            "status": "PLANNED_NOT_EXECUTED",
            "completion_claim": False,
        })
    return kernels


def execution_band(
    band_id: str,
    order: int,
    name: str,
    depends_on: list[str],
    clusters: list[dict[str, Any]],
    parallel_lanes: list[str],
    exit_gate: str,
) -> dict[str, Any]:
    return {
        "record_kind": "semantic_gap_macro_execution_band",
        "band_id": band_id,
        "order": order,
        "name": name,
        "depends_on_band_refs": depends_on,
        "program_refs": sorted({row["program_ref"] for row in clusters}),
        "cluster_refs": sorted(row["cluster_id"] for row in clusters),
        "cluster_count": len(clusters),
        "represented_atom_count": sum(row["atom_count"] for row in clusters),
        "parallel_lane_refs": parallel_lanes,
        "parallelism_law": "Lanes may run concurrently only when their named owners, evidence sets and target records are independent; every result remains separately attributable.",
        "exit_gate": exit_gate,
        "status": "PLANNED_NOT_EXECUTED",
        "completion_claim": False,
    }


def build() -> dict[str, Any]:
    exact = load_jsonl(SEM / "structured_projection/exact-contract-input-candidates.jsonl")
    targeted = load_jsonl(SEM / "structured_projection/targeted-evidence-work-packages.jsonl")
    decisions = load_jsonl(SEM / "applicability_matrices/family-axis-decision-clusters.jsonl")
    authorities = load_jsonl(SEM / "source_authority_audit/readiness-audits.jsonl")
    researched_symbols = load_jsonl(SEM / "p1_authority_symbols/high-fanout-semantic-research.jsonl")
    remaining_symbol_batches = load_jsonl(SEM / "p1_authority_symbols/remaining-symbol-research-batches.jsonl")
    symbol_archetype_programs = load_jsonl(SEM / "p1_authority_symbols/archetype-research-programs.jsonl")
    p2_summary = load_json(SEM / "p2_owner_adjudication/summary.json")
    p1b_summary = load_json(SEM / "p1b_foundation_authority_adjudication/summary.json")
    p2_dockets = load_jsonl(SEM / "p2_owner_adjudication/owner-adjudication-dockets.jsonl")
    p2_occurrences = load_jsonl(SEM / "p2_owner_adjudication/occurrence-disposition-candidates.jsonl")
    p2_units = load_jsonl(SEM / "p2_owner_adjudication/owner-decision-units.jsonl")
    p2_waves = load_jsonl(SEM / "p2_owner_adjudication/owner-decision-waves.jsonl")
    p2_owner_proposals = load_jsonl(SEM / "p2_owner_adjudication/owner-proposals.jsonl")
    p2_occurrence_proposals = load_jsonl(SEM / "p2_owner_adjudication/occurrence-relation-proposals.jsonl")
    p2_proposal_conflicts = load_jsonl(SEM / "p2_owner_adjudication/proposal-conflicts.jsonl")
    p2_proposal_counterfactuals = load_jsonl(SEM / "p2_owner_adjudication/owner-proposal-counterfactuals.jsonl")
    p2_challenge_packages = load_jsonl(SEM / "p2_owner_adjudication/owner-adjudication-challenge-packages.jsonl")
    p2_ratification_templates = load_jsonl(SEM / "p2_owner_adjudication/owner-ratification-packet-templates.jsonl")
    p3_summary = load_json(SEM / "p3_applicability_adjudication/summary.json")
    p3e_summary = load_json(SEM / "p3e_grain_cardinality_evidence/summary.json")
    p3e_grain_coordinate_summary = load_json(SEM / "p3e_grain_coordinate_ontology/summary.json")
    p3s_summary = load_json(SEM / "p3s_state_change_evidence/summary.json")
    p3s_state_change_coordinate_summary = load_json(SEM / "p3s_state_change_coordinate_ontology/summary.json")
    p3o_summary = load_json(SEM / "p3o_order_topology_evidence/summary.json")
    p3o_order_topology_coordinate_summary = load_json(SEM / "p3o_order_topology_coordinate_ontology/summary.json")
    p3c_summary = load_json(SEM / "p3c_composition_algebra_evidence/summary.json")
    p3c_composition_algebra_coordinate_summary = load_json(SEM / "p3c_composition_algebra_coordinate_ontology/summary.json")
    p3i_summary = load_json(SEM / "p3i_identity_equality_evidence/summary.json")
    p3i_identity_equality_coordinate_summary = load_json(SEM / "p3i_identity_equality_coordinate_ontology/summary.json")
    p3u_summary = load_json(SEM / "p3u_partiality_uncertainty_evidence/summary.json")
    p3u_partiality_uncertainty_coordinate_summary = load_json(SEM / "p3u_partiality_uncertainty_coordinate_ontology/summary.json")
    time_coordinate_summary = load_json(SEM / "time_coordinate_ontology/summary.json")
    semantic_object_coordinate_summary = load_json(SEM / "semantic_object_coordinate_ontology/summary.json")
    semantic_role_coordinate_summary = load_json(SEM / "semantic_role_coordinate_ontology/summary.json")
    authority_trust_coordinate_summary = load_json(SEM / "authority_trust_coordinate_ontology/summary.json")
    effect_boundary_coordinate_summary = load_json(SEM / "effect_boundary_coordinate_ontology/summary.json")
    evidence_conformance_coordinate_summary = load_json(SEM / "evidence_conformance_coordinate_ontology/summary.json")
    representation_coordinate_summary = load_json(SEM / "representation_coordinate_ontology/summary.json")
    compatibility_evolution_coordinate_summary = load_json(SEM / "compatibility_evolution_coordinate_ontology/summary.json")
    privacy_security_safety_coordinate_summary = load_json(SEM / "privacy_security_safety_coordinate_ontology/summary.json")
    resources_failure_coordinate_summary = load_json(SEM / "resources_failure_coordinate_ontology/summary.json")
    targeted_evidence_coverage_summary = load_json(SEM / "targeted_evidence_coverage/summary.json")
    semantic_research_frontier_summary = load_json(SEM / "semantic_research_frontier/summary.json")
    semantic_decision_locus_summary = load_json(SEM / "semantic_decision_locus_ontology/summary.json")
    p4_summary = load_json(SEM / "p4_ratification_ingestion/summary.json")
    p5_summary = load_json(SEM / "p5_exact_contract_adjudication/summary.json")
    p6_summary = load_json(SEM / "p6_implementation_qualification/summary.json")
    p7_summary = load_json(SEM / "p7_offer_binding_qualification/summary.json")
    p8_summary = load_json(SEM / "p8_vertical_acceptance_tensor/summary.json")
    semantic_phases = load_jsonl(SEM / "semantic-execution-phases.jsonl")
    product_vacancies = load_jsonl(QUALIFICATION / "evidence-vacancies.jsonl")
    product_programs = load_jsonl(QUALIFICATION / "product-qualification-programs.jsonl")
    vertical_programs = load_jsonl(QUALIFICATION / "product-vertical-acceptance-programs.jsonl")
    archetypes = load_jsonl(CONTRACT_GENERATION / "contract-archetypes.jsonl")
    semantic_axes = {x["axis"] for x in load_json(SEM / "semantic-axis-ontology.json")["axes"]}
    clusters: list[dict[str, Any]] = []

    for row in authorities:
        missing = row["missing_or_failed_controls"]
        if missing:
            clusters.append(cluster("source-structure", row["family_id"].split(".")[-1], "P00", len(missing), [row["family_id"]], [], "MISSING", "SOURCE_CORPUS", "FAMILY", ["EXACT_SCHEMA", "EXECUTABLE_ORACLE"], ["source authority decision"], reuse_layer="SOURCE_CONCEPT_SCHEME", decision_shape="STRUCTURAL_OBLIGATION", propagation_mode="NO_PROPAGATION"))
        clusters.append(cluster("source-authority", row["family_id"].split(".")[-1], "P01", 1, [row["family_id"]], [], "UNRATIFIED", "SOURCE_CORPUS", "FAMILY", ["PRIMARY_SOURCE", "CONFLICT_APPRAISAL", "OWNER_DECISION"], ["family-axis evidence", "exact contract specification"], reuse_layer="SOURCE_CONCEPT_SCHEME", decision_shape="FAMILY_DEFAULT", propagation_mode="IMPORT_EXACT"))

    for row in researched_symbols:
        key = row["symbol_ref"].replace(".", "-")
        affected = [item["library_ref"] for item in row["affected_occurrences"]]
        clusters.append(cluster("researched-symbol-owner", key, "P02", 1, row["affected_family_refs"], ["identity_and_equality"], "UNRATIFIED", "PUBLIC_SYMBOL", "SYMBOL", ["PRIMARY_SOURCE", "CONFLICT_APPRAISAL", "OWNER_DECISION", "EXACT_SCHEMA"], ["public type graph", "exact contracts", "compiler lowering"], affected=affected, reuse_layer="SHARED_PRIMITIVE", decision_shape="SHARED_CARRIER", propagation_mode="PROFILE"))

    for row in remaining_symbol_batches:
        key = row["batch_id"].removeprefix("batch.p1.remaining-symbols.").removesuffix(".v1")
        primary_research_complete = row.get("research_state") == "BOUNDED_PRIMARY_RESEARCH_COMPLETE"
        clusters.append(cluster(
            "symbol-owner-adjudication-batch" if primary_research_complete else "symbol-research-batch",
            key,
            "P02",
            row["packet_count"],
            row["family_refs"],
            ["identity_and_equality"],
            "UNRATIFIED" if primary_research_complete else ("AMBIGUOUS" if row["definition_conflict_count"] == 0 else "CONFLICTING"),
            "PUBLIC_SYMBOL",
            "GLOBAL",
            ["CONFLICT_APPRAISAL", "OWNER_DECISION", "EXACT_SCHEMA"] if primary_research_complete else ["PRIMARY_SOURCE", "CONFLICT_APPRAISAL", "OWNER_DECISION", "EXACT_SCHEMA"],
            ["public type graph", "exact contracts", "compiler lowering"],
            affected=row["packet_refs"],
            reuse_layer="SHARED_PRIMITIVE",
            decision_shape="SHARED_CARRIER",
            propagation_mode="PROFILE",
        ))

    for row in targeted:
        key = f"{row['family_id'].split('.')[-1]}.{row['axis'].replace('_','-')}"
        clusters.append(cluster("family-axis-evidence", key, "P03", row["library_count"], [row["family_id"]], [row["axis"]], "MISSING", "FAMILY_AXIS_MODULE", "FAMILY_AXIS", ["PRIMARY_SOURCE", "CONFLICT_APPRAISAL"], ["applicability ratification"], reuse_layer="FAMILY_PROFILE", decision_shape="FAMILY_DEFAULT", propagation_mode="PROFILE"))

    decision_groups: dict[tuple[str, str], list[dict[str, Any]]] = collections.defaultdict(list)
    for row in decisions:
        decision_groups[(row["family_id"], row["axis"])].append(row)
    for (family, axis), rows in sorted(decision_groups.items()):
        key = f"{family.split('.')[-1]}.{axis.replace('_','-')}"
        members = [ref for row in rows for ref in row["member_preclassification_refs"]]
        clusters.append(cluster("applicability", key, "P04", sum(r["member_count"] for r in rows), [family], [axis], "UNRATIFIED", "FAMILY_AXIS_MODULE", "FAMILY_AXIS", ["OWNER_DECISION"], ["exact contract specification"], affected=members, reuse_layer="FAMILY_PROFILE", decision_shape="EXCEPTION_CLUSTER", propagation_mode="OVERRIDE_WITH_EVIDENCE"))

    exact_groups: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in exact:
        exact_groups[row["family_id"]].append(row)
    for family, rows in sorted(exact_groups.items()):
        library_refs = [row["library_ref"] for row in rows]
        clusters.append(cluster("exact-contract", family.split(".")[-1], "P05", len(rows), [family], sorted(semantic_axes), "UNRATIFIED", "LIBRARY_CONTRACT", "FAMILY", ["OWNER_DECISION", "EXACT_SCHEMA", "EXECUTABLE_ORACLE"], ["compiler binding", "implementation", "qualification"], affected=library_refs, reuse_layer="LIBRARY_INSTANCE", decision_shape="EXACT_CONTRACT", propagation_mode="INHERIT_OBLIGATIONS"))
        clusters.append(cluster("implementation", family.split(".")[-1], "P06", len(rows), [family], [], "UNIMPLEMENTED", "IMPLEMENTATION", "FAMILY", ["IMPLEMENTATION_RECEIPT", "EXECUTABLE_ORACLE"], ["qualification", "product acceptance"], affected=library_refs, reuse_layer="IMPLEMENTATION_OFFER", decision_shape="PROVIDER_OFFER", propagation_mode="MAP_WITH_LOSS"))
        clusters.append(cluster("qualification", family.split(".")[-1], "P07", len(rows), [family], [], "UNQUALIFIED", "QUALIFICATION", "FAMILY", ["INDEPENDENT_DIFFERENTIAL", "PRODUCT_ACCEPTANCE"], ["selectable compiler offer", "completion claim"], affected=library_refs, reuse_layer="IMPLEMENTATION_OFFER", decision_shape="QUALIFICATION_GATE", propagation_mode="NO_PROPAGATION"))

    vacancy_groups: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in product_vacancies:
        vacancy_groups[row["gate_ref"]].append(row)
    for gate_ref, rows in sorted(vacancy_groups.items()):
        gate_key = gate_ref.removeprefix("gate.qp.").replace("_", "-")
        is_vertical = gate_ref in {"gate.qp.two_vertical_structures", "gate.qp.executed_vertical_acceptance"}
        clusters.append(cluster("product-gate", gate_key, "P07", len(rows), [], [], "UNQUALIFIED", "QUALIFICATION", "PRODUCT", ["IMPLEMENTATION_RECEIPT", "INDEPENDENT_DIFFERENTIAL", "PRODUCT_ACCEPTANCE"], ["product ratification", "build-ready verdict", "vertical solution selection"], affected=[row["candidate_id"] for row in rows], reuse_layer="VERTICAL_SOLUTION_PACK" if is_vertical else "PRODUCT_ASSEMBLY", decision_shape="PRODUCT_ACCEPTANCE" if is_vertical else "QUALIFICATION_GATE", propagation_mode="NO_PROPAGATION"))

    program_rank = {pid: index for index, (pid, *_rest) in enumerate(PROGRAMS)}
    clusters.sort(key=lambda x: (program_rank[x["program_ref"]], -x["fanout_score"], x["cluster_id"]))
    for rank, row in enumerate(clusters, 1):
        row["execution_rank"] = rank
    method_kernels = closure_method_kernels(clusters)

    bands: list[dict[str, Any]] = []
    source_clusters = [row for row in clusters if row["program_ref"] in {"P00", "P01"}]
    bands.append(execution_band("band.semantic-closure.01-source", 1, "Source structure and authority", [], source_clusters, [row["family_refs"][0] for row in source_clusters if row["family_refs"]], "All 23 family sources have exact current receipts and a bounded owner authority decision."))
    symbol_clusters = [row for row in clusters if row["program_ref"] == "P02"]
    symbol_coordination_lanes = [row["research_id"] for row in researched_symbols] + [row["research_program_id"] for row in symbol_archetype_programs]
    owner_decision_lanes = [row["wave_id"] for row in p2_waves]
    bands.append(execution_band("band.semantic-closure.02-symbols", 2, "Shared symbol semantics and ownership", ["band.semantic-closure.01-source"], symbol_clusters, owner_decision_lanes, "All 210 symbol packets have a content-addressed owner disposition and all 666 occurrences have an explicit owner declaration, exact/profiled import, qualified homonym, migration, retirement or rejection decision."))

    previous = "band.semantic-closure.02-symbols"
    for index, phase in enumerate(semantic_phases, 3):
        axes = {ref.removeprefix("lane.semantic-axis.").replace("-", "_") for ref in phase["axis_lane_refs"]}
        phase_clusters = [row for row in clusters if row["program_ref"] in {"P03", "P04"} and set(row["semantic_axes"]) <= axes]
        band_id = f"band.semantic-closure.{index:02d}-axis-phase-{index - 2}"
        bands.append(execution_band(band_id, index, phase["phase_id"].split(".")[-1].replace("-", " ").title(), [previous], phase_clusters, phase["axis_lane_refs"], phase["exit_gate"]))
        previous = band_id

    exact_clusters = [row for row in clusters if row["program_ref"] == "P05"]
    bands.append(execution_band("band.semantic-closure.08-contracts", 8, "Exact contract lowering", [previous], exact_clusters, sorted({row["family_refs"][0] for row in exact_clusters}), "Every library has an owner-ratified exact contract or an explicit blocked residual; compiler binding stays fail-closed otherwise."))
    implementation_clusters = [row for row in clusters if row["program_ref"] == "P06"]
    bands.append(execution_band("band.semantic-closure.09-implementation", 9, "Implementation offers", ["band.semantic-closure.08-contracts"], implementation_clusters, [row["archetype_id"] for row in archetypes], "Implementations bind exact contract editions and emit reproducible build, runtime and conformance receipts."))
    qualification_clusters = [row for row in clusters if row["program_ref"] == "P07"]
    bands.append(execution_band("band.semantic-closure.10-qualification", 10, "Qualification, products and vertical acceptance", ["band.semantic-closure.09-implementation"], qualification_clusters, sorted(vacancy_groups), "Independent qualification, portability, product acceptance and two unrelated executed verticals are evidenced for the same immutable scope."))

    by_program = collections.Counter(row["program_ref"] for row in clusters)
    atoms_by_program = collections.Counter()
    for row in clusters:
        atoms_by_program[row["program_ref"]] += row["atom_count"]
    open_primary_batches = [row for row in remaining_symbol_batches if row.get("research_state") == "OPEN_PRIMARY_RESEARCH"]
    researched_archetype_batches = [row for row in remaining_symbol_batches if row.get("research_state") == "BOUNDED_PRIMARY_RESEARCH_COMPLETE"]
    summary = {
        "program_id": "program.semantic-gap-topology.v1",
        "edition": 1,
        "as_of": AS_OF,
        "completion_claim": False,
        "gap_clusters": len(clusters),
        "represented_gap_atoms": sum(row["atom_count"] for row in clusters),
        "closure_method_kernels": len(method_kernels),
        "closure_programs": len(PROGRAMS),
        "clusters_by_program": dict(sorted(by_program.items())),
        "atoms_by_program": dict(sorted(atoms_by_program.items())),
        "source_authorities_ratified": 0,
        "foundation_authority_templates": p1b_summary["ratification_packet_templates"],
        "foundation_authority_templates_ready_for_review": p1b_summary["authority_review_ready_templates"],
        "foundation_authority_templates_blocked": p1b_summary["blocked_templates"],
        "canonical_exact_gaps_closed": 0,
        "symbol_owner_execution_units": len(p2_units),
        "symbol_owner_decision_waves": len(p2_waves),
        "symbol_owner_adjudication_dockets": len(p2_dockets),
        "symbol_occurrence_disposition_candidates": len(p2_occurrences),
        "symbol_owner_proposals": len(p2_owner_proposals),
        "symbol_owner_proposals_with_named_candidates": p2_summary["owner_proposals_with_named_candidates"],
        "symbol_owner_proposals_blocked": p2_summary["owner_proposals_blocked"],
        "symbol_occurrence_relation_proposals": len(p2_occurrence_proposals),
        "symbol_occurrence_relation_proposals_unresolved": p2_summary["occurrence_relation_proposals_unresolved"],
        "symbol_owner_proposal_conflicts": len(p2_proposal_conflicts),
        "symbol_owner_proposal_counterfactuals": len(p2_proposal_counterfactuals),
        "symbol_owner_proposal_counterfactual_instabilities": p2_summary["counterfactually_unstable_owner_proposals"],
        "symbol_owner_challenge_packages": len(p2_challenge_packages),
        "symbol_owner_ratification_packet_templates": len(p2_ratification_templates),
        "symbol_owner_ratification_packet_templates_ready_for_review": p2_summary["ratification_packet_templates_ready_for_authority_review"],
        "family_axis_applicability_dockets": p3_summary["family_axis_dockets"],
        "family_axis_applicability_review_packages": p3_summary["review_packages"],
        "family_axis_applicability_review_ready": p3_summary["review_ready_dockets"],
        "family_axis_applicability_blocked": p3_summary["blocked_dockets"],
        "grain_cardinality_evidence_candidates": p3e_summary["primary_evidence_candidates"],
        "grain_cardinality_evidence_dockets": p3e_summary["family_dockets"],
        "grain_cardinality_evidence_represented_library_occurrences": p3e_summary["represented_library_occurrences"],
        "grain_coordinate_transformation_kernels": p3e_grain_coordinate_summary["transformation_kernels"],
        "grain_coordinate_member_routes": p3e_grain_coordinate_summary["target_member_routes"],
        "grain_coordinate_research_clusters": p3e_grain_coordinate_summary["research_clusters"],
        "grain_coordinate_operation_profiles_supplied": p3e_grain_coordinate_summary["operation_positioned_profiles_supplied"],
        "state_change_evidence_candidates": p3s_summary["primary_evidence_candidates"],
        "state_change_evidence_dockets": p3s_summary["family_dockets"],
        "state_change_evidence_represented_library_occurrences": p3s_summary["represented_library_occurrences"],
        "state_change_subject_archetypes": p3s_state_change_coordinate_summary["state_subject_archetypes"],
        "state_change_transition_kernels": p3s_state_change_coordinate_summary["transition_kernels"],
        "state_change_member_routes": p3s_state_change_coordinate_summary["target_member_routes"],
        "state_change_research_clusters": p3s_state_change_coordinate_summary["research_clusters"],
        "state_change_subject_profiles_supplied": p3s_state_change_coordinate_summary["state_subject_profiles_supplied"],
        "order_topology_evidence_candidates": p3o_summary["primary_evidence_candidates"],
        "order_topology_evidence_dockets": p3o_summary["family_dockets"],
        "order_topology_evidence_represented_library_occurrences": p3o_summary["represented_library_occurrences"],
        "order_topology_relation_archetypes": p3o_order_topology_coordinate_summary["relation_archetypes"],
        "order_topology_relation_kernels": p3o_order_topology_coordinate_summary["relation_kernels"],
        "order_topology_member_routes": p3o_order_topology_coordinate_summary["target_member_routes"],
        "order_topology_research_clusters": p3o_order_topology_coordinate_summary["research_clusters"],
        "order_topology_relation_profiles_supplied": p3o_order_topology_coordinate_summary["relation_coordinate_profiles_supplied"],
        "composition_algebra_evidence_candidates": p3c_summary["primary_evidence_candidates"],
        "composition_algebra_evidence_dockets": p3c_summary["family_dockets"],
        "composition_algebra_evidence_represented_library_occurrences": p3c_summary["represented_library_occurrences"],
        "composition_algebra_operator_archetypes": p3c_composition_algebra_coordinate_summary["operator_archetypes"],
        "composition_algebra_operator_kernels": p3c_composition_algebra_coordinate_summary["operator_kernels"],
        "composition_algebra_member_routes": p3c_composition_algebra_coordinate_summary["target_member_routes"],
        "composition_algebra_research_clusters": p3c_composition_algebra_coordinate_summary["research_clusters"],
        "composition_algebra_operator_profiles_supplied": p3c_composition_algebra_coordinate_summary["operator_coordinate_profiles_supplied"],
        "identity_equality_evidence_candidates": p3i_summary["primary_evidence_candidates"],
        "identity_equality_evidence_dockets": p3i_summary["family_dockets"],
        "identity_equality_evidence_represented_library_occurrences": p3i_summary["represented_library_occurrences"],
        "identity_equality_bearer_archetypes": p3i_identity_equality_coordinate_summary["identity_bearer_archetypes"],
        "identity_equality_kernels": p3i_identity_equality_coordinate_summary["identity_equality_kernels"],
        "identity_equality_member_routes": p3i_identity_equality_coordinate_summary["target_member_routes"],
        "identity_equality_research_clusters": p3i_identity_equality_coordinate_summary["research_clusters"],
        "identity_equality_relation_profiles_supplied": p3i_identity_equality_coordinate_summary["identity_equality_relation_profiles_supplied"],
        "partiality_uncertainty_evidence_candidates": p3u_summary["primary_evidence_candidates"],
        "partiality_uncertainty_evidence_dockets": p3u_summary["family_dockets"],
        "partiality_uncertainty_evidence_represented_library_occurrences": p3u_summary["represented_library_occurrences"],
        "partiality_uncertainty_bearer_archetypes": p3u_partiality_uncertainty_coordinate_summary["bearer_archetypes"],
        "partiality_uncertainty_kernels": p3u_partiality_uncertainty_coordinate_summary["partiality_uncertainty_kernels"],
        "partiality_uncertainty_member_routes": p3u_partiality_uncertainty_coordinate_summary["target_member_routes"],
        "partiality_uncertainty_research_clusters": p3u_partiality_uncertainty_coordinate_summary["research_clusters"],
        "partiality_uncertainty_profiles_supplied": p3u_partiality_uncertainty_coordinate_summary["partiality_uncertainty_profiles_supplied"],
        "time_temporal_bearer_archetypes": time_coordinate_summary["temporal_bearer_archetypes"],
        "time_temporal_operation_kernels": time_coordinate_summary["temporal_operation_kernels"],
        "time_structural_family_dockets": time_coordinate_summary["structural_family_dockets"],
        "time_member_routes": time_coordinate_summary["target_member_routes"],
        "time_research_clusters": time_coordinate_summary["research_clusters"],
        "time_family_source_evidence_bindings_supplied": time_coordinate_summary["family_source_evidence_bindings_supplied"],
        "time_coordinate_profiles_supplied": time_coordinate_summary["time_coordinate_profiles_supplied"],
        "semantic_object_bearer_archetypes": semantic_object_coordinate_summary["semantic_object_bearer_archetypes"],
        "semantic_object_operation_kernels": semantic_object_coordinate_summary["semantic_object_operation_kernels"],
        "semantic_object_structural_family_dockets": semantic_object_coordinate_summary["structural_family_dockets"],
        "semantic_object_member_routes": semantic_object_coordinate_summary["target_member_routes"],
        "semantic_object_research_clusters": semantic_object_coordinate_summary["research_clusters"],
        "semantic_object_family_source_evidence_bindings_supplied": semantic_object_coordinate_summary["family_source_evidence_bindings_supplied"],
        "semantic_object_coordinate_profiles_supplied": semantic_object_coordinate_summary["semantic_object_coordinate_profiles_supplied"],
        "semantic_role_archetypes": semantic_role_coordinate_summary["semantic_role_archetypes"],
        "semantic_role_operation_kernels": semantic_role_coordinate_summary["semantic_role_operation_kernels"],
        "semantic_role_structural_family_dockets": semantic_role_coordinate_summary["structural_family_dockets"],
        "semantic_role_member_routes": semantic_role_coordinate_summary["target_member_routes"],
        "semantic_role_research_clusters": semantic_role_coordinate_summary["research_clusters"],
        "semantic_role_family_source_evidence_bindings_supplied": semantic_role_coordinate_summary["family_source_evidence_bindings_supplied"],
        "semantic_role_coordinate_profiles_supplied": semantic_role_coordinate_summary["semantic_role_coordinate_profiles_supplied"],
        "authority_trust_bearer_archetypes": authority_trust_coordinate_summary["authority_trust_bearer_archetypes"],
        "authority_trust_operation_kernels": authority_trust_coordinate_summary["authority_trust_operation_kernels"],
        "authority_trust_structural_family_dockets": authority_trust_coordinate_summary["structural_family_dockets"],
        "authority_trust_member_routes": authority_trust_coordinate_summary["target_member_routes"],
        "authority_trust_research_clusters": authority_trust_coordinate_summary["research_clusters"],
        "authority_trust_family_source_evidence_bindings_supplied": authority_trust_coordinate_summary["family_source_evidence_bindings_supplied"],
        "authority_trust_coordinate_profiles_supplied": authority_trust_coordinate_summary["authority_trust_coordinate_profiles_supplied"],
        "effect_boundary_bearer_archetypes": effect_boundary_coordinate_summary["effect_boundary_bearer_archetypes"],
        "effect_boundary_operation_kernels": effect_boundary_coordinate_summary["effect_boundary_operation_kernels"],
        "effect_boundary_structural_family_dockets": effect_boundary_coordinate_summary["structural_family_dockets"],
        "effect_boundary_member_routes": effect_boundary_coordinate_summary["target_member_routes"],
        "effect_boundary_research_clusters": effect_boundary_coordinate_summary["research_clusters"],
        "effect_boundary_family_source_evidence_bindings_supplied": effect_boundary_coordinate_summary["family_source_evidence_bindings_supplied"],
        "effect_boundary_coordinate_profiles_supplied": effect_boundary_coordinate_summary["effect_boundary_coordinate_profiles_supplied"],
        "evidence_conformance_bearer_archetypes": evidence_conformance_coordinate_summary["evidence_conformance_bearer_archetypes"],
        "evidence_conformance_operation_kernels": evidence_conformance_coordinate_summary["evidence_conformance_operation_kernels"],
        "evidence_conformance_structural_family_dockets": evidence_conformance_coordinate_summary["structural_family_dockets"],
        "evidence_conformance_member_routes": evidence_conformance_coordinate_summary["target_member_routes"],
        "evidence_conformance_research_clusters": evidence_conformance_coordinate_summary["research_clusters"],
        "evidence_conformance_family_source_evidence_bindings_supplied": evidence_conformance_coordinate_summary["family_source_evidence_bindings_supplied"],
        "evidence_conformance_coordinate_profiles_supplied": evidence_conformance_coordinate_summary["evidence_conformance_coordinate_profiles_supplied"],
        "representation_bearer_archetypes": representation_coordinate_summary["representation_bearer_archetypes"],
        "representation_operation_kernels": representation_coordinate_summary["representation_operation_kernels"],
        "representation_structural_family_dockets": representation_coordinate_summary["structural_family_dockets"],
        "representation_member_routes": representation_coordinate_summary["target_member_routes"],
        "representation_research_clusters": representation_coordinate_summary["research_clusters"],
        "representation_family_source_evidence_bindings_supplied": representation_coordinate_summary["family_source_evidence_bindings_supplied"],
        "representation_directional_preservation_profiles_supplied": representation_coordinate_summary["directional_preservation_profiles_supplied"],
        "compatibility_evolution_bearer_archetypes": compatibility_evolution_coordinate_summary["compatibility_evolution_bearer_archetypes"],
        "compatibility_evolution_operation_kernels": compatibility_evolution_coordinate_summary["compatibility_evolution_operation_kernels"],
        "compatibility_evolution_structural_family_dockets": compatibility_evolution_coordinate_summary["structural_family_dockets"],
        "compatibility_evolution_member_routes": compatibility_evolution_coordinate_summary["target_member_routes"],
        "compatibility_evolution_research_clusters": compatibility_evolution_coordinate_summary["research_clusters"],
        "compatibility_evolution_family_source_evidence_bindings_supplied": compatibility_evolution_coordinate_summary["family_source_evidence_bindings_supplied"],
        "compatibility_evolution_directional_vectors_supplied": compatibility_evolution_coordinate_summary["directional_compatibility_vectors_supplied"],
        "compatibility_evolution_change_lifecycle_profiles_supplied": compatibility_evolution_coordinate_summary["change_lifecycle_profiles_supplied"],
        "privacy_security_safety_bearer_archetypes": privacy_security_safety_coordinate_summary["privacy_security_safety_bearer_archetypes"],
        "privacy_security_safety_operation_kernels": privacy_security_safety_coordinate_summary["privacy_security_safety_operation_kernels"],
        "privacy_security_safety_structural_family_dockets": privacy_security_safety_coordinate_summary["structural_family_dockets"],
        "privacy_security_safety_member_routes": privacy_security_safety_coordinate_summary["target_member_routes"],
        "privacy_security_safety_research_clusters": privacy_security_safety_coordinate_summary["research_clusters"],
        "privacy_security_safety_family_source_evidence_bindings_supplied": privacy_security_safety_coordinate_summary["family_source_evidence_bindings_supplied"],
        "privacy_profiles_supplied": privacy_security_safety_coordinate_summary["privacy_profiles_supplied"],
        "security_profiles_supplied": privacy_security_safety_coordinate_summary["security_profiles_supplied"],
        "safety_profiles_supplied": privacy_security_safety_coordinate_summary["safety_profiles_supplied"],
        "resources_failure_bearer_archetypes": resources_failure_coordinate_summary["resources_failure_bearer_archetypes"],
        "resources_failure_operation_kernels": resources_failure_coordinate_summary["resources_failure_operation_kernels"],
        "resources_failure_structural_family_dockets": resources_failure_coordinate_summary["structural_family_dockets"],
        "resources_failure_member_routes": resources_failure_coordinate_summary["target_member_routes"],
        "resources_failure_research_clusters": resources_failure_coordinate_summary["research_clusters"],
        "resources_failure_family_source_evidence_bindings_supplied": resources_failure_coordinate_summary["family_source_evidence_bindings_supplied"],
        "finite_resource_profiles_supplied": resources_failure_coordinate_summary["finite_resource_profiles_supplied"],
        "total_failure_profiles_supplied": resources_failure_coordinate_summary["total_failure_profiles_supplied"],
        "targeted_evidence_axes": targeted_evidence_coverage_summary["targeted_axes"],
        "targeted_evidence_work_packages": targeted_evidence_coverage_summary["targeted_work_packages"],
        "targeted_evidence_library_occurrences": targeted_evidence_coverage_summary["targeted_library_occurrences"],
        "targeted_evidence_unrouted_axes": len(targeted_evidence_coverage_summary["unrouted_axes"]),
        "targeted_evidence_unrouted_work_packages": targeted_evidence_coverage_summary["unrouted_work_packages"],
        "semantic_frontier_axes": semantic_research_frontier_summary["semantic_axes"],
        "semantic_frontier_lanes": semantic_research_frontier_summary["research_lanes"],
        "semantic_frontier_member_axis_cells": semantic_research_frontier_summary["member_axis_cells"],
        "semantic_frontier_review_ready_dockets": semantic_research_frontier_summary["review_ready_dockets"],
        "semantic_frontier_blocked_dockets": semantic_research_frontier_summary["blocked_dockets"],
        "semantic_decision_bearer_archetypes": semantic_decision_locus_summary["bearer_archetypes"],
        "semantic_decision_axis_profiles": semantic_decision_locus_summary["semantic_axis_profiles"],
        "semantic_decision_family_axis_factorizations": semantic_decision_locus_summary["family_axis_factorizations"],
        "semantic_decision_member_axis_cells_preserved": semantic_decision_locus_summary["member_axis_cells_preserved"],
        "semantic_decision_coordinate_refined_axes": semantic_decision_locus_summary["coordinate_refined_axes"],
        "semantic_decision_coordinate_refined_target_member_routes": semantic_decision_locus_summary["coordinate_refined_target_member_routes"],
        "ratification_ingestion_templates": p4_summary["total_templates"],
        "ratification_ingestion_verified": p4_summary["verified_ratifications"],
        "canonical_delta_candidates": p4_summary["canonical_delta_candidates"],
        "exact_contract_adjudication_dockets": p5_summary["exact_contract_dockets"],
        "exact_contract_archetype_kernels": p5_summary["archetype_obligation_kernels"],
        "exact_contract_family_kernels": p5_summary["family_semantic_kernels"],
        "exact_contract_execution_packages": p5_summary["execution_packages"],
        "exact_contract_lowering_gates": p5_summary["compiler_lowering_gates"],
        "implementation_concrete_reference_resolutions": p6_summary["concrete_reference_resolutions"],
        "implementation_qualification_scope_kernels": p6_summary["qualification_scope_kernels"],
        "implementation_shared_qualification_scopes": p6_summary["shared_qualification_scope_kernels"],
        "implementation_independent_slots": p6_summary["implementation_slots"],
        "implementation_subject_dockets": p6_summary["subject_dockets"],
        "implementation_evidence_vacancy_packages": p6_summary["evidence_vacancy_packages"],
        "implementation_compiler_selection_gates": p6_summary["selection_gates"],
        "implementation_product_dockets": p6_summary["product_qualification_dockets"],
        "qualified_implementations": p6_summary["qualified_implementations"],
        "selected_implementation_offers": p6_summary["selected_implementation_offers"],
        "build_ready_products": p6_summary["build_ready_products"],
        "implementation_qualification_profile_kernels": p7_summary["qualification_profile_kernels"],
        "implementation_conformance_context_workstreams": p7_summary["conformance_context_workstreams"],
        "implementation_represented_context_obligations": p7_summary["represented_subject_context_occurrences"],
        "implementation_offer_intake_templates": p7_summary["implementation_offer_intake_templates"],
        "semantic_physical_binding_gates": p7_summary["semantic_physical_binding_gates"],
        "authorized_semantic_physical_bridges": p7_summary["authorized_semantic_physical_bridges"],
        "vertical_acceptance_slots": p8_summary["unrelated_vertical_slots"],
        "vertical_acceptance_gate_classes": p8_summary["acceptance_gate_classes"],
        "vertical_acceptance_slot_gate_obligations": p8_summary["slot_gate_obligations"],
        "vertical_acceptance_products_with_structural_pilots": p8_summary["products_with_any_structural_pilot"],
        "vertical_acceptance_products_with_two_structural_pilots": p8_summary["products_with_two_unrelated_structural_pilots"],
        "executed_vertical_acceptances": p8_summary["executed_vertical_acceptances"],
        "ratified_symbol_owners": p2_summary["ratified_symbol_owners"],
        "ratified_symbol_occurrence_dispositions": p2_summary["ratified_occurrence_dispositions"],
        "symbol_packets_with_bounded_primary_research": len(researched_symbols) + sum(row["packet_count"] for row in researched_archetype_batches),
        "symbol_packets_open_primary_research": sum(row["packet_count"] for row in open_primary_batches),
        "open_primary_research_archetypes": sorted({row["research_archetype"] for row in open_primary_batches}),
        "symbol_packets_still_requiring_owner_adjudication": len(p2_dockets),
        "symbol_research_coordination_programs": len(symbol_archetype_programs),
        "symbol_research_coordination_lanes": len(symbol_coordination_lanes),
        "archetype_semantic_axis_research_lanes": sum(len(row["semantic_axis_refs"]) for row in symbol_archetype_programs),
        "product_gate_execution_units": len(vacancy_groups),
        "represented_product_evidence_vacancies": len(product_vacancies),
        "strategy": "Close root semantic and authority decisions at the highest valid reusable layer, inherit them by exact digest, then adjudicate only residual library-local differences.",
    }
    lattice = {
        "lattice_id": "lattice.semantic-closure-compression.v1",
        "edition": 1,
        "as_of": AS_OF,
        "completion_claim": False,
        "closure_law": "Adjudicate at the highest semantically valid reusable layer; inherit exact obligations downward; preserve every lower-layer exception, authority decision and evidence gate.",
        "levels": [
            {"rank": 0, "reuse_layer": "SOURCE_CONCEPT_SCHEME", "member_count": len(authorities), "open_execution_units": len(authorities), "owns": "source vocabulary, editions and evidence authority", "cannot_own": "SAN semantic meaning"},
            {"rank": 1, "reuse_layer": "GLOBAL_CONSTITUTION", "member_count": len(semantic_axes), "open_execution_units": len(semantic_axes), "owns": "cross-domain questions and non-collapse laws", "cannot_own": "family vocabulary or applicability"},
            {"rank": 2, "reuse_layer": "SHARED_PRIMITIVE", "member_count": sum(row["packet_count"] for row in remaining_symbol_batches) + len(researched_symbols), "open_execution_units": len(remaining_symbol_batches) + len(researched_symbols), "owns": "one exact shared carrier or qualified homonym decision", "cannot_own": "library-local residuals"},
            {"rank": 3, "reuse_layer": "CONTRACT_ARCHETYPE", "member_count": len(archetypes), "open_execution_units": len(archetypes), "owns": "structural type, operation, refusal and oracle obligations", "cannot_own": "domain vocabulary, defaults or acceptance"},
            {"rank": 4, "reuse_layer": "FAMILY_PROFILE", "member_count": len(authorities), "open_execution_units": len(targeted), "owns": "family vocabulary, semantic profiles and family defaults", "cannot_own": "true bounded-context exceptions"},
            {"rank": 5, "reuse_layer": "LIBRARY_INSTANCE", "member_count": len(exact), "open_execution_units": len(exact_groups), "owns": "exact public contract and local residuals", "cannot_own": "provider behavior or product acceptance"},
            {"rank": 6, "reuse_layer": "IMPLEMENTATION_OFFER", "member_count": len(exact), "open_execution_units": len(exact_groups), "owns": "artifact, capability, target and runtime evidence", "cannot_own": "canonical semantics"},
            {"rank": 7, "reuse_layer": "PRODUCT_ASSEMBLY", "member_count": len(product_programs), "open_execution_units": len(vacancy_groups), "owns": "coherent job, lifecycle, assembly and product acceptance gates", "cannot_own": "imported library semantics"},
            {"rank": 8, "reuse_layer": "VERTICAL_SOLUTION_PACK", "member_count": len(vertical_programs), "open_execution_units": 2, "owns": "industry-specific configuration, workflow, data, authority and executed acceptance", "cannot_own": "horizontal primitives or provider qualification"},
        ],
        "propagation_laws": [
            "constraints flow downward; evidence and observations do not become semantic authority",
            "a lower layer may narrow or specialize only through an explicit profiled exception",
            "an assembly composes imported contracts and never absorbs their semantic ownership",
            "same spelling, shape or provider encoding never licenses inheritance",
            "compiler lowering binds exact editions and emits unresolved residuals instead of defaults",
            "qualification and product acceptance never propagate upward as domain truth",
        ],
        "compression_metrics": {
            "library_contract_atoms": len(exact),
            "library_contract_family_workstreams": len(exact_groups),
            "symbol_packets": sum(row["packet_count"] for row in remaining_symbol_batches) + len(researched_symbols),
            "symbol_owner_workstreams": len(remaining_symbol_batches) + len(researched_symbols),
            "remaining_symbol_batches": len(remaining_symbol_batches),
            "remaining_symbol_archetype_programs": len(symbol_archetype_programs),
            "archetype_semantic_axis_research_lanes": sum(len(row["semantic_axis_refs"]) for row in symbol_archetype_programs),
            "symbol_band_coordination_lanes": len(symbol_coordination_lanes),
            "symbol_owner_proposals_with_named_candidates": p2_summary["owner_proposals_with_named_candidates"],
            "foundation_authority_templates_ready_for_review": p1b_summary["authority_review_ready_templates"],
            "symbol_owner_proposals_blocked": p2_summary["owner_proposals_blocked"],
            "symbol_owner_proposal_conflicts": len(p2_proposal_conflicts),
            "symbol_owner_proposal_counterfactual_instabilities": p2_summary["counterfactually_unstable_owner_proposals"],
            "symbol_owner_challenge_packages": len(p2_challenge_packages),
            "symbol_owner_ratification_packet_templates_ready_for_review": p2_summary["ratification_packet_templates_ready_for_authority_review"],
            "family_axis_applicability_review_packages": p3_summary["review_packages"],
            "family_axis_applicability_review_ready": p3_summary["review_ready_dockets"],
            "grain_cardinality_evidence_candidates": p3e_summary["primary_evidence_candidates"],
            "grain_coordinate_transformation_kernels": p3e_grain_coordinate_summary["transformation_kernels"],
            "grain_coordinate_member_routes": p3e_grain_coordinate_summary["target_member_routes"],
            "grain_coordinate_research_clusters": p3e_grain_coordinate_summary["research_clusters"],
            "state_change_evidence_candidates": p3s_summary["primary_evidence_candidates"],
            "state_change_transition_kernels": p3s_state_change_coordinate_summary["transition_kernels"],
            "state_change_member_routes": p3s_state_change_coordinate_summary["target_member_routes"],
            "state_change_research_clusters": p3s_state_change_coordinate_summary["research_clusters"],
            "order_topology_evidence_candidates": p3o_summary["primary_evidence_candidates"],
            "order_topology_relation_kernels": p3o_order_topology_coordinate_summary["relation_kernels"],
            "order_topology_member_routes": p3o_order_topology_coordinate_summary["target_member_routes"],
            "order_topology_research_clusters": p3o_order_topology_coordinate_summary["research_clusters"],
            "composition_algebra_evidence_candidates": p3c_summary["primary_evidence_candidates"],
            "composition_algebra_operator_kernels": p3c_composition_algebra_coordinate_summary["operator_kernels"],
            "composition_algebra_member_routes": p3c_composition_algebra_coordinate_summary["target_member_routes"],
            "composition_algebra_research_clusters": p3c_composition_algebra_coordinate_summary["research_clusters"],
            "identity_equality_evidence_candidates": p3i_summary["primary_evidence_candidates"],
            "identity_equality_kernels": p3i_identity_equality_coordinate_summary["identity_equality_kernels"],
            "identity_equality_member_routes": p3i_identity_equality_coordinate_summary["target_member_routes"],
            "identity_equality_research_clusters": p3i_identity_equality_coordinate_summary["research_clusters"],
            "partiality_uncertainty_evidence_candidates": p3u_summary["primary_evidence_candidates"],
            "partiality_uncertainty_kernels": p3u_partiality_uncertainty_coordinate_summary["partiality_uncertainty_kernels"],
            "partiality_uncertainty_member_routes": p3u_partiality_uncertainty_coordinate_summary["target_member_routes"],
            "partiality_uncertainty_research_clusters": p3u_partiality_uncertainty_coordinate_summary["research_clusters"],
            "time_temporal_bearer_archetypes": time_coordinate_summary["temporal_bearer_archetypes"],
            "time_temporal_operation_kernels": time_coordinate_summary["temporal_operation_kernels"],
            "time_structural_family_dockets": time_coordinate_summary["structural_family_dockets"],
            "time_member_routes": time_coordinate_summary["target_member_routes"],
            "time_research_clusters": time_coordinate_summary["research_clusters"],
            "semantic_object_bearer_archetypes": semantic_object_coordinate_summary["semantic_object_bearer_archetypes"],
            "semantic_object_operation_kernels": semantic_object_coordinate_summary["semantic_object_operation_kernels"],
            "semantic_object_structural_family_dockets": semantic_object_coordinate_summary["structural_family_dockets"],
            "semantic_object_member_routes": semantic_object_coordinate_summary["target_member_routes"],
            "semantic_object_research_clusters": semantic_object_coordinate_summary["research_clusters"],
            "semantic_role_archetypes": semantic_role_coordinate_summary["semantic_role_archetypes"],
            "semantic_role_operation_kernels": semantic_role_coordinate_summary["semantic_role_operation_kernels"],
            "semantic_role_structural_family_dockets": semantic_role_coordinate_summary["structural_family_dockets"],
            "semantic_role_member_routes": semantic_role_coordinate_summary["target_member_routes"],
            "semantic_role_research_clusters": semantic_role_coordinate_summary["research_clusters"],
            "authority_trust_bearer_archetypes": authority_trust_coordinate_summary["authority_trust_bearer_archetypes"],
            "authority_trust_operation_kernels": authority_trust_coordinate_summary["authority_trust_operation_kernels"],
            "authority_trust_structural_family_dockets": authority_trust_coordinate_summary["structural_family_dockets"],
            "authority_trust_member_routes": authority_trust_coordinate_summary["target_member_routes"],
            "authority_trust_research_clusters": authority_trust_coordinate_summary["research_clusters"],
            "effect_boundary_bearer_archetypes": effect_boundary_coordinate_summary["effect_boundary_bearer_archetypes"],
            "effect_boundary_operation_kernels": effect_boundary_coordinate_summary["effect_boundary_operation_kernels"],
            "effect_boundary_structural_family_dockets": effect_boundary_coordinate_summary["structural_family_dockets"],
            "effect_boundary_member_routes": effect_boundary_coordinate_summary["target_member_routes"],
            "effect_boundary_research_clusters": effect_boundary_coordinate_summary["research_clusters"],
            "evidence_conformance_bearer_archetypes": evidence_conformance_coordinate_summary["evidence_conformance_bearer_archetypes"],
            "evidence_conformance_operation_kernels": evidence_conformance_coordinate_summary["evidence_conformance_operation_kernels"],
            "evidence_conformance_structural_family_dockets": evidence_conformance_coordinate_summary["structural_family_dockets"],
            "evidence_conformance_member_routes": evidence_conformance_coordinate_summary["target_member_routes"],
            "evidence_conformance_research_clusters": evidence_conformance_coordinate_summary["research_clusters"],
            "representation_bearer_archetypes": representation_coordinate_summary["representation_bearer_archetypes"],
            "representation_operation_kernels": representation_coordinate_summary["representation_operation_kernels"],
            "representation_structural_family_dockets": representation_coordinate_summary["structural_family_dockets"],
            "representation_member_routes": representation_coordinate_summary["target_member_routes"],
            "representation_research_clusters": representation_coordinate_summary["research_clusters"],
            "compatibility_evolution_bearer_archetypes": compatibility_evolution_coordinate_summary["compatibility_evolution_bearer_archetypes"],
            "compatibility_evolution_operation_kernels": compatibility_evolution_coordinate_summary["compatibility_evolution_operation_kernels"],
            "compatibility_evolution_structural_family_dockets": compatibility_evolution_coordinate_summary["structural_family_dockets"],
            "compatibility_evolution_member_routes": compatibility_evolution_coordinate_summary["target_member_routes"],
            "compatibility_evolution_research_clusters": compatibility_evolution_coordinate_summary["research_clusters"],
            "privacy_security_safety_bearer_archetypes": privacy_security_safety_coordinate_summary["privacy_security_safety_bearer_archetypes"],
            "privacy_security_safety_operation_kernels": privacy_security_safety_coordinate_summary["privacy_security_safety_operation_kernels"],
            "privacy_security_safety_structural_family_dockets": privacy_security_safety_coordinate_summary["structural_family_dockets"],
            "privacy_security_safety_member_routes": privacy_security_safety_coordinate_summary["target_member_routes"],
            "privacy_security_safety_research_clusters": privacy_security_safety_coordinate_summary["research_clusters"],
            "resources_failure_bearer_archetypes": resources_failure_coordinate_summary["resources_failure_bearer_archetypes"],
            "resources_failure_operation_kernels": resources_failure_coordinate_summary["resources_failure_operation_kernels"],
            "resources_failure_structural_family_dockets": resources_failure_coordinate_summary["structural_family_dockets"],
            "resources_failure_member_routes": resources_failure_coordinate_summary["target_member_routes"],
            "resources_failure_research_clusters": resources_failure_coordinate_summary["research_clusters"],
            "targeted_evidence_axes": targeted_evidence_coverage_summary["targeted_axes"],
            "targeted_evidence_work_packages": targeted_evidence_coverage_summary["targeted_work_packages"],
            "targeted_evidence_library_occurrences": targeted_evidence_coverage_summary["targeted_library_occurrences"],
            "semantic_frontier_axes": semantic_research_frontier_summary["semantic_axes"],
            "semantic_frontier_lanes": semantic_research_frontier_summary["research_lanes"],
            "semantic_frontier_member_axis_cells": semantic_research_frontier_summary["member_axis_cells"],
            "semantic_decision_bearer_archetypes": semantic_decision_locus_summary["bearer_archetypes"],
            "semantic_decision_axis_profiles": semantic_decision_locus_summary["semantic_axis_profiles"],
            "semantic_decision_family_axis_factorizations": semantic_decision_locus_summary["family_axis_factorizations"],
            "semantic_decision_coordinate_refined_axes": semantic_decision_locus_summary["coordinate_refined_axes"],
            "ratification_ingestion_verified": p4_summary["verified_ratifications"],
            "canonical_delta_candidates": p4_summary["canonical_delta_candidates"],
            "exact_contract_archetype_kernels": p5_summary["archetype_obligation_kernels"],
            "exact_contract_family_kernels": p5_summary["family_semantic_kernels"],
            "exact_contract_execution_packages": p5_summary["execution_packages"],
            "implementation_concrete_references": p6_summary["concrete_reference_resolutions"],
            "implementation_qualification_scopes": p6_summary["qualification_scope_kernels"],
            "implementation_independent_slots": p6_summary["implementation_slots"],
            "implementation_subjects": p6_summary["subject_dockets"],
            "implementation_qualification_profiles": p7_summary["qualification_profile_kernels"],
            "implementation_conformance_workstreams": p7_summary["conformance_context_workstreams"],
            "semantic_physical_binding_gates": p7_summary["semantic_physical_binding_gates"],
            "vertical_acceptance_slots": p8_summary["unrelated_vertical_slots"],
            "vertical_acceptance_gate_workstreams": p8_summary["acceptance_gate_classes"],
            "vertical_acceptance_obligations": p8_summary["slot_gate_obligations"],
            "product_evidence_vacancies": len(product_vacancies),
            "product_gate_workstreams": len(vacancy_groups),
            "closure_method_kernels": len(method_kernels),
        },
        "authority_limit": "Compression changes scheduling and inheritance only. It does not collapse identities, waive per-instance conformance or close any canonical gap.",
    }
    return {"ontology": ONTOLOGY, "programs": program_rows(), "clusters": clusters, "method_kernels": method_kernels, "bands": bands, "summary": summary, "lattice": lattice}


def schema() -> dict[str, Any]:
    required = ["record_kind", "cluster_id", "gap_kind", "program_ref", "atom_count", "family_refs", "affected_scope_refs", "semantic_axes", "defect_kind", "locus", "scope_grain", "reuse_layer", "decision_shape", "propagation_mode", "required_evidence_kinds", "blocked_outputs", "fanout_score", "lifecycle", "canonical_gaps_closed", "status", "execution_rank"]
    return {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://san.example/spec/semantic-gap-cluster-v1.schema.json", "type": "object", "additionalProperties": False, "required": required, "properties": {key: {} for key in required}}


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "gap-ontology.json": json.dumps(built["ontology"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "gap-cluster.schema.json": json.dumps(schema(), ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "closure-programs.jsonl": "".join(canonical(row) + "\n" for row in built["programs"]),
        "gap-clusters.jsonl": "".join(canonical(row) + "\n" for row in built["clusters"]),
        "closure-method-kernels.jsonl": "".join(canonical(row) + "\n" for row in built["method_kernels"]),
        "macro-execution-bands.jsonl": "".join(canonical(row) + "\n" for row in built["bands"]),
        "closure-lattice.json": json.dumps(built["lattice"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    manifest = {name: {"bytes": len(text.encode()), "sha256": hashlib.sha256(text.encode()).hexdigest()} for name, text in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.semantic-gap-topology.v1", "as_of": AS_OF, "files": manifest, "completion_claim": False}, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    for name, text in outputs().items():
        (HERE / name).write_text(text)
    summary = build()["summary"]
    print(f"BUILD PASS gap topology: {summary['gap_clusters']} batchable clusters represent {summary['represented_gap_atoms']} open atoms across {summary['closure_programs']} dependency-ordered programs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
