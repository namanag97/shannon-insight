# Corpus architecture router

This package makes the Solution Synthesis & Assurance architecture the organizing nervous system
of the research corpus. Explicit governed package prefixes route every non-self file to one bounded
mechanism, input/output IR stage, compilation-frontier class, earliest binding phase, authority and
invalidation policy. Longest-prefix selection is deterministic; equal-specificity ambiguity and
unrecognized top-level packages fail validation.

Every parseable JSONL row and JSON document/array member receives a lossless occurrence route.
Declared identities receive a compact reverse-index row. Other records remain addressable through
file-route identity plus one-based record position and are covered by the file's record-set digest;
one finding per affected file preserves the need for schema-identity adjudication. Package routing
fields are not repeated for every record. File routing can remain valid when a JSON fixture refuses
parsing; the parse finding blocks only record-level claims.

Generated outputs are normalized as:

```text
record identity/position -> file route -> package route -> architecture component + IR/frontier/phase
```

`record-routes.jsonl` is the declared-identity reverse index. `record-identity-findings.jsonl`
contains files with position-addressed occurrences whose stable semantic identity remains unproven.

The router excludes its own generated directory to avoid a self-hashing fixed-point. Its bootstrap
boundary is explicit in `summary.json`.

```bash
python3 research/product_ontology/corpus_architecture_router/build_router.py
python3 research/product_ontology/corpus_architecture_router/validate.py
```
