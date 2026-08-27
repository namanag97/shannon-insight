# Executable conformance, evaluation and qualification system

Status: **candidate research corpus**, retrieved and generated 2026-08-25. This is not a test
runner, accreditation, certification, provider recommendation, or claim that any library, method,
provider, target or deployment is qualified. Its purpose is to make the missing evidence explicit
before a compiler is permitted to bind an offer.

The bundle is deterministic and does not depend on an LLM or agent. Agents may propose laws,
populations or counterexamples, but only accountable authority, deterministic checkers, retained
evidence and exact-scope receipts can affect qualification.

## The non-collapsible evidence ladder

```text
declaration
    |  "the fields exist"
    v
schema validation
    |  "the program is well-formed for this toolchain"
    v
compile / type check
    |  "a named semantic claim follows under stated assumptions"
    v
semantic law proof
    |  "these tests ran on this exact subject and population"
    v
executed test
    |  "these measurements occurred under this protocol"
    v
benchmark
    |  "this behavior was observed at this deployed occurrence"
    v
deployed observation
    |  "a demonstrably independent party appraised scoped evidence"
    v
independent appraisal
    |
    v
qualified for one exact scope -- never "universally qualified"
```

No lower rung implies a higher rung. A benchmark does not prove semantics. A production observation
does not prove causality or future behavior. Independent appraisal does not erase limitations.

## Exact qualification identity

```text
semantic requirement edition
        + law/oracle identity and edition
        + subject semantic identity
        + artifact digest
        + dependency-lock digest
        + configuration digest
        + build/toolchain/environment digest
        + provider offer snapshot
        + deployed target occurrence
        + population/generator/corpus identity
        + seed/schedule/fault plan
        + time and evidence-validity interval
        + accountable authority
        |
        v
qualification receipt for that exact tuple
```

Changing any supported component creates a new qualification question. Version-string equality is
not artifact equality; target-profile equality is not occurrence equality; list documentation is not
an execution receipt.

## Qualification lifecycle

```text
Candidate
   |
   | schema receipt
   v
StructurallyValid
   |
   | authority-owned law contract
   v
SemanticallySpecified
   |
   | exact execution receipt(s)
   v
Executed
   |
   | independent appraisal
   v
Appraised
   |
   | all mandatory gates, no unresolved counterexample
   v
QualifiedForExactScope ---- expiry ----> Expired
          |                                  |
          +------------ revocation ----------+
                           |
                           v
                        Revoked

Candidate ---- explicit risk decision ----> WaivedForExactScope
                                             (waived != pass)
```

Forbidden shortcuts include `schema-valid -> qualified`, `benchmark-pass -> qualified`, retrying a
failure until it disappears, treating timeout as pass, and turning a waiver into evidence.

## Oracle system

An oracle is a governed contract, not merely an expected value. Each oracle declares:

- authority and edition;
- input/test domain and partiality;
- `pass | fail | inconclusive | invalid` verdicts;
- assumptions, tolerances, uncertainty and acceptable residual risk;
- counterexample production and minimization;
- evidence needed to reproduce the verdict; and
- invalidation triggers.

Four complementary oracle patterns are instantiated for every context family:

```text
normative reference evaluator    specification/executable reference owns expected result
executable law predicate         domain authority owns invariant/relation
metamorphic relation             a valid transform predicts an output relation
independent comparison           separately developed implementations must agree or adjudicate
```

Agreement is not truth when implementations share code, dependencies, tests or the same erroneous
reference. `independence-criteria.jsonl` therefore checks code lineage, ownership, decisive
dependencies, test/oracle lineage, data/site independence, infrastructure correlation and conflicts.

## Test population and coverage

Passing sampled tests never means exhaustive correctness. Every population must declare included
and excluded partitions, sampling/generation method, seed policy, coverage measure and residual risk.
The 20 mandatory coverage axes include:

