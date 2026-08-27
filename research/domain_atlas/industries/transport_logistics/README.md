# Transport and logistics analytical case atlas

This pack is a decision-level, non-LLM analytical atlas for the movement, handling, custody, condition, safety, reliability, and recovery of goods, people, vehicles, and transport equipment. It is deliberately **not a KPI catalogue**. A KPI can be an observation or objective inside a case, but the unit represented here is a governed question that ends in a decision, intervention, control change, investigation, or evidence-backed refusal to act.

## Pack inventory

| Artifact | Records | Purpose |
|---|---:|---|
| `analytics-cases.jsonl` | 192 | Sovereign operational questions, decision/action, grain, actors, methods, operations, evidence, assumptions, invariants, and failure modes |
| `sources.jsonl` | 84 | Standards, regulators, official statistics, professional bodies, and official implementations; 84 distinct primary URLs |
| `source-systems.jsonl` | 51 | Required source classes, governed objects, read/change modes, time/finality semantics, authority, hazards, and evidence |
| `data-shapes.jsonl` | 62 | Reusable graph, event, interval, trajectory, time-series, document, ledger, probabilistic, simulation, and optimization shapes |

All records conform to `../schema/industry-research-record.schema.json`. Every analytical case has `llm_dependency: "none"`: an LLM is neither required nor allowed to substitute for the numerical, rules, causal, optimization, simulation, safety, or adjudication core.

## Subindustry coverage

| Bounded context | Cases | Operating scope |
|---|---:|---|
| Supply networks | 16 | End-to-end constraints, lead-time RCA, amplification, planning, inventory, allocation, disruption, criticality, conformance, sourcing, network design, traceability, customs, carbon and working capital |
| Intermodal forwarding | 12 | Mode/itinerary choice, connections, handoffs, consolidation, equipment, documents, control-tower intervention, procurement, recovery, margin and claims |
| Warehousing | 22 | Receiving, WMS/WCS flow, constraint/queue diagnosis, slotting, waves, paths, docks, labor, inventory, sortation, robots, condition, maintenance, ergonomics, safety, capacity and returns |
| Parcel and postal | 14 | Scan gaps, missorts, hubs, sort plans, cutoff, route/ETA, delivery failures, address, loss, reverse flow, capacity, quality measurement and lockers |
| Trucking | 18 | HOS-feasible dispatch, ETA, detention, backhaul, lane reliability, road bottlenecks, parking, load compliance, energy, maintenance, driver safety, hazmat, carrier oversight and fleet size |
| Rail freight | 15 | Path capacity, robust timetables, yards, dwell, blocking, wagon/locomotive allocation, ETA, train control, defects, crossing risk, recovery, energy and message conformance |
| Maritime shipping | 16 | Weather routing, ETA, schedule propagation, service recovery/design, speed/bunker/CII, stowage, reefers, charges, empties, casualties, chokepoints, AIS and connectivity |
| Ports and terminals | 17 | Berths, just-in-time arrival, cranes, yard, CHE, gates, road/rail/barge connections, terminal CCR, rehandles, maintenance, energy, safety, channel, conformance, twins and recovery |
| Air cargo | 12 | Booking/capacity, ULD build, routing/ETA, special cargo, cutoffs, regulatory holds, flight allocation, recovery, message/custody conformance and claims |
| Airports and airlines | 17 | Robust schedules, aircraft/crew recovery, turnaround CCR, A-CDM, runway/gate/surface control, delay propagation, baggage, deicing, maintenance, trajectory, safety, diversion and investment |
| Public transit | 20 | Arrival/headway control, bunching RCA, connections, crews/vehicles, demand/crowding/capacity, dwell, fares, accessibility/equity, recovery, assets, safety, network design and conformance |
| Shared mobility and curb | 13 | Rebalancing, fleet/energy, geofences, parking/clutter, safety, availability/equity, curb state/allocation/dwell/pricing and privacy |

The source-system and data-shape records use `transport.logistics.cross_modal` because they are composable technical contracts. A named system may be most common in one mode, but its event, authority, finality, and data-quality concern can be reused by intermodal and control-tower cases. Analytical cases bind the explicit operating bounded context.

## What “all analytics” means here

The atlas saturates independent analytical axes rather than promising a mathematically closed list of all future questions:

- **Operating lifecycle:** plan, source, quote, book, accept, consolidate, receive, store, pick, handle, load, dispatch, move, hand off, inspect, clear, connect, arrive, unload, deliver, return, repair, recover, settle, claim, and dispose.
- **Decision horizon:** real-time control, shift/day execution, tactical capacity and contracting, strategic network/infrastructure design, incident investigation, and regulatory assurance.
- **Analytical family:** description, reconciliation, data-quality diagnosis, process mining, conformance, constraint/CCR localization, queueing, bottleneck detection, root-cause/causal inference, anomaly detection, reliability/survival, calibrated probabilistic forecasting, graph/network analysis, geospatial analysis, routing, packing, assignment, scheduling, inventory control, stochastic/robust/multi-objective optimization, control, discrete-event and agent-based simulation, stress testing, safety/barrier analysis, forensic evidence reconstruction, accounting, policy and distributional analysis.
- **Outcome family:** flow, service, safety, legality, accessibility, labor and fairness, condition/quality, reliability, asset health, capacity, cost/cash, revenue, emissions/energy, resilience, evidence sufficiency, and privacy.
- **Failure regime:** recurrent congestion, stochastic variability, structural bottleneck, missing or contradictory data, equipment failure, human/system interaction, external disruption, malicious or fraudulent behavior, and rare high-consequence events.

