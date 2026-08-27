# Public service, safety, justice, social-service, education, research, and nonprofit analytics

This is an evidence-backed **analytical-case corpus**, not a KPI catalog and not a product
boundary. It covers provider-neutral, non-LLM analytical work across public administration,
public safety and emergency management, public defense sustainment where public evidence permits,
justice, social services, education, research institutions, nonprofit operations, international
development, and humanitarian response.

All records are `sourced_candidate` research inputs until cross-industry deduplication,
jurisdiction-specific legal review, practitioner review, independent methodological appraisal, and
adjudication. An official reporting specification proves the existence and semantics of a source
contract; it does **not** by itself prove that a proposed analytical method is effective, causal,
fair, lawful, or fit for an operational decision.

## Corpus inventory

| Artifact | Records | Unit |
|---|---:|---|
| `sources.jsonl` | 59 | primary standard, regulator, official statistic, official implementation, or primary professional source |
| `source-systems.jsonl` | 27 | provider-neutral source-system capability need |
| `data-shapes.jsonl` | 25 | exact analytical shape with grain, keys, time, change, uncertainty, lineage, and relationships |
| `analytics-cases.jsonl` | 108 | decision, diagnostic, evaluation, workflow, simulation, or optimization case |

The analytical cases are distributed as follows:

| Sector family | Cases | Representative subindustries |
|---|---:|---|
| Public administration | 15 | digital service, permitting, regulation, procurement, grants, finance, workforce, public works, records access, policy, planning |
| Public safety and public defense | 15 | emergency communications, emergency management, fire/EMS, law enforcement-data quality, road safety, hazard mitigation, unclassified defense sustainment |
| Justice | 15 | courts, prosecution/public defense, legal aid, corrections, reentry, supervision, juvenile justice, justice statistics |
| Social services | 16 | access, income support, food assistance, homelessness, child welfare, casework, workforce development, health coverage, housing, program integrity |
| Education | 16 | early learning, K-12, civil rights, assessment, special education, workforce/adult education, operations, planning, higher education |
| Research institutions | 15 | sponsored programs, research finance, laboratories, core facilities, clinical trials, research integrity, repositories, libraries, scholarly communication |
| Nonprofit/NGO/humanitarian | 16 | direct service, fundraising, volunteers, grantmaking, governance, finance, development cooperation, international programs, humanitarian response and logistics |

Examples are full analytical objects: permit rework localization; emergency dispatch interval RCA;
court continuance bottlenecks; benefit underpayment/overpayment causal pathways; coordinated-entry
access fairness; assessment measurement invariance; special-education service-delivery conformance;
trial outcome-switching audit; sample lineage integrity; humanitarian needs synthesis; aid exclusion,
duplication and diversion diagnosis; and do-no-harm-constrained allocation.

## Analytical coverage

The pack exercises, in case-specific combinations:

- service journey and funnel analysis, process mining, conformance checking, queueing, critical-path
  and bottleneck localization;
- diagnostic analysis, fault trees, control analysis, root-cause analysis, record-linkage and
  measurement-error sensitivity;
- cohort, panel, sequence, recurrent-event, multistate, survival, competing-risk, reliability,
  maintainability, calibration, psychometric and small-area methods;
- randomized and quasi-experimental evaluation, target-trial emulation, interrupted time series,
  difference-in-differences, synthetic control, mediation, implementation fidelity and contribution
  analysis, but only when their identification conditions are satisfied;
- probabilistic and hierarchical forecasting, capacity planning, location-allocation, scheduling,
  inventory/network flow, robust and stochastic optimization, microsimulation, discrete-event and
  hazard scenario simulation, stress testing and value-of-information analysis;
- fraud-risk and anomaly **triage** with adjudicated samples and control feedback—not automated fraud
  findings;
- safety, civil-rights, equity, geographic-access, disclosure-risk and subgroup error analysis with
  explicit denominator, uncertainty and protected-use boundaries.

There is no LLM dependency. Every case is marked `llm_dependency: none`. Text-bearing operational
systems may still exist, but these core cases use authoritative structured events, metadata,
human-coded taxonomies, validated instruments, or governed review findings. Any later language-model
augmentation must remain optional, separately evaluated, and unable to create authoritative facts or
high-impact decisions.

## Source-system and shape boundaries

The source-system records separate operational authority from analytical use. They include case and
service systems, contact centers, licensing/inspection, grants and contracts, ERP ledgers, workforce
and credential rosters, asset/work-order systems, GIS, CAD/dispatch, incident reporting, EOC logs,
court and corrections systems, eligibility/payment systems, HMIS, WIOA participant systems, student
information and assessment systems, postsecondary administration, research awards/protocols,
scholarly identifiers, LIMS/instruments, donor/volunteer CRM, IATI/CRS activity systems, and protected
humanitarian assessment/distribution/feedback systems.

The data shapes prevent common semantic collapses. In particular:

```text
application completeness != approval != appeal finality
award ceiling != obligation != outlay != cash
reported incident != population incidence
arrest != conviction != return to custody
eligibility != enrollment != payment != service receipt
underpayment error != overpayment error != fraud
referral != acceptance != service delivery != outcome
school membership != attendance != participation != attainment
raw response != scale score != plausible value != course grade
project award != protocol != study != output != impact
commitment != disbursement != expenditure != affected-person result
registration duplicate != deliberate diversion
```

## Evidence posture

