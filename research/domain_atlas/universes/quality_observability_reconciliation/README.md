# Quality, observability and reconciliation universe

Status: broad evidence-backed research candidate; **not adjudicated and not complete**.

This package maps the horizontal domain that starts with an intended use or declared obligation,
observes an identified data cut, detects conditions, separates evidence from judgment, and—only
with distinct authority—permits reconciliation, correction, release or certification. It is a
future intent-compiler input and candidate pure-library decomposition, not a vendor application.
Provider features appear only as implementation evidence. Large-language-model and generative
methods are excluded from the core.

```text
 intended use + risk                    producer / consumer declaration
          |                                         |
          v                                         v
 fitness requirement <----policy---- declared data contract
          |                                         |
          +-----------------+-----------------------+
                            v
                metric / rule / SLO definitions
                            |
                    typed subject + data cut
                            |
          +-----------------+--------------------+
          v                 v                    v
     conformance       profiling/change      telemetry + lineage
     validation          detection              observation
          |                 |                    |
          +-------- scoped evidence receipts ---+
                            |
                   detection / signal / break
                            |
                   authorized adjudication
                     /             \
              accepted/waived     defect confirmed
                                      |
                           proposal -> correction/restatement
                                      |
                         retest -> release/certification

 reconciliation is a sibling comparison path, not a synonym for validation:

 source observation --matching/tolerance--> accounting representation
          \                                      /
           +---- independent control truth -----+
```

## Concepts that must not collapse

- Validity is predicate satisfaction; quality is multidimensional; fitness is a decision for a
  named use and loss profile.
- Conformance compares to a declaration. Observability emits signals about behavior.
  Reconciliation compares identified populations under matching, tolerance and truth-role rules.
- Detection produces a signal. Adjudication assigns authorized meaning. Correction changes or
  restates data. These are three different authority boundaries.
- A declared contract is normative. An observed contract is sampled evidence. Observation never
  silently amends a declaration.
- Source truth records an originating event or observation. Accounting truth recognizes and
  periodizes it. Control truth independently tests the representation. Lawful disagreement among
  the three is possible and must be explicit.
- Assertion outcome (`pass`, `fail`, `skip`, `error`) and gate disposition (`block`, `warn`,
  `quarantine`, `permit`, `waive`) remain independent.
- Evidence, a signed receipt, a defect verdict, a certificate and proof of a compiler obligation
  are not interchangeable.

The machine-readable form of these and seven more distinctions is in
`semantic-distinctions.jsonl`; the validator makes the nine sovereign distinctions above
mandatory.

## Candidate decomposition

The 37 bounded-context candidates cover requirements and fitness; dimensions and metrics;
declared and observed contracts; schema and rule conformance; validation and test cases; profiling,
baselines, anomaly, shift and change-point detection; instrumentation, correlation, SLOs and
alerts; incident cases and defect adjudication; reconciliation definition, execution, breaks and
control truth; correction proposal/execution; quarantine, certification, evidence and waivers;
reference alignment, duplicate/entity resolution, completeness/timeliness, sampling, lineage
impact, policy and remediation verification.

Each context has:

- an explicit candidate aggregate, owned/excluded semantics and non-collapse laws;
- three provider-neutral capabilities and four typed operations;
- a compiler decision that cannot be supplied by a hidden provider default;
- invariants and typed pre-execution refusals;
- an intent requirement, provider-neutral offer template and total operation compiler mapping;
- one pure-kernel/effect-port library boundary candidate;
- bindings to types/shapes, pipelines, lineage, governance, semantic layer, runtime and industry
  cases.

The library boundaries deliberately keep provider SDKs, ambient clocks, ambient randomness,
hidden network access and mutable global state out of pure kernels. An effectful operation must
obtain an explicit port and produce a scoped receipt.

## Files

- `bounded-context-candidates.jsonl`, `capabilities.jsonl`, `typed-operations.jsonl` — candidate
  domain and operation surface.