```text
semantic classes + exact boundaries + invalid inputs
states + transitions + histories + schedules
failure/recovery + time + scale + skew + missingness
deployment distributions + risk slices
version pairs + targets + configurations + dependencies
adversarial twins + historical replay/migration
```

For statistical and predictive claims, the authority must additionally own the estimand, sampling
frame, loss, error costs, alpha/beta or interval coverage, multiplicity policy, practical-equivalence
margin, missingness/censoring model, calibration criterion and shift policy. A high test score is not
deployment utility. Training/development resampling is not external validation.

## Outcomes, flakiness and counterexamples

```text
all gates pass                       -> Pass (only exact scope)
valid oracle finds counterexample    -> Fail
timeout / underpowered / flaky       -> Inconclusive
identity mismatch / stale / revoked  -> Invalid
active accountable waiver            -> Waived, never Pass
```

Retries append evidence; they never overwrite attempts. A flaky subject or harness retains every
seed, schedule, environment and outcome. A counterexample remains attached to the universal claim
until the defect is fixed, the claim is lawfully narrowed, or risk authority issues a scoped,
expiring waiver. Counterexample shrinking must preserve failure semantics, not merely minimize bytes.

## Compositional guarantees

```text
 component A: assumes XA, guarantees GA
 component B: assumes XB, guarantees GB
                         |
                         v
        prove GA satisfies XB (directionally)
        prove interface editions/carriers agree
        prove effects/retries/cancellation compose
        prove resource and interference budgets compose
        prove temporal/security/privacy/numeric laws compose
        execute end-to-end negative twins
                         |
                         v
             composite guarantee GA + GB
```

Two qualified parts do not automatically form a qualified whole. `composition-laws.jsonl` encodes
assume/guarantee, interface, effects, resources, time, failure, security, privacy, numerical,
statistical, multi-version and end-to-end laws.

## Coverage of test and evaluation methods

The 76 context families cover structural schema and type checks; algebraic/property/model-based,
metamorphic, differential, golden and normative conformance tests; parser/stateful fuzzing; mutation
and multi-axis coverage; deterministic simulation, chaos and failure injection; distributed safety,
replay, migration, restore and rolling upgrades; security, cryptographic-vector, privacy and
supply-chain testing; latency, throughput, memory, I/O, cost, energy, scaling and soak benchmarks;
numerical accuracy/stability/floating-point behavior; power, uncertainty, calibration, predictive
validation, shift and slice analysis; reproducibility; compatibility; accessibility/i18n/usability;
and data, temporal, geospatial, document, stream, graph, process-mining, optimization, SA-CCR and
acute-care examples.

For each family, the bundle produces four oracle contracts, three test-population techniques, one
authority-owned decision, one proof obligation and one coverage-matrix row. These are typed research
hypotheses, not fabricated executed results.

The first retained execution is under `executions/lp_solver_exact_scope/`. It runs OR-Tools
9.15.6755 GLOP/MPSolver and highspy 1.15.1 in separate pinned Python environments over six
continuous-LP fixtures. The safe objective/status profile passes for both, while precise
infeasible-versus-unbounded substitution fails for GLOP/MPSolver. A same-process native-library
negative twin also requires target-level process isolation for the observed pair. Four receipts are
retained at the executed-test layer; none is independently appraised, qualified or portable.

## Two unrelated verticals and their negative twins

### Banking SA-CCR

The positive path requires an exact regulation edition, legal-entity and netting-set identity,
temporal market/reference inputs, deterministic calculator artifact, numerical law suite,
independent implementation and reconciliation. It remains unqualified.

The negative twin refuses the assumption that equal counterparty display names imply equal legal
entities or netting sets. A schema-valid and numerically precise calculation can still be legally
false.

### Acute-care temporal event analysis

The positive path requires exact event/object identity, clinical-state semantics, code-system
editions, occurrence versus recording time, site-specific truth, temporal leakage checks, external
validation and clinical appraisal. This covers state-aware object-centric event analysis and temporal
event/knowledge-graph analytics without pretending a graph schema establishes clinical truth.

