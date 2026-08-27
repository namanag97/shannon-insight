#!/usr/bin/env python3
"""Validate Master/Reference Data exact boundaries and non-collapse laws."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import build_corpus


ROOT = Path(__file__).resolve().parent


def load(name: str) -> list[dict]:
    return [json.loads(line) for line in (ROOT / name).read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    data = {name: load(name) for name in build_corpus.FILES}
    for name, rows in data.items():
        assert manifest["files"][name]["records"] == len(rows)
        assert manifest["files"][name]["sha256"] == hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    assert len(data["sources.jsonl"]) == 16 and all(row["url"].startswith("https://") for row in data["sources.jsonl"])
    assert len(data["bounded-contexts.jsonl"]) == 7
    decisions = data["decision-points.jsonl"]
    assert len(decisions) == 35 and all(row["default"] is None and row["default_law"] == "forbidden" for row in decisions)
    libs = data["library-contracts.jsonl"]
    assert len(libs) == 7 and len({row["library_id"] for row in libs}) == 7
    assert sum(row["library_id"].startswith("library.master_data.") for row in libs) == 4
    assert sum(row["library_id"].startswith("library.reference_data.") for row in libs) == 3
    decision_ids = {row["decision_id"] for row in decisions}
    for lib in libs:
        assert len(lib["public_types"]) >= 12 and len(lib["operations"]) == 4
        assert set(lib["operation_refs"]) == {op["operation_ref"] for op in lib["operations"]}
        assert set(lib["decision_refs"]) <= decision_ids and len(lib["decision_refs"]) == 5
        assert all(op["input_types"] and op["output_type"].startswith("Result<") for op in lib["operations"])
    authority = next(row for row in libs if row["library_id"] == "library.master_data.source_authority")
    assert not any("register" in op["operation_ref"] for op in authority["operations"])
    identity = next(row for row in libs if row["library_id"] == "library.master_data.domain_identity")
    assert identity["effect_boundary"] == "pure_effect_intents"
    laws = " ".join(law for lib in libs for law in lib["laws"]).lower()
    for phrase in ["not a source-record identifier", "never registers or rewrites", "not universal truth", "not a source mutation", "not thereby a mastered business entity", "code, code identity, concept", "does not imply a reverse mapping"]:
        assert phrase in laws, phrase
    offers = [row for row in data["compiler-contracts.jsonl"] if row["record_kind"] == "capability_offer"]
    assert len(data["compiler-contracts.jsonl"]) == 21 and len(offers) == 7
    assert all(not row["portable"] and not row["selectable"] and row["qualified_implementation_count"] == 0 for row in offers)
    assert len(data["negative-twins.jsonl"]) == 13 and manifest["completion_claim"] is False
    print("VALIDATION PASS master/reference data governance: 7 exact boundaries, 35 no-default decisions, 0 qualified offers")


if __name__ == "__main__":
    main()
