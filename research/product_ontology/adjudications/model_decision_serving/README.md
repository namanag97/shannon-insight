# Model, feature, inference and decision product adjudication

This bundle applies the product split test before suite packaging or implementation naming. It
retains six product candidates:

1. predictive model engineering and lifecycle;
2. feature definition and serving platform;
3. predictive inference serving;
4. predictive model evaluation and monitoring;
5. deterministic decision modeling and execution; and
6. an optional model/agent extension runtime.

The sixth product is neither ambient nor authoritative. It exists only at a declared use site and
can be removed without changing deterministic parsing, typing, binding, analytics, decision logic,
authorization, effect execution, receipts or reconciliation.

```text
source facts + governed time              predictive task + study contract
              |                                      |
              v                                      v
        feature platform ----------------> model engineering/lifecycle
              |                                      |
              | historical cut                       | approved model edition
              v                                      v
       batch scoring composition              inference serving
              |                                      |
              +--------------- prediction -----------+
                                      |
                                      v
                         deterministic decision service
                                      |
                                      v
                              action proposal only
                                      |
                         authority + effect runtime

optional model/agent extension -> typed proposal -> deterministic gates above
```

Reclassifications are explicit:

- a model registry is a lifecycle component, not the whole lifecycle product;
- a distributed training runtime is a provider for resolved training jobs;
- batch scoring is a dataflow composition, not a product created by execution mode;
- vector indexing belongs to search/index serving and is not a feature platform;
- a prediction is not a decision, authorization, effect or outcome; and
- evaluation and monitoring produce scoped evidence, not self-issued deployment approval.

The generated JSONL registry preserves semantic owners, capabilities, library seams, requirements,
unqualified offers, relations, negative twins, legacy crosswalks and compiler-library projections.
Every physical offer remains unqualified and non-portable.

All six products now have complete candidate 29-field DDD dossiers. Twenty-seven of the twenty-eight
bundle libraries are attributed exactly to one product: seven lifecycle, four feature, three online
inference, five assurance, five deterministic decision and three optional-extension seams. The
remaining batch-scoring library stays attributed to a composition component, because an execution
mode does not become a product. Product attribution also propagates to every compiler map and typed
gap.

The four former compiler gaps now resolve to seven exact contracts. Historical feature retrieval
splits into temporal-plan compilation and pure cut evaluation. Materialization splits into coverage/
restatement planning and write/receipt reconciliation. Online feature retrieval uses one exact
request/response/freshness protocol. Inference routing splits per-request revision selection from
guarded rollout and route-change reconciliation. All six products are structurally mapped but
still unqualified. No structural projection qualifies a provider, proves portability, authorizes a
traffic transition or constitutes vertical acceptance.

The optional extension is deliberately small. It owns task declaration, bounded invocation and
typed proposal validation only. Removing it must leave deterministic vocabulary, typechecking,
binding, analytics, lifecycle, evidence, decision logic, authority checks, effects and
reconciliation unchanged. Statistical and learned predictive methods remain ordinary declared
method providers; an `AI`, model-family or agent label grants no semantic or evidentiary status.

Rebuild and validate from the repository root:

```sh
python3 research/product_ontology/adjudications/model_decision_serving/build_bundle.py
python3 research/product_ontology/adjudications/model_decision_serving/validate.py
python3 research/product_ontology/adjudications/model_decision_serving/build_bundle.py --check
```
