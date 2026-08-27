#!/usr/bin/env python3
"""Dependency-free integrity validator with optional Draft 2020-12 validation."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ATLAS = ROOT.parents[1]
COLLECTIONS = [
    "providers.jsonl", "products.jsonl", "implementation-artifacts.jsonl", "documented-offers.jsonl",
    "product-source-surfaces.jsonl", "occurrence-templates.jsonl", "compiler-requirements.jsonl",
    "requirement-offer-mappings.jsonl", "protocol-class-crosswalks.jsonl", "adapter-library-boundaries.jsonl",
    "library-semantic-contracts.jsonl",
    "qualification-probes.jsonl", "official-sources.jsonl", "innovations-2021-2026.jsonl",
    "negative-twins.jsonl", "gaps.jsonl",
]


def rows(name: str) -> list[dict]:
    result = []
    for no, line in enumerate((ROOT / name).read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            result.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise AssertionError(f"{name}:{no}: invalid JSON: {exc}") from exc
    return result


def ids(path: Path, key: str) -> set[str]:
    return {json.loads(line)[key] for line in path.read_text().splitlines() if line.strip()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schemas", action="store_true")
    args = parser.parse_args()

    manifest = json.loads((ROOT / "manifest.json").read_text())
    data = {name: rows(name) for name in COLLECTIONS}
    all_rows = [row for group in data.values() for row in group]
    all_ids = [row["record_id"] for row in all_rows]
    assert len(all_ids) == len(set(all_ids)), "record IDs are not globally unique"

    source_classes = ids(ATLAS / "universes/source_systems/source-classes.jsonl", "class_id")
    protocols = ids(ATLAS / "universes/connectors_protocols/protocols.jsonl", "protocol_id")
    providers = {r["record_id"] for r in data["providers.jsonl"]}
    products = {r["record_id"] for r in data["products.jsonl"]}
    artifacts = {r["record_id"] for r in data["implementation-artifacts.jsonl"]}
    offers = {r["record_id"] for r in data["documented-offers.jsonl"]}
    surfaces = {r["record_id"] for r in data["product-source-surfaces.jsonl"]}
    occurrences = {r["record_id"] for r in data["occurrence-templates.jsonl"]}
    requirements = {r["record_id"] for r in data["compiler-requirements.jsonl"]}
    evidence = {r["record_id"] for r in data["official-sources.jsonl"]}

    assert len(source_classes) == 171
    assert {r["source_class_ref"] for r in data["product-source-surfaces.jsonl"]} == source_classes
    assert {r["protocol_ref"] for r in data["protocol-class-crosswalks.jsonl"]} == protocols
    assert len(data["official-sources.jsonl"]) >= 180
    assert len({r["url"] for r in data["official-sources.jsonl"]}) >= 180
    assert len(providers) + len(products) + len(artifacts) >= 300
    assert len(data["adapter-library-boundaries.jsonl"]) >= 50
    assert len(data["library-semantic-contracts.jsonl"]) == 1
    assert len(data["innovations-2021-2026.jsonl"]) >= 30
    assert len(data["gaps.jsonl"]) >= 30
    assert len(data["negative-twins.jsonl"]) >= 30

    forbidden_hosts = ("wikipedia.org", "reddit.com", "medium.com")
    for row in data["official-sources.jsonl"]:
        assert row["authority"] == "primary"
        assert row["url"].startswith("https://")
        assert not any(host in row["url"] for host in forbidden_hosts)
        assert "does not prove" in row["use_limit"].lower() or "supports the named" in row["use_limit"].lower()

    for row in data["products.jsonl"]:
        assert row["provider_ref"] in providers
        assert set(row["candidate_source_class_refs"]) <= source_classes
        assert set(row["candidate_protocol_refs"]) <= protocols
        assert row["conformance_status"] == "unproven_until_occurrence_qualification"
        assert set(row["evidence_refs"]) <= evidence
    for row in data["implementation-artifacts.jsonl"]:
        assert row["product_ref"] in products
        assert not row["compiler_bindable"]
        assert row["digest"] is None
        assert set(row["source_class_refs"]) <= source_classes
        assert set(row["protocol_refs"]) <= protocols
    for row in data["documented-offers.jsonl"]:
        assert row["product_ref"] in products
        assert not row["compiler_bindable"]
    for row in data["product-source-surfaces.jsonl"]:
        assert row["product_ref"] in products and row["offer_ref"] in offers
        assert row["source_class_ref"] in source_classes
        assert set(row["protocol_refs"]) <= protocols
        assert row["mapping_confidence"] == "candidate_not_conformance"
    for row in data["occurrence-templates.jsonl"]:
        assert row["product_ref"] in products and row["offer_ref"] in offers and row["artifact_ref"] in artifacts
        assert row["source_class_ref"] in source_classes
        assert row["probe_receipts"] == [] and not row["compiler_bindable"]
        assert row["deployment_identity"]["exact_version_or_build"] == "required"
        assert row["security"]["credential_ref"] == "required_reference_only"
    for row in data["requirement-offer-mappings.jsonl"]:
        assert row["requirement_ref"] in requirements and row["offer_ref"] in offers
        assert row["surface_ref"] in surfaces and row["occurrence_template_ref"] in occurrences
        assert not row["compiler_bindable"] and len(row["required_receipts"]) >= 40
    for row in data["protocol-class-crosswalks.jsonl"]:
        assert row["protocol_ref"] in protocols and set(row["source_class_refs"]) <= source_classes
        assert "business semantics" in row["does_not_establish"]

    cursor = data["library-semantic-contracts.jsonl"][0]
    assert cursor["library_id"] == "library.source.source_cursor"
    assert cursor["semantic_owner_context"] == "ctx.source.source_cursor"
    assert cursor["effect_boundary"] == "pure_no_io"
    assert len(cursor["decision_refs"]) == len(cursor["decisions"]) == 8
    assert all(row["default"] is None and row["default_law"] == "forbidden" for row in cursor["decisions"])
    assert len(cursor["public_types"]) >= 12 and len(cursor["operation_refs"]) >= 7
    assert {row["operation_ref"] for row in cursor["operations"]} == set(cursor["operation_refs"])
    assert len({row["output_type"] for row in cursor["operations"]}) >= 5
    assert any("paging token is not a CDC resume token" in law for law in cursor["laws"])
    assert any("durable processing checkpoint" in law for law in cursor["laws"])

    # No generated artifact may contain credentials or silently claim completion/qualification.
    serialized = json.dumps(all_rows, sort_keys=True).lower()
    assert "api_key_value" not in serialized and "password_value" not in serialized and "secret_value" not in serialized
    assert not any(r.get("status") in {"complete", "qualified", "conformant"} for r in all_rows)
    assert manifest["credentials_collected"] == 0 and manifest["real_live_probes"] == 0
    assert manifest["completion_claim"] is False and manifest["open_world"] is True

    for name in COLLECTIONS:
        info = manifest["files"][name]
        assert info["records"] == len(data[name]), f"manifest record count drift: {name}"
        assert info["sha256"] == hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), f"digest drift: {name}"

    if args.schemas:
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            print("ERROR --schemas requested but jsonschema is unavailable", file=sys.stderr)
            return 2
        schema = json.loads((ROOT / "schemas/record.schema.json").read_text())
        validator = Draft202012Validator(schema)
        for name, group in data.items():
            for index, row in enumerate(group, start=1):
                errors = sorted(validator.iter_errors(row), key=lambda e: list(e.path))
                assert not errors, f"{name}:{index}: {errors[0].message}"

    print(
        "PASS source occurrence catalog: "
        f"{len(source_classes)} source classes; {len(protocols)} protocol crosswalks; "
        f"{len(products)} products; {len(artifacts)} artifacts; {len(occurrences)} templates; "
        f"{len(data['official-sources.jsonl'])} official sources; "
        f"{len(data['adapter-library-boundaries.jsonl'])} adapter boundaries; "
        "0 live probes / 0 credentials / 0 bindable occurrences"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
