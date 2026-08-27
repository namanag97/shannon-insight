#!/usr/bin/env python3
"""Validate the industry-foundation corpus without third-party dependencies."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
ID_RE = re.compile(r"^[a-z][a-z0-9]*(\.[a-z][a-z0-9_-]*)+$")
EXPECTED_SOURCE_SHA = "fc408f57bd3a4f33c35a4f384ec0010283dd72774892c8d48ae1330a8caeb57f"
EXPECTED_NODE_SHA = "95c56251dc356d7810a9de4f30e5bdc32d54b0b0d200adf3270a0c998042709d"
EXPECTED_LEVEL_COUNTS = {"section": 22, "division": 87, "group": 258, "class": 463}


class ValidationError(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def read_json(name: str) -> Any:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def read_jsonl(name: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for lineno, line in enumerate((ROOT / name).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"{name}:{lineno}: {exc}") from exc
        require(isinstance(value, dict), f"{name}:{lineno}: record is not an object")
        rows.append(value)
    return rows


def require_fields(record: dict[str, Any], fields: set[str], label: str) -> None:
    missing = sorted(fields - record.keys())
    require(not missing, f"{label}: missing fields {missing}")


def validate_sources(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    required = {
        "record_id", "record_kind", "edition", "status", "title", "publisher", "source_kind",
        "url", "supports", "authority_scope", "limitations", "accessed_at"
    }
    allowed_status = {"candidate", "verified", "stale", "rejected"}
    allowed_kind = {
        "standard", "regulator", "official_statistics", "professional_body", "academic",
        "official_implementation", "incident", "industry_primary"
    }
    require(len(rows) >= 25, f"source gate: {len(rows)} < 25")
    require(len({row["publisher"] for row in rows}) >= 10, "source gate: fewer than 10 publishers")
    index: dict[str, dict[str, Any]] = {}
    for i, row in enumerate(rows, 1):
        label = f"sources.jsonl:{i}"
        require_fields(row, required, label)
        rid = row["record_id"]
        require(ID_RE.fullmatch(rid) is not None, f"{label}: invalid id {rid}")
        require(rid not in index, f"{label}: duplicate id {rid}")
        require(row["record_kind"] == "source_evidence", f"{label}: wrong record_kind")
        require(row["status"] in allowed_status, f"{label}: invalid status")
        require(row["source_kind"] in allowed_kind, f"{label}: invalid source_kind")
        require(row["url"].startswith("https://"), f"{label}: source URL is not HTTPS")
        require(bool(row["supports"]), f"{label}: supports is empty")
        require(len(row["supports"]) == len(set(row["supports"])), f"{label}: duplicate supports")
        require(len(row["limitations"]) == len(set(row["limitations"])), f"{label}: duplicate limitations")
        index[rid] = row
    structure = index.get("source.un.isic.rev5.structure")
    require(structure is not None, "missing official ISIC Revision 5 structure source")
    require(structure.get("content_sha256") == EXPECTED_SOURCE_SHA, "unexpected ISIC source digest")
    return index


def validate_schemes(rows: list[dict[str, Any]], sources: dict[str, dict[str, Any]]) -> set[str]:
    required = {
        "scheme_id", "scheme_series_id", "record_kind", "edition", "status", "name", "custodian",
        "scheme_kind", "concept_classified", "statistical_unit", "geographic_scope",
        "temporal_validity", "hierarchy", "assignment_rules", "atlas_role", "source_refs",
        "official_crosswalks", "limitations"
    }
    ids: set[str] = set()
    for i, row in enumerate(rows, 1):
        label = f"classification-schemes.json[{i}]"
        require_fields(row, required, label)
        rid = row["scheme_id"]
        require(ID_RE.fullmatch(rid) is not None, f"{label}: invalid scheme id {rid}")
        require(ID_RE.fullmatch(row["scheme_series_id"]) is not None, f"{label}: invalid series id")
        require(rid not in ids, f"{label}: duplicate scheme id {rid}")
        require(row["record_kind"] == "classification_scheme", f"{label}: wrong record_kind")
        require(bool(row["geographic_scope"]), f"{label}: empty geography")
        require(bool(row["hierarchy"]["levels"]), f"{label}: empty hierarchy")
        require(bool(row["assignment_rules"]), f"{label}: empty assignment rules")
        require(bool(row["source_refs"]), f"{label}: empty source refs")
        for ref in row["source_refs"]:
            require(ref in sources, f"{label}: unknown source ref {ref}")
        for artifact in row["official_crosswalks"]:
            require(artifact["source_ref"] in sources, f"{label}: unknown crosswalk source")
        ids.add(rid)
    require("scheme.un.isic.rev5" in ids, "missing ISIC Revision 5 scheme")
    require(sum(r["atlas_role"] == "jurisdictional_activity_view" for r in rows) >= 5,
            "fewer than five jurisdictional activity views")
    require(sum(r["atlas_role"] == "specialist_analytical_overlay" for r in rows) >= 10,
            "fewer than ten specialist overlays")
    return ids


def validate_nodes(rows: list[dict[str, Any]], sources: dict[str, dict[str, Any]]) -> set[str]:
    require(len(rows) == 830, f"ISIC node count {len(rows)} != 830")
    counts = Counter(row.get("level") for row in rows)
    require(dict(counts) == EXPECTED_LEVEL_COUNTS, f"ISIC level counts {dict(counts)}")
    digest = hashlib.sha256((ROOT / "isic-rev5.nodes.jsonl").read_bytes()).hexdigest()
    require(digest == EXPECTED_NODE_SHA, f"generated node digest changed: {digest}")
    index: dict[str, dict[str, Any]] = {}
    code_index: dict[tuple[str, str], str] = {}
    for i, row in enumerate(rows, 1):
        label = f"isic-rev5.nodes.jsonl:{i}"
        rid = row["record_id"]
        require(ID_RE.fullmatch(rid) is not None, f"{label}: invalid id")
        require(rid not in index, f"{label}: duplicate id {rid}")
        require(row["source_sha256"] == EXPECTED_SOURCE_SHA, f"{label}: source digest mismatch")
        require(row["source_refs"] == ["source.un.isic.rev5.structure"], f"{label}: wrong source")
        require(row["source_refs"][0] in sources, f"{label}: unknown source")
        key = (row["level"], row["scheme_code"])
        require(key not in code_index, f"{label}: duplicate level/code {key}")
        code_index[key] = rid
        index[rid] = row

    children: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        parent = row["parent_id"]
        if row["level"] == "section":
            require(parent is None and row["ancestor_ids"] == [], f"{row['record_id']}: invalid root")
        else:
            require(parent in index, f"{row['record_id']}: unknown parent {parent}")
            parent_row = index[parent]
            require(parent_row["level_ordinal"] + 1 == row["level_ordinal"],
                    f"{row['record_id']}: parent skips hierarchy level")
            require(row["ancestor_ids"][-1] == parent, f"{row['record_id']}: last ancestor is not parent")
            expected_ancestors = parent_row["ancestor_ids"] + [parent]
            require(row["ancestor_ids"] == expected_ancestors, f"{row['record_id']}: ancestor chain mismatch")
            children[parent].append(row["record_id"])
    for row in rows:
        actual = len(children[row["record_id"]])
        require(row["child_count"] == actual, f"{row['record_id']}: child count mismatch")
        require(row["is_leaf"] == (actual == 0), f"{row['record_id']}: leaf flag mismatch")
    require(all(index[rid]["level"] == "class" for rid in index if index[rid]["is_leaf"]),
            "non-class leaf found in ISIC hierarchy")
    return set(index)


def validate_crosswalks(
    rows: list[dict[str, Any]], sources: dict[str, dict[str, Any]], schemes: set[str], nodes: set[str]
) -> None:
    dimensions = {"concept", "statistical_unit", "geography", "time", "inclusions_exclusions"}
    reviewed_status = {"reviewed", "adjudicated"}
    for i, row in enumerate(rows, 1):
        label = f"crosswalks.jsonl:{i}"
        require(row["record_kind"] == "crosswalk_assertion", f"{label}: wrong kind")
        require(ID_RE.fullmatch(row["record_id"]) is not None, f"{label}: invalid id")
        require(bool(row["source_members"]) and bool(row["target_members"]), f"{label}: empty members")
        for member in row["source_members"] + row["target_members"]:
            require(member["scheme_edition_id"] in schemes, f"{label}: unknown scheme {member['scheme_edition_id']}")
            if member.get("node_id") is not None:
                require(member["node_id"] in nodes, f"{label}: unknown node {member['node_id']}")
        require(set(row["dimension_assessment"]) == dimensions, f"{label}: incomplete dimensions")
        require(bool(row["evidence_refs"]), f"{label}: no evidence")
        for ref in row["evidence_refs"]:
            require(ref in sources, f"{label}: unknown evidence {ref}")
        if row["status"] in reviewed_status:
            require(row["review"]["classification_reviewer"] is not None, f"{label}: no classification reviewer")
            require(row["review"]["domain_reviewer"] is not None, f"{label}: no domain reviewer")
            require(row["review"]["reviewed_at"] is not None, f"{label}: no review date")
        if row["relation"] != "equivalent_extent":
            require(row["transitive_use"] == "forbidden", f"{label}: non-equivalent relation made transitive")
        if row["allocation"]["weight_semantics"] == "official":
            require(row["allocation"]["weight_source_ref"] in sources, f"{label}: official weight lacks source")


def validate_claims(rows: list[dict[str, Any]], sources: dict[str, dict[str, Any]]) -> None:
    for i, row in enumerate(rows, 1):
        label = f"claims.jsonl:{i}"
        require(row["record_kind"] == "evidence_claim", f"{label}: wrong kind")
        require(ID_RE.fullmatch(row["record_id"]) is not None, f"{label}: invalid id")
        require(bool(row["support"]), f"{label}: unsupported claim")
        for support in row["support"]:
            require(support["source_ref"] in sources, f"{label}: unknown source {support['source_ref']}")
            require(bool(support["locator"].strip()), f"{label}: empty locator")
        if row["status"] == "verified":
            require(row["review"]["reviewer"] is not None, f"{label}: verified without reviewer")
            require(row["review"]["reviewed_at"] is not None, f"{label}: verified without date")


def validate_json_schemas(
    source_rows: list[dict[str, Any]],
    scheme_rows: list[dict[str, Any]],
    node_rows: list[dict[str, Any]],
    crosswalk_rows: list[dict[str, Any]],
    claim_rows: list[dict[str, Any]],
) -> None:
    try:
        import jsonschema
    except ImportError as exc:
        raise ValidationError("--schemas requires the jsonschema package") from exc

    schema_sets = [
        (
            source_rows,
            json.loads((ROOT.parent / "schema" / "industry-research-record.schema.json").read_text()),
            "shared source-evidence schema",
        ),
        (scheme_rows, read_json("schema/classification-scheme.schema.json"), "classification scheme schema"),
        (node_rows, read_json("schema/industry-taxonomy-node.schema.json"), "industry node schema"),
        (crosswalk_rows, read_json("schema/crosswalk-assertion.schema.json"), "crosswalk schema"),
        (claim_rows, read_json("schema/evidence-claim.schema.json"), "evidence claim schema"),
    ]
    format_checker = jsonschema.FormatChecker()
    for rows, schema, label in schema_sets:
        validator = jsonschema.Draft202012Validator(schema, format_checker=format_checker)
        for i, row in enumerate(rows, 1):
            errors = sorted(validator.iter_errors(row), key=lambda error: list(error.path))
            require(not errors, f"{label} record {i}: {errors[0].message if errors else ''}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schemas", action="store_true", help="also run JSON Schema validation (requires jsonschema)")
    args = parser.parse_args()
    try:
        source_rows = read_jsonl("sources.jsonl")
        sources = validate_sources(source_rows)
        scheme_rows = read_json("classification-schemes.json")
        schemes = validate_schemes(scheme_rows, sources)
        node_rows = read_jsonl("isic-rev5.nodes.jsonl")
        nodes = validate_nodes(node_rows, sources)
        crosswalk_rows = read_jsonl("crosswalks.jsonl")
        validate_crosswalks(crosswalk_rows, sources, schemes, nodes)
        claim_rows = read_jsonl("claims.jsonl")
        validate_claims(claim_rows, sources)
        evidence_policy = read_json("evidence-policy.json")
        completeness_policy = read_json("completeness-policy.json")
        review_policy = read_json("review-policy.json")
        manifest = read_json("manifest.json")
        require(evidence_policy["minimum_foundation_sources"] <= len(sources), "policy source minimum not met")
        require(len(completeness_policy["coverage_dimensions"]) >= 12, "too few completeness dimensions")
        require(len(completeness_policy["gates"]) >= 8, "too few completeness gates")
        require(len(review_policy["roles"]) >= 4, "too few review roles")
        manifest_counts = manifest["corpus_counts"]
        observed_counts = {
            "authoritative_sources": len(sources),
            "source_publishers": len({row["publisher"] for row in sources.values()}),
            "classification_schemes_and_overlays": len(scheme_rows),
            "crosswalk_assertions": len(crosswalk_rows),
            "evidence_claims": len(claim_rows),
            "completeness_dimensions": len(completeness_policy["coverage_dimensions"]),
            "completeness_gates": len(completeness_policy["gates"]),
        }
        require(manifest_counts == observed_counts, f"manifest count drift: {observed_counts}")
        require(manifest["reference_spine"]["source_sha256"] == EXPECTED_SOURCE_SHA,
                "manifest source digest drift")
        require(manifest["reference_spine"]["generated_sha256"] == EXPECTED_NODE_SHA,
                "manifest generated digest drift")
        if args.schemas:
            validate_json_schemas(source_rows, scheme_rows, node_rows, crosswalk_rows, claim_rows)
    except (ValidationError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"FAIL industry foundation: {exc}", file=sys.stderr)
        return 1

    print("PASS industry foundation")
    print(f"  authoritative sources: {len(sources)} from {len({r['publisher'] for r in sources.values()})} publishers")
    print(f"  classification schemes/overlays: {len(scheme_rows)}")
    print("  ISIC Revision 5 nodes: 830 (22/87/258/463)")
    print(f"  typed crosswalk assertions: {len(crosswalk_rows)}")
    print(f"  evidence claims: {len(claim_rows)}")
    print(f"  completeness dimensions/gates: {len(completeness_policy['coverage_dimensions'])}/{len(completeness_policy['gates'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
