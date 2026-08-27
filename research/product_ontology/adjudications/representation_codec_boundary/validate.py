#!/usr/bin/env python3
"""Validate the representation/codec non-product boundary."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from build_bundle import HERE, OUTPUTS, load_source, materialize
from source_model import SOURCE, source_bytes


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def identity(row: dict) -> str:
    for key in ("source_id", "artifact_id", "decision_id", "meaning_id", "library_id", "requirement_id", "offer_id", "relation_id", "legacy_ref", "test_id", "binding_map_id", "gap_id", "kind"):
        if key in row:
            return str(row[key])
    return "<missing>"


def main() -> int:
    errors: list[str] = []
    require = lambda ok, msg: None if ok else errors.append(msg)
    require(SOURCE.is_file() and SOURCE.read_bytes() == source_bytes(), "source.json differs from source_model.py")
    source = load_source()
    payloads, expected_manifest = materialize(source)
    manifest = json.loads((HERE / "manifest.json").read_text())
    require(manifest == expected_manifest, "manifest projection drift")
    for filename, content in payloads.items():
        require((HERE / filename).is_file() and (HERE / filename).read_bytes() == content, f"stale {filename}")
    for filename, digest in manifest.get("file_sha256", {}).items():
        if (HERE / filename).is_file():
            require(hashlib.sha256((HERE / filename).read_bytes()).hexdigest() == digest, f"digest mismatch {filename}")
    data = {section: rows(HERE / filename) for section, filename in OUTPUTS.items()}
    registry = rows(HERE / "registry.jsonl")
    require(Counter(row["record_kind"] for row in registry) == Counter(manifest["counts"]), "manifest counts differ")
    keys = [(row["record_kind"], identity(row)) for row in registry]
    require(len(keys) == len(set(keys)), "duplicate identity")

    evidence = {row["source_id"]: row for row in data["sources"]}
    artifacts = {row["artifact_id"]: row for row in data["artifacts"]}
    libraries = {row["library_id"]: row for row in data["libraries"]}
    nodes = set(artifacts) | set(libraries)
    require(len(evidence) >= 10, "source floor")
    require(not any(row["kind"] == "product" for row in artifacts.values()), "codec product reappeared")
    require("pattern.codec_as_service" in artifacts and "component.codec_runtime" in artifacts, "pattern/runtime split missing")
    decisions = {row["decision_id"]: row for row in data["boundary_decisions"]}
    decision = decisions.get("decision.rcb.codec_service")
    require(decision is not None and decision["disposition"] == "reclassify_as_library_runtime_component", "codec-service disposition drift")
    for ident, row in artifacts.items():
        require(all(ref in evidence for ref in row.get("evidence_refs", [])), f"bad artifact evidence {ident}")
        owner = row.get("semantic_owner_ref")
        if owner:
            require(owner in artifacts and artifacts[owner]["kind"] == "semantic_contract", f"bad owner {ident}")
    for ident, row in libraries.items():
        require(row["owner_ref"] in artifacts, f"bad library owner {ident}")
        for field in ("provides", "types", "operations", "decisions", "invariants", "refusals"):
            require(bool(row.get(field)), f"empty {field} {ident}")
        require("model_or_agent_output_cannot_select_loss_authority_or_bypass_validation" in row["invariants"], f"agent law missing {ident}")

    compiler_path = HERE.parents[2] / "domain_atlas/compiler/library_registry/library-contributions.jsonl"
    concrete = {row["library_id"] for row in rows(compiler_path)}
    maps = {row["binding_map_id"]: row for row in data["binding_maps"]}
    require(len(libraries) == 8 and len(maps) == 8, "eight library/map boundaries required")
    require({row["abstract_library_ref"] for row in maps.values()} == set(libraries), "map coverage")
    for ident, row in maps.items():
        require(row["compiler_disposition"] == "structurally_projected_unqualified", f"bad map disposition {ident}")
        require(len(row["concrete_library_refs"]) == 1 and row["concrete_library_refs"][0] in concrete, f"unknown compiler library {ident}")
        require(row["portable_offer"] is False and row.get("gap_ref") is None, f"fabricated map claim {ident}")
    require(not data["binding_gaps"], "structural binding gaps reappeared")
    require(len(data["semantic_gaps"]) >= 10 and all(row["blocking"] for row in data["semantic_gaps"]), "gap floor")
    negative_ids = {row["test_id"] for row in data["negative_tests"]}
    require(len(negative_ids) >= 20, "negative floor")
    require({"negative.rcb.codec_product", "negative.rcb.lossy_default", "negative.rcb.agent_select", "negative.rcb.ai_codec"}.issubset(negative_ids), "critical negatives")
    require(manifest["derived"]["product_candidates"] == 0 and manifest["derived"]["qualified_offers"] == 0, "fabricated product/qualification")
    for row in data["relations"]:
        require(row["from_ref"] in nodes and row["to_ref"] in nodes, f"bad relation {row['relation_id']}")
    for row in data["crosswalks"]:
        require(all(ref in nodes for ref in row["canonical_refs"]), f"bad crosswalk {row['legacy_ref']}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"PASS representation/codec boundary: {len(evidence)} sources; 0 products; {len(artifacts)} artifacts; {len(libraries)} libraries; {len(maps)} compiler maps; {len(data['semantic_gaps'])} gaps; {len(data['negative_tests'])} negative twins")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
