#!/usr/bin/env python3
"""Validate the DDD seam doctrine and its first product audit."""

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
    assert len(data["sources.jsonl"]) == 7
    assert {row["kind"] for row in data["boundary-kinds.jsonl"]} == {
        "domain", "subdomain", "bounded_context", "aggregate", "domain_service", "capability",
        "library", "provider", "product", "suite", "solution_pack",
    }
    assert len(data["seam-forces.jsonl"]) == 15
    assert [row["ordinal"] for row in data["seam-discovery-procedure.jsonl"]] == list(range(1, 13))
    negatives = " ".join(row["unsafe_claim"] for row in data["negative-tests.jsonl"])
    for phrase in ["Every reusable library deserves", "Every product is exactly", "Every bounded context must", "Repository, crate", "vendor SKU", "complete upfront ontology"]:
        assert phrase in negatives
    audit = {row["subject_ref"]: row for row in data["metadata-discovery-seam-audit.jsonl"]}
    assert len(audit) == 7 and audit["product.metadata_discovery"]["verdict"] == "retain"
    assert audit["library.metadata_discovery.acquisition_port"]["semantic_owner_ref"] == "context.metadata_discovery.acquisition"
    assert audit["library.metadata_discovery.federation"]["semantic_owner_ref"] == "context.metadata_discovery.federation"
    for suffix in ["assertion_record", "discovery_projection", "search_browse", "freshness_coverage"]:
        assert audit[f"library.metadata_discovery.{suffix}"]["semantic_owner_ref"] == "context.metadata_discovery.catalog"
    assert manifest["completion_claim"] is False
    print("VALIDATION PASS DDD seam doctrine: boundaries stay orthogonal; metadata has 1 product, 3 contexts and 6 libraries")


if __name__ == "__main__":
    main()
