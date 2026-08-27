# Built, food and environmental analytics research pack

This pack is a machine-readable, evidence-backed decomposition of analytical work across the
land–food–built-asset–environment continuum. It covers agriculture, forestry, capture fisheries,
aquaculture, food and beverage processing, construction, engineering, real estate, facilities and
environmental services. It deliberately models **decision/diagnostic workflows**, not KPI names or
vendor product categories.

The current publication contains:

- **188 analytical cases** across 124 subindustry/operating-context candidates;
- **42 source-system capability classes**;
- **40 data-shape contracts**;
- **80 primary authoritative sources**;
- **13 analytical modes**, including diagnosis, RCA, causal studies, reliability, spatial analysis,
  process/bottleneck analysis, prediction, simulation, optimization, risk, compliance and valuation;
- no LLM, prompt, RAG, agent-memory or generative-model dependency in the analytical core.

All records validate against the shared
[`industry-research-record` schema](../schema/industry-research-record.schema.json). They remain
`sourced_candidate` research records until cross-industry deduplication and independent specialist
review.

## Files

| File | Contract |
|---|---|
| `analytics-cases.jsonl` | One situated question → evidence → decision/action → verification loop per line |
| `source-systems.jsonl` | Provider-neutral source capability requirements, not connector or vendor names |
| `data-shapes.jsonl` | Exact grain, identity, time, change, uncertainty, carrier and invalid-inference obligations |
| `sources.jsonl` | Primary standard, regulator, official-statistics, professional-body or official-implementation evidence |
| `coverage-summary.json` | Deterministic counts by domain and analytical mode |
| `build_corpus.py` | Maintainable authoring source, referential-integrity audit and deterministic generator |

Regenerate and audit:

```bash
python3 research/domain_atlas/industries/built_food_environment/build_corpus.py
```

The generator rejects missing source/system/shape references, duplicate record identities,
case records without a decision, and any LLM-dependent core case.

## Case contract

Every analytical case instantiates this coordinate system:

```text
subindustry
× sovereign decision question
× analytical mode and method
× operating object and population
× grain and time model
× source-system capability
× exact data shape
× assumptions and failure modes
× uncertainty
× intervention authority
× outcome-verification receipt
```

A metric can be an input, output or guardrail. It cannot substitute for this contract. For example,
“yield,” “OEE,” “occupancy,” “emissions,” “recovery,” “stock,” “variance” and “utilization” are not
cases without a qualified population, denominator, time, method, decision and action boundary.

The intended workflow is:

```text
observation/sample/event
  → detection or estimate
  → diagnosis / RCA
  → prediction or scenario
  → constrained recommendation
  → separately authorized action
  → observed outcome and verification receipt
```

## Industry and subindustry coverage

### Agriculture and farm services

The corpus covers crop production, irrigated agriculture, crop protection, controlled-environment
agriculture, grain storage, agricultural research, crop-risk/insurance evidence, dairy, livestock,
herd/flock health, nutrition, fertility, welfare, antimicrobial stewardship, manure/circularity,
farm machinery, equipment reliability and farm financial scenarios.

Cases include field/zone yield calibration; yield-gap and emergence RCA; stability zoning;
weather/soil/cultivar/input attribution; water balance and constrained irrigation; variable-rate
nutrient optimization; pest spread and treatment effects; spray drift/label conformance;
planting/harvest scheduling; machine queue/reliability and capacity-constrained-resource (CCR)
analysis; designed trials; crop-loss attribution; greenhouse control; grain drying/spoilage; farm
liquidity stress; milk/lactation diagnosis; feed conversion/formulation; reproductive survival;
disease/contact investigation; heat/welfare risk; withdrawal/resistance; and manure footprinting.

### Forestry and wood supply

Coverage includes probability-sample forest inventory, silviculture, growth/yield, harvest planning,
rotation economics, wildfire, fuel treatment, forest health, illegal logging/encroachment, logging,
road/skid-trail design, equipment flow, bucking/assortment, carbon MRV, habitat/ecosystem services
and reforestation.

The data model preserves `evaluation → plot → condition → tree` sampling structure and expansion
factors. A stand projection is a model result, never an observation. Forest stock, carbon stock,
timber inventory and product inventory are separate meanings.

### Capture fisheries and aquaculture

Capture-fishery cases cover reviewed stock assessment; CPUE standardization; harvest-control-rule
simulation; in-season quota/bycatch-cap depletion; catch/landing/discard reconciliation; bycatch and
protected-species mitigation; fleet/trip optimization; VMS/track risk; survey design; and landing/cold
chain flow.

