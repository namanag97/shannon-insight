# Industry and subindustry analytical-need atlas

The unit is an **analytical case**, not a KPI. A metric may be one input, output or guardrail of a
case, but cannot stand in for the question, diagnosis, decision or action.

```text
Industry -> Subindustry -> Operating context -> Analytical case
Analytical case =
    sovereign question
  + actors and decision/action
  + population/unit/grain/time
  + source systems and exact data shapes
  + analytical study/method/operations
  + assumptions, uncertainty and failure modes
  + outputs, evidence and feedback
```

Examples include counterparty-credit-risk investigation, process conformance, causal diagnosis,
root-cause analysis, bottleneck localization, reliability assessment, forecasting, simulation,
optimization, stress testing and decision control. “Revenue,” “risk score” or “OEE” alone is not
an analytical case.

The reference decomposition in `examples/counterparty-credit-risk-case-map.md` shows how one
industry case family expands into multiple decisions and analyses while reusing horizontal methods.

```text
metric/formula             = a governed measure or calculation
analytical practice        = a portable method/study/evidence contract
industry analytical case  = a situated question -> evidence -> decision/action loop
workflow/process           = the operational sequence in which cases and decisions occur
product                    = a user-facing outcome and lifecycle promise built from several contexts
```

Never manufacture “coverage” by treating every KPI, dashboard tile, dimension slice, vendor feature
or arbitrary combination of facets as a new analytical type.

Each industry-family research pack should contain:

- `README.md`
- `sources.jsonl` with at least 25 authoritative sources for the family;
- `analytics-cases.jsonl`;
- `source-systems.jsonl`;
- `data-shapes.jsonl`; and
- explicit coverage gaps and evidence posture.

The shared candidate schema is `schema/industry-research-record.schema.json`. These are research
candidates until cross-industry deduplication, source verification and independent review.
