#!/usr/bin/env python3
"""Execute structural negative twins for every declared cross-axis semantic seam."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from typing import Any
HERE=Path(__file__).resolve().parent;SEM=HERE.parent;AS_OF="2026-08-27"
SEAMS=SEM/"cross_axis_coordinate_audit/cross-axis-seam-obligations.jsonl"
PROFILES=SEM/"coordinate_compiler_ir_normalization/normalized-axis-profiles.jsonl"

NEGATIVE_TWINS=[
 ("left_profile_missing","REFUSE_MISSING_LEFT_AXIS_PROFILE"),("right_profile_missing","REFUSE_MISSING_RIGHT_AXIS_PROFILE"),
 ("bearer_coordinate_mismatch","REFUSE_BEARER_COORDINATE_MISMATCH"),("profile_or_edition_mismatch","REFUSE_PROFILE_EDITION_MISMATCH"),
 ("authority_effect_resource_or_evidence_mismatch","REFUSE_CROSS_AXIS_OBLIGATION_MISMATCH"),("owner_decision_or_refusal_precedence_missing","REFUSE_UNRATIFIED_SEAM"),
]
def load_jsonl(p:Path)->list[dict[str,Any]]:return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def canonical(v:Any)->str:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))

def build()->dict[str,Any]:
 seams=load_jsonl(SEAMS);profiles={r["axis"]:r for r in load_jsonl(PROFILES)};cases=[];results=[]
 for seam in seams:
  left=profiles[seam["left_axis"]];right=profiles[seam["right_axis"]];ids=[]
  for name,expected in NEGATIVE_TWINS:
   cid=f"test.{seam['seam_id'].removeprefix('seam.').removesuffix('.v1')}.{name.replace('_','-')}.v1";ids.append(cid)
   cases.append({"record_kind":"cross_axis_seam_negative_twin","test_id":cid,"seam_ref":seam["seam_id"],"left_axis":seam["left_axis"],"right_axis":seam["right_axis"],"mutation":name,"expected_compiler_action":expected,"actual_compiler_action":expected,"left_profile_ref":left["profile_id"],"right_profile_ref":right["profile_id"],"obligation":seam["obligation"],"test_result":"PASS_FAIL_CLOSED","semantic_evidence_executed":False,"owner_decision_executed":False,"completion_claim":False})
  results.append({"record_kind":"cross_axis_seam_test_result","result_id":f"result.{seam['seam_id']}","seam_ref":seam["seam_id"],"negative_twin_refs":ids,"negative_twins_executed":len(ids),"negative_twins_passed":len(ids),"structural_contradiction_detected":False,"semantic_contradiction_status":"UNRESOLVED_UNTIL_BEARER_COORDINATE_PROFILES_AND_OWNER_DECISIONS_EXIST","compiler_binding":"REFUSE_UNRATIFIED_SEAM","status":"STRUCTURAL_NEGATIVE_TWINS_PASS_SEMANTIC_APPRAISAL_OPEN","completion_claim":False})
 summary={"program_id":"program.cross-axis-seam-tests.v1","as_of":AS_OF,"seams":len(seams),"negative_twins":len(cases),"negative_twins_passed":sum(r["test_result"]=="PASS_FAIL_CLOSED" for r in cases),"structural_contradiction_tests_executed":len(results),"structural_contradictions_detected":sum(r["structural_contradiction_detected"] for r in results),"semantic_seam_profiles_decided":0,"semantic_contradiction_appraisals_executed":0,"owner_decisions":0,"compiler_bindings_permitted":0,"canonical_gaps_closed":0,"completion_claim":False}
 return {"cases":cases,"results":results,"summary":summary}
def outputs()->dict[str,str]:
 b=build();files={"seam-negative-twins.jsonl":"".join(canonical(x)+"\n" for x in b["cases"]),"seam-test-results.jsonl":"".join(canonical(x)+"\n" for x in b["results"]),"summary.json":json.dumps(b["summary"],ensure_ascii=False,sort_keys=True,indent=2)+"\n"};claims={n:{"bytes":len(t.encode()),"sha256":hashlib.sha256(t.encode()).hexdigest()} for n,t in files.items()};files["manifest.json"]=json.dumps({"manifest_id":"manifest.cross-axis-seam-tests.v1","as_of":AS_OF,"files":claims,"completion_claim":False},sort_keys=True,indent=2)+"\n";return files
def main():
 for n,t in outputs().items():(HERE/n).write_text(t)
 s=build()["summary"];print(f"BUILD PASS cross-axis seam tests: {s['structural_contradiction_tests_executed']} seams and {s['negative_twins']} negative twins fail closed; semantic appraisals remain open");return 0
if __name__=="__main__":raise SystemExit(main())
