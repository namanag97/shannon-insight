# Manufacturing and industrial analytics research pack

This pack models manufacturing analytics as **situated evidence-to-decision cases**, not as a list
of dashboard measures. OEE, yield, cycle time, energy intensity, defect rate and similar measures
appear only inside a case that states the population, grain, time model, evidence, method,
failure modes and accountable action.

All records are research candidates. They are deliberately upstream of product boundaries and are
not claims that one product, semantic model or implementation should own the whole domain.

## Pack inventory

| Artifact | Records | Purpose |
|---|---:|---|
| `sources.jsonl` | 62 | Verified primary or official evidence records |
| `subindustries.jsonl` | 40 | Manufacturing operating-context registry |
| `analytics-cases.jsonl` | 148 | Questions, diagnoses, decisions and analytical contracts |
| `source-systems.jsonl` | 39 | Required source classes, objects, change modes and authority limits |
| `data-shapes.jsonl` | 40 | Required grains, keys, time roles, uncertainty and provenance |

The case layer spans 73 analytical-mode labels. Every case has `llm_dependency: "none"`: its
method, evidence and action contract is defined without an LLM. Text may still be an input shape,
but no model-generated narrative is accepted as measurement, causal proof, disposition or control
authority.

## Manufacturing boundary and context spine

The registry starts with the U.S. Census NAICS manufacturing boundary and then adds operating
contexts that matter analytically. It includes food and beverage; textile, apparel and leather;
wood, pulp, paper, printing and packaging; refining, bulk and specialty chemicals, industrial
gases, pharmaceuticals and biologics; devices, plastics and rubber; cement, glass and ceramics;
steel, nonferrous metals, foundry and forging; fabricated metals and machinery; electronics,
semiconductor front-end and back-end, and electrical equipment; automotive, batteries, aerospace,
heavy transport and composites; furniture, additive manufacturing, contract job shops, photonics,
renewable-energy equipment and mineral processing.

Each context has at least one explicit case, operating mode, representative process and evidence
reference. `mfg.all` is used only for genuinely cross-manufacturing needs; it does not erase the
specialized cases.

## Analytical coverage

The 148 cases include, among other families:

- loss-tree reconciliation, OEE availability/performance/quality decomposition, microstops,
  current and migrating bottlenecks, starvation/blocking, WIP, queues, cycle time, line balance,
  changeovers, schedule adherence, capacity scenarios and execution conformance;
- SPC stability and small-shift detection, multivariate drift, capability with distribution and
  measurement assumptions, sampling design, measurement-system analysis, defect stratification,
  change-point diagnosis, causal confirmation, FMEA/control-plan feedback and tolerance analysis;
- first-pass yield, rework loops, scrap and recovery, metrology drift, vision false calls, NDE,
  predictive quality, CAPA effectiveness, deviation and OOS/OOT investigation, continued process
  verification, PAT, batch endpoint, design of experiments and review by exception;
- anomaly detection, fault diagnosis, recurrent failure, remaining life, maintenance-strategy
  evaluation, spares risk, shutdown scope, corrosion, fouling, tool wear, calibration intervals,
  field reliability, reliability growth and maintenance quality;
- finite scheduling, dispatch and inventory policies, joint maintenance-production scheduling,
  set-point optimization, control-performance assessment, soft sensors, simulation, digital-twin
  VVUQ, layout and product-mix decisions;
- alarm floods, operator response, trip sequences, bypass exposure, safeguard/barrier health,
  process-hazard and change actions, incident and near-miss learning, OT anomalies, energy and mass
  balances, water, utilities, emissions, waste, product carbon and permit conformance;
- wafer-map yield, semiconductor FDC, run-to-run control, chamber matching, overlay/CD and test
  yield; electronics solder-process and traceability diagnosis;
- automotive torque, weld, coating and end-of-line diagnosis; battery electrode, formation,
  grading and safety genealogy; additive melt-pool, qualification and distortion; composite cure,
  serialized aerospace configuration and first-article evidence;
- reaction hazards, refinery yield/blending, industrial-gas purity, mineral recovery, steel heat,
  casting, rolling, kilns, glass furnaces, paper web breaks, food kill steps and allergens,
  cold-chain exposure, textile shade, apparel flow, wood drying, plastics cavity balance, rubber
  cure, printing registration, package seals, optical yield and cut nesting.

The bottleneck cases explicitly distinguish a binding system constraint from high utilization.
Constraint identity is modeled as time-, route-, product-mix- and regime-dependent and must survive
throughput-sensitivity or simulation tests.

## Source-system needs

The carrier layer follows ISA-95 separation while preserving cross-layer identity and time:

