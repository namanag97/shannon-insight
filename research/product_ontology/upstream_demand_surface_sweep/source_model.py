"""Evidence-bounded upstream demand-surface delta, 2026-08-27."""

SOURCES = [
    ("source.upstream.3gpp-nwdaf", "3GPP TS 23.288 / ETSI TS 123 288", "3GPP/ETSI", "https://www.etsi.org/deliver/etsi_ts/123200_123299/123288/18.11.00_60/ts_123288v181100p.pdf", "NWDAF exposes request/subscription analytics services to consumers; analytics output is not consumer application logic or control authority."),
    ("source.upstream.iso-21508-2026", "ISO 21508:2026 Earned value management", "ISO", "https://www.iso.org/standard/87899.html", "EVM integrates cost, schedule and scope across public/private organizations of any size, sector, project, programme or portfolio."),
    ("source.upstream.primavera", "Oracle Primavera Cloud Schedule Management", "Oracle", "https://docs.oracle.com/cd/E80480_01/English/user_guides/schedule_management_user_guide/primavera_schedule_management_user.pdf", "Primavera operates schedules, baselines, contracts, potential change orders, costs, payment applications and approvals as distinct state."),
    ("source.upstream.semi-e134", "SEMI E134-1225 Data Collection Management", "SEMI", "https://store-us.semi.org/products/e13400-semi-e134-specification-for-data-collection-management", "Named data-collection plans own event/exception/trace selection, state-machine execution, on-demand acquisition, output and equipment-performance constraints."),
    ("source.upstream.semi-e190", "SEMI E190-1124 Equipment Data Publication", "SEMI", "https://store-us.semi.org/products/e19000-semi-e190-specification-for-equipment-data-publication-edp", "Equipment-data categories and shareable/nonshareable access concepts are explicit and supplier/user access is negotiated."),
    ("source.upstream.asam-ods", "ASAM ODS 6.2.1", "ASAM", "https://www.asam.net/standards/detail/ods/", "Test-data management covers test systems, measurement devices, measured/calculated data, calibration, instrumentation and testing workflows."),
    ("source.upstream.sec-edgar", "SEC EDGAR filing technical specifications and manual", "U.S. SEC", "https://www.sec.gov/submit-filings/technical-specifications", "Submission types bind form-specific taxonomy/schema editions and validation; submissions receive acceptance or suspension outcomes."),
    ("source.upstream.odk", "ODK form audit and submission management", "ODK", "https://docs.getodk.org/central-api-submission-management/", "Forms, submissions and server audit logs retain distinct identity and lifecycle."),
    ("source.upstream.fhir-specimen", "HL7 FHIR R5 Specimen", "HL7", "https://hl7.org/fhir/specimen.html", "Specimens own collection, origin, processing, condition, parentage, status and container concerns independently of observations and reports."),
    ("source.upstream.fhir-diagnostic", "HL7 FHIR R5 DiagnosticReport", "HL7", "https://hl7.org/fhir/diagnosticreport.html", "Reports bind specimens and observations, have final/amended/retracted lifecycle, and remain distinct from individual results."),
    ("source.upstream.stix-2-1", "STIX 2.1", "OASIS", "https://docs.oasis-open.org/cti/stix/v2.1/errata01/stix-v2.1-errata01.pdf", "Observed Data records what was seen; a Sighting is a distinct intelligence assertion about what the observation implies."),
    ("source.upstream.edrm-2", "EDRM 2.0", "EDRM", "https://edrm.net/edrm-projects/edrm-2-0/", "Evidence production spans identification, preservation, collection, processing, review, analysis, production, presentation and disposition."),
    ("source.upstream.energistics", "Energistics WITSML/RESQML/PRODML architecture", "Energistics", "https://energistics.org/witsml-developers-users", "Well/drilling, earth/reservoir and production models are separate domain standards sharing a common technical architecture and transfer protocol."),
    ("source.upstream.gs1-traceability", "GS1 Global Traceability and EPCIS", "GS1", "https://ref.gs1.org/standards/global-traceability/2.0.0/", "Traceable-object identity, critical tracking events, transformations, aggregation and key data elements are independently represented across parties."),
    ("source.upstream.iab-ads", "IAB Tech Lab ads.txt and programmatic provenance", "IAB Tech Lab", "https://iabtechlab.com/ads.txt/", "Publisher inventory authorization and seller-chain transparency are separate from auction, exposure and conversion state."),
    ("source.upstream.acord-pc", "ACORD Property & Casualty Data Standards", "ACORD", "https://www-dev.acord.org/standards-architecture/acord-data-standards/Property_Casualty_Data_Standards", "Messages and transaction sequences support insurance processes but do not themselves become policy, coverage, claim or payment business state."),
]

