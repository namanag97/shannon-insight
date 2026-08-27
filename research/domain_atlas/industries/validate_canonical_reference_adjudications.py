#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATLAS = HERE.parent
ROOT = ATLAS.parents[1]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


queue = {row["queue_id"]: row for row in load_jsonl(HERE / "canonical-reference-review-queue.jsonl")}
decisions = load_jsonl(HERE / "canonical-reference-adjudications.jsonl")
practices = {
    row["practice_id"]: row
    for row in load_jsonl(ATLAS / "universes/analytics_types/candidate-practices.jsonl")
}
summary = json.loads((HERE / "canonical-reference-effective-summary.json").read_text(encoding="utf-8"))
integration = json.loads((HERE / "integration-audit.json").read_text(encoding="utf-8"))

assert len(decisions) == len({row["queue_id"] for row in decisions}) == 3
resolved_occurrences = 0
for row in decisions:
    assert row["queue_id"] in queue
    source = queue[row["queue_id"]]
    assert source["reference_domain"] == row["reference_domain"] == "analytical_practice"
    assert source["raw_ref"] == row["raw_ref"]
    assert source["status"] == "open"
    assert row["relation"] == "exact_alias"
    assert row["status"] == "research_resolved_candidate_not_ratified"
    assert row["completion_claim"] is False
    assert row["remaining_gate"] == "canonical analytical-practice authority ratification"
    assert len(row["candidate_target_refs"]) == 1
    target = row["candidate_target_refs"][0]
    assert target in practices
    assert row["decision_basis"]
    assert all(item.get("claim") and item.get("source_ref") for item in row["decision_basis"])
    resolved_occurrences += source["occurrence_count"]

raw_count = integration["canonical_reference_review_queue_records"]
raw_methods = integration["canonical_reference_closure"]["unresolved_method_refs"]
assert summary["raw_queue_records"] == raw_count
assert summary["research_resolved_candidate_records"] == len(decisions)
assert summary["research_resolved_occurrences"] == resolved_occurrences
assert summary["remaining_open_research_records"] == raw_count - len(decisions)
assert summary["method_reference_frontier"]["raw_unresolved_distinct"] == raw_methods
assert summary["method_reference_frontier"]["research_resolved_candidate_distinct"] == len(decisions)
assert summary["method_reference_frontier"]["remaining_open_research_distinct"] == raw_methods - len(decisions)
assert summary["method_reference_frontier"]["canonically_ratified_distinct"] == 0
assert summary["completion_claim"] is False
print(f"PASS canonical reference adjudications: {len(decisions)} method refs / {resolved_occurrences} occurrences research-resolved; authority ratification withheld")
