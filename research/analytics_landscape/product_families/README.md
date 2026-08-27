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
organizations, an independently declared and recomputed company count of at least 25, at least eight research or
standards references, and internally consistent coverage counts. These are breadth floors, not
proof of completeness, product promotion, semantic ratification, implementation qualification or
vertical acceptance.

The validator also rejects conflicting or duplicate normalized organization identities and any
crosswalk row that claims completion or product ratification. Parent/acquisition normalization,
claim-bound product evidence, evidence-role tagging, and complete sovereign seam ownership remain
explicit downstream research debts; a passing breadth validator does not discharge them.
The exact satisfied/partial/open disposition of the ten consolidation requirements is recorded in
`consolidation-hardening-audit.jsonl`.

Validate from the repository root:

```bash
python3 research/analytics_landscape/product_families/validate.py
```