DEMAND_SURFACES = [
    ("authoritative-declarations", ["regulatory_filing", "industry_message", "certificate", "submission_package", "plan_order_authorization"]),
    ("acquisition-artifacts", ["collection_plan", "instrument", "measurement_campaign", "observation", "sample", "media_signal_document", "telemetry_subscription"]),
    ("operated-state", ["case", "order_trade_claim_shipment", "experiment_campaign", "facility_asset", "engineering_model_twin"]),
    ("analytical-objects", ["question", "population_cohort", "feature_metric", "method_run", "result_uncertainty", "finding_comparison"]),
    ("decision-chain", ["finding", "proposal", "decision", "authorization", "effect", "receipt", "review_reversal"]),
    ("evidence-chain", ["source", "occurrence", "admitted_value", "derived_result", "assertion", "evidence", "verification", "appraisal"]),
    ("time-and-grain", ["identity", "occurrence", "valid_time", "observation_time", "processing_time", "publication_time", "revision_vintage", "as_of_cut"]),
    ("cross-organization-exchange", ["sender", "receiver", "authority", "contract", "schema_edition", "acknowledgement", "custody", "provenance", "exit"]),
]

UNIVERSAL_LAWS = [
    ("analytics-service-not-application-or-control", "analytics service != application logic != control effect", ["source.upstream.3gpp-nwdaf"]),
    ("observation-not-assertion", "observation != interpreted assertion", ["source.upstream.stix-2-1", "source.upstream.fhir-diagnostic"]),
    ("message-not-business-state", "process message != business aggregate state", ["source.upstream.acord-pc"]),
    ("source-not-evidence-production", "source document != collected evidence occurrence != processed review derivative != responsive assertion != production artifact", ["source.upstream.edrm-2"]),
    ("measurement-not-engineering-model", "measurement != well model != reservoir interpretation != simulation model != production observation", ["source.upstream.energistics"]),
    ("traceability-not-inventory", "master item != physical traceable instance != logistics event != custody != genealogy transformation != inventory position", ["source.upstream.gs1-traceability"]),
    ("test-not-laboratory-sample", "engineering test run != laboratory specimen lifecycle", ["source.upstream.asam-ods", "source.upstream.fhir-specimen"]),
    ("filing-not-report", "regulatory filing package != analytical report != submission attempt != regulator acknowledgement", ["source.upstream.sec-edgar"]),
    ("instrument-not-response", "collection instrument edition != deployment != response occurrence != admitted answer", ["source.upstream.odk"]),
    ("policy-not-provisioning", "access policy decision != entitlement issuance != provisioning effect != access-use receipt", ["source.upstream.semi-e190"]),
    ("project-plan-not-authorized-baseline", "planning alternative != authorized delivery baseline != progress observation != forecast-at-completion != approved change", ["source.upstream.iso-21508-2026", "source.upstream.primavera"]),
    ("inventory-not-ad-event", "publisher inventory != auction opportunity != bid != winning bid != impression != conversion", ["source.upstream.iab-ads"]),
]

