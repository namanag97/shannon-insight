# Core semantic primitives

This directory is a provider-neutral, open-world **candidate corpus** for the semantic
foundations that every enterprise data, analytics and application compiler will reuse. It does
not claim that the world is closed, that a cited standard is implemented, or that a proposed
bounded context is accepted domain truth.

The central result is negative as much as positive: there must not be one `common`, `types`, or
`utils` crate that silently owns all of these concepts. They are six neighboring universes with
different authorities, equality laws, lifecycles and failure catalogs.

```text
                         ENTERPRISE INTENT
             desired change / constraint / acceptance
                              |
               who/what?      |       when/for how long?
                    +---------+---------+
                    v                   v
           IDENTIFIER + IDENTITY       TIME
        namespace / resolution /   clocks / calendars /
        merge / split / version     valid + record time
                    \                   /
                     \                 /
                      v               v
                    QUANTITY + INFORMATION STATE
                units / money / probability /
                  uncertainty / missingness
                              |
                 who may decide or act?
                              v
                         AUTHORITY
               delegation / approval / issuance /
                    entitlement / revocation
                              |
                              v
                   DECISION -> ACTION -> EFFECT
                         |                  |
                         +---- feedback ---+
```

## Constitutional distinctions

These are compile-time or binding-time proof obligations, not documentation slogans:

```text
identifier       != identity
proof of control != subject identity
digest equality  != semantic equality or truth
merge            != proof of historical equivalence

instant          != local date-time
elapsed duration != calendar period
valid time       != recording / transaction time
clock reading    != causal order

number           != quantity
unit one         != absence of a quantity kind
probability      != confidence != score
missing          != zero
censored         != missing
money            != decimal

intent           != implementation
goal             != metric
requirement      != acceptance evidence
verification     != validation

authority        != responsibility
authentication   != authorization
approval         != issuance
policy decision  != enforcement
revocation       != deletion

recommendation   != decision
decision         != action
action           != effect
observation      != fact
association      != causal effect
rollback         != compensation
```

## What is modeled

### 1. Enterprise intent, outcome, constraint and acceptance

Owns actors and harmed parties, problem framing, mission and negative mission, goals,
objectives, outcomes, value and harm, assumptions and falsifiers, risks to objectives,
constraints, requirements and refinements, traceability, acceptance, verification, validation,
quality attributes, service objectives, tolerances, options, scope, non-goals and dependencies.

An intent is a desired change under an authority. A metric is evidence about that change. An
acceptance criterion is a predicate and evidence contract. None of these chooses an
implementation unless an authorized constraint says so.

### 2. Identifier, identity, namespace, version and resolution

Owns syntax, schemes, namespaces, naming authorities, assignment, resolution, dereferencing,
subject identity, attributes, evidence, proof of control, entity resolution, record linkage,
candidate matches, adjudication, equivalence claims, merge, split, supersession, aliases,
versions, editions, occurrences, revocation, canonicalization and correlation risk.

Identifier comparison is parameterized by scheme, namespace, edition and time. Entity resolution
produces an evidence-qualified claim or adjudication record; it cannot output metaphysical truth.

### 3. Temporal position, interval, calendar, clock and database time

Owns temporal reference systems, clocks and readings, instants, local dates and times, offsets,
zones, calendars, periods, durations, intervals and Allen relations, recurrence, business
calendars, precision, event/observation/valid/recording/transaction/processing/decision/correction
times, bitemporal history, causal clocks and clock uncertainty.

```text
modeled reality:       [----------- valid time -----------]
source observation:               observation_time
event occurrence:                     event_time
system knowledge:                         recording_time
database history:                         [-- transaction time -->
decision:                                        decision_time
late correction:                                          correction_time
```

No timestamp is accepted without a declared representation and time semantics. A local time in a
fold or gap must be resolved by policy; a timezone offset is not a timezone; and wall-clock order
does not prove causality.

### 4. Quantity, unit, scale, money, probability and partial information

Owns number representations, quantity kinds, dimensions, units and systems, scale types,
nominal/ordinal values, counts, measurands, results, uncertainty, precision/accuracy/resolution,
tolerance, money/currency/valuation, ratios/rates/proportions, index numbers, probabilities,
odds/likelihood, intervals, scores, missing/not-applicable/unknown/withheld states, censoring,
partial results, bounds and rounding.

```text
raw scalar
   |
   +-- quantity kind -- dimension -- unit -- scale
   |                                  |
   |                              conversion law
   |
   +-- measurement procedure -- uncertainty -- coverage semantics
   |
   +-- information state: observed | missing(reason) | censored(bound)
                           | withheld(authority) | not_applicable | invalid
```

A probability must expose the event/sample space and interpretation. A confidence interval,
credible interval and measurement coverage interval are separate carriers. Missingness mechanisms
are hypotheses, not values inferred from a null marker.

### 5. Authority, ownership, delegation and policy precedence

Owns authority sources, mandates, scope/jurisdiction, ownership, stewardship, responsibility,
accountability, delegation and subdelegation, roles, entitlements, capability grants, approval,
maker-checker, separation of duties, issuance, activation, suspension, revocation, expiry,
policies, applicability, combining/precedence, authorization decisions, obligations, enforcement,
exceptions, appeal and review.

```text
authority source -> mandate -> delegation -> scoped decision authority
                                         |
request + facts + policy ----------------+--> policy decision
                                                  |
                                       obligation | advice
                                                  v
                                    separate enforcement point
                                                  |
                                           effect receipt
```

The compiler must bind policy-authoring authority, decision authority, issuance authority and
effect authority independently. Deny/permit/indeterminate/not-applicable remain distinct, and
policy-combining order is an exposed decision.

### 6. Governed decision, action, feedback and effect authority

