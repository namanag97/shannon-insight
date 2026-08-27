#!/usr/bin/env python3
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def load(n): return [json.loads(x) for x in (ROOT/n).read_text().splitlines() if x.strip()]
def main():
 before={p.name:p.read_bytes() for p in ROOT.glob("*.json*")}; out=subprocess.run([sys.executable,str(ROOT/"build_corpus.py")],capture_output=True,text=True,check=True); after={p.name:p.read_bytes() for p in ROOT.glob("*.json*")}; assert before==after,"generated drift"
 ss,cs,ds,ls,lens,ns=(load(n) for n in ("sources.jsonl","bounded-contexts.jsonl","decision-points.jsonl","library-contracts.jsonl","boundary-lens-adjudication.jsonl","negative-twins.jsonl"))
 assert len(ss)>=25 and len(cs)==4 and len(ds)>=100 and len(ls)==4 and len(lens)==12 and len(ns)>=30
 assert all(d["default"] is None and d["default_law"]=="forbidden" for d in ds); assert all(l["qualification_required"] is False for l in ls)
 print(out.stdout.strip()); print(f"VALIDATION PASS acr: {sum(len(l['operations']) for l in ls)} operations; zero qualified implementations")
if __name__=="__main__": main()
