# Governed reusable-library contribution registry

This directory is the normalized research boundary between the domain atlas and later Rust or
multi-language implementation work. It contains no application code and makes no claim that any
candidate has been implemented or qualified.

Current generated snapshot: 846 contributions, 653 design contexts, 596 families, 963
context-to-library relations, 2,417 operations, 196 dependency edges, 297 kernel mappings and 89
duplicate/conflict reviews: 88 open and one adjudicated as explicit coexistence. All source contributions now name a semantic owner; this does not
promote any candidate to an adjudicated, implemented, qualified or portable state.

The legacy compiler `library-contribution.schema.json` and each governed universe library registry
(`library-*.jsonl` or `libraries.jsonl`) are read-only source projections. Their local shapes and
status words are preserved in the crosswalk, but they are not treated as this registry's canonical
schema. A filename convention is never evidence for or against a semantic library boundary.

## Identity and dependency DAG

```text
bounded context + authority
          |
          | owns meaning
          v
   library family/class ---------> product
          |                         ^
          | contains                | packages (never owns meaning)
          v                         |
 library contribution contract ----+
     |       |        |
     |       |        +--> capability requirement --match--> capability offer
     |       |                                             (portable only with >=2
     |       |                                              independent qualified impls)
     |       |
     |       +--> operation-to-library / kernel-to-library
     |
     +--> implementation artifact --contained by--> crate/package
                   |                                  |
                   | compiled by                      | resolves feature/dependency graph
                   v                                  v
              build artifact ----------------------> SBOM/provenance/advisories
                   |
                   | deployed as
                   v
             deployed service --> runtime effect receipts + resource observations

Pure contribution:
  typed input -> law-governed operation -> typed outcome | typed refusal

Effectful contribution:
  typed input -> pure decision -> effect intent -> runtime adapter -> effect receipt
```

An implementation, crate/package, build, deployed service, and product have separate identities.
The presence of code, a crate, a successful build, or a deployed endpoint is not proof that the
library laws conform. Rust source compatibility, semantic compatibility, wire compatibility, ABI
compatibility, MSRV, target support, feature compatibility, and behavioral compatibility are also
separate dimensions.

## Boundary admission and refusal

A contribution is admitted only as a candidate when the source names a semantic owner and a
provider-neutral responsibility that can be tested and replaced independently. Final adjudication
still requires cohesion, ownership, dependency-cycle, law, and substitution review.

The registry explicitly refuses:

- one library per vocabulary term;
- vendor SDKs, framework utility bags, or product suites as semantic families;
- crate/package, generated SDK, deployment chart, microservice, or database driver identity as
  sufficient proof of a library boundary;
- ambient clock, randomness, environment, filesystem, network, process, or global mutable state in
  a pure boundary;
- a portable offer based on one implementation;
- existing code or green tests as law conformance outside their exact evidence scope.

Each refusal is a versioned `typed_gap` with a resolution condition, so later evidence can resolve
it without silently weakening the rule.

## What a contribution exposes

Every normalized `library_contribution` contains:

- exactly one semantic owner plus contributing contexts, responsibilities, exclusions, boundary
  rationale, and removal/substitution seams;
- exact public type, trait, and operation identities with typed inputs, output, purity, effect
  intent/receipt types, refusals, and errors;
- explicit decisions and configuration types with no provider- or environment-derived semantic
  defaults;
- laws, invariants, deterministic posture, sync/async mode, cancellation, concurrency, thread
  safety, and finite time/state/resource contracts;
- separate ABI, serialization, DTO, and anti-corruption boundaries;
- an additive feature/dependency graph and cycle policy;
- MSRV, Rust edition, `no_std`, target, provider, and target-capability slots without inventing
  implementation facts;
- license, advisory, SBOM, reproducibility, provenance, unsafe, FFI, and generated-code policy;
- semantic/API/behavior/wire/ABI/MSRV/target/feature compatibility, migration, deprecation, and
  evidence invalidation expectations;
- law, fixture, fuzz, model, property, and differential conformance classes;
- scoped evidence and versioned gaps.

## Generated artifacts

`registry.jsonl` is the canonical ordered stream. The smaller JSONL files are deterministic
materialized views by record kind:

```text
metamodel.json                         closed identity and non-collapse laws
library-registry.schema.json           JSON Schema Draft 2020-12 union
library-design-contexts.jsonl          bounded-context/library design contexts
library-families.jsonl                 owner-scoped compatibility families
library-contributions.jsonl            normalized reusable contribution candidates
artifact-kind-definitions.jsonl        implementation/package/build/service/product distinctions
context-to-library.jsonl               context ownership/contribution links
operation-to-library.jsonl             typed operation links
kernel-to-library.jsonl                algorithm/runtime kernel links
dependency-edges.jsonl                 typed candidate dependency graph
capability-requirements.jsonl          implementation requirements
capability-offers.jsonl                withheld/portable offer state
decisions.jsonl                        typed library architecture decisions
evidence-sources.jsonl                 primary/official research sources
innovations-2021-2026.jsonl            evidenced non-LLM innovations
typed-gaps.jsonl                       boundary refusals and resolution conditions
review-queue.jsonl                     duplicate/conflict adjudication queue
local-crosswalk.jsonl                  every local source line to normalized identity
manifest.json                          source inventory, counts, digests, quality gates
exact_api_closure/                     deterministic priority queue covering every exact-API gap
contract_generation/                   archetypes, family constitutions, boundary clusters and batch work packages
```

The schema also defines concrete future `implementation_artifact`, `package_artifact`,
`build_artifact`, `deployed_service`, and `product` records. None are emitted today because the
corpus does not bind digest-addressed implementation and conformance evidence.

