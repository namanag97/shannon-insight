# Product-composition environment lifecycle

This universe owns the reusable layer between a product profile and component/runtime mechanisms.
It is not a lakehouse implementation, deployment controller or product UI.

```text
product profile + exact component requirements
                  |
                  v
       capability closure and bindings
                  |
                  v
 desired edition != observed occurrence cut
                  |
                  v
 drift + readiness + rollout/rollback + exit plans
                  |
                  v
 typed effect intents -> qualified runtime/provider adapters
```

The exact library is `library.product_composition.environment_lifecycle`. It owns product-profile
composition, capability closure, desired/observed comparison, drift classification, environment
readiness and change/exit planning. It imports component semantics and runtime mechanisms without
acquiring them.

The library is pure with explicit effect intents. It does not execute reconciliation, qualify a
provider, authorize irreversible effects, accept a rollout, or declare an exit complete. Its
reference offer remains non-selectable with zero qualified implementations.

Build and validate:

```bash
python3 research/domain_atlas/universes/product_composition_lifecycle/build_corpus.py
python3 research/domain_atlas/universes/product_composition_lifecycle/validate_corpus.py
```
