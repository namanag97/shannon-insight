#!/usr/bin/env python3
"""Validate exact data-marketplace contracts and ownership boundaries."""

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
    assert len(data["sources.jsonl"]) == 19 and all(row["url"].startswith("https://") for row in data["sources.jsonl"])
    contexts = {row["context_id"] for row in data["bounded-contexts.jsonl"]}
    assert contexts == {"context.data_marketplace.merchandising", "context.data_marketplace.acquisition", "context.data_marketplace.evidence"}
    decisions = data["decision-points.jsonl"]
    assert len(decisions) == 36 and all(row["default"] is None and row["default_law"] == "forbidden" for row in decisions)
    decision_ids = {row["decision_id"] for row in decisions}
    libraries = data["library-contracts.jsonl"]
    assert len(libraries) == 6 and len({row["library_id"] for row in libraries}) == 6
    for library in libraries:
        assert len(library["public_types"]) >= 19 and len(library["operations"]) == 4
        assert set(library["operation_refs"]) == {op["operation_ref"] for op in library["operations"]}
        assert len(library["decision_refs"]) == 6 and set(library["decision_refs"]) <= decision_ids
        assert all(op["input_types"] and op["output_type"].startswith("Result<") and op["purity"] == "pure" for op in library["operations"])
        assert not ({"data-product publication or source truth", "identity, credential, purpose or policy authority", "business approval or legal agreement authority", "entitlement, provisioning, access, transfer or delivery effects", "usage-metering, invoice, settlement or accounting truth", "consumer fitness, acceptance or outcome truth"} - set(library["must_not_own"]))
    owners = {row["library_id"]: row["semantic_owner_context"] for row in libraries}
    assert owners["library.data_marketplace.offer_listing"] == owners["library.data_marketplace.discovery_ranking"] == "context.data_marketplace.merchandising"
    for suffix in ["eligibility_broker", "subscription_case", "fulfillment_handoff"]:
        assert owners[f"library.data_marketplace.{suffix}"] == "context.data_marketplace.acquisition"
    assert owners["library.data_marketplace.terms_usage_evidence"] == "context.data_marketplace.evidence"
    boundaries = {row["library_id"]: row["effect_boundary"] for row in libraries}
    assert boundaries["library.data_marketplace.discovery_ranking"] == boundaries["library.data_marketplace.eligibility_broker"] == "pure_no_io"
    for suffix in ["offer_listing", "subscription_case", "fulfillment_handoff", "terms_usage_evidence"]:
        assert boundaries[f"library.data_marketplace.{suffix}"] == "pure_effect_intents"
    laws = " ".join(law for library in libraries for law in library["laws"]).lower()
    for phrase in ["data product, published product edition", "catalog membership, visibility", "credential verification proves", "approval dispatch or receipt is not approval", "approved request, agreement, fulfillment intent", "usage observation, metered quantity"]:
        assert phrase in laws, phrase
    compiler = data["compiler-contracts.jsonl"]
    offers = [row for row in compiler if row["record_kind"] == "capability_offer"]
    assert len(compiler) == 18 and len(offers) == 6
    assert all(not row["portable"] and not row["selectable"] and row["qualified_implementation_count"] == 0 for row in offers)
    assert len(data["negative-twins.jsonl"]) == 20 and manifest["completion_claim"] is False
    print("VALIDATION PASS data marketplace: 1 product projection, 3 contexts, 6 exact libraries, 36 no-default decisions, 0 qualified offers")


if __name__ == "__main__":
    main()