The 59 sources were checked on 2026-08-25. They emphasize authoritative primary materials rather
than vendor pages or KPI lists. Important anchors include the
[OMB federal evaluation standards](https://www.whitehouse.gov/wp-content/uploads/2020/03/M-20-12.pdf),
[GAO Fraud Risk Framework](https://www.gao.gov/products/gao-15-593sp),
[FEMA National Risk Index methodology](https://www.fema.gov/sites/default/files/documents/fema_national-risk-index_technical-documentation.pdf),
[FBI UCR/NIBRS technical specifications](https://le.fbi.gov/informational-tools/ucr/ucr-technical-specifications-user-manuals-and-data-tools),
[BJS recidivism program](https://bjs.ojp.gov/recidivism-program),
[HUD HMIS standards](https://files.hudexchange.info/resources/documents/HMIS-Data-Standards.pdf),
[SNAP quality-control system](https://www.fns.usda.gov/snap/qc),
[CMS T-MSIS Data Guide](https://www.medicaid.gov/tmsis/dataguide),
[Common Education Data Standards](https://ceds.ed.gov/cedsdownloads.aspx),
[NAEP technical documentation](https://nces.ed.gov/nationsreportcard/tdw/default.aspx),
[IPEDS methodology](https://nces.ed.gov/ipeds/survey-components/ipeds-survey-methodology),
[ClinicalTrials.gov API data model](https://clinicaltrials.gov/data-api/about-api),
[DataCite metadata schema](https://datacite-metadata-schema.readthedocs.io/en/4.7/),
[IATI Standard](https://reference.iatistandard.org/en/iati-standard/),
[Core Humanitarian Standard](https://www.corehumanitarianstandard.org/), and the
[OCHA Data Responsibility Guidelines](https://centre.humdata.org/data-responsibility-guidelines-2025/).

Every case cites evidence records by stable ID. Evidence records state their authority scope and
material limitations. Source-system and shape records also cite the sources that justify their
objects or semantics.

## High-impact and sensitive-use boundaries

These are hard research constraints, not UI disclaimers:

1. **No automated adverse decisions.** No case may determine guilt, bail, sentence, supervision
   sanction, benefit denial or termination, child removal or placement, discipline, special-education
   placement, admission, aid, grade, employment, or access to essential humanitarian assistance.
2. **No predictive policing or person dangerousness.** Public-safety cases analyze system flow,
   measurement, geography, resources, safety and reporting processes. They do not predict who will
   offend or increase enforcement exposure based on a score.
3. **Support is separate from punishment.** Justice risk/needs analysis is limited to validated,
   supportive post-sentencing service use. A validation result never creates authorization for a
   punitive or liberty-restricting use.
4. **Error is not fraud.** Benefit accuracy treats underpayment and overpayment symmetrically. Fraud
   and diversion signals produce evidence packets for independent review, not findings.
5. **Protected attributes have a constrained purpose.** They may be retained in protected analytical
   tiers to measure disparity, measurement error, access, and remedy effectiveness. They may not be
   used to intensify surveillance, punishment, denial, or exclusion.
6. **Data minimization and tiering are required.** Education records, justice histories, health and
   benefit data, homelessness records, complaints, child-welfare data, and crisis microdata require
   purpose authority, least privilege, retention limits, correction, audit and disclosure review.
7. **Humanitarian data can cause physical harm.** Exact location, identity, vulnerability and
   complaint data must follow contextual sensitivity classification and information-sharing
   protocols. Technically de-identified data may still expose a small or displaced population.
8. **Community and due-process rights outrank optimization.** Notice, explanation, appeal,
   participation, consent where applicable, safeguarding, local leadership and do-no-harm constraints
   cannot be traded away for a higher objective score.
9. **Public defense scope is deliberately narrow.** Only public, unclassified business, asset,
   maintenance, reliability, inventory and sustainment analytics are represented. Intelligence,
   targeting, adversary analysis, operational missions, weapons employment and classified readiness
   are excluded.
10. **Tribal and Indigenous data require sovereign authority.** Federal or state reporting authority
    does not displace Tribal governance, negotiated definitions, collective rights, CARE-aligned
    review, or locally required custody and reuse conditions.

## Known gaps and non-claims

This pack does not claim extensional completion. Its closed record metamodel supports open-world
extension; a missing jurisdiction, method, source, population, modality, or decision becomes a typed
research gap rather than an invented mapping.

Material gaps remaining for future editions include:

- much deeper primary-source coverage for each individual subindustry and for jurisdictions outside
  the United States; the current pack has 59 authoritative sources across the family, not 25 sources
  independently re-verified for every subindustry;
- country-specific administrative law, public-record law, procurement, education, social-protection,
  justice and nonprofit-accounting variants;
- Tribal/Indigenous, territorial, rural, informal-service, refugee-host-government, and low-connectivity
  source systems authored with the relevant data-governance authorities;
- public libraries, archives, museums, elections, legislatures, diplomacy, immigration, tax
  administration, pensions, veterans services, parks, water/waste, and environmental regulation at
  the same case depth;
- qualitative evidence and affected-person/community-defined outcomes beyond the structured system
  interfaces represented here;
- independent effectiveness evidence for each proposed intervention and method in each local context;
- cross-industry adjudication of shared contexts such as grants, workforce, finance, casework,
  geospatial access, asset maintenance and program evaluation.

Public health delivery is intentionally not exhaustively decomposed here because it is a separate,
large clinical and population-health domain; only source contracts needed for Medicaid, research,
privacy, and emergency-service boundaries are included.

## Rebuild and verification

Regenerate the checked-in JSONL deterministically:

```bash
python3 research/domain_atlas/industries/public_education/build_corpus.py
```

The generator checks duplicate IDs, all evidence references, all case-to-source-system and
case-to-shape references, the minimum source floor, and per-sector case floors. The 219 generated
records also validate against
`research/domain_atlas/industries/schema/industry-research-record.schema.json` using JSON Schema
Draft 2020-12.

