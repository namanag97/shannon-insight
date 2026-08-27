# Lineage Repository Persistence Port

This universe closes the provider-neutral persistence seam beneath the Lineage and Provenance
product. It defines one exact library contract, not a graph database recommendation.

```text
validated lineage assertions + coverage/gap evidence
                         |
                         v
               append batch and intent
                         |
                  repository adapter
                         |
                         v
          exact provider effect receipt
                         |
        reconcile + immutable graph-edition manifest
                         |
          +--------------+--------------+
          |                             |
   cut-bound read                 change scan/cursor
          |                             |
          +--------------+--------------+
                         |
               snapshot verification

external retention/hold/erasure decision --> disposition intent --> provider receipt
```

The repository owns persistence protocol semantics only. It does not own lineage vocabulary,
relation or path semantics, assertion truth, semantic acceptance, causal inference, capture/query
completeness, policy, retention, disclosure, erasure, evidence admissibility or provider
qualification.

Every operation is pure: it assembles, plans, validates or reconciles typed effects. The contract
has 16 explicit decision points, 13 operations, 18 non-collapse laws and 20 adversarial twins.
Storage acknowledgement, semantic validation, graph-edition publication and evidence acceptance
remain distinct. Commit order is not event/validity/causal order. Not-found is not proven absence.
A canonical digest, ETag, signature, OCFL inventory or BagIt manifest proves only its exact scoped
representation or fixity claim.

Current status is specified but unimplemented. The structural offer has zero qualified
implementations and is neither selectable nor portable.

Run from this directory:

```sh
python3 build_corpus.py
python3 validate_corpus.py
```
