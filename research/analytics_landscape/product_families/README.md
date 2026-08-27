# Horizontal analytics coverage-family research corpus

This package is a broad SOTA evidence seed for 38 horizontal analytics coverage coordinates. It is
not a second canonical product registry. A row may represent a sovereign product, a product
cluster, a mathematical/method family, shared semantic or experience infrastructure, or a
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
implementation qualification or vertical acceptance.

The breadth validator rejects conflicting organization definitions, duplicate normalized names,
stale counts, and any crosswalk row that claims completion or product ratification. That protection
is intentionally narrower than identity or evidence closure.

`build_evidence_governance.py`, `validate_evidence_governance.py`, and `evidence_governance/` now turn the organization-identity, claim-binding and evidence-role debts
into deterministic entity, claim and frontier ledgers. The generated rows preserve every source
membership while explicitly refusing to infer legal identity, product/project/foundation kind,
acquisition, rename, parentage, exact claim support or semantic authority from a name or homepage.
The exact satisfied/partial/open disposition of all ten consolidation requirements remains in
`consolidation-hardening-audit.jsonl`.

Validate from the repository root:

```bash
python3 research/analytics_landscape/product_families/validate.py
python3 research/analytics_landscape/product_families/build_evidence_governance.py \
  --output /tmp/horizontal-evidence-governance
python3 research/analytics_landscape/product_families/validate_evidence_governance.py \
  --generated /tmp/horizontal-evidence-governance
```

A validator pass proves only the laws it executes. It does not resolve provisional identities,
ratify evidence roles, qualify implementations or manufacture vertical acceptance receipts from well-formatted JSON.
