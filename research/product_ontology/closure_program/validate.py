#!/usr/bin/env python3
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
def load(name): return [json.loads(x) for x in (HERE / name).read_text().splitlines() if x.strip()]
tranches = load("closure-tranches.jsonl")
batch = load("source-authority-ratification-batch.jsonl")
closure_summary = json.loads((HERE / "summary.json").read_text())
assert len(tranches) == 9
assert sum(row["quotient_count"] for row in tranches) == 686
rebase_summary = json.loads((HERE.parent / "research_convergence_rebase/summary.json").read_text())
assert sum(row["atom_count"] for row in tranches) == rebase_summary["current_gap_atoms"]
assert len(batch) == 23 and len({row["family_ref"] for row in batch}) == 23
assert all(row["status"] == "READY_FOR_NAMED_RATIFIER_REVIEW" for row in batch)
assert all(all(row["checks"].values()) for row in batch)
assert closure_summary["canonical_gaps_closed"] == 0
print(f"PASS closure cockpit: 686 quotients / {rebase_summary['current_gap_atoms']:,} atoms; first 23 source-authority decisions are ratifier-ready")