Owns decision requirements, information and knowledge inputs, models, rules, tables, evaluation,
recommendations, human judgment, decision records and explanation, action proposal,
authorization, command, execution, refusal, effect observation, outcome attribution, feedback,
control loops, interventions, holdouts, compensation, rollback/recall, appeal, override,
monitoring and decision quality.

```text
qualified evidence + policy + decision authority
                        |
                        v
                    DECISION --------> decision record
                        |
                 action proposal
                        |
              effect-authority check
                  pass / \ refuse
                      v
                    ACTION ----------> execution receipt
                        |
                        v
                 EFFECT OBSERVATION -- not automatically causal effect
                        |
           study design / baseline / counterfactual
                        v
                  OUTCOME APPRAISAL
                        |
                      feedback
```

Agents and LLMs may be replaceable providers behind recommendation, judgment-assistance or action
proposal ports. They do not change any authority, evidence, time, quantity, refusal, idempotency or
effect laws. The core remains deterministic where its contract says deterministic.

## Compiler contract

Every candidate bounded context emits four records:

```text
compiler_requirement
  semantic edition + scope + authority + time + equality + refusal policy
             |
             v
capability_offer
  typed construction + deterministic evaluation + explicit partiality
             |
             v
compiler_mapping
  bind only when identity and guarantees match; never bind by product name
             |
             v
proof_obligation
  input totality + round trip + equality soundness + freshness + idempotency
  + negative-twin rejection
```

The compiler may refuse, or it may insert a typed degradation only when the intent grants that
choice and names a residual owner. It may not turn absence of proof into a default.

## Library decomposition

The 60 candidate library boundaries use four layers:

```text
pure       semantic carriers, constructors, algebra, comparison, validation
runtime    clocks, ledgers, policy evaluation, effect execution and receipts
adapter    time-zone, identifier resolver, unit registry, provider/wire ACLs
test       law oracles, model/property tests, negative twins and conformance suites
```

Each library owns a narrow vocabulary, invariants and typed refusals. It does not own application
orchestration, provider selection, foreign DTO semantics or legal conclusions. Important seams
include `scoped-identifier`, `bitemporal-ledger`, `partial-information`, `policy-algebra`,
`action-authorizer`, `effect-port` and the six conformance libraries.

## Rust applicability

Rust is a useful target language, not the source of domain truth:

- opaque newtypes can prevent namespace, unit or policy-ID mixing;
- enums can make closed local lifecycle and refusal states exhaustive;
- typestates can enforce local construction and issuance prerequisites;
- traits and associated types can expose provider-neutral clocks, resolvers, registries, policy
  evaluators and effect executors;
- `PhantomData` can carry build-time-closed unit, scope or time-scale markers;
- `Result` carries legitimate refusals; `Option` is not a missingness model;
- serde DTOs stop at an anti-corruption layer before validated domain construction.

Distributed authority, time, uniqueness and effects still require runtime protocols and evidence.
An in-process Rust type cannot prove them.

## Two unrelated vertical proofs

The acute-care case requires a clinician-declared target, time-qualified observations,
unit-checked quantities, separate recommendation/decision/action authority, administration
evidence and effect review. Its negative twin refuses to treat a recommendation as a medication
order or correlation as treatment effect.

The electric-power case requires event identity, valid event intervals, interval-qualified meter
quantities, baseline uncertainty, dispatch authority, resource action, telemetry, counterfactual
effect estimation and settlement acceptance. Its negative twin refuses to treat dispatch receipt
as curtailed load.

## Artifacts

- `metamodel.json` — six families, representation/equality stacks and constitutional distinctions.
- `sources.jsonl` — 138 authority-scoped primary standards, specifications and original papers.
- `bounded-contexts.jsonl` — 171 candidate bounded contexts with explicit in/out scope.
- `semantic-records.jsonl` — 1,576 types, operations, decisions and executable-law candidates.
- `invariants-refusals.jsonl` — 342 exact construction and boundary laws.
- `lifecycles.jsonl` — 24 semantic/runtime/published/correction state machines.
- `context-acls.jsonl` — 25 neighboring-family anti-corruption contracts.
- `compiler-contracts.jsonl` — 684 requirement/offer/mapping/proof records.
- `library-boundaries.jsonl` — 60 pure/runtime/adapter/test candidates.
- `rust-applicability.jsonl` — 36 implementation mappings with explicit limits.
- `innovations-2021-2026.jsonl` — 35 non-LLM developments and their limits.
- `experts.jsonl` — 48 artifact-linked expert learning routes with a misuse warning for each.
- `vertical-examples.jsonl` — two unrelated end-to-end examples and negative twins.
- `gaps.jsonl` — 18 open problems that block or qualify compiler binding.
- `schema/`, `build_corpus.py`, `validate_corpus.py`, `manifest.json` — deterministic contract and validation.

## Generate and validate

```bash
python3 research/domain_atlas/universes/core_semantic_primitives/build_corpus.py
python3 research/domain_atlas/universes/core_semantic_primitives/validate_corpus.py
```

The validator checks schema conformance when `jsonschema` is available, thresholds, uniqueness,
referential closure, all mandatory distinctions, family coverage, compiler contract symmetry,
library-layer coverage, artifact-linked expert routes, non-LLM core separation, vertical negative twins, manifest hashes and
byte-for-byte deterministic regeneration.

## Honest limits

This is an evidence-backed candidate map, not completeness proof. It does not solve cross-domain
entity ground truth, clock trust, retroactive distributed correction, missingness identifiability,
currency valuation, policy-authority conflict, offline revocation latency, irreversible action
compensation or causal attribution. Those remain typed gaps with a compiler posture of refusal or
an explicitly authorized degradation and residual owner.