| Plane | Representative source classes | Authority boundary |
|---|---|---|
| Business and planning | ERP/cost, APS, supplier quality, field/warranty | Orders, commitments, cost and plans; not subsecond machine truth |
| Product and process definition | PLM/PDM, CAD/CAM/CAE, engineering change, batch recipe | Designed configuration and approved process definition; not proof of execution |
| Operations execution | MES/MOM, WMS/material, traceability, workforce, manual records | Dispatch, consumption, genealogy and execution context |
| Control and observation | PLC/DCS, SCADA/HMI, historian, IIoT/edge, machine and robot controllers, semiconductor equipment, IPC CFX | Observed state and control events with clock, compression and finality hazards |
| Quality and laboratory | QMS, LIMS, instruments, QIF metrology, vision and NDE | Measurement, nonconformance and release evidence with calibration and uncertainty |
| Asset, utility and risk | CMMS/EAM, condition monitoring, energy/BMS, EHS, process safety, SIS, alarms, OT security | Maintenance, resource and safeguard evidence; never implicit command authority |
| Regulated evidence and models | Part 11-style records, digital twins/simulation | Effective, reviewable records and bounded model scenarios; not operational fact by default |

Every source-system record states expected objects, snapshot/change/stream modes, time ordering and
finality, schema semantics, system authority and known hazards such as backdating, compression,
identifier reuse, calibration drift and restatement.

## Data-shape needs

The shape layer is intentionally richer than tables of measures. It includes effective-dated
equipment and configuration hierarchies; time series, events and state intervals; batch
trajectories; genealogy and routing graphs; BOM/configuration and scheduling networks; quality,
SPC and measurement-uncertainty records; defects, images, waveforms, spectra, chromatograms, point
clouds, CAD/PMI and NDE volumes; wafer and other spatial maps; maintenance and survival/exposure
histories; alarm and safety-barrier graphs; mass-energy networks; recipes and material composition;
audit trails and control actions; simulation experiments and optimization problems; environmental,
laboratory, workforce, cost, free-text and spatial-material evidence.

All shapes retain explicit keys, event/valid/record time roles, change semantics, uncertainty,
quality provenance and relationships. As-designed, as-planned, as-executed, as-inspected and
as-maintained states are not silently conflated.

## Evidence posture

The 62 source records were URL-verified on 2026-08-25 and represent 21 publishers. They comprise
23 standards, 18 regulator sources, 8 official implementations, 6 professional-body sources,
4 official-statistics sources and 3 industry-primary sources. Publishers include ISO, IEC, ISA,
NIST, SEMI, IPC, DMSC, AIAG/IATF, MTConnect, OPC Foundation, FDA, FAA, OSHA, EPA, DOE, NASA, USDA,
USGS, the U.S. Census Bureau and the European Commission Joint Research Centre.

Evidence references establish that a need, boundary, method family or data exchange exists. They do
not by themselves validate every proposed implementation, threshold, estimator or intervention.
Many standards are licensed; public abstracts support only the stated scope, not undisclosed
requirements. Regulated decisions remain subject to the effective law, approved procedure and
accountable quality, safety or environmental authority.

## Safety and decision invariants

- Raw observations, derived features, hypotheses, recommendations, decisions and executed actions
  remain distinct and independently traceable.
- Correlation, ranking, feature importance and anomaly scores are not represented as root cause.
- Selection, censoring, regime, measurement, clock and genealogy failures are part of every case's
  failure model.
- Safety trips, control moves, batch or lot release, maintenance deferral and personnel decisions
  are never implicitly authorized by an analytical output.
- Transport to another product, line, site, material, process regime or jurisdiction requires
  revalidation.
- Workforce analytics do not authorize individual productivity ranking or punitive surveillance.

## Known gaps and next research

This is broad coverage, not a proof of universal completeness. Before adjudication it still needs:

- independent review by operators, process engineers, quality, reliability, safety, regulatory,
  metrology and industrial-engineering practitioners from each major context;
- deeper jurisdictional coverage beyond the present U.S./EU-heavy evidence base and mapping from
  licensed standards to exact clause-level obligations where access permits;
- more primary plant datasets, incident sets and reproducible benchmarks for method evaluation,
  including rare failure, safety, multimodal and distribution-shift regimes;
- decomposition below the current context spine for specialized products, unit operations and
  regulated modalities, with cross-industry deduplication of shared analytical practices;
- source-freshness monitoring, version/effectivity mapping and conformance testing for actual
  provider schemas and implementation profiles;
- formal evaluation contracts for identifiability, measurement uncertainty, calibration,
  robustness, optimization feasibility, simulator/twin credibility and intervention feedback;
- privacy, labor, export-control, trade-secret, cybersecurity and data-residency review for each
  deployment rather than blanket policy assumptions.

Accordingly all cases, systems and shapes are `sourced_candidate`, not `reviewed` or `adjudicated`.

## Rebuild and validate

`build_cases.py` is the deterministic case generator. From the repository root:

```bash
python3 research/domain_atlas/industries/manufacturing_industrial/build_cases.py
uv run --with jsonschema python research/domain_atlas/industries/manufacturing_industrial/validate.py
```

The validator applies the shared industry schema, checks minimum breadth, unique IDs, HTTPS and
verified source posture, evidence/system/shape/subindustry references, explicit subindustry
representation, analytical-mode coverage and the non-LLM boundary.
