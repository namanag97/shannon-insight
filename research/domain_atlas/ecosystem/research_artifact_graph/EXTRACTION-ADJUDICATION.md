# Research extraction and adjudication workflow

## 1. Register identity before interpreting content

Create or resolve, independently:

1. abstract work identity;
2. exact edition/version/revision;
3. venue occurrence and publication status;
4. exact artifact/file/URL and retrieval occurrence;
5. each person or collective contributor identity;
6. contributor role and order from that edition; and
7. institution affiliation only when an occurrence-scoped primary source supports it.

Never merge people on display name. Never infer first invention from the earliest artifact found.
Never use current affiliation as historical affiliation.

## 2. Extract a claim package, not a prose summary

For each independently addressable claim capture:

- exact locator and wording paraphrase;
- research problem and question;
- definitions and symbols;
- population/system/workload and unit of analysis;
- assumptions, preconditions, exclusions, and threat model;
- claim kind: definition, theorem, algorithmic, empirical, engineering, negative, conjectural;
- method, model, estimator, algorithm, and pseudocode identities;
- complexity, guarantee, convergence, approximation, error, numerical, and determinism scope;
- data/benchmark identity, edition, split, preprocessing, protocol, baselines, hardware/software;
- metric/estimand, result, effect size, uncertainty, sensitivity, and multiplicity handling;
- artifact/code/dataset/checksum, license/IP, and implementation maturity;
- limitations, threats to validity, failed cases, partiality, and residual questions; and
- citations that are dependencies, replications, contradictions, extensions, or merely context.

Missing values are explicit `unknown`/review items; absence is never converted to “none.”

## 3. Normalize without erasing context

```text
artifact-scoped term
   -> proposed concept mapping
   -> same meaning? ---- yes ---> canonical concept candidate
          |
          no/uncertain
          v
      retain separate concept + context relation + review item
```

Homonyms remain separate. Synonyms require definition/equality comparison. A formula with the same
surface syntax can have different units, populations, conditioning, missingness, or time semantics.

## 4. Adjudicate empirical evidence

Compare only after aligning:

- question/estimand;
- population/workload and sampling;
- data version, preprocessing, and leakage boundary;
- baseline implementation and tuning budget;
- hardware/software/configuration;
- metric direction, aggregation, and uncertainty;
- time horizon and evaluation split; and
- failure, abstention, timeout, and excluded-run policy.

If these do not align, record `incomparable`, not `contradictory`. Replication types are exact,
conceptual, robustness, reproduction, reanalysis, and target qualification.

## 5. Convert to compiler knowledge through gates

### Semantic gate

A definition becomes a type candidate only after identity, equality, construction, canonicalization,
validity, units/time, and loss rules are known.

### Method gate

A method becomes selectable only after purpose, input/output contract, assumptions, refusal cases,
guarantee scope, and competing-method boundaries are explicit.

### Algorithm gate

An algorithm becomes IR only after partiality, complexity, determinism, numerical behavior,
parallel/concurrent semantics, approximation/error, and resource parameters are explicit.

### Implementation/library gate

An implementation becomes a library contribution only after exact version/commit, license/IP,
API/ABI, dependency and feature surface, failure model, cancellation/thread safety, unsafe/FFI,
serialization boundary, reproducible build, target support, and conformance tests are known.

### Qualification gate

A benchmark becomes a provider/target qualification only after the declared target occurrence,
dataset/workload, configuration, scale, resource/cost envelope, metric, and acceptance threshold match.

### Product gate

Research evidence can support a capability candidate; it does not establish customer demand,
operability, adoption, support model, economics, or a product boundary. Those need separate evidence.

## 6. Predictive-model extraction extension

For any predictive artifact, additionally capture:

- forecast/classification/ranking/survival/anomaly target;
- entity and prediction occurrence identity;
- decision time, observation cutoff, horizon, label availability, censoring, and leakage;
- static/dynamic/exogenous features and future-availability assumptions;
- point/distribution/quantile/set/risk output;
- loss versus downstream decision utility;
- train/validation/test or temporal backtest protocol;
- calibration, sharpness, coverage, discrimination, and uncertainty;
- class imbalance, missingness, drift, shift, subgroup, and out-of-domain behavior;
- fitted-model lineage and feature/code/data/environment digests;
- human override, abstention, monitoring, retraining, rollback, and expiration policy.

Prediction, causal estimation, optimization, and simulation remain separate method families even when
one pipeline uses several of them.

## 7. Process-event research extension

For OCEL/OCED/EKG/state-aware work additionally capture:

- event, object/entity, relation, qualifier, activity/type, and identity semantics;
- occurrence, valid, recording, ingestion, and ordering time;
- multiplicity, lifecycle, changing attributes, and relation validity;
- case/leading-object/perspective choice;
- state owner, state function, threshold/model/rule origin, ambiguity, and transition law;
- source-to-event extraction mapping and unobserved-event assumptions;
- transformation preservation/loss for OCEL ↔ OCED profile ↔ EKG/tEKG;
- discovery/conformance/prediction target and evaluation protocol.

Compiler rule: an event-data format can preserve declared relations; it cannot prove that the source
mapping, object identities, state semantics, or process interpretation are true.

## 8. Promotion states

```text
discovered
 -> metadata_verified
 -> full_text_extracted
 -> independently_reviewed
 -> concept_adjudicated
 -> compiler_mapped
 -> library_candidate
 -> implementation_qualified
 -> production_occurrence_qualified
```

Retraction, supersession, contradiction, new negative evidence, license change, target change, or
benchmark invalidation can demote any downstream state. Historical records remain immutable and the
new decision is appended with evidence.

