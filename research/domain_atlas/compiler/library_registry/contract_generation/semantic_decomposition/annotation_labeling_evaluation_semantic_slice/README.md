# Annotation, labeling and reference-evaluation semantic slice

This deterministic research slice separates annotation workflow from source truth, statistical
agreement, accepted reference authority, dataset curation and downstream model/effect authority.

```text
source occurrence + selector + schema/instructions
                         |
population -> sample -> assignment -> annotation occurrence
                                      |
                              review/correction
                                      |
agreement estimate -> consensus result -> adjudication
                                      |
                         accepted reference edition

sources + membership/filter/dedup + balance/splits + rights/docs
                                      |
                              dataset release
```

“Ground truth” is rejected as a portable semantic name because it implies absolute truth. The
portable object is an accepted, scoped, versioned, challengeable and recallable reference edition
with named evidence and authority. Agreement is not correctness; consensus is not adjudication;
adjudication is not source truth.

The slice retains both `product.annotation_operations` and
`product.dataset_curation_workbench` as separate products with narrower ownership. A curated
dataset can contain no annotations, while annotations may target occurrences across multiple
dataset editions. Dataset Curation owns purpose/membership decisions, split and audit evidence,
immutable edition identity, release, maintenance and recall. It imports preparation, annotation,
quality methods, rights authority, storage, publication service and model lifecycle.

Fourteen exact Dataset Curation library seams replace the earlier three coarse placeholders:
definition/purpose, source admission/membership, selection, derivation recipes, duplicate
adjudication, cohort coverage, partition assignment, leakage audit, annotation binding, rights/use
manifest, dataset profiles, documentation projections, immutable edition manifests and
release/maintenance/recall.

Every finding remains unratified. No exact contract/provider has been selected, no implementation
is qualified and no canonical gap is closed.

```bash
python3 build_annotation_labeling_evaluation_semantic_slice.py
python3 validate.py
```
