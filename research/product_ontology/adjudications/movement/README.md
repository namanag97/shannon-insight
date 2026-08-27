# Data movement boundary adjudication — edition 1

Status: **evidence-backed adjudicated candidate**, not a ratified portfolio, implementation or
provider qualification.

The term `pipeline` is a composition pattern. It must not collapse the independently versioned
state, authority, operation and exit boundaries below.

```text
pattern.data_pipeline
        |
        v
suite.data_integration  -- packaging only; owns no imported semantics
        |
        +--> source connectivity control .......... presumptive product
        +--> source replication / CDC ............. strong product candidate
        +--> managed ingestion / delivery ......... strong product candidate
        +--> pipeline orchestration ............... strong product candidate
        +--> stateful dataflow execution .......... strong product candidate
        +--> batch transformation build ........... presumptive product
        +--> event streaming platform ............. strong product candidate
        +--> operational data activation .......... strong product candidate
                    |
                    v
        typed capability requirements and offers
                    |
                    +--> semantic contracts
                    +--> exact protocol/interface editions
                    +--> pure/effect-bounded library contracts
                    +--> unqualified implementations/providers
```

## Principal adjudications

1. A vendor connector, plugin or adapter is a provider offer. It is not a product merely because
   it has a SKU or repository.
2. A source-native database cursor, broker offset, ingestion delivery cursor, dataflow checkpoint
   and workflow logical date are different semantic types.
3. CDC owns source snapshot/change reconstruction. Managed ingestion composes capture and
   destination delivery into an operated source-to-target promise.
4. Orchestration owns schedules, workflow runs, task attempts, retries, backfills and cancellation.
   It does not own the semantics or correctness of tasks.
5. Stateful dataflow owns logical transforms, event time, watermarks, operator state, checkpoints
   and recovery. End-to-end exactly-once additionally requires replayable sources and transactional
   or idempotent sinks.
6. Transformation build composes five exact seams: definition compilation, selection closure,
   incremental materialization planning, target mutation protocol and build-evidence assembly.
   It imports package retrieval, query-language compilation and physical execution, scheduling,
   target commit/publication authority, quality authority and lineage storage.
7. Event streaming owns durable channels/logs, partitions, retention, replay and consumer progress;
   it does not own source capture or payload business meaning.
8. Operational activation is split from analytical ingestion because it exercises authority over
   operational destination objects. An analytical result is never sufficient authorization.
9. ETL, ELT, CDC and reverse ETL are topology/processing patterns. Only independently adopted and
   operated promises become products.
10. LLMs or agents may propose mappings and recovery actions through typed ports. They do not
    acquire source semantics, effect authority or product identity.
11. Schema mapping is not one runtime blob. Its cold-path compiler owns exact structural
    correspondence, representability and loss-explicit plan construction; its hot-path executor
    evaluates only an accepted immutable plan. Schema compatibility, ontology mapping, reference
    crosswalks, business conversion, capture and delivery acknowledgement remain separate.
12. A transformation manifest is not an invocation selection. The former is the complete resolved
    project; the latter is a deterministic selector/set/graph closure over one exact manifest.
    Likewise, incremental calculus, target effects and evidence classification are not one
    materialization library. Build success is never target publication or business acceptance.
13. Activation mapping composes three pure seams: destination-contract normalization, immutable
    mapping-plan compilation and per-record proposal evaluation. Match evidence is imported from
    an accountable identity owner. The evaluator emits an effect proposal and authority request;
    policy decision, execution, retry, compensation, receipt reconciliation and outcome acceptance
    remain separately owned.

## Compiler-facing state

```text
17 requirements       all UNBOUND
10 observed offers    all UNQUALIFIED
18 product libraries  exact product attribution and requirement coverage
18 compiler maps      all structural/unqualified; 0 exact binding gaps
 8 DDD dossiers       complete 29-field candidate dossiers
 0 portable offers
 0 ratified products
```

The compiler must therefore return typed residual gaps rather than select Airbyte, Debezium,
Airflow, Flink, dbt, Kafka, Hightouch or another observed implementation by brand.

## Files

- `source.json` — canonical researched/adjudicated source.
- `metamodel.json` — record kinds, split-test axes and non-collapse laws.
- `artifacts.jsonl` — patterns, suite, products, capabilities, semantic contracts, standards,
  interfaces, implementations, providers and neighboring products.
- `boundary-decisions.jsonl` — evidence per split-test coordinate and exact dispositions.
- `semantic-ownership.jsonl` — one candidate owner and executable invariant per meaning.
- `library-contracts.jsonl` — types, operations, decisions, invariants, refusals, dependencies and
  effect boundaries, each with exact product attribution.
- `product-ddd-dossiers.jsonl` — one full strategic/tactical DDD dossier per movement product.
- `product-library-binding-maps.jsonl`, `product-library-binding-gaps.jsonl` — exact compiler
  projections where semantics align, otherwise named fail-closed gaps.
- `requirements.jsonl`, `offers.jsonl` — honest unbound compiler inputs.
- `legacy-crosswalks.jsonl` — exact mapping from global and generic legacy identities.
- `negative-tests.jsonl` — constitutional anti-collapse cases.
- `registry.jsonl`, `manifest.json` — deterministic union and digest/count manifest.

## Rebuild and validate

```bash
python3 research/product_ontology/adjudications/movement/enrich_source.py
python3 research/product_ontology/adjudications/movement/build_bundle.py
python3 research/product_ontology/adjudications/movement/validate.py
python3 research/product_ontology/adjudications/movement/enrich_source.py --check
python3 research/product_ontology/adjudications/movement/build_bundle.py --check
```

Passing proves structural, referential, evidence, boundary and honesty laws. It does not prove
provider conformance, production fitness, product-market fit or global portfolio completeness.
