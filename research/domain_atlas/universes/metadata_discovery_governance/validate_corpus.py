#!/usr/bin/env python3
"""Validate metadata-discovery exact contracts and DDD boundary correction."""

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
    data = {name:load(name) for name in build_corpus.FILES}
    for name, rows in data.items():
        assert manifest["files"][name]["records"] == len(rows)
        assert manifest["files"][name]["sha256"] == hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    assert len(data["sources.jsonl"]) == 15 and all(row["url"].startswith("https://") for row in data["sources.jsonl"])
    contexts = {row["context_id"] for row in data["bounded-contexts.jsonl"]}
    assert contexts == {"context.metadata_discovery.acquisition", "context.metadata_discovery.catalog", "context.metadata_discovery.federation"}
    decisions = data["decision-points.jsonl"]
    assert len(decisions) == 30 and all(row["default"] is None and row["default_law"] == "forbidden" for row in decisions)
    libs = data["library-contracts.jsonl"]
    assert len(libs) == 6 and len({row["library_id"] for row in libs}) == 6
    decision_ids = {row["decision_id"] for row in decisions}
    for lib in libs:
        assert len(lib["public_types"]) >= 16 and len(lib["operations"]) == 4
        assert set(lib["operation_refs"]) == {op["operation_ref"] for op in lib["operations"]}
        assert set(lib["decision_refs"]) <= decision_ids and len(lib["decision_refs"]) == 5
        assert all(op["input_types"] and op["output_type"].startswith("Result<") for op in lib["operations"])
    owners = {row["library_id"]:row["semantic_owner_context"] for row in libs}
    assert owners["library.metadata_discovery.acquisition_port"] == "context.metadata_discovery.acquisition"
    assert owners["library.metadata_discovery.federation"] == "context.metadata_discovery.federation"
    for suffix in ["assertion_record", "discovery_projection", "search_browse", "freshness_coverage"]:
        assert owners[f"library.metadata_discovery.{suffix}"] == "context.metadata_discovery.catalog"
    kinds = {row["library_id"]:row["effect_boundary"] for row in libs}
    assert kinds["library.metadata_discovery.freshness_coverage"] == "pure_no_io"
    assert all(kinds[f"library.metadata_discovery.{suffix}"] == "pure_effect_intents" for suffix in ["acquisition_port","assertion_record","discovery_projection","search_browse","federation"])
    laws = " ".join(law for lib in libs for law in lib["laws"]).lower()
    for phrase in ["harvest attempt, extraction receipt", "absence from one extraction is not deletion", "observed, declared, inferred", "catalog record, cataloged resource", "match, score, rank", "global last-write-wins", "configured schedule is not", "slo pass"]:
        assert phrase in laws, phrase
    offers = [row for row in data["compiler-contracts.jsonl"] if row["record_kind"] == "capability_offer"]
    assert len(data["compiler-contracts.jsonl"]) == 18 and len(offers) == 6
    assert all(not row["portable"] and not row["selectable"] and row["qualified_implementation_count"] == 0 for row in offers)
    assert len(data["negative-twins.jsonl"]) == 14 and manifest["completion_claim"] is False
    print("VALIDATION PASS metadata discovery: 1 product projection, 3 contexts, 6 exact libraries, 30 no-default decisions, 0 qualified offers")


if __name__ == "__main__":
    main()
