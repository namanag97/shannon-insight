#!/usr/bin/env python3
"""Build deterministic materialized views for the movement adjudication corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source.json"

SECTIONS: dict[str, tuple[str, str]] = {
    "sources": ("evidence_source", "source_id"),
    "artifact_kinds": ("artifact_kind_definition", "kind"),
    "artifacts": ("artifact", "artifact_id"),
    "boundary_decisions": ("boundary_decision", "decision_id"),
    "ownership": ("semantic_ownership", "meaning_id"),
    "libraries": ("library_contract", "library_id"),
    "requirements": ("capability_requirement", "requirement_id"),
    "offers": ("capability_offer", "offer_id"),
    "relations": ("relation", "relation_id"),
    "crosswalks": ("legacy_crosswalk", "legacy_ref"),
    "negative_tests": ("negative_test", "test_id"),
}

OUTPUTS = {
    "sources": "evidence.jsonl",
    "artifact_kinds": "artifact-kinds.jsonl",
    "artifacts": "artifacts.jsonl",
    "boundary_decisions": "boundary-decisions.jsonl",
    "ownership": "semantic-ownership.jsonl",
    "libraries": "library-contracts.jsonl",
    "requirements": "requirements.jsonl",
    "offers": "offers.jsonl",
    "relations": "relations.jsonl",
    "crosswalks": "legacy-crosswalks.jsonl",
    "negative_tests": "negative-tests.jsonl",
}

MOVEMENT_SECTIONS = {
    **SECTIONS,
    "binding_maps": ("product_library_binding_map", "binding_map_id"),
    "binding_gaps": ("product_library_binding_gap", "gap_id"),
    "ddd_dossiers": ("product_ddd_dossier", "dossier_id"),
}

MOVEMENT_OUTPUTS = {
    **OUTPUTS,
    "binding_maps": "product-library-binding-maps.jsonl",
    "binding_gaps": "product-library-binding-gaps.jsonl",
    "ddd_dossiers": "product-ddd-dossiers.jsonl",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def jsonl_bytes(rows: list[dict[str, Any]]) -> bytes:
    return ("".join(canonical_json(row) + "\n" for row in rows)).encode()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_source() -> dict[str, Any]:
    value = json.loads(SOURCE.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("source.json must contain an object")
    return value


def _materialize(
    source: dict[str, Any],
    sections: dict[str, tuple[str, str]],
    outputs: dict[str, str],
) -> tuple[dict[str, bytes], dict[str, Any]]:
    edition = source["edition"]
    partitions: dict[str, list[dict[str, Any]]] = {}
    registry: list[dict[str, Any]] = []
    for section, (record_kind, identity_key) in sections.items():
        rows = [{"record_kind": record_kind, "edition": edition, **raw} for raw in source[section]]
        rows.sort(key=lambda row: str(row[identity_key]))
        partitions[section] = rows
        registry.extend(rows)
    registry.sort(key=lambda row: (row["record_kind"], canonical_json(row)))

    metamodel = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://san.example/spec/{HERE.name}-adjudication-metamodel-v0.1.0.json",
        "contract_id": source["contract_id"],
        "edition": edition,
        "status": source["status"],
        "record_kinds": {
            record_kind: {"source_section": section, "identity_key": identity_key}
            for section, (record_kind, identity_key) in sections.items()
        },
        "artifact_kinds": {row["kind"]: row for row in source["artifact_kinds"]},
        "split_test_axes": [
            "user", "job", "adoption", "semantics", "authority",
            "lifecycle", "operation", "economics", "interface", "market_evidence",
        ],
        "split_test_verdicts": {
            "merge_or_reclassify": [0, 6],
            "defer": [7, 12],
            "presumptive_product": [13, 16],
            "strong_product_candidate": [17, 20],
        },
        "relation_predicates": [
            "packaged_as", "packages", "offers", "requires", "governed_by",
            "specializes", "implements", "realizes",
        ],
        "binding_phases": [
            "authoring", "compile_time", "deployment_time", "runtime", "qualification_time",
        ],
        "non_collapse_laws": source.get("non_collapse_laws", [
            "pipeline pattern != suite != product",
            "connector plugin != provider offer != product",
            "source cursor != transport offset != delivery cursor != workflow logical date",
            "orchestration task success != data correctness or delivery commit",
            "operator-state exactly-once != end-to-end external-effect exactly-once",
            "transport envelope does not own payload meaning",
            "movement does not acquire source-system business authority",
            "observed lineage != causal influence",
            "analytical row != authorized operational effect",
            "ETL/ELT topology != product identity",
            "optional model or agent assistance does not create semantic ownership or effect authority",
        ]),
    }

    payloads: dict[str, bytes] = {
        outputs[section]: jsonl_bytes(rows) for section, rows in partitions.items()
    }
    payloads["registry.jsonl"] = jsonl_bytes(registry)
    payloads["metamodel.json"] = json_bytes(metamodel)

    manifest = {
        "contract_id": source["contract_id"],
        "edition": edition,
        "status": source["status"],
        "scope": source["scope"],
        "negative_scope": source["negative_scope"],
        "source_sha256": digest(SOURCE.read_bytes()),
        "counts": dict(sorted(Counter(row["record_kind"] for row in registry).items())),
        "derived": {
            "product_candidates": sum(row["kind"] == "product" for row in source["artifacts"]),
            "portable_offers": sum(row["portable"] for row in source["offers"]),
            "qualified_offers": sum(row["qualified_implementation_count"] > 0 for row in source["offers"]),
            "unbound_requirements": sum(row["status"] == "unbound" for row in source["requirements"]),
            "legacy_crosswalks": len(source["crosswalks"]),
        },
        "file_sha256": {filename: digest(data) for filename, data in sorted(payloads.items())},
    }
    payloads["manifest.json"] = json_bytes(manifest)
    return payloads, manifest


def materialize(source: dict[str, Any]) -> tuple[dict[str, bytes], dict[str, Any]]:
    """Shared base materializer used by older adjudication bundles."""
    return _materialize(source, SECTIONS, OUTPUTS)


def movement_materialize(source: dict[str, Any]) -> tuple[dict[str, bytes], dict[str, Any]]:
    """Movement materializer with product DDD and compiler-map projections."""
    return _materialize(source, MOVEMENT_SECTIONS, MOVEMENT_OUTPUTS)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="refuse if generated files differ")
    args = parser.parse_args()
    payloads, manifest = (
        movement_materialize(load_source())
        if HERE.name == "movement"
        else materialize(load_source())
    )
    changed = []
    for filename, data in sorted(payloads.items()):
        path = HERE / filename
        if not path.exists() or path.read_bytes() != data:
            changed.append(filename)
            if not args.check:
                path.write_bytes(data)
    if args.check and changed:
        print("STALE generated files: " + ", ".join(changed))
        return 1
    print(canonical_json({"counts": manifest["counts"], "derived": manifest["derived"], "status": "PASS"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
