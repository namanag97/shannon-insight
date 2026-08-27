#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(name):
    return [json.loads(x) for x in (HERE / name).read_text(encoding="utf-8").splitlines() if x.strip()]


tranches = load("closure-tranches.jsonl")
batch = load("source-authority-ratification-batch.jsonl")
closure_summary = json.loads((HERE / "summary.json").read_text(encoding="utf-8"))
assert len(tranches) == 9
assert sum(row["quotient_count"] for row in tranches) == 686
rebase_summary = json.loads((HERE.parent / "research_convergence_rebase/summary.json").read_text(encoding="utf-8"))
assert sum(row["atom_count"] for row in tranches) == rebase_summary["current_gap_atoms"]
assert len(batch) == 23 and len({row["family_ref"] for row in batch}) == 23
assert all(row["status"] == "READY_FOR_NAMED_RATIFIER_REVIEW" for row in batch)
assert all(all(row["checks"].values()) for row in batch)
assert closure_summary["canonical_gaps_closed"] == 0

for script in (
    HERE / "validate_master_frontier.py",
    ROOT / "research/domain_atlas/validate_ownership_adjudications.py",
    ROOT / "research/domain_atlas/industries/validate_exact_alias_candidates.py",
    ROOT / "research/domain_atlas/industries/validate_canonical_reference_review_batches.py",
):
    result = subprocess.run([sys.executable, str(script)], cwd=ROOT, text=True, capture_output=True)
    if result.returncode:
        raise SystemExit((result.stdout + "\n" + result.stderr).strip())
    print(result.stdout.strip())

print(f"PASS closure cockpit: 686 historical quotients / {rebase_summary['current_gap_atoms']:,} atoms retained as trace; live master frontier validated separately; first 23 source-authority decisions are ratifier-ready")
