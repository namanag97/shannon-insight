#!/usr/bin/env python3
"""Validate all B07 disposition layers while withholding canonical authority."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATLAS = HERE.parent


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    queue = {row["queue_id"]: row for row in load(HERE / "canonical-reference-review-queue.jsonl")}
    ledger = load(HERE / "canonical-reference-adjudications.jsonl")
    machine = load(HERE / "canonical-reference-auto-alias-candidates.jsonl")
    current = load(HERE / "canonical-reference-current-method-candidates.jsonl")
    practices = {row["practice_id"] for row in load(ATLAS / "universes/analytics_types/candidate-practices.jsonl")}
    summary = json.loads((HERE / "canonical-reference-effective-summary.json").read_text(encoding="utf-8"))

    assert len(ledger) == len({row["queue_id"] for row in ledger})
    statuses = Counter(row["status"] for row in ledger)
    relations = Counter(row["relation"] for row in ledger)
    domains = Counter(row["reference_domain"] for row in ledger)
    for row in ledger:
        source = queue[row["queue_id"]]
        assert row["reference_domain"] == source["reference_domain"]
        assert row["raw_ref"] == source["raw_ref"]
        assert row["completion_claim"] is False and row["remaining_gate"]
        assert row["status"] in {"research_resolved_candidate_not_ratified", "typed_extension_gap_open"}
        if row["relation"] == "exact_alias":
            assert row["status"] == "research_resolved_candidate_not_ratified"
            assert row["reference_domain"] == "analytical_practice"
            assert len(row["candidate_target_refs"]) == 1 and row["candidate_target_refs"][0] in practices
        if row["status"] == "typed_extension_gap_open":
            assert row["relation"] == "typed_extension_gap"
            assert not row["candidate_target_refs"] and row["extension_gap_refs"]

    layers = [
        {row["queue_id"] for row in ledger},
        {row["queue_id"] for row in machine},
        {row["queue_id"] for row in current},
    ]
    assert sum(len(layer) for layer in layers) == len(set().union(*layers))
    covered = set().union(*layers)
    assert covered <= set(queue)
    assert summary["raw_queue_records"] == len(queue)
    assert summary["ledger_disposition_records"] == len(ledger)
    assert summary["ledger_research_resolved_candidate_records"] == statuses["research_resolved_candidate_not_ratified"]
    assert summary["ledger_typed_extension_gap_records"] == statuses["typed_extension_gap_open"]
    assert summary["ledger_exact_alias_records"] == relations["exact_alias"]
    assert summary["machine_exact_alias_candidate_records"] == len(machine)
    assert summary["current_method_identity_candidate_records"] == len(current)
    assert summary["covered_queue_records"] == len(covered)
    assert summary["uncovered_queue_records"] == len(set(queue) - covered)
    assert summary["ledger_records_by_domain"] == dict(sorted(domains.items()))
    assert summary["semantic_ratifications"] == 0 and summary["completion_claim"] is False
    print(
        "PASS canonical reference frontier: "
        f"{len(ledger)} ledger dispositions + {len(machine)} machine exact candidates + {len(current)} current-method candidates "
        f"cover {len(covered)}/{len(queue)} queue records; {statuses['typed_extension_gap_open']} typed gaps and all authority gates remain explicit"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
