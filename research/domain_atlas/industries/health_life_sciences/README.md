# Healthcare and life-sciences analytical-need atlas

This is a **pre-product, vendor-neutral research pack**. Its unit is a decision, diagnostic,
investigation or controlled workflow—not a KPI and not a dashboard. It decomposes what must be
understood before product boundaries are drawn across care delivery, payment, public health,
research, regulated manufacturing, diagnostics, devices, genomics and digital health.

Generated edition-1 coverage:

| Artifact | Count | Meaning |
|---|---:|---|
| `analytics-cases.jsonl` | 155 | Decision/action cases with question, grain, methods, operations, uncertainty, authority and evidence |
| `source-systems.jsonl` | 30 | Vendor-neutral source classes with objects, change modes, time/finality, authority and hazards |
| `data-shapes.jsonl` | 31 | Domain shapes preserving modality, grain, identity, time, uncertainty, change and provenance |
| `sources.jsonl` | 48 | Internet-verified primary standards, regulators and official implementations |
| Subindustries | 21 | Every subindustry listed below has at least one encoded case |
| Analytical modes | 29 | Operational through causal, safety, optimization, simulation and regulatory analysis |

All analytical cases set `llm_dependency` to `none`. Classical statistics, numerical methods,
optimization, process mining and governed statistical learning are allowed. No case needs prompt,
RAG, generative or agent-memory semantics.

## Subindustry coverage

1. Acute-care hospitals and health systems
2. Primary, specialty, ambulatory and surgical care
3. Emergency departments, urgent care and EMS
4. Behavioral health and substance-use care
5. Rehabilitation, skilled nursing, long-term care, home health and hospice
6. Dental and oral health
7. Commercial health insurance
8. Medicare, Medicaid and public purchasers
9. ACOs and value-based care entities
10. Retail, specialty and health-system pharmacy
11. Pharmacy benefit management
12. Public-health agencies and programmes
13. Pharmaceutical discovery and development
14. Biotechnology, translational and omics research
15. Sponsors, CROs, trial sites and decentralized trials
16. Pharmaceutical and biopharmaceutical manufacturing
17. Medical devices, IVDs and combination products
18. Clinical laboratories, pathology and imaging diagnostics
19. Genomics and precision medicine
20. Blood, tissue, cell and organ services
21. Digital health, remote monitoring and wearables

The cases include deterioration escalation, care-path conformance, systems RCA, cause-contribution
ranking, infection/outbreak investigation, queues and bottlenecks, capacity and workforce control,
causal intervention evaluation, survival/competing-risk analysis, claims and diagnosis
reconciliation, payment-integrity audit, network adequacy, prior-authorization flow, health-economic
decision analysis, trial quality-by-design and centralized monitoring, endpoint traceability,
pharmacovigilance, continued process verification, deviation/CAPA, reliability, recall,
experimental design, dose-response, omics, variant interpretation and regulated release evidence.

Bare acronyms are not semantic identities. In particular, `RCA` is encoded as systems event
investigation with competing hypotheses. `CCR` is ambiguous across healthcare; this pack uses the
explicit `cause_contribution_ranking` mode and will not compile bare `CCR` without a context owner.

## Evidence posture

The 48 sources were located and inspected on 2026-08-25. They are issued by standards bodies,
regulators or official implementers including HL7, DICOM/NEMA, ASTP/ONC, LOINC/Regenstrief,
SNOMED International, NLM, CMS/Medicaid, CDC, AHRQ, the Joint Commission, WHO, FDA, CDISC, ICH,
EMA, NIH and NCBI. Each source record states what it supports, its authority scope and its
limitations. Examples include:

- HL7 FHIR and Bulk Data for clinical/administrative resource and population-export semantics;
- DICOM for imaging object and exchange semantics;
- CMS claims, BCDA/CCLF, RADV, prior-authorization, MSSP, T-MSIS and CLIA sources;
- CDC NHSN, NNDSS and public-health data-modernization sources;
- FDA study-data, risk-based monitoring, real-world evidence, QMSR, MAUDE, UDI, DSCSA, PAT,
  process-validation and Part 11 sources;
- CDISC, ICH E6(R3), EMA CTIS and EMA pharmacovigilance/RWD/DARWIN EU sources; and
- NIH genomic-data-sharing, NCBI SRA, HL7 Genomics, LOINC, SNOMED CT and RxNorm sources.

`sourced_candidate` does **not** mean that a regulator directly prescribed the composed analytics.
Primary sources establish workflow, data, quality, safety or authority facts. Each analytical
composition still requires independent clinical/domain, statistical, privacy, safety, human-factors
and regulatory review for its intended use.

## Source and shape boundaries

The pack deliberately preserves false twins:

```text
order != dispense != administration
claim != clinical event
surveillance case != bedside diagnosis
signal != causal adverse reaction
device report count != incidence
raw read != called variant != clinical interpretation
trial CRF value != analysis endpoint
process sensor signal != quality-unit batch disposition
prediction != diagnosis, denial, treatment, allocation or product release
```

Clinical/effective time, documentation time, source-finality time and analytical availability time
remain separate. Corrections append versions. Patient, participant, sample, device, batch, claim,
site and package identities retain their assigning authorities and are never joined by value alone.

## Known incompleteness

This is an open-world atlas, not a claim that 155 cases enumerate every future need. The
machine-readable `coverage-gaps.json` records ten material gaps, including jurisdiction breadth,
specialty/disease depth, veterinary/One Health, interface versions, method certification,
terminology licensing, global privacy, prospective outcome evidence and standard conflicts.

The user-requested stronger bar of **25 primary sources per subindustry** is explicitly open. This
edition has 48 verified primary sources for the family, not 525 distinct sources (21 × 25). Closing
that gap requires a separate evidence programme with contradiction mapping and independent review;
the corpus does not disguise family-level evidence as subindustry-level completion.

## Rebuild and verify

From the repository root:

```bash
python3 research/domain_atlas/industries/health_life_sciences/build_pack.py
python3 research/domain_atlas/industries/health_life_sciences/validate_pack.py
```

The validator uses `jsonschema` when installed and a dependency-free contract validator otherwise.
It checks the shared industry schema, identifiers, all references, manifest counts,
primary-source minimum and diversity, non-LLM dependency, all 21 subindustries, required analytical
modes, and that every source-system/data-shape record is exercised by at least one analytical case.

These records remain research candidates until cross-industry deduplication, DDD ownership
adjudication, contradiction review and intended-use validation.
