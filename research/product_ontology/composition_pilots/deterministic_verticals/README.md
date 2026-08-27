# Deterministic vertical composition pilot

This candidate corpus tests whether the research graph can compile four unrelated industry cases into exact product, library and capability requirements without making an LLM or agent part of the core. It is a structural proof and refusal proof, not a production deployment, provider qualification, clinical validation, financial-control attestation or operational authorization.

```text
industry case + vocabulary + source/data/evidence references
                              |
                              v
                     product boundaries
                              |
                              v
             exact semantic/runtime library contracts
                              |
                              v
                    capability requirements
                              |
                qualified offers + receipts?
                    /                 \
                  no                   yes
                  |                     |
       refuse physical binding     bind for exact scope
```

## Current proof candidates

| Vertical | Products | Required libraries | Conditional libraries | Methods |
|---|---:|---:|---:|---:|
| Acute-care bed-flow bottleneck localization and capacity simulation | 13 | 83 | 0 | 5 |
| Retail tender, settlement and cash-loss reconciliation | 10 | 81 | 2 | 4 |
| Midstream pipeline nomination and capacity allocation | 11 | 69 | 0 | 3 |
| Manufacturing finite-capacity production scheduling | 10 | 65 | 0 | 3 |

All four graphs share 55 horizontal libraries while retaining different industry identities, units of analysis and vertical method selections. Pairwise reuse and each composition's non-shared libraries are retained separately. The commerce document branch activates deterministic OCR or form extraction only when a typed predicate requires it.

The pipeline case is also linked through the binder to a precise terminal-status requirement. The
exact GLOP/MPSolver offer is refused for that requirement; the exact highspy/HiGHS offer remains a
candidate with a typed appraisal gap. The deterministic model-class adjudicator refuses the broad
network-flow, hydraulic, scheduling and contract-priority problem as LP, while classifying only a
closed finite-coefficient continuous-LP screening cut. Physical binding still stops: the exact
offer lacks independent qualification and production-target evidence, all vertical-acceptance gates
are unexecuted, and no analytical result has effect authority. A method label never selects a solver
model class.

The manufacturing case is linked to the finite-domain CP and integer-only CP-SAT facets, the exact
OR-Tools CP-SAT Python offer and its corrected adapter occurrence. Core, global-constraint,
scheduling, enumeration and UNKNOWN-preservation profiles passed internally, while the first
retained adapter occurrence failed enumeration. The composition still refuses physical binding:
the small fixtures do not prove the plant's complete formulation, no independent appraisal or
production resource qualification exists, and no plant authority accepted schedule publication or
dispatch. Callback observation is not enumeration intent, and neither is effect authority.

## Deterministic-core law

- Parsing, type checking, formula evaluation, validation, constraint solving, numerical execution, authorization and receipts cannot be discharged by generated prose or proposals.
- No `library.mae.*` requirement enters any core graph.
- Removing the complete model/agent extension family leaves all four graphs unchanged.
- An ambient agent-injection negative twin is refused because no explicit intent selected it.
- Predictive models remain analytical method implementations with explicit data, calibration, validation and monitoring contracts; they are not silently recast as agents.

## Provider substitution

Eight substitution trials recompute compatibility from exact identity, contract coverage and
evidence. The generic OR-Tools/HiGHS and AnyLogic/Simio pairs are refused because project or product
facades are not bindable artifact offers. StatsForecast is refused because the selected health
composition requires forecast reconciliation. The executed OR-Tools/GLOP-versus-highspy trial
passes only the weaker safe continuous-LP profile: exact terminal-status substitution is refused,
and the safe profile remains unqualified because executed tests are not independent appraisal.
The precise-status refusal is now exercised in both the health test matrix and the actual pipeline
composition. The PM4Py/ProM and Tika/PDFBox observations remain unqualified. No provider is claimed
portable.

## Vertical acceptance contracts

Each composition now has one machine-readable acceptance contract and eight blocking, unexecuted
gates:

```text
source/cut fitness
  -> semantic/policy fitness
  -> method/model validity
  -> exact physical conformance
  -> operational envelope
  -> authority/safety/effect boundary
  -> outcome monitoring/reconciliation
  -> change/rollback/exit
```

The 32 gates carry case authorities, invariants, failure modes, methods, operations and evidence
references from their exact industry records. Every receipt list is empty and every verdict remains
`not_executed_blocked`. A provider test, provider qualification, structural composition or metric
improvement cannot substitute for vertical acceptance.

## Files

- `vertical-compositions.jsonl` — the four resolved structural graphs and compile-phase verdicts.
- `substitution-trials.jsonl` — exact contract/evidence-based substitution refusals.
- `optional-extension-removal-trials.jsonl` — removal proofs and the ambient-injection negative twin.
- `vertical-acceptance-contracts.jsonl` — one authority-bound acceptance contract per vertical.
- `vertical-acceptance-gates.jsonl` — 32 blocking case-specific evidence gates; none executed.
- `cross-vertical-reuse.json` — shared versus vertical-only library sets.
- `metamodel.json` — phase order and non-collapse laws.
- `manifest.json` — counts and SHA-256 digests.
- `build_corpus.py` and `validate_corpus.py` — deterministic generation and semantic validation.

Run:

```sh
python3 research/product_ontology/composition_pilots/deterministic_verticals/build_corpus.py --check
python3 research/product_ontology/composition_pilots/deterministic_verticals/validate_corpus.py
```
