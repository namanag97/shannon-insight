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

- `BI Reporting` is challenged for a possible split between interactive exploration and
  formal reporting/publication.
- `Embedded Analytics` and `Analytical Notebook` remain existing product boundaries with
  narrower presentation imports.
- Spreadsheet/grid and generic scientific/3D experiences require product split tests.
- Maps, graphs, process views, signal views and image overlays remain specialized library
  families unless independent generic product economics and lifecycles are proven.
- Alert rule, alert occurrence, subscription, notification and acknowledgment are separate
  lifecycles.
- Accessibility equivalence is a constitutional requirement and library family, not an
  optional feature or standalone product.

## Build and validate

```bash
python3 build_bundle.py
python3 validate.py
```

The input snapshot binds this audit to the current retained-product readiness corpus and
the existing BI/visualization semantic slice. Any upstream change makes the package stale.
