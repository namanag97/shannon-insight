# Intent-to-analytics compiler blueprint

The proposed compiler accepts a domain-aware analytical intent and produces a verified platform
plan: connectors, contracts, pipelines, semantic models, analytics machines, policies, tests,
jobs, deployment artifacts, monitoring, lineage, cost controls, and maintenance obligations.

## Central equation

```text
compiled platform =
    intent
  + versioned domain pack
  + source capability registry
  + horizontal machine registry
  + deployment capability registry
  + compiler policies
```

A universal, completed ontology of the world is neither possible nor required. The compiler owns
a small closed meta-model. Versioned domain packs extend it using published extension rules.

## Representation strategy

```text
authored JSON/YAML domain packs
             |
             v
typed attributed multi-hypergraph  <-- semantic resolution/query index
             |
             v
staged immutable compiler IRs      <-- deterministic compilation and proof gates
             |
             v
generated artifacts + evidence manifest
```

The hypergraph represents many-to-many domain meaning. The staged IRs make code generation,
reproducibility, validation, and error localization tractable.

## Files

- `compiler_model.json` — compiler passes, IR levels, hypergraph model, artifacts, and proof gates.
- `source_system_taxonomy.json` — protocol-oriented source classes and connector capabilities.
- `domain_pack.schema.json` — DDD plus analytical-domain pack contract.
- `intent.schema.json` — declarative analytical intent contract.
- `example_intents.json` — equivalent sports and oil operational intents.
- `validate_compiler_model.py` — structural and referential compiler-model checks.

## Non-goals

- Guessing business semantics from column names and silently treating guesses as facts.
- Generating operational actions without policy, confidence, and approval contracts.
- Listing every vendor product as a different source-system type.
- Encoding an industry directly inside connector, execution, or analytical libraries.
- Claiming compilation succeeded when a proof obligation remains unresolved.

Unknowns are first-class compiler errors or explicit human-resolution tasks—not opportunities for
implicit defaults.
