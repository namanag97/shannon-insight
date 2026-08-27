# Session S2 — independent library, composition, and compiler contract candidate

## Commission

Produce an independent, globally researched candidate contract defining how accepted
domain semantics may become pure and composable libraries, how all legitimate
decisions are exposed, and how those libraries contribute to a generic compiler that
can close declared application intent without domain-name branching or hidden guesses.

Return this artifact:

```text
candidate-b-library-composition-compiler-contract-v0.1.0.zip
```

This is a contract and proof-fixture task. Do not implement the final SAN compiler or
mass-generate libraries. Do not request or use Session S1's output.

## Governing intent

The attached `BASE-RESEARCH-CONSTITUTION.md` is binding. Treat all SAN and data-library
archives as candidate evidence and stress inputs, not authority. Preserve the
distinction between semantic owners, effect/mechanism units, provider adapters,
compiler/tooling units, profiles, cards, compositions, application packages, crates,
and running services.

The target capability is declaration-driven composition across arbitrary enterprise
applications and data/analytics solutions. An industry solution may be assembled from
applications, capabilities, cards/profiles, libraries, foundations, effect/runtime
mechanisms, and provider offers, but this proposed ladder must be examined and
corrected rather than assumed.

## Research authority

Research the current Internet broadly and globally. Draw on language and compiler
design, package/module systems, software product lines, feature/configuration models,
constraint solving, effect systems, algebraic and property-based specification,
protocol/state-machine composition, capability/security systems, interface definition,
intermediate representations, build systems, reproducible supply chains, deployment
planning, and provider/resource negotiation. Include mature non-Rust ecosystems and
counterexamples. Record sources and contested design choices at claim level.

Rust may be a strong implementation language; it must not become the universal
metamodel. Specify language-neutral contracts and a Rust reference realization.

## Required architecture classifications

Define precise admission and non-equivalence rules for at least:

```text
semantic library family
foundation semantic library
effect or mechanism library
interface/contract-only unit
provider adapter or implementation offer
runtime/resource controller
compiler/tooling unit
profile or specialization
card, recipe or composition
application chassis and product/application package
industry solution pack
crate/package/module/workspace
portable IR, target-owned IR, target artifact and runtime evidence
```

The contract must allow zero, one, or many libraries per accepted bounded context and
zero, one, or many packages per library family. It must define evidence required to
justify each mapping.

## Library admissibility

Define a machine-checkable library-family contract that determines whether a candidate:

- has one explicit semantic or technical responsibility and named owner;
- exposes a complete, finite, typed decision surface including mandatory choices,
  defaults, constraints, invalid combinations, derivations, extensions, policies,
  migrations, and deliberately unselectable cases;
- owns invariants, refusal semantics, public types and compatibility commitments;
- separates pure semantics from time, randomness, storage, network, identity lookup,
  secrets, scheduling, telemetry and other effects through explicit capabilities;
- preserves determinism or declares bounded controlled nondeterminism;
- has no hidden global state, environment discovery, provider leakage, ambient I/O,
  family-name branching, or silent fallback;
- supports serialization, canonicalization, digest/provenance, versioning, migration,
  explanation, inspection and conformance;
- provides positive, negative, property, metamorphic, compatibility and composition
  tests capable of detecting vacuous implementations;
- states resource, safety, security, privacy and operational obligations without
  claiming responsibility it does not own.

Define how responsibility completeness, decision completeness, behavioral
completeness, composition closure, and execution evidence differ.

## Compiler contribution contract

Define a universal, typed contribution envelope through which a family can publish
what the compiler needs without making the central compiler understand that family by
name. It must be able to represent at least:

```text
requirements and obligations
offers and implementation/provider capabilities
decision domains, selections and selection authority
constraints, compatibility and conflicts
owned and imported capabilities
artifacts and schemas
portable semantic nodes/edges/hyperedges
effect and resource requirements
target-lowering requirements
diagnostics, refusals and explanations
proof obligations, provenance and evidence posture
extensions, migrations, deprecations and supersession
```

Define the necessary algebras and laws for merge, meet/join or compatible combination,
selection, conflict, refusal, explanation, fixed-point closure, and deterministic
canonicalization. Prove or explicitly bound termination, order independence,
monotonicity, idempotence, and conflict preservation where they are claimed.

An omitted required decision must refuse; it must not become a guessed default. A
default is a versioned semantic decision owned by someone, not compiler convenience.

## Artifact and execution ladder

Define the distinct artifacts, owners, inputs, outputs, versioning, provenance, and
proof transitions from declared intent through:

```text
parsed/declarative source
verified owner-local requirements and selections
closed family plans
cross-family semantic closure
portable application IR or graph
target-specific lowering inputs and target-owned IRs
sealed target artifacts and deployment plans
runtime/resource/provider binding
observed runtime evidence and assurance results
```

Adjudicate whether one universal IR is possible or whether a portfolio of owner-typed
IRs with explicit bridges is required. Keep semantic closure separate from physical
provider selection. Define where secrets and private binding material may enter and
how they remain outside portable public semantics.

## Recursive composition

Define how accepted units can form reusable profiles, cards, capabilities,
applications, product packages, and industry solutions without creating new semantic
authority by aggregation. Specify composition identity, dependency and conflict
handling, overrides, extension boundaries, provenance, compatibility, partial
configuration, explanation, and recursive sealing. Correct the proposed vertical
ladder when evidence demands another structure.

## Proof obligations and stress cases

Provide executable or machine-checkable reference fixtures across dissimilar domains,
including Identifier, accounting/ledger, work/case, accessibility, runtime/resource
planning, and data engineering/analytics. Include at least one mixed-industry
application composition and negative twins for:

```text
same family name with incompatible semantics
valid schemas with missing semantic decisions
one context incorrectly forced into one crate
provider choice leaking into portable closure
runtime evidence claimed from compilation alone
conflict erased by merge order
hidden default changing across editions
effectful implementation masquerading as pure semantics
profile or application package admitted as a semantic owner
```

The Rust reference must demonstrate types, traits, typestates or finite machines,
sealed/public boundaries, feature/configuration posture, error/refusal types, effect
ports, canonical serialization, and property/conformance tests. It is evidence for the
contract, not the final compiler.

## Deliverable and acceptance

Return a deterministic ZIP containing the normative library/composition/compiler
contract, closed schemas and vocabularies, decision and contribution models,
admissibility rules, artifact DAG, IR portfolio decision, runtime/provider boundary,
Rust reference fixtures, positive/negative test vectors, evidence/conflict/gap ledgers,
generated documentation, manifest, checksums, and an executable validator.

The final response must state the archive digest; major architecture decisions and
rejected alternatives; validation and proof checks actually executed; stress results;
disagreements with attached SAN candidates; known gaps; and whether the candidate is
ready for blind adjudication against an independent sovereign semantic-domain contract.

