# Code generation, build, packaging and supply-chain atlas

Status: broad evidence-backed research candidate; **not adjudicated, implemented or complete**.

This directory specifies the provider-neutral universe after typed IR lowering. It is future
compiler input, not a compiler implementation and not a catalog of preferred tools. Large-language-
model and generative-AI code generation are explicitly out of scope. "Generation" here means
deterministic schema-, template-, AST- and compiler-driven transformation.

## The boundary after typed IR

```text
 semantic intent
      |
      v
 typed IR + discharged lowering decisions
      |                        (lowering stops here)
      +-------------------------------+
      |                               |
      v                               v
 target/backend contract        source-generation contract
      |                               |
 backend IR                     template + parameters
      |                               |
      |                         target-language AST
      |                               |
      |                         generated source + provenance
      |                               |
      +------------ compile/encode ---+
                       |
           object / core Wasm / component
                       |
                  link / assemble
                       |
       package or OCI artifact (immutable digest)
                       |
       +---------------+-------------------+
       |                                   |
       v                                   v
 deployment manifest                 release-channel record
       |                                   |
       +----------- authorized rollout ----+
                       |
                running occurrence

 dependency constraints --resolve--> locked dependency graph
 locked dependency graph + build graph --execute--> action results

 artifact closure --inventory--> SBOM
 build result --claim inputs/process--> provenance attestation
 statement --authenticate signer--> signed envelope + transparency material
```

The main lifecycle is accompanied, not replaced, by test/oracle receipts, documentation, license
and advisory review, hermeticity checks, independent rebuilds, caches, remote execution, artifact
repositories, release gates, rollback or roll-forward plans, decommission checks and evidence
bundles.

## Sovereign distinctions

These are machine-enforced in `compatibility-invalidation-laws.jsonl`:

- Typed IR lowering selects semantic operations and representations; backend code generation
  selects target encodings. A backend may not silently re-decide lowering semantics.
- A source template is a parameterized input; a generated source file is a materialized output;
  a compiled object or binary is another artifact again.
- A package is distributable material. A deployment manifest is desired controller input. A
  running occurrence is observed runtime state. None proves the next.
- Dependency resolution chooses versions, sources and features. Build execution runs actions over
  that resolved graph.
- Reproducible bits are evidence of byte equality under declared rebuild conditions, not proof of
  semantic conformance.
- An SBOM inventories components and relationships. Provenance claims how a digest-addressed
  subject was built. An attestation envelope authenticates statement bytes. These are separate.
- A verified signing identity establishes who signed under a trust policy, not that the claim is
  true or that the signer was authorized.
- Redeploying a prior artifact does not reverse database, queue, object-store or external state.
  State rollback, compensation and roll-forward repair require their own plan and evidence.

## Candidate decomposition

The 51 candidate bounded contexts cover:

- target contracts, backend selection, target features, IR-to-backend translation, native code,
  core Wasm, components, WIT/canonical ABI and ABI/FFI;
- source ASTs, templates, generated-source ownership, formatting, source maps and debug metadata;
- build graphs, invalidation, dependency/feature/toolchain resolution, Cargo workspaces and build
  scripts, polyglot builds, cross-compilation, linking and binary closure;
- package assembly, package metadata and versioning;
- schema/client/SDK, database migration, pipeline, configuration, infrastructure, deployment,
  test, fixture/oracle and documentation generation;
- licenses, vulnerability advisories, SBOMs, provenance/attestations and signing identity;
- hermeticity, reproducibility, local/remote caching, remote execution and repositories;
- release channels, rollout, artifact rollback, state rollback/roll-forward, decommission and
  evidence receipts.

Every context has two capabilities and two typed operations, one explicit no-hidden-default
decision, one compiler pass, one principal artifact, a generation requirement, an unbound offer
template, and a pure-kernel/toolchain-adapter boundary. Offers declare supported subsets, effects,
versions, configuration, exclusions and evidence; an offer is never provider qualification by
itself.

## Compatibility and invalidation model

Compatibility is directional and multidimensional. A binding checks structure, semantics, target
or execution environment, policy and evidence. Important checks include target-feature subsets,
ABI calling/layout/ownership/unwind exactness, core Wasm imports/exports, WIT world and canonical
ABI compatibility, schema writer/reader policy, public-surface SemVer and destination API versions.

Action identity must conservatively include every result-affecting input: typed-IR digest,
generator and pass implementation, transitive templates or schemas, decision set, resolved
dependency graph, feature closure, target/ABI/sysroot, toolchain and formatter digests, allowed
environment, and declared build-script inputs. A digest match permits cache reuse only inside an
accepted trust namespace; it does not prove that the key was complete.

## Library, toolchain and adapter seams

`library-toolchain-boundaries.jsonl` keeps normalization, compatibility checking and deterministic
planning in pure contracts. Process execution, file materialization, repositories, clocks,
randomness and networks are explicit ports. Adapters translate a plan to a pinned tool invocation
and return status, logs, observed environment/toolchain identity and output digests. Ambient
network, clock, environment lookup and mutable registry state are forbidden unless declared as
inputs.

Rust/Cargo is a detailed target because Cargo distinguishes resolver, features, target-conditioned
dependencies, workspaces, profiles, build scripts and package publication. The polyglot boundary
also retains native resolution/tool semantics for CMake/Meson, Go, npm and Python packages rather
than forcing them into a fictitious universal lock model.

## Proof and receipt contracts

