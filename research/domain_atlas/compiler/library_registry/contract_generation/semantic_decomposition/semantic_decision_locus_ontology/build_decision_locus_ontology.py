#!/usr/bin/env python3
"""Build a bearer- and scope-aware factorization for all semantic-axis work."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
AS_OF = "2026-08-27"
DOCKETS = SEM / "p3_applicability_adjudication/family-axis-review-dockets.jsonl"
FRONTIER = SEM / "semantic_research_frontier/axis-frontier.jsonl"

AXIS_REFINEMENTS = {
    "semantic_object": {
        "refinement_ref": "semantic_object_coordinate_ontology",
        "summary_path": SEM / "semantic_object_coordinate_ontology/summary.json",
    },
    "semantic_role": {
        "refinement_ref": "semantic_role_coordinate_ontology",
        "summary_path": SEM / "semantic_role_coordinate_ontology/summary.json",
    },
    "authority_and_trust": {
        "refinement_ref": "authority_trust_coordinate_ontology",
        "summary_path": SEM / "authority_trust_coordinate_ontology/summary.json",
    },
    "effect_boundary": {
        "refinement_ref": "effect_boundary_coordinate_ontology",
        "summary_path": SEM / "effect_boundary_coordinate_ontology/summary.json",
    },
    "evidence_and_conformance": {
        "refinement_ref": "evidence_conformance_coordinate_ontology",
        "summary_path": SEM / "evidence_conformance_coordinate_ontology/summary.json",
    },
    "grain_and_cardinality": {
        "refinement_ref": "p3e_grain_coordinate_ontology",
        "summary_path": SEM / "p3e_grain_coordinate_ontology/summary.json",
    },
    "state_and_change": {
        "refinement_ref": "p3s_state_change_coordinate_ontology",
        "summary_path": SEM / "p3s_state_change_coordinate_ontology/summary.json",
    },
    "order_and_topology": {
        "refinement_ref": "p3o_order_topology_coordinate_ontology",
        "summary_path": SEM / "p3o_order_topology_coordinate_ontology/summary.json",
    },
    "composition_algebra": {
        "refinement_ref": "p3c_composition_algebra_coordinate_ontology",
        "summary_path": SEM / "p3c_composition_algebra_coordinate_ontology/summary.json",
    },
    "identity_and_equality": {
        "refinement_ref": "p3i_identity_equality_coordinate_ontology",
        "summary_path": SEM / "p3i_identity_equality_coordinate_ontology/summary.json",
    },
    "partiality_and_uncertainty": {
        "refinement_ref": "p3u_partiality_uncertainty_coordinate_ontology",
        "summary_path": SEM / "p3u_partiality_uncertainty_coordinate_ontology/summary.json",
    },
    "time": {
        "refinement_ref": "time_coordinate_ontology",
        "summary_path": SEM / "time_coordinate_ontology/summary.json",
    },
    "representation": {
        "refinement_ref": "representation_coordinate_ontology",
        "summary_path": SEM / "representation_coordinate_ontology/summary.json",
    },
    "compatibility_and_evolution": {
        "refinement_ref": "compatibility_evolution_coordinate_ontology",
        "summary_path": SEM / "compatibility_evolution_coordinate_ontology/summary.json",
    },
    "privacy_security_safety": {
        "refinement_ref": "privacy_security_safety_coordinate_ontology",
        "summary_path": SEM / "privacy_security_safety_coordinate_ontology/summary.json",
    },
    "resources_and_failure": {
        "refinement_ref": "resources_failure_coordinate_ontology",
        "summary_path": SEM / "resources_failure_coordinate_ontology/summary.json",
    },
}


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


PRIMARY_SOURCES = [
    {
        "source_id": "source.decision-locus.owl2-primer",
        "title": "OWL 2 Web Ontology Language Primer",
        "publisher": "W3C",
        "url": "https://www.w3.org/TR/owl2-primer/",
        "bounded_claim": "Classes, properties, individuals, values, equality, restrictions and keys are distinct modeling constructs; spelling does not supply their relationships.",
        "authority_limit": "OWL semantics do not choose SAN bounded contexts, owners, operation contracts or closed-world applicability.",
    },
    {
        "source_id": "source.decision-locus.shacl",
        "title": "Shapes Constraint Language",
        "publisher": "W3C",
        "url": "https://www.w3.org/TR/shacl/",
        "bounded_claim": "Constraints apply to explicit targets and focus nodes, and property shapes apply through paths; a constraint is positioned rather than ambient.",
        "authority_limit": "SHACL validation does not establish domain truth, source authority, repair, acceptance or universal closed-world semantics.",
    },
    {
        "source_id": "source.decision-locus.prov-o",
        "title": "PROV-O: The PROV Ontology",
        "publisher": "W3C",
        "url": "https://www.w3.org/TR/prov-o/",
        "bounded_claim": "Entity, activity and agent are distinct and influence relations can be qualified when role, plan, time or other relation detail matters.",
        "authority_limit": "PROV-O expresses provenance relations; it does not prove causality, correctness, authority or acceptance of the described result.",
    },
    {
        "source_id": "source.decision-locus.odrl",
        "title": "ODRL Information Model 2.2",
        "publisher": "W3C",
        "url": "https://www.w3.org/TR/odrl-model/",
        "bounded_claim": "Permission, prohibition and duty are separate rule forms with explicit parties, actions, assets, constraints and remedies or consequences.",
        "authority_limit": "ODRL is a policy expression model, not proof of legal validity, identity, enforcement, fulfillment or safe effect execution.",
    },
]


BEARER_ARCHETYPES = [
    ("semantic_subject", ["bounded_context_ref", "subject_kind_ref", "subject_ref"], "type, entity, value, occurrence or aggregate that a meaning is about"),
    ("property_or_relation", ["subject_ref", "relation_ref", "object_or_value_ref", "qualification_ref"], "property, edge, path, ordering, topology or qualified relation"),
    ("operation_position", ["subject_ref", "operation_ref", "semantic_position", "port_ref"], "input, output, parameter, state, event, evidence, receipt or sink-effect position"),
    ("transition_or_history", ["subject_ref", "lifecycle_ref", "transition_or_observation_ref", "time_basis_ref"], "state transition, version, change occurrence, observation or historical interval"),
    ("authority_or_policy", ["policy_ref", "party_or_role_ref", "action_or_decision_ref", "resource_or_effect_ref"], "permission, prohibition, obligation, delegation, decision, approval or acceptance"),
    ("representation_artifact", ["meaning_ref", "representation_layer", "artifact_ref", "edition_or_digest_ref"], "logical schema, published language, wire value, byte encoding, physical layout or generated binding"),
    ("execution_obligation", ["operation_ref", "runtime_ref", "resource_or_failure_ref", "scope_ref"], "resource budget, cancellation, retry, failure, effect or operational guarantee"),
    ("evidence_claim", ["claim_ref", "subject_ref", "profile_ref", "evidence_ref"], "claim, argument, evidence, defeater, oracle, observation, verdict or receipt"),
    ("compatibility_path", ["producer_artifact_ref", "consumer_ref", "change_ref", "direction"], "directional compatibility, migration, transform, upcast, backfill, rollout or decommission path"),
    ("composition_expression", ["operator_ref", "operand_refs", "result_ref", "law_profile_ref"], "composition operator, operands, result, algebraic laws, residual information and effects"),
]


def bearer_rows() -> list[dict[str, Any]]:
    rows = []
    for name, key, meaning in BEARER_ARCHETYPES:
        rows.append(
            {
                "record_kind": "semantic_decision_bearer_archetype",
                "archetype_id": f"bearer.semantic-decision.{name}.v1",
                "coordinate_key": key,
                "meaning": meaning,
                "propagation_law": "A decision propagates only when every coordinate in the key and every declared precondition is equal or explicitly mapped without hidden loss.",
                "exception_law": "Any changed coordinate, invariant, authority, effect, time basis, representation, evidence profile or acceptance boundary creates an explicit residual.",
                "completion_claim": False,
            }
        )
    return rows


# axis, bearer archetypes, coordinate questions, dependencies, local-residual triggers
AXIS_PROFILES = [
    ("semantic_object", ["semantic_subject"], ["what kind of thing", "instance versus type versus occurrence", "inside which bounded context"], ["identity_and_equality"], ["different subject kind", "different bounded-context meaning", "type/instance punning"]),
    ("semantic_role", ["semantic_subject", "operation_position"], ["what role", "in which contract or operation", "relative to which counterparty"], ["authority_and_trust", "effect_boundary"], ["same noun in a different interaction", "provider versus semantic owner", "input versus executor"]),
    ("identity_and_equality", ["semantic_subject", "property_or_relation"], ["identifier scope", "occurrence continuity", "value equality", "semantic equivalence", "canonical representation"], ["grain_and_cardinality", "representation", "time"], ["different namespace or lifecycle", "different equality relation", "canonical bytes only"]),
    ("grain_and_cardinality", ["operation_position"], ["semantic unit", "container", "multiplicity", "cardinality bounds", "boundedness and completeness"], ["identity_and_equality", "order_and_topology", "time", "partiality_and_uncertainty"], ["different operation or port", "grain-changing transform", "local rather than global completeness"]),
    ("state_and_change", ["transition_or_history", "operation_position"], ["state subject", "legal transition", "change occurrence", "desired/observed/accepted state"], ["identity_and_equality", "time", "authority_and_trust", "effect_boundary"], ["different lifecycle subject", "observation versus command", "terminality or reversibility differs"]),
    ("time", ["transition_or_history", "property_or_relation"], ["time role", "clock or calendar", "instant or interval", "validity versus recording basis", "precision and uncertainty"], ["state_and_change", "order_and_topology", "partiality_and_uncertainty"], ["different time role", "different clock/calendar", "validity and recording time diverge"]),
    ("order_and_topology", ["property_or_relation", "operation_position"], ["ordered subject", "relation kind", "total/partial/preorder", "partition scope", "topological incidence or path"], ["identity_and_equality", "grain_and_cardinality", "time"], ["local versus global order", "serialization versus semantic order", "topology versus causality"]),
    ("partiality_and_uncertainty", ["operation_position", "evidence_claim"], ["missing/unknown carrier", "reason", "propagation/refusal", "uncertainty kind", "calibration or completeness scope"], ["grain_and_cardinality", "time", "evidence_and_conformance"], ["null versus absent versus unknown", "stale versus probabilistic", "different calibration population"]),
    ("authority_and_trust", ["authority_or_policy", "evidence_claim"], ["who may assert", "who may decide", "who may execute", "delegation and revocation", "who may accept"], ["effect_boundary", "privacy_security_safety", "evidence_and_conformance"], ["approval versus issuance", "decision versus enforcement", "delegation scope or revocation differs"]),
    ("effect_boundary", ["operation_position", "execution_obligation", "authority_or_policy"], ["pure computation", "proposal", "command", "executor", "acknowledgement", "receipt", "accepted business effect"], ["authority_and_trust", "state_and_change", "resources_and_failure"], ["same verb at a different effect stage", "retry or idempotency differs", "acceptance is external"]),
    ("representation", ["representation_artifact", "operation_position"], ["owned meaning", "logical schema", "published language", "wire/byte/physical carrier", "codec and loss"], ["semantic_object", "identity_and_equality", "compatibility_and_evolution"], ["same meaning with different carrier", "lossy mapping", "physical layout mistaken for semantics"]),
    ("composition_algebra", ["composition_expression", "operation_position"], ["operator", "operand/result types", "identity or zero", "laws", "precedence/conflict", "residual information and effects"], ["semantic_object", "effect_boundary", "partiality_and_uncertainty"], ["law preconditions differ", "pure and effectful composition differ", "loss or conflict policy differs"]),
    ("compatibility_and_evolution", ["compatibility_path", "representation_artifact"], ["producer/consumer", "direction", "change kind", "transform/upcast/backfill", "rollout and in-flight disposition"], ["representation", "state_and_change", "evidence_and_conformance"], ["consumer set differs", "backward versus forward direction", "historical replay changes meaning"]),
    ("resources_and_failure", ["execution_obligation", "operation_position"], ["finite budget", "failure stage", "retryability", "cancellation", "overload/backpressure", "recovery evidence"], ["effect_boundary", "state_and_change", "evidence_and_conformance"], ["runtime or target differs", "failure is partial effect", "budget or retry policy differs"]),
    ("evidence_and_conformance", ["evidence_claim", "representation_artifact"], ["bounded claim", "subject edition", "profile", "oracle or observation", "defeaters", "verdict authority"], ["authority_and_trust", "compatibility_and_evolution", "partiality_and_uncertainty"], ["evidence proves a different claim", "profile or edition differs", "observation versus acceptance"]),
    ("privacy_security_safety", ["authority_or_policy", "execution_obligation", "evidence_claim"], ["asset or subject", "purpose", "trust boundary", "threat/hazard", "control", "residual risk and acceptance"], ["authority_and_trust", "effect_boundary", "resources_and_failure"], ["purpose or residency differs", "threat and hazard are collapsed", "control evidence is stale or out of scope"]),
]


def axis_profile_rows() -> list[dict[str, Any]]:
    rows = []
    for axis, archetypes, questions, dependencies, residuals in AXIS_PROFILES:
        rows.append(
            {
                "record_kind": "semantic_axis_decision_locus_profile",
                "profile_id": f"profile.semantic-decision-locus.{axis.replace('_', '-')}.v1",
                "axis": axis,
                "bearer_archetype_refs": [f"bearer.semantic-decision.{name}.v1" for name in archetypes],
                "coordinate_questions": questions,
                "dependency_axis_refs": dependencies,
                "local_residual_triggers": residuals,
                "quotient_levels": [
                    "global non-collapse law",
                    "bearer archetype contract",
                    "family-axis default candidate",
                    "member exception cluster",
                    "operation/port/use-site residual",
                    "exact contract and acceptance evidence",
                ],
                "allowed_propagation": "Import a decision only when its bearer coordinate, dependencies, preconditions, invariants, authority, effect and evidence profile match exactly.",
                "prohibited_inference": "Library name, family membership, lexical facet, modal candidate or evidence presence cannot establish member applicability.",
                "owner_decision": "UNRESOLVED",
                "completion_claim": False,
            }
        )
    return rows


ONTOLOGY = {
    "ontology_id": "ontology.semantic-decision-locus.v1",
    "edition": 1,
    "as_of": AS_OF,
    "question": "What does each semantic decision attach to, at what scope may it propagate, and which changed coordinate forces an explicit residual?",
    "decision_coordinate": [
        "axis_ref",
        "bearer_archetype_ref",
        "bearer_coordinate",
        "bounded_context_ref",
        "scope_ref",
        "profile_or_edition_ref",
        "authority_ref",
        "evidence_ref",
    ],
    "scope_lattice": [
        "global_non_collapse_law",
        "bearer_archetype",
        "family_axis_candidate",
        "member_exception_cluster",
        "library_member",
        "operation_or_port",
        "use_site_or_vertical",
        "runtime_offer",
        "acceptance_context",
    ],
    "propagation_relations": [
        "IMPORT_EXACT",
        "PROFILE_WITH_EXPLICIT_QUALIFICATION",
        "COMPOSE_WITH_DECLARED_LAWS",
        "MAP_WITH_DECLARED_LOSS",
        "OVERRIDE_WITH_OWNER_EVIDENCE",
        "NO_PROPAGATION_LOCAL_RESIDUAL",
    ],
    "decision_states": [
        "DISCOVERY_ONLY",
        "EVIDENCE_CANDIDATE",
        "FAMILY_DEFAULT_CANDIDATE",
        "MEMBER_APPLICABILITY_UNRESOLVED",
        "OWNER_RATIFIED",
        "EXACT_CONTRACT_VALIDATED",
        "IMPLEMENTATION_QUALIFIED",
        "USE_SITE_ACCEPTED",
    ],
    "non_collapse_laws": [
        "axis is not bearer",
        "bearer archetype is not bearer instance",
        "family default is not member applicability",
        "member applicability is not operation-port completeness",
        "exact semantic contract is not implementation",
        "implementation is not provider offer",
        "provider offer is not use-site acceptance",
        "evidence presence is not bounded claim satisfaction",
        "inheritance without coordinate equality is information loss",
    ],
    "source_refs": [row["source_id"] for row in PRIMARY_SOURCES],
    "owner_decisions": 0,
    "member_applicability_decisions": 0,
    "canonical_gaps_closed": 0,
    "completion_claim": False,
}


def build() -> dict[str, Any]:
    profiles = axis_profile_rows()
    profile_by_axis = {row["axis"]: row for row in profiles}
    frontier_by_axis = {row["axis"]: row for row in load_jsonl(FRONTIER)}
    dockets = load_jsonl(DOCKETS)
    if set(profile_by_axis) != set(frontier_by_axis):
        raise ValueError("axis locus profiles differ from the live semantic frontier")
    refinement_summaries = {
        axis: load_json(config["summary_path"])
        for axis, config in AXIS_REFINEMENTS.items()
    }

    factorizations = []
    for docket in sorted(dockets, key=lambda row: (row["semantic_axis"], row["family_ref"])):
        axis = docket["semantic_axis"]
        profile = profile_by_axis[axis]
        frontier = frontier_by_axis[axis]
        refinement = AXIS_REFINEMENTS.get(axis)
        refinement_summary = refinement_summaries.get(axis)
        factorizations.append(
            {
                "record_kind": "family_axis_semantic_factorization",
                "factorization_id": f"factorization.{docket['matrix_ref'].removeprefix('matrix.')}.v1",
                "axis": axis,
                "family_ref": docket["family_ref"],
                "matrix_ref": docket["matrix_ref"],
                "review_docket_ref": docket["docket_id"],
                "decision_locus_profile_ref": profile["profile_id"],
                "bearer_archetype_refs": profile["bearer_archetype_refs"],
                "member_count": docket["member_count"],
                "member_preclassification_refs": docket["member_preclassification_refs"],
                "frontier_lane_ref": frontier["lane_ref"],
                "current_review_class": docket["review_class"],
                "family_default_candidate_ref": docket["review_candidate_default_cluster_ref"],
                "coordinate_refinement_ref": refinement["refinement_ref"] if refinement else None,
                "coordinate_refinement_target_member_routes": refinement_summary["target_member_routes"] if refinement_summary else 0,
                "required_factorized_outputs": [
                    "family bearer-coordinate default or explicit no-default verdict",
                    "member exception clusters keyed by changed coordinates",
                    "operation/port/use-site residuals where the axis profile requires them",
                    "owner receipt and negative twins",
                ],
                "selected_family_default_decision": "UNRESOLVED",
                "member_applicability_decisions": 0,
                "owner_decision": "UNRESOLVED",
                "canonical_gaps_closed": 0,
                "completion_claim": False,
            }
        )

    summary = {
        "program_id": "program.semantic-decision-locus-factorization.v1",
        "as_of": AS_OF,
        "bearer_archetypes": len(BEARER_ARCHETYPES),
        "semantic_axis_profiles": len(profiles),
        "family_axis_factorizations": len(factorizations),
        "member_axis_cells_preserved": sum(row["member_count"] for row in factorizations),
        "initial_family_axis_quotient": len(factorizations),
        "raw_cell_to_family_axis_ratio": round(sum(row["member_count"] for row in factorizations) / len(factorizations), 6),
        "coordinate_refined_axes": len(AXIS_REFINEMENTS),
        "coordinate_refined_target_member_routes": sum(
            row["target_member_routes"] for row in refinement_summaries.values()
        ),
        "coordinate_unrefined_axes": len(profiles) - len(AXIS_REFINEMENTS),
        "family_default_decisions": 0,
        "member_applicability_decisions": 0,
        "owner_decisions": 0,
        "canonical_gaps_closed": 0,
        "completion_claim": False,
    }
    return {
        "ontology": ONTOLOGY,
        "sources": PRIMARY_SOURCES,
        "bearers": bearer_rows(),
        "profiles": profiles,
        "factorizations": factorizations,
        "summary": summary,
    }


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "decision-locus-ontology.json": json.dumps(built["ontology"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "primary-sources.jsonl": "".join(canonical(row) + "\n" for row in built["sources"]),
        "bearer-archetypes.jsonl": "".join(canonical(row) + "\n" for row in built["bearers"]),
        "axis-locus-profiles.jsonl": "".join(canonical(row) + "\n" for row in built["profiles"]),
        "family-axis-factorizations.jsonl": "".join(canonical(row) + "\n" for row in built["factorizations"]),
        "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    claims = {
        name: {"bytes": len(text.encode()), "sha256": hashlib.sha256(text.encode()).hexdigest()}
        for name, text in files.items()
    }
    files["manifest.json"] = json.dumps(
        {
            "manifest_id": "manifest.semantic-decision-locus-factorization.v1",
            "as_of": AS_OF,
            "files": claims,
            "completion_claim": False,
        },
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    ) + "\n"
    return files


def main() -> int:
    for name, text in outputs().items():
        (HERE / name).write_text(text)
    summary = build()["summary"]
    print(
        "BUILD PASS semantic decision locus: "
        f"{summary['semantic_axis_profiles']} axes and {summary['member_axis_cells_preserved']} cells "
        f"factor through {summary['family_axis_factorizations']} family-axis quotients; decisions remain zero"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
