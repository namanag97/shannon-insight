#!/usr/bin/env python3
"""Join the five phase constitutions to all 368 family-axis review packages."""

from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from typing import Any

HERE=Path(__file__).resolve().parent
AS_OF="2026-08-26"
PHASE_DIRS=["phase1_subject_grain","phase2_dynamics_information","phase3_authority_effect_safety","phase4_representation_evolution","phase5_behavior_resources_proof"]

def canonical(value:Any)->str:return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def load_jsonl(path:Path)->list[dict[str,Any]]:return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]

def build()->dict[str,Any]:
    phases=[];axis_to_module={}
    for phase_number,dirname in enumerate(PHASE_DIRS,1):
        path=HERE/dirname/"constitution.json";constitution=json.loads(path.read_text())
        axes=[]
        for module in constitution["modules"]:
            axis=module["axis"];assert axis not in axis_to_module
            axis_to_module[axis]={"phase":phase_number,"constitution_ref":constitution["constitution_id"],"module_ref":module["module_id"],"source_path":str(path.relative_to(HERE))}
            axes.append(axis)
        phases.append({"phase":phase_number,"constitution_ref":constitution["constitution_id"],"status":constitution["status"],"axes":axes,"source_path":str(path.relative_to(HERE)),"completion_claim":constitution["completion_claim"]})
    packages=load_jsonl(HERE/"family-axis-review-packages.jsonl")
    inheritance=[]
    for package in packages:
        binding=axis_to_module[package["axis"]]
        inheritance.append({
            "record_kind":"family_semantic_constitution_inheritance_candidate","edition":1,
            "inheritance_id":f"inheritance.{package['family_id']}.{package['axis'].replace('_','-')}",
            "family_id":package["family_id"],"axis":package["axis"],"library_count":package["library_count"],
            "work_package_ref":package["work_package_id"],"candidate_facet_counts":package["candidate_facet_counts"],
            "phase":binding["phase"],"constitution_ref":binding["constitution_ref"],"module_ref":binding["module_ref"],
            "inheritance_mode":"CANDIDATE_DEFAULT_REQUIRES_OWNER_ATTESTATION",
            "required_owner_output":["one axis-level applicability decision for every family member","only family or library additions exceptions and prohibitions","evidence vacancies and conflicting owner claims","non-collapse and negative-twin results","exact source-contract import reference after ratification"],
            "allowed_member_decisions":["APPLICABLE_AS_IS","APPLICABLE_WITH_EXCEPTION","CONDITIONAL","INAPPLICABLE_WITH_REASON","PROHIBITED_WITH_REASON","UNRESOLVED"],
            "closure_effect":"Ratifies inherited semantic obligations for this family-axis only; exact library gaps close separately after source contract and conformance gates.",
            "status":"OWNER_APPLICABILITY_AND_EXCEPTION_MATRIX_REQUIRED",
        })
    family_ids={x["family_id"] for x in inheritance}
    coverage={"record_kind":"semantic_constitution_coverage","coverage_id":"coverage.semantic-axis.constitutions.v1","edition":1,"as_of":AS_OF,"status":"ALL_GLOBAL_CONSTITUTIONS_CANDIDATE_COMPLETE_OWNER_RATIFICATION_OPEN","completion_claim":False,"axis_count":len(axis_to_module),"family_count":len(family_ids),"family_axis_matrix_count":len(inheritance),"phases":phases,"axis_bindings":[{"axis":axis,**binding} for axis,binding in sorted(axis_to_module.items())],"execution_rule":"Ratify five global phase constitutions once; then process 23 family exception matrices per axis. Never copy full constitutions into 674 libraries and never infer applicability from lexical matches.","canonical_gap_effect":0}
    summary={"program_id":"program.semantic-axis.constitution-coverage.v1","edition":1,"as_of":AS_OF,"global_phase_constitutions":len(phases),"axes":len(axis_to_module),"families":len(family_ids),"family_axis_matrices":len(inheritance),"library_axis_manual_reviews_replaced_by_inheritance":True,"canonical_exact_gaps_closed":0,"next_gate":"Owner-ratify constitutions and family applicability/exception matrices; then generate exact library source contracts and conformance obligations."}
    return {"coverage":coverage,"inheritance":inheritance,"summary":summary}

def outputs()->dict[str,str]:
    b=build();files={"constitution-coverage.json":json.dumps(b["coverage"],ensure_ascii=False,sort_keys=True,indent=2)+"\n","family-inheritance-queue.jsonl":"".join(canonical(x)+"\n" for x in b["inheritance"]),"constitution-coverage-summary.json":json.dumps(b["summary"],ensure_ascii=False,sort_keys=True,indent=2)+"\n"};manifest={n:{"sha256":hashlib.sha256(t.encode()).hexdigest(),"bytes":len(t.encode())} for n,t in files.items()};files["constitution-coverage-manifest.json"]=json.dumps({"manifest_id":"manifest.semantic-axis.constitution-coverage.v1","as_of":AS_OF,"files":manifest},sort_keys=True,indent=2)+"\n";return files

def main()->int:
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args();stale=[]
    for n,t in outputs().items():
        q=HERE/n
        if a.check:
            if not q.is_file() or q.read_text()!=t:stale.append(n)
        else:q.write_text(t)
    if stale:print("STALE "+", ".join(stale));return 1
    s=build()["summary"];print(f"{'CHECK' if a.check else 'BUILD'} PASS semantic constitution coverage: {s['global_phase_constitutions']} phases, {s['axes']} axes, {s['families']} families, {s['family_axis_matrices']} inheritance matrices");return 0

if __name__=="__main__":raise SystemExit(main())
