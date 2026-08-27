#!/usr/bin/env python3
"""Prioritize unresolved B04 organization-family claims into evidence campaigns."""
from __future__ import annotations

import argparse
import json
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
OUTPUT_FILES = (
    "evidence-upgrade-campaigns.jsonl",
    "evidence-upgrade-campaign-summary.json",
)


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def write_json(path: Path, value: Any) -> None:
    path.write_text(canonical_json(value) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.write_text(
        "".join(canonical_json(row) + "\n" for row in rows),
        encoding="utf-8",
    )


def build_records() -> dict[str, Any]:
    claims = load_jsonl(HERE / "organization-family-membership-claims.jsonl")
    identities = load_jsonl(HERE / "organization-identity-projection.jsonl")
    identity_gaps = load_jsonl(HERE / "organization-identity-gaps.jsonl")
    identity_by_id = {row["organization_id"]: row for row in identities}
    gap_by_id = {row["organization_id"]: row for row in identity_gaps}
    claims_by_org: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for claim in claims:
        claims_by_org[claim["organization_id"]].append(claim)

    campaigns: list[dict[str, Any]] = []
    for org_id, memberships in claims_by_org.items():
        identity = identity_by_id[org_id]
        gap = gap_by_id[org_id]
        family_refs = sorted({row["family_id"] for row in memberships})
        homepage_only = sum(
            row["evidence_strength"] == "WEAK_HOMEPAGE_ONLY"
            for row in memberships
        )
        exact_open = sum(
            not row["evidence_locator"]["exact_claim_support"]
            for row in memberships
        )
        provisional_identity = identity["identity_status"] == "PROVISIONAL_INTERNAL_HANDLE"
        priority_score = (
            len(memberships) * 10
            + homepage_only * 3
            + exact_open * 2
            + int(provisional_identity) * 5
        )
        campaigns.append(
            {
                "record_kind": "horizontal_evidence_upgrade_campaign",
                "campaign_id": "evidence-upgrade." + org_id,
                "organization_id": org_id,
                "canonical_name": identity["canonical_name"],
                "canonical_url": identity["canonical_url"],
                "source_declared_kind": identity["source_declared_kind"],
                "identity_status": identity["identity_status"],
                "family_refs": family_refs,
                "weak_membership_count": len(memberships),
                "homepage_only_count": homepage_only,
                "open_exact_locator_count": exact_open,
                "identity_gap_ref": gap["gap_id"],
                "priority_score": priority_score,
                "required_evidence_upgrade": [
                    "authoritative entity kind and identifier or exact identity evidence",
                    "exact product or project identity",
                    "official product, technical, specification, architecture, or release resource",
                    "stable selector and recoverable source-state identifier",
                    "bounded capability or adoption claim for each supported family",
                    "edition, version, effective date, and last-verified date when applicable",
                    "organization-product-project relationship",
                    "acquisition, rename, parent, predecessor, or successor relation when applicable",
                ],
                "promotion_law": (
                    "A source may strengthen only the exact bounded family claim selected and "
                    "verified; organization-wide reputation is never transitive evidence."
                ),
                "status": "OPEN_EVIDENCE_AND_IDENTITY_RESEARCH",
                "semantic_authority": False,
                "implementation_qualification": False,
                "executed_acceptance": False,
                "completion_claim": False,
            }
        )

    campaigns.sort(
        key=lambda row: (
            -row["priority_score"],
            -row["weak_membership_count"],
            row["canonical_name"].casefold(),
            row["organization_id"],
        )
    )
    summary = {
        "report_id": "horizontal_evidence_upgrade_campaigns",
        "schema_version": "2.0.0",
        "as_of": load(HERE / "manifest.json")["as_of"],
        "organization_campaign_count": len(campaigns),
        "weak_membership_count": len(claims),
        "open_exact_locator_count": sum(
            row["open_exact_locator_count"] for row in campaigns
        ),
        "provisional_identity_campaign_count": sum(
            row["identity_status"] == "PROVISIONAL_INTERNAL_HANDLE"
            for row in campaigns
        ),
        "top_20_campaigns": [
            {
                "organization_id": row["organization_id"],
                "name": row["canonical_name"],
                "weak_membership_count": row["weak_membership_count"],
                "open_exact_locator_count": row["open_exact_locator_count"],
                "priority_score": row["priority_score"],
            }
            for row in campaigns[:20]
        ],
        "strong_memberships_created": 0,
        "semantic_ratifications_created": 0,
        "implementation_qualifications_created": 0,
        "executed_acceptances_created": 0,
        "status": "PRIORITIZED_EXACT_EVIDENCE_AND_IDENTITY_RESEARCH_NOT_UPGRADED",
        "completion_claim": False,
    }
    return {
        "evidence-upgrade-campaigns.jsonl": campaigns,
        "evidence-upgrade-campaign-summary.json": summary,
    }


def write_outputs(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    records = build_records()
    write_jsonl(output_dir / OUTPUT_FILES[0], records[OUTPUT_FILES[0]])
    write_json(output_dir / OUTPUT_FILES[1], records[OUTPUT_FILES[1]])


def compare_outputs(expected: Path, actual: Path) -> list[str]:
    errors: list[str] = []
    for name in OUTPUT_FILES:
        if not (expected / name).is_file():
            errors.append("committed generated output missing: " + name)
        elif (expected / name).read_bytes() != (actual / name).read_bytes():
            errors.append("generated output is stale: " + name)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=HERE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        with tempfile.TemporaryDirectory(prefix="b04-evidence-upgrade-") as raw:
            rebuilt = Path(raw)
            write_outputs(rebuilt)
            errors = compare_outputs(HERE, rebuilt)
        for error in errors:
            print("ERROR: " + error)
        if errors:
            return 1
        print(f"PASS B04 evidence-upgrade campaigns are current: {len(OUTPUT_FILES)} files")
        return 0
    write_outputs(args.output_dir)
    print(canonical_json(load(args.output_dir / OUTPUT_FILES[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
