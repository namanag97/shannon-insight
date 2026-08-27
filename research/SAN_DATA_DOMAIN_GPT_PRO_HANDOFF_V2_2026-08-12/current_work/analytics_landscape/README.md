# Analytics landscape knowledge base

This directory is a durable, evidence-backed map of the non-AI analytics sector. It links
analytics domains and subdomains to specialist companies, academic experts, practitioner
experts, standards, innovations, and primary sources.

## Files

- `analytics_knowledge_base.json` — normalized research catalogue and review state.
- `expert_learning.json` — transferable lessons and platform implications for every verified expert.
- `analytics_type_taxonomy.json` — faceted classification of every analytics type across 15 axes.
- `data_ontology.json` — layered carrier, semantic, observation, and analytical-structure ontology.
- `DATA_ONTOLOGY.md` — conceptual guide, type equations, axes, and strict boundary rules.
- `data_contract_profile.schema.json` — reusable schema for semantically typed domain contracts.
- `domain_field_profiles.json` — sports and oil-and-gas contract examples using the same type system.
- `schema.json` — JSON Schema for structural validation.
- `review_protocol.md` — recurring research and evidence-review procedure.
- `review_cycle.py` — selects due domains and manages auditable review manifests.
- `validate_catalog.py` — dependency-free structural and referential-integrity checks.
- `composition/` — machine-readable horizontal machines, vertical domain packs, and typed wiring.
- `domain_engineering/` — applied DDD context map for the data platform, including semantic
  ownership, aggregates, commands, events, refusals, laws, Rust mappings, and the analytical
  decision boundary.

## Scope

The catalogue focuses on analytics as the primary product, service, or research discipline.
General cloud vendors and diversified consultancies are excluded. Companies whose independent
status changed are retained when they remain historically or technically important, but their
status is stated explicitly.

AI-first, LLM, generative-AI, conversational-BI, and agentic-analytics capabilities are outside
the current scope. A company is not excluded merely because it later added AI features; only its
non-AI analytics capabilities are mapped.

## Run validation

```bash
python3 research/analytics_landscape/validate_catalog.py
```

## Run the recurring review cycle

Inspect ranked review needs:

```bash
python3 research/analytics_landscape/review_cycle.py status
```

Open a deep-review manifest for the highest-priority domain:

```bash
python3 research/analytics_landscape/review_cycle.py start --kind deep
```

After adding evidence to the catalogue, complete every item in the generated manifest and run:

```bash
python3 research/analytics_landscape/review_cycle.py complete \
  --run research/analytics_landscape/runs/review-identifier.json \
  --reviewer "reviewer name" \
  --mark-reviewed
```

The completion command refuses to mark a domain reviewed when checklist or minimum company/expert
coverage gates are not satisfied.

## Coverage semantics

- `seeded`: credible initial entities exist, but coverage is knowingly incomplete.
- `reviewing`: an active evidence review is underway.
- `reviewed`: the domain passed the review protocol during the recorded review window.
- `stale`: its review deadline passed.

No `seeded` domain should be described as exhaustive. `Expert` means a person with evidence of
substantial research, standards, technical, or practitioner contribution to the linked specialty;
it does not mean every employee or commentator in the market.
