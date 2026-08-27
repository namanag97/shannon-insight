#!/usr/bin/env python3
"""Validate P2 owner-adjudication coverage without ratifying any owner."""
from __future__ import annotations

import collections
import hashlib
import json

from build_p2 import (
    CHALLENGE_ONTOLOGY,
    DEPENDENCY_EDGES,
    DISPOSITION_ONTOLOGY,
    HERE,
    LIBRARY_CONTRIBUTIONS,
    NAME_DERIVED_FEATURES,
    P1,
    RATIFICATION_CONTRACT,
    ROUTE_TO_WAVE,
    challenge_class,
    load_jsonl,
    outputs,
    proposed_owners,
    without_name_derived_evidence,
)


def acyclic(waves: list[dict]) -> bool:
    dependencies = {row["wave_id"]: set(row["depends_on_wave_refs"]) for row in waves}
    resolved = set()
    while dependencies:
        ready = sorted(key for key, refs in dependencies.items() if refs <= resolved)
        if not ready:
            return False
        for key in ready:
            resolved.add(key)
            del dependencies[key]
    return True


def main() -> int:
    expected = outputs()
    for name, text in expected.items():
        path = HERE / name
        assert path.is_file() and path.read_text() == text, f"stale {name}"

    manifest = json.loads((HERE / "manifest.json").read_text())
    assert manifest["completion_claim"] is False
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"]
        assert hashlib.sha256(data).hexdigest() == claim["sha256"], name

    summary = json.loads((HERE / "summary.json").read_text())
    dockets = load_jsonl(HERE / "owner-adjudication-dockets.jsonl")
    occurrences = load_jsonl(HERE / "occurrence-disposition-candidates.jsonl")
    units = load_jsonl(HERE / "owner-decision-units.jsonl")
    waves = load_jsonl(HERE / "owner-decision-waves.jsonl")
    owner_proposals = load_jsonl(HERE / "owner-proposals.jsonl")
    occurrence_proposals = load_jsonl(HERE / "occurrence-relation-proposals.jsonl")
    proposal_conflicts = load_jsonl(HERE / "proposal-conflicts.jsonl")
    proposal_counterfactuals = load_jsonl(HERE / "owner-proposal-counterfactuals.jsonl")
    challenge_packages = load_jsonl(HERE / "owner-adjudication-challenge-packages.jsonl")
    ratification_templates = load_jsonl(HERE / "owner-ratification-packet-templates.jsonl")
    packets = load_jsonl(P1 / "symbol-adjudication-packets.jsonl")
    sources = load_jsonl(P1 / "primary-sources.jsonl")
    libraries = load_jsonl(LIBRARY_CONTRIBUTIONS)
    dependency_edges = load_jsonl(DEPENDENCY_EDGES)

    packet_by_ref = {row["packet_id"]: row for row in packets}
    source_ids = {row["source_id"] for row in sources}
    assert len(packet_by_ref) == len(packets) == 210
    assert len(source_ids) == len(sources)
    assert len(dockets) == summary["symbol_dockets"] == 210
    assert len(occurrences) == summary["represented_occurrences"] == 666
    assert len(units) == summary["owner_decision_units"] == 108
    assert len(waves) == summary["owner_decision_waves"] == 4
    assert len(owner_proposals) == summary["owner_proposals"] == 210
    assert len(occurrence_proposals) == summary["occurrence_relation_proposals"] == 666
    assert len(proposal_conflicts) == summary["proposal_conflicts"] == 118
    assert len(proposal_counterfactuals) == summary["proposal_counterfactuals"] == 210
    assert summary["owner_proposals_with_named_candidates"] == 116
    assert summary["owner_proposals_blocked"] == 94
    assert summary["occurrence_relation_proposals_unresolved"] == 345
    assert summary["counterfactually_stable_owner_proposals"] == 195
    assert summary["counterfactually_unstable_owner_proposals"] == 15
    assert len(challenge_packages) == summary["owner_adjudication_challenge_packages"] == 29
    assert len(ratification_templates) == summary["ratification_packet_templates"] == 210
    assert summary["ratification_packet_templates_ready_for_authority_review"] == 92
    assert summary["ratification_packet_templates_blocked"] == 118
    assert summary["symbols_with_bounded_primary_research"] == 210
    assert summary["symbols_with_explicit_owner_hypotheses"] == 2
    assert summary["symbols_with_disposition_hypotheses"] == 70
    assert summary["ratified_symbol_owners"] == summary["ratified_occurrence_dispositions"] == 0
    assert summary["canonical_mutations_allowed"] == summary["canonical_exact_gaps_closed"] == 0
    assert summary["completion_claim"] is False

    docket_packet_refs = [row["symbol_packet_ref"] for row in dockets]
    assert len(docket_packet_refs) == len(set(docket_packet_refs)) == 210
    assert set(docket_packet_refs) == set(packet_by_ref)
    assert [row["priority_rank"] for row in dockets] == list(range(1, 211))
    assert collections.Counter(row["research_route"] for row in dockets) == collections.Counter({
        "CROSS_FAMILY_SHARED_OWNER_HYPOTHESIS_RESEARCH": 38,
        "FAMILY_SHARED_OWNER_OR_LOCAL_IMPORT_RESEARCH": 95,
        "HOMONYM_OR_DEFINITION_CONFLICT_RESEARCH": 77,
    })
    assert all(row["research_state"] == "BOUNDED_PRIMARY_RESEARCH_COMPLETE" for row in dockets)
    assert all(row["research_basis_refs"] and row["source_refs"] for row in dockets)
    assert all(set(row["source_refs"]) <= source_ids for row in dockets)
    assert all(row["selected_symbol_disposition"] == "UNRESOLVED" for row in dockets)
    assert all(row["selected_semantic_owner_ref"] is None and row["ratification_receipt_ref"] is None for row in dockets)
    assert all(row["allowed_symbol_dispositions"] == DISPOSITION_ONTOLOGY["symbol_dispositions"] for row in dockets)
    assert all(row["required_owner_decisions"] and row["non_collapse_laws"] and row["authority_limits"] for row in dockets)
    assert all(not row["canonical_mutation_allowed"] and row["canonical_gaps_closed"] == 0 and not row["completion_claim"] for row in dockets)
    assert all(row["decision_wave_ref"] == ROUTE_TO_WAVE[row["research_route"]] for row in dockets)

    expected_occurrences = {
        (packet["packet_id"], occurrence["library_ref"], occurrence["name"], occurrence["definition_digest"])
        for packet in packets
        for occurrence in packet["occurrences"]
    }
    actual_occurrences = {
        (row["symbol_packet_ref"], row["library_ref"], row["current_public_name"], row["current_definition_digest"])
        for row in occurrences
    }
    assert len(expected_occurrences) == len(actual_occurrences) == 666
    assert expected_occurrences == actual_occurrences
    assert len({row["occurrence_id"] for row in occurrences}) == 666
    assert all(row["docket_ref"] in {d["docket_id"] for d in dockets} for row in occurrences)
    assert all(row["selected_occurrence_relation"] == "UNRESOLVED" and row["selected_owner_ref"] is None for row in occurrences)
    assert all(row["allowed_occurrence_relations"] == DISPOSITION_ONTOLOGY["occurrence_relations"] for row in occurrences)
    assert all(row["ratification_receipt_ref"] is None and not row["canonical_mutation_allowed"] and row["canonical_gaps_closed"] == 0 for row in occurrences)
    assert all(not row["completion_claim"] and row["status"] == "BLOCKED_PENDING_SYMBOL_OWNER_RATIFICATION" for row in occurrences)

    # Evidence-ranked proposals are decision support only. They must cover the exact decision
    # surface, remain unratified and never close or mutate a canonical gap.
    docket_by_id = {row["docket_id"]: row for row in dockets}
    occurrence_by_id = {row["occurrence_id"]: row for row in occurrences}
    library_by_id = {row["library_id"]: row for row in libraries}
    edge_pairs = {(row["from_ref"], row["to_ref"]) for row in dependency_edges}
    proposal_by_id = {row["proposal_id"]: row for row in owner_proposals}
    assert len(docket_by_id) == len(dockets)
    assert len(occurrence_by_id) == len(occurrences)
    assert len(library_by_id) == len(libraries)
    assert len(proposal_by_id) == len(owner_proposals)
    assert {row["docket_ref"] for row in owner_proposals} == set(docket_by_id)
    assert {row["symbol_packet_ref"] for row in owner_proposals} == set(packet_by_ref)
    assert sum(bool(row["proposed_owner_refs"]) for row in owner_proposals) == 116
    assert sum(row["status"] == "BLOCKED_NEEDS_OWNER_EVIDENCE" for row in owner_proposals) == 94

    allowed_dispositions = set(DISPOSITION_ONTOLOGY["symbol_dispositions"])
    forbidden_owner_classes = {"provider_adapter", "target_backend"}
    for proposal in owner_proposals:
        docket = docket_by_id[proposal["docket_ref"]]
        docket_occurrence_libraries = {
            row["library_ref"] for row in occurrences if row["docket_ref"] == docket["docket_id"]
        }
        ranking_refs = [row["library_ref"] for row in proposal["candidate_rankings"]]
        ranking_scores = [row["score"] for row in proposal["candidate_rankings"]]
        assert proposal["symbol_ref"] == docket["symbol_ref"]
        assert proposal["symbol_packet_ref"] == docket["symbol_packet_ref"]
        assert proposal["proposed_symbol_disposition"] in allowed_dispositions
        assert len(ranking_refs) == len(set(ranking_refs))
        assert set(ranking_refs) == docket_occurrence_libraries
        assert ranking_scores == sorted(ranking_scores, reverse=True)
        assert set(proposal["proposed_owner_refs"]) <= docket_occurrence_libraries
        assert all(library_by_id[ref]["library_class"] not in forbidden_owner_classes for ref in proposal["proposed_owner_refs"])
        assert proposal["ratification_required"] and proposal["ratification_receipt_ref"] is None
        assert not proposal["canonical_mutation_allowed"] and proposal["canonical_gaps_closed"] == 0
        assert not proposal["completion_claim"]
        if proposal["proposed_owner_refs"]:
            assert proposal["proposed_symbol_disposition"] != "UNRESOLVED"
            assert proposal["status"] == "PROPOSED_UNRATIFIED"
        else:
            assert proposal["status"] == "BLOCKED_NEEDS_OWNER_EVIDENCE"
        for ranking in proposal["candidate_rankings"]:
            assert ranking["library_class"] == library_by_id[ranking["library_ref"]]["library_class"]
            assert ranking["evidence_features"]
            for feature in ranking["evidence_features"]:
                if feature["feature"] == "explicit_owner_context_dependency_incoming":
                    assert all((source, ranking["library_ref"]) in edge_pairs for source in feature["value"])
                if feature["feature"] == "explicit_semantic_contract_dependency_outgoing":
                    assert all((ranking["library_ref"], target) in edge_pairs for target in feature["value"])

    assert len({row["relation_proposal_id"] for row in occurrence_proposals}) == 666
    assert {row["occurrence_ref"] for row in occurrence_proposals} == set(occurrence_by_id)
    assert sum(row["proposed_occurrence_relation"] == "UNRESOLVED" for row in occurrence_proposals) == 345
    allowed_relations = set(DISPOSITION_ONTOLOGY["occurrence_relations"])
    for relation in occurrence_proposals:
        occurrence = occurrence_by_id[relation["occurrence_ref"]]
        owner_proposal = proposal_by_id[relation["owner_proposal_ref"]]
        assert relation["docket_ref"] == occurrence["docket_ref"] == owner_proposal["docket_ref"]
        assert relation["symbol_ref"] == occurrence["symbol_ref"] == owner_proposal["symbol_ref"]
        assert relation["library_ref"] == occurrence["library_ref"]
        assert relation["profile_candidates"] == occurrence["local_profile_candidates"]
        assert relation["proposed_occurrence_relation"] in allowed_relations
        assert relation["proposed_owner_ref"] is None or relation["proposed_owner_ref"] in owner_proposal["proposed_owner_refs"]
        assert relation["ratification_required"] and relation["ratification_receipt_ref"] is None
        assert not relation["canonical_mutation_allowed"] and relation["canonical_gaps_closed"] == 0
        assert not relation["completion_claim"]
        if relation["proposed_occurrence_relation"] == "UNRESOLVED":
            assert relation["proposed_owner_ref"] is None
            assert relation["status"] == "BLOCKED_PENDING_OWNER_EVIDENCE"
            assert relation["confidence"] == "UNRESOLVED"
        else:
            assert relation["proposed_owner_ref"] is not None
            assert relation["status"] == "PROPOSED_UNRATIFIED"
        if relation["proposed_occurrence_relation"] == "OWNER_DECLARATION":
            assert relation["library_ref"] == relation["proposed_owner_ref"]
        if relation["proposed_occurrence_relation"] in {"IMPORT_EXACT", "IMPORT_WITH_PROFILE", "QUALIFIED_LOCAL_HOMONYM"}:
            assert relation["library_ref"] != relation["proposed_owner_ref"]

    expected_conflict_proposals = {
        row["proposal_id"]
        for row in owner_proposals
        if row["blockers"] or row["proposed_symbol_disposition"] == "UNRESOLVED" or not row["proposed_owner_refs"]
    }
    assert len({row["conflict_id"] for row in proposal_conflicts}) == len(proposal_conflicts)
    assert {row["proposal_ref"] for row in proposal_conflicts} == expected_conflict_proposals
    assert all(row["status"] == "OPEN" and not row["completion_claim"] for row in proposal_conflicts)

    counterfactual_by_proposal = {row["proposal_ref"]: row for row in proposal_counterfactuals}
    assert len(counterfactual_by_proposal) == len(proposal_counterfactuals) == 210
    assert set(counterfactual_by_proposal) == set(proposal_by_id)
    assert collections.Counter(row["stability"] for row in proposal_counterfactuals) == {"STABLE": 195, "UNSTABLE": 15}
    for proposal_id, counterfactual in counterfactual_by_proposal.items():
        proposal = proposal_by_id[proposal_id]
        recomputed_rankings = without_name_derived_evidence(proposal["candidate_rankings"])
        recomputed_owners, recomputed_confidence, recomputed_blockers = proposed_owners(
            proposal["proposed_symbol_disposition"], recomputed_rankings
        )
        assert counterfactual["removed_feature_kinds"] == sorted(NAME_DERIVED_FEATURES)
        assert counterfactual["counterfactual_owner_refs"] == recomputed_owners
        assert counterfactual["counterfactual_confidence"] == recomputed_confidence
        assert counterfactual["counterfactual_blockers"] == recomputed_blockers
        assert counterfactual["stability"] == (
            "STABLE" if counterfactual["baseline_owner_refs"] == recomputed_owners else "UNSTABLE"
        )
        if counterfactual["stability"] == "STABLE":
            assert proposal["proposed_owner_refs"] == counterfactual["baseline_owner_refs"]
        else:
            assert proposal["proposed_owner_refs"] == []
            assert "owner proposal changes when all name-derived evidence is removed" in proposal["blockers"]
        assert counterfactual["ratification_required"]
        assert not counterfactual["canonical_mutation_allowed"]
        assert counterfactual["canonical_gaps_closed"] == 0 and not counterfactual["completion_claim"]

    conflict_by_id = {row["conflict_id"]: row for row in proposal_conflicts}
    challenge_member_refs = [ref for row in challenge_packages for ref in row["conflict_refs"]]
    assert len(challenge_member_refs) == len(set(challenge_member_refs)) == len(proposal_conflicts) == 118
    assert set(challenge_member_refs) == set(conflict_by_id)
    assert sum(row["member_count"] for row in challenge_packages) == 118
    package_keys = {
        (row["challenge_class"], row["research_route"], row["research_archetype"])
        for row in challenge_packages
    }
    assert len(package_keys) == len(challenge_packages) == 29
    for package in challenge_packages:
        assert package["challenge_class"] in CHALLENGE_ONTOLOGY
        ontology = CHALLENGE_ONTOLOGY[package["challenge_class"]]
        assert package["semantic_axis_refs"] == ontology["semantic_axis_refs"]
        assert package["challenge_questions"] == ontology["questions"]
        assert package["member_count"] == len(package["conflict_refs"])
        assert len({*package["conflict_refs"]}) == package["member_count"]
        for conflict_ref, proposal_ref, docket_ref, symbol_ref in zip(
            package["conflict_refs"],
            package["proposal_refs"],
            package["docket_refs"],
            package["symbol_refs"],
        ):
            conflict = conflict_by_id[conflict_ref]
            proposal = proposal_by_id[proposal_ref]
            docket = docket_by_id[docket_ref]
            counterfactual = counterfactual_by_proposal[proposal_ref]
            assert conflict["proposal_ref"] == proposal_ref
            assert conflict["docket_ref"] == docket_ref
            assert conflict["symbol_ref"] == symbol_ref == proposal["symbol_ref"] == docket["symbol_ref"]
            assert challenge_class(conflict, proposal, counterfactual) == package["challenge_class"]
            assert docket["research_route"] == package["research_route"]
            assert docket["research_archetype"] == package["research_archetype"]
        assert package["decision_grain"] == "PER_SYMBOL_AND_PER_EXACT_OCCURRENCE"
        assert package["ratification_required"] and package["status"] == "OPEN_REVIEW_QUOTIENT"
        assert not package["canonical_mutation_allowed"] and package["canonical_gaps_closed"] == 0
        assert not package["completion_claim"]

    relation_proposal_by_id = {row["relation_proposal_id"]: row for row in occurrence_proposals}
    challenge_package_ids = {row["challenge_package_id"] for row in challenge_packages}
    ratification_occurrence_refs = [
        ref for row in ratification_templates for ref in row["occurrence_relation_proposal_refs"]
    ]
    assert len(ratification_occurrence_refs) == len(set(ratification_occurrence_refs)) == 666
    assert set(ratification_occurrence_refs) == set(relation_proposal_by_id)
    assert collections.Counter(row["status"] for row in ratification_templates) == {
        "READY_FOR_NAMED_AUTHORITY_REVIEW": 92,
        "BLOCKED_BY_CHALLENGE_PACKAGE": 118,
    }
    for template in ratification_templates:
        docket = docket_by_id[template["docket_ref"]]
        proposal = proposal_by_id[template["proposal_ref"]]
        counterfactual = counterfactual_by_proposal[template["proposal_ref"]]
        template_relations = [relation_proposal_by_id[ref] for ref in template["occurrence_relation_proposal_refs"]]
        assert template["symbol_ref"] == docket["symbol_ref"] == proposal["symbol_ref"]
        assert template["symbol_packet_ref"] == docket["symbol_packet_ref"]
        assert template["family_refs"] == docket["family_refs"]
        assert template["counterfactual_ref"] == counterfactual["counterfactual_id"]
        assert template["candidate_symbol_disposition"] == proposal["proposed_symbol_disposition"]
        assert template["candidate_owner_refs"] == proposal["proposed_owner_refs"]
        assert template["candidate_confidence"] == proposal["confidence"]
        assert template["occurrence_count"] == len(template_relations) == docket["occurrence_count"]
        assert template["unresolved_occurrence_count"] == sum(
            row["proposed_occurrence_relation"] == "UNRESOLVED" for row in template_relations
        )
        assert all(row["owner_proposal_ref"] == proposal["proposal_id"] for row in template_relations)
        assert template["required_receipt_fields"] == RATIFICATION_CONTRACT["required_receipt_fields"]
        assert all(value is None for value in template["submission"].values())
        assert template["ratification_receipt_ref"] is None and template["ratification_required"]
        assert not template["canonical_mutation_allowed"] and template["canonical_gaps_closed"] == 0
        assert not template["completion_claim"]
        if template["status"] == "READY_FOR_NAMED_AUTHORITY_REVIEW":
            assert template["conflict_ref"] is None and template["challenge_package_ref"] is None
            assert proposal["proposed_owner_refs"] and counterfactual["stability"] == "STABLE"
            assert template["unresolved_occurrence_count"] == 0
        else:
            assert template["conflict_ref"] in conflict_by_id
            assert template["challenge_package_ref"] in challenge_package_ids

    unit_packet_refs = [ref for row in units for ref in row["symbol_packet_refs"]]
    assert len(unit_packet_refs) == len(set(unit_packet_refs)) == 210
    assert set(unit_packet_refs) == set(packet_by_ref)
    assert sum(row["symbol_count"] for row in units) == 210
    assert sum(row["represented_occurrence_count"] for row in units) == 666
    assert sum(row["unit_kind"] == "DIRECT_HIGH_FANOUT_SYMBOL" for row in units) == 19
    assert sum(row["unit_kind"] == "LOSSLESS_RESEARCH_BATCH_QUOTIENT" for row in units) == 89
    assert all(len({packet_by_ref[ref]["research_route"] for ref in row["symbol_packet_refs"]}) == 1 for row in units)
    assert all(row["decision_wave_ref"] == ROUTE_TO_WAVE[row["research_route"]] for row in units)
    assert all(row["decision_grain"] == "PER_SYMBOL_AND_PER_EXACT_OCCURRENCE" for row in units)
    assert all(not row["canonical_mutation_allowed"] and row["canonical_gaps_closed"] == 0 and not row["completion_claim"] for row in units)

    assert [row["execution_rank"] for row in waves] == [1, 2, 3, 4]
    assert acyclic(waves)
    first_three = waves[:3]
    wave_unit_refs = [ref for row in first_three for ref in row["decision_unit_refs"]]
    assert len(wave_unit_refs) == len(set(wave_unit_refs)) == 108
    assert set(wave_unit_refs) == {row["decision_unit_id"] for row in units}
    wave_packet_refs = [ref for row in first_three for ref in row["symbol_packet_refs"]]
    assert len(wave_packet_refs) == len(set(wave_packet_refs)) == 210
    assert set(wave_packet_refs) == set(packet_by_ref)
    assert [row["symbol_count"] for row in first_three] == [38, 95, 77]
    occurrence_wave = waves[3]
    assert occurrence_wave["symbol_count"] == 210 and occurrence_wave["represented_occurrence_count"] == 666
    assert set(occurrence_wave["symbol_docket_refs"]) == {row["docket_id"] for row in dockets}
    assert occurrence_wave["depends_on_wave_refs"] == [row["wave_id"] for row in first_three]
    assert all(not row["completion_claim"] for row in waves)

    for claim in summary["input_snapshot"]["files"]:
        path = HERE.parents[6] / claim["path"]
        data = path.read_bytes()
        assert len(data) == claim["bytes"]
        assert hashlib.sha256(data).hexdigest() == claim["sha256"]
        assert len(load_jsonl(path)) == claim["record_count"]

    print("PASS P2 owner adjudication: 210 researched symbols and 666 exact occurrences; 116 counterfactually stable named-owner proposals, 118 open conflicts in 29 challenge packages, 92 authority-review-ready templates, 0 ratified owners or canonical mutations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
