# Causal inference and experimentation semantic slice

This package is an evidence-backed, owner-unratified semantic decomposition of the exact causal and
experimentation libraries currently present in the live registry. It does not select exact APIs,
qualify implementations, close canonical gaps or authorize compiler assembly.

## Boundary

```text
domain question + intervention meaning
                 |
                 v
     causal question -----> estimand
                 |              |
                 v              v
      study protocol      identification assumptions
         /       \          /                \
 assignment   exposure   causal graph     design route
         \       /          \                /
          study cuts          identified functional
                 \             /
                  estimator binding
                         |
                  estimate + uncertainty
                         |
       diagnostics + sensitivity + transport
                         |
                  sealed result manifest
                         |
                  conclusion appraisal
                         |
             evidence-only decision handoff
                         X
             no operational action authority
```

The existing experimentation product consumes eleven libraries governing protocol, randomization,
assignment, exposure, integrity, analysis cuts, result sealing and conclusion lifecycle. Five
causal-analysis libraries have no declared product consumer in the captured graph. They remain
composable study/method libraries until independent product evidence establishes users, operations,
SLOs, lifecycle, adoption and exit.

`library.predictive.causal_effect_learners` is projected for semantic ownership migration: nuisance
prediction can be imported, but treatment-effect meaning belongs to a causal estimand and
identification context. `library.method_kernels.causal_methods` is only a composition facade.

## Contents

- 30 primary, official or foundational sources with bounded implications and authority limits;
- 36 reusable semantic modules;
- 42 non-collapse laws;
- 46 causal and experimental method boundaries;
- 16 expert learning profiles;
- 8 recent non-LLM innovations from 2022–2025;
- 16 exact library bindings and 256 library-by-axis decision candidates;
- 8 product/capability/library boundary findings.

Every axis row contains a researched decision question but no coordinate answer. Owner ratification,
exact contracts, conformance oracles, independent implementations and downstream acceptance remain
zero, so compiler binding fails closed.

## Validation

```bash
python3 research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/causal_inference_semantic_slice/validate.py
```
