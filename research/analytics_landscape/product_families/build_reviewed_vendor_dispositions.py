#!/usr/bin/env python3
"""Build total B04 dispositions for organizations whose product evidence was reviewed."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
BASE = HERE / "organization-family-membership-claims.jsonl"
EXACT = HERE / "effective-evidence-upgrade-dispositions.jsonl"
REVIEWS = HERE / "reviewed-organizations.json"
OUTPUT = HERE / "organization-family-review-dispositions.jsonl"
SUMMARY = HERE / "effective-evidence-frontier-summary.json"

RETAIN = "RETAIN_EXACT_PRODUCT_EVIDENCE"
REJECT = "REJECT_WEAK_CANDIDATE_FROM_CANONICAL_EVIDENCE"
ALLOWED = {RETAIN, REJECT}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def main() -> int:
    base = load_jsonl(BASE)
    exact_all = load_jsonl(EXACT)
    exact = [row for row in exact_all if row["disposition_kind"] == "BASE_CLAIM_UPGRADE"]
    discoveries = [
        row for row in exact_all if row["disposition_kind"] == "STRONG_EVIDENCE_DISCOVERY"
    ]
    review_source = load_json(REVIEWS)

    claims_by_id = {row["claim_id"]: row for row in base}
    if len(claims_by_id) != len(base):
        raise SystemExit("duplicate base claim IDs")
    exact_by_claim = {row["claim_id"]: row for row in exact}
    if len(exact_by_claim) != len(exact):
        raise SystemExit("duplicate exact-evidence claim IDs")

    claims_by_organization: dict[str, list[dict]] = defaultdict(list)
    for claim in base:
        claims_by_organization[claim["organization_id"]].append(claim)

    review_organizations = review_source.get("organizations", [])
    reviewed_ids = [row["organization_id"] for row in review_organizations]
    if len(reviewed_ids) != len(set(reviewed_ids)):
        raise SystemExit("duplicate reviewed organization IDs")

    output_rows: list[dict] = []
    for review in review_organizations:
        organization_id = review["organization_id"]
        organization_claims = claims_by_organization.get(organization_id)
        if not organization_claims:
            raise SystemExit(f"reviewed organization has no base claims: {organization_id}")
        if review.get("absence_claim") is not False:
            raise SystemExit(f"review must explicitly refuse absence claim: {organization_id}")
        if review.get("default_unretained_disposition") != REJECT:
            raise SystemExit(f"invalid default disposition: {organization_id}")

        scopes = review.get("official_research_scope", [])
        if not scopes:
            raise SystemExit(f"missing official research scope: {organization_id}")
        for locator in scopes:
            parsed = urlparse(locator)
            if parsed.scheme != "https" or not parsed.netloc:
                raise SystemExit(
                    f"invalid official research-scope locator for {organization_id}: {locator}"
                )

        retained = set(review.get("retained_claim_ids", []))
        organization_claim_ids = {row["claim_id"] for row in organization_claims}
        unknown_retained = retained - organization_claim_ids
        if unknown_retained:
            raise SystemExit(
                f"{organization_id}: retained claims outside organization scope: "
                f"{sorted(unknown_retained)}"
            )
        missing_exact = retained - exact_by_claim.keys()
        if missing_exact:
            raise SystemExit(
                f"{organization_id}: retained claims lack exact evidence: {sorted(missing_exact)}"
            )
        undeclared_exact = {
            claim_id
            for claim_id in organization_claim_ids
            if claim_id in exact_by_claim and claim_id not in retained
        }
        if undeclared_exact:
            raise SystemExit(
                f"{organization_id}: exact evidence omitted from retained set: "
                f"{sorted(undeclared_exact)}"
            )

        for claim in sorted(organization_claims, key=lambda row: row["claim_id"]):
            claim_id = claim["claim_id"]
            if claim_id in retained:
                exact_row = exact_by_claim[claim_id]
                disposition = RETAIN
                rationale = (
                    "Retained because an exact official product-documentation locator "
                    "supports the bounded organization-family claim. Semantic authority "
                    "and implementation qualification remain withheld."
                )
                exact_upgrade_id = exact_row["upgrade_id"]
                official_locator = exact_row["official_locator"]
                product_id = exact_row["product_id"]
            else:
                disposition = REJECT
                rationale = review["default_unretained_rationale"]
                exact_upgrade_id = None
                official_locator = None
                product_id = None

            if disposition not in ALLOWED:
                raise SystemExit(f"invalid generated disposition: {claim_id}")
            output_rows.append(
                {
                    "review_id": f"review.{claim_id}",
                    "record_kind": "organization_family_evidence_review_disposition",
                    "claim_id": claim_id,
                    "organization_id": organization_id,
                    "family_id": claim["family_id"],
                    "disposition": disposition,
                    "rationale": rationale,
                    "reviewed_on": review["reviewed_on"],
                    "official_research_scope": scopes,
                    "exact_upgrade_id": exact_upgrade_id,
                    "official_locator": official_locator,
                    "product_id": product_id,
                    "absence_claim": False,
                    "semantic_authority": False,
                    "qualification_claim": False,
                    "completion_claim": False,
                }
            )

    output_rows.sort(key=lambda row: row["claim_id"])
    if len({row["claim_id"] for row in output_rows}) != len(output_rows):
        raise SystemExit("duplicate generated review dispositions")
    OUTPUT.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in output_rows),
        encoding="utf-8",
    )

    disposition_counts = Counter(row["disposition"] for row in output_rows)
    reviewed_claim_ids = {row["claim_id"] for row in output_rows}
    exact_claim_ids = set(exact_by_claim)
    open_weak_claim_ids = set(claims_by_id) - reviewed_claim_ids - exact_claim_ids
    exact_unreviewed_claim_ids = exact_claim_ids - reviewed_claim_ids
    summary = {
        "report_id": "effective_horizontal_evidence_frontier",
        "as_of": review_source["as_of"],
        "base_membership_claim_count": len(base),
        "exact_product_evidence_claim_count": len(exact_claim_ids),
        "strong_discovery_claim_count": len(discoveries),
        "reviewed_organization_count": len(reviewed_ids),
        "reviewed_claim_count": len(reviewed_claim_ids),
        "retained_reviewed_claim_count": disposition_counts[RETAIN],
        "rejected_reviewed_claim_count": disposition_counts[REJECT],
        "exact_unreviewed_claim_count": len(exact_unreviewed_claim_ids),
        "open_weak_membership_claim_count": len(open_weak_claim_ids),
        "accounted_claim_count": (
            len(reviewed_claim_ids) + len(open_weak_claim_ids) + len(exact_unreviewed_claim_ids)
        ),
        "reviewed_organization_ids": sorted(reviewed_ids),
        "non_absence_law": (
            "Rejecting a weak candidate removes it from canonical product-boundary "
            "evidence; it does not assert that the organization lacks the capability."
        ),
        "semantic_authority_promotions": 0,
        "qualification_promotions": 0,
        "completion_claim": False,
        "status": "REVIEWED_VENDOR_CLAIMS_TOTAL_OPEN_WEAK_FRONTIER_EXPLICIT",
    }
    if summary["accounted_claim_count"] != len(base):
        raise SystemExit("effective frontier does not account for every base claim")
    SUMMARY.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
