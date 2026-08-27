#!/usr/bin/env python3
"""Dependency-free, cross-shard validation for horizontal coverage families."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse


HERE = Path(__file__).resolve().parent


def load(path: Path):
    return json.loads(path.read_text())


def valid_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def main() -> int:
    errors: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    manifest = load(HERE / "manifest.json")
    shard_names = manifest.get("shards", [])
    expected_ids = manifest.get("family_ids", [])
    gates = manifest.get("coverage_gates", {})
    require(manifest.get("status") == "review_candidate", "corpus must remain a review candidate")
    require(manifest.get("expected_family_count") == 38, "manifest family count drift")
    require(len(shard_names) == 19 and len(set(shard_names)) == 19, "expected 19 unique shards")
    require(len(expected_ids) == 38 and len(set(expected_ids)) == 38, "expected 38 unique family ids")
    require(manifest.get("ontology_level_policy", "").startswith("A family label is a research coverage coordinate"), "ontology-level safeguard missing")
    require(gates.get("min_organizations_per_family") == 25, "organization floor drift")
    require(gates.get("min_companies_per_family") == 25, "company floor drift")
    require(gates.get("min_research_references_per_family", 0) >= 8, "research floor too weak")

    families: list[dict] = []
    for shard_name in shard_names:
        path = HERE / shard_name
        require(path.is_file(), f"missing shard {shard_name}")
        if not path.is_file():
            continue
        shard = load(path)
        require(set(shard) == {"schema_version", "as_of", "families"}, f"unexpected shard keys {shard_name}")
        require(shard.get("schema_version") == manifest.get("schema_version"), f"schema version drift {shard_name}")
        require(shard.get("as_of") == manifest.get("as_of"), f"as-of drift {shard_name}")
        require(len(shard.get("families", [])) == 2, f"each shard must contain exactly two families: {shard_name}")
        families.extend(shard.get("families", []))

    require([row.get("id") for row in families] == expected_ids, "family order/identity differs from manifest")
    require(len(families) == 38, "cross-shard family count drift")

    global_orgs: dict[str, tuple[str, str, str]] = {}
    global_refs: dict[str, tuple] = {}
    company_floor = gates.get("min_companies_per_family", 25)
    for family in families:
        ident = family.get("id", "<missing>")
        require(isinstance(family.get("sovereign_question"), str) and len(family["sovereign_question"]) >= 20, f"weak sovereign question {ident}")
        require(len(set(family.get("negative_charter", []))) >= 3, f"negative charter incomplete {ident}")
        require(len(set(family.get("required_product_surfaces", []))) >= 8, f"product-completeness surfaces incomplete {ident}")

        orgs = family.get("organizations", [])
        refs = family.get("research", [])
        org_ids = [row.get("id") for row in orgs]
        ref_ids = [row.get("id") for row in refs]
        require(len(orgs) >= gates.get("min_organizations_per_family", 25), f"organization floor missed {ident}")
        require(len(org_ids) == len(set(org_ids)), f"duplicate organization inside {ident}")
        companies = [row for row in orgs if row.get("organization_kind") == "company"]
        require(len(companies) >= company_floor, f"company floor missed {ident}: {len(companies)}")
        require(all(row.get("organization_kind") in {"company", "nonprofit_project"} for row in orgs), f"unknown organization kind {ident}")
        require(all(valid_url(row.get("url", "")) for row in orgs), f"invalid organization URL {ident}")
        require(len(refs) >= gates.get("min_research_references_per_family", 8), f"research floor missed {ident}")
        require(len(ref_ids) == len(set(ref_ids)), f"duplicate research reference inside {ident}")
        require(all(valid_url(row.get("url", "")) and row.get("title") and row.get("kind") and row.get("tags") for row in refs), f"incomplete research reference {ident}")

        coverage = family.get("coverage", {})
        require(coverage.get("organization_count") == len(orgs), f"declared organization count stale {ident}")
        require(coverage.get("research_count") == len(refs), f"declared research count stale {ident}")
        require(coverage.get("organization_floor") == gates.get("min_organizations_per_family"), f"family organization floor drift {ident}")
        require(coverage.get("research_floor") == gates.get("min_research_references_per_family"), f"family research floor drift {ident}")
        require(coverage.get("status") == "review_candidate", f"family overclaims review state {ident}")

        for row in orgs:
            definition = (row["name"], row["url"], row["organization_kind"])
            require(row["id"].startswith("org_"), f"invalid organization id {row.get('id')}")
            if row["id"] in global_orgs:
                require(global_orgs[row["id"]] == definition, f"conflicting organization definition {row['id']}")
            else:
                global_orgs[row["id"]] = definition
        for row in refs:
            definition = (row["title"], row["url"], row["kind"], tuple(row["tags"]), row.get("year"))
            require(row["id"].startswith("ref_"), f"invalid research id {row.get('id')}")
            if row["id"] in global_refs:
                require(global_refs[row["id"]] == definition, f"conflicting research definition {row['id']}")
            else:
                global_refs[row["id"]] = definition

    crosswalk_path = (HERE / manifest.get("canonical_boundary_crosswalk", "")).resolve()
    require(crosswalk_path.is_file(), "canonical ontology-level crosswalk missing")
    if crosswalk_path.is_file():
        crosswalk = [json.loads(line) for line in crosswalk_path.read_text().splitlines() if line.strip()]
        require([row.get("frontier_id") for row in crosswalk] == [f"H{i:02d}" for i in range(1, 39)], "canonical frontier crosswalk is not complete")
        require(all(row.get("adjudicated_ontology_level") and row.get("disposition") for row in crosswalk), "canonical frontier row lacks ontology disposition")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    company_count = sum(kind == "company" for _, _, kind in global_orgs.values())
    print(
        "PASS horizontal coverage-family corpus: "
        f"{len(families)} families in {len(shard_names)} shards; "
        f"{len(global_orgs)} unique organizations ({company_count} companies); "
        f"{len(global_refs)} unique research/standards references; "
        "every family has >=25 companies and remains review_candidate"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
