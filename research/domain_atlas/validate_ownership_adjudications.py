#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
source = json.loads((HERE / "ownership-ambiguities.json").read_text(encoding="utf-8"))
rows = [json.loads(x) for x in (HERE / "ownership-adjudications.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
source_terms = {x["term"] for x in source["ambiguities"]}
row_terms = {x["term"] for x in rows}
assert len(rows) == len(source_terms) == 8
assert row_terms == source_terms
assert len({x["adjudication_id"] for x in rows}) == len(rows)
allowed = {"split", "split_by_semantic_question", "single_authority_owner_plus_imported_reference", "authority_plus_local_reaction", "split_with_shared_algebra"}
for row in rows:
    assert row["status"] == "research_resolved_candidate_not_ratified"
    assert row["completion_claim"] is False
    assert row["remaining_gate"] == "named semantic-owner ratification"
    assert row["verdict"] in allowed
    assert len(row["noncollapse_laws"]) >= 3
    assert row["owner_disposition"]
    assert row["evidence"]
    assert all(e["claim"] and e["role"] and e["source"] for e in row["evidence"])
print("PASS ownership adjudications: 8/8 legacy ambiguities research-resolved; ratification withheld")
