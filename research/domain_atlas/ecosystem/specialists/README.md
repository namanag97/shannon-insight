# Specialist analytics and decision-science ecosystem

This directory is an evidence graph, **not a ranking, endorsement, market map, or completeness
claim**. It records specialist organizations, exact expert contributions, and dated non-LLM
innovations that can teach the SAN corpus about analytical practices, reusable libraries, product
boundaries, and delivery patterns.

```text
source evidence
   | supports
   v
claim ----> company ----> analytical practice <---- expert contribution
                 |                 ^                       |
                 |                 |                       v
                 +--> product/IP --+                  artifact/paper
                 |
                 +--> vertical case
                 |
                 +--> provider/library dependency

dated innovation ----> artifact + practice + compiler implication
```

## What “specialist” means here

An organization is eligible when analytics, operations research, measurement, process analysis,
semantic metrics, data reliability, experimentation, forecasting, simulation, or vertical decision
analytics is the principal product/service identity or a separately governed specialist unit. Broad
infrastructure conglomerates are not primary company records. They may be named only as a provider,
parent, acquisition state, maintained-artifact steward, or evidence source.

Company self-description is a **claim**, not proof of effectiveness. Official product documentation
can verify that a capability is exposed, but not that it works well in every stated industry.
Outcome claims require independent or customer-primary evidence and remain limited to the stated
deployment. Marketing feature names never create analytical-practice types.

The policy is machine-readable in `inclusion-policy.json`. Every company record carries a purity
assessment, currentness date, claim/evidence posture, LLM quarantine, limitations, and confidence.

## Record sets

- `companies.jsonl` — specialist organizations and specialist units;
- `experts.jsonl` — exact contributions and learnings, not a popularity list;
- `innovations.jsonl` — dated 2021-08-25 through 2026-08-25 non-LLM innovations;
- `sources.jsonl` — primary/authoritative evidence and explicit limitations;
- `practice-company-edges.jsonl` and `expert-practice-edges.jsonl` — normalized graph edges;
- `coverage-gaps.json` — known omissions and adjudication queues;
- `schemas/` — JSON Schemas; and
- `validate.py` — referential, evidence, date-window, purity, and schema validation.
- `all-experts-registry.jsonl` — lossless name-level navigation index across every encoded expert
  corpus; it is not a ranking or a claim to contain every expert in the world;
- `all-specialist-companies-registry.jsonl` — normalized union of the specialist and operations-
  research company corpora, retaining every source record and its limitations;
- `build_consolidated_registry.py` and `validate_consolidated_registry.py` — deterministic builders
  and integrity checks for those two navigation indexes.

All records are research candidates. `current_as_of` means “checked against the cited evidence by
that date”; it is not a promise that a firm, affiliation, product, or URL remains unchanged later.

## Validation

```bash
python3 research/domain_atlas/ecosystem/specialists/build_corpus.py
python3 research/domain_atlas/ecosystem/specialists/validate.py
python3 research/domain_atlas/ecosystem/specialists/build_consolidated_registry.py
python3 research/domain_atlas/ecosystem/specialists/validate_consolidated_registry.py
```

`build_corpus.py` is the reviewable source for the generated JSONL files. The validator uses only
the Python standard library for mandatory referential/evidence checks and additionally applies the
JSON Schemas when the optional `jsonschema` package is available.
