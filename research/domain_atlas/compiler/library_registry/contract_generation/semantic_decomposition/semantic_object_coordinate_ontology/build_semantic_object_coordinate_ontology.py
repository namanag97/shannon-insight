#!/usr/bin/env python3
"""Build a bearer-positioned semantic-object ontology and lossless all-member rebase."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
AS_OF = "2026-08-27"
PRECLASSIFICATIONS = SEM / "applicability_matrices/member-preclassifications.jsonl"
sys.path.insert(0, str(SEM))
from member_axis_rebase import build_member_rebase, load_jsonl  # noqa: E402


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


PRIMARY_SOURCES = [
    {"source_id":"source.semantic-object.rdf12","title":"RDF 1.2 Concepts and Abstract Data Model","publisher":"W3C","url":"https://www.w3.org/TR/rdf12-concepts/","bounded_implication":"Resources, referents, IRIs, literals, blank nodes, triple terms, statements, graphs and datasets are distinct constructs; an RDF graph is a symbolic structure rather than a domain conceptual model.","authority_limit":"RDF does not choose a bounded-context subject kind, owner, identity, lifecycle, role, truth, authority or application closed-world policy."},
    {"source_id":"source.semantic-object.owl2-syntax","title":"OWL 2 Structural Specification and Functional-Style Syntax","publisher":"W3C","url":"https://www.w3.org/TR/owl2-syntax/","bounded_implication":"Classes, datatypes, object/data/annotation properties, named/anonymous individuals, literals, axioms and ontologies occupy distinct language positions, with constrained metamodeling.","authority_limit":"OWL categories and punning do not establish SAN domain kinds, aggregate boundaries, operational lifecycle, assertion authority or member applicability."},
    {"source_id":"source.semantic-object.prov-o","title":"PROV-O: The PROV Ontology","publisher":"W3C","url":"https://www.w3.org/TR/prov-o/","bounded_implication":"Entities with fixed aspects, activities occurring over time, responsible agents and generation/usage/invalidation relations are distinct provenance subjects.","authority_limit":"Provenance classification does not prove domain truth, causality, ownership, validity, acceptance or exact operational semantics."},
    {"source_id":"source.semantic-object.json-schema","title":"JSON Schema Core 2020-12","publisher":"JSON Schema","url":"https://json-schema.org/draft/2020-12/json-schema-core","bounded_implication":"JSON instances, schema documents, vocabularies, assertions, annotations, applicators and locations are distinct roles even when all use JSON carriers.","authority_limit":"Carrier validation does not choose domain referents, identity, ownership, lifecycle, truth, effects or semantic compatibility."},
    {"source_id":"source.semantic-object.odrl","title":"ODRL Information Model 2.2","publisher":"W3C","url":"https://www.w3.org/TR/odrl-model/","bounded_implication":"Policies, rules, permissions, prohibitions, duties, assets, parties, actions, constraints, offers and agreements have different normative positions and conflict behavior.","authority_limit":"ODRL does not make every rule a policy, every resource an asset, an offer a grant, or syntax an enforced effect."},
    {"source_id":"source.semantic-object.cloudevents","title":"CloudEvents Specification","publisher":"CNCF","url":"https://github.com/cloudevents/spec/blob/main/cloudevents/spec.md","bounded_implication":"An event has context attributes and data describing an occurrence; event envelope, occurrence and payload are separable.","authority_limit":"An event envelope does not establish business truth, observation completeness, command intent, state, causal sufficiency or accepted effect."},
    {"source_id":"source.semantic-object.verifiable-credentials","title":"Verifiable Credentials Data Model v2.0","publisher":"W3C","url":"https://www.w3.org/TR/vc-data-model-2.0/","bounded_implication":"Issuer, holder, subject, claims, evidence, status and securing mechanisms occupy distinct roles in a credential ecosystem.","authority_limit":"Cryptographic verification is not truth of claims, subject identity, authority for every use, current validity or acceptance."},
    {"source_id":"source.semantic-object.kubernetes-api","title":"Kubernetes API Conventions","publisher":"Kubernetes","url":"https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md","bounded_implication":"API resources distinguish desired specification, current status, object identity, generations, conditions and subresources.","authority_limit":"A resource representation or status field is not a universal domain aggregate, observation truth, desired-state authority or accepted external effect."},
]


ARCHETYPES = [
    ("typed_value","Identity-less value interpreted under an exact semantic type and equality profile."),
    ("quantity_or_measure","Value with dimension, unit, scale, uncertainty and measurement semantics."),
    ("identifier_or_reference","Symbol or handle intended to denote or resolve another subject."),
    ("domain_entity","Identity-bearing subject with continuity across state change."),
    ("aggregate_or_consistency_boundary","Entity cluster controlled through one root and invariant boundary."),
    ("historical_occurrence","Particular happening or existence occurrence distinct from its description."),
    ("domain_event","Past-tense domain fact about a transition or occurrence."),
    ("fact_or_assertion","Proposition asserted true within a scope, authority and time profile."),
    ("observation_or_measurement","Act/result of observing a subject under a procedure and conditions."),
    ("command_or_request","Refusable request to attempt a state change or effect."),
    ("intent_goal_or_requirement","Desired outcome or constraint, not an execution plan or effect."),
    ("plan_workflow_or_process","Prospective or executable ordering of work and decisions."),
    ("rule_constraint_or_specification","Predicate or normative condition over candidate worlds or actions."),
    ("policy","Authority-scoped collection of rules with applicability, precedence and effect semantics."),
    ("decision_or_judgment","Outcome of evaluating evidence, policy, discretion or optimization."),
    ("state","Current semantic condition of an identity-bearing subject."),
    ("snapshot_or_view","Representation selected from state/history under a declared cut and projection."),
    ("relation_or_edge","Typed association among subjects, possibly identity- and lifecycle-bearing itself."),
    ("graph_or_dataset","Scoped collection of statements, relations or observations with boundary semantics."),
    ("collection_or_stream","Multiplicity-bearing container whose set/bag/sequence/map/stream laws matter."),
    ("document_message_or_envelope","Communicative or documentary artifact with authorship and envelope/content seams."),
    ("schema_type_or_vocabulary_term","Metalevel constraint or meaning declaration, not its instance."),
    ("representation_artifact","Logical, serialized or physical carrier of another subject or assertion."),
    ("resource","Consumable, allocatable or addressable thing with capacity and lifecycle."),
    ("capability_or_offer","Potential ability or provider offer, not allocation, entitlement or execution."),
    ("entitlement_or_authorization","Authority-scoped permission to request or perform an action."),
    ("allocation_lease_or_reservation","Time/scope-bounded assignment of resource capacity."),
    ("execution_attempt_or_activity","Concrete attempt/activity with inputs, state, failures and receipts."),
    ("effect_or_outcome","World change or result, distinct from request, attempt and acceptance."),
    ("claim","Contestable proposition advanced by a claimant."),
    ("evidence_item","Artifact or observation offered in support or defeat of a claim."),
    ("proof_attestation_or_receipt","Scoped verification or execution evidence, not universal truth."),
    ("actor_agent_or_party","Subject occupying responsibility, authority or participation roles."),
]


KERNELS = [
    "classify_subject_kind","declare_type","instantiate","construct_value","create_entity","create_occurrence",
    "assert_fact","retract_or_supersede_assertion","record_observation","issue_command","refuse_command",
    "declare_intent","refine_requirement","construct_plan","start_execution_attempt","complete_or_fail_attempt",
    "evaluate_rule","evaluate_policy","render_decision","transition_state","take_snapshot","project_view",
    "create_relation","end_relation","construct_graph_or_dataset","collect_or_stream","publish_document_or_message",
    "validate_instance_against_schema","annotate_instance","encode_representation","decode_representation",
    "resolve_reference","reify_relation_or_statement","derive_subject","copy_or_clone","version_or_supersede",
    "discover_resource","advertise_capability","require_capability","authorize_or_entitle","allocate_or_lease",
    "release_or_revoke_allocation","propose_effect","execute_effect","accept_or_reject_outcome","make_claim",
    "attach_evidence","evaluate_evidence","verify_proof_or_attestation","issue_receipt","materialize_or_dematerialize",
    "merge_or_split_subjects","import_or_export_boundary","qualify_provider_offer","adjudicate_disputed_kind",
]


def archetype_rows() -> list[dict[str, Any]]:
    return [{"record_kind":"semantic_object_bearer_archetype","archetype_id":f"archetype.semantic-object.{n}.v1","meaning":m,"applicability":"UNRESOLVED_PER_SUBJECT_AND_USE_SITE","completion_claim":False} for n,m in ARCHETYPES]


def kernel_rows() -> list[dict[str, Any]]:
    return [{"record_kind":"semantic_object_operation_kernel","kernel_id":f"kernel.semantic-object.{n.replace('_','-')}.v1","operation":n,"required_input":"EXACT_SUBJECT_KIND_AND_CONTEXT","required_output":"TYPED_OUTCOME_WITH_PROVENANCE_AND_RESIDUALS","effect_classification":"MUST_BE_DECLARED_PER_BINDING","completion_claim":False} for n in KERNELS]


ONTOLOGY = {
    "ontology_id":"ontology.semantic-axis.semantic-object-coordinate.v1","edition":1,"as_of":AS_OF,"axis":"semantic_object",
    "domain_question":"What exact kind of thing is governed at this position, in which bounded context and metalevel, with what identity, lifecycle, assertion, authority, representation and effect semantics?",
    "coordinate_key":["bounded_context_ref","semantic_owner_ref","subject_ref","subject_kind_ref","metalevel_ref","edition_ref","use_site_ref"],
    "required_coordinate_fields":[
        "referent_domain_and_boundary","intrinsic_kind_versus_contextual_role","type_instance_occurrence_and_metalevel",
        "identity_equality_and_reference_profile","lifecycle_mutability_and_continuity","asserted_observed_requested_derived_or_represented_mode",
        "authority_responsibility_and_provenance","time_state_and_history_profile","grain_cardinality_and_container_laws",
        "relation_endpoints_direction_and_qualification","representation_schema_carrier_and_loss","open_closed_world_and_existence_assumptions",
        "partiality_dispute_and_unknown_kind","command_execution_effect_and_acceptance_seams","policy_privacy_security_and_safety_scope",
        "composition_split_merge_and_precedence","compatibility_migration_and_versioning","evidence_invalidators_and_conformance_oracles",
    ],
    "non_collapse_laws":[
        "referent_is_not_identifier_or_representation","type_is_not_instance_and_instance_is_not_occurrence",
        "entity_is_not_record_row_document_or_snapshot","event_is_not_command_observation_or_state",
        "fact_is_not_claim_and_claim_is_not_evidence_or_truth","intent_is_not_plan_attempt_effect_or_accepted_outcome",
        "rule_is_not_policy_decision_or_enforcement","state_is_not_history_snapshot_or_status_carrier",
        "resource_is_not_capability_entitlement_allocation_or_usage","schema_conformance_is_not_domain_truth",
        "proof_or_signature_is_not_identity_authority_truth_or_fitness","one_subject_may_have_multiple_explicit_roles_without_global_punning",
    ],
    "compiler_refusals":["REFUSE_UNBOUND_SUBJECT_KIND","REFUSE_CONTEXT_OR_METALEVEL_PUNNING","REFUSE_REFERENT_REPRESENTATION_COLLAPSE","REFUSE_COMMAND_EVENT_EFFECT_COLLAPSE","REFUSE_CLAIM_EVIDENCE_TRUTH_COLLAPSE","REFUSE_RESOURCE_CAPABILITY_AUTHORITY_COLLAPSE","REFUSE_MISSING_OWNER_EVIDENCE_OR_CONFORMANCE"],
    "status":"STRUCTURAL_COORDINATE_ONTOLOGY_DECISIONS_OPEN","completion_claim":False,
}


def structural_dockets() -> list[dict[str, Any]]:
    by_family: dict[str,list[str]] = defaultdict(list)
    for row in load_jsonl(PRECLASSIFICATIONS):
        if row["axis"] == "semantic_object": by_family[row["family_id"]].append(row["library_ref"])
    return [{"record_kind":"semantic_object_structural_rebase_docket","docket_id":f"docket.semantic-object-coordinate.{f.removeprefix('constitution.family.').replace('_','-')}.v1","family_ref":f,"library_refs":sorted(rs),"library_count":len(rs),"evidence_candidate_refs":[],"source_evidence_binding":"UNRESOLVED_PER_FAMILY_AND_USE_SITE","authority_limit":"Mechanical semantic-object preclassification supplies membership and lexical discovery only."} for f,rs in sorted(by_family.items())]


def route(facets: tuple[str,...]) -> str:
    return "LEXICAL_DISCOVERY_PROJECTION_ONLY_SUBJECT_RESEARCH_REQUIRED" if facets else "NO_MEMBER_SUBJECT_KIND_EVIDENCE_VACANCY"


def build() -> dict[str, Any]:
    dockets = structural_dockets()
    rebase = build_member_rebase(axis="semantic_object",dockets=dockets,preclassifications_path=PRECLASSIFICATIONS,cluster_prefix="cluster.semantic-object-coordinate-rebase",cluster_route=route)
    clusters=[{"record_kind":"semantic_object_member_research_cluster",**r,"required_next_evidence":["authoritative bounded-context subject and metalevel inventory","identity lifecycle role assertion and provenance contract","state time grain relation representation and effect coordinates","owner counterexamples negative twins and conformance oracles"],"family_source_evidence_binding":"UNRESOLVED","member_applicability":"UNRESOLVED","owner_decision":"UNRESOLVED","canonical_gaps_closed":0,"completion_claim":False} for r in rebase["clusters"]]
    members=[{"record_kind":"semantic_object_member_research_route","route_id":f"route.semantic-object-coordinate.{r['library_ref'].removeprefix('library.').replace('.','-').replace('_','-')}",**r,"flat_projection_effect":"DISCOVERY_ROUTING_ONLY_NOT_APPLICABILITY","required_subject_kind_and_metalevel_inventory":"NOT_YET_SUPPLIED","required_identity_lifecycle_role_and_assertion_profile":"NOT_YET_SUPPLIED","required_representation_effect_authority_and_conformance_contracts":"NOT_YET_SUPPLIED","family_source_evidence_binding":"UNRESOLVED","member_applicability":"UNRESOLVED","owner_decision":"UNRESOLVED","canonical_gaps_closed":0,"status":"LOSSLESSLY_ROUTED_RESEARCH_OPEN","completion_claim":False} for r in rebase["members"]]
    extensions=[{"record_kind":"semantic_object_exact_contract_extension_candidate","extension_id":f"extension.semantic-object-coordinate.{f.removeprefix('constitution.family.').replace('_','-')}.v1","family_ref":f,"structural_rebase_docket_ref":d["docket_id"],"represented_library_refs":d["library_refs"],"represented_library_count":d["library_count"],"required_record_kinds":["subject_kind_inventory","metalevel_and_role_profile","identity_lifecycle_assertion_contract","representation_and_effect_seam","authority_evidence_and_conformance_oracle"],"source_evidence_binding":"UNRESOLVED","owner_decision":"UNRESOLVED","member_applicability_decisions":0,"canonical_gaps_closed":0,"status":"CANDIDATE_UNRATIFIED","completion_claim":False} for f,d in sorted(rebase["docket_by_family"].items())]
    summary={"program_id":"program.semantic-object-coordinate-ontology-and-rebase.v1","as_of":AS_OF,"axis":"semantic_object","primary_sources":len(PRIMARY_SOURCES),"semantic_object_bearer_archetypes":len(ARCHETYPES),"semantic_object_operation_kernels":len(KERNELS),"structural_family_dockets":len(dockets),"family_extension_candidates":len(extensions),"research_clusters":len(clusters),"target_member_routes":len(members),"routes_with_lexical_discovery_projection":rebase["lexical_member_count"],"routes_with_no_member_subject_kind_evidence":rebase["vacancy_member_count"],"subject_kind_inventories_supplied":0,"semantic_object_coordinate_profiles_supplied":0,"family_source_evidence_bindings_supplied":0,"member_applicability_decisions":0,"owner_decisions":0,"canonical_gaps_closed":0,"completion_claim":False}
    return {"ontology":ONTOLOGY,"sources":PRIMARY_SOURCES,"archetypes":archetype_rows(),"kernels":kernel_rows(),"dockets":dockets,"clusters":clusters,"members":members,"extensions":extensions,"summary":summary}


def outputs() -> dict[str,str]:
    b=build(); files={"semantic-object-coordinate-ontology.json":json.dumps(b["ontology"],ensure_ascii=False,sort_keys=True,indent=2)+"\n","primary-sources.jsonl":"".join(canonical(r)+"\n" for r in b["sources"]),"semantic-object-bearer-archetypes.jsonl":"".join(canonical(r)+"\n" for r in b["archetypes"]),"semantic-object-operation-kernels.jsonl":"".join(canonical(r)+"\n" for r in b["kernels"]),"structural-family-dockets.jsonl":"".join(canonical(r)+"\n" for r in b["dockets"]),"member-research-clusters.jsonl":"".join(canonical(r)+"\n" for r in b["clusters"]),"member-semantic-object-routes.jsonl":"".join(canonical(r)+"\n" for r in b["members"]),"extension-candidates.jsonl":"".join(canonical(r)+"\n" for r in b["extensions"]),"summary.json":json.dumps(b["summary"],ensure_ascii=False,sort_keys=True,indent=2)+"\n"}
    claims={n:{"bytes":len(t.encode()),"sha256":hashlib.sha256(t.encode()).hexdigest()} for n,t in files.items()}
    files["manifest.json"]=json.dumps({"manifest_id":"manifest.semantic-object-coordinate-ontology-and-rebase.v1","as_of":AS_OF,"files":claims,"completion_claim":False},sort_keys=True,indent=2)+"\n"
    return files


def main() -> int:
    for n,t in outputs().items(): (HERE/n).write_text(t)
    s=build()["summary"]
    print(f"BUILD PASS semantic-object coordinate ontology: {s['semantic_object_bearer_archetypes']} bearers, {s['semantic_object_operation_kernels']} kernels, {s['research_clusters']} clusters and {s['target_member_routes']} exact routes; decisions remain zero")
    return 0


if __name__ == "__main__": raise SystemExit(main())
