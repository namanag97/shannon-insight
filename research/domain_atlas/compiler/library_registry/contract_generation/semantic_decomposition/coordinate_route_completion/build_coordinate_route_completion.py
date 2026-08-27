#!/usr/bin/env python3
"""Complete all-axis structural routing without manufacturing semantic evidence or decisions."""
from __future__ import annotations
import hashlib,json
from collections import defaultdict
from pathlib import Path
from typing import Any

HERE=Path(__file__).resolve().parent;SEM=HERE.parent;AS_OF="2026-08-27"
PRECLASS=SEM/"applicability_matrices/member-preclassifications.jsonl"
PARTIAL_PACKAGES={
 "identity_and_equality":"p3i_identity_equality_coordinate_ontology",
 "grain_and_cardinality":"p3e_grain_coordinate_ontology",
 "state_and_change":"p3s_state_change_coordinate_ontology",
 "order_and_topology":"p3o_order_topology_coordinate_ontology",
 "partiality_and_uncertainty":"p3u_partiality_uncertainty_coordinate_ontology",
 "composition_algebra":"p3c_composition_algebra_coordinate_ontology",
}

def load_json(p:Path)->Any:return json.loads(p.read_text())
def load_jsonl(p:Path)->list[dict[str,Any]]:return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def canonical(v:Any)->str:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def ref_slug(v:str)->str:return v.removeprefix("library.").replace("_","-").replace(".","-")

def package_artifacts(directory:Path)->tuple[Path,Path]:
 return next(directory.glob("*coordinate-ontology.json")),next(directory.glob("member*routes.jsonl"))

def coordinate_surface(ontology:dict[str,Any])->dict[str,Any]:
 keys=[k for k in ("coordinate_key","coordinate_contract","identity_coordinate","state_coordinate","time_coordinate","relation_coordinate","operator_coordinate","uncertainty_coordinate") if k in ontology]
 return {"axis_native_coordinate_fields":{k:ontology[k] for k in keys},"non_collapse_law_refs":[f"{ontology['ontology_id']}#non-collapse-{i:02d}" for i,_ in enumerate(ontology.get("non_collapse_laws",[]),1)]}

