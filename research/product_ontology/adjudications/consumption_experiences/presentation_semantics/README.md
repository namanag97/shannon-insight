# Presentation SOTA atlas projection

This package converts the upstream research note at
`docs/research/SOTA-PRESENTATION-CAPABILITY-ATLAS-2026-08-27.md` into deterministic JSONL.
It retains 50 product observations, 142 normalized visual-pattern candidates, 68 question-intent
routes, 17 specialist families and 50 target seam candidates.

The source note declares 82 evidence sources but does not contain 82 exact source records or URLs.
The projection therefore records that number only as a narrative claim and reports zero
machine-readable evidence sources. It does not promote provider observations into semantic
authority, canonical contracts, qualification or ratification. The existing
`presentation_experience_gap_audit` remains the canonical adjudication corpus.

Rebuild and validate from the repository root:

```bash
python3 research/product_ontology/adjudications/consumption_experiences/presentation_semantics/build_bundle.py
python3 research/product_ontology/adjudications/consumption_experiences/presentation_semantics/bridge_validate.py
```
