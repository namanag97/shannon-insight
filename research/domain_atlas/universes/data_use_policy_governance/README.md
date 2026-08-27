# Data Use Policy Governance

This universe specifies provider-neutral policy administration, deterministic policy decision,
usage-obligation handoff and decision-evidence contracts without stealing identity, classification,
purpose, consent, legal, entitlement, enforcement or business-effect authority from their owners.

```text
product.data_use_policy
  |
  +-- context.data_use_policy.administration
  |     +-- library.data_use_policy.policy_edition
  |     `-- library.data_use_policy.rule_combination
  |
  +-- context.data_use_policy.decision
  |     +-- library.data_use_policy.request_context
  |     `-- library.data_use_policy.decision_evaluation
  |
  `-- context.data_use_policy.usage
        +-- library.data_use_policy.obligation_protocol
        `-- library.data_use_policy.decision_evidence

external owners ---------------- editioned references/evidence --------+
 identity, resources, purpose, classification, consent, legal basis     |
                                                                         v
external PEP/effect runtime <---- intents and receipts ---- policy product
```

The product/context/library cardinalities are intentional. PAP, PDP, PIP and PEP separation,
DDD/context mapping, ODRL and XACML semantics, UCON continuity, privacy vocabulary, ports and
adapters, formal state modeling and production decision telemetry were triangulated. Enforcement
remains outside: permit is not approval, entitlement, disclosure, mutation or an effect receipt.

## Counts

- 17 primary, official or official implementation sources
- 3 bounded contexts
- 36 no-default decisions
- 6 exact libraries
- 24 typed operations
- 18 negative twins
- 18 compiler records
- 0 qualified, portable or selectable offers

Run:

```bash
python3 build_corpus.py
python3 validate_corpus.py
```
