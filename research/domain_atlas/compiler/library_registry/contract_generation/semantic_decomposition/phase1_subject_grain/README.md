# Phase 1 — subject, identity/equality, and grain/cardinality

This candidate constitution answers three questions before any library API or compiler IR is
generated:

```text
What exact subject?  ×  under what identity/equality relation?  ×  at what grain/cardinality?
```

It prohibits universal `Object`, `Id`, `Record`, `Collection`, equality and grain facades. It
instead exposes nine equality layers, nine independent grain coordinates, explicit cardinality and
boundedness states, total comparison/regrain outcomes, adapter proof obligations and typed compiler
refusals.

Six bounded primary-source claims support the seams using RDF 1.2, RFC 3986, SHACL, Apache Beam,
OpenTelemetry Metrics and Apache Arrow. Each claim records its authority limit. The constitution is
an evidence-backed candidate pending named-owner ratification; it generates no exact Rust API,
canonical mutation, implementation qualification or closed gap.

Run:

```sh
python3 research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/phase1_subject_grain/build_phase1.py
python3 research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/phase1_subject_grain/validate.py
```
