# What is still missing

The project currently has a strong **enumeration and research spine**, not a finished platform or
compiler. The main mistake to avoid is treating all missing pieces as “libraries.” They occupy
different semantic and lifecycle layers.

```text
BUSINESS / VERTICAL MEANING
  industries -> analytical cases -> decisions/actions -> acceptance evidence
                         |
HORIZONTAL ANALYTICAL MEANING
  practices -> study/method contracts -> formulas/metrics -> uncertainty/evaluation
                         |
DATA MEANING AND REPRESENTATION
  sources -> observations/types/shapes -> schemas -> encodings/layouts/compression
                         |
LOGICAL EXECUTION
  typed operations -> pipelines/dataflows -> queries/plans -> analytical methods
                         |
PHYSICAL EXECUTION
  algorithms -> kernels -> libraries -> engines/providers -> compute/storage/network
                         |
PRODUCTION AND CONSUMPTION
  deployment/jobs -> SLO/recovery/security -> APIs/BI/apps -> support/economics
                         |
COMPILER AND PRODUCTS
  requirements <-> offers -> bindings -> IR/lowering -> artifacts/receipts
  products/suites/solution packs are derived from all of the above
```

## The examples in the question are different planes

| Term | Correct domain | What must be modeled |
| --- | --- | --- |
| Pipeline | Logical dataflow + runtime orchestration | ports, state, time, delivery, checkpoint, retry, replay, backfill, maintenance |
| Compute | Runtime/resource control | execution model, CPU/GPU/memory/network, placement, budgets, cancellation, failure domains |
| Kernel | Physical executable implementation | exact typed operation, ABI/layout, target, numeric behavior, resource bounds, qualification |
| Method | Analytical/study contract | intent, assumptions, inputs/outputs, uncertainty, evaluation; it may have many algorithms |
| Algorithm | Procedure implementing a method/problem class | preconditions, guarantee, complexity, randomness, stopping, failure |
| Compression | Encoding/layout mechanism | codec, losslessness/error, splittability, random access, checksums, CPU/memory trade-off |
| Library | Reusable contribution | exported types/traits/operations, decisions, laws, requirements/offers, effects and receipts |
| Product | User/outcome/lifecycle promise | adoption, UX, operation, SLO, support, commercial and exit boundary |

```text
practice: probabilistic forecasting
    -> method: ARIMA / state space / hierarchical reconciliation / ...
        -> algorithm: fitting and inference procedure
            -> kernels: matrix factorization, convolution, quantile, random sampling, ...
                -> library implementation
                    -> CPU/GPU/runtime/provider offer

logical operation: compress column chunk
    -> codec + parameters + loss law
        -> kernel implementation
            -> target offer + benchmark/conformance receipt

pipeline: CDC source -> decode -> validate -> deduplicate -> temporalize -> table commit
    -> each arrow/node is a typed operation
    -> the pipeline owns composition, state and recovery
    -> connectors/table/runtime libraries merely offer implementations
```

## Highest-risk open gaps

1. Most of the 559 distinct bounded-context candidates have not been owner-adjudicated or converted
   into complete DDD contracts; the global context map is under active research.
2. The 908 analytical-practice and 1,062 typed-operation records remain hypothesis queues. Method,
   operation and owner crosswalks are incomplete even where deep horizontal corpora now exist.
3. The data type/shape candidate now contains 45 axes, 31 carriers, 77 semantic types, 177 shapes,
   167 operation-totality records and 62 representation crosswalks, but independent modality audit,
   canonical owner decisions and executed round-trip/provider conformance remain open.
4. Candidate library and provider/target registries now exist, but they mostly describe contracts and
   offer templates. The analytical-product slice now maps all 14 abstract contract groups to concrete
   compiler requirements and reports zero remaining blocking decomposition gaps; signal/image,
   process, statistics, causal, forecasting, anomaly/change, graph, spatial, experimentation,
   optimization, simulation, deterministic document analysis and optional-assistance splits are
   structurally closed and remain unqualified. Executed conformance receipts, implementation
   manifests, removal/substitution exercises and live deployed-occurrence evidence remain sparse.
5. IR/lowering and codegen/build specifications now exist. The binder/solver specification is active;
   no production parser, graph store, solver, verifier, target backend or artifact emitter exists yet.
6. A global product-boundary corpus now contains 59 candidates and all 6,490 T001-T110
   applicability cells. The lakehouse, data-movement, governance-semantics and analytical-method slices have exact evidence-carrying
   adjudications. The analytical slice additionally has 14 product-group-to-library maps with scoped
   qualification and substitution laws, but no map is a passing provider binding. No global count is
   ratified until context ownership, truth satisfaction, customer lifecycle evidence, substitution,
   operation and exit proofs close.
7. Security/privacy, quality/reconciliation, governance/ontology/MDM, lineage/provenance/evidence,
   messaging, consumption and runtime now have deep candidate corpora. Platform commercial/support,
   global authority/time/identity adjudication and production SRE receipts remain incomplete.
8. Exact expert-contribution portfolios and the research-artifact graph are active. The earlier 52-expert
   specialist seed is too shallow to convert individual papers, formalisms, tools and limitations into
   compiler requirements or library boundaries.
9. Predictive statistical/ML coverage now contains 474 model families, 5,688 typed components,
   60 candidate library boundaries and 187 sources; executable target/study/estimator/evaluation,
   leakage, calibration, lifecycle and provider-qualification closure remains open.
10. Recurring change intelligence now distinguishes feed failure, signals, verified events, deployed
    rollout and invalidation, but live monitors and requalification receipts are not operational.
11. The optional LLM/generative/agent extension and analytical-assistance port are now typed research
    candidates, but production evaluation, nondeterminism, cost, privacy, security, fallback and provider
    qualification remain open. Deterministic core compilation, authorization, effects and evidence do
    not depend on them.
12. No end-to-end mixed-industry solution has yet been compiled, deployed and independently verified.
13. “25 sources per individual subindustry” is not met; current vertical packs satisfy a family-level gate
    and record the stronger requirement as open.
14. The first schema-clean nine-pack integration audit found 4,169 distinct unresolved canonical references:
    2,031 analytical-practice names, 1,378 typed-operation names, 398 industry/subindustry names and
    362 source-system class names. These are now governed in
    `industries/canonical-reference-review-queue.jsonl`; no string-based equivalence is permitted.
15. Application behavior was previously only an assembly/IR placeholder. The candidate universe at
    `universes/application_behavior/` now specifies 7 contexts, 12 contracts, 17 operations, 4
    state machines, 8 reusable libraries, 16 conformance tests, 16 negative twins and 8 explicit
    assembly edges. It remains open: all offers are unimplemented and unqualified, tests are not
    executed, no effect authority is granted, and no unrelated vertical has accepted the corpus.

The machine-readable status for every plane is `coverage-planes.jsonl`. A finite plane list is not a
completeness proof; it is a governed review boundary that must admit typed extensions and gaps.