## Honest current status

At the last deterministic generation:

```text
universe library-registry artifacts inventoried        53
source candidate registries                            44
local source schemas marked noncanonical                8
provider qualification contracts inventoried            1
source candidates crosswalked                         846
normalized contribution candidates                    846
explicit boundary-refusal gaps                         12
contributions or explicit typed gaps                   858
bounded-context/library design contexts                653
library families                                       596
typed architecture decisions                            32
primary/official evidence sources                       84
non-LLM innovations from 2021-2026                      25
open duplicate/conflict review items                    88
adjudicated explicit-coexistence review items             1
portable offers                                          0
```

Contribution statuses are candidate, specified-but-unimplemented, observed-but-unverified, or
rejected for a missing semantic owner. The current snapshot contains no missing-owner rejection;
the 33 data-shape, 30 optional model-extension and 60 predictive-library source projections now
carry their already-modeled or explicitly adjudicated owner references. Every contribution also
has an explicit semantic/policy/algorithm/oracle/port/runtime/adapter class and
pure/effect-intent/effectful boundary. Three exact reusable reference-closure contracts now own API
description parsing, provider-offer closure and package closure; query compilation composes the
existing query syntax and binding libraries. Remaining contribution gaps include 674 exact API
contracts, zero unresolved shared-owner closures, 473 source-declared gaps and implementation evidence for
all 846 contributions. Missing owners, missing class/effect boundaries and dangling dependency
identities are hard-gated at zero; those structural milestones resolve no implementation or
qualification evidence.
All 846 capability offers are withheld because the registry binds zero qualified independent
implementations. A portable offer requires at least two implementations with different controlling
maintainers, no shared implementation source, and independent build and conformance evidence.

## Rebuild and validate

Run from the repository root:

```sh
python3 research/domain_atlas/compiler/library_registry/generate_registry.py
python3 research/domain_atlas/compiler/library_registry/validate_registry.py
uv run --with jsonschema python research/domain_atlas/compiler/library_registry/validate_jsonschema.py
python3 research/domain_atlas/compiler/library_registry/contract_generation/build_program.py
python3 research/domain_atlas/compiler/library_registry/contract_generation/validate.py
```

The generator sorts source paths, identities, keys, arrays derived as sets, and output records. It
uses a fixed research date and emits a SHA-256 manifest. The first validator is dependency-free and
checks the JSON Schema constraints used by this corpus, manifest digests, partitions, current source-file
coverage, unique identities, graph references and acyclicity, all quantitative gates, the six
conformance classes, explicit effect/resource/boundary fields, and the two-independent-
implementation portability rule.

The second asks the reference `jsonschema` implementation to check the schema itself and validate
every record against Draft 2020-12.

The exact-API closure program ranks all remaining gaps by retained-product use, unrelated-vertical
reuse, dependency centrality, kernel use and effect risk. Its queue is complete rather than sampled:
66 items are currently P0 product-and-vertical dependencies, 281 P1 product dependencies, 177 P2
shared-graph dependencies and 150 P3 remainder items. Priority changes work order, never the closure
contract.

The bulk contract-generation program makes the backlog tractable without manufacturing semantics.
It classifies every open item against 19 structural archetypes, creates 23 family-constitution work
items, assigns every candidate to one of 460 owner-scoped boundary-falsification clusters, emits
146 bounded cross-owner collision signals, and arranges 57 family/lane work packages into seven
dependency waves. Archetypes generate obligations only. Boundary adjudication and
owner-authored family and library semantics remain prerequisites to publishing a source contract;
therefore none of these generated proposals closes a canonical exact-API gap.

The first boundary wave separately adjudicates all 33 candidate data-shape libraries against a
five-layer shape/standard-profile/representation/codec/provider constitution and batches owner
ratification into five semantic-kind work packages. This prevents format names and provider effects
from being mass-produced as domain semantics. The decisions remain candidates until owner
ratification and exact source-contract publication.

Every open exact-contract candidate also has a non-authoritative 16-axis semantic signature. The
axes cover semantic object and role, identity/equality, grain/cardinality, state/change, time,
order/topology, partiality/uncertainty, authority/trust, effect boundary, representation,
composition, compatibility/evolution, resources/failure, evidence/conformance and
privacy/security/safety. The 109 controlled facet modules let families reuse laws while retaining
per-library applicability and exceptions.

Running the generator twice without source changes must produce the same manifest and bytes. If an
active universe adds or changes a `library-*.jsonl` or `libraries.jsonl` file, validation fails until
regeneration, which makes crosswalk drift visible rather than silently omitting new candidates.

## Research basis

The evidence registry uses authoritative Rust Project material for API design, Cargo metadata,
features, dependency resolution, SemVer compatibility, MSRV, targets, unsafe, FFI, panic/unwinding,
and documentation tests; W3C WebAssembly/WASI and Bytecode Alliance material for WIT, Canonical ABI,
components, async/cancellation, and generated bindings; and primary/official specifications for
SemVer, JSON Schema, OpenAPI, protobuf, IETF wire/error formats, SPDX, CycloneDX, SLSA, in-toto, TUF,
Sigstore, OSV, RustSec, Reproducible Builds, NIST SSDF/C-SCRM, ISO/IEC/IEEE 42010, Parnas information
hiding, and Cockburn ports/adapters and component strategy.

Tool repositories such as `cargo-semver-checks`, `cargo-vet`, `cargo-auditable`, and
`cargo-cyclonedx` are evidence about those tools only. They are not promoted into Rust language law
or semantic-conformance proof.