BOUNDARY_HYPOTHESES = [
    ("project-portfolio-controls", "Project & Portfolio Controls", "PROMOTE_STRONG_HORIZONTAL_PRODUCT", "Owns authorized delivery baselines, schedule/cost/progress control, changes and performance evidence; remains separate from choosing future plans.", ["source.upstream.iso-21508-2026", "source.upstream.primavera"]),
    ("test-measurement-data-operations", "Test & Measurement Data Operations", "PROMOTE_PRESUMPTIVE_HORIZONTAL_PRODUCT", "Owns test-system configuration, unit under test, test plan/run, measurement channels, calibration context and evidence.", ["source.upstream.semi-e134", "source.upstream.asam-ods"]),
    ("regulatory-filing-submission-operations", "Regulatory Filing & Submission Operations", "PROMOTE_PRESUMPTIVE_HORIZONTAL_PRODUCT", "Owns filing packages, rule/taxonomy editions, validation, attempts, acknowledgements and correction/amendment.", ["source.upstream.sec-edgar"]),
    ("structured-collection-instrument-operations", "Structured Data Collection & Instrument Operations", "PROMOTE_PRESUMPTIVE_HORIZONTAL_PRODUCT", "Owns instrument/question editions, control flow, deployment, response occurrences, audit, validation and offline synchronization.", ["source.upstream.odk"]),
    ("laboratory-sample-operations", "Laboratory Sample Operations", "PROMOTE_PRESUMPTIVE_SEPARATE_PRODUCT", "Owns specimen/sample identity, collection, custody, preparation, analytical method binding, result review and release; imports measurement libraries.", ["source.upstream.fhir-specimen", "source.upstream.fhir-diagnostic"]),
    ("engineering-model-digital-twin-operations", "Engineering Model & Digital Twin Operations", "CONTINUE_CROSS_VERTICAL_FALSIFICATION", "Strong independent model lifecycle evidence exists, but construction/BIM, reservoir, manufacturing and infrastructure replacement tests remain required.", ["source.upstream.energistics"]),
    ("traceability-genealogy-operations", "Traceability & Genealogy Operations", "PROMOTE_PRESUMPTIVE_HORIZONTAL_PRODUCT", "Owns traceable-object occurrences, custody/event history, transformations, genealogy corrections and cross-party trace evidence; not ETA analytics.", ["source.upstream.gs1-traceability"]),
    ("data-access-entitlement-provisioning", "Data Access Entitlement & Provisioning", "SPLIT_FROM_POLICY_RESEARCH_REQUIRED", "Data-use policy decides; a separate lifecycle may issue/revoke entitlements and execute provisioning with receipts.", ["source.upstream.semi-e190"]),
    ("analytics-subscription-delivery", "Analytics Subscription & Delivery", "RETAIN_AS_EXACT_LIBRARY_SEAM_NOT_PRODUCT", "NWDAF supports a reusable request/subscription/delivery/feedback contract but not yet a separately adopted product lifecycle.", ["source.upstream.3gpp-nwdaf"]),
    ("ediscovery", "eDiscovery", "REHOME_INTO_EXISTING_PRODUCT_GRAPH", "Use the evidence-production lifecycle to deepen Case Investigation, Assurance, Document Review and Dataset Curation rather than make a legal-industry product horizontal.", ["source.upstream.edrm-2"]),
]

CONTRACTS = [
    "acquisition-plan", "acquisition-run-attempt", "acquisition-output", "acquisition-termination-refusal",
    "analytics-subscription", "analytics-delivery", "analytics-feedback", "analytics-accuracy-assessment",
    "filing-package", "filing-rule-taxonomy-edition", "filing-validation", "submission-attempt", "regulator-acknowledgement", "filing-correction-amendment",
    "instrument-definition-edition", "instrument-deployment", "response-occurrence", "response-audit", "offline-sync-reconciliation",
    "test-system-configuration", "unit-or-specimen-under-test", "test-plan", "test-run", "measurement-channel-result", "calibration-context", "test-evidence-publication",
    "specimen-identity", "specimen-collection-custody", "specimen-processing", "analytical-method-binding", "laboratory-result-release",
    "preservation-directive", "collected-evidence-occurrence", "processing-derivation", "review-coding", "privilege-assertion", "production-set", "redaction-decision", "production-receipt",
    "traceable-object-occurrence", "critical-tracking-event", "genealogy-transformation", "custody-transfer", "trace-correction",
    "access-entitlement", "entitlement-revocation", "provisioning-effect", "access-use-receipt",
    "authorized-delivery-baseline", "progress-status-cut", "project-change-request", "forecast-at-completion", "earned-value-assessment",
]

VERTICAL_PACKS = [
    ("ad-tech", ["auction_request", "bid", "deal", "seller_authorization", "impression", "exposure", "conversion", "attribution_claim", "incremental_effect_estimate", "activation_receipt"]),
    ("insurance", ["policy", "exposure_unit", "insured_object", "peril", "coverage", "claim", "claim_feature", "reserve_development", "catastrophe_event", "payment", "jurisdiction"]),
    ("genomics-clinical", ["phenotype_case", "variant_representation", "repository_access", "workflow_execution", "data_use_authorization", "qc_metric"]),
    ("semiconductor", ["equipment_control", "equipment_data_acquisition", "collection_plan", "equipment_data_entitlement"]),
    ("oil-gas", ["well_drilling_measurement", "earth_reservoir_model", "simulation_model", "production_observation", "transfer_protocol"]),
]
