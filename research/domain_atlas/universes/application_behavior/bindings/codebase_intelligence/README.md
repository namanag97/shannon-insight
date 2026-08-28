# Code-intelligence application binding

This package binds the executable `src/shannon_insight` Python distribution to the provider-neutral
[application-behavior universe](../../README.md). It answers a narrow question that the wider data
and analytics research previously left dangerously implicit: **what is the Python package, and what
is it not?**

## Boundary verdict

`src/shannon_insight` is an implemented candidate **Software / Codebase Intelligence and Engineering
Analytics application product**. It observes software repositories, derives software-domain facts,
relationships, signals, findings and snapshots, and presents evidence to engineering decision
makers.

It is not the universal enterprise data-and-analytics platform. The `research/` Python programs are
a separate research/corpus/validation/qualification workbench. Neither surface gains semantic,
provider, qualification or ratification authority from being written in Python.

```text
enterprise data + analytics constitution
                  │
                  ├── provider-neutral application behavior
                  ├── source/data/identity/time contracts
                  ├── method and presentation contracts
                  ├── runtime/evidence/policy contracts
                  │
                  ▼
Software / Codebase Intelligence product
                  │
                  ├── repository observation
                  ├── software identity and syntax facts
                  ├── relationship graph/tensor
                  ├── temporal and analytical method kernels
                  ├── engineering signals and findings
                  ├── retained snapshots
                  └── reports/API/CLI experience
                  │
                  ▼
Python implementation in src/shannon_insight

research/**/*.py
        └── authoring/build/validation/migration/execution workbench
            (never production or semantic authority by location alone)
```

The architecture preserves language-independent seams. Apache Arrow is evidence for a
language-agnostic columnar representation, Substrait for cross-language relational plans,
OpenTelemetry for distinct telemetry signal kinds, and PyPA for Python package/build metadata.
Those sources support interoperability boundaries; they do not make this implementation the owner
of portable data, plan, telemetry or domain meaning.

## Generated artifacts

- `product-binding.json`: sovereign product boundary, DDD surfaces, authority, states, refusals,
  non-collapse laws and withheld qualification gates.
- `component-bindings.jsonl`: exactly one role for every top-level `src/shannon_insight` component.
- `library-bindings.jsonl`: ten exact product-library scopes with types, operations, decisions,
  invariants, refusals, dependencies, evolution and compiler bindings.
- `research-python-roles.jsonl`: every Python file under `research/`, explicitly separated from the
  executable product and classified as authoring, builder, validator, migration, test, support or
  qualification harness.
- `evidence.jsonl`: claim-bound source evidence with explicit non-proofs.
- `summary.json` and `manifest.json`: computed counts and digest-bound provenance.

## Hard laws

```text
Python package                 != enterprise data-and-analytics platform
research builder               != production compiler
repository occurrence          != universal source-system registry
parser / AST library           != product boundary
relationship graph or tensor   != universal graph semantics
engineering signal             != universal business metric
engineering finding            != authorized remediation
unit-test success              != provider qualification
```

A new top-level implementation component or research Python file makes validation fail until it is
classified. Generated totals are computed from the checked-out repository; hand-edited counts have
no authority.

## Build and validate

```bash
python3 build_binding.py
python3 validate_binding.py
python3 build_binding.py --check
```

The binding remains unratified and unqualified. Independent implementation appraisal, portability,
physical provider evidence and executed vertical acceptance remain downstream gates.
