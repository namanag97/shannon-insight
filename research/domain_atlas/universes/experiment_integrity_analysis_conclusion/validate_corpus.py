#!/usr/bin/env python3
"""Validate the experiment integrity/analysis/conclusion corpus and generated drift."""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def load(name): return [json.loads(x) for x in (ROOT/name).read_text().splitlines() if x.strip()]
def validate_gaps_against_schema(gaps, schema):
 required=set(schema["required"]); allowed=set(schema["properties"]); kinds=set(schema["properties"]["gap_class"]["enum"])
 for gap in gaps:
  assert required <= set(gap) <= allowed and gap["gap_class"] in kinds and gap["status"]=="OPEN"
  assert all(gap[k] for k in ("semantic_axes","scope_refs","closure_evidence","blocked_outputs"))
def main():
 before={p.name:p.read_bytes() for p in ROOT.glob("*.json*")}
 out=subprocess.run([sys.executable,str(ROOT/"build_corpus.py")],capture_output=True,text=True,check=True)
 after={p.name:p.read_bytes() for p in ROOT.glob("*.json*")}
 assert before==after,"generated drift"
 manifest=json.loads((ROOT/"manifest.json").read_text()); schema=json.loads((ROOT/"corpus-control.schema.json").read_text())
 for name,meta in manifest["files"].items(): assert meta["sha256"]==hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),name
 sources,contexts,decisions,libs,lenses,profiles,neg,gaps=(load(n) for n in ("sources.jsonl","bounded-contexts.jsonl","decision-points.jsonl","library-contracts.jsonl","boundary-lens-adjudication.jsonl","qualification-profiles.jsonl","negative-twins.jsonl","gaps.jsonl"))
 validate_gaps_against_schema(gaps,schema); assert len(gaps)==5 and manifest["completion_claim"] is False
 assert len(sources)>=25 and len(contexts)==6 and len(libs)==6 and len(decisions)>=150 and len(lenses)==12 and len(neg)>=45
 assert all(d["default"] is None and d["default_law"]=="forbidden" for d in decisions)
 assert all(l["qualification_required"] is False and l["qualified_implementation_count"]==0 and l["status"]=="specified" for l in libs)
 assert len(profiles)==6 and all(p["status"]=="template_not_executed" and p["results"]==[] for p in profiles)
 assert all(any("agent" in law.lower() or "model" in law.lower() for law in l["laws"]) for l in libs)
 assert all(l["operation_refs"] and l["decision_refs"] and l["conformance_oracles"] for l in libs)
 print(out.stdout.strip()); print(f"VALIDATION PASS eiac: {sum(len(l['operation_refs']) for l in libs)} operations; 5 typed open gaps; zero qualified implementations")
if __name__=="__main__": main()
