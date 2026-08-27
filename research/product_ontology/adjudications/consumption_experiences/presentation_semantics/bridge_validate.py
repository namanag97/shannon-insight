#!/usr/bin/env python3
"""Validate presentation-semantics bridges against the live Shannon Insight corpus."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
RESEARCH = HERE.parents[3]


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    bridges = rows(HERE / "canonical-bridges.jsonl")
    parent_libraries = {row["library_id"] for row in rows(PARENT / "library-contracts.jsonl")}
    parent_products = {
        row["artifact_id"] for row in rows(PARENT / "artifacts.jsonl")
        if row.get("kind") == "product"
    }
    binding_maps = rows(PARENT / "product-library-binding-maps.jsonl")
    compiler_registry = {
        row["library_id"]
        for row in rows(RESEARCH / "domain_atlas/compiler/library_registry/library-contributions.jsonl")
    }

    errors: list[str] = []
    expected_products = {
        "product.bi_reporting",
        "product.embedded_analytics",
        "product.analytical_notebook",
    }
    if not expected_products.issubset(parent_products):
        errors.append(f"parent product set missing expected presentation consumers: {sorted(expected_products - parent_products)}")

    mapped_parent_libraries = {row["abstract_library_ref"] for row in binding_maps}
    for bridge in bridges:
        parent_ref = bridge["parent_consumption_library_ref"]
        compiler_refs = bridge["compiler_library_refs"]
        if parent_ref is None:
            if compiler_refs:
                errors.append(f"vacancy fabricates compiler refs {bridge['canonical_bridge_id']}")
            if bridge["status"] != "candidate_vacancy_requires_parent_adjudication":
                errors.append(f"vacancy status drift {bridge['canonical_bridge_id']}")
            continue
        if parent_ref not in parent_libraries:
            errors.append(f"unknown parent consumption library {bridge['canonical_bridge_id']}:{parent_ref}")
        if parent_ref not in mapped_parent_libraries:
            errors.append(f"parent library lacks canonical compiler binding map {bridge['canonical_bridge_id']}:{parent_ref}")
        for compiler_ref in compiler_refs:
            if compiler_ref not in compiler_registry:
                errors.append(f"unknown compiler library {bridge['canonical_bridge_id']}:{compiler_ref}")
        if bridge["status"] != "projects_to_existing_parent_contract_unqualified":
            errors.append(f"existing bridge status drift {bridge['canonical_bridge_id']}")
        if bridge["ratified"] or bridge["qualified"]:
            errors.append(f"bridge fabricates authority {bridge['canonical_bridge_id']}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    existing = sum(1 for row in bridges if row["parent_consumption_library_ref"])
    vacancies = len(bridges) - existing
    print(
        "PASS presentation-semantics canonical bridge: "
        f"{existing} candidate seams project to existing consumption/compiler contracts; "
        f"{vacancies} remain explicit parent-adjudication vacancies; 0 ratified/qualified bridges"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
