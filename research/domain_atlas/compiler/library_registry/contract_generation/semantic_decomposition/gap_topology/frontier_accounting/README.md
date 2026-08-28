# Exhaustive semantic-gap frontier accounting

This package provides the missing lossless accounting layer between the semantic gap topology and
its exact source occurrences.

The parent topology is a useful quotient and execution schedule, but a cluster count alone does not
prove that every constituent gap remains attributable. This package reconstructs every atom from the
same exact input records used by `build_gap_topology.py`, then assigns each atom to:

1. exactly one source cluster;
2. exactly one reusable semantic-decision kernel;
3. exactly one disposition class; and
4. exactly one local residual with an owner, evidence need, closure condition and invalidation rule.

The package deliberately distinguishes research routing from closure. A reusable kernel shares the
question protocol, evidence schema, refusal pattern and conformance mechanics. It never shares a
semantic answer, authority receipt, implementation verdict, qualification or acceptance decision.

## Outputs

- `disposition-taxonomy.jsonl` defines the complete disposition vocabulary.
- `decision-kernels.jsonl` encodes reusable, falsifiable semantic-decision kernels.
- `cluster-dispositions.jsonl` gives every parent quotient one exact disposition and atom-set digest.
- `atom-dispositions-00.jsonl` through `atom-dispositions-31.jsonl` preserve every exact source atom.
- `summary.json` reports conserved counts and zero/unmapped checks.
- `validation-report.json` records the proof obligations enforced by `validate.py`.
- `manifest.json` binds generated files by SHA-256, bytes and record count.

## Closure discipline

The current corpus may legitimately produce:

- `COVERED_BY_REUSABLE_KERNEL`;
- `EVIDENCE_VACANCY`;
- `IMPLEMENTATION_ONLY`; and
- `QUALIFICATION_ONLY`.

It may not claim `CLOSED_BY_EXISTING_VALID_EVIDENCE` without an exact scope-bound closure receipt.
It may not infer implementation, portability, product readiness or vertical acceptance from
structural coverage, a passing builder or an attractive diagram. Software architecture has enough
ceremonial optimism already.

## Rebuild and validate

```bash
python3 research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/gap_topology/build_gap_topology.py
python3 research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/gap_topology/validate.py
python3 research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/gap_topology/frontier_accounting/integrate_frontier_accounting.py
python3 research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/gap_topology/frontier_accounting/build_frontier_accounting.py
python3 research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/gap_topology/frontier_accounting/validate.py
python3 research/product_ontology/validate_registry.py
```

All records remain unratified research/control artifacts and carry `completion_claim:false`.
