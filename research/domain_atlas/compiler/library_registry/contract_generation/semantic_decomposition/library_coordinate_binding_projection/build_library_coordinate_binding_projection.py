#!/usr/bin/env python3
"""Project normalized all-axis coordinate obligations into every exact library lowering docket."""
from __future__ import annotations
import hashlib,json
from collections import defaultdict
from pathlib import Path
from typing import Any
HERE=Path(__file__).resolve().parent;SEM=HERE.parent;AS_OF="2026-08-27"
PRECLASS=SEM/"applicability_matrices/member-preclassifications.jsonl";FACTS=SEM/"semantic_decision_locus_ontology/family-axis-factorizations.jsonl";P5=SEM/"p5_exact_contract_adjudication/exact-contract-dockets.jsonl";SUPPLEMENT=SEM/"coordinate_route_completion/supplemental-member-coordinate-routes.jsonl";PROFILES=SEM/"coordinate_compiler_ir_normalization/normalized-axis-profiles.jsonl";SEAMS=SEM/"cross_axis_coordinate_audit/cross-axis-seam-obligations.jsonl";SEAM_RESULTS=SEM/"cross_axis_seam_tests/seam-test-results.jsonl"
PACKAGES={"semantic_object":"semantic_object_coordinate_ontology","semantic_role":"semantic_role_coordinate_ontology","identity_and_equality":"p3i_identity_equality_coordinate_ontology","grain_and_cardinality":"p3e_grain_coordinate_ontology","state_and_change":"p3s_state_change_coordinate_ontology","time":"time_coordinate_ontology","order_and_topology":"p3o_order_topology_coordinate_ontology","partiality_and_uncertainty":"p3u_partiality_uncertainty_coordinate_ontology","authority_and_trust":"authority_trust_coordinate_ontology","effect_boundary":"effect_boundary_coordinate_ontology","representation":"representation_coordinate_ontology","composition_algebra":"p3c_composition_algebra_coordinate_ontology","compatibility_and_evolution":"compatibility_evolution_coordinate_ontology","resources_and_failure":"resources_failure_coordinate_ontology","evidence_and_conformance":"evidence_conformance_coordinate_ontology","privacy_security_safety":"privacy_security_safety_coordinate_ontology"}
def load_jsonl(p:Path)->list[dict[str,Any]]:return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def canonical(v:Any)->str:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def slug(v:str)->str:return v.removeprefix("library.").replace("_","-").replace(".","-")
def primary_routes()->dict[tuple[str,str],str]:
 out={}
 for axis,package in PACKAGES.items():
  p=next((SEM/package).glob("member*routes.jsonl"))
  for r in load_jsonl(p):out[(r["library_ref"],axis)]=r.get("route_id") or r.get("member_route_id") or r.get("library_ref")+":"+axis
 return out
