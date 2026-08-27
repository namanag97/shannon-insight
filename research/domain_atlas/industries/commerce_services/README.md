# Commerce and consumer-services analytical-case atlas

This pack is a sourced research candidate for retail, wholesale, consumer packaged goods (CPG),
ecommerce, hospitality, travel, restaurants and consumer services. It is deliberately a
**pre-product, pre-bounded-context evidence pack**: its cases, source-system needs and data shapes
are inputs to later domain-driven-design adjudication, not a proposed product catalog or a claim
that the domain boundary is settled.

The generated edition contains:

| Artifact | Records | Purpose |
| --- | ---: | --- |
| `analytics-cases.jsonl` | 216 | Situated question-to-evidence-to-decision/action loops |
| `source-systems.jsonl` | 30 | Authority, objects, access/change semantics and hazards |
| `data-shapes.jsonl` | 24 | Grain, keys, time roles, relationships, provenance and uncertainty |
| `sources.jsonl` | 56 | Primary standards, regulators, official statistics and official implementations |
| `manifest.json` | 1 | Reproducible counts and pack metadata |

Every line conforms to the shared candidate contract in
`../schema/industry-research-record.schema.json`. `build_pack.py` is the deterministic source for
the JSONL artifacts; `validate_pack.py` enforces pack-specific coverage and referential rules.

## Analytical case, not KPI

A case must name a sovereign question, decision actor, action, population, native grain, time
model, source cut, shapes, methods, operations, uncertainty, assumptions, failure modes,
invariants, evidence and feedback. A metric can be an input, output or guardrail, but is not itself
a case.

Examples of the distinction:

| Metric-only fragment (excluded) | Analytical case represented here |
| --- | --- |
| shrink rate | localize whether receipt, transfer, shelf, scan, theft or master-data paths caused the discrepancy, then issue a controlled investigation/recount action |
| conversion rate | estimate a pre-registered checkout intervention effect with exposure integrity, interference checks, guardrails and rollback criteria |
| occupancy or RevPAR | forecast stay demand and jointly control room rate/inventory under overbooking, displacement and service constraints |
| on-time delivery | reconstruct case events, identify the responsible queue/resource bottleneck and test a feasible routing or capacity intervention |

## Subindustry coverage

Counts reflect case applicability. A reusable case can apply to several subindustries, so this table
does not sum to the 216 unique records.

| Family | Subindustry | Cases |
| --- | --- | ---: |
| Retail | grocery; convenience; fashion/specialty; omnichannel | 32 each |
| Wholesale | merchant distribution; B2B marketplace | 21 each |
| CPG | food/beverage; personal/household; durable goods | 26 each |
| Ecommerce | direct-to-consumer; marketplace; subscription | 30 each |
| Hospitality | lodging; resort; short-stay | 26 each |
| Travel | airline/airport; tour/destination; ground/rental | 29 each |
| Restaurants | quick service; full service; delivery/catering | 26 each |
| Consumer services | appointment; field/home; contact/subscription | 26 each |

The case inventory covers operational control, diagnosis, causal analysis, experimentation,
forecasting, process conformance, root-cause localization, bottleneck analysis, simulation,
optimization, pricing, assortment, inventory, recommendation, anomaly, reliability, risk, fraud,
survival, segmentation, spatial, text and vision work. The manifest records the exact multi-label
counts; headline coverage includes 84 diagnostic, 77 forecasting, 73 optimization, 61 causal, 59
process, 56 simulation, 47 root-cause, 32 experimental, 21 recommendation, 19 pricing and 19
bottleneck-tagged cases.

The inventory includes such decision families as phantom inventory, lost-sales estimation,
replenishment, allocation, substitution, promotion incrementality, price elasticity, markdown,
assortment and space, queue/capacity control, pick/pack/dispatch conformance, returns and refunds,
marketplace quality/fraud, subscription retention, demand and production planning, trade-promotion
causality, traceability/recall exposure, perishability and HACCP, room/flight capacity and revenue
management, disruption recovery, baggage and airport milestones, kitchen flow, labor scheduling,
appointment no-show and overbooking, field-service routing/first-time-fix, contact-center routing,
service recovery and experimentation.

## Source-system and data-shape breadth

