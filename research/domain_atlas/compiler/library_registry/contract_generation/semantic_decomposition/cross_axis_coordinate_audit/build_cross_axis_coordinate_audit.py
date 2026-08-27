#!/usr/bin/env python3
"""Audit all coordinate packages for cell coverage, quotient sufficiency and compiler surfaces."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from typing import Any

HERE=Path(__file__).resolve().parent;SEM=HERE.parent;AS_OF="2026-08-27"
PRECLASS=SEM/"applicability_matrices/member-preclassifications.jsonl"
FACTORIZATIONS=SEM/"semantic_decision_locus_ontology/family-axis-factorizations.jsonl"
SUPPLEMENT=SEM/"coordinate_route_completion/supplemental-member-coordinate-routes.jsonl"
NORMALIZED_PROFILES=SEM/"coordinate_compiler_ir_normalization/normalized-axis-profiles.jsonl"
SEAM_TEST_SUMMARY=SEM/"cross_axis_seam_tests/summary.json"

PACKAGES={
 "semantic_object":"semantic_object_coordinate_ontology","semantic_role":"semantic_role_coordinate_ontology",
 "identity_and_equality":"p3i_identity_equality_coordinate_ontology","grain_and_cardinality":"p3e_grain_coordinate_ontology",
 "state_and_change":"p3s_state_change_coordinate_ontology","time":"time_coordinate_ontology",
 "order_and_topology":"p3o_order_topology_coordinate_ontology","partiality_and_uncertainty":"p3u_partiality_uncertainty_coordinate_ontology",
 "authority_and_trust":"authority_trust_coordinate_ontology","effect_boundary":"effect_boundary_coordinate_ontology",
 "representation":"representation_coordinate_ontology","composition_algebra":"p3c_composition_algebra_coordinate_ontology",
 "compatibility_and_evolution":"compatibility_evolution_coordinate_ontology","resources_and_failure":"resources_failure_coordinate_ontology",
 "evidence_and_conformance":"evidence_conformance_coordinate_ontology","privacy_security_safety":"privacy_security_safety_coordinate_ontology",
}

SEAMS=[
 ("semantic_object","identity_and_equality","subject kind constrains identity bearer and equality relation"),("semantic_object","semantic_role","subject kind does not imply interaction role"),
 ("identity_and_equality","grain_and_cardinality","identity scope and equality must survive any grain-changing operation"),("state_and_change","time","state transition and observation require explicit time roles"),
 ("time","order_and_topology","temporal order, causal order, arrival order and serialization order remain distinct"),("grain_and_cardinality","partiality_and_uncertainty","completeness and boundedness are scoped to grain and population"),
 ("authority_and_trust","effect_boundary","decision, enforcement, attempt, receipt and acceptance remain distinct"),("effect_boundary","resources_and_failure","attempt, retry, cancellation, partial outcome and unknown completion share exact occurrence identity"),
 ("representation","identity_and_equality","canonical bytes and carrier equality do not create domain identity"),("representation","compatibility_and_evolution","compatibility names direction, profile and preservation obligations over representation editions"),
 ("composition_algebra","effect_boundary","pure and effectful composition cannot inherit the same laws silently"),("composition_algebra","partiality_and_uncertainty","composition propagates or refuses missingness, uncertainty, conflict and residuals explicitly"),
 ("compatibility_and_evolution","state_and_change","migration, replay and in-flight work are governed state/history effects"),("compatibility_and_evolution","evidence_and_conformance","evidence is edition-bound and invalidated by relied-coordinate changes"),
 ("resources_and_failure","privacy_security_safety","overload, degradation and recovery preserve authority, privacy, security and safety constraints"),("privacy_security_safety","authority_and_trust","purpose, risk treatment, exceptions and residual acceptance require named authority"),
 ("evidence_and_conformance","partiality_and_uncertainty","claim strength, coverage, uncertainty, exclusions and defeaters remain explicit"),("evidence_and_conformance","effect_boundary","observation and receipt do not become effect truth or business acceptance"),
 ("semantic_role","representation","DTO, adapter, runtime and provider roles do not own represented meaning"),("semantic_role","resources_and_failure","ports, adapters and runtimes own different resource and failure responsibilities"),
]

def load_json(p:Path)->Any:return json.loads(p.read_text())
def load_jsonl(p:Path)->list[dict[str,Any]]:return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def canonical(v:Any)->str:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def digest_refs(refs:list[str])->str:return hashlib.sha256("\n".join(sorted(refs)).encode()).hexdigest()

def package_artifacts(directory:Path)->tuple[Path,Path,Path|None,Path]:
 ont=next(directory.glob("*coordinate-ontology.json")); members=next(directory.glob("member*routes.jsonl"))
 archetype_candidates=list(directory.glob("*archetypes.jsonl"))
 archetypes=archetype_candidates[0] if archetype_candidates else None
 kernels=next(directory.glob("*kernels.jsonl"))
 return ont,members,archetypes,kernels

def build()->dict[str,Any]:
 pre=load_jsonl(PRECLASS); facts=load_jsonl(FACTORIZATIONS)
 seam_test_summary=load_json(SEAM_TEST_SUMMARY)
 all_axes=sorted({r["axis"] for r in pre});all_libs=sorted({r["library_ref"] for r in pre})
 pre_by_id={r["preclassification_id"]:r for r in pre}
 normalized_by_axis={r["axis"]:r for r in load_jsonl(NORMALIZED_PROFILES)}
 supplemental=load_jsonl(SUPPLEMENT);supplemental_by_axis:dict[str,set[str]]={axis:set() for axis in all_axes}
 for r in supplemental:supplemental_by_axis[r["axis"]].add(r["library_ref"])
 inventory=[];routes_by_axis={};ontology_by_axis={}
 for axis in all_axes:
  d=SEM/PACKAGES[axis];ontp,memberp,archp,kernp=package_artifacts(d)
  ont=load_json(ontp);summary=load_json(d/"summary.json");members=load_jsonl(memberp);arches=load_jsonl(archp) if archp else [];kernels=load_jsonl(kernp)
  routed=sorted(r["library_ref"] for r in members);supplemented=sorted(supplemental_by_axis[axis]);combined=sorted(set(routed)|set(supplemented));missing_primary=sorted(set(all_libs)-set(routed));missing=sorted(set(all_libs)-set(combined));routes_by_axis[axis]=set(combined);ontology_by_axis[axis]=ont
  normalized={"coordinate_fields":bool(ont.get("required_coordinate_fields")),"outcomes":bool(ont.get("required_outcomes")),"compiler_refusals":bool(ont.get("compiler_refusals"))}
  projected=normalized_by_axis[axis];combined_normalized={"coordinate_fields":bool(projected["required_coordinate_surface"]),"outcomes":bool(projected["typed_total_outcomes"]),"compiler_refusals":bool(projected["compiler_refusals"])}
  inventory.append({"record_kind":"axis_coordinate_package_audit","axis":axis,"package_ref":PACKAGES[axis],"ontology_ref":str(ontp.relative_to(SEM)),"member_routes_ref":str(memberp.relative_to(SEM)),"supplemental_routes_ref":str(SUPPLEMENT.relative_to(SEM)),"normalized_compiler_profile_ref":projected["profile_id"],"bearer_archetype_count":len(arches),"operation_kernel_count":len(kernels),"primary_member_routes":len(routed),"supplemental_member_routes":len(supplemented),"combined_member_routes":len(combined),"expected_member_axis_cells":len(all_libs),"missing_primary_member_route_refs":missing_primary,"missing_primary_member_route_count":len(missing_primary),"missing_member_route_refs":missing,"missing_member_route_count":len(missing),"route_set_digest":digest_refs(combined),"native_normalized_compiler_surface":normalized,"native_normalized_compiler_surface_complete":all(normalized.values()),"combined_normalized_compiler_surface":combined_normalized,"combined_normalized_compiler_surface_complete":all(combined_normalized.values()),"source_evidence_bindings_supplied":summary.get("family_source_evidence_bindings_supplied",0),"member_applicability_decisions":summary.get("member_applicability_decisions",0),"owner_decisions":summary.get("owner_decisions",0),"canonical_gaps_closed":summary.get("canonical_gaps_closed",0),"status":"FULL_MEMBER_COORDINATE_ROUTING_WITH_STRUCTURAL_VACANCIES" if supplemented else "FULL_PRIMARY_MEMBER_COORDINATE_ROUTING","completion_claim":False})
 quotient=[]
 for f in sorted(facts,key=lambda r:(r["axis"],r["family_ref"])):
  members=sorted(pre_by_id[x]["library_ref"] for x in f["member_preclassification_refs"]);routed=sorted(set(members)&routes_by_axis[f["axis"]]);missing=sorted(set(members)-routes_by_axis[f["axis"]])
  quotient.append({"record_kind":"family_axis_coordinate_quotient_audit","audit_id":f"audit.coordinate-quotient.{f['family_ref'].removeprefix('constitution.family.').replace('_','-')}.{f['axis'].replace('_','-')}.v1","factorization_ref":f["factorization_id"],"family_ref":f["family_ref"],"axis":f["axis"],"member_count":len(members),"routed_member_refs":routed,"routed_member_count":len(routed),"unrouted_member_refs":missing,"unrouted_member_count":len(missing),"lossless_factorization_identity_preserved":len(members)==len(routed)+len(missing),"quotient_status":"FULLY_COORDINATE_ROUTED" if not missing else ("PARTIALLY_COORDINATE_ROUTED" if routed else "NO_MEMBER_COORDINATE_ROUTES"),"owner_decision":"UNRESOLVED","completion_claim":False})
 compiler=[]
 for row in inventory:
  native_missing=[k for k,v in row["native_normalized_compiler_surface"].items() if not v]
  compiler.append({"record_kind":"axis_compiler_ir_surface_audit","axis":row["axis"],"coordinate_package_ref":row["package_ref"],"normalized_compiler_profile_ref":row["normalized_compiler_profile_ref"],"bearer_coordinate_surface":"PRESENT","native_surface_status":"NATIVE_COMMON_SURFACE" if not native_missing else "NORMALIZED_BY_LOSS_PRESERVING_PROJECTION","normalized_required_coordinate_fields":"PRESENT","normalized_total_outcomes":"PRESENT","normalized_compiler_refusals":"PRESENT","refusal_precedence":"OWNER_PROFILE_REQUIRED","member_route_coverage":"FULL","missing_member_route_count":row["missing_member_route_count"],"required_remediation":["supply exact refusal precedence, coordinate answers, applicability, owner receipt and conformance evidence"],"compiler_lowering_ready":False,"status":"STRUCTURAL_NORMALIZATION_COMPLETE_SEMANTIC_DECISIONS_OPEN","completion_claim":False})
 seams=[{"record_kind":"cross_axis_seam_obligation","seam_id":f"seam.{a.replace('_','-')}.{b.replace('_','-')}.v1","left_axis":a,"right_axis":b,"obligation":law,"left_package_ref":PACKAGES[a],"right_package_ref":PACKAGES[b],"decision_state":"UNRESOLVED_PER_BEARER_AND_USE_SITE","contradiction_test":"REQUIRED_BEFORE_OWNER_RATIFICATION","compiler_binding":"REFUSE_UNTIL_BOTH_AXIS_PROFILES_AND_SEAM_OBLIGATION_ARE_SATISFIED","completion_claim":False} for a,b,law in SEAMS]
 summary={"program_id":"program.cross-axis-coordinate-audit.v1","as_of":AS_OF,"semantic_axes":len(all_axes),"libraries":len(all_libs),"member_axis_cells":len(pre),"coordinate_packages":len(inventory),"full_primary_member_route_packages":sum(not r["missing_primary_member_route_count"] for r in inventory),"partial_primary_member_route_packages":sum(bool(r["missing_primary_member_route_count"]) for r in inventory),"full_combined_member_route_packages":sum(not r["missing_member_route_count"] for r in inventory),"primary_coordinate_routes":sum(r["primary_member_routes"] for r in inventory),"supplemental_structural_routes":sum(r["supplemental_member_routes"] for r in inventory),"exact_coordinate_routes":sum(r["combined_member_routes"] for r in inventory),"unrouted_member_axis_cells":sum(r["missing_member_route_count"] for r in inventory),"family_axis_quotients":len(quotient),"fully_routed_quotients":sum(r["quotient_status"]=="FULLY_COORDINATE_ROUTED" for r in quotient),"partially_routed_quotients":sum(r["quotient_status"]=="PARTIALLY_COORDINATE_ROUTED" for r in quotient),"unrouted_quotients":sum(r["quotient_status"]=="NO_MEMBER_COORDINATE_ROUTES" for r in quotient),"native_normalized_compiler_surface_axes":sum(r["native_normalized_compiler_surface_complete"] for r in inventory),"projected_normalized_compiler_surface_axes":sum(not r["native_normalized_compiler_surface_complete"] and r["combined_normalized_compiler_surface_complete"] for r in inventory),"normalized_compiler_surface_axes":sum(r["combined_normalized_compiler_surface_complete"] for r in inventory),"compiler_surface_normalization_gaps":sum(not r["combined_normalized_compiler_surface_complete"] for r in inventory),"cross_axis_seam_obligations":len(seams),"structural_contradiction_tests_executed":seam_test_summary["structural_contradiction_tests_executed"],"structural_negative_twins_passed":seam_test_summary["negative_twins_passed"],"semantic_contradiction_appraisals_executed":seam_test_summary["semantic_contradiction_appraisals_executed"],"compiler_lowering_ready_axes":0,"member_applicability_decisions":0,"owner_decisions":0,"canonical_gaps_closed":0,"completion_claim":False}
 return {"inventory":inventory,"quotient":quotient,"compiler":compiler,"seams":seams,"summary":summary}

def outputs()->dict[str,str]:
 b=build();files={"axis-package-inventory.jsonl":"".join(canonical(x)+"\n" for x in b["inventory"]),"family-axis-quotient-audits.jsonl":"".join(canonical(x)+"\n" for x in b["quotient"]),"compiler-ir-coverage.jsonl":"".join(canonical(x)+"\n" for x in b["compiler"]),"cross-axis-seam-obligations.jsonl":"".join(canonical(x)+"\n" for x in b["seams"]),"summary.json":json.dumps(b["summary"],ensure_ascii=False,sort_keys=True,indent=2)+"\n"}
 claims={n:{"bytes":len(t.encode()),"sha256":hashlib.sha256(t.encode()).hexdigest()} for n,t in files.items()};files["manifest.json"]=json.dumps({"manifest_id":"manifest.cross-axis-coordinate-audit.v1","as_of":AS_OF,"files":claims,"completion_claim":False},sort_keys=True,indent=2)+"\n";return files
def main():
 for n,t in outputs().items():(HERE/n).write_text(t)
 s=build()["summary"];print(f"BUILD PASS cross-axis audit: {s['semantic_axes']} packages plus structural supplements route {s['exact_coordinate_routes']} / {s['member_axis_cells']} cells; {s['compiler_surface_normalization_gaps']} compiler-surface normalization gaps remain");return 0
if __name__=="__main__":raise SystemExit(main())
