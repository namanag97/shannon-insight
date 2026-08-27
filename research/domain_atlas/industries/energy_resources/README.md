# Energy and resources analytical-need atlas

This pack is a sourced candidate decomposition of **217 decision, diagnostic, control and
workflow cases** across 27 energy/resources subindustries. It is deliberately not a KPI catalog.
Every case states the question, accountable actors, decision/action, population and grain,
effective-time model, evidence-bearing inputs, methods and operations, outputs, uncertainty,
failure modes and authority boundary.

The pack contains:

| Artifact | Records | Purpose |
|---|---:|---|
| `sources.jsonl` | 63 | Primary standards, regulators, official statistics and official implementations |
| `source-systems.jsonl` | 32 | Source-system capability and authority needs, independent of vendor |
| `data-shapes.jsonl` | 32 | Temporal, spatial, graph, signal, document, ledger, model and uncertainty contracts |
| `analytics-cases.jsonl` | 217 | Situated question → evidence → method → decision/action loops |

All records conform to `../schema/industry-research-record.schema.json`. The generator preserves
the reviewed compact seeds and makes regeneration deterministic; the validator adds referential,
coverage and non-metric semantic checks.

## Boundary and subindustry coverage

| Family | Subindustries | Cases |
|---|---|---:|
| Oil and gas | exploration/resource/reservoir; drilling/completions; production; midstream pipeline; gas processing/LNG; refining | 53 |
| Power generation | thermal; nuclear; hydropower | 22 |
| Grid and utility | transmission operations; wholesale markets; distribution/DER; retail/demand | 34 |
| Renewables and storage | solar; wind; geothermal/bioenergy; battery/pumped storage | 25 |
| Water | source/treatment; distribution; wastewater; stormwater/reuse | 34 |
| Mining and minerals | exploration/resource; extraction; processing/metals; tailings/closure | 36 |
| New energy/resources | hydrogen; carbon storage | 13 |

The boundary includes physical operations, regulated reporting, engineering and network models,
market/commercial decisions, maintenance, safety and environmental evidence. It does not claim a
single universal operating model: site, commodity, market, jurisdiction and asset class remain
explicit applicability dimensions.

## Analytical coverage

Cases may use several modes because operational questions rarely fit one technique. The 217 cases
contain 588 mode assignments:

| Mode | Assignments | Typical decision object |
|---|---:|---|
| Diagnostic | 98 | discriminate physical failure, bad data, model error or operating condition |
| Simulation | 90 | replay or project reservoir, grid, hydraulic, process, geotechnical or market state |
| Risk | 82 | choose mitigations under consequence, uncertainty and authority constraints |
| Optimization | 79 | select feasible schedule, topology, blend, release, design or maintenance portfolio |
| Material balance | 42 | reconcile mass, energy, water, inventory, emissions or custody transfers |
| Conformance | 40 | test execution/evidence against permit, standard, procedure, contract or model envelope |
| Spatial | 35 | localize plume, orebody, leak, failure, constraint, route or monitoring gap |
| Forecasting | 29 | issue vintage-preserved probabilistic demand, resource, condition or failure forecasts |
| Reliability | 28 | estimate failure behavior and select inspection, maintenance or redundancy actions |
| Process control | 26 | assess or tune governed control loops without autonomous safety actuation |
| Causal | 19 | distinguish plausible drivers and required discriminating evidence |
| Bottleneck | 18 | identify the binding physical, network, capacity or workflow constraint |
| Root cause | 17 | reconstruct incident/outage chains and corrective actions |
| Market | 17 | make dispatch, bid, hedge, congestion, valuation or portfolio decisions |

Representative cases include well-control influx diagnosis, drilling dysfunction and NPT causal
analysis, reservoir history matching, pipeline leak localization, refinery hydrogen/steam network
optimization, power-plant heat-rate loss decomposition, nuclear trip reconstruction, dam potential
failure monitoring, state-estimator topology diagnosis, protection misoperation, cascading outage
replay, DER hosting capacity, renewable forecast calibration, battery degradation diagnosis,
water-network leak localization, treatment excursion cause analysis, sewer overflow attribution,
mine-plan stochastic optimization, flotation bottleneck diagnosis, tailings failure-mode monitoring,
hydrogen embrittlement assessment and CO2 plume conformance.

## Source-system and data-shape posture

