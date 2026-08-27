# Method, algorithm, kernel, and implementation universe

This universe closes the layer between a named analytical practice and executable code. It is an
open, evidence-backed candidate corpus—not a claim that every future method or implementation has
been enumerated.

```text
enterprise question + decision
              |
              v
     analytical practice                 why the analysis exists
              |
              v
        study design                     what observations can answer it
              |
              v
 estimand / measure / decision target    the exact quantity or result sought
              |
              v
        method family                    assumptions + result/evidence contract
              |
       +------+-------+
       |              |
       v              v
 formula / model    estimator            mathematical meaning / fitted procedure
       |              |
       +------+-------+
              v
          algorithm                      finite procedure and termination law
              |
              v
      numerical/data kernels             typed executable primitives
              |
              v
 reusable library contribution           API + effects + removal seam
              |
              v
 versioned provider offer                actual target support + limits + evidence
              |
              v
 configuration + qualification           explicit decisions and conformance receipts
              |
              v
 fitted artifact / result / evidence      reproducible output with claim boundary
```

## Terms that must not be collapsed

| Term | Owns | Does not own |
|---|---|---|
| Analytical practice | intent, question, decision proximity | implementation |
| Study design | assignment/sampling/observation plan and identification argument | numeric solver |
| Estimand | exact target quantity and population/time/grain | estimator |
| Formula | declarative mathematical expression and its domain | execution strategy |
| Model | a declared representation of a system or distribution, possibly fitted | universal truth |
| Estimator | procedure mapping observations to an estimate | the estimand's meaning |
| Method family | assumptions, applicability, output and evidence contract | provider identity |
| Algorithm | finite procedure with complexity, state and termination semantics | business intent |
| Kernel | typed low-level primitive over concrete representations | analytical conclusion |
| Solver | orchestrated algorithm system for a model class | model semantics |
| Library | reusable implementation contribution with an explicit effect boundary | product promise |
| Provider offer | versioned, target-qualified capability and limits | semantic ownership |
| Product | packaged outcome, operating obligations and user experience | primitive taxonomy |

`mean`, for example, is simultaneously a mathematical formula, an aggregation operation and a
possible kernel. “Compare average length of stay after an intervention” is an analytical practice
and study design. The compiler must retain those different identities and connect them with typed
edges.

## Compression boundary

Compression is required by analytical systems but is not an analytical method:

```text
semantic value/shape
   -> representation encoding (dictionary, delta, RLE, bit packing)
   -> compression codec (zstd, Snappy, ...)
   -> framed bytes + integrity metadata
```

Encoding can change random access, predicate pushdown and numerical interpretation. Compression can
change CPU, memory, latency, transfer and decompression-bomb risk. Both are physical-data kernel
contracts owned by representation/storage/transport contexts. Analytical plans may require them, but
method code cannot silently choose them.

## Compiler laws

1. Resolve the practice, study design and estimand before selecting a method.
2. Refuse a method when its identification, sampling, time, missingness or independence assumptions
   are unproved or explicitly waived by authorized policy.
3. Lower method requirements to algorithms and kernels by typed contracts, never by package name.
4. Bind precision, null/NaN behavior, ordering, randomness, determinism, device, layout, cancellation,
   memory and work budgets explicitly.
5. A provider document is offer evidence, not a conformance receipt for a deployed binary.
6. A fitted artifact carries method, data, code, configuration, provider, target and seed digests.
7. A result preserves partiality: invalid, unsupported, not-identified, non-converged, cancelled and
   numerically suspect are not aliases for success.
8. Evaluation data must be separated from fitting/tuning data according to the study contract.
9. Approximation and floating-point error bounds cannot be strengthened during lowering.
10. Unknown meaning or an unqualified implementation produces a typed compiler gap.

## Coverage

The current candidate corpus covers descriptive, inferential, causal, experimental, forecasting,
anomaly/change, process, data-quality, reliability, queueing, simulation, graph, spatial, text,
classical search, signal, image and semantic-metric methods. Operations research is mapped to the
dedicated `../operations_research/` corpus rather than copied here.

