#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(name):
    return [
        json.loads(x) for x in (HERE / name).read_text(encoding="utf-8").splitlines() if x.strip()
    ]


tranches = load("closure-tranches.jsonl")
batch = load("source-authority-ratification-batch.jsonl")
effective_receipts = load("effective-research-resolution-receipts.jsonl")
closure_summary = json.loads((HERE / "summary.json").read_text(encoding="utf-8"))
assert len(tranches) == 9
rebase_summary = json.loads(
    (HERE.parent / "research_convergence_rebase/summary.json").read_text(encoding="utf-8")
)
assert sum(row["quotient_count"] for row in tranches) == rebase_summary["current_gap_quotients"]
assert sum(row["atom_count"] for row in tranches) == rebase_summary["current_gap_atoms"]
assert (
    sum(row["research_residual_quotient_count_before_current_supplements"] for row in tranches)
    == rebase_summary["research_residual_quotients"]
)
assert (
    sum(row["research_residual_atom_count_before_current_supplements"] for row in tranches)
    == rebase_summary["research_residual_atoms"]
)
assert (
    sum(row["research_residual_quotient_count"] for row in tranches)
    == closure_summary["research_residual_quotients"]
)
assert (
    sum(row["research_residual_atom_count"] for row in tranches)
    == closure_summary["research_residual_atoms"]
)
assert (
    sum(row["current_supplement_resolved_atom_count"] for row in tranches)
    == closure_summary["current_supplement_resolved_atoms"]
)
assert len(effective_receipts) == closure_summary["current_supplement_resolved_quotients"]
assert (
    sum(row["resolved_research_atoms"] for row in effective_receipts)
    == closure_summary["current_supplement_resolved_atoms"]
)
assert all(
    row["canonical_gaps_closed"] == 0 and row["completion_claim"] is False
    for row in effective_receipts
)
assert all(row["effective_research_residual_atoms"] >= 0 for row in effective_receipts)
assert len(batch) == closure_summary["source_authority_prepared_payload_count"]
assert len({row["family_ref"] for row in batch}) == len(batch)
assert closure_summary["source_authority_current_family_count"] == next(
    row["quotient_count"] for row in tranches if row["gap_kind"] == "source-authority"
)
assert closure_summary["source_authority_unprepared_family_count"] == next(
    row["research_residual_quotient_count"]
    for row in tranches
    if row["gap_kind"] == "source-authority"
)
assert closure_summary["source_authority_unprepared_family_count"] == 0
assert (
    closure_summary["source_authority_prepared_payload_count"]
    == closure_summary["source_authority_current_family_count"]
)
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

print(
    f"PASS closure cockpit: {rebase_summary['prior_gap_quotients']} prior-snapshot quotients retained as provenance; {rebase_summary['current_gap_quotients']} live quotients / {rebase_summary['current_gap_atoms']:,} atoms; {closure_summary['research_residual_quotients']} effective research residual quotients / {closure_summary['research_residual_atoms']} atoms after {len(effective_receipts)} current supplement; {len(batch)}/{closure_summary['source_authority_current_family_count']} source-authority decisions prepared"
)
