# Transformation Build Semantics

This universe replaces the two coarse labels `library.transform_manifest` and
`library.materialization` with five exact, provider-neutral library contracts:

```text
Batch Transformation Build product
│
├── Transformation Definition and Selection context
│   ├── library.transform_definition.compiler
│   └── library.transform_selection.closure
│
├── Transformation Materialization Planning context
│   ├── library.materialization.incremental_planner
│   └── library.materialization.mutation_protocol
│
└── Transformation Build Evidence context
    └── library.transform_build.evidence
```

The split is intentional:

- definition compilation owns the complete resolved project, not one invocation;
- selection closure owns invocation-specific set and graph algebra;
- incremental planning owns full/incremental/restatement validity over exact cuts and target state;
- mutation protocol owns conditional effect requests and receipt reconciliation, not target I/O;
- build evidence owns honest result, derivation and provenance assembly, not publication authority.

Imported neighbors remain separate: package closure, query-language compilation, source and target
catalog state, physical query/mutation execution, scheduling, quality authority, lineage storage,
attestation signing, provider qualification and publication acceptance.

## Evidence and method

The corpus uses 27 primary or official sources spanning dbt, Dataform, SQLMesh, Iceberg, Delta,
OpenLineage, SLSA, in-toto, W3C PROV, Bazel query algebra, reproducible builds, DBSP and
differential dataflow. Each source states both what it supports and what it does not prove.

All 12 mandatory boundary lenses are applied with references to the governed method ensemble.
The output contains 93 explicit no-default decisions, 39 typed pure operations, 32 negative twins,
three explicit boundary verdicts and five structurally matching but unimplemented compiler offers.

## Authority posture

```text
compile success != selected execution
selected execution != provider execution
provider success != materialization commit
materialization commit != quality pass
quality pass != publication approval
publication approval != business acceptance
```

Models and agents may propose attributed selectors, configurations, change classifications or
diagnostics. They cannot choose hidden defaults, waive refusals, authorize effects, accept evidence,
publish results or qualify implementations.

## Rebuild and validate

```bash
python3 research/domain_atlas/universes/transformation_build_semantics/build_corpus.py
python3 research/domain_atlas/universes/transformation_build_semantics/validate_corpus.py
```

This is a specified, unimplemented, open-world candidate corpus. It claims zero qualified or
portable implementations and does not claim the surrounding product ontology is complete.
