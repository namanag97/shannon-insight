# Global expert-to-contribution portfolios

This is a deterministic **candidate evidence graph**, not a ranking, endorsement, citation league,
complete bibliography, or claim to contain “all experts.” Its purpose is narrower and more useful:
turn individually identified non-LLM artifacts into reviewable domain knowledge without confusing
authorship, invention, expertise, advocacy, maintenance, affiliation, implementation, or independent
replication.

```text
curated person seed                         exact primary artifact locator
      |                                                   |
      | routes research; proves nothing                   | DOI / spec / repo / release
      v                                                   v
identity candidate --qualified authored edge--> artifact edition
      |                                                   |
      | profile/ORCID review                              | content review
      v                                                   v
identity receipt                                  claim + limitation + concept
                                                          |
                                      independent replication / falsification
                                                          |
                                                          v
 family contract -> decision points -> invariants -> compiler proof
        |                  |                  |              |
        +----------> pure model libs + method libs + adapters + qualification
```

The graph currently routes 180 people through 15 domains and 60 contribution families. The pinned
Crossref snapshot provides DOI-level bibliography discovery; the builder deduplicates artifacts and
emits typed authorship, title-routing, and concept-candidate edges. Bibliographic metadata admits
only the `authored` relation. It does **not** admit inventor, expert, maintainer, advocate, implementer,
or independent-replicator claims.

## What is machine-readable

- `metamodel.json` — constitutional laws, node/role/claim types, evidence precedence, and admission rules;
- `experts.jsonl` — identity-scoped portfolio candidates and compiler learnings;
- `artifacts.jsonl` — exact DOI/primary locators, authors, dates, venues, evidence scope, and limitations;
- `contribution-edges.jsonl` — qualified authorship, family-routing, and title-term evidence edges;
- `families.jsonl` and `coverage-matrix.json` — 15-domain/60-family breadth and explicit uncovered areas;
- `compiler-library-mappings.jsonl` — family inputs, outputs, decisions, laws, candidate library seams,
  qualification requirements, and compiler targets;
- `artifact-conversion-candidates.jsonl` — one explicit person/work/edition/family conversion row per
  selected portfolio artifact, including admitted role, candidate concepts, representation inputs,
  outputs, decision points, invariants, library/compiler targets, and blocking evidence;
- `implementation-tool-evidence.jsonl` — artifacts whose titles suggest a system/tool, deliberately
  withheld from implementation admission until a versioned repository/release is verified;
- `innovations-2021-2026.jsonl` — dated candidates, deliberately withheld from innovation admission
  until novelty, predecessor, non-LLM delta, implementation, and independent evidence are reviewed;
- `review-queue.jsonl` — identity, role, content, implementation, limitation, replication, and mapping work;
- `counterevidence-queue.jsonl` — one falsification program per family;
- `bibliographic-identities.jsonl`, `bibliography-snapshot.jsonl`,
  `bibliography-dblp-targeted.jsonl`, and `collection-failures.jsonl` — pinned
  collector inputs and honest failures; and
- `schemas/`, `build_corpus.py`, and `validate_corpus.py` — contract and deterministic validation.

## Conversion rule

An expert portfolio is useful to the compiler only after this chain succeeds:

```text
person --exact role--> artifact --content claim--> semantic contract
  --scope/limitation--> decision + invariant + refusal + result
  --independent evidence--> executable oracle / fixture / qualification
  --boundary adjudication--> pure library + adapter + provider offer
  --binder proof--> compiler-selectable capability
```

Stopping at a famous name, a paper title, a citation count, or a product association would poison the
domain model. Therefore every generated compiler mapping remains
`candidate_requires_artifact_content_review` and every recent publication remains
`not_admitted_bibliographic_candidate`.

## Dirk Fahland and deep portfolios

The global graph supplies breadth. The sibling `../process_mining_expert_pilot/` supplies deep
artifact-by-artifact adjudication of Dirk Fahland’s process-mining portfolio—including exact
relations among OCEL/object-centric event data, SA-OCEL, TEKG, behavioral/event knowledge graphs,
conformance, performance, and root-cause work. That deep stream should merge by stable artifact and
concept identifiers; it must upgrade or reject candidate edges rather than overwrite evidence
history.

## Rebuild and validate

The collector is research-time network I/O; the builder and validator are offline and deterministic.

```bash
python3 research/domain_atlas/ecosystem/expert_portfolios/build_corpus.py
python3 research/domain_atlas/ecosystem/expert_portfolios/validate_corpus.py
```

To refresh discovery metadata deliberately, run `collect_crossref.py`, review the diff and failures,
run `collect_dblp_targeted.py` for ambiguous same-name portfolios, then rebuild. `collect_dblp.py` and `collect_openalex.py` are alternative discovery collectors; their
outputs are never treated as invention or expertise evidence.

## Honest gaps

This edition does not claim authoritative identity profiles for every person, complete bibliographies,
explicit CRediT roles for most papers, standards/patent completeness, software-maintenance history,
independent replication depth, practitioner coverage, geographic/language equity, or production
qualification. Those are blocking review items, not silent assumptions. The first 180-person breadth
pass is a research queue; the useful endpoint is the governed artifact-to-contract conversion.
