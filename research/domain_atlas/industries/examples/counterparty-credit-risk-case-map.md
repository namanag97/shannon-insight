# Counterparty credit risk: reference vertical analytical-case map

`CCR` means **counterparty credit risk** in the banking and capital-markets context. Cross-counterparty
aggregation and concentration are parts of that case family. The acronym is prohibited as shorthand
for manufacturing constraints or bottlenecks.

CCR demonstrates why an industry analytical need is not a KPI:

```text
                                   COUNTERPARTY CREDIT RISK
                                                |
                +-------------------------------+------------------------------+
                |                               |                              |
          semantic authority               analytical cases              decisions/actions
                |                               |                              |
    +-----------+-----------+       +-----------+------------+      +----------+-----------+
    |           |           |       |           |            |      |          |           |
 legal      party/group   trade +  current    future       stress/  approve/   margin/    close-out/
 netting    identity      collateral exposure  exposure     default  reject     collateral  hedge
 sets       hierarchy     state     + EAD       distribution paths   trade      call        restrict
    |           |           |       |           |            |      |          |           |
 enforce-   connected-   valuation  reconcile  simulation/  WWR +   limits/    disputes/   liquidation
 ability    party rollup market data aggregate scenario     conc.   escalation cure        feasibility
```

## The case family decomposes into distinct analytical cases

1. **Exposure reconstruction and reconciliation** — determine the authoritative trade, valuation,
   payment and collateral state and reconcile it to books and records.
2. **Legal netting-set determination** — determine which transactions may be aggregated under an
   enforceable close-out netting and margin agreement for a jurisdiction and time.
3. **Current-exposure measurement** — calculate gross and net replacement exposure under the
   applicable valuation, collateral and netting rules.
4. **Potential-future-exposure estimation** — estimate the future exposure distribution over the
   margin period of risk and contractual horizons, not merely one reported number.
5. **Wrong-way-risk diagnosis** — identify dependence between exposure and counterparty default or
   credit deterioration, including specific and general wrong-way risk.
6. **Cross-counterparty aggregation and concentration analysis** — roll exposure through legal-entity,
   connected-counterparty, industry, geography, product, collateral and funding relationships without
   applying invalid additive assumptions.
7. **Stress and default-path analysis** — evaluate market-credit joint scenarios, liquidity of close-out,
   collateral failure and simultaneous counterparty distress.
8. **Limit surveillance and pre-trade impact** — determine whether a proposed or existing exposure
   complies with limits, warnings and exception authority and what action follows.
9. **Margin and collateral adequacy analysis** — determine calls, disputes, eligibility, haircuts,
   concentration, settlement state and residual exposure.
10. **CVA and sensitivity analysis** — value counterparty credit risk with applicable spreads, netting and
    margin terms, and explain drivers and sensitivities.
11. **Counterparty deterioration and watchlist diagnosis** — synthesize credit-quality changes and
    exposure paths into governed escalation, not an opaque score alone.
12. **Close-out readiness and action planning** — test whether complete exposure and cash-flow state can
    be assembled in time and whether termination, hedging, collateral freeze and liquidation steps are
    executable.
13. **Model and system validation** — backtest, benchmark, reconcile and challenge exposure models,
    aggregation logic, assumptions and operational controls.

Each case must separately declare its question, unit and population, time horizon, decision/action,
required source state, legal authority, methods, assumptions, uncertainty, failure modes, evidence and
feedback. Measures such as CE, PFE, EAD or CVA are typed outputs or inputs of these cases; none is the
identity of the case.

## Compositional placement

```text
banking vertical pack
  CCR vocabulary + legal concepts + case definitions + decision policies
        |
        +--references--> horizontal analytical-practice registry
        |                 reconciliation, aggregation, simulation, stress testing,
        |                 concentration, dependence, sensitivity, validation, surveillance
        |
        +--requires----> source-system classes
        |                 trade capture, valuation, collateral, legal agreement, market data,
        |                 counterparty master, limits, payments/settlement, accounting
        |
        +--requires----> typed data/shape contracts
        |                 temporal trade state, netting graph, scenarios, distributions,
        |                 curves/surfaces, collateral lots, hierarchies, audit evidence
        |
        +--requires----> owned operations
                          identify, reconcile, value, net, aggregate, simulate, stress,
                          compare, allocate, explain, validate, decide, escalate
```

## Primary anchors

- Basel Committee, [Guidelines for counterparty credit risk management](https://www.bis.org/bcbs/publ/d588.pdf).
- Basel Framework, [Standardised approach to counterparty credit risk](https://www.bis.org/basel_framework/chapter/CRE/52.htm).
- Basel Framework, [Internal models method for counterparty credit risk](https://www.bis.org/basel_framework/chapter/CRE/53.htm).
- Federal Reserve, [Interagency Supervisory Guidance on Counterparty Credit Risk Management](https://www.federalreserve.gov/frrs/guidance/interagency-supervisory-guidance-on-counterparty-credit-risk-management.htm).
- Federal Reserve, [SR 21-19: Counterparty credit risk management after Archegos](https://www.federalreserve.gov/supervisionreg/srletters/SR2119.htm).

These sources establish scope and obligations; they do not by themselves prove global completeness.

