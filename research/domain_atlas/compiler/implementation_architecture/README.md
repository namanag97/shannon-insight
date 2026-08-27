# Deterministic compiler implementation architecture

Status: **researched architecture candidate; not an implemented compiler and not a completeness
claim**. This bundle connects the existing corpus metamodel, canonical-reference mapper, IR/lowering,
binder/solver, provider/target qualification, codegen/build, conformance and change-intelligence
work into an implementable set of components and ports.

The architecture does not make an LLM the compiler. A model or agent may propose a declaration,
mapping, plan or diagnostic explanation through an optional port. Its output remains untrusted input
until deterministic validation, exact reference resolution, law checking and authority succeed.

## End-to-end architecture

```text
 authored intent + exact imports + registry/evidence snapshot roots
                 |
                 v
  +------------------------- FRONT END -------------------------+
  | bytes -> lossless CST -> declaration AST -> structural check|
  |             source anchors and omissions survive             |
  +-----------------------------+--------------------------------+
                                v
  +---------------- IDENTITY / ADJUDICATION ---------------------+
  | stable ID != edition != occurrence != digest                 |
  | namespace -> exact resolve -> canonical assertion/review gap  |
  | authority/delegation/precedence -> frozen compilation snapshot|
  +-----------------------------+--------------------------------+
                                v
  +---------------------- SEMANTIC CORE -------------------------+
  | typed n-ary hypergraph -> type/effect/lifecycle judgments     |
  | law obligations -> proved | contradicted | unknown            |
  +-----------------------------+--------------------------------+
                                v
  +---------------------- PASS / LOWERING -----------------------+
  | stage legality -> typed rewrites -> equivalence checking      |
  | semantic IR -> requirements; stable schedule + pass receipts  |
  +-----------------------------+--------------------------------+
                                v
  +---------------------- BIND / SOLVE --------------------------+
  | structural candidates -> semantic subsumption                |
  | -> hard SAT/UNSAT/UNKNOWN -> authorized Pareto/lexicographic  |
  | -> exact qualification -> resource admission                 |
  +-----------------------------+--------------------------------+
                                v
  +-------------------- PHYSICAL / CODEGEN ----------------------+
  | qualified algorithm/kernel/target -> effect-free plan         |
  | -> backend contract -> hermetic actions -> immutable artifacts|
  +-----------------------------+--------------------------------+
                                v
  +-------------------- EVIDENCE / CHANGE -----------------------+
  | artifact + proof + build + runtime receipts                  |
  | support-set graph -> invalidation -> recheck/rebind/migrate   |
  +--------------------------------------------------------------+

 Side planes:
   cancellation/resource budgets | security/capabilities | transactions
   deterministic cache           | diagnostics           | observability
   CLI == library semantics      | plugin sandbox        | conformance
```

The following boundaries are constitutional:

```text
parse != resolve != canonical adjudication
type derivation != law proof != external evidence
structural candidate != semantic satisfaction != global feasibility
feasible != preferred != qualified != admitted != deployed
stable identity != edition != occurrence != content digest
cache reuse != proof                 plan != effect authority
signature != truth != authorization  cancellation != UNSAT
```

## Hypergraph and persistence candidate

The semantic corpus is a typed hypergraph because many useful facts are n-ary and scoped. A simple
property edge such as `offer SATISFIES requirement` loses direction, edition, target, configuration,
authority, evidence and time. The canonical form therefore reifies the assertion:

```text
                 +-- role:requirement --> Requirement
RelationClaim ---+-- role:offer -------> Offer
   |             +-- role:target ------> TargetOccurrence
   +-- kind: directional_satisfaction
   +-- scope, authority, edition, status, valid/record time
   +-- evidence/support set
```

The storage candidate is not “pick a graph database.” It is:

1. canonical immutable records and receipts;
2. an append-only fact/commit log;
3. atomic snapshot manifests referencing exact transitive digests;
4. rebuildable relational/adjacency/reverse-support indexes;
5. optional RDF, property-graph or query-engine projections that never become semantic owners.

SQLite, embedded Rust KV stores, RDF systems and in-memory graph libraries are compared as
mechanisms. None is selected without exact scale, failure, durability, concurrency and recovery
qualification.

## Determinism and incremental computation

```text
QueryKey = digest(
  query identity + implementation edition/digest + typed key +
  registry/evidence snapshot roots + authority decision-set digest +
  target/configuration where applicable
)

query reads ---------------------------> support-set edges
old dependency graph + changed keys ---> transitive dirty closure
clean or reused checked results --------> new dependency graph

required law: incremental(snapshot X) == clean(snapshot X)
```

