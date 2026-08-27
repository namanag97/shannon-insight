# Shared-owner library boundary adjudication

This is the deterministic collision review for the 30 normalized library candidates that projected
more than one semantic owner. It refuses the tempting repair of choosing the first context. The
verdict graph distinguishes a single owner with contributor contexts, replacement by existing
composition, and split-before-composition.

The current candidate verdict is 10 direct retains, one completed collision-removing rename and
nineteen coarse candidates retired in favor of existing compositions. No shared-owner closure gap
remains in this finite 30-candidate set. Every retirement has an exact identity crosswalk,
resolvable replacement edges, no compatibility alias and an explicit closure law. A verdict is not
ratification, implementation, qualification or compiler selectability.

Run from the repository root:

```sh
python3 research/product_ontology/adjudications/shared_owner_boundaries/build_bundle.py
python3 research/product_ontology/adjudications/shared_owner_boundaries/validate.py
```
