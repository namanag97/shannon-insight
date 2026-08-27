# Signal, condition and event-history semantic slice

This package derives its 35-library universe from the 26 declared dependencies of
`product.signal_condition_diagnostics` plus nine formalism neighbors needed to expose shared
time-series/statistical foundations and quality/telemetry homonyms.

```text
phenomenon + measurand + quantity/unit
                 |
 acquisition + calibration + traceability
                 |
        observation / measurement result
                 |
 sampled signal + clock + gaps + information cut
                 |
 window -> filter/resample/transform -> signal features
                 |
 population + summaries + versioned baseline
          /              |              \
  anomaly score     change evidence   event history
       |                 |            /     \
 threshold        offline/online   survival competing risk
          \              |              /
           bounded condition finding
                       |
             diagnostic hypothesis
                       X
       correlation/change != causal proof
                       |
 evidence case + authority-bound judgment
                       |
             proposed action handoff
                       X
 authorization != execution != acceptance
```

## Boundary result

- The Signal and Condition Diagnostics product remains coherent as a measurement-to-finding and
  review lifecycle, with physical/business action authority outside.
- `time_series_semantics` is a missing shared import: sample indexes, information cuts, gaps,
  revisions and temporal splits cannot be inferred from method providers.
- Descriptive statistics and statistical estimators are shared primitives; no standalone product
  boundary is proven by the captured graph.
- Forecasts are imported origin/horizon/target-specific predictive outputs. Diagnostics does not
  own forecast selection, reconciliation or publication.
- Event-history semantics own censoring, risk sets and estimands; predictive survival models are
  implementations/imports, not event semantic owners.
- Quality anomaly/change/correlation kernels remain data-quality-context specializations. They may
  share qualified methods but not subjects, authorities, lifecycles or effects with condition
  diagnostics.
- Telemetry correlation remains a telemetry specialization and does not acquire physical
  measurement/calibration meaning.
- Diagnostic and “root-cause” hypotheses remain separate from causal identification.
- Numerical and forecasting facades are composition-only and cannot choose hidden baselines,
  thresholds, estimands or claim strength.
- Eleven concrete references lack P5 and coordinate dockets under their declared IDs; compiler
  routing remains explicitly refused.

The slice contains 38 primary, normative or official sources, 43 semantic modules, 67 method
boundaries, 50 non-collapse laws, 16 expert-learning profiles, eight recent non-LLM innovations,
35 exact library bindings and 560 explicit library-by-axis questions. It selects no coordinate
answer, owner decision, exact contract, qualified provider or canonical closure.

## Validation

```bash
python3 research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/signal_condition_semantic_slice/validate.py
```