The source-system catalog covers operational historians/SCADA/DCS, alarms and events, upstream
well/reservoir stores, pipeline control and integrity, laboratories/LIMS, asset/EAM and work
management, inspection/NDE, engineering documents/configuration, safety barriers/permit-to-work/MOC,
emissions and environmental monitoring, grid EMS/ADMS/OMS/DERMS, synchrophasor/disturbance systems,
reliability reporting, market and meter data, weather/resource data, water/sewer network models,
hydrologic/groundwater monitoring, mine planning/fleet/plant control, geotechnical/tailings
monitoring, remote sensing/survey, spatial/GIS and enterprise commercial/planning systems.

The data-shape catalog makes critical semantics explicit rather than reducing everything to a
table: irregular telemetry with quality flags; alarms/event intervals; high-rate waveforms and
phasors; topology and versioned network state; depth-indexed well logs; seismic/spatial cubes;
engineering configuration and inspection media; material/energy ledgers; assays and censored lab
results; forecasts with issue time and ensembles; scenario/optimization models and solver receipts;
outage and causal graphs; schedules/resource networks; geotechnical observations; hydrologic rating
curves; emissions inventories; permit/limit applicability; market transactions; and financial
project scenarios. Each record identifies keys, grains, event/effective/issue/processing times,
correction semantics, units/bases, uncertainty and provenance.

## Evidence posture

The family evidence gate is met with **63 sources from 30 publishing bodies**: 17 standards, 16
official-statistics sources, 14 regulators, 14 official implementations and two professional-body
frameworks. Sources include SPE/PRMS, Energistics, BSEE, PHMSA, API, EIA, OPC Foundation, ISA,
NRC, IAEA, FERC, NERC, IEC, IEEE, NREL, DOE, EPA, USGS, MSHA, UNEP/GISTM, JORC, Canadian securities
regulators/NI 43-101, UNECE/UNFC, NIOSH, OSMRE, OGC and NETL.

Evidence records state what each source supports and its authority limitation. A citation supports
the existence of a domain need, reporting/data shape, method family or governed workflow; it does
**not** certify every generated case, implementation, local rule, model calibration or decision.
Public official data may be aggregated, delayed, revised, censored, confidential or defined
differently from internal operational data. Standards with paywalled normative text are represented
only to the extent supported by their official public descriptions.

## Safety, authority and LLM boundary

All case records set `llm_dependency` to `prohibited_core`. This means a language model is not part
of the authoritative calculation, protection/control path, safety classification, compliance
determination or autonomous actuation. A later product may use a quarantined assistant for search or
draft explanation only if every claim resolves to governed evidence and a human authority approves
the action.

Across the pack:

- raw observations and prior revisions remain addressable;
- observations, estimates, forecasts, scenarios and decisions remain different fact kinds;
- safety, legal, environmental and authority constraints cannot be softened as objective weights;
- model/data cutoff, assumptions, uncertainty, refusals and unresolved evidence are receipted; and
- the named operational authority—not an analytic—executes the action.

## Known gaps and next research gates

This is `sourced_candidate`, not reviewed or adjudicated ontology. Important remaining work is:

- obtain operator, engineer, regulator and market-participant review for each subindustry;
- expand jurisdictional variants beyond the strong US/North American evidence base and map local
  adoption of international standards;
- verify source URLs, editions, access conditions and supersession on a recurring schedule;
- add more subindustry-specific primary evidence for offshore wind, marine energy, district energy,
  coal/uranium mining, brines/industrial minerals, geothermal field operations, petrochemicals,
  LNG shipping, desalination, water reuse and mine closure finance;
- decompose broad combined contexts such as geothermal/bioenergy and battery/pumped storage where
  product or regulatory boundaries demand independent models;
- map exact protocol/profile/version compatibility and commercial source adapters without turning
  vendor products into domain concepts;
- test method assumptions, observability and decision loss against real field datasets, including
  rare-event and near-miss bias;
- develop privacy, indigenous/community rights, cybersecurity, records-retention and confidential
  infrastructure overlays for each applicable jurisdiction;
- independently deduplicate portable analytical practices from domain-specific cases before a
  product boundary is chosen; and
- adjudicate safety-critical cases with the relevant engineering assurance lifecycle. This research
  pack is not a certified controller, operating procedure, regulatory filing or engineering seal.

The 63-source count is for the **industry family**, as required by the shared research contract. It
must not be represented as 25 sources for each of the 27 subindustries; that deeper evidence gate is
still open.

## Rebuild and verify

From the repository root:

```bash
python3 research/domain_atlas/industries/energy_resources/build_corpus.py
uv run --with jsonschema python research/domain_atlas/industries/energy_resources/validate_corpus.py
```

The first command deterministically rewrites the four JSONL artifacts. The second validates all 344
records against the shared schema and checks uniqueness, referential integrity, minimum evidence and
coverage, question/decision structure, non-metric cases and the prohibited-core LLM boundary.
