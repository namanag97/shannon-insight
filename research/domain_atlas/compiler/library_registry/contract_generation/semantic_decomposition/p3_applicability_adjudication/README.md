# P3 family × semantic-axis applicability adjudication

P3 turns the 10,784 library × semantic-axis cells into an authority-review surface without inferring
applicability from spelling, generic structure, frequency or absence of a signal. The exact decision
grain remains one family default plus every candidate cluster and every library-local exception.

## Compression result

The 10,784 cells are represented exactly by 368 family-axis dockets and factored losslessly into 33
review packages keyed by semantic phase, axis and review class:

- 54 uniform, evidence-bearing matrices are ready for family-axis review;
- 204 matrices have a unique modal cluster plus explicit exception clusters and are review-ready;
- 103 matrices are blocked by generic-context evidence vacancies;
- 7 matrices are blocked because no unique modal candidate exists.

Thus 258 templates can be presented to a named family-axis authority and 110 remain fail-closed.
Review readiness is not applicability ratification.

## Artifacts

- `review-ontology.json` defines the four review classes and their required challenge.
- `family-axis-review-dockets.jsonl` preserves every matrix, cluster, member, evidence state and
  targeted evidence package.
- `family-axis-review-packages.jsonl` is the reversible quotient used to share evidence and negative
  twins. A package never bulk-approves its member families.
- `ratification-contract.json` defines required receipt fields, refusals and non-claims.
- `family-axis-ratification-packet-templates.jsonl` binds all 368 dockets to the input snapshot.
  Submission and receipt fields remain empty.
- `summary.json` and `manifest.json` provide counts and content-addressed reproducibility.

## Non-collapse laws

```text
modal cluster          != ratified family default
no discovery signal    != inapplicable
generic context        != domain evidence
family default         != library-local exception
applicability receipt  != exact contract or implementation proof
review package         != bulk authority
```

Rebuild and validate:

```text
python3 build_p3.py
python3 validate.py
```

Ratified family defaults, ratified member exceptions, canonical mutations and canonical gaps closed
remain zero.