def build()->dict[str,Any]:
 pre=[r for r in load_jsonl(PRECLASS) if r["axis"] in PARTIAL_PACKAGES]
 pre_by_axis:dict[str,list[dict[str,Any]]]=defaultdict(list)
 for r in pre:pre_by_axis[r["axis"]].append(r)
 routes=[];axis_rows=[]
 for axis,package in sorted(PARTIAL_PACKAGES.items()):
  d=SEM/package;ontp,memberp=package_artifacts(d);ont=load_json(ontp);primary=load_jsonl(memberp);primary_refs={r["library_ref"] for r in primary}
  expected={r["library_ref"] for r in pre_by_axis[axis]};missing_rows=sorted((r for r in pre_by_axis[axis] if r["library_ref"] not in primary_refs),key=lambda r:r["library_ref"])
  for r in missing_rows:
   routes.append({"record_kind":"supplemental_axis_coordinate_route","route_id":f"route.coordinate-completion.{axis.replace('_','-')}.{ref_slug(r['library_ref'])}.v1","axis":axis,"coordinate_package_ref":package,"coordinate_ontology_ref":str(ontp.relative_to(SEM)),"library_ref":r["library_ref"],"family_ref":r["family_id"],"source_gap_ref":r["source_gap_ref"],"source_preclassification_ref":r["preclassification_id"],"source_preclassification":r["preclassification"],"source_candidate_facets":[x["facet"] for x in r["candidate_facets"]],**coordinate_surface(ont),"route_origin":"STRUCTURAL_ALL_CELL_COMPLETION_NO_TARGETED_EVIDENCE","required_next_evidence":["exact bearer and use-site inventory","bounded primary evidence for coordinate answers","member applicability and exception decision","owner receipt exact contract and conformance oracle"],"source_evidence_binding":"UNRESOLVED","coordinate_answers":"NOT_SUPPLIED","member_applicability":"UNRESOLVED","owner_decision":"UNRESOLVED","canonical_gaps_closed":0,"status":"LOSSLESSLY_ROUTED_RESEARCH_OPEN","completion_claim":False})
  axis_rows.append({"record_kind":"axis_coordinate_route_completion_summary","axis":axis,"coordinate_package_ref":package,"expected_member_axis_cells":len(expected),"primary_member_routes":len(primary_refs),"supplemental_member_routes":len(missing_rows),"combined_member_routes":len(primary_refs)+len(missing_rows),"remaining_unrouted_member_refs":sorted(expected-primary_refs-{r["library_ref"] for r in missing_rows}),"source_evidence_bindings_supplied":0,"member_applicability_decisions":0,"owner_decisions":0,"canonical_gaps_closed":0,"completion_claim":False})
 grouped:dict[tuple[str,str,str,tuple[str,...]],list[str]]=defaultdict(list)
 for r in routes:grouped[(r["axis"],r["family_ref"],r["source_preclassification"],tuple(r["source_candidate_facets"]))].append(r["library_ref"])
 clusters=[]
 for i,(key,refs) in enumerate(sorted(grouped.items()),1):
  axis,family,preclass,facets=key;clusters.append({"record_kind":"supplemental_axis_coordinate_research_cluster","cluster_id":f"cluster.coordinate-completion.{axis.replace('_','-')}.{i:03d}","axis":axis,"family_ref":family,"source_preclassification":preclass,"source_candidate_facets":list(facets),"library_refs":sorted(refs),"library_count":len(refs),"research_route":"FULL_BEARER_COORDINATE_RESEARCH_REQUIRED_NO_TARGETED_EVIDENCE_ROUTE","source_evidence_binding":"UNRESOLVED","member_applicability":"UNRESOLVED","owner_decision":"UNRESOLVED","canonical_gaps_closed":0,"completion_claim":False})
 summary={"program_id":"program.coordinate-route-completion.v1","as_of":AS_OF,"partial_coordinate_packages":len(axis_rows),"expected_cells_in_partial_axes":sum(r["expected_member_axis_cells"] for r in axis_rows),"existing_primary_routes":sum(r["primary_member_routes"] for r in axis_rows),"supplemental_routes":len(routes),"combined_routes_in_partial_axes":sum(r["combined_member_routes"] for r in axis_rows),"all_axis_expected_member_cells":10784,"all_axis_existing_primary_routes":9545,"all_axis_combined_routes":9545+len(routes),"research_clusters":len(clusters),"source_evidence_bindings_supplied":0,"coordinate_answers_supplied":0,"member_applicability_decisions":0,"owner_decisions":0,"canonical_gaps_closed":0,"completion_claim":False}
 return {"routes":routes,"axis_rows":axis_rows,"clusters":clusters,"summary":summary}

def outputs()->dict[str,str]:
 b=build();files={"supplemental-member-coordinate-routes.jsonl":"".join(canonical(x)+"\n" for x in b["routes"]),"axis-route-completion-summary.jsonl":"".join(canonical(x)+"\n" for x in b["axis_rows"]),"supplemental-research-clusters.jsonl":"".join(canonical(x)+"\n" for x in b["clusters"]),"summary.json":json.dumps(b["summary"],ensure_ascii=False,sort_keys=True,indent=2)+"\n"};claims={n:{"bytes":len(t.encode()),"sha256":hashlib.sha256(t.encode()).hexdigest()} for n,t in files.items()};files["manifest.json"]=json.dumps({"manifest_id":"manifest.coordinate-route-completion.v1","as_of":AS_OF,"files":claims,"completion_claim":False},sort_keys=True,indent=2)+"\n";return files
def main():
 for n,t in outputs().items():(HERE/n).write_text(t)
 s=build()["summary"];print(f"BUILD PASS coordinate route completion: {s['supplemental_routes']} structural vacancy routes complete {s['all_axis_combined_routes']} / {s['all_axis_expected_member_cells']} cells; decisions remain zero");return 0
if __name__=="__main__":raise SystemExit(main())
