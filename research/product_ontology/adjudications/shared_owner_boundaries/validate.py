#!/usr/bin/env python3
"""Validate the multi-owner library boundary adjudication."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
REGISTRY = ROOT / "research/domain_atlas/compiler/library_registry/registry.jsonl"


def load(name: str) -> list[dict]:
    return [json.loads(line) for line in (HERE / name).read_text(encoding="utf-8").splitlines() if line]


def main() -> None:
    manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
    for name, item in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == item["sha256"], name
        assert len(load(name)) == item["records"], name
    registry = [json.loads(line) for line in REGISTRY.read_text(encoding="utf-8").splitlines()]
    libraries = {row["library_id"]: row for row in registry if row.get("record_kind") == "library_contribution"}
    ambiguous = {row["library_id"] for row in libraries.values() if any(gap.get("gap_kind") == "ambiguous_semantic_owner" for gap in row["gaps"])}
    verdicts = load("verdicts.jsonl")
    edges = load("replacement-edges.jsonl")
    gaps = load("closure-gaps.jsonl")
    assert len(verdicts) == 30
    assert all(row["subject_ref"] in libraries or row["disposition"] == "replaced_and_retired" for row in verdicts)
    assert len({row["verdict_id"] for row in verdicts}) == 30
    assert Counter(row["disposition"] for row in verdicts) == Counter({"retain_unique_owner": 10, "retain_unique_owner_after_rename": 1, "replaced_and_retired": 19})
    assert all(row["unique_owner_context_ref"] for row in verdicts)
    assert all(row["status"] == "adjudicated_candidate_not_ratified" for row in verdicts)
    assert all(row["to_ref_exists"] and row["to_ref"] in libraries for row in edges)
    assert len(gaps) == 0
    assert all(row["blocking"] and row["status"] == "open" for row in gaps)
    assert ambiguous == {row["subject_ref"] for row in gaps}
    selectable = [row for row in verdicts if row["compiler_selectable_after_verdict"]]
    assert len(selectable) == 11
    assert all(row["disposition"] in {"retain_unique_owner", "retain_unique_owner_after_rename"} for row in selectable)
    crosswalks = load("identity-crosswalks.jsonl")
    assert len(crosswalks) == 20
    assert all(row["compatibility_alias_permitted"] is False for row in crosswalks)
    composition_crosswalks = [row for row in crosswalks if row["record_kind"] == "library_composition_crosswalk"]
    assert len(composition_crosswalks) == 19
    assert all(row["legacy_ref"] not in libraries and set(row["canonical_refs"]) <= set(libraries) for row in composition_crosswalks)
    assert len(load("negative-twins.jsonl")) >= 6
    print("PASS shared-owner adjudication: 30/30 candidates covered; 10 retain, 1 completed rename, 19 retired compositions, 0 split; 0 source-closure gaps; every replacement edge resolves")


if __name__ == "__main__":
    main()
