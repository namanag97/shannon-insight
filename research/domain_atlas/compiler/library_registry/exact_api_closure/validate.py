#!/usr/bin/env python3
"""Validate exact and complete coverage of the central exact-API backlog."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from build_program import (
    FAMILY_PRIMARY_EVIDENCE_SEEDS,
    HERE,
    REGISTRY,
    build_batches,
    build_records,
    outputs,
    rows,
)


def main() -> int:
    expected = outputs()
    for name, content in expected.items():
        path = HERE / name
        assert path.is_file() and path.read_text(encoding="utf-8") == content, f"stale {name}"
    manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
    for name, item in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == item["sha256"], name
        assert len(data) == item["bytes"], name
    queue = rows(HERE / "closure-queue.jsonl")
    batches = rows(HERE / "research-batches.jsonl")
    libraries = rows(REGISTRY / "library-contributions.jsonl")
    exact_gap_refs = {
        library["library_id"]
        for library in libraries
        if any(gap["gap_kind"] == "exact_api_contract_missing" for gap in library["gaps"])
    }
    assert len(queue) == len(exact_gap_refs) == len(build_records())
    assert {row["library_ref"] for row in queue} == exact_gap_refs
    assert len({row["closure_id"] for row in queue}) == len(queue)
    assert all(row["placeholder_dimensions"] for row in queue)
    assert all(len(row["required_source_contract"]) == 10 for row in queue)
    assert all(row["status"] == "OPEN_OWNER_CONTRACT_REQUIRED" for row in queue)
    assert queue == sorted(queue, key=lambda row: (-row["priority_score"], row["library_ref"]))
    assert batches == build_batches(queue)
    assigned_closures = [ref for batch in batches for ref in batch["closure_refs"]]
    assert len(assigned_closures) == len(set(assigned_closures)) == len(queue)
    assert set(assigned_closures) == {row["closure_id"] for row in queue}
    assert all(batch["item_count"] == len(batch["closure_refs"]) == len(batch["library_refs"]) for batch in batches)
    assert all(batch["research_family"] != "unclassified_refuse" for batch in batches)
    assert all(batch["evidence_program"] and batch["execution_strategy"] for batch in batches)
    seeded_families = {batch["research_family"] for batch in batches if batch["primary_evidence_seeds"]}
    assert seeded_families == set(FAMILY_PRIMARY_EVIDENCE_SEEDS)
    assert all(batch["evidence_seed_status"] == "DISCOVERY_ONLY_NOT_ADOPTED_AUTHORITY" for batch in batches)
    for batch in batches:
        for seed in batch["primary_evidence_seeds"]:
            assert set(seed) == {"title", "uri", "claim_scope"}
            assert seed["uri"].startswith("https://") and seed["claim_scope"]
    summary = json.loads((HERE / "summary.json").read_text(encoding="utf-8"))
    assert summary["open_items"] == len(queue) and summary["research_batches"] == len(batches) and summary["completion_claim"] is False
    print(f"PASS exact-API closure program: {len(queue)} gaps in {len(batches)} research batches, covered exactly once; top={queue[0]['library_ref'] if queue else 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
