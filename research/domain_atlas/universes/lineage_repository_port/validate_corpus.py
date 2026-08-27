#!/usr/bin/env python3
"""Validate the exact lineage repository port and its authority boundaries."""

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
    assert len(data["sources.jsonl"]) == 17 and all(row["url"].startswith("https://") for row in data["sources.jsonl"])
    assert [row["context_id"] for row in data["bounded-contexts.jsonl"]] == ["context.lineage_repository.persistence"]
    decisions = data["decision-points.jsonl"]
    assert len(decisions) == 16 and all(row["default"] is None and row["default_law"] == "forbidden" for row in decisions)
    library = data["library-contracts.jsonl"][0]
    assert library["library_id"] == "library.lineage_repository.port"
    assert library["effect_boundary"] == "pure_effect_intents" and len(library["operations"]) == 13
    assert len(library["public_types"]) >= 65 and len(library["decision_refs"]) == 16
    assert set(library["operation_refs"]) == {op["operation_ref"] for op in library["operations"]}
    assert all(op["input_types"] and op["output_type"].startswith("Result<") and op["purity"] == "pure" for op in library["operations"])
    assert {
        "library.lpe.prov-statement-algebra",
        "library.lpe.provenance-assertion",
        "library.lpe.provenance-bundle",
    } <= set(library["dependencies"])
    assert not ({"lineage vocabulary, relation semantics or graph-query inference", "assertion truth, semantic acceptance or causal claims", "capture or query completeness", "identity, policy, retention, disclosure, hold or erasure authority", "evidence admissibility or relying decisions", "physical provider implementation or provider qualification"} - set(library["must_not_own"]))
    laws = " ".join(library["laws"]).lower()
    for phrase in ["assertion identity, assertion edition", "append intent, dispatch", "recording time, commit time", "not found, hidden by policy", "retention, legal hold", "repository substitution requires"]:
        assert phrase in laws, phrase
    offers = [row for row in data["compiler-contracts.jsonl"] if row["record_kind"] == "capability_offer"]
    assert len(data["compiler-contracts.jsonl"]) == 3 and len(offers) == 1
    assert offers[0]["qualified_implementation_count"] == 0 and not offers[0]["portable"] and not offers[0]["selectable"]
    assert len(data["negative-twins.jsonl"]) == 20 and manifest["completion_claim"] is False
    print("VALIDATION PASS lineage repository port: 1 context, 1 exact library, 16 no-default decisions, 13 pure operations, 0 qualified offers")


if __name__ == "__main__":
    main()
