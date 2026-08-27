# Research convergence rebase

This deterministic projection rebases the preserved GPT Pro research delta onto the current
canonical gap topology without promoting candidate decisions to canonical truth.

The preserved GPT Pro package is an immutable 686-quotient historical snapshot. The live topology
may grow. Every unchanged historical quotient rebases as `REBASED_PROPOSED_UNRATIFIED`; a new
quotient or positive atom delta becomes an explicit `NEW_RESEARCH_RESIDUAL_OPEN` or
`REBASED_WITH_NEW_RESEARCH_RESIDUAL_OPEN` row. Removed quotients and negative atom deltas fail and
require an explicit retirement/scope migration.

This matters for the new application-behavior family: it adds source-authority, symbol, semantic
axis, exact-contract, implementation and qualification work that the old research package never
observed. Prior research conclusions are preserved, but they are not silently projected onto the
new members. P06/P07 implementation and qualification additions remain physical evidence gates;
P01-P05 additions remain research/adjudication residuals.

Research convergence is not ratification. The projection closes no canonical gap and invents no
implementation, qualification, build, appraisal or vertical-acceptance evidence.

Run:

```text
python3 build_rebase.py
python3 validate.py
```
