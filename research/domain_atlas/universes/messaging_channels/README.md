# Messaging and channel universe

Status: evidence-backed research candidate; not adjudicated and not a completeness claim.

The semantic unit is a provider-neutral logical messaging/channel contract. Protocols, engines,
libraries, offers, and deployments are related evidence-bearing artifacts, never synonyms.

```text
business intent / facts / observations
                 |
                 v
       logical channel contract
       (identity, time, order, delivery, retention, security)
                 |
          compiler requirement
                 v
          protocol binding  <----> client / adapter boundary
                 |
                 v
          broker or engine  <----> versioned provider offer
                 |
                 v
       deployed occurrence (configuration + limits + receipts)
                 |
                 v
  producer effect -> publication -> transport -> consumption -> downstream effect
       proof              proof          proof          proof              proof
```

No component-level `exactly once` feature proves end-to-end exactly once. The five stages above
must be established separately and composed. A broker acknowledgement can be durable receipt but
is not business acceptance. A message identifier is not a business idempotency key. Per-partition
order is not global order. Retry, redelivery and replay have different attempt identities. A DLQ is
mechanical diversion; adjudicated quarantine owns custody, correction and release.

Time is labeled: event time, producer time, broker time, ingest time and processing time cannot be
substituted silently. Bridges can preserve or weaken a contract and must receipt any loss; they
cannot strengthen semantics merely by choosing a more capable target.

## Corpus

- 109 primary/official sources, with implementation and provider documentation scoped as evidence rather than canonical domain semantics.
- 53 bounded-context candidates.
- 106 capabilities, 212 typed operations, 53 decisions and 20 channel contracts (391 combined records).
- 12 total lifecycles, 20 delivery-composition laws and 53 invariant/refusal records.
- 53 requirements, 53 offer templates and 53 compiler mappings.
- 24 library/adapter boundaries, 20 layer-boundary records and 17 qualification profiles.
- 24 non-generative 2021-2026 innovation candidates, 109 evidence records and 24 honest gaps.
- Two unrelated verticals—commerce order commands and industrial turbine telemetry—with a failure twin for each.

## Files and validation

All registries are deterministic JSONL and each has a JSON Schema in `schemas/`. Example artifacts
are under `examples/`. `manifest.json` and `coverage-report.json` state exact counts and candidate
status. Regenerate with `python3 build_corpus.py`; verify with `python3 validate_corpus.py`.

The validator checks deterministic regeneration, schemas, unique IDs, references, layer separation,
source authority, lifecycle totality, delivery-stage non-inference laws, innovations, vertical
independence, failure twins, LLM/generative exclusion, counts, and honest incompleteness.
