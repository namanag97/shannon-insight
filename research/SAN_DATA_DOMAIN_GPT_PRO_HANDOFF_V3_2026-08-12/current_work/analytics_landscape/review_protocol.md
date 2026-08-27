# Recurring review protocol

## Cadence

- Run a light review every 30 days for ownership, product-status, and broken-link changes.
- Run a deep domain review every 90 days.
- Immediately review a company after an acquisition, shutdown, major rebrand, or product sunset.
- Review a subdomain after a new standard, major handbook, or field-defining conference release.

## Deep-review sequence

1. Select the oldest or lowest-coverage domain from `review.queue`.
2. Read its standards, handbooks, conference proceedings, and university research-group pages.
3. Build a discovery list of companies and people; do not add them as experts yet.
4. Verify company scope from an official product/company page and current ownership from a
   reliable corporate announcement or filing.
5. Verify academic experts from university profiles, standards authorship, handbook editorship,
   or sustained peer-reviewed contributions.
6. Verify practitioner experts from technical authorship, category creation, standards work, or
   sustained product leadership. Job title alone is insufficient.
7. Add relationship evidence, a confidence score, and `last_verified` date.
8. Search for disconfirming evidence: product sunset, acquisition, role change, overstated
   specialization, or dependence on excluded AI functionality.
9. Run `validate_catalog.py` and inspect the generated coverage summary.
10. Set a domain to `reviewed` only when its completion criteria are satisfied.

Use `review_cycle.py status` for selection and `review_cycle.py start` to create the auditable
manifest. The generated manifest is the authoritative record for checklist evidence and review
notes. `review_cycle.py complete --mark-reviewed` enforces the minimum quantitative gate.

## Completion criteria for a reviewed domain

- A clear domain definition and non-overlapping subdomain boundaries.
- At least two authoritative field sources.
- At least five currently relevant specialist companies, when a commercial market exists.
- At least five experts with a mix of academic and practitioner perspectives.
- Each company and expert relationship has supporting evidence.
- Acquisitions and historical companies are labelled.
- Known gaps, contested terminology, and exclusions are recorded.

## Evidence tiers

1. Standards, specifications, official university profiles, peer-reviewed handbooks, filings.
2. Official technical documentation, company announcements, source repositories.
3. Reputable conference biographies and independent technical evaluations.
4. Vendor blogs and interviews; useful but require triangulation for strong claims.
5. Directories, social profiles, aggregators, and community posts; discovery only.

## Confidence

- `0.90–1.00`: direct authoritative evidence and recent verification.
- `0.75–0.89`: strong evidence, but scope or current status needs some interpretation.
- `0.60–0.74`: credible discovery lead requiring another source.
- Below `0.60`: do not publish as a confirmed relationship.
