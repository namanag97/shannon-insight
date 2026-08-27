# Finance and insurance analytical-case atlas

This pack is a sourced candidate inventory of decisions and analytical questions for finance and insurance. Its unit is an **analytical case**, not a KPI, dashboard, model, or product feature. Every case fixes a question, action, actors, unit and population, grain and clocks, source-system and data-shape needs, methods and operations, assumptions, invariants, failure modes, evidence, and limitations.

The pack was researched and validated on 2026-08-25. It contains:

| Registry | Records | Purpose |
|---|---:|---|
| `analytics-cases.jsonl` | 268 | Non-LLM diagnostic, RCA, detection, prediction, causal, experimental, process, capacity, optimization, simulation, stress, surveillance, reconciliation, valuation, and decision/control cases |
| `sources.jsonl` | 63 | Primary standards, regulators, official implementations/statistics, and industry-primary evidence from 31 publishers |
| `source-systems.jsonl` | 41 | Capability classes with objects, read/change modes, time/finality, semantics, authority, and hazards |
| `data-shapes.jsonl` | 39 | Required grains, keys, modalities, time roles, change semantics, uncertainty, provenance, and relationships |
| `build_cases.py` | — | Deterministic case-corpus generator |
| `validate_pack.py` | — | Shared-schema, reference-integrity, modality, evidence, breadth, and CCR gates |
| `coverage.json` | — | Machine-readable count, status, scope, and gap declaration |

All 268 cases declare `llm_dependency: none`. Language models may later assist discovery or explanation outside the governed analytical core, but no case here needs an LLM to compute, reconcile, authorize, or evidence its result.

## Subindustry and operating coverage

The 48 assigned labels span retail, commercial, universal, and treasury banking; payments cards, merchant acquiring, PSPs, instant, wholesale, cross-border, and stablecoin rails; consumer, mortgage, commercial, and asset-finance lending plus BNPL; broker-dealers, trading, derivatives, and post-trade; institutional, fund, private-fund, and wealth/advisory businesses; property/casualty, specialty, life, health, long-term-care, annuity, claims, investment, reinsurance, and retrocession operations; open finance, embedded finance, digital assets, and stablecoins; and payment systems, CCPs, CSDs, trade repositories, and exchanges. AML, fraud, sanctions, conduct, fair-lending, reporting, and operational-risk concerns cross those boundaries.

Cases are grouped as follows:

| Case family | Count | Representative concerns |
|---|---:|---|
| Banking | 20 | Balance-sheet and margin diagnosis, liquidity, IRRBB, deposit behavior, stress, transfer pricing, reconciliation, process and capacity |
| Counterparty credit risk | 24 | Identity/grouping, netting, exposure, collateral, PFE/EAD/CVA, wrong-way risk, concentration, default stress, limits and actions |
| Payments | 25 | Message and ledger reconciliation, fraud, liquidity/queues, fees, routing, FX/settlement, operations, causal and experimental policy evaluation |
| Lending | 27 | Origination, underwriting, pricing, affordability, fair lending, portfolio migration, CECL/IFRS 9, recovery, collections, process mining and optimization |
| Financial crime | 18 | Entity/network resolution, transaction monitoring, sanctions, SAR quality, typology drift, investigator capacity and governed actions |
| Capital markets | 28 | Feed and book integrity, best execution, TCA, market and counterparty risk, valuation, P&L explain, surveillance, lifecycle and settlement |
| Asset and wealth management | 24 | Performance/attribution, valuation, liquidity, portfolio construction, limits, flows, suitability, conflicts, filings and operations |
| P&C and specialty insurance | 30 | Pricing, underwriting, claims, reserving, leakage/fraud, catastrophe, exposure accumulation, process, capital and intervention |
| Life, health, LTC and annuities | 18 | Mortality/morbidity/lapse, ALM, guarantees, utilization, provider access, claims, IFRS 17 and capital |
| Reinsurance and retrocession | 15 | Treaty terms, bordereaux, aggregation, recoverables, reinstatement, spirals, collateral, cat and capital stress |
| Fintech and digital finance | 18 | Consumer-authorized data, consent, APIs, BNPL, embedded finance, stablecoins, custody, on-chain/off-chain reconciliation and safeguards |
| Financial-market infrastructure | 21 | Payment/settlement queues, CCP margin/default resources, CSD finality, participant risk, recovery, operational resilience and PFMI disclosure |

## Counterparty credit risk is a bounded context, not a KPI

Here **CCR means banking counterparty credit risk**. It is represented by 24 cases and several linked bounded-context records:

| Concern | Required semantics and data | Example decision |
|---|---|---|
| Counterparty identity | Legal entity, LEI, direct/ultimate parent, connected-client and economic-dependency graph, ownership effective dates, exclusions and overrides | Merge or split groups; escalate unresolved identity; set group scope |
| Contract and netting | Trade lifecycle, product, agreement, netting set, collateral set, jurisdiction, enforceability opinion, close-out and margin-period-of-risk terms | Permit or disallow netting; change agreement; restrict jurisdiction/product |
| Exposure | Current exposure/replacement cost, mark-to-market, cashflows, collateral allocation, simulated future exposure cube, PFE horizon/profile and EAD transformation | Approve, resize, hedge, novate, compress, clear or reject activity |
| Valuation adjustment | PD/LGD, funding and market scenarios, CVA contributors and hedges, model/version provenance | Price or hedge CVA; allocate limits/capital; challenge valuation |
| Wrong-way and concentration | Counterparty/guarantor/collateral/underlying dependencies, country/sector/issuer/group aggregation and stress co-movement | Tighten terms, substitute collateral, diversify or reduce exposure |
| Default and stress | Historical/hypothetical shocks, largest-counterparty default, intraday and margin stress, liquidation/close-out timing, contagion and survivor resources | Invoke limits, margin, close-out, default-management or contingency action |
| Control and explainability | Pre-trade and post-trade limits, breaches, overrides, decision receipts, contributor drill-down and reconciliation | Block/approve with authority; remediate data/model/control cause |

