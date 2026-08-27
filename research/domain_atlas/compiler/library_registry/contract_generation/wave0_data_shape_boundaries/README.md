# Wave 0 — data-shape boundary adjudication

The 33 `candidate.lib.*` records are not accepted as reusable-library boundaries in their current
form. Every one owns both logical/domain shape semantics and a representation profile; several also
mix parsing, serialization, protocol execution or provider concerns.

This adjudication applies a five-layer constitution:

```text
domain / observation semantics
        ↓ explicit mapping
published language / standard logical model
        ↓ preservation + loss contract
representation profile
        ↓ codec/container/layout contract
bytes and physical layout
        ↓ effect port
provider runtime adapter
```

Thirty-two boundaries are proposed for split and no-alias rename. The glTF candidate is not admitted
as a second logical shape alongside the scene graph; it becomes a representation/profile
conformance contract bound to scene-graph semantics. Twenty-three existing crosswalks survive as
independent, unqualified representation-binding records.

Ratification is also batched by semantic kind into five work packages. The packages share the
questions, allowed dispositions and exit evidence while preserving one independently traceable
decision per candidate. This is the scalable unit of human/domain-owner review: reviewers decide a
family rule once and record only genuine exceptions, rather than redrafting the same boundary
analysis 33 times.

These are evidence-adjudicated candidates, not silent canonical mutations. Canonical shape owners
must ratify broader/specialization relations, affected family owners must accept replacement
identities, and every retained layer still requires an exact source contract. No implementation or
provider is qualified and no exact-API gap is closed by this bundle.

Run:

```sh
python3 research/domain_atlas/compiler/library_registry/contract_generation/wave0_data_shape_boundaries/build_wave0.py
python3 research/domain_atlas/compiler/library_registry/contract_generation/wave0_data_shape_boundaries/validate.py
```
