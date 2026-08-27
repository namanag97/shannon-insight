# P5 exact-contract adjudication and compiler lowering gates

P5 replaces a flat 674-gap checklist with a lossless contract hypergraph. Every exact library
contract remains an independent decision, but reusable obligations are authored at their correct
seams:

```text
                 19 archetype obligation kernels
                    structure, never semantics
                              |
23 family semantic kernels ---+--- 57 execution packages
shared vocabulary/decisions        scheduling and evidence work
                              |
                              v
                    674 exact contract dockets
                              |
                              v
                    674 compiler lowering gates
```

This is deliberately not one partition. An exact contract simultaneously belongs to an archetype
kernel, family kernel and execution package. The exact docket is the join point for their editions,
plus the library-local residuals.

## Exact dependencies preserved

- all 674 current `exact_api_contract_missing` gaps;
- all 10,784 family-axis dependencies, exactly 16 per library;
- all 666 repeated-symbol occurrence proposals across 225 affected libraries;
- one boundary-falsification cluster per library;
- 146 cross-owner collision records affecting 108 libraries;
- family source-authority and constitution decisions;
- declared semantic dependency edges;
- all owner-authored contract dimensions, placeholder types/traits/operations and structural draft
  digests.

## Artifacts

- `contract-dimension-ontology.json` defines fifteen orthogonal exact-contract dimensions.
- `exact-contract-dockets.jsonl` is the per-library hypergraph join surface.
- `archetype-obligation-kernels.jsonl` shares structural roles and laws without supplying domain
  vocabulary or defaults.
- `family-semantic-kernels.jsonl` shares family decisions while preserving every library exception.
- `execution-packages.jsonl` preserves the 57 evidence/research schedules.
- `exact-contract-ratification-packet-templates.jsonl` requires complete snapshot-bound owner
  decisions, exact API, laws, refusals, effects, compatibility, evidence and attestation.
- `compiler-lowering-gates.jsonl` gives the compiler a total refusal surface.

All 674 gates currently return `REFUSE_EXACT_CONTRACT_LOWERING`. Source authority, boundaries,
family constitutions, semantic-axis applicability and relevant shared-symbol ownership are
unratified. Structural drafts exist, but structural drafts are not exact contracts.

Run `python3 build_p5.py` and `python3 validate.py`. Ratified contracts, lowered candidates,
canonical mutations and canonical gaps closed remain zero.