The 23 receipt contracts define a claim, digest-addressed subject, identified producer, verification
method, required fields and explicit non-claim. They cover backend semantics, target compatibility,
deterministic emission, generated-source provenance, graph completeness, dependency and toolchain
locking, ABI probes, package/schema/migration checks, generated tests, hermeticity, reproducibility,
SBOM and provenance subject binding, signing identity, repository integrity, release authority,
rollout observation, rollback eligibility and decommission checks.

No receipt is promoted into universal truth. Scope, method, producer, subject, inputs, outcome and
limitations travel together. A signature receipt authenticates a statement; the claim still needs
claim-specific evidence and authorization policy.

## Target examples and refusals

- `examples/native-rust-service.json` follows an already-lowered Rust service through an
  `x86_64-unknown-linux-musl` contract, native object/link/package stages, an OCI image and a
  digest-pinned Kubernetes manifest.
- `examples/wasi-component.json` follows an already-lowered transform through core Wasm,
  componentization against a versioned WIT world, canonical ABI obligations and OCI artifact
  storage.
- `examples/negative-failures.jsonl` requires typed refusal for unsupported targets, CPU-feature
  mismatch, ABI unwind mismatch, undeclared `build.rs` inputs, breaking schema evolution,
  ambient-time nondeterminism, attestation-subject mismatch, mutable-tag identity and artifact-only
  rollback after irreversible state migration.

Examples contain illustrative digests and are test vectors for the atlas validator, not executable
release artifacts.

## Files

- `bounded-context-candidates.jsonl` — 51 provisional boundaries and ownership surfaces.
- `capabilities.jsonl`, `typed-operations.jsonl`, `decision-points.jsonl`,
  `compiler-passes.jsonl`, `artifacts.jsonl` — the 357 principal compiler-facing records.
- `generation-requirements.jsonl`, `backend-offer-templates.jsonl` — 51 exact requirements and 51
  provider/toolchain offer shapes; no binding exists until compatibility and evidence checks pass.
- `compatibility-invalidation-laws.jsonl` — 30 non-collapse, compatibility and action-key laws.
- `library-toolchain-boundaries.jsonl` — 51 candidate pure-kernel/effect-port seams.
- `proof-receipt-contracts.jsonl` — 23 scoped proof/evidence contracts.
- `sources.jsonl` — 108 primary research, open specifications and official project documents.
- `innovations-2021-2026.jsonl` — 25 recent non-LLM developments and their limited relevance.
- `gaps.jsonl` — 24 explicit blockers to a completion claim.
- `examples/` — two positive target traces and nine expected failures.
- `schemas/` — JSON Schema Draft 2020-12 shapes for every JSONL record kind.
- `manifest.json` — deterministic counts, evidence-role coverage and `completion_claim: false`.
- `build_atlas.py`, `validate_atlas.py` — deterministic generator and dependency-free validator.

## Evidence policy

| Evidence class | Supports | Does not support |
|---|---|---|
| open specification | semantics required of conforming implementations in that specification | implementation correctness or universal adoption |
| official documentation | mechanisms and constraints declared by the owning project | provider-neutral truth outside the documented version/scope |
| original research | authors' formalization, system or empirical finding | normative policy or universal boundary ownership |

The sources emphasize Rust/Cargo/rustc, SemVer, SPDX, CycloneDX, SLSA, in-toto, DSSE, Sigstore,
TUF, Reproducible Builds, Nix, Bazel and REAPI, OCI, WebAssembly/WASI/components, Kubernetes,
OpenAPI, AsyncAPI, JSON Schema, protobuf/gRPC, migration tools and original build/schema-evolution
research. URL presence is not a freshness or conformance audit.

## Rebuild and validate

From the repository root:

```bash
python3 research/domain_atlas/compiler/codegen_build/build_atlas.py
python3 research/domain_atlas/compiler/codegen_build/validate_atlas.py
```

The validator checks deterministic regeneration, every generated schema, unique IDs, internal and
source references, one-to-one context coverage for decisions/passes/artifacts/requirements/offers/
boundaries, candidate status, exact sovereign laws, authority diversity, recent non-LLM innovation
dates, both examples, expected refusals, honest gaps and the false completion claim.

Validated edition-1 counts as of 2026-08-25:

- 51 bounded-context candidates;
- 102 capabilities, 102 typed operations, 51 decisions, 51 compiler passes and 51 artifacts —
  **357 principal records**;
- 51 generation requirements and 51 backend/provider offer templates;
- 30 compatibility/invalidation laws and 51 library/toolchain boundaries;
- 23 proof/receipt contracts;
- 108 sources: 34 open specifications, 65 official-documentation records and 9 original-research
  records;
- 25 non-LLM innovations from 2021–2026, 24 honest gaps and 9 negative failures.

## Honest completeness limits

This corpus does not prove enumeration saturation, final domain ownership, source freshness,
provider conformance, backend correctness, ABI safety, cross-schema semantic equivalence,
migration reversibility, full build-script tracing, worker trust, cache-key completeness, SBOM
completeness, license/legal conclusions, vulnerability absence, signer authorization, release
fitness, state recoverability or consumer discovery before decommission. Compiler bootstrap trust
also remains open: pinning a compiler digest does not answer the trusting-trust problem.

The manifest therefore fixes `completion_claim` to `false`, and the validator requires the
enumeration, boundary-adjudication, source-freshness and bootstrap-trust gaps to remain explicit.
