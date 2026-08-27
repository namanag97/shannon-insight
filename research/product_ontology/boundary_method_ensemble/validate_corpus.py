#!/usr/bin/env python3
"""Validate method coverage and non-collapse laws."""

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
    methods = data["methods.jsonl"]
    assert len(methods) >= 70 and len({row["method_id"] for row in methods}) == len(methods)
    expected_families = {"strategy_landscape","business_product","domain_semantics","work_behavior","information_semantics","architecture_structure","reuse_variability","formal_verification","trust_operations","empirical_evidence","analytical_formulation"}
    assert {row["family"] for row in methods} == expected_families
    assert all(row["primary_question"] and row["outputs"] and row["seam_evidence_for"] and row["not_proof_of"] for row in methods)
    assert len(data["required-lenses.jsonl"]) == 12
    assert all(row["default_if_missing"] == "UNDETERMINED_NOT_PASS" for row in data["required-lenses.jsonl"])
    tri = data["metadata-discovery-triangulation.jsonl"]
    assert len(tri) == 6 and all(len(row["supporting_methods"]) >= 4 and row["residual"] for row in tri)
    assert set(method for row in tri for method in row["supporting_methods"]) <= {row["method_id"] for row in methods}
    assert manifest["completion_claim"] is False
    print(f"VALIDATION PASS boundary ensemble: {len(methods)} methods across {len(expected_families)} families; missing lens fails closed")


if __name__ == "__main__":
    main()
