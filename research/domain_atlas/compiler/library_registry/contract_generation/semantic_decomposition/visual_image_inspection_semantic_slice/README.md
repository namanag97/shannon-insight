# Visual/image analysis and inspection semantic slice

This fail-closed research slice separates image carriers and sampled fields, acquisition and
calibration, image-analysis methods, predictive candidates, inspection plans/recipes/runs,
review/disposition authority and machine effects.

It retains `product.visual_inspection_operations` as an unratified product candidate, but narrows
it to the operated inspection lifecycle. Device transports, measurement/calibration semantics,
generic image algorithms, predictive-model lifecycle, annotation/ground truth, vertical defect
vocabularies, quality authority and physical control remain imported owners.

It also retains `product.image_analysis_workbench`: image analysis is an independently adoptable
project/workspace/recipe/run/result/review/publication job across scientific, medical, media and
industrial contexts and must not be forced into production inspection. It imports carrier,
lattice, radiometry, calibration, method, vertical-vocabulary and downstream-authority owners.

The existing `library.method_kernels.image_methods` boundary is challenged as overbroad because it
combines carrier/lattice semantics, filtering, morphology, segmentation, registration, features
and measurement under one contract. Twenty-three typed vacancies now include the fourteen exact
Image Analysis workbench seams and nine Visual Inspection seams.

Generated artifacts are deterministic. Run:

```text
python3 build_visual_image_inspection_semantic_slice.py
python3 validate.py
```

No record ratifies an owner, selects an exact contract, qualifies an implementation or closes a
canonical gap.
