# SAN whole data-domain GPT Pro handoff — corrected V2

This package is the corrected handoff for a long-running GPT Pro research and implementation
program. It models the whole data, data-engineering and analytics domain; it is not a KPI,
electricity/GB or optimization project.

Upload the ZIP to GPT Pro and paste the complete contents of `MASTER_PROMPT.md`. If the interface
accepts the ZIP plus a short instruction, use:

> Read `MASTER_PROMPT.md` and every packaged input. Treat the master prompt as governing where
> inputs disagree. Execute the research and implementation program autonomously; do not stop at a
> plan. Return a resumable checkpoint and a deterministic downloadable artifact package.

## Governing correction

- Analytics is not reducible to metrics, dashboards, objectives or action selection.
- Analytical intent, practice, evidence, outputs and operational effects are separate axes.
- Open-ended exploration and investigation may produce findings or better questions, not actions.
- Electricity per useful GB is one optional late stress test, not the mission or default example.
- The target is a stable horizontal semantic/capability foundation plus extensible vertical packs.

## Contents

```text
MASTER_PROMPT.md
    Governing mission, corrected boundaries, DDD contract, Rust/YAML/IR responsibilities,
    research requirements, deliverables and acceptance gates.

current_work/analytics_landscape/
    Existing evidence-backed research seeds: analytics catalogue, data ontology, composition
    model, sports/oil packs, compiler sketch, 21-context DDD model and validators.

external_analyses/sspec-sovereign-specification-contract.txt
    Candidate universal specification constitution and registry profiles.

external_analyses/external-99-module-review-candidate.txt
    Unverified prose proposing 99 semantic modules. The claimed generated archive was not
    supplied and must not be treated as independently verified.

external_analyses/telecom-energy-compiler-stress-test.txt
    Optional narrow stress test for physical/optimization/control boundaries. It is deliberately
    demoted and must not govern the architecture.

INPUT_PROVENANCE.md
    Trust status for each packaged input.
```

## Scope

The core is provider-neutral and non-Generative-AI/LLM. Classical statistics, experimentation,
causal methods, process mining, simulation, operations research, signal processing and other
non-generative analytical practices are first-class. Conventional machine learning is at most an
optional bounded extension. Generative AI, LLM, RAG and agent concepts are quarantined.

## Existing seed validation

Run from `current_work/analytics_landscape` after extracting:

```bash
python3 validate_catalog.py
python3 composition/validate_composition.py
python3 domain_engineering/validate_domain_model.py
```

These commands validate the structure of existing research drafts only. They do not prove
semantic completeness or the new compiler acceptance gates.
