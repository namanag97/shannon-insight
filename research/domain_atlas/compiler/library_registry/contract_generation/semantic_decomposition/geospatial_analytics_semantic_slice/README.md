# Geospatial analytics semantic slice

This package is an evidence-backed, owner-unratified decomposition of every live library reached by
the Geospatial Workbench's declared product bindings plus its query, predictive and composition
neighbors. Product edges—not keyword matching—define the coverage universe.

```text
world phenomenon / domain feature
              |
     observation + spatial support
              |
   CRS + datum + epoch + axes
              |
      coordinate operation
              |
   +----------+-------------+
   |                        |
geometry + topology    coverage + grid
   |                        |
vector/network         raster/terrain
   +----------+-------------+
              |
 geocode / statistics / trajectory / 3D
              |
 typed spatial workflow + provider binding
              |
       run evidence + result
              |
   accuracy appraisal + publication
              X
    no dispatch or decision authority
```

## Boundary result

- 23 libraries feed the Geospatial Analysis Workbench.
- Coordinate transformation is also consumed by Visual Inspection Operations, making it a shared
  spatial-reference primitive rather than workbench-owned semantics.
- `qck.spatial-semantics` and `qck.spatial-kernels` belong at the query-engine ACL/kernel seam.
- `predictive.spatial_models` belongs to predictive model-family semantics while importing spatial
  support, CRS and weights.
- `method_kernels.spatial_methods` is composition-only and owns no spatial meaning.
- Carriers such as GeoJSON, GeoParquet, COG, LAS/COPC and 3D Tiles remain representation profiles.

The slice contains 40 primary, normative or official sources, 39 semantic modules, 51 method
boundaries, 43 non-collapse laws, 16 expert-learning profiles, nine recent non-LLM innovations,
27 exact library bindings and 432 explicit library-by-axis questions. No coordinate answer, owner
decision, exact contract, qualified implementation or canonical closure is selected.

## Validation

```bash
python3 research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/geospatial_analytics_semantic_slice/validate.py
```
