#!/usr/bin/env python3
"""Validate total reviewed-vendor B04 evidence dispositions and frontier accounting."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE / "organization-family-membership-claims.jsonl"
EXACT = HERE / "effective-evidence-upgrade-dispositions.jsonl"
REVIEWS = HERE / "reviewed-organizations.json"
DISPOSITIONS = HERE / "organization-family-review-dispositions.jsonl"
SUMMARY = HERE / "effective-evidence-frontier-summary.json"

RETAIN = "RETAIN_EXACT_PRODUCT_EVIDENCE"
REJECT = "REJECT_WEAK_CANDIDATE_FROM_CANONICAL_EVIDENCE"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def fail(message: str) -> None:
    raise SystemExit(message)


def main() -> int:
    base = load_jsonl(BASE)
    exact_all = load_jsonl(EXACT)
    exact = [row for row in exact_all if row["disposition_kind"] == "BASE_CLAIM_UPGRADE"]
    discoveries = [
        row for row in exact_all if row["disposition_kind"] == "STRONG_EVIDENCE_DISCOVERY"
    ]
    reviews = load_json(REVIEWS)
    dispositions = load_jsonl(DISPOSITIONS)
    summary = load_json(SUMMARY)

    base_by_claim = {row["claim_id"]: row for row in base}
    exact_by_claim = {row["claim_id"]: row for row in exact}
    disposition_by_claim = {row["claim_id"]: row for row in dispositions}
    if len(base_by_claim) != len(base):
        fail("duplicate base claim IDs")
    if len(exact_by_claim) != len(exact):
        fail("duplicate exact-evidence claim IDs")
    if len(disposition_by_claim) != len(dispositions):
        fail("duplicate review disposition claim IDs")

    reviewed_ids = {row["organization_id"] for row in reviews.get("organizations", [])}
    expected_reviewed_claims = {
        row["claim_id"] for row in base if row["organization_id"] in reviewed_ids
    }
    if set(disposition_by_claim) != expected_reviewed_claims:
        missing = expected_reviewed_claims - disposition_by_claim.keys()
        unexpected = disposition_by_claim.keys() - expected_reviewed_claims
        fail(
            f"review disposition totality mismatch; missing={sorted(missing)} "
            f"unexpected={sorted(unexpected)}"
        )

    counts: Counter[str] = Counter()
    for claim_id, row in disposition_by_claim.items():
        base_row = base_by_claim[claim_id]
        if (row["organization_id"], row["family_id"]) != (
            base_row["organization_id"],
            base_row["family_id"],
        ):
            fail(f"scope drift: {claim_id}")
        if row.get("absence_claim") is not False:
            fail(f"absence claim not refused: {claim_id}")
        for field in (
            "semantic_authority",
            "qualification_claim",
            "completion_claim",
        ):
            if row.get(field) is not False:
                fail(f"illegal {field} promotion: {claim_id}")

        disposition = row["disposition"]
        counts[disposition] += 1
        if disposition == RETAIN:
            exact_row = exact_by_claim.get(claim_id)
            if not exact_row:
                fail(f"retained claim lacks exact evidence: {claim_id}")
            if row.get("exact_upgrade_id") != exact_row["upgrade_id"]:
                fail(f"retained upgrade identity mismatch: {claim_id}")
            if row.get("official_locator") != exact_row["official_locator"]:
                fail(f"retained locator mismatch: {claim_id}")
            if row.get("product_id") != exact_row["product_id"]:
                fail(f"retained product identity mismatch: {claim_id}")
        elif disposition == REJECT:
            if claim_id in exact_by_claim:
                fail(f"exact evidence claim was rejected: {claim_id}")
            if any(
                row.get(field) is not None
                for field in (
                    "exact_upgrade_id",
                    "official_locator",
                    "product_id",
                )
            ):
                fail(f"rejected claim carries exact evidence fields: {claim_id}")
        else:
            fail(f"invalid disposition: {claim_id} -> {disposition}")

    reviewed_claim_ids = set(disposition_by_claim)
    exact_claim_ids = set(exact_by_claim)
    open_weak = set(base_by_claim) - reviewed_claim_ids - exact_claim_ids
    exact_unreviewed = exact_claim_ids - reviewed_claim_ids
    expected_summary = {
        "base_membership_claim_count": len(base),
        "exact_product_evidence_claim_count": len(exact),
        "strong_discovery_claim_count": len(discoveries),
        "reviewed_organization_count": len(reviewed_ids),
        "reviewed_claim_count": len(reviewed_claim_ids),
        "retained_reviewed_claim_count": counts[RETAIN],
        "rejected_reviewed_claim_count": counts[REJECT],
        "exact_unreviewed_claim_count": len(exact_unreviewed),
        "open_weak_membership_claim_count": len(open_weak),
        "accounted_claim_count": len(base),
    }
    for field, expected in expected_summary.items():
        if summary.get(field) != expected:
            fail(f"summary mismatch for {field}: {summary.get(field)!r} != {expected!r}")
    if summary.get("completion_claim") is not False:
        fail("completion claim must remain false")
    if summary.get("semantic_authority_promotions") != 0:
        fail("semantic-authority promotion count must remain zero")
    if summary.get("qualification_promotions") != 0:
        fail("qualification promotion count must remain zero")

    print(
        json.dumps(
            {
                "validated": True,
                "reviewed_organization_count": len(reviewed_ids),
                "reviewed_claim_count": len(reviewed_claim_ids),
                "retained_reviewed_claim_count": counts[RETAIN],
                "rejected_reviewed_claim_count": counts[REJECT],
                "open_weak_membership_claim_count": len(open_weak),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
