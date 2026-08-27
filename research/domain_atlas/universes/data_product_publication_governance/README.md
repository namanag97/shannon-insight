# Data Product Publication Governance

This universe specifies product identity and edition, port/dependency assembly, accountability,
readiness evidence, publication, consumer change, recall and exit without collapsing the product
into its datasets, contracts, catalog records, marketplace offers or deployment effects.

```text
product.data_product_publication
  |
  +-- context.data_product_publication.definition
  |     +-- library.data_product_publication.product_edition
  |     +-- library.data_product_publication.port_assembly
  |     `-- library.data_product_publication.accountability_binding
  |
  +-- context.data_product_publication.readiness
  |     `-- library.data_product_publication.readiness_evidence
  |
  `-- context.data_product_publication.lifecycle
        +-- library.data_product_publication.publication_protocol
        +-- library.data_product_publication.consumer_change
        `-- library.data_product_publication.recall_exit
```

One operated product is retained because these contexts jointly maintain one adoptable product
promise and lifecycle. They remain separate semantic models: definition cannot certify itself;
readiness cannot publish; publication cannot list an offer, grant access or deliver data.

## Counts

- 19 primary, authoritative or official implementation sources
- 3 bounded contexts
- 42 no-default decisions
- 7 exact libraries
- 28 typed operations
- 20 negative twins
- 21 compiler records
- 0 qualified, portable or selectable offers

Run:

```bash
python3 build_corpus.py
python3 validate_corpus.py
```
