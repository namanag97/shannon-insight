# Data-sharing contract exact-scope execution

This package executes the current abstract `library.data_sharing_contract` semantics through two deliberately different local reference implementations and a shared differential suite.

It is an **executed-test evidence packet**, not product qualification. Both implementations are authored by the same research campaign, so they do not satisfy independent-control or independent-appraisal gates.

The exact exercised contract is the current lakehouse adjudication surface:

- decisions: cut resolution, recipient binding, purpose binding, grant scope, revocation, recall and export;
- operations: draft/publish share, resolve cut, adjudicate grant, subscribe, disclose, revoke, recall and export;
- invariants: disclosures bind exact cut/recipient/purpose/grant/policy; revocation fences new disclosure; source semantic ownership does not transfer; recalls retain unresolved downstream residuals;
- refusals: all eight contract refusals are exercised by executable negative cases.

The two implementations use different state models:

1. copy-on-write functional state;
2. append-only event reduction.

The run additionally performs differential checks over the happy path, revocation and recall scenarios and retains a deterministic receipt bound to source digests.

Run:

```bash
python3 run_execution.py
python3 validate_execution.py
```

Promotion remains prohibited until semantic-law authority, independent appraisal, independently controlled implementation evidence, physical binding and vertical acceptance are supplied through the qualification program.

`qualification-binding.json` attaches the retained execution receipt to the exact qualification subject without marking the gate passed. It explicitly records that semantic-law authority, digest-bound implementation identity and reproducible-build evidence are still prerequisite vacancies.
