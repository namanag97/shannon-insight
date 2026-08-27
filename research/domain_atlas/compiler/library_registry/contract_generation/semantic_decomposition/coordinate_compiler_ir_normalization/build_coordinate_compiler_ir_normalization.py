#!/usr/bin/env python3
"""Normalize axis-native coordinate ontologies into a common structural compiler-IR surface."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from typing import Any
HERE=Path(__file__).resolve().parent;SEM=HERE.parent;AS_OF="2026-08-27"

PACKAGES={
 "semantic_object":"semantic_object_coordinate_ontology","semantic_role":"semantic_role_coordinate_ontology","identity_and_equality":"p3i_identity_equality_coordinate_ontology","grain_and_cardinality":"p3e_grain_coordinate_ontology","state_and_change":"p3s_state_change_coordinate_ontology","time":"time_coordinate_ontology","order_and_topology":"p3o_order_topology_coordinate_ontology","partiality_and_uncertainty":"p3u_partiality_uncertainty_coordinate_ontology","authority_and_trust":"authority_trust_coordinate_ontology","effect_boundary":"effect_boundary_coordinate_ontology","representation":"representation_coordinate_ontology","composition_algebra":"p3c_composition_algebra_coordinate_ontology","compatibility_and_evolution":"compatibility_evolution_coordinate_ontology","resources_and_failure":"resources_failure_coordinate_ontology","evidence_and_conformance":"evidence_conformance_coordinate_ontology","privacy_security_safety":"privacy_security_safety_coordinate_ontology",
}

NORMALIZATION={
 "semantic_object":{
  "outcomes":["classified","classified_with_qualification","qualified_homonym","metalevel_ambiguous","boundary_ambiguous","outside_bounded_context","unsupported","indeterminate","refused"],
  "refusals":["REFUSE_UNBOUND_SUBJECT_KIND_OR_BOUNDED_CONTEXT","REFUSE_TYPE_INSTANCE_OCCURRENCE_COLLAPSE","REFUSE_REFERENT_IDENTIFIER_REPRESENTATION_COLLAPSE","REFUSE_EVENT_COMMAND_EFFECT_OR_CLAIM_EVIDENCE_TRUTH_COLLAPSE"]},
 "semantic_role":{
  "outcomes":["role_bound","role_bound_with_qualification","multi_role_profile","direction_ambiguous","counterparty_ambiguous","ownership_conflict","authority_conflict","outside_contract","unsupported","refused"],
  "refusals":["REFUSE_LIBRARY_WIDE_ROLE_DEFAULT","REFUSE_PORT_ADAPTER_PROVIDER_RUNTIME_COLLAPSE","REFUSE_PLANNER_AS_EXECUTOR","REFUSE_IMPLEMENTATION_PROVIDER_AS_SEMANTIC_OWNER","REFUSE_ROLE_WITHOUT_OPERATION_DIRECTION_COUNTERPARTY_AND_USE_SITE"]},
 "identity_and_equality":{
  "outcomes":["same_occurrence","same_identifier_under_scope","equal_carrier","equal_value","structurally_equal","canonical_representation_equal","digest_equal_only","semantically_equivalent","behaviorally_equivalent","approximately_equal","isomorphic","match_candidate","merge_authorized","distinct","indeterminate","refused"],
  "refusals":["REFUSE_NAME_OR_KEY_AS_IDENTITY","REFUSE_EQUAL_BYTES_OR_DIGEST_AS_SEMANTIC_EQUALITY","REFUSE_SIMILARITY_AS_ENTITY_MERGE","REFUSE_ALIAS_AS_IDENTITY_CONTINUITY","REFUSE_EQUALITY_WITHOUT_RELATION_LAWS_SCOPE_AND_LIFECYCLE"]},
 "grain_and_cardinality":{
  "outcomes":["grain_preserved","filtered_subset","expanded","reduced","aggregated","regrouped","rekeyed","windowed","sampled","partial_collection","unbounded_collection","cardinality_mismatch","completeness_unknown","refused"],
  "refusals":["REFUSE_LIBRARY_WIDE_GRAIN_DEFAULT","REFUSE_ELEMENT_CONTAINER_COLLECTION_COLLAPSE","REFUSE_UNDECLARED_GRAIN_CHANGE","REFUSE_LOCAL_COMPLETENESS_AS_GLOBAL_COMPLETENESS","REFUSE_UNBOUNDED_CARDINALITY_WITHOUT_RESOURCE_PROFILE"]},
 "state_and_change":{
  "outcomes":["created","transitioned","unchanged","patched","reconciled","superseded","revoked","cancel_requested","cancelled","completed","terminal","invalid_transition","version_conflict","partially_applied","unknown_completion","refused"],
  "refusals":["REFUSE_GENERIC_STATUS_WITHOUT_STATE_SUBJECT","REFUSE_COMMAND_OR_OBSERVATION_AS_TRANSITION","REFUSE_DESIRED_AS_OBSERVED_OR_ACCEPTED_STATE","REFUSE_CANCELLATION_AS_ROLLBACK_OR_COMPENSATION","REFUSE_TERMINALITY_OR_REVERSIBILITY_WITHOUT_LIFECYCLE_LAW"]},
 "time":{
  "outcomes":["represented_exactly","converted_exactly","rounded_with_residual","ambiguous_local_time","nonexistent_local_time","uncertain_instant_or_interval","before","after","overlaps","concurrent_or_incomparable","late","expired","watermark_advanced","finality_unknown","indeterminate","refused"],
  "refusals":["REFUSE_UNTYPED_TIMESTAMP","REFUSE_OFFSET_AS_TIME_ZONE","REFUSE_ELAPSED_DURATION_AS_CALENDAR_PERIOD","REFUSE_EVENT_RECORDING_PROCESSING_DECISION_TIME_COLLAPSE","REFUSE_WATERMARK_AS_COMPLETENESS_OR_FINALITY","REFUSE_TIME_CONVERSION_WITHOUT_SCALE_CALENDAR_ZONE_PRECISION_AND_UNCERTAINTY"]},
 "order_and_topology":{
  "outcomes":["ordered","partially_ordered","preordered","concurrent","incomparable","cycle_detected","path_found","path_absent","connected","disconnected","topologically_related","linearization_produced","ranked_with_ties","ambiguous_relation","refused"],
  "refusals":["REFUSE_SERIALIZATION_OR_ARRIVAL_AS_SEMANTIC_ORDER","REFUSE_TOTAL_ORDER_WHERE_RELATION_IS_PARTIAL","REFUSE_DEPENDENCY_AS_CAUSALITY","REFUSE_HIERARCHY_PARTONOMY_TAXONOMY_OR_GRAPH_COLLAPSE","REFUSE_LINEARIZATION_WITHOUT_TIE_AND_INFORMATION_LOSS_PROFILE"]},
 "partiality_and_uncertainty":{
  "outcomes":["present","absent","present_null","unknown","invalid","stale","pending","withheld","censored","partial","approximate","interval","distribution","quantile_or_sample_path","imputed","interpolated","extrapolated","infeasible","solver_unknown","indeterminate","refused"],
  "refusals":["REFUSE_OPTION_OR_NULL_AS_UNIVERSAL_INFORMATION_STATE","REFUSE_UNKNOWN_AS_FALSE_ZERO_EMPTY_OR_INFEASIBLE","REFUSE_POINT_ESTIMATE_AS_DISTRIBUTION","REFUSE_CONFIDENCE_SCORE_WITHOUT_POPULATION_CALIBRATION_AND_LOSS","REFUSE_IMPUTED_INTERPOLATED_OR_EXTRAPOLATED_AS_OBSERVED"]},
 "composition_algebra":{
  "outcomes":["composed","composed_with_residual","conflict","non_convergent","law_unproved","type_mismatch","order_unsafe","effect_unsafe","unsupported","refused"],
  "refusals":["REFUSE_SYNTACTIC_NESTING_AS_SEMANTIC_COMPOSITION","REFUSE_UNPROVED_ASSOCIATIVITY_COMMUTATIVITY_OR_IDEMPOTENCE","REFUSE_MERGE_JOIN_UNION_OVERLAY_OVERRIDE_OR_RECONCILIATION_COLLAPSE","REFUSE_EFFECTFUL_REORDERING_WITHOUT_INDEPENDENCE_AND_RESOURCE_PROOF","REFUSE_LOSSY_COMPOSITION_WITHOUT_RESIDUAL"]},
}

COMMON_IR={"ir_contract_id":"contract.compiler.semantic-coordinate-normalization.v1","required_roles":["AxisRef","BearerArchetypeRef","BearerCoordinate","BoundedContextRef","CoordinateProfileRef","UseSiteRef","TypedOutcomeEnumRef","RefusalSetRef","RefusalPrecedenceRef","EvidenceRequirementSetRef","ResidualRef","OwnerDecisionRef"],"propagation_rule":"A normalized profile may propagate only when bearer coordinates, preconditions, semantic dependencies, authority, effects, resources, evidence and acceptance context match exactly.","lowering_rule":"Normalization makes heterogeneous axes inspectable by one compiler. It does not decide coordinates, applicability, ownership, exact contracts, implementation selection or acceptance.","completion_claim":False}

def load_json(p:Path)->Any:return json.loads(p.read_text())
def canonical(v:Any)->str:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def ontology_path(package:str)->Path:return next((SEM/package).glob("*coordinate-ontology.json"))
def native_coordinates(o:dict[str,Any])->dict[str,Any]:return {k:o[k] for k in ("required_coordinate_fields","coordinate_key","coordinate_contract","identity_coordinate","state_coordinate","time_coordinate","relation_coordinate","operator_coordinate","uncertainty_coordinate") if k in o}

def build()->dict[str,Any]:
 profiles=[]
 for axis,package in sorted(PACKAGES.items()):
  p=ontology_path(package);o=load_json(p);override=NORMALIZATION.get(axis,{})
  fields=o.get("required_coordinate_fields") or native_coordinates(o)
  outcomes=o.get("required_outcomes") or override["outcomes"]
  refusals=o.get("compiler_refusals") or override["refusals"]
  profiles.append({"record_kind":"normalized_axis_compiler_ir_profile","profile_id":f"profile.compiler-ir.semantic-axis.{axis.replace('_','-')}.v1","axis":axis,"source_coordinate_package_ref":package,"source_ontology_ref":str(p.relative_to(SEM)),"normalization_origin":"NATIVE_COMMON_SURFACE" if axis not in NORMALIZATION else "LOSS_PRESERVING_AXIS_NATIVE_PROJECTION","common_ir_contract_ref":COMMON_IR["ir_contract_id"],"bearer_archetype_refs":"RESOLVE_FROM_DECISION_LOCUS_PROFILE","required_coordinate_surface":fields,"typed_total_outcomes":outcomes,"compiler_refusals":refusals,"refusal_precedence":"AXIS_OWNER_MUST_SUPPLY_EXACT_PRECEDENCE_PER_PROFILE","evidence_requirements":["bounded primary evidence for coordinate answers","owner applicability and exception receipt","negative twins for non-collapse laws","exact contract and conformance oracle"],"residual_channel":"REQUIRED_FOR_PARTIAL_LOSSY_AMBIGUOUS_UNKNOWN_OR_UNSUPPORTED_OUTCOME","member_coordinate_answers":0,"member_applicability_decisions":0,"owner_decisions":0,"compiler_lowering_ready":False,"status":"STRUCTURAL_NORMALIZATION_DECISIONS_OPEN","completion_claim":False})
 summary={"program_id":"program.coordinate-compiler-ir-normalization.v1","as_of":AS_OF,"semantic_axes":len(profiles),"native_common_surface_axes":sum(r["normalization_origin"]=="NATIVE_COMMON_SURFACE" for r in profiles),"axis_native_projection_axes":sum(r["normalization_origin"]=="LOSS_PRESERVING_AXIS_NATIVE_PROJECTION" for r in profiles),"normalized_coordinate_surfaces":sum(bool(r["required_coordinate_surface"]) for r in profiles),"normalized_total_outcome_surfaces":sum(bool(r["typed_total_outcomes"]) for r in profiles),"normalized_refusal_surfaces":sum(bool(r["compiler_refusals"]) for r in profiles),"refusal_precedence_profiles_supplied":0,"member_coordinate_answers":0,"member_applicability_decisions":0,"owner_decisions":0,"compiler_lowering_ready_axes":0,"canonical_gaps_closed":0,"completion_claim":False}
 return {"contract":COMMON_IR,"profiles":profiles,"summary":summary}
def outputs()->dict[str,str]:
 b=build();files={"common-compiler-ir-contract.json":json.dumps(b["contract"],ensure_ascii=False,sort_keys=True,indent=2)+"\n","normalized-axis-profiles.jsonl":"".join(canonical(x)+"\n" for x in b["profiles"]),"summary.json":json.dumps(b["summary"],ensure_ascii=False,sort_keys=True,indent=2)+"\n"};claims={n:{"bytes":len(t.encode()),"sha256":hashlib.sha256(t.encode()).hexdigest()} for n,t in files.items()};files["manifest.json"]=json.dumps({"manifest_id":"manifest.coordinate-compiler-ir-normalization.v1","as_of":AS_OF,"files":claims,"completion_claim":False},sort_keys=True,indent=2)+"\n";return files
def main():
 for n,t in outputs().items():(HERE/n).write_text(t)
 s=build()["summary"];print(f"BUILD PASS coordinate compiler-IR normalization: {s['semantic_axes']} axes expose common coordinate/outcome/refusal surfaces; {s['axis_native_projection_axes']} require loss-preserving projections and all decisions remain open");return 0
if __name__=="__main__":raise SystemExit(main())