Aquaculture cases cover owned cultured-cohort biomass, feeding/FCR control, water-quality forecast,
mortality/disease RCA, site carrying capacity, cohort transfer/harvest scheduling, hatchery survival,
infrastructure/escape risk, farm-gate production reconciliation and lifecycle footprinting.

The corpus forbids these false equivalences:

```text
fishing effort != catch
gross catch != retained catch != landings != sale
fishery-dependent abundance index != absolute population size
capture fishery catch != aquaculture farm-gate production
biological stock != quota account != inventory stock
```

### Food and beverage processing

Coverage spans batch/continuous manufacturing, recipe/formulation, meat/poultry pathogen controls,
dairy standardization, seafood recovery, grain milling, beverage/fermentation, packaging, cold chain,
supplier quality, sanitation/CIP, allergens, shelf life, traceability/recall, production planning,
utilities/sustainability and maintenance.

Cases go beyond OEE and yield: normalized mass/solids balance; loss-tree decomposition; starvation,
blockage, queue and CCR localization; downtime failure mechanisms; multivariate batch trajectories;
HACCP/preventive-control sufficiency; CCP exposure; thermal lethality; environmental pathogen/strain
hotspots; allergen–recipe–label reconciliation; foreign-material escape; remaining shelf life;
sanitation conformance; minimal defensible recall scope; supplier method disagreement; cold-chain
custody RCA; sequence-dependent scheduling; fermentation kinetics; and water/energy/waste flows.

Safety, quality and traceability remain separate authorities:

```text
food-safety plan definition
!= real-time process control
!= deviation and corrective action
!= verification sampling
!= product disposition
!= recall authorization
```

### Construction and construction materials

Coverage includes residential/commercial/industrial/heavy-civil project controls, lean/workface
planning, field productivity, design/change coordination, cost/quantity controls, reality capture,
quality/rework, safety, procurement, logistics, earthworks, concrete, modular/prefab, utility
coordination, systems completion, construction-materials plants and demolition/material recovery.

The project cases include schedule-logic credibility; probabilistic risk-critical paths; delay and
concurrency forensics; make-ready constraints; location flow; trade/crane/inspection CCR analysis;
installed-quantity productivity RCA; cost-to-complete distributions; graph-based change impact;
constructability/clash triage; model–procured–delivered–installed–paid quantity reconciliation;
point-cloud progress/tolerance verification; defect/rework recurrence; task-exposure RCA; dynamic
workface conflicts; long-lead risk; site logistics; mass haul; concrete maturity; and turnover
readiness.

The term **CCR is never globally normalized**. Here it means a context-qualified
capacity-constrained resource under Theory of Constraints. A source using another expansion must
declare it before semantic binding.

### Engineering

Coverage includes systems engineering, structural, geotechnical, water/hydraulics, transportation,
process engineering, MEP, surveying/geomatics, design assurance, value engineering, commissioning
and engineering-management workflow.

Cases include requirement/interface/verification coverage; technical-performance trajectories;
structural limit-state reliability; model–test–monitor calibration; uncertain 3D ground models;
settlement/slope observation; hydraulic/flood and traffic simulation; heat/mass-balance
debottlenecking; MEP diversity/sizing; deformation monitoring; independent design checks; option
trade studies; functional-performance test diagnosis; and engineering review bottlenecks.

Simulation is an evidence kind, not a physical observation. Its configuration, mesh, loads,
boundaries, solver/version, verification, validation regime and extrapolation limits remain attached.

### Real estate

Coverage includes valuation/appraisal, automated valuation-model assurance, housing/market indexes,
acquisitions, portfolio risk, leasing, property management, development/site selection, demand
absorption, capital planning, energy retrofit, physical climate risk, retail, office/workplace,
industrial/logistics and hospitality.

The records distinguish property, building, legal interest, unit/space, lease, tenant, transaction,
valuation and appraisal review. They also distinguish physical, contractual, available and economic
occupancy. A transaction price, appraised value, modeled value and constant-quality index are not
interchangeable.

### Facilities and workplaces

Coverage includes asset maintenance, work management, HVAC, energy, indoor environment/workplace,
cleaning, healthcare critical assets, data centers, campuses, public estates, security/access,
fire/life safety, vertical transportation, building water, grounds and continuity/resilience.

Cases include asset survival/bad actors; optimal maintenance; work-order queues; HVAC fault
isolation; weather/occupancy-normalized energy RCA; peak/flexible load dispatch; comfort/IAQ source
diagnosis; privacy-preserving space use; reservation/no-show mismatch; demand-based cleaning;
clinical-service availability; data-center thermal/capacity risk; central-plant dispatch; deferred
maintenance consequences; access sequence diagnosis; fire-system impairment; elevator passenger
queues; building-water loss/stagnation; irrigation/ecosystem service; and dependency-based continuity.

