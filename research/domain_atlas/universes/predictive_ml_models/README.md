# Predictive analytics and statistical machine-learning universe

This is a deterministic, open-world candidate corpus for non-generative predictive analytics. It
does not declare a winning model and it does not treat a paper, package, citation count or benchmark
as deployment qualification. Its purpose is to let an enterprise compiler preserve the distinctions
that model catalogues normally erase.

The core excludes LLM application semantics, prompt/RAG pipelines and agent orchestration. A future
optional extension may bind such capabilities through the same contracts, but cannot change core
prediction, evidence, resource or authority laws.

## The compilation chain

```text
business question + harmed parties + permitted action
                       |
                       v
              predictive task contract
     target | population | grain | horizon | action | cost
                       |
                       v
       feature + label + observation-time contracts
   valid time | recorded time | available time | finality
                       |
                       v
          study and partition plan + leakage proof
   fit | tune | calibrate | final test | external validation
                       |
                       v
       model family -- structure -- objective / loss
             |              |              |
             +--------------+--------------+
                            v
                         estimator
                            |
                            v
             optimization / training algorithm
                            |
                            v
             typed numerical / graph / tensor kernels
                            |
                            v
       qualified provider occurrence + exact target profile
                            |
                            v
  fitted artifact (data/code/config/provider/seed digests)
                            |
                            v
 calibration -- evaluator -- uncertainty -- decision rule
                            |
                            v
        monitored deployment + label-maturity feedback
```

No arrow may be skipped. In particular:

```text
prediction target != model family != model structure != fitted artifact
model             != estimator    != objective/loss != training algorithm
algorithm         != kernel       != package         != provider occurrence
score             != probability != calibrated risk != authorized decision
predictive fit    != causal identification
explanation       != evidence     != causal mechanism
```

## Why the process-research examples matter

The corpus explicitly encodes the research family the user highlighted because it exposes a
general compiler problem: the representation is part of the analytical contract.

```text
OCED / OCEL 2.0
 events + objects + qualified relations + time-varying attributes
        |
        +--> declared case projection --------> trace-prefix predictor
        |           (loss may occur)
        |
        +--> temporal EKG (tEKG) --------------> temporal graph predictor
        |    entity snapshots retain state history
        |
        +--> HOEG encoding --------------------> heterogeneous GNN predictor
        |    event/object node types and interactions retained
        |
        +--> state-aware OCEL / SA-OCPM -------> state-aware predictor
             derived state-transition events and state-labelled projection
```

These are not synonyms:

- **OCED/OCEL** owns event-data exchange meaning.
- **tEKG** is a temporal graph representation and transformation algorithm; it is not by itself a
  predictor.
- **HOEG** is a heterogeneous object-event graph encoding used with a predictive architecture.
- **SA-OCPM/state-aware OCEL** introduces domain-derived state rules, generated state-change events
  and state-aware labels. The state rule and ordering choice require domain authority.
- A **case projection** is a possibly lossy view over object-centric data, never the canonical truth
  by default.

Flattening all of these into “process prediction” would prevent the compiler from proving temporal
validity, interaction retention, information loss and provider applicability.

## Experts are artifact-linked, not ranked

`experts.jsonl` contains authors attached to exact primary artifacts. It answers “what can be learned
from this person’s demonstrated work?” without claiming that authorship is universal authority.
Examples include:

- Dirk Fahland: multidimensional event knowledge graphs; OCED core-model design space and known
  limits; actor-aware process concept drift.
- Dina Kretzschmann, Alessandro Berti and Wil van der Aalst: state-aware object-centric process
  mining with explicit derived state transitions.
- Shahrzad Khayatbashi, Olaf Hartig and Amin Jalali: snapshot-preserving OCEL-to-temporal-EKG
  transformation.
- Tim K. Smit, Hajo Reijers and Xixi Lu: HOEG encoding and its bounded evidence for object-centric
  remaining-time prediction.
- Riccardo Galanti, Massimiliano de Leoni, Nicolò Navarin and Alan Marazzi: object-interaction-aware
  predictive process analytics.
- Robert Tibshirani, Leo Breiman, Jerome Friedman, Vladimir Vapnik, Rob Hyndman, Susan Athey,
  Aaditya Ramdas and many others: exact primary artifacts are linked rather than summarized as
  reputation.

The expert graph is deliberately open. Missing people and artifacts are gaps; citation or h-index is
not used as a superiority score.

## Orthogonal classification

`classification-axes.json` separates at least these non-collapsible axes:

```text
output geometry       scalar | vector | set | sequence | graph | distribution | survival...
learning signal       full | weak | semi | self-supervised representation | online | transfer...
data posture          grouped | longitudinal | spatial | network | censored | missing | drifting...
epistemic family      parametric | semiparametric | nonparametric; frequentist | Bayesian...
prediction timing     batch | rolling origin | event-triggered | streaming | real-time...
decision proximity    information | triage | review | recommendation | authorized automation...
```

The axes classify a resolved occurrence, not a Cartesian explosion of named products. No axis value
implies another.

## Corpus contents

- `model-families.jsonl` — sourced, provider-neutral contracts spanning 24 method domains.
- `predictive-components.jsonl` and `component-edges.jsonl` — explicit task, structure, objective,
  estimator, algorithm, representation, kernel, fitted artifact, calibration, evaluator and decision
  nodes for every candidate family.
- `operations.jsonl` — target resolution, study planning, fitting, prediction and evaluation
  operations with partial/refusal states.
- `decision-points.jsonl` — semantic, evidence, numerical, resource and deployment choices; missing
  values refuse compilation.
- `library-boundaries.jsonl` — pure/effect-bounded reusable contribution seams.
- `representation-input-requirements.jsonl` — typed input and information-loss laws.
- `provider-qualification-profiles.jsonl` — unexecuted templates; none falsely claims a pass.
- `compiler-mappings.jsonl` — mappings to the shared analytical-practice/study/estimand/model/
  estimator/algorithm/kernel/artifact/evaluation graph.
- `sources.jsonl`, `evidence-edges.jsonl`, `experts.jsonl`, and `expert-artifact-links.jsonl` — primary
  evidence and attribution graph.
- `innovations-2021-2026.jsonl` — non-LLM, artifact-scoped recent candidates with limitations.
- `vertical-examples.jsonl` and `negative-twins.jsonl` — unrelated banking, health, manufacturing and
  object-centric logistics falsification fixtures.
- `gaps.jsonl` — explicit open-world and qualification gaps.

## Deterministic use

```bash
python3 research/domain_atlas/universes/predictive_ml_models/build_corpus.py
python3 research/domain_atlas/universes/predictive_ml_models/validate_corpus.py
```

The current validator checks quotas, uniqueness, referential integrity, source/author attribution,
the exact process-research artifacts, component non-collapse, recent-evidence counts, negative twins,
unexecuted qualification state and the non-generative core boundary. Passing means structurally
usable research data, not complete science or production readiness.