The 30 source-system needs span POS/tender, order management, catalog/PIM/menu, inventory ledger,
procurement/ERP, WMS, transportation/dispatch, pricing/promotion/revenue management,
merchandising, CRM/loyalty/CDP, digital behavior, advertising/experimentation, payment/fraud,
returns/recommerce, supplier/trade promotion, sensor/RFID/vision, workforce/time/payroll,
customer-service/contact-center, PMS/CRS, hotel distribution, housekeeping/maintenance,
airline offer/order, flight/airport operations, baggage/departure control, travel booking,
restaurant KDS, food-safety/HACCP, appointment/field service, external context and a quarantined
LLM gateway. Each need distinguishes operational authority from convenient availability and
records late-arrival, correction, finality and schema hazards.

The 24 shapes cover transaction lines; state events; inventory snapshots plus movements;
bitemporal master/hierarchy records; offer and price waterfalls; journey events; experiment and
causal panels; forecast vintages; process logs; queue intervals; spatial trajectories; traceability
graphs; sensors; image/video detections; text/audio conversations; documentary evidence;
workforce schedules/actuals; hotel room-nights; flight milestones; routed work orders; HACCP logs;
recall-exposure graphs; and LLM inference receipts. Shapes preserve event, effective, recorded,
decision and analysis-cut time rather than flattening them into one timestamp.

## Evidence posture

The 56 sources are first-party or primary authorities: 15 standards, 10 regulator sources, 12
official-statistics sources, 17 official implementation/API sources and 2 professional-body
sources. They include GS1, the United Nations, U.S. Census Bureau, FDA, Codex, USDA, CPSC, FTC,
CPPA, EDPB, PCI SSC, W3C, NIST, OpenTravel Alliance, Oracle, IATA, EUROCONTROL, U.S. DOT,
Eurostat, Shopify, Amazon, Google, Square, Twilio, DOL and BLS.

`verification_status: verified` means the cited official page was reachable and reviewed as an
evidence candidate on 2026-08-25. It does **not** mean that a regulatory interpretation, connector
contract, analytical identification strategy or product boundary has been independently
adjudicated. A case may cite direct vertical evidence plus transitive source-system/shape evidence;
neither kind grants automatic decision authority.

LLMs are not a core dependency. Fourteen cases mark LLM use as `quarantined_optional`; any such
case must use the governed gateway and inference-receipt shape. Generated extraction, summary or
proposal output remains provenance-bearing and abstainable, and never receives direct write or
decision authority. All other cases declare `llm_dependency: none`.

## Known gaps and non-claims

- The family-level 25-source threshold is exceeded, but this edition does **not** claim 25 unique
  primary sources for each of the 24 narrow subindustries. A stricter per-subindustry gate needs a
  dedicated second pass, especially for wholesale, short-stay, resorts, tours/destinations,
  ground/rental and specialized consumer services.
- Breadth is high, but enumeration is not closed. Cruise, rail/bus, casinos/gaming,
  attractions/events, fuel retail, pharmacy commerce, auto dealerships, salons/wellness, funeral
  services and repair specialties need explicit subindustry packs rather than silent inference
  from adjacent cases.
- Jurisdiction-specific adoption and change—food codes, traceability dates, privacy/automated
  decision rules, labor scheduling/tips, negative options, platform obligations, occupancy taxes
  and passenger protections—requires current local legal review. Sources are not legal advice.
- Several standards and provider schemas are versioned, partially gated or proprietary. Actual API
  availability, history depth, quotas, write permissions, deletion semantics, security controls and
  commercial cost need provider-specific conformance tests.
- Causal and experimental cases are research designs, not push-button estimators. Eligibility,
  overlap, interference, measurement integrity, unobserved confounding, heterogeneous effects and
  rollback safety need case-specific review.
- Method and operation references are candidate horizontal capabilities. They require
  cross-industry registry reconciliation before becoming stable shared semantics.
- Case reuse across named subindustries is intentional but can hide local vocabulary, constraints
  and owner differences. DDD review must decide whether question, authority, invariants, lifecycle
  and change cadence support one context or several.
- This pack does not propose products, dashboards, autonomous actions, universal formulas or a
  canonical enterprise model. It supplies evidence-bearing analytical needs from which those later
  decisions may be made.

## Reproduce and validate

From the repository root:

```bash
python3 research/domain_atlas/industries/commerce_services/build_pack.py
python3 research/domain_atlas/industries/commerce_services/validate_pack.py
```

The pack validator checks JSONL integrity, required fields, cross-file references, source count and
verification, mandatory analytical modes, a minimum of 20 applicable cases per subindustry,
question/action/failure/invariant structure, complete system/shape use, LLM quarantine and manifest
consistency. The shared JSON Schema should also be run in the repository-wide validation pipeline.
