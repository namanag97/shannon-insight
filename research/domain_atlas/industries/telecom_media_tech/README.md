# Telecom, media and technology analytical-case research pack

This pack maps operational questions to evidence, decisions and actions across communications
networks, broadcast and digital media, advertising technology, software/SaaS, public cloud and
data-center operations. It is an open-world research candidate, not a claim that a finite catalogue
can exhaust every enterprise, jurisdiction, technology generation or vendor implementation.

The unit is an **analytical case**, not a KPI. A latency percentile, churn rate, PUE value, ad-fill
rate or error-budget balance can be an input, guardrail or output; it is not by itself a diagnostic
or decision workflow.

## Inventory

| File | Records | Purpose |
|---|---:|---|
| `analytics-cases.jsonl` | 121 | 44 telecom, 40 media/advertising and 37 software/cloud/data-center decision cases |
| `sources.jsonl` | 92 | 32 telecom, 28 media/advertising and 32 software/cloud/data-center primary sources |
| `source-systems.jsonl` | 71 | Operational source-system needs, authority boundaries and ingestion hazards |
| `data-shapes.jsonl` | 85 | Required event, graph, sequence, field, ledger, distribution and state shapes |

The cases cover 26 named subindustries:

- telecom: mobile operator, MVNO/roaming, fixed broadband, cable, fixed wireless, backbone ISP,
  enterprise connectivity, satellite/NTN, voice/UCaaS and CDN/edge;
- media: broadcast, studio/post, OTT video, streaming audio, FAST, publishing/news, gaming and
  advertising/adtech; and
- technology: software vendor, SaaS, API platform, cloud IaaS/PaaS/serverless, managed hosting and
  data-center colocation.

## Analytical coverage

Telecom cases include multi-layer alarm and service-impact correlation, packet and routing RCA,
latency/loss localization, QoS and slice assurance, RAN coverage/interference/handover diagnosis,
cell and transport bottlenecks, demand/capacity forecasting, traffic engineering, network digital
twin scenarios, energy control, signaling storms, NF overload, roaming fraud, charging leakage,
interconnect reconciliation, robocall investigation, churn/retention effects, complaint and field
dispatch diagnosis, CPE/Wi-Fi/access/optical/cable impairment localization, DNS/CDN/peering
operations, resilience stress and maintenance/change risk.

Media and advertising cases include PTP and RTP fault isolation, sender-timing and playout
conformance, SCTE cue/ad-insertion/blackout diagnosis, loudness and technical QC, archive integrity,
production and render bottlenecks, linear and FAST scheduling, content demand and commissioning,
rights/royalty reconciliation, OTT rebuffering and bitrate-ladder choice, multi-CDN steering, player
crashes and experiments, subscription churn, catalog discovery, deduplicated audience reach,
media-mix and incrementality studies, auction/floor/supply-path diagnostics, invalid traffic,
viewability, frequency/pacing/creative/ad-pod optimization, inventory forecasting, brand-safety
audit, deletion propagation and game-economy control.

Software, cloud and data-center cases include SLO burn control, trace-based RCA, tail latency,
saturation/noisy-neighbor/database/retry diagnostics, autoscaling and capacity optimization,
incident/change/canary causal analysis, restore and DR proof, product experiments, churn uplift,
pricing and unit economics, cost anomalies/rightsizing/commitments, software-delivery bottlenecks,
flaky tests and build scheduling, SBOM exposure and vulnerability prioritization, account takeover
and API abuse, data-pipeline and quality blast-radius RCA, thermal/cooling/power/storage diagnosis,
PUE driver reconciliation and carbon-aware placement.

## Evidence posture

All 92 evidence records point to official standards bodies, regulators, official implementations,
professional bodies or industry-primary publications and were accessed on 2026-08-25. The pack
meets the 25-source floor independently for each of its three evidence families. Important anchors
include 3GPP management and charging specifications; IETF IPFIX, active measurement, BMP, topology
and YANG standards; ITU, TM Forum, Broadband Forum, CableLabs, GSMA and FCC material; SMPTE,
AMWA, EBU, DVB and SCTE media standards; IAB Tech Lab and MRC advertising measurement material;
and OpenTelemetry, Prometheus/OpenMetrics, Google SRE/DORA, Kubernetes, FOCUS, SLSA, NIST,
Redfish, Swordfish, ASHRAE, ISO, DOE, Uptime Institute, SPDX, CycloneDX, CISA and CVSS sources.

`verified` on a source record means the official landing page or artifact was located and its
claimed support was checked at research time. It does not mean every edition, licensed attachment,
national adoption, vendor implementation or analytical conclusion has been independently audited.
`sourced_candidate` and `hypothesis` on cases and shapes preserve this distinction.

## Required semantic separations

- intended, configured, discovered and observed topology are distinct temporal claims;
- an alarm is not a root cause, and a probable-cause code is not causal proof;
- a packet, flow, session, service, product and customer-impact episode have different identities;
- event time, observation time, processing time, effective time and correction time are preserved;
- logical events are separate from delivery attempts, retries and compensations;
- request means, percentile sketches, censored timeouts and raw samples are not interchangeable;
- requested, limited, allocated, ready, reserved, failed-over and useful capacity are distinct;
- a media asset, essence, rendition, manifest, segment, cue, ad opportunity, auction, impression,
  valid/viewable exposure and attributed outcome are separate facts;
- devices, households, accounts and people are not silently equated in audience measurement;
- a bill, usage record, allocation, credit, adjustment and accounting entry remain reconcilable;
- intended release, built artifact, deployed version, effective exposure and rollback are distinct;
- backup success is not restore success, and declared RPO/RTO is not demonstrated recovery;
- nameplate, provisioned, reserved, available and operational facility capacity are separate; and
- PUE requires a versioned measurement boundary and interval, not only a ratio value.

Every analytical case has `llm_dependency: "none"`. LLMs may later be offered as quarantined
interfaces for evidence retrieval or narrative drafting, but they are neither the mathematical
method nor an authority for causal, billing, safety, security, compliance or control decisions.

## Known gaps and next research

The catalogue deliberately leaves open:

- vendor-private OSS/BSS counters, alarm dictionaries, RF models, router silicon signals and
  managed-cloud control-plane details;
- licensed or member-only normative text and conformance suites whose public landing pages were
  accessible but whose full clauses need authorized review;
- jurisdiction-specific telecom, privacy, advertising, accessibility, content, retention and
  lawful-intercept obligations;
- walled-garden audience and advertising logs, proprietary identity graphs, fraud labels, brand
  taxonomies and bid-fee disclosures;
- console/app-store/game-platform telemetry and off-platform virtual-economy trading;
- proprietary database optimizer state, hypervisor scheduling, accelerator fabrics, cloud quotas
  and provider failure-domain details;
- facility-specific electrical single-line diagrams, protection settings, CFD models, utility
  tariffs, marginal grid emissions and hazardous switching procedures; and
- empirical calibration, effect sizes, alert thresholds, cost curves and action authority for each
  deployment.

These gaps should become explicit evidence or integration work, never guessed fields. Before
runtime use, bind local method, operation, source-class and subindustry references to canonical
universes; verify applicable source editions; map source authority and consent; and test every
action against rollback, safety and audit requirements.

## Validation

The four JSONL files conform to
`../schema/industry-research-record.schema.json`. Local evidence, source-system and data-shape
references are closed within this pack. Repository-wide canonical bindings remain research work
and are reported by `../validate_integration.py`; structural validity is not compiler readiness.
