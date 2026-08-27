#!/usr/bin/env python3
"""Validate generated human-work/review corpus and deterministic drift."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
def load(name: str) -> list[dict]: return [json.loads(x) for x in (ROOT / name).read_text().splitlines() if x.strip()]
def main() -> None:
    before = {p.name: p.read_bytes() for p in ROOT.glob("*.json*")}
    out = subprocess.run([sys.executable, str(ROOT / "build_corpus.py")], capture_output=True, text=True, check=True)
    after = {p.name: p.read_bytes() for p in ROOT.glob("*.json*")}
    assert before == after, "generated drift"
    sources, contexts, decisions, libs, lenses, neg = (load(n) for n in ("sources.jsonl", "bounded-contexts.jsonl", "decision-points.jsonl", "library-contracts.jsonl", "boundary-lens-adjudication.jsonl", "negative-twins.jsonl"))
    assert len(sources) >= 25 and len(contexts) == 6 and len(libs) == 7 and len(decisions) >= 145 and len(lenses) == 12 and len(neg) >= 40
    assert all(d["default"] is None and d["default_law"] == "forbidden" for d in decisions)
    assert all(l["qualification_required"] is False and l["status"] == "specified" for l in libs)
    assert all(any("agent" in law.lower() or "model" in law.lower() for law in l["laws"]) for l in libs)
    print(out.stdout.strip()); print(f"VALIDATION PASS hwra: {sum(len(l['operations']) for l in libs)} operations; zero qualified implementations")
if __name__ == "__main__": main()
