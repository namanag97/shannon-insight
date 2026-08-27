# Lakehouse boundary adjudication — edition 1

Status: **evidence-backed adjudicated candidate**, not a ratified portfolio, implementation or
provider qualification.

This bundle corrects the first lakehouse falsification pilot by keeping the orthogonal identities
that a compositional compiler must bind independently.

```text
architecture pattern                  vertical solution pack
pattern.lakehouse                     not present
        |                             (industry language/rules are external)
        v
suite.lakehouse  -- packaging only; owns no imported semantics
        |
        +--> managed lakehouse experience ........ presumptive product
        +--> catalog service ...................... strong product candidate
        +--> query execution service .............. strong product candidate
        +--> ingestion/delivery ................... strong product candidate
        +--> managed table maintenance ............ strong product candidate
        +--> data sharing/exchange ................. strong product candidate
                 |
                 v
        typed capability requirements/offers
                 |
                 +--> semantic contracts
                 +--> exact standards/editions
                 +--> library contracts
                 +--> implementations
                 +--> provider/resource offers
```

The term **lakehouse** therefore does not denote one sovereign product. It denotes an architecture
pattern and, optionally, a suite. The suite may package several product promises, but containment
does not transfer table, catalog, query, policy, quality, lineage or business-semantic ownership.

## Principal adjudications

1. `product.analytical_table_management` is split. Table identity and state belong to a semantic
   contract specialized by exact Iceberg, Delta and Hudi editions and realized by capabilities,
   libraries and implementations. A format or library is not a product.
2. `product.lakehouse_control_plane` is merged into
   `capability.environment_reconciliation` under the managed experience until independent
   adoption, service and exit evidence proves a separate product.
3. Table maintenance is two identities: pure planning/equivalence capabilities and an optional
   independently adopted **managed maintenance product** with destructive authority, support,
   SLOs and exit.
4. Cross-format translation is a capability with mandatory residual and loss reports. It never
   proves that all table-format features are equivalent.
5. Quality, lineage, data-use authority and business metrics remain neighboring products. The
   lakehouse experience imports them; it does not re-own them.
6. Lakehouse is horizontal architecture, not a sports, banking, healthcare, energy or other
   industry solution pack.
7. Query execution and ingestion/delivery are not redefined inside the lakehouse suite. They are
   digest-pinned conformist imports from their canonical adjudications. The legacy lakehouse-only
   identity `product.ingestion_delivery_service` is a completed rename to the shared canonical
   `product.ingestion_delivery` identity.

## Compiler-facing state

```text
21 requirements       all UNBOUND
 8 observed offers    all UNQUALIFIED
14 local library contracts and normalized compiler maps
14 exact compiler projections, all UNQUALIFIED
 0 exact compiler gaps
 4 complete 29-field product DDD dossiers
 0 portable offers
 0 ratified products
```

That is deliberate. Official projects and products demonstrate plausible separability, but do
not satisfy SAN qualification gates without exact versions, implementation identities, scoped
conformance results, operational envelopes and fresh receipts.

## Files

- `source.json` — canonical researched/adjudicated source.
- `metamodel.json` — record kinds, split-test axes and non-collapse laws.
- `artifacts.jsonl` — pattern, suite, product, capability, semantic-contract, standard,
  implementation, provider, resource, interface and neighboring-product nodes.
- `boundary-decisions.jsonl` — evidence per split-test coordinate and merge/split/reclassify
  dispositions.
- `semantic-ownership.jsonl` — one owner and one executable invariant candidate per meaning.
- `library-contracts.jsonl` — types, operations, exposed decisions, invariants, refusals,
  dependencies and effect boundaries.
- `product-ddd-dossiers.jsonl` — complete candidate strategic/tactical DDD for managed
  experience, catalog, managed maintenance and data sharing.
- `product-ddd-delegations.jsonl` — exact dossier and binding-map imports for query execution and
  ingestion/delivery. Each import pins canonical record and file digests, forbids local
  redefinition and is revalidated against its source bundle.
- `requirements.jsonl`, `offers.jsonl` — honest compiler inputs with no fabricated binding.
- `product-library-binding-maps.jsonl`, `product-library-binding-gaps.jsonl` — one normalized map
  per local library; the current exact structural gap set is empty.
- `compiler-library-bindings.jsonl` — every exactly mapped local lakehouse library projected to
  the shared persistence compiler contribution and its withheld requirement/offer. The local maintenance
  plan deliberately decomposes into compaction planning, clustering planning and destructive
  reachability/GC policy, which qualify and substitute independently. Data sharing maps to the
  existing sharing contract; similarly named generic reconcilers are refused for environment
  lifecycle because they lack capability closure, readiness, drift, rollout, rollback and exit.
- `legacy-crosswalks.jsonl` — exact dispositions for the earlier pilot IDs.
- `negative-tests.jsonl` — constitutional anti-collapse cases.
- `registry.jsonl`, `manifest.json` — deterministic union and digest/count manifest.

## Rebuild and validate

```bash
python3 research/product_ontology/adjudications/lakehouse/enrich_source.py
python3 research/product_ontology/adjudications/lakehouse/build_bundle.py
python3 research/product_ontology/adjudications/lakehouse/validate.py
python3 research/product_ontology/adjudications/lakehouse/enrich_source.py --check
python3 research/product_ontology/adjudications/lakehouse/build_bundle.py --check
```

Passing establishes structural, referential, ownership, evidence, non-collapse and honesty laws.
It does not qualify a provider, prove product-market fit or ratify the global portfolio.
