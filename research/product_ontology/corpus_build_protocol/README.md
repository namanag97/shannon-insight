# Governed corpus build protocol

This package defines how Python participates in the Shannon data-and-analytics architecture. Python is a deterministic research/corpus workbench and bounded prototype harness. It is not semantic authority, a provider qualification service, or the required implementation language for runtime libraries.

## Package law

Every automatically executable corpus package eventually needs an explicit contract naming:

- package kind and authority class;
- exact build and validation commands;
- upstream package dependencies, input selectors and unresolved input surfaces;
- rebuild and write-boundary policies;
- fixed-point membership where repository-wide inventory is observed;
- negative claims preventing structural output from becoming semantic, qualification or ratification authority.

The protocol distinguishes deterministic projections, repository-wide fixed-point projections, aggregate validators, authored sources, execution campaigns and immutable historical snapshots. These categories cannot be silently interchanged.

`observed-package-candidates.jsonl` is a deterministic inventory of Python package-shaped directories. Discovery does not grant execution authority. Uncontracted packages are emitted into `migration-gaps.jsonl`, and the orchestrator refuses to run them.

The migration is factored rather than scheduled as hundreds of independent fixes. `contract-candidate-dockets.jsonl` gives every uncontracted package the same nine decision axes, and `migration-batches.jsonl` groups them into nine dependency waves from authored/evidence classification through universes, vertical contexts, product boundaries, semantic contracts, compiler binding, qualification and repository fixed points.

## Commands

From the repository root:

```text
python3 research/product_ontology/corpus_build_protocol/build_registry.py
python3 research/product_ontology/corpus_build_protocol/validate.py
python3 research/product_ontology/corpus_build_protocol/orchestrate.py plan package.product_ontology_aggregate_validation
python3 research/product_ontology/corpus_build_protocol/orchestrate.py verify package.solution_synthesis_architecture
```

`execute` requires a clean worktree, complete input ownership, and an enabled package contract. It runs enabled deterministic builders twice, requires byte-identical package trees, executes validators and refuses writes outside declared package roots. Execution receipts are structural build evidence only; they do not qualify implementations or ratify domain contracts.

## Current boundary

This is a migration protocol, not a fabricated claim that every legacy generator is already governed. The registry contracts the high-fanout architecture, rebase, closure, inventory and aggregate-validation path first. Every remaining discovered package stays explicitly non-executable until its inputs, outputs, dependencies, ownership and rebuild semantics are adjudicated.
