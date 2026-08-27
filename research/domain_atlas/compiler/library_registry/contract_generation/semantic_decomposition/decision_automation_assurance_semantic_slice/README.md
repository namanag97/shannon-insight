# Decision automation and assurance-case appraisal semantic slice

This deterministic, evidence-backed and unratified slice decomposes
`formalism.decision_automation_assurance`. It retains two independently adoptable products and
tests their current library ownership rather than merging them because both consume policies and
evidence.

## Boundary result

```text
facts + decision model edition
        │ evaluate
        ▼
decision result ──> action proposal ──ACL──> external authorization
                                              │
                                              ▼
                                    effect attempt/receipt/outcome

claim + criteria + argument + admitted evidence
        │ planned, independent, challengeable appraisal
        ▼
bounded verdict ──ACL──> external relying decision
```

- Decision Automation owns decision requirements, typed model/table/rule semantics, static
  analysis, testing, editions, deterministic invocation, total results, traces and proposals.
- Assurance Case Appraisal owns scoped claims, argument/defeater graphs, appraisal plans,
  occurrence-qualified appraisers, evidence admission/appraisal, findings, challenges and bounded
  verdict lifecycles.
- Authorization and effects remain external to Decision Automation. The currently attached action
  authorizer and effect port are candidate imports, not owned authority.
- Generic custody, evidence bundles, signatures, disclosure and record lifecycle are reusable
  imports. Assurance owns their claim-bound appraisal use, not their universal semantics.
- Attestation, RATS appraisal result, assurance bounded verdict and relying-party decision are four
  distinct artifacts and authorities.
- Business-decision, authorization, governance, data-use, appraisal and runtime policies are typed
  homonyms and cannot bind by the word `policy`.

## Encoded coverage

- 43 primary or official sources with supported-claim and authority limits;
- 44 semantic modules;
- 170 deterministic, formal, testing, argumentation and appraisal method types;
- 65 non-collapse laws;
- 26 expert learning profiles and 15 recent innovations;
- the exact 20-library union declared by the two products plus 48 justified neighbors;
- 24 missing library-boundary candidates; and
- 1,088 library × semantic-axis decisions, all explicitly unresolved and unratified.

The slice claims no owner decision, exact contract, qualified implementation, canonical gap
closure or compiler-selectable binding.

## Rebuild and validate

```bash
python3 build_decision_automation_assurance_semantic_slice.py
python3 validate.py
```
