# Horizontal analytics coverage-family research corpus

This package is a broad SOTA evidence seed for 38 horizontal analytics coverage coordinates. It is
not a second canonical product registry. A row may represent a sovereign product, a product
cluster, a mathematical or method family, shared semantic or experience infrastructure, or a
cross-cutting constitution.

The authoritative ontology-level disposition for each row is maintained in:

```text
research/product_ontology/inventory_challenges/
  presentation_experience_gap_audit/
    external-38-family-frontier-crosswalk.jsonl
```

Every shard must contain exactly the manifest-declared families, at least 25 distinct
organizations, an independently declared and recomputed company count of at least 25, at least
eight research or standards references, and internally consistent coverage counts. These are
breadth floors, not proof of completeness, product promotion, semantic ratification,
implementation qualification, or vertical acceptance.

## Evidence identity and claim governance

The B04 projection is integrated into this package rather than maintained as a parallel registry.
Its sovereign question is whether the corpus may assert an entity, bounded evidence claim,
locator, evidence role, or downstream gate state without confusing research evidence with
authority or execution.

Normative research-governance inputs:

- `evidence-governance-policy.json`: gate order, role vocabulary, identity and relationship kinds,
  primary-source claim cards, negative charter, and non-collapse laws;
- `evidence-governance.schema.json`: machine-readable record contracts;
- `build_evidence_governance.py` and `validate_evidence_governance.py`: deterministic projection
  and semantic validation;
- `build_evidence_upgrade_campaigns.py` and
  `validate_evidence_upgrade_campaigns.py`: deterministic prioritization of unresolved exact
  evidence and identity research.

Generated ledgers:

- `research-reference-role-projection.jsonl`: one unratified role projection per unique source;
- `research-reference-family-claims.jsonl`: one bounded claim per source-family occurrence;
- `organization-family-membership-claims.jsonl`: one candidate-adoption claim per
  organization-family occurrence;
- `organization-identity-projection.jsonl`: provisional corpus handles only;
- `organization-identity-gaps.jsonl`: exact identity and relationship review obligations;
- `evidence-governance-frontier.jsonl`: current HR03-HR05 gate state;
- `evidence-governance-summary.json`: recomputed totals and explicit zero downstream gates;
- `evidence-upgrade-campaigns.jsonl` and `evidence-upgrade-campaign-summary.json`: prioritized
  research work without promotion.

Core laws include:

```text
legal entity != brand != product != project != foundation
source URL != exact claim locator
candidate adoption reference != verified adoption
adoption evidence != semantic authority
proposed role != ratified role
semantic ratification != implementation qualification != executed acceptance
```

All current organization identities remain `PROVISIONAL_INTERNAL_HANDLE`. Every current source URL
remains non-exact until a stable selector, recoverable source state, and bounded-support review are
present. Generating the ledgers exposes debt; it does not repair it.

## Validation

From the repository root:

```bash
python3 research/analytics_landscape/product_families/validate.py
python3 research/analytics_landscape/product_families/build_evidence_governance.py --check
python3 research/analytics_landscape/product_families/validate_evidence_governance.py
python3 research/analytics_landscape/product_families/build_evidence_upgrade_campaigns.py --check
python3 research/analytics_landscape/product_families/validate_evidence_upgrade_campaigns.py
```

A validator pass proves only the laws it executes. It does not resolve provisional identities,
verify exact locators, ratify evidence roles, qualify implementations, or manufacture vertical
acceptance receipts from neatly sorted JSON.
