# Telemetry Signal Semantics

This universe owns provider-neutral operational telemetry meanings. It deliberately does not own data-quality observability, business measures, source-system events, domain events, audit facts, lineage, service health, SLO verdicts, incidents, root cause, causality, or effect authority.

The previous generic `library.platform.telemetry` facade collapsed at least ten independently changing contracts. This corpus separates:

1. observed-resource and instrumentation-scope attribution;
2. editioned telemetry schemas and semantic conventions;
3. trace graphs;
4. metric streams;
5. log and event records;
6. execution profiles;
7. context and baggage propagation;
8. observation reduction, sampling and information loss;
9. cross-signal correlation; and
10. export delivery attempts and receipts.

The decisive separations are:

```text
observed entity != instrumentation producer != collector != destination
telemetry resource identity != enterprise/master-data identity
trace parent != span link != temporal correlation != causality
metric zero != absence != gap != reset != stale
log record != domain event != audit fact != incident
recorded != retained != sampled != exported != accepted != stored != queryable
correlation != root cause
telemetry != service health != business outcome
```

OpenTelemetry is retained as standards evidence and an observed implementation family. It does not acquire semantic ownership of enterprise entities, business events, health policies or analytics. Profiles remain explicitly alpha. Every reference offer is unqualified, non-portable and non-selectable.

Build and validate:

```bash
python3 research/domain_atlas/universes/telemetry_signals/build_corpus.py
python3 research/domain_atlas/universes/telemetry_signals/validate_corpus.py
```
