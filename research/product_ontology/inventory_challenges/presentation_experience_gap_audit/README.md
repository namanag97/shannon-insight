# Presentation & Analytical Experience Gap Audit

This package challenges the presentation side of the product ontology without treating
"dashboard" as a synonym for every analytical consumption experience.

It factorizes the domain into:

```text
analytical result kind
  x presentation artifact
  x semantic axis
  x product boundary
  x exact library contract
```

The generated tensors are intentionally open and fail-closed. They do not select a visual
encoding, ratify a product, qualify a renderer, or claim that a view is accessible merely
because it emitted pixels or ARIA text.

## Boundary posture

- `BI Reporting` now has an evidence-backed, unratified split adjudication into
  `Interactive Analytics Exploration` and `Formal Reporting & Publication`. Both candidates
  pass the ten-axis product test; canonical graph migration, qualification, vertical
  acceptance and ratification remain open.
- `Embedded Analytics` and `Analytical Notebook` remain existing product boundaries with
  narrower presentation imports.
- Spreadsheet/grid and generic scientific/3D experiences require product split tests.
- Maps, graphs, process views, signal views and image overlays remain specialized library
  families unless independent generic product economics and lifecycles are proven.
- Alert rule, alert occurrence, subscription, notification and acknowledgment are separate
  lifecycles.
- Accessibility equivalence is a constitutional requirement and library family, not an
  optional feature or standalone product.

## External 38-family challenge

The externally proposed 38-family map is preserved losslessly in
`external-38-family-frontier-crosswalk.jsonl`, but its rows are not automatically products.
Every row is classified as a product, product cluster, method/library family, shared semantic
foundation, cross-cutting constitution, candidate split, or research vacancy and is mapped to
exact retained product identities.

The crosswalk falsifies several incoming "missing" claims: notebooks, experimentation,
forecasting, simulation, optimization, graph, geospatial, predictive-model lifecycle,
planning, activation and optional agent/model extensions already have retained boundaries.
Only two rows survive as genuine new boundary-research vacancies in this pass:

- analytical content management and collaboration;
- subscriptions, alerts and insight delivery.

This yields a typed coverage frontier above the product registry rather than an unjustified
second product registry. `frontier-level-non-collapse-laws.jsonl` makes the essential level
distinctions executable.

## Build and validate

```bash
python3 build_bundle.py
python3 validate.py
```

The input snapshot binds this audit to the current retained-product readiness corpus and
the existing BI/visualization semantic slice. Any upstream change makes the package stale.
