# SAN data and analytics research/build handoff

This package is a self-contained handoff for a long-running GPT Pro research and implementation
task. Upload the ZIP to GPT Pro, then paste the complete contents of `MASTER_PROMPT.md` as the
request. If the interface accepts a file plus a short instruction, use:

> Read `MASTER_PROMPT.md` and every packaged input. Execute the program autonomously; do not stop
> at a plan. Produce a resumable checkpoint and downloadable deterministic artifact package.

## Package contents

```text
MASTER_PROMPT.md
    Governing mission, research method, implementation requirements, iteration protocol,
    evidence rules, deliverables and acceptance gates.

current_work/analytics_landscape/
    Our present evidence-backed analytics catalogue, layered data ontology, horizontal machine
    seed, sports/oil vertical packs, compiler sketch, 21-context DDD model and validators.

external_analyses/sspec-sovereign-specification-contract.txt
    Candidate universal specification constitution and registry profiles.

external_analyses/external-99-module-review-candidate.txt
    Prose report proposing 99 horizontal DAT semantic modules. The referenced generated archive
    was not supplied, so its file counts, checksum and validator claims remain unverified.

external_analyses/telecom-energy-compiler-stress-test.txt
    Detailed declaration-to-optimization/control example for reducing electricity per useful GB
    transferred under telecom constraints.
```

## Important interpretation

The package contains research drafts and candidate decompositions—not a completed Rust/YAML
domain language. GPT Pro must audit rather than blindly merge them.

The external 99-module report should first be imported as candidate records. Each candidate needs
a disposition: sovereign library, module, declarative definition, catalog entry, recipe, provider
capability, runtime mechanism, vertical concept, duplicate, or rejected boundary.

## Scope

The baseline is provider-neutral, non-AI data engineering and analytics. Classical statistics,
experimentation, causal analysis, simulation and optimization are in scope. ML data products may
be an optional extension. Generative-AI/LLM/RAG/agent concepts must remain a quarantined optional
extension and may not become dependencies of the core.

## Existing validation commands

From `current_work/analytics_landscape` inside the extracted package:

```bash
python3 validate_catalog.py
python3 composition/validate_composition.py
python3 domain_engineering/validate_domain_model.py
```

Passing these proves structural consistency of the current drafts, not semantic completeness.
