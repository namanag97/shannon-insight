# Application behavior universe

This package closes an uncovered horizontal plane: the provider-neutral contracts needed to
describe an enterprise application's commands, queries, state transitions, long-running
coordination, events, projections, effect handoff, and execution evidence. It is a candidate
universe, not a claim that these records cover every enterprise application.

The semantic owner is the application context represented by each record. Existing universes
remain owners of imported meanings: data types own data semantics, persistence owns durability,
pipeline/dataflow owns data movement, security/policy owns authorization, runtime/resource owns
capacity and execution, provenance owns evidence relations, and products/vertical packs own
customer and business meaning. The application plane may reference those contracts but cannot
silently absorb them.

The corpus distinguishes:

- commands from events, queries from projections, aggregate state from persistence, workflows
  from generic dataflow, compensation from rollback, decision results from authority, envelopes
  from event meaning, and receipts from business outcomes;
- declarations and decisions from effect intents, executor observations, and business acceptance;
- compiler candidate edges from application-runtime, human-adjudication, dataflow-composition,
  semantic-import, and effect-gateway assembly mechanisms.

Every row carries lifecycle, time, authority, resource, side-effect, invariant, refusal, and
evidence surfaces. All offers are explicit unimplemented reference offers with zero qualification
receipts and are therefore not bindable. All conformance tests are specified but unexecuted.

Evidence is deliberately scoped. OpenAPI describes an HTTP interface; RFC 9110 supplies transport
safe/idempotent laws; CloudEvents supplies an interoperable event envelope; SCXML and BPMN/DMN
provide state/process/decision notation; the Sagas paper motivates explicit compensation; PROV-DM
structures provenance relations; Amazon States Language supplies one runtime-specific retry/catch
representation; JSON Schema supplies structural validation; RFC 9457 supplies an error-detail
representation. None of these sources proves domain ownership, authorization, business truth,
portable implementation behavior, or product acceptance.

Run the fail-closed checks:

```text
python3 build_corpus.py --check
python3 validate_corpus.py --determinism
```

The builder is the only authoring-to-artifact path. JSONL records are sorted by stable ID, JSON is
canonicalized, and `manifest.json` records byte hashes and counts. `coverage-report.json` is an
explicit open-world accounting with `completion_claim: false`.
