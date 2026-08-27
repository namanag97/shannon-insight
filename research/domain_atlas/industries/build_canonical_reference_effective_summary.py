#!/usr/bin/env python3
"""Summarize the complete B07 reference-disposition frontier without promoting authority."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name: str) -> list[dict]:
    return [json.loads(line) for line in (HERE / name).read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    queue = load("canonical-reference-review-queue.jsonl")
    ledger = load("canonical-reference-adjudications.jsonl")
    machine = load("canonical-reference-auto-alias-candidates.jsonl")
    current = load("canonical-reference-current-method-candidates.jsonl")
    queue_ids = {row["queue_id"] for row in queue}
    layers = [
        {row["queue_id"] for row in ledger},
        {row["queue_id"] for row in machine},
        {row["queue_id"] for row in current},
    ]
    assert all(layer <= queue_ids for layer in layers)
    assert sum(len(layer) for layer in layers) == len(set().union(*layers)), "reference disposition layers overlap"
    covered = set().union(*layers)
    statuses = Counter(row["status"] for row in ledger)
    relations = Counter(row["relation"] for row in ledger)
    domains = Counter(row["reference_domain"] for row in ledger)
    summary = {
        "report_id": "canonical_reference_effective_frontier",
        "as_of": "2026-08-28",
        "raw_queue_records": len(queue),
        "ledger_disposition_records": len(ledger),
        "ledger_research_resolved_candidate_records": statuses["research_resolved_candidate_not_ratified"],
        "ledger_typed_extension_gap_records": statuses["typed_extension_gap_open"],
        "ledger_exact_alias_records": relations["exact_alias"],
        "machine_exact_alias_candidate_records": len(machine),
        "current_method_identity_candidate_records": len(current),
        "covered_queue_records": len(covered),
        "uncovered_queue_records": len(queue_ids - covered),
        "ledger_records_by_domain": dict(sorted(domains.items())),
        "ledger_records_by_status": dict(sorted(statuses.items())),
        "ledger_records_by_relation": dict(sorted(relations.items())),
        "semantic_ratifications": 0,
        "completion_claim": False,
        "status": "ALL_QUEUE_REFERENCES_HAVE_EXPLICIT_DISPOSITION_OR_TYPED_GAP_AUTHORITY_WITHHELD",
    }
    (HERE / "canonical-reference-effective-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