The CCR source-system classes deliberately separate party/LEI authority, trade capture, collateral and margin, pricing/risk simulation, CCR aggregation, limits, and accounting/reporting. The central grains are legal-entity relationship, trade/netting-set, collateral lot/obligation, counterparty-netting-set-scenario-horizon exposure, and decision/override receipt. That separation prevents entity consolidation, legally enforceable netting, market simulation, collateral eligibility, and management-limit policy from being collapsed into one measure.

## Evidence posture

The 63-source registry contains 60 regulator, standard, official-statistics, or official-implementation records and three professional-body/industry-primary records. The backbone includes BCBS and Basel Framework materials; Federal Reserve, FFIEC, FinCEN, OFAC, CFPB, OCC, FDIC, FASB, SEC, FINRA, and CFTC sources; ISO 20022 and CPMI/IOSCO PFMI; EBA, ECB, ESMA, EIOPA, IFRS, IAIS, and NAIC sources; GLEIF; and primary FIX, FpML, ISDA, ACORD, and GIPS specifications or implementations.

Evidence references are attached to every case, system, and shape. They establish why the analytical concern and required data exist; they do not certify a single universal formula. Exact formulas, eligibility rules, scenario parameters, regulatory versions, legal opinions, and management thresholds must be pinned in a jurisdiction/product/entity-specific semantic policy before execution.

The status `sourced_candidate` is intentional. A source can support a case without adjudicating its interpretation for every legal entity, product, jurisdiction, or reporting date. Promotion to `reviewed` or `adjudicated` requires accountable domain, legal/compliance, model-risk, data-authority, and decision-authority review.

## Source-system and data concerns

Capability classes are vendor-neutral and cover ledgers and subledgers; payments gateways, switches, settlement and disputes; customer, party, KYC, sanctions, LEI and ownership graphs; origination, servicing, collateral, collections and impairment; market data, security master, OMS/EMS, trade capture, pricing/risk, margin, repositories and settlement; portfolio accounting, performance, transfer agency and advice; policy, billing, claims, actuarial, catastrophe, reinsurance and investment systems; open-finance consent/API, BNPL, blockchain node/indexer and digital custody; CCP/CSD/RTGS/FPS infrastructure; regulatory reporting, case management, general ledger, documents and operational telemetry.

The shape registry explicitly represents relational, event, bitemporal, graph, tensor/cube, time-series, order-book, spatial/grid, document, message, XBRL/taxonomy, ledger, process/conformance, model-governance, reconciliation, and decision-receipt data. Each shape distinguishes authority and provenance, event/effective/as-of/processing/finality time, mutable state from append-only events, observation from estimate, correction from deletion, and fact from legal/model interpretation.

## Validation

From the repository root:

```bash
UV_CACHE_DIR=/tmp/uv-cache-finance-insurance \
  uv run --with jsonschema \
  research/domain_atlas/industries/finance_insurance/validate_pack.py
```

The validator checks the shared `industry-research-record.schema.json`, record-ID uniqueness, all local references, evidence and publisher minima, subindustry breadth, allowed and required analytical modes, question/action framing, `llm_dependency`, and the explicit 24-case CCR contract.

## Known gaps and non-claims

- This is a broad candidate atlas, not proof that a finite list exhausts every enterprise, product, jurisdiction, decision, or edge case. New bounded contexts and cases should be added when materially different units, authority, grains, clocks, invariants, or actions appear.
- The 63 sources cover the industry family and all major families above; there are not 25 independent primary sources for every one of the 48 labels. Treat any per-label 25-source requirement as an unmet evidence-expansion gate, not as completed coverage.
- Evidence is cluster- and concern-level. Clause-level traceability from each input, formula, threshold, and action to exact source sections remains future adjudication work.
- Proprietary payment-scheme, exchange/FMI, vendor, credit-bureau, catastrophe-model, insurer-rate-filing, treaty, and market-data specifications are not reproduced. Implementations must bind licensed rulebooks and schemas.
- Jurisdiction-specific prudential, conduct, privacy, insurance, securities, tax, accounting, insolvency, close-out-netting, and reporting rules can conflict or change. Digital-asset, stablecoin, open-finance, and BNPL rules are especially time-sensitive.
- Health-insurance cases cover payer analytics only; clinical-care decision support and jurisdiction-specific protected-health-information controls are outside this pack.
- Academic method benchmarking and vendor/model comparison were not used as normative evidence. Model selection, backtesting, calibration, stability, bias, uncertainty, and approval are explicit downstream model-governance obligations.
- Public sources often cannot expose participant-, counterparty-, claim-, order-, or treaty-level data. Synthetic or confidential validation is required before claiming empirical performance.
- URLs and editions are a dated evidence snapshot. A recurring freshness and link-integrity review is required before regulatory or production reliance.

