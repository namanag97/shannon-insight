# Metadata Discovery Governance

This universe specifies the horizontal semantic contracts required to acquire source-attributed
metadata and make it discoverable without converting catalog records, projections, search rank or
service measurements into source truth, certification or access authority.

```text
product.metadata_discovery
  |
  +-- context.metadata_discovery.acquisition
  |     `-- library.metadata_discovery.acquisition_port
  |
  +-- context.metadata_discovery.catalog
  |     +-- library.metadata_discovery.assertion_record
  |     +-- library.metadata_discovery.discovery_projection
  |     +-- library.metadata_discovery.search_browse
  |     `-- library.metadata_discovery.freshness_coverage
  |
  `-- context.metadata_discovery.federation
        `-- library.metadata_discovery.federation
```

The context/library cardinality is intentional. DDD, product discovery, service blueprinting,
ports-and-adapters, formal state modeling, SRE and measurement theory were triangulated in
`research/product_ontology/boundary_method_ensemble/`. Assertion, projection, search and discovery
measurement share one catalog model; acquisition and federation require distinct integration
languages. Physical search/index execution remains an imported provider/product concern.

## Counts

- 15 authoritative or official implementation sources
- 3 bounded contexts
- 30 no-default decisions
- 6 exact libraries
- 24 typed operations
- 14 negative twins
- 18 compiler records
- 0 qualified, portable or selectable offers

Run:

```bash
python3 build_corpus.py
python3 validate_corpus.py
```