The library/provider seeds include scientific-statistics, process, graph, spatial, search, signal,
image, data-quality, semantic-metric, array, linear-algebra, Arrow compute and codec implementations.
They are representative qualification targets, not vendor rankings.

Process coverage deliberately exposes separate contributions for event/object projection, case
projection, State-Aware OCEL derivation, temporal Event Knowledge Graph projection, discovery,
conformance and performance analysis. `OCEL 2.0 != OCED != State-Aware OCEL != temporal EKG`, and
none of those representation contracts is a process-discovery or conformance algorithm. The older
`process_methods` record remains a coarse compatibility facade and must not be bound when one of the
exact contracts is required.

The same rule now applies to six additional compatibility facades:

- statistics splits into distribution algebra, descriptive summaries, tests/resampling,
  regression/GLM, survival/event-history and probabilistic inference;
- causal analysis splits into graph/assumption identification, effect estimation and
  refutation/sensitivity;
- forecasting splits into time-series/index and information-cut semantics, estimator execution,
  rolling evaluation/calibration and reconciliation; and
- anomaly/change splits into baseline artifacts, anomaly detectors, change-point detectors and a
  non-authoritative finding/adjudication handoff;
- graph splits into representation/view semantics, traversal/path algorithms, centrality,
  community/partition algorithms and GraphBLAS/semiring runtime kernels; and
- spatial splits into CRS/support semantics, coordinate transformation, vector
  geometry/topology, raster/grid methods and spatial statistics.

The broad `statistical_estimators`, `causal_methods`, `forecasting_methods`, `graph_methods` and
`spatial_methods` records remain only as compatibility facades. Product binding maps are forbidden
from using them as exact contracts.

Experimentation is not a feature-flag facade. It composes six independently governed surfaces:
analysis design; prospective protocol/eligibility; a total assignment state machine;
randomization/allocation algorithms; actual exposure occurrences; and immutable analysis
cuts/stopping rules. Statistical tests and causal estimation bind after those contracts. In
particular, `assignment != exposure != metric observation != analysis cut != estimate != decision`.

Document analysis is also decomposed rather than hidden behind “text analytics.” Container/profile
semantics, a positioned content graph, parser adapters, layout, OCR, table extraction, form
extraction, provenance/loss, classification, information extraction and extraction evaluation are
independent contracts. This keeps a parser pass, an OCR hypothesis and an accepted business fact
from becoming aliases.

LLM, prompt, RAG, generative-model and agent-memory semantics are forbidden from the deterministic
method core. They may be selected through the removable `../model_agent_extension/`, whose
proposals must return through the same schemas, validators, authority gates and evidence contracts.

## Artifacts

- `classification-axes.json` — orthogonal classification axes and anti-cross-product laws.
- `method-families.jsonl` — provider-neutral method-family contracts.
- `implementation-records.jsonl` — formulas, models, estimators, algorithms and kernels.
- `library-boundaries.jsonl` — reusable contribution boundaries compatible with the shared compiler
  library contract.
- `compiler-requirements-offers.jsonl` — requirement and provider-offer seeds compatible with the
  shared compiler binding contract.
- `decision-points.jsonl` — explicit decisions compatible with the shared decision-point contract.
- `qualification-receipts.jsonl` — qualification profiles and unexecuted receipt templates; no
  template falsely claims a pass.
- `artifact-result-contracts.jsonl` — provider-neutral study, plan, fitted-state, result,
  evaluation and evidence-envelope contracts.
- `sources.jsonl` — primary papers, standards and maintained official documentation.
- `innovations.jsonl` — non-LLM 2021–2026 innovation/adoption records with limitations.
- `gaps.json` — explicit open-world, evidence and implementation gaps.
- `build_corpus.py` — reviewable authoring source and deterministic generator.
- `validate_corpus.py` — structural, referential, coverage and exclusion checks.

Regenerate and validate:

```bash
python3 research/domain_atlas/universes/method_kernels/build_corpus.py
python3 research/domain_atlas/universes/method_kernels/validate_corpus.py
```
