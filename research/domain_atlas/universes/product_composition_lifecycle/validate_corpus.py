#!/usr/bin/env python3
"""Validate product-composition lifecycle references and non-collapse laws."""

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
    assert len(data["sources.jsonl"]) >= 7 and all(row["url"].startswith("https://") for row in data["sources.jsonl"])
    assert len(data["bounded-contexts.jsonl"]) == 4
    decisions = data["decision-points.jsonl"]
    assert len(decisions) == 12 and all(row["default"] is None and row["default_law"] == "forbidden" for row in decisions)
    library = data["library-contracts.jsonl"][0]
    assert library["library_id"] == "library.product_composition.environment_lifecycle"
    assert library["semantic_owner_context"] == "context.product_composition.environment_reconciliation"
    assert len(library["public_types"]) >= 30 and len(library["operations"]) == 8
    assert set(library["operation_refs"]) == {row["operation_ref"] for row in library["operations"]}
    assert set(library["decision_refs"]) == {row["decision_id"] for row in decisions}
    laws = " ".join(library["laws"]).lower()
    for phrase in ["never acquires", "desired state, observed state", "not capability closure", "does not imply environment readiness", "rollback is not assumed", "deletion is not exit"]:
        assert phrase in laws, phrase
    compiler = data["compiler-contracts.jsonl"]
    offer = next(row for row in compiler if row["record_kind"] == "capability_offer")
    assert offer["qualified_implementation_count"] == 0 and not offer["portable"] and not offer["selectable"]
    rule = next(row for row in compiler if row["record_kind"] == "binding_rule")
    assert rule["structural_match"] and not rule["selectable"]
    assert len(data["negative-twins.jsonl"]) >= 8
    assert manifest["completion_claim"] is False and manifest["qualified_implementation_count"] == 0
    print("PASS product composition lifecycle: 7 primary/official sources; 4 contexts; 12 no-default decisions; 1 exact unimplemented library; 8 negative twins; 0 qualified implementations")


if __name__ == "__main__":
    main()
