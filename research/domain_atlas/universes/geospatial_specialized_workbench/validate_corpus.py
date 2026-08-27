#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parent
def load(n):return [json.loads(x) for x in (R/n).read_text().splitlines() if x.strip()]
def validate_gaps_against_schema(gaps,schema):
 required=set(schema["required"]);allowed=set(schema["properties"]);kinds=set(schema["properties"]["gap_class"]["enum"])
 for gap in gaps:
  assert required<=set(gap)<=allowed and gap["gap_class"] in kinds and gap["status"]=="OPEN"
  assert all(gap[k] for k in ("semantic_axes","scope_refs","closure_evidence","blocked_outputs"))
def main():
 b={p.name:p.read_bytes() for p in R.glob("*.json*")};o=subprocess.run([sys.executable,str(R/"build_corpus.py")],capture_output=True,text=True,check=True);a={p.name:p.read_bytes() for p in R.glob("*.json*")};assert b==a,"generated drift"
 manifest=json.loads((R/"manifest.json").read_text());schema=json.loads((R/"corpus-control.schema.json").read_text())
 for name,meta in manifest["files"].items():assert meta["sha256"]==hashlib.sha256((R/name).read_bytes()).hexdigest(),name
 s,c,d,l,x,n,p,gaps=(load(i) for i in ("sources.jsonl","bounded-contexts.jsonl","decision-points.jsonl","library-contracts.jsonl","boundary-lens-adjudication.jsonl","negative-twins.jsonl","qualification-profiles.jsonl","gaps.jsonl"))
 validate_gaps_against_schema(gaps,schema);assert len(gaps)==5 and manifest["completion_claim"] is False
 assert len(s)>=40 and len(c)==8 and len(d)>=300 and len(l)==18 and len(x)==12 and len(n)>=30 and len(p)==18
 assert all(q["default"] is None and q["default_law"]=="forbidden" for q in d)
 assert all(z["qualified_implementation_count"]==0 and z["status"]=="specified" for z in l)
 assert all(any("agent" in law.lower() or "model" in law.lower() for law in z["laws"]) for z in l)
 assert all(q["status"]=="template_not_executed" and q["results"]==[] for q in p)
 print(o.stdout.strip());print(f"VALIDATION PASS gsw: {sum(len(z['operation_refs']) for z in l)} operations; 5 typed open gaps; zero qualified implementations")
if __name__=="__main__":main()