- `decision-points.jsonl`, `invariants-refusals.jsonl`, `semantic-distinctions.jsonl` — semantics
  that the compiler must preserve or refuse.
- `requirements.jsonl`, `offer-templates.jsonl`, `compiler-mappings.jsonl` — intent requirements,
  unbound provider offers and total operation-to-binding mappings.
- `library-boundary-candidates.jsonl` — composable pure-kernel/effect-port seams.
- `cross-plane-mappings.jsonl` — explicit mappings to all seven adjacent planes and industry
  case candidates.
- `sources.jsonl` — primary standards, open specifications, regulatory material, original research
  and official implementation documentation with authority scope and limitations.
- `innovations.jsonl` — 2021–2026 developments; these establish mechanisms, not adoption or final
  boundaries.
- `gaps.jsonl` — explicit semantic, compiler, assurance, interoperability and completeness gaps.
- `schemas/*.schema.json` — JSON Schema Draft 2020-12 schemas for every JSONL record kind.
- `manifest.json` — deterministic counts, evidence-role counts and the false completion claim.
- `build_corpus.py` and `validate_corpus.py` — deterministic generator and dependency-free
  structural/reference/coverage validator.

## Evidence policy

Evidence roles are intentionally separate:

| Role | What it can support | What it cannot support |
|---|---|---|
| normative or regulatory authority | terms and obligations inside the issuer's scope | universal ownership outside that scope |
| open specification | interoperability and conformance semantics for that specification | proof that providers implement it correctly |
| original research | a method, guarantee or empirical finding reported by its authors | normative policy or universal fitness |
| official implementation evidence | that a project or product exposes a mechanism | a provider-neutral semantic contract |

All 76 evidence records are primary in this sense; implementation documentation is never counted
as universal authority. Sources are claim-scoped, dated and limitation-bearing. URL presence is not
an independent freshness or adoption audit.

## Compiler stance

```text
intent
  -> normalize vocabulary and truth roles
  -> bind subject, version, grain, population and data cut
  -> resolve every semantic decision
  -> type-check operation, policy, measure, tolerance and effects
  -> match only a qualified capability offer
  -> discharge invariants and evidence obligations
  -> emit plan + receipts
  -> otherwise emit a typed gap/refusal
```

There are no hidden defaults for null behavior, sampling, baseline, severity, tolerance, matching,
truth role, correction mode, certification authority or waiver scope. A provider's default is an
offer fact, not intent.

## Rebuild and validate

```bash
python3 research/domain_atlas/universes/quality_observability_reconciliation/build_corpus.py
python3 research/domain_atlas/universes/quality_observability_reconciliation/validate_corpus.py
```

The validator checks deterministic regeneration, the generated JSON Schemas, unique identities,
all internal and evidence references, total compiler mappings, pure/effect operation partitions,
all seven cross-plane links, candidate-only status, authority-role diversity, recent-innovation
dates and minimum-depth thresholds.

Validated edition-1 counts as of 2026-08-25:

- 37 bounded-context candidates;
- 111 capability candidates and 148 typed-operation candidates (259 combined);
- 37 decisions, 37 invariant/refusal sets and 16 non-collapse distinctions;
- 37 requirements, 37 offer templates and 148 total compiler mappings;
- 37 library boundaries and 37 seven-plane mappings;
- 76 primary sources: 21 normative, 24 open-specification, 3 regulatory, 8 original-research and
  20 official implementation-evidence records;
- 26 innovations from 2021–2026 and 28 explicit gaps.

## Honest completeness limits

This is deliberately an open-world candidate catalog. It does **not** prove enumeration saturation,
provider conformance, semantic equivalence among rule languages, statistical calibration,
fitness thresholds for any industry, legal or regulatory sufficiency, or independent review.
The context and library boundaries may split or merge. Source links have not all been independently
archived. Recent project documentation can change. The manifest therefore fixes
`completion_claim` to `false`, and the validator requires the independent-review and
enumeration-saturation gaps to remain explicit.