The negative twin refuses the assumption that documentation or database recording order equals
clinical occurrence order. This catches a causal/pathway error that can survive schema, compilation,
benchmark and ordinary prediction tests.

## Library boundaries and Rust applicability

The 48 candidate boundaries separate pure identities/digests/schemas/laws/oracles/generators,
runtime runners/corpora/measurements/replay, effect ports for target probes/faults/sandboxes, adapters
for toolchains/security/accessibility/attestation, and vertical oracle plugins.

Rust can make local illegal states difficult to represent:

```rust
enum Verdict { Pass, Fail(Counterexample), Inconclusive(Reason), Invalid(Reason) }

Candidate<S>
  -> StructurallyValid<S>
  -> SemanticallySpecified<S, LawEdition>
  -> Executed<S, ArtifactDigest, TargetOccurrence, Population>
  -> Appraised<S, Appraiser>
  -> QualifiedFor<ExactScope>
```

Newtypes separate artifact, configuration, dependency, target and oracle identities. Typestates
prevent promotion without receipts; enums preserve partial outcomes; sealed traits protect governed
law interfaces; deterministic ordered collections support canonical receipts; effect ports keep pure
qualification planning separate from execution.

Rust cannot establish that an oracle is the right business law, an implementation is truly
independent, a population is representative, a measurement is authentic, an expert has authority,
or a corpus is complete. Those remain evidence and governance questions.

## Machine-readable artifacts

- `metamodel.json` — constitutional laws, evidence ladder, state and verdict vocabulary.
- `sources.jsonl` — 124 scope-bound primary standards/specifications, original papers and official
  project/tool documents.
- `context-families.jsonl`, `oracle-contracts.jsonl`, `test-techniques.jsonl` — test universe.
- `decision-points.jsonl`, `proof-obligations.jsonl`, `coverage-matrix.jsonl` — compiler gates.
- `evidence-layer-contracts.jsonl`, `verdict-rules.jsonl`, `population-axes.jsonl` — evidence logic.
- `qualification-state-machines.jsonl`, `qualification-receipt-contract.schema.json` — lifecycle and
  exact receipt schema.
- `independence-criteria.jsonl`, `composition-laws.jsonl`, `waiver-contracts.jsonl` — promotion laws.
- `requirements.jsonl`, `offers.jsonl`, `requirement-offer-mappings.jsonl` — all illustrative offers
  intentionally non-bindable.
- `library-boundaries.jsonl`, `rust-applicability.jsonl` — implementation decomposition.
- `examples.jsonl` — two unrelated verticals plus their adversarial twins.
- `innovations-2021-2026.jsonl` — 32 dated, non-LLM research candidates.
- `gaps.jsonl` — open authority, population, composition, statistical and vertical gaps.
- `build_bundle.py`, `validate_bundle.py`, `manifest.json` — deterministic generation and checks.

## Build and validate

```bash
python3 research/domain_atlas/compiler/conformance_evaluation/build_bundle.py
python3 research/domain_atlas/compiler/conformance_evaluation/validate_bundle.py
```

The validator checks deterministic regeneration, unique identities, source and context closure,
thresholds, evidence-layer separation, mandatory families, fail-closed verdicts, receipt identity,
forbidden lifecycle shortcuts, independent vertical twins and that every illustrative offer remains
non-bindable. Its final line deliberately prints `0 actual offers qualified`.

## Honest gaps

This corpus does not prove complete oracle coverage, representative populations, actual provider
behavior, current target capacity, universal tolerances, end-to-end composition, genuine
implementation independence, vertical legal/clinical authority, or any concrete offer's fitness.
Those are not paperwork omissions: each needs exact execution, retained raw evidence, accountable
appraisal and a scoped receipt. The machine model makes those absences visible instead of silently
converting them to confidence.