New cases should be added when a new tuple of actor, sovereign question, intervention, population/grain, time model, evidence contract, or failure mode cannot be represented by an existing case. Merely adding another metric or slice does not create a new analytical case.

## Metric versus analytical case

“Truck turn time” is a measure. “Which queue, document, inspection, lane, chassis, container, yard, equipment, or appointment condition causes delay, and which control should change?” is an analytical case. The latter binds:

1. a governed population and event grain;
2. competing causal mechanisms and capture failure modes;
3. the actor authorized to intervene;
4. feasible actions and non-negotiable safety/legal constraints;
5. source authority, time/finality, uncertainty, and lineage;
6. post-decision monitoring and an expiry/reassessment condition.

That distinction is applied throughout `analytics-cases.jsonl`.

## Source and semantic posture

The evidence set is intentionally dominated by primary authorities:

- cross-modal semantics: ASCM SCOR, GS1 EPCIS/CBV and traceability, UN/CEFACT MMT, UN/LOCODE, WCO, OGC;
- safety and regulation: OSHA, NIOSH, FMCSA, FHWA, FRA, PHMSA, FTA, FAA, IMO, IHO;
- modal interoperability: UPU/USPS, DATEX II, ERA TAF TSI and railML, DCSA and TIC 4.0, IATA ONE Record/AIDX/Cargo-XML, A-CDM, GTFS/NeTEx/SIRI, MDS/GBFS/CDS;
- official operational/statistical evidence: FAF, CFS, NOAA AIS, USACE waterborne commerce, UNCTAD connectivity, ASPM/BTS, NTD.

A case evidence reference means the source supports the governed objects, lifecycle, constraints, data semantics, safety obligation, or official population needed by the case. It does **not** claim that a regulator or standard mandates the exact algorithm named in `method_refs`.

Important semantic separations retained by the pack:

- plan/request/target/estimate versus observation/actual versus legal adjudication;
- business effective time versus source record time versus ingest time versus decision time;
- mutable low-latency feeds versus revisioned operational truth versus settled regulatory/financial records;
- physical object identity versus document identity versus journey/case identity;
- a missing event versus a proven missing physical action;
- sampled or modeled official statistics versus execution-level census;
- screening/risk prioritization versus causal fault or liability.

## Source-system concerns that must survive ingestion

Connectors are insufficient if they flatten source behavior. Implementations must retain:

- authority by object and field, partner/jurisdiction scope, edit actor, and legal status;
- CDC/event ordering, corrections, cancellations, supersession, restatement, and settlement finality;
- event time, record time, ingest time, valid time, service/operating date, plan/prediction vintage, and local timezone;
- master-data and topology versions, code-list/schema profile, unit and coordinate reference system;
- sensor calibration, sample/coverage regime, receiver/device identity, GPS/map-match confidence, and outage intervals;
- nested logistics units, consists, ULD/container inheritance, interline/interchange custody, and split/merge genealogy;
- privacy tier and purpose limitation for workers, drivers, passengers, payment tokens, addresses, and precise trajectories.

## Evidence status and limitations

Records are `sourced_candidate`, not adjudicated production designs. Sources were accessed on 2026-08-25. The URLs were checked for authoritative ownership and relevance, but the pack still requires independent domain review, jurisdiction-specific legal review, local system profiling, algorithm validation, and safety assurance.

Known gaps and boundaries:

- local union agreements, labor rules, tariffs, contracts, exemptions, airport/port/rail operating rules, and municipal ordinances cannot be universalized;
- proprietary TOS/WMS/WCS/ELD/CAN/interlocking/airline/airport/vendor fields require versioned local profiles;
- source availability is uneven: some bodies license detailed schemas, some feeds require registration, and official statistics have lag or sampling boundaries;
- pipeline transport, military logistics, autonomous road certification, space transport, and deeply specialized commodity regimes need separate bounded-context packs;
- cybersecurity analytics is represented only where it affects evidence and operational safety; it needs a dedicated threat/response atlas;
- privacy, labor fairness, safety, and liability decisions require human governance even though no LLM is used;
- case coverage is open-world. The count is a researched saturation baseline, not proof that no future subindustry, regulation, failure mechanism, or decision question can exist.

## Suggested use

Select cases by actor and decision horizon, then bind each case to local systems and shapes. Adjudicate object authority, clocks, population, assumptions, invariants, failure modes, and decision rights before choosing an implementation. Build semantic-layer measures only after that binding: a reusable measure is valid only within the case’s population, grain, time/finality, and uncertainty contract.
