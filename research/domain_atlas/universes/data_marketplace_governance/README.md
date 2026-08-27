# Data Marketplace Governance exact universe

This universe decomposes one operated Data Marketplace product into three bounded contexts and six
provider-neutral libraries. It is intentionally downstream of exact Data Product Publication and
Data Use Policy contracts. It does not turn a catalog, offer, policy, approval workflow,
provisioning adapter, billing record or data-delivery system into the marketplace.

```text
published product + external terms/policy/price editions
                         |
                         v
  merchandising: offer/listing --> discovery/ranking
                         |
                         v
  acquisition: eligibility broker --> subscription case --> fulfillment handoff
                         |                                      |
                         |                                      +--> external provisioning/access/transfer
                         v
  evidence: terms acknowledgement + usage/charge references + marketplace receipt
```

The exact contracts preserve these non-collapse boundaries:

- product publication is not an offer or listing;
- an offer proposes terms and grants no permission;
- visibility, relevance, ranking, recommendation, suitability and eligibility are distinct;
- credential verification is not claim truth or eligibility;
- eligibility, approval, agreement, entitlement, provisioning, access and consumption are distinct;
- a dispatch, protocol response or provider receipt proves only its exact contracted occurrence;
- terms acknowledgement is not consent, legal validity, policy permission or consumer acceptance;
- usage observation, normalized billing record, charge, invoice, settlement and payment are distinct.

Every operation is pure. Effectful libraries emit typed intents and reconcile exact receipts.
Every semantic decision is explicit and has no default. Models and agents may supply attributed
proposals or diagnostics but cannot rank with hidden semantics, decide eligibility, approve,
negotiate, provision, accept evidence or ratify outcomes.

Current status is specified but unimplemented: all six structural offers have zero qualified
implementations and are neither selectable nor portable.

Run from this directory:

```sh
python3 build_corpus.py
python3 validate_corpus.py
```
