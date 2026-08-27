# Operational activation mapping semantic kernel

This corpus resolves the coarse `library.activation_mapping` label into three exact, pure seams:

```text
provider contracts + offer
          |
          v
destination-profile compiler  -- exact provider-neutral capabilities
          |
source contract + declaration + schema mapper
          |
          v
activation-mapping compiler    -- immutable accepted plan + residuals
          |
source occurrence + externally issued match observations
          |
          v
activation-mapping evaluator   -- effect proposal + authority request
          |
          +--> external policy/authorization owner
          +--> external effect port and provider
          +--> external receipt/reconciliation contract
```

The evaluator deliberately emits a non-authoritative `ActivationEffectProposal`. It does not perform lookup I/O, adjudicate identity, authorize, execute, retry, compensate, accept outcomes or qualify providers.

Run:

```bash
python3 build_corpus.py
python3 validate_corpus.py
```

The generated records are research-grade specified contracts, not qualified implementations. Structural compatibility never makes an offer selectable.