`rustc` red/green queries, Salsa, Buck2 DICE, Bazel Skyframe and Nix provide different useful
mechanisms. None supplies SAN's semantic authority or evidence model by itself. Equality-based
reuse is allowed only when the result's contract defines equality and the support set is complete.

## Rust design applicability

Rust is a good implementation language for the deterministic core because it can preserve several
local distinctions:

```rust
enum CompilationOutcome {
    Complete(ReleaseEvidence),
    Partial(PlanFragment, NonEmptyGap),
    Unsat(CheckedSufficientCore),
    Unknown(UnknownReason, PartialEvidence),
    Refused(NonEmptyDiagnostic),
    Cancelled(CancellationReceipt),
}

// Illustrative only: semantic IDs cannot be substituted for occurrences/digests.
struct SemanticId(String);
struct EditionId(String);
struct OccurrenceId(String);
struct ContentDigest([u8; 32]);
```

Use newtypes for identities, enums for partiality, sealed traits for constitutional meanings,
typestates for local phase ordering, immutable values, explicit effect traits, and canonical ordered
collections at serialization boundaries. Do not turn every domain concept into a typestate: dynamic
registries, authority and external evidence remain data checked at runtime.

Candidate mechanisms such as Rowan, Salsa, Petgraph, SlotMap, Serde, rkyv, Tower, Tokio utilities,
Wasmtime and embedded stores appear in `rust-applicability.jsonl` and `system-comparisons.jsonl`.
They are not selected by popularity. Selection requires semantic fit, failure behavior,
determinism, resource envelope, maintenance, evidence and a removable seam.

## Extension and agent isolation

```text
untrusted plugin/model/agent
          |
          v
 capability-limited proposal port --finite fuel/memory/time--+
          |                                                   |
          v                                                   v
 parse + exact resolve + deterministic checks          cancellation receipt
          |
          v
 authority decision -> effect intent -> separate executor -> effect receipt
```

Core crates never import an agent SDK. An optional adapter imports core public contracts. A plugin
cannot register a semantic kind merely by returning a string; it supplies an editioned manifest,
typed schema, laws/checkers, namespace and qualification evidence. Unknown semantics stay opaque and
cannot satisfy requirements.

## Files and counts

- `contexts.jsonl`: 66 bounded-context/component questions.
- `capabilities.jsonl`, `operations.jsonl`, `decision-points.jsonl`, `laws.jsonl`: 396 principal
  machine-facing records.
- `components.jsonl`, `ports.jsonl`: component ownership and typed input/output ports.
- `persistence-schema-candidates.jsonl`: 24 logical relations; implementation-neutral.
- `algorithm-pass-mappings.jsonl`: preconditions, postconditions, action keys and parallelism rules.
- `requirements.jsonl`, `offers.jsonl`: intentionally unbound architecture requirements/offers.
- `library-boundaries.jsonl`: 40 candidate pure/effect-port crate seams.
- `rust-applicability.jsonl`, `system-comparisons.jsonl`: applicability without popularity choice.
- `diagnostics.jsonl`: 60 stable machine diagnostic contracts.
- `api-contracts.jsonl`: 20 CLI and Rust library request/result contracts.
- `conformance-tests.jsonl`: 25 exact-boundary, property, fuzz, model, fault and differential tests.
- `performance-resource-model.jsonl`, `threat-model.jsonl`: finite work and trust boundaries.
- `innovations-2021-2026.jsonl`: 30 non-LLM developments and limited relevance.
- `prototype-traces.jsonl`: energy and banking SA-CCR positives plus negative twins.
- `sources.jsonl`: normalized primary/open/official/original sources reused from compiler research and
  architecture-specific official sources.
- `gaps.jsonl`: blockers that prevent an implementation/completeness claim.

## Build and validate

```bash
python3 research/domain_atlas/compiler/implementation_architecture/build_bundle.py
python3 research/domain_atlas/compiler/implementation_architecture/validate_bundle.py
```

The generator uses fixed upstream research files, canonical JSON, sorted identities and SHA-256
manifests. The validator checks thresholds, reference closure, phase laws, unbound offers,
positive/negative twins, open blockers, file digests and byte-identical regeneration.

## Explicit blockers

This bundle does not implement a parser, store, checker, solver, binder, backend or runtime. The
normative grammar, complete canonical registries, executable laws, exact provider occurrences,
qualification suites, target backends, performance envelope, security review, migrations and two
independent conforming implementations are absent. These are recorded as failures to claim
completion, not work the future compiler may infer.