All recommendations that affect building controls, life safety, clinical services or occupancy are
proposals. A separately authorized control system or human role owns the actuation.

### Environmental services

Coverage includes air monitoring/planning, water quality, drinking/wastewater, collection, material
recovery, organics, landfill, hazardous waste, remediation, toxic releases, GHG inventories, LCA,
circular-economy scenarios, ecology/biodiversity, environmental compliance/management and
environmental laboratories.

Cases include monitor/sample QA; pollutant-source attribution; attainment-control scenarios;
censored water-result semantics; flow-adjusted loads; wastewater upset/aeration control;
distribution loss/contamination response; collection routing and service RCA; MRF recovery/purity
and CCR; digestion/compost kinetics; landfill airspace/gas/leachate; manifest custody; contaminant
plume inversion; remedy rebound; TRI method/change attribution; Part 98-qualified GHG accounting;
comparative LCA; waste pathway alternatives; biodiversity intervention effects; permit/obligation
evidence; EMS improvement; and lab holding-time/capacity/method performance.

## Source-system capability map

The 42 source classes are intentionally provider-neutral. They include:

- farm-management, precision-machine/ISOBUS, soil/laboratory, Earth observation, weather, irrigation,
  livestock, forest inventory/operations, wildfire, vessel/e-logbook, observers/electronic
  monitoring, stock-assessment and aquaculture control;
- MES/batch, SCADA/PLC/DCS/historian, QMS/HACCP, LIMS, EPCIS traceability, cold-store/WMS/TMS;
- construction CDE, BIM/federation, schedule, cost/EVM, field/work-package, survey/reality capture,
  engineering simulation and requirements/test/commissioning;
- property/lease, transaction/appraisal, energy benchmark/audit, BAS/BACnet, CMMS/EAM and
  occupancy/access/workplace;
- air emissions, water/treatment, waste fleet/scale, MRF/organics/landfill, hazardous-waste,
  environmental-management, lifecycle-inventory and EHS/exposure systems.

Every class must support stable object identity, schema/code/unit discovery, a reproducible snapshot
cut, bounded backfill, correction/delete semantics, event versus record time, finality/reopen rules,
least-privilege/purpose scope and evidence of what was actually read. A connector that only “returns
rows” does not conform.

## Data shapes and invalid inferences

The 40 shapes span versioned vector features, categorical and continuous raster cubes,
multidimensional coverages, point clouds, irregular/interval time series, ordered event logs,
hierarchical samples, cohort panels, transformation graphs, bitemporal ledgers, temporal constraint
graphs, typed evidence graphs, simulation arrays and attributed lifecycle-flow networks.

Selected invariants:

- CRS, geometry epoch and spatial support are required before overlay or area/volume operations.
- Forecast issue time, valid time and lead time cannot collapse into one timestamp.
- A prescription, setpoint or command is not evidence that an operation occurred.
- Event arrival order is not assumed to be event order.
- Non-detect is not numeric zero; detection/quantitation limit and method remain attached.
- A sample is not a census; inclusion probabilities, strata and expansion factors remain attached.
- A current geometry or asset hierarchy is not silently projected into history.
- Design intent, approved-for-construction, as-built and operational states remain distinct.
- Invoice, commitment, incurred cost, earned value and payment are distinct ledgers.
- Work-order count is not failure count; preventive work and censored service intervals remain clear.
- Voluntary benchmarking cohorts are not treated as representative without an explicit selection
  model.
- Monitored, factor-calculated, modeled and reasonably estimated emissions retain method identity.
- LCA comparisons require a common functional unit, boundary, allocation and impact-method version.

## Evidence posture

The 80 records are primary authoritative pages or documents from ISO, OGC, FAO, Codex, WMO, WOAH,
USDA, NOAA, USGS, EPA, FDA, OSHA, FHFA, GAO, NASA, GS1, IEC/ISA, buildingSMART, ASHRAE, IVSC,
The Appraisal Foundation, ICES, the OPC Foundation and related official bodies. They support
definitions, model families, source/data requirements, uncertainty/QA obligations and decision
workflows. They do **not** prove that one method is universally optimal or that this pack is a final
product boundary.

Representative anchors include:

- [OGC SensorThings](https://www.ogc.org/standards/sensorthings/),
  [SSURGO](https://www.nrcs.usda.gov/resources/data-and-reports/soil-survey-geographic-database-ssurgo),
  [Landsat Collection 2](https://www.usgs.gov/landsat-missions/landsat-collection-2-surface-reflectance)
  and [WMO agricultural meteorology](https://community.wmo.int/site/knowledge-hub/programmes-and-initiatives/agricultural-meteorology/guide-agricultural-meteorological-practices-gamp2010-edition-wmo-no134);
- [FAO FRA](https://www.fao.org/forest-resources-assessment/en/),
  [USFS FIADB](https://research.fs.usda.gov/understory/forest-inventory-and-analysis-database-user-guide-nfi)
  and [FAO CWP](https://www.fao.org/cwp-on-fishery-statistics/handbook/en/?type=111);
- [Codex CXC 1-1969](https://www.fao.org/fao-who-codexalimentarius/codex-texts/codes-of-practice/en/),
  [FDA traceability](https://www.fda.gov/food/food-safety-modernization-act-fsma/fsma-final-rule-requirements-additional-traceability-records-certain-foods),
  [GS1 EPCIS](https://ref.gs1.org/standards/epcis/2.0.1/) and
  [ISA-95](https://www.isa.org/standards-and-publications/isa-standards/isa-95-standard);
- [ISO 19650](https://www.iso.org/standard/68078.html),
  [IFC 4.3](https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/content/scope.htm),
  [GAO Schedule Assessment Guide](https://www.gao.gov/products/gao-16-89g) and
  [NASA Systems Engineering Handbook](https://www.nasa.gov/wp-content/uploads/2018/09/nasa_systems_engineering_handbook_0.pdf);
- [ISO 41001](https://www.iso.org/standard/68021.html),
  [BACnet](https://data.ashrae.org/BACnet/),
  [DOE Building Energy Data](https://www.energy.gov/cmei/buildings/building-energy-data),
  [IVS](https://ivsc.org/new-edition-of-the-international-valuation-standards-ivs-published/)
  and [FHFA HPI](https://www.fhfa.gov/fhfa-house-price-index);
- [EPA AQS](https://aqs.epa.gov/aqsweb/documents/data_api.html),
  [EPA WQX](https://www.epa.gov/waterdata/water-quality-data-upload-wqx),
  [EPA GHGRP](https://www.epa.gov/ghgreporting/what-ghgrp),
  [IPCC 2019 Refinement](https://efdb.ipcc-nggip.iges.or.jp/public/2019rf/index.html) and
  [ISO 14040](https://www.iso.org/standard/37456.html).

## Bounded-context implications

This research supports, but does not yet adjudicate, at least these semantic ownership boundaries:

```text
Land Parcel / Field / Crop Cycle / Agronomic Operation / Input Application / Irrigation Decision
Animal Identity / Cohort / Health Episode / Treatment / Withdrawal / Production Recording
Forest Evaluation / Plot / Condition / Tree / Stand Prescription / Timber Harvest / Carbon Claim
Biological Fish Stock / Fishing Trip / Effort / Catch / Landing / Cultured Cohort
Recipe Definition / Batch Execution / Process Control / Material Genealogy / Lab Evidence
Food Hazard Plan / CCP Monitoring / Deviation / Product Disposition / Recall
Built Asset / Design Model / Information Container / Schedule / Work Package / Constraint
Cost Ledger / Change / Inspection / Nonconformance / Requirement / Verification / Acceptance
Property / Legal Interest / Space / Lease / Occupancy / Valuation / Appraisal Review
Facility Asset / Work Order / Failure / Building Control / Energy Account / Occupancy Observation
Environmental Sample / Result / Emission Inventory / Obligation / Permit / Manifest / LCA Study
```

The same word can have incompatible laws across these contexts. `stock`, `yield`, `batch`, `lot`,
`occupancy`, `release`, `control`, `critical`, `verification`, `completion`, `margin` and `CCR` must be
bound before formula or semantic-model compilation.

## Explicit gaps and next research gates

This is intentionally an open-world corpus, not a claim that 188 records exhaust human analytical
practice. Remaining work includes:

- independent review by agronomy, veterinary, forestry, fisheries, food-process authority,
  construction-controls, engineering, valuation, facilities, environmental science and regulatory
  specialists;
- more jurisdiction-specific source packs outside the international/U.S.-heavy evidence base;
- deeper primary research for seed/genomics, horticulture, marine aquaculture, pulp/paper, specific
  food processes, tunnelling/mining-adjacent construction, rail/airport/port engineering, affordable
  housing, laboratories/cleanrooms, ecological restoration and environmental justice;
- explicit mapping of every method and operation reference to the horizontal analytics/operation
  universes, followed by cross-industry deduplication;
- adjudication of bounded-context identities, owners, laws, refusal precedence and published
  languages;
- provider conformance fixtures for each source-system class and executable oracles for key data
  shapes;
- recurring freshness checks for standards, regulations, APIs, classifications and official
  datasets.

New cases should be added only when they introduce a distinct situated question, decision/action,
study or evidence contract. Arbitrary dimension combinations, metrics, dashboard tiles, vendor
features and synonyms must not inflate coverage counts.
