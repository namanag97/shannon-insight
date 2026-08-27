#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

def load(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]

source = load(HERE / "gaps.jsonl")
effective = load(HERE / "effective-gap-dispositions.jsonl")
source_ids = {row["record_id"] for row in source}
effective_ids = {row["gap_id"] for row in effective}
assert len(source) == len(source_ids) == 20
assert len(effective) == len(effective_ids) == 20
assert source_ids == effective_ids
allowed = {"OPEN", "NARROWED_OPEN", "CLOSED"}
for row in effective:
    assert row["effective_status"] in allowed
    assert row["remaining_requirement"]
    assert row["evidence_refs"]
    if row["effective_status"] == "NARROWED_OPEN":
        assert row.get("superseded_claim")
    if row["effective_status"] == "CLOSED":
        raise AssertionError("No global gap is currently supportably closed end to end")
print("PASS effective global gap rebase: 20/20 historical gaps preserved; stale wording narrowed; 0 unsupported closure claims")
