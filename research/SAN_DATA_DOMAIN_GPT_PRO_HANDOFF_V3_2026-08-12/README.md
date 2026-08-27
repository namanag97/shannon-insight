# Universal data and analytics domain — GPT Pro handoff V3

This package contains the research inputs and governing specification for constructing a
machine-readable data, data-engineering, and analytics domain model and its initial compiler
kernel.

Upload the ZIP to GPT Pro and provide the complete contents of `MASTER_PROMPT.md` as the request.
When only a short accompanying instruction is needed, use:

> Execute `MASTER_PROMPT.md` using every packaged file as an audited research input. Produce the
> specified repository, executable foundation, deterministic artifacts, and resumable checkpoint.

## Files

```text
MASTER_PROMPT.md
    Governing assignment, domain scope, modelling requirements, implementation contract,
    deliverables, execution method, and acceptance criteria.

INPUT_PROVENANCE.md
    Origin and trust status of the packaged inputs.

current_work/analytics_landscape/
    Existing research catalogues, ontology, domain model, composition model, examples, and
    structural validators.

external_analyses/
    Candidate specification, module, and vertical stress-test material requiring audit.
```

The supplied inputs are drafts and candidates. Passing their validators proves structural
consistency only. `MASTER_PROMPT.md` defines the requested scope and acceptance criteria.

## Existing input validation

Run from `current_work/analytics_landscape`:

```bash
python3 validate_catalog.py
python3 composition/validate_composition.py
python3 domain_engineering/validate_domain_model.py
```
