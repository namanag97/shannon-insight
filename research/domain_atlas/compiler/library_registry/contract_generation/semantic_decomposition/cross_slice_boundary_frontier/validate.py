#!/usr/bin/env python3
"""Validate the cross-slice boundary frontier as a lossless refusing package."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
BUILDER = HERE / "build_cross_slice_boundary_frontier.py"


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def unique(rows: list[dict[str, Any]], key: str) -> None:
    values = [row[key] for row in rows]
    if len(values) != len(set(values)):
        fail(f"duplicate {key}")


def import_builder() -> Any:
    spec = importlib.util.spec_from_file_location("cross_slice_boundary_frontier_builder", BUILDER)
    if spec is None or spec.loader is None:
        fail("cannot load builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_dag(rows: list[dict[str, Any]]) -> None:
    unique(rows, "stage_ref")
    refs = {row["stage_ref"] for row in rows}
    expected = [f"stage.boundary.{index:02d}_{suffix}" for index, suffix in enumerate([
        "exact_inventory", "semantic_quotient", "collision_tests", "owner_candidates",
        "product_boundary", "library_boundary", "contract_lowering",
        "implementation_qualification", "vertical_acceptance",
    ])]
    if [row["stage_ref"] for row in rows] != expected:
        fail("ratification DAG stages or order changed")
    visited: set[str] = set()
    visiting: set[str] = set()

    def visit(ref: str) -> None:
        if ref in visiting:
            fail("ratification DAG contains a cycle")
        if ref in visited:
            return
        visiting.add(ref)
        row = next(item for item in rows if item["stage_ref"] == ref)
        for dependency in row["dependency_refs"]:
            if dependency not in refs:
                fail(f"unknown DAG dependency {dependency}")
            visit(dependency)
        visiting.remove(ref)
        visited.add(ref)

    for ref in refs:
        visit(ref)


def main() -> int:
    builder = import_builder()
    expected_outputs = builder.outputs()
    for name, expected in expected_outputs.items():
        path = HERE / name
        if not path.exists() or path.read_text() != expected:
            fail(f"generated artifact is stale or nondeterministic: {name}")

    inventory = load_jsonl(HERE / "exact-finding-inventory.jsonl")
    vacancy_routes = load_jsonl(HERE / "vacancy-routes.jsonl")
    archetypes = load_jsonl(HERE / "vacancy-semantic-quotients.jsonl")
    boundary_routes = load_jsonl(HERE / "boundary-finding-routes.jsonl")
    boundary_kinds = load_jsonl(HERE / "boundary-decision-quotients.jsonl")
    collisions = load_jsonl(HERE / "cross-namespace-collision-candidates.jsonl")
    collision_dockets = load_jsonl(HERE / "collision-review-dockets.jsonl")
    collision_families = load_jsonl(HERE / "collision-review-families.jsonl")
    meaning_partitions = load_jsonl(HERE / "collision-meaning-partitions.jsonl")
    collision_adjudications = load_jsonl(HERE / "collision-adjudication-candidates.jsonl")
    owner_dockets = load_jsonl(HERE / "owner-candidate-dockets.jsonl")
    owner_contexts = load_jsonl(HERE / "owner-context-candidates.jsonl")
    owner_adjudications = load_jsonl(HERE / "owner-adjudication-candidates.jsonl")
    negative_twins = load_jsonl(HERE / "collision-negative-twins.jsonl")
    owner_challenges = load_jsonl(HERE / "owner-counterfactual-challenges.jsonl")
    consolidation_hypotheses = load_jsonl(HERE / "context-consolidation-hypotheses.jsonl")
    consolidation_routes = load_jsonl(HERE / "context-consolidation-routes.jsonl")
    boundary_challenge_routes = load_jsonl(HERE / "boundary-challenge-evidence-routes.jsonl")
    negative_twin_receipts = load_jsonl(HERE / "collision-negative-twin-gate-receipts.jsonl")
    owner_evidence_vacancies = load_jsonl(HERE / "owner-challenge-evidence-vacancies.jsonl")
    owner_evidence_programs = load_jsonl(HERE / "owner-challenge-evidence-programs.jsonl")
    cohesion_vacancies = load_jsonl(HERE / "context-cohesion-evidence-vacancies.jsonl")
    cohesion_programs = load_jsonl(HERE / "context-cohesion-evidence-programs.jsonl")
    namespace_observations = load_jsonl(HERE / "namespace-structural-observations.jsonl")
    namespace_challenges = load_jsonl(HERE / "namespace-boundary-challenge-candidates.jsonl")
    namespace_subcontexts = load_jsonl(HERE / "namespace-subcontext-candidates.jsonl")
    namespace_review_packages = load_jsonl(HERE / "namespace-authority-review-packages.jsonl")
    p0_namespace_dispositions = load_jsonl(HERE / "p0-namespace-disposition-candidates.jsonl")
    p0_subcontext_dispositions = load_jsonl(HERE / "p0-subcontext-disposition-candidates.jsonl")
    p0_boundary_negative_twins = load_jsonl(HERE / "p0-boundary-negative-twins.jsonl")
    p0_route_projections = load_jsonl(HERE / "p0-downstream-route-projections.jsonl")
    p0_finding_projections = load_jsonl(HERE / "p0-boundary-finding-projections.jsonl")
    p0_product_dossier_bindings = load_jsonl(HERE / "p0-product-dossier-bindings.jsonl")
    contract_dockets = load_jsonl(HERE / "provisional-contract-lowering-dockets.jsonl")
    contract_archetypes = load_jsonl(HERE / "contract-lowering-archetypes.jsonl")
    intake_routes = load_jsonl(HERE / "p5-intake-routes.jsonl")
    frontier = load_jsonl(HERE / "execution-frontier.jsonl")
    admission_audit = load_json(HERE / "implementation-vertical-admission-audit.json")
    dag = load_jsonl(HERE / "ratification-dag.jsonl")
    packages = load_jsonl(HERE / "ratification-packages.jsonl")
    summary = load_json(HERE / "summary.json")
    manifest = load_json(HERE / "manifest.json")

    if (len(inventory), len(vacancy_routes), len(boundary_routes)) != (343, 227, 116):
        fail("source partition counts changed; inspect upstream findings before accepting")
    unique(inventory, "finding_id")
    unique(vacancy_routes, "route_id")
    unique(vacancy_routes, "proposed_library_ref")
    unique(boundary_routes, "route_id")
    unique(archetypes, "archetype_ref")
    unique(boundary_kinds, "boundary_kind_ref")
    unique(collisions, "collision_id")
    unique(collision_dockets, "docket_id")
    unique(collision_families, "collision_family_ref")
    unique(meaning_partitions, "partition_id")
    unique(collision_adjudications, "adjudication_candidate_id")
    unique(owner_dockets, "docket_id")
    unique(owner_dockets, "proposed_library_ref")
    unique(owner_contexts, "context_candidate_ref")
    unique(owner_adjudications, "owner_adjudication_candidate_id")
    unique(owner_adjudications, "candidate_library_ref")
    unique(negative_twins, "negative_twin_id")
    unique(owner_challenges, "challenge_id")
    unique(consolidation_hypotheses, "hypothesis_ref")
    unique(consolidation_routes, "route_id")
    unique(consolidation_routes, "candidate_library_ref")
    unique(boundary_challenge_routes, "route_id")
    unique(boundary_challenge_routes, "boundary_finding_ref")
    unique(negative_twin_receipts, "receipt_id")
    unique(owner_evidence_vacancies, "vacancy_id")
    unique(owner_evidence_programs, "program_ref")
    unique(cohesion_vacancies, "vacancy_id")
    unique(cohesion_programs, "program_ref")
    unique(namespace_observations, "observation_id")
    unique(namespace_challenges, "challenge_candidate_ref")
    unique(namespace_challenges, "namespace")
    unique(namespace_subcontexts, "subcontext_candidate_ref")
    unique(namespace_review_packages, "package_ref")
    unique(p0_namespace_dispositions, "namespace_disposition_candidate_ref")
    unique(p0_namespace_dispositions, "namespace")
    unique(p0_subcontext_dispositions, "disposition_candidate_ref")
    unique(p0_subcontext_dispositions, "subcontext_candidate_ref")
    unique(p0_boundary_negative_twins, "negative_twin_ref")
    unique(p0_route_projections, "projection_ref")
    unique(p0_route_projections, "candidate_library_ref")
    unique(p0_finding_projections, "projection_ref")
    unique(p0_finding_projections, "boundary_finding_ref")
    unique(p0_product_dossier_bindings, "binding_ref")
    unique(p0_product_dossier_bindings, "product_ref")
    unique(contract_dockets, "docket_id")
    unique(contract_dockets, "candidate_library_ref")
    unique(contract_archetypes, "contract_lowering_archetype_ref")
    unique(intake_routes, "intake_route_id")
    unique(frontier, "frontier_ref")
    unique(packages, "package_id")

    inventory_refs = {row["finding_id"] for row in inventory}
    vacancy_source_refs = {row["source_finding_ref"] for row in vacancy_routes}
    boundary_source_refs = {row["source_finding_ref"] for row in boundary_routes}
    if vacancy_source_refs & boundary_source_refs:
        fail("vacancy and boundary partitions overlap")
    if vacancy_source_refs | boundary_source_refs != inventory_refs:
        fail("vacancy and boundary partitions are not lossless")

    source_vacancies = {
        row["proposed_library_ref"]
        for row in inventory
        if row.get("candidate_disposition") == "NEW_LIBRARY_BOUNDARY_CANDIDATE_UNRATIFIED"
    }
    if {row["proposed_library_ref"] for row in vacancy_routes} != source_vacancies:
        fail("vacancy routes do not exactly preserve proposed library identities")

    archetype_refs = {row["archetype_ref"] for row in archetypes}
    if len(archetypes) != 21 or sum(row["member_count"] > 0 for row in archetypes) < 20:
        fail("semantic quotient coverage regressed")
    routed_by_archetype: dict[str, set[str]] = {ref: set() for ref in archetype_refs}
    for row in vacancy_routes:
        if row["primary_archetype_ref"] not in archetype_refs:
            fail("vacancy route has unknown primary archetype")
        if row["primary_archetype_ref"] in row["secondary_archetype_refs"]:
            fail("primary archetype repeated as secondary")
        if not set(row["secondary_archetype_refs"]).issubset(archetype_refs):
            fail("vacancy route has unknown secondary archetype")
        if not row["local_residual_required"] or row["semantic_equivalence_claim"] or row["merge_authorized"]:
            fail("semantic quotient weakened exact identity or authorized merge")
        routed_by_archetype[row["primary_archetype_ref"]].add(row["proposed_library_ref"])
    for row in archetypes:
        members = routed_by_archetype[row["archetype_ref"]]
        if row["member_count"] != len(members) or set(row["member_library_refs"]) != members:
            fail(f"archetype membership mismatch: {row['archetype_ref']}")

    kind_refs = {row["boundary_kind_ref"] for row in boundary_kinds}
    routed_by_kind: dict[str, set[str]] = {ref: set() for ref in kind_refs}
    for row in boundary_routes:
        if row["boundary_kind_ref"] not in kind_refs:
            fail("boundary route has unknown kind")
        routed_by_kind[row["boundary_kind_ref"]].add(row["source_finding_ref"])
    for row in boundary_kinds:
        refs = routed_by_kind[row["boundary_kind_ref"]]
        if row["finding_count"] != len(refs) or set(row["source_finding_refs"]) != refs:
            fail(f"boundary-kind membership mismatch: {row['boundary_kind_ref']}")

    namespaces_by_library = {row["proposed_library_ref"]: row["namespace"] for row in vacancy_routes}
    for row in collisions:
        refs = row["candidate_library_refs"]
        namespaces = {namespaces_by_library[ref] for ref in refs}
        if len(refs) < 2 or len(namespaces) < 2 or set(row["namespace_refs"]) != namespaces:
            fail(f"invalid cross-namespace collision: {row['collision_id']}")
        if row["merge_authorized"]:
            fail("collision candidate improperly authorizes merge")

    collision_refs = {row["collision_id"] for row in collisions}
    if {row["collision_ref"] for row in collision_dockets} != collision_refs:
        fail("collision dockets do not preserve every collision candidate exactly once")
    family_refs = {row["collision_family_ref"] for row in collision_families}
    routed_by_collision_family: dict[str, set[str]] = {ref: set() for ref in family_refs}
    for row in collision_dockets:
        if row["collision_family_ref"] not in family_refs:
            fail("collision docket has unknown family")
        if row["merge_authorized"] or row["disposition_state"] != "OPEN_UNRATIFIED":
            fail("collision docket makes an unratified merge or disposition claim")
        routed_by_collision_family[row["collision_family_ref"]].add(row["collision_ref"])
    for row in collision_families:
        refs = routed_by_collision_family[row["collision_family_ref"]]
        if row["docket_count"] != len(refs) or set(row["collision_refs"]) != refs:
            fail(f"collision-family membership mismatch: {row['collision_family_ref']}")

    expected_partition_pairs = {
        (row["collision_id"], library_ref)
        for row in collisions for library_ref in row["candidate_library_refs"]
    }
    actual_partition_pairs = {
        (row["collision_ref"], row["candidate_library_ref"]) for row in meaning_partitions
    }
    if actual_partition_pairs != expected_partition_pairs or len(meaning_partitions) != len(expected_partition_pairs):
        fail("collision meaning partitions do not preserve every exact collision member")
    if any(
        not row["candidate_meaning_statement"] or not row["semantic_module_candidate_refs"]
        or not row["evidence_source_refs"] or not row["meaning_identity_preserved"]
        or row["merge_authorized"]
        for row in meaning_partitions
    ):
        fail("collision meaning partition lacks meaning/module/evidence or authorizes merge")
    if {row["collision_ref"] for row in collision_adjudications} != collision_refs:
        fail("collision adjudication candidates do not cover all collision candidates")
    allowed_collision_dispositions = {
        "GENERIC_SURFACE_TOKEN_NO_MERGE_SIGNAL_CANDIDATE",
        "SHARED_MECHANIC_WITH_LOCAL_PROFILES_CANDIDATE",
        "HOMONYM_KEEP_DISTINCT_CANDIDATE",
    }
    partitions_by_collision: dict[str, set[str]] = {}
    for row in meaning_partitions:
        partitions_by_collision.setdefault(row["collision_ref"], set()).add(row["partition_id"])
    for row in collision_adjudications:
        if set(row["member_partition_refs"]) != partitions_by_collision[row["collision_ref"]]:
            fail("collision adjudication candidate has incomplete member partitions")
        if row["candidate_disposition"] not in allowed_collision_dispositions:
            fail("collision adjudication candidate has unknown disposition")
        if row["authority_verdict"] != "MISSING" or row["candidate_state"] != "REVERSIBLE_EVIDENCE_PACKET_UNRATIFIED":
            fail("collision adjudication candidate overclaims authority")
        if row["merge_authorized"]:
            fail("collision adjudication candidate authorizes merge")
    partition_by_ref = {row["partition_id"]: row for row in meaning_partitions}
    adjudication_refs = {row["adjudication_candidate_id"] for row in collision_adjudications}
    expected_twin_kinds = {
        "TYPE_SUBSTITUTION", "INVARIANT_TRANSPLANT", "OWNER_REBIND",
        "STATE_MACHINE_REPLAY", "AUTHORITY_EFFECT_TRANSFER",
    }
    if len(negative_twins) != len(collisions) * len(expected_twin_kinds):
        fail("collision negative-twin matrix is incomplete")
    twins_by_collision: dict[str, set[str]] = {}
    for row in negative_twins:
        twins_by_collision.setdefault(row["collision_ref"], set()).add(row["negative_twin_kind"])
        if row["collision_adjudication_candidate_ref"] not in adjudication_refs:
            fail("negative twin has unknown collision adjudication candidate")
        if row["member_a_partition_ref"] not in partition_by_ref or row["member_b_partition_ref"] not in partition_by_ref:
            fail("negative twin has unknown member partition")
        if row["member_a_library_ref"] == row["member_b_library_ref"]:
            fail("negative twin compares a member with itself")
        if row["execution_state"] != "UNEXECUTED_AUTHORITY_ORACLE_MISSING":
            fail("negative twin overclaims execution")
        if not row["evidence_source_refs"]:
            fail("negative twin lacks source evidence")
    if set(twins_by_collision) != collision_refs or any(kinds != expected_twin_kinds for kinds in twins_by_collision.values()):
        fail("each collision must expose all five negative-twin kinds")
    twin_refs = {row["negative_twin_id"] for row in negative_twins}
    if {row["negative_twin_ref"] for row in negative_twin_receipts} != twin_refs:
        fail("structural gate receipts do not cover every negative twin")
    for row in negative_twin_receipts:
        if row["gate_result"] != "REFUSED" or not row["structural_gate_executed"]:
            fail("negative-twin structural gate did not execute fail closed")
        if row["semantic_distinctness_proven"] or row["authority_verdict_supplied"]:
            fail("negative-twin gate receipt converts missing proof into a semantic verdict")
        if set(row["refusal_codes"]) != {
            "EXACT_EQUIVALENCE_PROOF_MISSING", "OWNER_AUTHORITY_RECEIPT_MISSING",
            "RATIFIED_MEMBER_CONTRACTS_MISSING",
        }:
            fail("negative-twin gate receipt has an unexpected refusal surface")

    if len(owner_dockets) != len(vacancy_routes):
        fail("owner-candidate docket count does not match exact proposed seams")
    if {row["proposed_library_ref"] for row in owner_dockets} != source_vacancies:
        fail("owner-candidate dockets do not preserve exact proposed seam identities")
    semantic_root = HERE.parent
    module_refs_by_slice: dict[str, set[str]] = {}
    for slice_name in {row["source_slice"] for row in owner_dockets}:
        modules = load_jsonl(semantic_root / slice_name / "semantic-modules.jsonl")
        module_refs_by_slice[slice_name] = {row["module_id"] for row in modules}
    contexts_by_ref: dict[str, set[str]] = {}
    for row in owner_dockets:
        if row["selection_state"] != "OPEN_NO_OWNER_SELECTED" or row["owner_ratified"]:
            fail("owner docket selects or ratifies an owner")
        if row["local_context_candidate_grain"] != "EXACT_SEAM_OWNER_LOCUS_NOT_PROVEN_BOUNDED_CONTEXT":
            fail("owner docket treats a seam-local owner locus as a proven bounded context")
        candidates = row["semantic_module_candidates"]
        if not candidates:
            fail(f"owner docket lacks source-slice semantic-module grounding: {row['proposed_library_ref']}")
        if row["semantic_module_grounding_gap"] != (not candidates):
            fail("semantic-module grounding gap flag is inconsistent")
        if any(candidate["score"] <= 0 for candidate in candidates):
            fail("semantic-module candidate has a non-positive score")
        if not {candidate["semantic_module_ref"] for candidate in candidates}.issubset(module_refs_by_slice[row["source_slice"]]):
            fail("owner docket references a semantic module outside its source slice")
        expected_collision_adjudications = {
            candidate["adjudication_candidate_id"] for candidate in collision_adjudications
            if row["proposed_library_ref"] in candidate["member_library_refs"]
        }
        if set(row["collision_adjudication_candidate_refs"]) != expected_collision_adjudications:
            fail("owner docket does not carry its exact collision evidence")
        expected_owner_readiness = (
            "BLOCKED_COLLISION_AUTHORITY_VERDICTS_MISSING" if expected_collision_adjudications
            else "EVIDENCE_PACKET_READY_OWNER_AUTHORITY_VERDICT_MISSING"
        )
        if row["owner_review_readiness"] != expected_owner_readiness:
            fail("owner docket readiness does not follow collision evidence")
        expected_owner_candidate = next(
            (candidate["owner_adjudication_candidate_id"] for candidate in owner_adjudications
             if candidate["owner_docket_ref"] == row["docket_id"]), None,
        )
        if row["owner_adjudication_candidate_ref"] != expected_owner_candidate:
            fail("owner docket does not carry its exact owner-adjudication candidate")
        contexts_by_ref.setdefault(row["local_context_candidate_ref"], set()).add(row["proposed_library_ref"])
    if set(contexts_by_ref) != {row["context_candidate_ref"] for row in owner_contexts}:
        fail("owner-context candidates do not exactly aggregate local context proposals")
    for row in owner_contexts:
        members = contexts_by_ref[row["context_candidate_ref"]]
        if row["member_count"] != len(members) or set(row["member_library_refs"]) != members:
            fail(f"owner-context membership mismatch: {row['context_candidate_ref']}")
        if row["context_boundary_state"] != "CANDIDATE_UNRATIFIED" or not row["cohesion_not_proven"]:
            fail("owner-context candidate overclaims boundary cohesion")
    expected_owner_candidate_libraries = {
        row["proposed_library_ref"] for row in owner_dockets
        if row["owner_review_readiness"] == "EVIDENCE_PACKET_READY_OWNER_AUTHORITY_VERDICT_MISSING"
    }
    if {row["candidate_library_ref"] for row in owner_adjudications} != expected_owner_candidate_libraries:
        fail("owner-adjudication candidates do not cover every collision-free owner docket")
    allowed_owner_dispositions = {
        "LOCAL_SEAM_OWNER_LOCUS_CANDIDATE", "SHARED_METHOD_CONTEXT_OWNER_CANDIDATE",
        "IMPORT_EXISTING_CONTEXT_OWNER_CANDIDATE", "OWNER_LOCUS_RESEARCH_OR_SPLIT_CANDIDATE",
    }
    for row in owner_adjudications:
        if row["candidate_disposition"] not in allowed_owner_dispositions:
            fail("owner-adjudication candidate has unknown disposition")
        if row["authority_verdict"] != "MISSING" or row["owner_selected"]:
            fail("owner-adjudication candidate selects an owner without authority")
        if row["candidate_state"] != "REVERSIBLE_OWNER_EVIDENCE_PACKET_UNRATIFIED":
            fail("owner-adjudication candidate overclaims state")
    owner_adjudication_refs = {row["owner_adjudication_candidate_id"] for row in owner_adjudications}
    expected_owner_challenge_kinds = {
        "REPLACE_WITH_BEST_EXISTING_CONTEXT", "REPLACE_WITH_SHARED_MECHANIC_CONTEXT",
        "SPLIT_STATEFUL_LIFECYCLE_FROM_PURE_MECHANIC", "INDEPENDENT_ADOPTION_AND_RELEASE",
        "TWO_UNRELATED_VERTICAL_LANGUAGE_TRANSFER", "AUTHORITY_EFFECT_AND_EXIT_BOUNDARY",
    }
    if len(owner_challenges) != len(owner_adjudications) * len(expected_owner_challenge_kinds):
        fail("owner counterfactual challenge matrix is incomplete")
    challenges_by_owner: dict[str, set[str]] = {}
    for row in owner_challenges:
        if row["owner_adjudication_candidate_ref"] not in owner_adjudication_refs:
            fail("owner challenge has unknown adjudication candidate")
        challenges_by_owner.setdefault(row["owner_adjudication_candidate_ref"], set()).add(row["challenge_kind"])
        if row["challenge_state"] not in {"EVIDENCE_PACKET_READY_UNEXECUTED", "NO_EXISTING_COUNTERFACTUAL_RESEARCH_GAP"}:
            fail("owner challenge overclaims execution")
        if row["authority_verdict"] != "MISSING":
            fail("owner challenge overclaims authority")
    if set(challenges_by_owner) != owner_adjudication_refs or any(
        kinds != expected_owner_challenge_kinds for kinds in challenges_by_owner.values()
    ):
        fail("each owner candidate must expose all six challenge kinds")
    challenge_by_ref = {row["challenge_id"]: row for row in owner_challenges}
    expected_owner_vacancy_pairs = {
        (challenge["challenge_id"], observation)
        for challenge in owner_challenges for observation in challenge["required_observations"]
    }
    actual_owner_vacancy_pairs = {
        (row["challenge_ref"], row["required_observation_kind"])
        for row in owner_evidence_vacancies
    }
    if actual_owner_vacancy_pairs != expected_owner_vacancy_pairs:
        fail("owner challenge evidence vacancies are not lossless")
    if any(
        row["challenge_ref"] not in challenge_by_ref or not row["candidate_source_refs"]
        or row["status"] != "OPEN_EVIDENCE_AND_AUTHORITY_MISSING"
        for row in owner_evidence_vacancies
    ):
        fail("owner challenge evidence vacancy lacks source grounding or stays falsely closed")
    owner_vacancies_by_program: dict[tuple[str, str], set[str]] = {}
    for row in owner_evidence_vacancies:
        owner_vacancies_by_program.setdefault(
            (row["challenge_kind"], row["required_observation_kind"]), set()
        ).add(row["vacancy_id"])
    if len(owner_evidence_programs) != len(owner_vacancies_by_program):
        fail("owner challenge evidence programs do not factor every challenge/observation pair")
    for row in owner_evidence_programs:
        refs = owner_vacancies_by_program[(row["challenge_kind"], row["required_observation_kind"])]
        if set(row["vacancy_refs"]) != refs or row["vacancy_count"] != len(refs):
            fail("owner challenge evidence program membership mismatch")
        if row["status"] != "OPEN_UNEXECUTED":
            fail("owner challenge evidence program overclaims execution")

    hypothesis_refs = {row["hypothesis_ref"] for row in consolidation_hypotheses}
    hypothesis_kinds = {row["hypothesis_kind"] for row in consolidation_hypotheses}
    if hypothesis_kinds != {"NAMESPACE_PRODUCT_LANGUAGE", "PRIMARY_SEMANTIC_MODULE", "SHARED_MECHANIC_ARCHETYPE"}:
        fail("context consolidation graph has an unknown or missing resolution")
    if len(consolidation_routes) != len(owner_dockets):
        fail("context consolidation routes do not cover all exact owner loci")
    owner_by_library = {row["proposed_library_ref"]: row for row in owner_dockets}
    for row in consolidation_routes:
        owner = owner_by_library[row["candidate_library_ref"]]
        if row["exact_owner_locus_ref"] != owner["local_context_candidate_ref"]:
            fail("context consolidation route changed the exact owner locus")
        if not {
            row["namespace_hypothesis_ref"], row["module_hypothesis_ref"],
            row["shared_mechanic_hypothesis_ref"],
        }.issubset(hypothesis_refs):
            fail("context consolidation route references an unknown hypothesis")
        if row["selected_context_ref"] is not None or row["route_state"] != "OPEN_NO_CONTEXT_BOUNDARY_SELECTED":
            fail("context consolidation route selects a boundary")
    for kind in hypothesis_kinds:
        member_occurrences = [
            library_ref for row in consolidation_hypotheses if row["hypothesis_kind"] == kind
            for library_ref in row["member_library_refs"]
        ]
        if len(member_occurrences) != len(owner_dockets) or set(member_occurrences) != source_vacancies:
            fail(f"context consolidation resolution is not lossless: {kind}")
    if any(
        row["boundary_verdict"] != "MISSING"
        or row["candidate_state"] != "REVERSIBLE_CONSOLIDATION_HYPOTHESIS_UNRATIFIED"
        for row in consolidation_hypotheses
    ):
        fail("context consolidation hypothesis overclaims a boundary")
    namespace_set = {row["namespace"] for row in owner_dockets}
    if {row["namespace"] for row in namespace_challenges} != namespace_set:
        fail("namespace boundary challenges do not cover all proposed seam namespaces")
    expected_namespace_tests = {
        "one_ubiquitous_language", "one_invariant_and_state_boundary", "one_authority_model",
        "coherent_change_cadence", "independent_substitutability", "explicit_acl_for_residuals",
    }
    observations_by_namespace: dict[str, set[str]] = {}
    for row in namespace_observations:
        observations_by_namespace.setdefault(row["namespace"], set()).add(row["cohesion_test_kind"])
        if row["semantic_or_boundary_verdict"] != "NOT_SUPPLIED":
            fail("namespace structural observation overclaims a verdict")
    if set(observations_by_namespace) != namespace_set or any(
        tests != expected_namespace_tests for tests in observations_by_namespace.values()
    ):
        fail("namespace observations do not cover all six cohesion tests")
    subcontext_refs = {row["subcontext_candidate_ref"] for row in namespace_subcontexts}
    owner_libraries_by_namespace: dict[str, set[str]] = {}
    for row in owner_dockets:
        owner_libraries_by_namespace.setdefault(row["namespace"], set()).add(row["proposed_library_ref"])
    subcontexts_by_namespace: dict[str, set[str]] = {}
    members_by_namespace: dict[str, list[str]] = {}
    for row in namespace_subcontexts:
        subcontexts_by_namespace.setdefault(row["namespace"], set()).add(row["subcontext_candidate_ref"])
        members_by_namespace.setdefault(row["namespace"], []).extend(row["member_library_refs"])
        if not row["evidence_source_refs"] or not row["semantic_module_candidate_refs"]:
            fail("namespace subcontext candidate lacks module/source grounding")
        if row["boundary_verdict"] != "MISSING" or row["candidate_state"] != "REVERSIBLE_SUBCONTEXT_CANDIDATE_UNRATIFIED":
            fail("namespace subcontext candidate overclaims a boundary")
    for namespace in namespace_set:
        members = members_by_namespace.get(namespace, [])
        if len(members) != len(set(members)) or set(members) != owner_libraries_by_namespace[namespace]:
            fail(f"namespace subcontext candidates do not partition exact members: {namespace}")
    challenge_by_namespace = {row["namespace"]: row for row in namespace_challenges}
    for namespace, row in challenge_by_namespace.items():
        if set(row["exact_member_library_refs"]) != owner_libraries_by_namespace[namespace]:
            fail("namespace boundary challenge changes exact member universe")
        if set(row["subcontext_candidate_refs"]) != subcontexts_by_namespace[namespace]:
            fail("namespace boundary challenge has incomplete subcontext candidates")
        if row["authority_verdict"] != "MISSING" or row["candidate_state"] != "REVERSIBLE_NAMESPACE_BOUNDARY_CHALLENGE_UNRATIFIED":
            fail("namespace boundary challenge overclaims authority")
        if len(row["observation_refs"]) != 6:
            fail("namespace boundary challenge lacks structural observations")
    for row in consolidation_routes:
        namespace = owner_by_library[row["candidate_library_ref"]]["namespace"]
        if row["namespace_boundary_challenge_ref"] != challenge_by_namespace[namespace]["challenge_candidate_ref"]:
            fail("consolidation route lacks its namespace boundary challenge")
        if row["namespace_subcontext_candidate_ref"] not in subcontext_refs:
            fail("consolidation route lacks its namespace subcontext candidate")
    packaged_namespaces = [namespace for row in namespace_review_packages for namespace in row["namespace_refs"]]
    packaged_subcontexts = [ref for row in namespace_review_packages for ref in row["subcontext_candidate_refs"]]
    if len(packaged_namespaces) != len(set(packaged_namespaces)) or set(packaged_namespaces) != namespace_set:
        fail("namespace authority packages do not partition namespaces exactly once")
    if len(packaged_subcontexts) != len(set(packaged_subcontexts)) or set(packaged_subcontexts) != subcontext_refs:
        fail("namespace authority packages do not partition subcontext candidates exactly once")
    allowed_namespace_priorities = {
        "P0_CROSS_PRODUCT_OR_KNOWN_SPLIT", "P1_NEW_PRODUCT_OR_AUTHORITY_ACL",
        "P2_INTERNAL_CONTEXT_COHESION",
    }
    for row in namespace_review_packages:
        if row["priority_band"] not in allowed_namespace_priorities:
            fail("namespace authority package has unknown priority")
        if row["readiness"] != "STRUCTURAL_OBSERVATIONS_READY_AUTHORITY_AND_COHESION_EVIDENCE_MISSING":
            fail("namespace authority package overclaims readiness")
        if not row["automatic_ratification_forbidden"]:
            fail("namespace authority package permits automatic ratification")
    p0_namespaces = {
        namespace for row in namespace_review_packages
        if row["priority_band"] == "P0_CROSS_PRODUCT_OR_KNOWN_SPLIT"
        for namespace in row["namespace_refs"]
    }
    if {row["namespace"] for row in p0_namespace_dispositions} != p0_namespaces:
        fail("P0 namespace dispositions do not exactly cover priority-zero namespaces")
    p0_subcontext_refs = {
        ref for row in namespace_review_packages
        if row["priority_band"] == "P0_CROSS_PRODUCT_OR_KNOWN_SPLIT"
        for ref in row["subcontext_candidate_refs"]
    }
    if {row["subcontext_candidate_ref"] for row in p0_subcontext_dispositions} != p0_subcontext_refs:
        fail("P0 subcontext dispositions do not exactly cover priority-zero subcontexts")
    p0_library_refs = {
        library_ref for row in namespace_subcontexts
        if row["subcontext_candidate_ref"] in p0_subcontext_refs
        for library_ref in row["member_library_refs"]
    }
    disposition_libraries = [
        library_ref for row in p0_subcontext_dispositions for library_ref in row["exact_member_library_refs"]
    ]
    if len(disposition_libraries) != len(set(disposition_libraries)) or set(disposition_libraries) != p0_library_refs:
        fail("P0 subcontext dispositions do not partition exact priority-zero libraries")
    disposition_refs = {row["disposition_candidate_ref"] for row in p0_subcontext_dispositions}
    namespace_disposition_refs = {row["namespace_disposition_candidate_ref"] for row in p0_namespace_dispositions}
    p0_product_refs = {
        ref for row in p0_namespace_dispositions
        for ref in row["candidate_owned_product_refs"] + row["candidate_consumer_product_refs"]
    }
    if {row["product_ref"] for row in p0_product_dossier_bindings} != p0_product_refs:
        fail("P0 product dossier bindings do not exactly cover the candidate product universe")
    dossier_binding_by_product = {row["product_ref"]: row for row in p0_product_dossier_bindings}
    dossier_binding_refs = {row["binding_ref"] for row in p0_product_dossier_bindings}
    allowed_dossier_states = {
        "COMPLETE_CANDIDATE_DOSSIER_PRESENT_UNRATIFIED",
        "PRODUCT_DOSSIER_AND_READINESS_RECORD_MISSING",
    }
    for row in p0_product_dossier_bindings:
        if row["binding_state"] not in allowed_dossier_states:
            fail("P0 product dossier binding has unknown state")
        if row["structural_dossier_presence_is_boundary_proof"]:
            fail("P0 product dossier binding promotes structural presence into proof")
        if row["binding_state"] == "COMPLETE_CANDIDATE_DOSSIER_PRESENT_UNRATIFIED":
            if not row["product_readiness_record_ref"] or not row["product_ddd_dossier_ref"]:
                fail("P0 complete dossier binding lacks exact readiness/dossier references")
            if row["product_ratification_state"] != "WITHHELD" or row["product_build_readiness"] != "NOT_BUILD_READY":
                fail("P0 dossier binding bypasses product ratification or build readiness")
        else:
            if row["product_readiness_record_ref"] is not None or row["product_ddd_dossier_ref"] is not None:
                fail("P0 missing dossier binding fabricates a product record")
        expected_dispositions = {
            disposition["disposition_candidate_ref"] for disposition in p0_subcontext_dispositions
            if row["product_ref"] in disposition["candidate_owner_product_refs"] + disposition["candidate_consumer_product_refs"]
        }
        if set(row["subcontext_disposition_candidate_refs"]) != expected_dispositions:
            fail("P0 product dossier binding loses subcontext dispositions")
    allowed_p0_dispositions = {
        "OWNED_CONTEXT_IN_EXISTING_PRODUCT_CANDIDATE", "ACL_CONTEXT_IN_CONSUMER_PRODUCT_CANDIDATE",
        "OWNED_CONTEXT_IN_NEW_PRODUCT_CANDIDATE", "SHARED_METHOD_CONTEXT_NO_PRODUCT_OWNER_CANDIDATE",
        "ASSURANCE_CONTEXT_OWNED_BY_QUERY_PRODUCT_CANDIDATE",
        "CROSS_LAYER_ACL_OWNED_BY_QUERY_PRODUCT_CANDIDATE",
    }
    for row in p0_subcontext_dispositions:
        if row["candidate_disposition"] not in allowed_p0_dispositions:
            fail("P0 subcontext disposition has unknown treatment")
        if not row["semantic_module_candidate_refs"] or not row["evidence_source_refs"]:
            fail("P0 subcontext disposition lacks source/module grounding")
        if row["boundary_verdict"] != "MISSING" or row["owner_verdict"] != "MISSING":
            fail("P0 subcontext disposition overclaims authority")
        if row["candidate_state"] != "REVERSIBLE_P0_SUBCONTEXT_DISPOSITION_UNRATIFIED":
            fail("P0 subcontext disposition is not reversible and unratified")
        if row["candidate_owner_locus_ref"] != row["subcontext_candidate_ref"]:
            fail("P0 subcontext disposition invents an owner locus outside its boundary candidate")
        allowed_products = set(builder.PRODUCT_CANDIDATES_BY_NAMESPACE[row["namespace"]])
        if not set(row["candidate_owner_product_refs"] + row["candidate_consumer_product_refs"]).issubset(allowed_products):
            fail("P0 subcontext disposition invents a product outside the namespace candidate universe")
        expected_dossier_refs = {
            dossier_binding_by_product[ref]["binding_ref"]
            for ref in row["candidate_owner_product_refs"] + row["candidate_consumer_product_refs"]
        }
        if set(row["product_dossier_binding_refs"]) != expected_dossier_refs:
            fail("P0 subcontext disposition does not preserve exact product dossier bindings")
        if row["candidate_disposition"] == "SHARED_METHOD_CONTEXT_NO_PRODUCT_OWNER_CANDIDATE" and row["candidate_owner_product_refs"]:
            fail("shared method context is falsely assigned to a product")
    p0_dispositions_by_namespace: dict[str, set[str]] = {}
    for row in p0_subcontext_dispositions:
        p0_dispositions_by_namespace.setdefault(row["namespace"], set()).add(row["disposition_candidate_ref"])
    allowed_relation_types = {
        "CUSTOMER_SUPPLIER_WITH_ACL", "PUBLISHED_LANGUAGE", "EVIDENCE_HANDOFF",
        "ANTI_CORRUPTION_LAYER", "PUBLISHED_LANGUAGE_WITHOUT_AUTHORITY_TRANSFER",
    }
    for row in p0_namespace_dispositions:
        if set(row["subcontext_disposition_candidate_refs"]) != p0_dispositions_by_namespace[row["namespace"]]:
            fail("P0 namespace disposition does not preserve all subcontext dispositions")
        if row["boundary_verdict"] != "MISSING" or row["candidate_state"] != "REVERSIBLE_P0_NAMESPACE_DISPOSITION_UNRATIFIED":
            fail("P0 namespace disposition overclaims a boundary")
        if len(row["required_negative_twin_refs"]) != 6:
            fail("P0 namespace disposition lacks the six boundary falsifiers")
        for relation in row["relation_candidates"]:
            if relation["relationship_candidate"] not in allowed_relation_types:
                fail("P0 relation has unknown relationship type")
            if not relation["authority_transfer_forbidden"] or relation["boundary_verdict"] != "MISSING":
                fail("P0 relation erases authority or overclaims a boundary")
            if not set(relation["subcontext_candidate_refs"]).issubset(p0_subcontext_refs):
                fail("P0 relation refers outside the P0 subcontext universe")
    twins_by_namespace: dict[str, set[str]] = {}
    for row in p0_boundary_negative_twins:
        twins_by_namespace.setdefault(row["namespace"], set()).add(row["negative_twin_ref"])
        if row["namespace_disposition_candidate_ref"] not in namespace_disposition_refs:
            fail("P0 negative twin has unknown namespace disposition")
        if row["execution_state"] != "UNEXECUTED_SEMANTIC_AND_AUTHORITY_EVIDENCE_REQUIRED" or row["negative_twin_result"] != "MISSING":
            fail("P0 negative twin falsely claims execution")
    if set(twins_by_namespace) != p0_namespaces or any(len(refs) != 6 for refs in twins_by_namespace.values()):
        fail("P0 negative twins do not supply six falsifiers per namespace")

    if len(p0_route_projections) != len(owner_dockets):
        fail("P0 downstream projections do not cover all exact library routes")
    contract_by_library = {row["candidate_library_ref"]: row for row in contract_dockets}
    intake_by_library = {row["candidate_library_ref"]: row for row in intake_routes}
    consolidation_by_library = {row["candidate_library_ref"]: row for row in consolidation_routes}
    projected_p0_libraries = set()
    for row in p0_route_projections:
        library_ref = row["candidate_library_ref"]
        if row["priority_zero_member"]:
            projected_p0_libraries.add(library_ref)
            if row["subcontext_disposition_candidate_ref"] not in disposition_refs:
                fail("P0 route lacks its subcontext disposition")
            if row["namespace_disposition_candidate_ref"] not in namespace_disposition_refs:
                fail("P0 route lacks its namespace disposition")
            if not set(row["product_dossier_binding_refs"]).issubset(dossier_binding_refs):
                fail("P0 route has an unknown product dossier binding")
        elif row["subcontext_disposition_candidate_ref"] is not None or row["namespace_disposition_candidate_ref"] is not None:
            fail("non-P0 route acquires a priority-zero disposition")
        if row["owner_docket_ref"] != owner_by_library[library_ref]["docket_id"]:
            fail("P0 route changes the exact owner docket")
        if row["context_consolidation_route_ref"] != consolidation_by_library[library_ref]["route_id"]:
            fail("P0 route changes the exact consolidation route")
        if row["provisional_contract_docket_ref"] != contract_by_library[library_ref]["docket_id"]:
            fail("P0 route changes the exact contract docket")
        if row["p5_intake_route_ref"] != intake_by_library[library_ref]["intake_route_id"]:
            fail("P0 route changes the exact P5 intake route")
        if row["compiler_admission_state"] != "WITHHELD_BOUNDARY_AND_OWNER_AUTHORITY_MISSING":
            fail("P0 route bypasses compiler admission")
    if projected_p0_libraries != p0_library_refs:
        fail("P0 downstream route projection loses exact P0 libraries")

    if len(p0_finding_projections) != len(boundary_challenge_routes):
        fail("P0 boundary-finding projections do not cover all boundary routes")
    challenge_route_by_finding = {row["boundary_finding_ref"]: row for row in boundary_challenge_routes}
    for row in p0_finding_projections:
        source = challenge_route_by_finding[row["boundary_finding_ref"]]
        expected_related = set(source["slice_candidate_universe_refs"]) & p0_library_refs
        if set(row["priority_zero_related_library_refs"]) != expected_related:
            fail("P0 boundary-finding projection is not the exact slice-universe intersection")
        if row["direct_relevance_or_boundary_claim"]:
            fail("P0 boundary-finding projection turns routing context into evidence")
        if row["boundary_challenge_route_ref"] != source["route_id"]:
            fail("P0 boundary-finding projection changes the exact challenge route")
    expected_cohesion_vacancy_pairs = {
        (hypothesis["hypothesis_ref"], test)
        for hypothesis in consolidation_hypotheses for test in hypothesis["required_cohesion_tests"]
    }
    actual_cohesion_vacancy_pairs = {
        (row["hypothesis_ref"], row["cohesion_test_kind"])
        for row in cohesion_vacancies
    }
    if actual_cohesion_vacancy_pairs != expected_cohesion_vacancy_pairs:
        fail("context cohesion evidence vacancies are not lossless")
    if any(
        not row["candidate_source_refs"]
        or row["status"] != "OPEN_EVIDENCE_AND_BOUNDARY_AUTHORITY_MISSING"
        for row in cohesion_vacancies
    ):
        fail("context cohesion vacancy lacks source grounding or stays falsely closed")
    cohesion_by_program: dict[tuple[str, str], set[str]] = {}
    for row in cohesion_vacancies:
        cohesion_by_program.setdefault(
            (row["hypothesis_kind"], row["cohesion_test_kind"]), set()
        ).add(row["vacancy_id"])
    if len(cohesion_programs) != len(cohesion_by_program):
        fail("context cohesion programs do not factor every hypothesis/test pair")
    for row in cohesion_programs:
        refs = cohesion_by_program[(row["hypothesis_kind"], row["cohesion_test_kind"])]
        if set(row["vacancy_refs"]) != refs or row["vacancy_count"] != len(refs):
            fail("context cohesion program membership mismatch")
        if row["status"] != "OPEN_UNEXECUTED":
            fail("context cohesion evidence program overclaims execution")

    boundary_finding_refs = {row["source_finding_ref"] for row in boundary_routes}
    if {row["boundary_finding_ref"] for row in boundary_challenge_routes} != boundary_finding_refs:
        fail("boundary challenge-evidence routes do not cover all non-vacancy findings")
    owner_libraries_by_slice: dict[str, set[str]] = {}
    for row in owner_dockets:
        owner_libraries_by_slice.setdefault(row["source_slice"], set()).add(row["proposed_library_ref"])
    negative_twin_refs = {row["negative_twin_id"] for row in negative_twins}
    consolidation_hypothesis_refs = {row["hypothesis_ref"] for row in consolidation_hypotheses}
    for row in boundary_challenge_routes:
        expected_universe = owner_libraries_by_slice.get(row["source_slice"], set())
        if set(row["slice_candidate_universe_refs"]) != expected_universe:
            fail("boundary challenge route has an incomplete slice candidate universe")
        ranked_refs = {candidate["candidate_library_ref"] for candidate in row["ranked_related_candidates"]}
        if not ranked_refs.issubset(expected_universe) or len(row["ranked_related_candidates"]) > 10:
            fail("boundary challenge route ranks candidates outside its slice universe")
        if any(candidate["relevance_score"] <= 0 or not candidate["overlap_tokens"] for candidate in row["ranked_related_candidates"]):
            fail("boundary challenge route has unsupported relevance ranking")
        if not set(row["owner_adjudication_candidate_refs"]).issubset(owner_adjudication_refs):
            fail("boundary challenge route has unknown owner-adjudication evidence")
        if not set(row["collision_adjudication_candidate_refs"]).issubset(adjudication_refs):
            fail("boundary challenge route has unknown collision-adjudication evidence")
        if not set(row["collision_negative_twin_refs"]).issubset(negative_twin_refs):
            fail("boundary challenge route has unknown negative-twin evidence")
        if not set(row["context_consolidation_hypothesis_refs"]).issubset(consolidation_hypothesis_refs):
            fail("boundary challenge route has unknown context-consolidation evidence")
        expected_state = "CONTEXT_ROUTED_UNRATIFIED" if expected_universe else "NO_CROSS_SLICE_CANDIDATE_CONTEXT_AVAILABLE"
        expected_universe_state = "PRESENT" if expected_universe else "NO_PROPOSED_LIBRARY_SEAMS_IN_SOURCE_SLICE"
        if row["route_state"] != expected_state or row["candidate_universe_state"] != expected_universe_state:
            fail("boundary challenge route does not distinguish absent candidate universes")
        if row["direct_evidence_claim"] or row["authority_verdict"] != "MISSING":
            fail("boundary challenge route converts context into proof")

    if len(contract_dockets) != len(vacancy_routes):
        fail("provisional contract/lowering dockets do not cover every exact proposed seam")
    if {row["candidate_library_ref"] for row in contract_dockets} != source_vacancies:
        fail("provisional contract/lowering dockets changed proposed seam identities")
    owner_docket_refs = {row["docket_id"] for row in owner_dockets}
    collision_docket_refs = {row["docket_id"] for row in collision_dockets}
    contract_dockets_by_archetype: dict[str, set[str]] = {}
    expected_facet_refs: set[str] | None = None
    for row in contract_dockets:
        if row["owner_docket_ref"] not in owner_docket_refs:
            fail("contract docket has unknown owner docket")
        if not set(row["collision_docket_refs"]).issubset(collision_docket_refs):
            fail("contract docket has unknown collision docket")
        facet_refs = {facet["facet_ref"] for facet in row["required_contract_facets"]}
        if len(facet_refs) != 24 or any(facet["state"] != "REQUIRED_UNRESOLVED" for facet in row["required_contract_facets"]):
            fail("contract docket does not expose all 24 unresolved contract facets")
        if expected_facet_refs is None:
            expected_facet_refs = facet_refs
        elif facet_refs != expected_facet_refs:
            fail("contract facet shape varies across provisional dockets")
        if row["contract_selection_state"] != "WITHHELD_CANDIDATE_NOT_CANONICAL":
            fail("contract selected before canonical boundary ratification")
        if row["compiler_lowering_state"] != "REFUSED_UPSTREAM_RATIFICATION_MISSING" or row["exact_contract_selected"]:
            fail("compiler lowering does not fail closed")
        contract_dockets_by_archetype.setdefault(row["primary_archetype_ref"], set()).add(row["docket_id"])
    if set(contract_dockets_by_archetype) != {row["semantic_archetype_ref"] for row in contract_archetypes}:
        fail("contract-lowering archetypes do not cover docket archetypes")
    for row in contract_archetypes:
        dockets = contract_dockets_by_archetype[row["semantic_archetype_ref"]]
        if row["docket_count"] != len(dockets) or set(row["contract_docket_refs"]) != dockets:
            fail(f"contract-lowering archetype membership mismatch: {row['contract_lowering_archetype_ref']}")
        if row["state"] != "PROVISIONAL_UNRATIFIED":
            fail("contract-lowering archetype overclaims ratification")
    if len(intake_routes) != len(contract_dockets):
        fail("P5 intake route count does not match contract dockets")
    if {row["candidate_library_ref"] for row in intake_routes} != source_vacancies:
        fail("P5 intake routes do not preserve exact candidate identities")
    if any(
        row["current_disposition"] != "WITHHELD_CANDIDATE_NOT_CANONICAL"
        or not row["name_join_forbidden"] or not row["automatic_canonical_mutation_forbidden"]
        for row in intake_routes
    ):
        fail("P5 intake route bypasses canonical admission")

    validate_dag(dag)
    expected_package_subjects = {
        row["archetype_ref"]: set(row["member_library_refs"])
        for row in archetypes if row["member_count"]
    }
    if len(packages) != len(expected_package_subjects) + len(boundary_kinds) + len(collision_families) + len(contract_archetypes):
        fail("ratification packages do not cover all nonempty quotients")
    if any(row["status"] not in {"OPEN_UNRATIFIED", "OPEN_UPSTREAM_BLOCKED"} for row in packages):
        fail("a ratification package claims progress without adjudication")
    if {row["package_ref"] for row in frontier} != {row["package_id"] for row in packages}:
        fail("execution frontier does not cover every ratification package exactly once")
    ready = [row for row in frontier if row["readiness"] == "STRUCTURAL_GATES_REFUSED_AUTHORITY_VERDICT_MISSING"]
    if len(ready) != len(collision_families):
        fail("only collision-family packages should be ready at the current frontier")
    if any(row["package_kind"] != "CROSS_NAMESPACE_COLLISION_REVIEW" for row in ready):
        fail("a downstream package bypasses collision review")
    partial_owner_packages = [
        row for row in frontier
        if row["readiness"] == "PARTIAL_OWNER_EVIDENCE_READY_AUTHORITY_VERDICT_MISSING"
    ]
    ready_owner_subjects = {
        ref for row in partial_owner_packages for ref in row["ready_subject_refs"]
    }
    expected_ready_owner_subjects = {
        row["proposed_library_ref"] for row in owner_dockets
        if row["owner_review_readiness"] == "EVIDENCE_PACKET_READY_OWNER_AUTHORITY_VERDICT_MISSING"
    }
    if ready_owner_subjects != expected_ready_owner_subjects:
        fail("partial owner-review frontier does not expose every collision-free owner docket")
    if any(row["package_kind"] != "LIBRARY_SEAM_ARCHETYPE_REVIEW" for row in partial_owner_packages):
        fail("non-library package claims partial owner readiness")
    if any(not row["automatic_execution_forbidden"] for row in frontier):
        fail("execution frontier permits automatic authority work")
    if admission_audit["candidate_library_seams"] != len(vacancy_routes):
        fail("implementation/vertical admission audit has stale candidate count")
    if admission_audit["provisional_contract_dockets_refusing"] != len(contract_dockets):
        fail("not every provisional contract docket refuses lowering")
    if admission_audit["implementation_work_admissible"] or admission_audit["vertical_work_admissible"]:
        fail("implementation or vertical work admitted before upstream ratification")
    if admission_audit["next_admissible_work"]["collision_family_package_count"] != len(collision_families):
        fail("admission audit does not point to the collision-family frontier")
    if admission_audit["next_admissible_work"]["collision_free_owner_docket_count"] != len(expected_ready_owner_subjects):
        fail("admission audit has stale collision-free owner-docket count")

    zero_fields = [
        "owner_decisions", "owner_selections", "ratified_product_boundaries", "ratified_library_boundaries",
        "exact_contracts_selected", "qualified_implementations", "vertical_acceptances",
        "canonical_gaps_closed",
    ]
    if any(summary[field] != 0 for field in zero_fields) or summary["completion_claim"]:
        fail("frontier makes a false closure claim")
    if summary["exact_findings"] != len(inventory) or summary["ratification_packages"] != len(packages):
        fail("summary counts are stale")
    if summary["semantic_module_grounding_gaps"] != 0:
        fail("owner-candidate semantic-module grounding is incomplete")
    if summary["owner_adjudication_candidates"] != len(owner_adjudications) or summary["owner_authority_verdicts"] != 0:
        fail("summary has stale or overclaimed owner-adjudication state")
    if summary["collision_negative_twins"] != len(negative_twins) or summary["executed_collision_negative_twins"] != 0:
        fail("summary has stale or overclaimed collision negative-twin state")
    if summary["executed_collision_structural_gates"] != len(negative_twin_receipts):
        fail("summary has stale collision structural-gate receipt count")
    if summary["owner_counterfactual_challenges"] != len(owner_challenges) or summary["executed_owner_counterfactual_challenges"] != 0:
        fail("summary has stale or overclaimed owner challenge state")
    if summary["owner_challenge_evidence_vacancies"] != len(owner_evidence_vacancies) or summary["owner_challenge_evidence_programs"] != len(owner_evidence_programs):
        fail("summary has stale owner challenge evidence-program counts")
    if summary["context_consolidation_hypotheses"] != len(consolidation_hypotheses) or summary["context_consolidation_routes"] != len(consolidation_routes):
        fail("summary has stale context-consolidation counts")
    if summary["context_boundary_verdicts"] != 0:
        fail("summary overclaims context-boundary verdicts")
    if summary["namespace_structural_observations"] != len(namespace_observations):
        fail("summary has stale namespace observation count")
    if summary["namespace_boundary_challenge_candidates"] != len(namespace_challenges):
        fail("summary has stale namespace challenge count")
    if summary["namespace_subcontext_candidates"] != len(namespace_subcontexts):
        fail("summary has stale namespace subcontext count")
    if summary["namespace_boundary_authority_verdicts"] != 0:
        fail("summary overclaims namespace boundary authority")
    if summary["namespace_authority_review_packages"] != len(namespace_review_packages):
        fail("summary has stale namespace authority-package count")
    if summary["p0_namespace_disposition_candidates"] != len(p0_namespace_dispositions):
        fail("summary has stale P0 namespace-disposition count")
    if summary["p0_subcontext_disposition_candidates"] != len(p0_subcontext_dispositions):
        fail("summary has stale P0 subcontext-disposition count")
    if summary["p0_exact_library_members"] != len(p0_library_refs):
        fail("summary has stale P0 exact-library count")
    if summary["p0_boundary_negative_twins"] != len(p0_boundary_negative_twins):
        fail("summary has stale P0 negative-twin count")
    if summary["p0_downstream_route_projections"] != len(p0_route_projections):
        fail("summary has stale P0 downstream-projection count")
    if summary["p0_boundary_finding_projections"] != len(p0_finding_projections):
        fail("summary has stale P0 boundary-finding projection count")
    if summary["p0_boundary_finding_projections_with_review_context"] != sum(
        bool(row["priority_zero_related_library_refs"]) for row in p0_finding_projections
    ):
        fail("summary has stale P0 boundary-finding review-context count")
    if summary["p0_boundary_authority_verdicts"] != 0:
        fail("summary overclaims P0 boundary authority")
    if summary["p0_product_dossier_bindings"] != len(p0_product_dossier_bindings):
        fail("summary has stale P0 product-dossier binding count")
    complete_dossiers = sum(
        row["binding_state"] == "COMPLETE_CANDIDATE_DOSSIER_PRESENT_UNRATIFIED"
        for row in p0_product_dossier_bindings
    )
    if summary["p0_complete_candidate_dossiers_present"] != complete_dossiers:
        fail("summary has stale P0 complete-candidate-dossier count")
    if summary["p0_missing_product_dossiers"] != len(p0_product_dossier_bindings) - complete_dossiers:
        fail("summary has stale P0 missing-product-dossier count")
    if summary["context_cohesion_evidence_vacancies"] != len(cohesion_vacancies) or summary["context_cohesion_evidence_programs"] != len(cohesion_programs):
        fail("summary has stale context-cohesion evidence-program counts")
    if summary["boundary_challenge_evidence_routes"] != len(boundary_challenge_routes) or summary["boundary_authority_verdicts"] != 0:
        fail("summary has stale or overclaimed boundary challenge routing")
    with_context = sum(bool(row["slice_candidate_universe_refs"]) for row in boundary_challenge_routes)
    if summary["boundary_routes_with_candidate_context"] != with_context:
        fail("summary has stale boundary routes-with-context count")
    if summary["boundary_routes_without_proposed_seam_universe"] != len(boundary_challenge_routes) - with_context:
        fail("summary has stale boundary routes-without-context count")
    if summary["collision_meaning_partitions"] != len(meaning_partitions):
        fail("summary has stale collision meaning-partition count")
    if summary["collision_adjudication_candidates"] != len(collision_adjudications) or summary["collision_authority_verdicts"] != 0:
        fail("summary has stale or overclaimed collision adjudication state")
    if summary["ready_review_packages"] != len(ready):
        fail("summary has stale ready-review package count")
    if summary["partial_owner_review_packages"] != len(partial_owner_packages):
        fail("summary has stale partial owner-review package count")
    if summary["implementation_work_admissible"] or summary["vertical_work_admissible"]:
        fail("summary admits downstream work prematurely")

    for name, claim in manifest["files"].items():
        payload = (HERE / name).read_bytes()
        if claim["bytes"] != len(payload) or claim["sha256"] != hashlib.sha256(payload).hexdigest():
            fail(f"manifest mismatch: {name}")
    if manifest["completion_claim"]:
        fail("manifest makes a completion claim")

    print(
        "VALIDATION PASS cross-slice boundary frontier: "
        f"{len(inventory)} findings preserved, {len(vacancy_routes)} exact seams routed through "
        f"{sum(row['member_count'] > 0 for row in archetypes)} nonempty semantic quotients, "
        f"{len(owner_dockets)} open owner dockets, {len(collision_dockets)} collision dockets in "
        f"{len(collision_families)} families, {len(boundary_routes)} boundary decisions and "
        f"{len(contract_dockets)} provisional contract/lowering dockets, {len(intake_routes)} withheld "
        f"P5 intake routes and {len(packages)} open ratification packages; "
        "0 boundaries ratified, 0 contracts selected, 0 implementations qualified, 0 vertical acceptances"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