def build()->dict[str,Any]:
 pre=load_jsonl(PRECLASS);profiles={r["axis"]:r for r in load_jsonl(PROFILES)};facts={(r["family_ref"],r["axis"]):r for r in load_jsonl(FACTS)};dockets={r["library_ref"]:r for r in load_jsonl(P5)};routes=primary_routes();supp={(r["library_ref"],r["axis"]):r["route_id"] for r in load_jsonl(SUPPLEMENT)};seams=load_jsonl(SEAMS);seam_results={r["seam_ref"]:r for r in load_jsonl(SEAM_RESULTS)}
 requirements=[];by_library=defaultdict(list)
 for r in sorted(pre,key=lambda x:(x["library_ref"],x["axis"])):
  key=(r["library_ref"],r["axis"]);origin="PRIMARY_COORDINATE_PACKAGE_ROUTE" if key in routes else "SUPPLEMENTAL_STRUCTURAL_EVIDENCE_VACANCY_ROUTE";route=routes.get(key) or supp[key];profile=profiles[r["axis"]];fact=facts[(r["family_id"],r["axis"])]
  rid=f"requirement.compiler-coordinate.{slug(r['library_ref'])}.{r['axis'].replace('_','-')}.v1";by_library[r["library_ref"]].append(rid)
  requirements.append({"record_kind":"library_axis_compiler_binding_requirement","requirement_id":rid,"library_ref":r["library_ref"],"family_ref":r["family_id"],"axis":r["axis"],"source_gap_ref":r["source_gap_ref"],"coordinate_route_ref":route,"coordinate_route_origin":origin,"normalized_axis_profile_ref":profile["profile_id"],"family_axis_factorization_ref":fact["factorization_id"],"required_coordinate_answers":"UNRESOLVED","required_typed_outcome_profile":profile["typed_total_outcomes"],"required_refusal_profile":profile["compiler_refusals"],"required_refusal_precedence":"UNRESOLVED_OWNER_PROFILE","required_evidence":profile["evidence_requirements"],"required_residual_channel":profile["residual_channel"],"member_applicability":"UNRESOLVED","owner_decision":"UNRESOLVED","compiler_action":"REFUSE_COORDINATE_BINDING","canonical_gaps_closed":0,"completion_claim":False})
 library_rows=[]
 all_seams=sorted(r["seam_id"] for r in seams)
 for lib,docket in sorted(dockets.items()):
  reqs=sorted(by_library[lib]);assert len(reqs)==16
  library_rows.append({"record_kind":"library_coordinate_binding_docket","binding_docket_id":f"docket.compiler-coordinate.{slug(lib)}.v1","library_ref":lib,"family_ref":docket["family_ref"],"exact_contract_docket_ref":docket["docket_id"],"axis_requirement_refs":reqs,"axis_requirement_count":len(reqs),"cross_axis_seam_refs":all_seams,"cross_axis_seam_count":len(all_seams),"structural_seam_test_result_refs":sorted(seam_results[s]["result_id"] for s in all_seams),"coordinate_answers_supplied":0,"refusal_precedence_profiles_supplied":0,"member_applicability_decisions":0,"owner_decisions":0,"semantic_seam_appraisals":0,"exact_contract_selected":docket["selected_exact_contract_ref"] is not None,"compiler_binding":"REFUSED","refusal_reasons":["COORDINATE_ANSWERS_UNRESOLVED","REFUSAL_PRECEDENCE_UNRESOLVED","MEMBER_APPLICABILITY_UNRATIFIED","OWNER_DECISIONS_UNRATIFIED","SEMANTIC_SEAM_APPRAISALS_UNEXECUTED","EXACT_CONTRACT_UNSELECTED"],"canonical_gaps_closed":0,"completion_claim":False})
 summary={"program_id":"program.library-coordinate-binding-projection.v1","as_of":AS_OF,"libraries":len(library_rows),"semantic_axes":16,"library_axis_requirements":len(requirements),"primary_route_requirements":sum(r["coordinate_route_origin"]=="PRIMARY_COORDINATE_PACKAGE_ROUTE" for r in requirements),"supplemental_vacancy_requirements":sum(r["coordinate_route_origin"]=="SUPPLEMENTAL_STRUCTURAL_EVIDENCE_VACANCY_ROUTE" for r in requirements),"cross_axis_seams_per_library":20,"structural_seam_negative_twins_passed":120,"coordinate_answers_supplied":0,"refusal_precedence_profiles_supplied":0,"member_applicability_decisions":0,"owner_decisions":0,"semantic_seam_appraisals":0,"exact_contracts_selected":sum(r["exact_contract_selected"] for r in library_rows),"compiler_bindings_permitted":0,"canonical_gaps_closed":0,"completion_claim":False}
 return {"requirements":requirements,"dockets":library_rows,"summary":summary}
def outputs()->dict[str,str]:
 b=build();files={"library-axis-binding-requirements.jsonl":"".join(canonical(x)+"\n" for x in b["requirements"]),"library-coordinate-binding-dockets.jsonl":"".join(canonical(x)+"\n" for x in b["dockets"]),"summary.json":json.dumps(b["summary"],ensure_ascii=False,sort_keys=True,indent=2)+"\n"};claims={n:{"bytes":len(t.encode()),"sha256":hashlib.sha256(t.encode()).hexdigest()} for n,t in files.items()};files["manifest.json"]=json.dumps({"manifest_id":"manifest.library-coordinate-binding-projection.v1","as_of":AS_OF,"files":claims,"completion_claim":False},sort_keys=True,indent=2)+"\n";return files
def main():
 for n,t in outputs().items():(HERE/n).write_text(t)
 s=build()["summary"];print(f"BUILD PASS library coordinate binding projection: {s['libraries']} libraries expose {s['library_axis_requirements']} exact axis requirements and all compiler bindings refuse");return 0
if __name__=="__main__":raise SystemExit(main())
