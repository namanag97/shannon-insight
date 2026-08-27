#!/usr/bin/env python3
"""Build the evidence-backed quality, reconciliation and control semantic slice."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
REGISTRY = SEM.parents[1]
ATLAS = REGISTRY.parents[1]
UNIVERSE = ATLAS / "universes/quality_observability_reconciliation"
AS_OF = "2026-08-27"
PRODUCTS = {"product.data_quality_operations", "product.reconciliation_control_operations"}
AXES = [
    "semantic_object", "semantic_role", "identity_and_equality", "grain_and_cardinality",
    "state_and_change", "time", "order_and_topology", "partiality_and_uncertainty",
    "authority_and_trust", "effect_boundary", "representation", "composition_algebra",
    "compatibility_and_evolution", "resources_and_failure", "evidence_and_conformance",
    "privacy_security_safety",
]

# These are imports at exact semantic seams, not product ownership transfers. The list is kept
# deliberately smaller than the complete neighbor product graphs.
NEIGHBORS = {
    "library.data_contract.contract_identity",
    "library.data_contract.quality_service_obligations",
    "library.data_contract.party_purpose_roles",
    "library.data_contract.change_breach_case",
    "library.schema_registry.subject_identity",
    "library.schema_registry.version_registry",
    "library.schema_registry.compatibility",
    "library.master_data.domain_identity",
    "library.master_data.source_authority",
    "library.csp.identity.entity-resolution",
    "library.csp.identity.merge-split-ledger",
    "library.method_kernels.descriptive_statistics",
    "library.method_kernels.statistical_estimators",
    "library.method_kernels.inferential_tests_resampling",
    "library.method_kernels.anomaly_baseline",
    "library.method_kernels.anomaly_detectors",
    "library.method_kernels.change_point_detectors",
    "library.csp.quantity.quantity-core",
    "library.csp.quantity.ratio-rate",
    "library.csp.quantity.probability-core",
    "library.csp.quantity.partial-information",
    "library.csp.quantity.uncertainty-propagation",
    "library.lpe.lineage-core",
    "library.lpe.field-lineage",
    "library.lpe.provenance-assertion",
    "library.lpe.evidence-bundle",
    "library.lpe.runtime-receipt-core",
    "library.cbv.analytical_case_reducer",
    "library.cbv.decision_handoff_algebra",
    "library.csp.decision.judgment-port",
    "library.csp.decision.action-proposal",
    "library.csp.decision.effect-port",
    "library.telemetry.metric_stream",
    "library.telemetry.schema_conventions",
    "library.pipeline.data_cut_algebra",
    "library.smf.aggregation_algebra",
    "library.smf.bitemporal_algebra",
    "library.smf.missingness_algebra",
    "library.cbv.notification_dispatch",
}

VACANCIES = [
    ("library.qor.quality-subject-cut-identity", "Quality evidence needs a shared identity for subject occurrence, edition, population, data cut and evaluation scope."),
    ("library.qor.population-denominator-algebra", "Completeness, rates and fitness claims need explicit expected/observed populations and denominator laws."),
    ("library.qor.validation-outcome-algebra", "Pass, fail, skip, error, unknown and not-applicable outcomes must remain total and distinct."),
    ("library.qor.enforcement-disposition-algebra", "Block, warn, quarantine, permit and waive are policy dispositions, not assertion outcomes."),
    ("library.qor.truth-role-algebra", "Reconciliation requires source, accounting, control and other scoped truth roles without declaring a universal book of record."),
    ("library.qor.tolerant-match-algebra", "Exact equality, key match, allocation, aggregation, tolerance and probabilistic candidate match need separate operators and residuals."),
    ("library.qor.control-occurrence-receipt", "A bounded control occurrence needs definition edition, cuts, attempts, exceptions, reviewer and completion evidence."),
    ("library.qor.correction-authority-effect-contract", "Repair proposal, approval, source mutation, compensating entry and restatement need an explicit effect/authority boundary."),
    ("library.qor.certificate-status-revocation", "Quality attestations need issuer scope, validity, status resolution, revocation and supersession semantics."),
    ("library.qor.quality-cost-loss-profile", "Fitness and sampling choices need explicit harm, loss, inspection cost and residual-risk carriers."),
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def slug(value: str) -> str:
    return value.replace("_", "-").replace(".", "-").replace("/", "-")


def product_rows() -> list[dict[str, Any]]:
    return load_jsonl(SEM / "product_coordinate_binding_projection/subject-coordinate-binding-projections.jsonl")


def declared_product_libraries() -> set[str]:
    return {
        edge["concrete_library_ref"]
        for row in product_rows() if row["product_ref"] in PRODUCTS
        for edge in row["concrete_bindings"]
    }


LIBRARIES = sorted(declared_product_libraries() | NEIGHBORS)


def source_ref(source_id: str) -> str:
    assert source_id.startswith("qor.src.")
    return "source.quality." + source_id.removeprefix("qor.src.").replace("_", "-")


EXTRA_SOURCES = [
    {
        "source_id": "source.quality.wang-strong-beyond-accuracy",
        "title": "Beyond Accuracy: What Data Quality Means to Data Consumers",
        "publisher": "Journal of Management Information Systems",
        "publication_year": 1996,
        "source_kind": "original_research",
        "url": "https://doi.org/10.1080/07421222.1996.11518099",
        "supported_claim": "Consumer research separates intrinsic, contextual, representational and accessibility dimensions and makes fitness task-relative.",
        "authority_limit": "An exploratory consumer study does not define universal dimensions, thresholds, product ownership or current industry practice.",
    },
    {
        "source_id": "source.quality.holoclean",
        "title": "HoloClean: Holistic Data Repairs with Probabilistic Inference",
        "publisher": "Proceedings of the VLDB Endowment",
        "publication_year": 2017,
        "source_kind": "original_research",
        "url": "https://arxiv.org/abs/1702.00820",
        "supported_claim": "Probabilistic inference can combine constraints, external evidence and statistical signals to propose data repairs with disclosed uncertainty.",
        "authority_limit": "Reported repair accuracy is dataset/method scoped and cannot confer defect, correction, source-truth or effect authority.",
    },
    {
        "source_id": "source.quality.nadeef",
        "title": "NADEEF: A Generalized Data Cleaning System",
        "publisher": "Proceedings of the VLDB Endowment",
        "publication_year": 2013,
        "source_kind": "original_research",
        "url": "https://www.vldb.org/pvldb/vol6/p1218-tang.pdf",
        "supported_claim": "Rule specification, detection/repair execution, metadata and custodian interaction can be separated behind extensible interfaces.",
        "authority_limit": "A research system architecture does not prove universal rule expressiveness, repair correctness, authority or production qualification.",
    },
    {
        "source_id": "source.quality.ilyas-chu-data-cleaning",
        "title": "Data Cleaning",
        "publisher": "ACM Books",
        "publication_year": 2019,
        "source_kind": "research_monograph",
        "url": "https://www.holoclean.io/publications",
        "supported_claim": "Data cleaning includes heterogeneous detection, repair, deduplication, fusion and uncertainty problems rather than one generic operation.",
        "authority_limit": "A research synthesis does not select business rules, approve a repair, establish source truth or qualify an implementation.",
    },
]


def sources() -> list[dict[str, Any]]:
    rows = []
    for row in load_jsonl(UNIVERSE / "sources.jsonl"):
        assert row["primary_source"]
        rows.append({
            "source_id": source_ref(row["source_id"]),
            "source_registry_ref": row["source_id"],
            "title": row["title"],
            "publisher": row["publisher"],
            "year": row["publication_year"],
            "source_kind": row["source_kind"],
            "url": row["url"],
            "supported_claim": "; ".join(row["claims_supported"]),
            "authority_limit": row["limitations"],
            "primary_or_official": True,
            "status": "INDEPENDENTLY_REBOUNDED_PRIMARY_OR_OFFICIAL",
        })
    for row in EXTRA_SOURCES:
        rows.append({**{key: value for key, value in row.items() if key != "publication_year"},
                     "year": row["publication_year"], "source_registry_ref": None,
                     "primary_or_official": True, "status": "INDEPENDENTLY_RESEARCHED_PRIMARY"})
    return sorted(rows, key=lambda row: row["source_id"])


DEPENDENCIES = {
    "quality_requirement": [],
    "fitness_for_use": ["quality_requirement", "quality_dimension_metric"],
    "quality_dimension_metric": ["quality_requirement"],
    "contract_declaration": [],
    "contract_observation": ["contract_declaration"],
    "schema_conformance": ["contract_declaration"],
    "rule_specification": ["quality_requirement"],
    "validation_execution": ["rule_specification", "schema_conformance"],
    "test_case_management": ["rule_specification"],
    "data_profiling": [],
    "statistical_baseline": ["data_profiling"],
    "anomaly_detection": ["statistical_baseline"],
    "distribution_shift": ["statistical_baseline"],
    "change_point_detection": ["statistical_baseline"],
    "observability_instrumentation": ["validation_execution"],
    "signal_correlation": ["observability_instrumentation"],
    "quality_slo": ["quality_dimension_metric"],
    "quality_alerting": ["quality_slo", "signal_correlation"],
    "quality_incident_case": ["quality_alerting"],
    "defect_adjudication": ["quality_incident_case", "validation_execution"],
    "reconciliation_definition": [],
    "reconciliation_execution": ["reconciliation_definition"],
    "reconciliation_break": ["reconciliation_execution"],
    "correction_proposal": ["defect_adjudication", "reconciliation_break"],
    "correction_execution": ["correction_proposal"],
    "quarantine_release": ["defect_adjudication"],
    "certification_attestation": ["evidence_receipt"],
    "evidence_receipt": [],
    "waiver_exception": ["quality_policy"],
    "reference_master_alignment": [],
    "accounting_control_reconciliation": ["reconciliation_definition"],
    "duplicate_entity_resolution": [],
    "completeness_timeliness": ["quality_dimension_metric"],
    "sampling_measurement": ["quality_requirement"],
    "lineage_quality_impact": ["evidence_receipt"],
    "quality_policy": ["quality_requirement"],
    "remediation_verification": ["correction_execution", "validation_execution"],
}


def modules() -> list[dict[str, Any]]:
    result = []
    for row in load_jsonl(UNIVERSE / "bounded-context-candidates.jsonl"):
        suffix = row["context_id"].removeprefix("qor.context.")
        result.append({
            "module_id": f"module.quality.{suffix.replace('_', '-')}",
            "owned_question": row["purpose"],
            "formalism": "+".join(row["aggregate_candidates"]),
            "source_refs": sorted(source_ref(ref) for ref in row["source_refs"]),
            "dependency_refs": sorted(f"module.quality.{dep.replace('_', '-')}" for dep in DEPENDENCIES[suffix]),
            "authority_limit": "Imports preserve neighboring truth and effect authority; provider mechanisms and vertical policy do not become universal semantics.",
            "research_status": "EVIDENCE_BACKED_CANDIDATE_UNRATIFIED",
        })
    return sorted(result, key=lambda row: row["module_id"])


def laws() -> list[dict[str, Any]]:
    rows = []
    for row in load_jsonl(UNIVERSE / "semantic-distinctions.jsonl"):
        rows.append({
            "law_id": "law.quality." + row["distinction_id"].removeprefix("qor.distinction.").replace("_", "-"),
            "statement": row["non_collapse_law"],
            "status": "EVIDENCE_BACKED_CANDIDATE_UNRATIFIED",
            "canonical_gaps_closed": 0,
        })
    seen = {row["statement"] for row in rows}
    for context in load_jsonl(UNIVERSE / "bounded-context-candidates.jsonl"):
        suffix = context["context_id"].removeprefix("qor.context.")
        for index, statement in enumerate(context["sovereign_distinctions"], 1):
            normalized = statement.strip().rstrip(".") + "."
            if normalized.lower() in {value.lower() for value in seen}:
                continue
            seen.add(normalized)
            rows.append({"law_id": f"law.quality.{suffix.replace('_', '-')}.{index}",
                         "statement": normalized,
                         "status": "EVIDENCE_BACKED_CANDIDATE_UNRATIFIED", "canonical_gaps_closed": 0})
    rows.extend([
        {"law_id": "law.quality.result-vs-disposition", "statement": "Assertion outcome is not enforcement disposition; pass/fail/skip/error never implies permit/block/warn/quarantine/waive without policy.", "status": "EVIDENCE_BACKED_CANDIDATE_UNRATIFIED", "canonical_gaps_closed": 0},
        {"law_id": "law.quality.break-vs-defect", "statement": "A reconciliation break is not necessarily a data defect; lawful timing, allocation, recognition and representation differences remain possible.", "status": "EVIDENCE_BACKED_CANDIDATE_UNRATIFIED", "canonical_gaps_closed": 0},
        {"law_id": "law.quality.balance-vs-equality", "statement": "Balanced aggregates do not prove row-level equality, matching completeness or absence of offsetting errors.", "status": "EVIDENCE_BACKED_CANDIDATE_UNRATIFIED", "canonical_gaps_closed": 0},
        {"law_id": "law.quality.proposal-vs-correction", "statement": "A deterministic, heuristic, statistical, model or agent repair proposal is not an approved correction, source observation or mutation authority.", "status": "EVIDENCE_BACKED_CANDIDATE_UNRATIFIED", "canonical_gaps_closed": 0},
        {"law_id": "law.quality.certificate-vs-truth", "statement": "A certificate records a scoped issuer claim under named criteria; it is not measurement truth, universal fitness or proof of future conformance.", "status": "EVIDENCE_BACKED_CANDIDATE_UNRATIFIED", "canonical_gaps_closed": 0},
    ])
    return sorted(rows, key=lambda row: row["law_id"])


def methods() -> list[dict[str, Any]]:
    rows = []
    for row in load_jsonl(UNIVERSE / "typed-operations.jsonl"):
        rows.append({
            "method_type_id": "method.quality." + row["operation_id"].removeprefix("qor.operation.").replace("_", "-"),
            "name": row["name"],
            "method_group": row["owner_context"].removeprefix("qor.context."),
            "effect_class": row["effect_class"],
            "determinism": row["determinism"],
            "signature": row["signature"],
            "selection_law": "Select only with exact subject/cut/policy editions, satisfied preconditions, total refusal handling and an explicit effect port when effectful.",
            "source_refs": sorted(source_ref(ref) for ref in row["source_refs"]),
            "status": "METHOD_CANDIDATE_UNRATIFIED",
        })
    return sorted(rows, key=lambda row: row["method_type_id"])


EXPERT_ROWS = [
    ("richard-wang", "Richard Y. Wang", ["source.quality.wang-strong-beyond-accuracy"], ["Model quality from the consumer/task perspective, not only database validity.", "Keep dimensions and fitness policies contextual."], "The study is exploratory and not a universal metric catalog."),
    ("diane-strong", "Diane M. Strong", ["source.quality.wang-strong-beyond-accuracy"], ["Separate intrinsic, contextual, representational and accessibility concerns.", "Elicit needs from users before selecting measures."], "The dimensional framework does not select thresholds or product boundaries."),
    ("ihab-ilyas", "Ihab F. Ilyas", ["source.quality.nadeef", "source.quality.holoclean", "source.quality.ilyas-chu-data-cleaning"], ["Separate heterogeneous rule specification from detection and repair execution.", "Retain uncertainty and human/authority seams around repair."], "Research systems and monographs do not authorize production corrections."),
    ("xu-chu", "Xu Chu", ["source.quality.holoclean", "source.quality.ilyas-chu-data-cleaning"], ["Treat cleaning as multiple method families with different assumptions.", "Make candidate evidence and repair provenance first-class."], "Probabilistic repair results are corpus and model scoped."),
    ("theodoros-rekatsinas", "Theodoros Rekatsinas", ["source.quality.holoclean"], ["Combine constraints and statistical evidence without hiding uncertainty.", "Expose inference configuration and candidate alternatives."], "Inference confidence is not adjudication or source truth."),
    ("christopher-re", "Christopher Ré", ["source.quality.holoclean"], ["Compile heterogeneous evidence into explicit probabilistic programs.", "Separate scalable inference from authority and effects."], "One probabilistic formulation does not cover every quality defect."),
    ("felix-naumann", "Felix Naumann", [source_ref("qor.src.metanome")], ["Data profiling is a family of discovery problems, not one summary call.", "Candidate dependencies and constraints remain hypotheses until accepted."], "Profiling surveys do not define business truth or acceptance."),
    ("ziawasch-abedjan", "Ziawasch Abedjan", [source_ref("qor.src.metanome")], ["Keep profiling tasks, algorithms and discovery guarantees explicit.", "Expose completeness and approximation limits."], "Discovery evidence remains data/sample scoped."),
    ("thorsten-papenbrock", "Thorsten Papenbrock", [source_ref("qor.src.metanome")], ["Treat dependency discovery, inclusion dependencies and uniqueness as distinct kernels.", "Retain exact candidate evidence and counterexamples."], "A discovered dependency is not an approved contract."),
    ("sebastian-schelter", "Sebastian Schelter", [source_ref("qor.src.deequ-paper")], ["Compile declarative constraints into scalable aggregate verification.", "Reuse computed states while preserving analyzer identity and scope."], "Reported scalability and checks do not establish universal fitness."),
    ("eric-breck", "Eric Breck", [source_ref("qor.src.tfdv-paper")], ["Separate schema inference, anomaly detection and accepted schema evolution.", "Protect training/serving boundaries with explicit data validation."], "ML-data validation patterns do not define all enterprise quality semantics."),
    ("albert-bifet", "Albert Bifet", [source_ref("qor.src.adwin")], ["Make adaptive-window assumptions and confidence parameters explicit.", "Treat detector resets as state transitions."], "ADWIN detects bounded distributional change, not cause or defect."),
    ("arthur-gretton", "Arthur Gretton", [source_ref("qor.src.mmd")], ["Define the two populations, kernel, test statistic and calibration before claiming shift.", "Separate evidence against equality from operational impact."], "A two-sample test does not diagnose cause or select remediation."),
    ("ryan-adams", "Ryan Prescott Adams", [source_ref("qor.src.bocpd")], ["Represent run length, hazard assumptions and posterior alternatives explicitly.", "Keep online evidence distinct from retrospective truth."], "Posterior change probability depends on the chosen generative model."),
    ("sudipto-guha", "Sudipto Guha", [source_ref("qor.src.rrcf")], ["Use streaming anomaly methods with explicit state, score and explanation boundaries.", "Do not collapse anomaly score into defect verdict."], "Forest scores are detector-specific and not universally comparable."),
    ("w3c-dqv-group", "W3C Data Quality Vocabulary Working Group", [source_ref("qor.src.w3c-dqv")], ["Keep dimension, metric, measurement, policy, annotation and certificate distinct.", "Bind each measurement to the resource computed on."], "DQV explicitly does not define one ideal quality model."),
    ("iso-square", "ISO/IEC JTC 1/SC 7 SQuaRE community", [source_ref("qor.src.iso25012"), source_ref("qor.src.iso25024")], ["Separate quality characteristics from measurement procedures.", "Use editioned normative vocabulary inside its scope."], "ISO catalog pages do not supply industry thresholds or implementation conformance."),
    ("jcgm", "JCGM metrology community", [source_ref("qor.src.jcgm-vim"), source_ref("qor.src.jcgm-gum")], ["Separate measurand, indication, result, calibration and uncertainty.", "Propagate uncertainty through an explicit measurement model."], "Metrology uncertainty is not all sampling, model or business uncertainty."),
    ("openlineage", "OpenLineage specification community", [source_ref("qor.src.openlineage-dq-metrics"), source_ref("qor.src.openlineage-dq-assertions")], ["Attach measurements/assertions to exact dataset/run identities.", "Keep assertion success separate from configured severity."], "Facets transport evidence; they do not establish truth or complete lineage."),
    ("bcbs", "Basel Committee on Banking Supervision", [source_ref("qor.src.bcbs239")], ["Require explicit ownership, aggregation controls and reconciliation where models differ.", "Treat completeness, timeliness, accuracy and adaptability as governed obligations."], "Banking supervisory principles are not universal horizontal semantics or implementation proof."),
]


def experts() -> list[dict[str, Any]]:
    return [{"expert_id": f"expert.quality.{key}", "name": name, "source_refs": refs,
             "lessons_for_composable_platform": lessons, "authority_limit": limit,
             "status": "LEARNING_PROFILE_NOT_AUTHORITY"}
            for key, name, refs, lessons, limit in EXPERT_ROWS]


def innovations() -> list[dict[str, Any]]:
    rows = []
    for row in load_jsonl(UNIVERSE / "innovations.jsonl"):
        rows.append({"innovation_id": "innovation.quality." + row["innovation_id"].removeprefix("qor.innovation.").replace("_", "-"),
                     "year": row["year"], "summary": row["description"],
                     "source_refs": sorted(source_ref(ref) for ref in row["source_refs"]),
                     "authority_limit": row["limitation"], "ai_or_llm_dependency": False,
                     "status": "RECENT_MECHANISM_NOT_ADOPTION_OR_BOUNDARY_PROOF"})
    return sorted(rows, key=lambda row: row["innovation_id"])


AXIS_QUESTIONS = {
    "semantic_object": "Which requirement, metric, rule, observation, signal, case, break, proposal, receipt or control occurrence is this library allowed to own?",
    "semantic_role": "Which declarer, observer, evaluator, detector, reviewer, controller, issuer or effect-port role applies at each operation position?",
    "identity_and_equality": "Which subject/cut/run/break/receipt identities and exact, tolerant, probabilistic or policy equality relations apply?",
    "grain_and_cardinality": "What population, denominator, sample, grouping, match multiplicity and residual cardinality bind each claim?",
    "state_and_change": "Which declaration, evaluation, incident, break, correction, waiver, certificate and remediation transitions are legal?",
    "time": "Which event, observation, validity, recording, window, lateness, effective, expiry and review times apply?",
    "order_and_topology": "Which lineage, dependency, matching, causality-claim, case and control-order relations are preserved?",
    "partiality_and_uncertainty": "How are missing, late, invalid, skipped, errored, censored, sampled, approximate, ambiguous and uncertain outcomes represented?",
    "authority_and_trust": "Who may declare requirements, adjudicate defects/breaks, waive controls, approve corrections, issue/revoke certificates and release data?",
    "effect_boundary": "Which operations are pure findings/proposals and which request quarantine, mutation, restatement, notification, publication or release effects?",
    "representation": "Which rule, profile, assertion, receipt, case, attestation and reconciliation-plan editions are accepted and how are losses disclosed?",
    "composition_algebra": "How do rules, metrics, samples, signals, matches, tolerances, gates, waivers and controls compose without hidden precedence?",
    "compatibility_and_evolution": "Which declaration/rule/baseline/tolerance/policy changes preserve replay, and which require migration, parallel run or revalidation?",
    "resources_and_failure": "Which scan, sample, state, latency, privacy, retry and effect budgets apply, and what are total typed failures?",
    "evidence_and_conformance": "Which exact subject/cut/configuration/attempt/results/authority evidence supports each scoped claim and negative twin?",
    "privacy_security_safety": "Which purpose, minimization, sensitive-value, disclosure, retention, poisoning, abuse and unsafe-correction constraints apply?",
}


def binding_modules(library_ref: str) -> list[str]:
    suffix = library_ref.rsplit(".", 1)[-1].replace("-", "_").removesuffix("_kernel")
    module_ids = {row["module_id"] for row in modules()}
    direct = f"module.quality.{suffix.replace('_', '-')}"
    result = {direct} if direct in module_ids else set()
    rules = [
        (("data_contract", "schema_registry"), ["contract-declaration", "contract-observation", "schema-conformance"]),
        (("master_data", "entity-resolution", "merge-split"), ["reference-master-alignment", "duplicate-entity-resolution"]),
        (("descriptive_statistics", "statistical_estimators", "inferential_tests"), ["data-profiling", "sampling-measurement", "statistical-baseline"]),
        (("anomaly_baseline",), ["statistical-baseline"]),
        (("anomaly_detectors",), ["anomaly-detection"]),
        (("change_point_detectors",), ["change-point-detection"]),
        (("quantity", "ratio-rate", "probability", "partial-information", "uncertainty"), ["quality-dimension-metric", "sampling-measurement"]),
        (("lineage", "provenance", "evidence-bundle", "runtime-receipt"), ["lineage-quality-impact", "evidence-receipt"]),
        (("analytical_case",), ["quality-incident-case", "reconciliation-break"]),
        (("decision_handoff", "judgment-port"), ["defect-adjudication", "reconciliation-break"]),
        (("action-proposal", "effect-port"), ["correction-proposal", "correction-execution", "quarantine-release"]),
        (("metric_stream", "schema_conventions"), ["observability-instrumentation", "signal-correlation"]),
        (("data_cut",), ["validation-execution", "reconciliation-execution"]),
        (("aggregation_algebra",), ["quality-dimension-metric", "reconciliation-execution"]),
        (("bitemporal",), ["contract-observation", "completeness-timeliness", "reconciliation-definition"]),
        (("missingness",), ["completeness-timeliness", "validation-execution"]),
        (("notification_dispatch",), ["quality-alerting"]),
    ]
    for needles, adds in rules:
        if any(needle in library_ref for needle in needles):
            result.update(f"module.quality.{name}" for name in adds)
    assert result, library_ref
    return sorted(result)


def boundary_findings() -> list[dict[str, Any]]:
    direct = declared_product_libraries()
    rows = [
        {"finding_id": "finding.quality.product-split.v1", "library_refs": sorted(direct), "current_product_refs": sorted(PRODUCTS), "candidate_disposition": "RETAIN_TWO_PRODUCTS_QUALITY_OPERATIONS_AND_RECONCILIATION_CONTROL_OPERATIONS", "reason": "Quality evaluates exact cuts against purpose-scoped requirements; reconciliation compares identified populations under truth roles, matching, tolerance and materiality and manages breaks.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.quality.observability-capability.v1", "library_refs": sorted(ref for ref in direct if any(word in ref for word in ["observability", "signal_correlation", "quality_slo", "quality_alerting"])), "current_product_refs": ["product.data_quality_operations"], "candidate_disposition": "RETAIN_DATA_QUALITY_OBSERVABILITY_AS_COMPOSABLE_CAPABILITIES_NOT_A_THIRD_SEMANTIC_OWNER", "reason": "Instrumentation, correlation, SLO and alert state support quality operations; general telemetry, incident delivery and lineage remain imported owners. A commercial observability suite may compose these without absorbing their meanings.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.quality.data-contract-acl.v1", "library_refs": sorted(ref for ref in NEIGHBORS if ref.startswith("library.data_contract.") or ref.startswith("library.schema_registry.")), "current_product_refs": [], "candidate_disposition": "IMPORT_DECLARATIONS_AND_SCHEMA_EDITIONS_WITHOUT_REOWNING_CONTRACT_OR_SCHEMA_AUTHORITY", "reason": "Quality observes and evaluates declarations but cannot silently author or mutate them.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.quality.identity-acl.v1", "library_refs": sorted(ref for ref in NEIGHBORS if "master_data" in ref or "identity" in ref), "current_product_refs": [], "candidate_disposition": "IMPORT_MASTER_REFERENCE_AND_ENTITY_IDENTITY_WITHOUT_REOWNING_MERGE_SPLIT_OR_SOURCE_AUTHORITY", "reason": "Alignment and duplicate signals are evidence; mastered identity and merge/split decisions remain neighboring owners.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.quality.accounting-vertical.v1", "library_refs": [], "current_product_refs": ["product.reconciliation_control_operations"], "candidate_disposition": "ACCOUNTING_CONTROL_RECONCILIATION_IS_A_VERTICAL_PROFILE_NOT_UNIVERSAL_HORIZONTAL_TRUTH", "reason": "Operational, accounting and control truth roles, materiality and control completion are valuable but must be bound by industry/application packs.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.quality.repair-authority.v1", "library_refs": sorted(ref for ref in direct if "correction" in ref), "current_product_refs": sorted(PRODUCTS), "candidate_disposition": "REPAIR_METHODS_PRODUCE_PROPOSALS_WHILE_APPROVAL_AND_MUTATION_REQUIRE_EXPLICIT_AUTHORITY_AND_EFFECT_PORTS", "reason": "Deterministic, heuristic, statistical, model and agent methods may propose repairs but cannot make observations true or authorize effects.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.quality.certificate-seam.v1", "library_refs": ["library.qor.certification_attestation_kernel", "library.qor.evidence_receipt_kernel"], "current_product_refs": ["product.data_quality_operations"], "candidate_disposition": "CERTIFICATION_REMAINS_SCOPED_CLAIM_LIFECYCLE_NOT_TRUTH_OR_GENERAL_ASSURANCE_PRODUCT", "reason": "Issuer authority, criteria, subject digest, validity and revocation must remain explicit; independent assurance is a neighboring product.", "owner_decision": "UNRATIFIED"},
        {"finding_id": "finding.quality.decision-effect-seam.v1", "library_refs": sorted(ref for ref in NEIGHBORS if ref.startswith("library.csp.decision.") or ref.startswith("library.cbv.decision")), "current_product_refs": sorted(PRODUCTS), "candidate_disposition": "QUALITY_AND_RECONCILIATION_FINDINGS_STOP_BEFORE_BUSINESS_DECISION_AND_EFFECT_AUTHORITY", "reason": "Evidence, defect/break verdicts, proposals and control completion can be inputs to decisions; they do not authorize unrelated business effects.", "owner_decision": "UNRATIFIED"},
    ]
    rows.extend({"finding_id": f"finding.quality.vacancy.{slug(ref)}.v1", "library_refs": [],
                 "proposed_library_ref": ref, "current_product_refs": [],
                 "candidate_disposition": "NEW_LIBRARY_BOUNDARY_CANDIDATE_UNRATIFIED",
                 "reason": reason, "owner_decision": "UNRATIFIED"} for ref, reason in VACANCIES)
    return rows


def build() -> dict[str, Any]:
    source_rows, module_rows, law_rows = sources(), modules(), laws()
    method_rows, expert_rows, innovation_rows = methods(), experts(), innovations()
    source_ids = {row["source_id"] for row in source_rows}
    assert all(set(row["source_refs"]) <= source_ids for row in module_rows + method_rows + expert_rows + innovation_rows)
    contributions = {row["library_id"]: row for row in load_jsonl(REGISTRY / "library-contributions.jsonl")}
    assert set(LIBRARIES) <= contributions.keys()
    coord = {row["library_ref"]: row for row in load_jsonl(SEM / "library_coordinate_binding_projection/library-coordinate-binding-dockets.jsonl")}
    exact = {row["library_ref"]: row for row in load_jsonl(SEM / "p5_exact_contract_adjudication/exact-contract-dockets.jsonl")}
    consumers = {ref: set() for ref in LIBRARIES}
    subjects = {ref: set() for ref in LIBRARIES}
    for row in product_rows():
        for edge in row["concrete_bindings"]:
            ref = edge["concrete_library_ref"]
            if ref in consumers:
                consumers[ref].add(row["product_ref"])
                subjects[ref].add(row["subject_ref"])
    targeted = {(row["axis"], row["library_ref"]): row for row in load_jsonl(SEM / "targeted_evidence_cluster_adjudication/member-adjudication-occurrences.jsonl")}
    modules_by_id = {row["module_id"]: row for row in module_rows}
    direct = declared_product_libraries()
    bindings, axes = [], []
    for ref in LIBRARIES:
        module_refs = binding_modules(ref)
        evidence_refs = sorted({source for module_id in module_refs for source in modules_by_id[module_id]["source_refs"]})
        exact_row, coord_row = exact.get(ref), coord.get(ref)
        routed = bool(exact_row and coord_row)
        bindings.append({
            "record_kind": "quality_reconciliation_control_library_semantic_binding_candidate",
            "binding_id": f"binding.quality-semantic-slice.{slug(ref)}.v1",
            "library_ref": ref,
            "library_name": contributions[ref]["name"],
            "semantic_module_refs": module_refs,
            "evidence_refs": evidence_refs,
            "exact_contract_docket_ref": exact_row["docket_id"] if exact_row else None,
            "coordinate_binding_docket_ref": coord_row["binding_docket_id"] if coord_row else None,
            "downstream_contract_route": "ROUTED" if routed else "MISSING_P5_AND_COORDINATE_DOCKET_TYPED_VACANCY",
            "downstream_subject_refs": sorted(subjects[ref]),
            "downstream_product_refs": sorted(consumers[ref]),
            "boundary_disposition_candidate": "RETAIN_DECLARED_PRODUCT_DEPENDENCY_WITH_NARROW_OWNER" if ref in direct else "RETAIN_FORMALISM_OR_ACL_NEIGHBOR_WITH_EXPLICIT_OWNER_SEAM",
            "compiler_binding": "REFUSED",
            "refusal_reasons": ([] if routed else ["DOWNSTREAM_CONTRACT_ROUTE_MISSING"]) + ["OWNER_RATIFICATION_MISSING", "MEMBER_AXIS_APPLICABILITY_UNRATIFIED", "EXACT_CONTRACT_UNSELECTED", "IMPLEMENTATIONS_UNQUALIFIED"],
            "completion_claim": False,
        })
        for axis in AXES:
            target = targeted.get((axis, ref))
            axes.append({
                "record_kind": "quality_reconciliation_control_library_axis_decision_candidate",
                "decision_candidate_id": f"decision-candidate.quality-axis.{slug(ref)}.{axis.replace('_', '-')}.v1",
                "library_ref": ref, "axis": axis, "semantic_module_refs": module_refs,
                "coordinate_question": AXIS_QUESTIONS[axis],
                "applicability_candidate": "REQUIRED_EXPLICIT_PROFILE",
                "evidence_refs": evidence_refs,
                "targeted_member_adjudication_occurrence_ref": target["occurrence_id"] if target else None,
                "coordinate_answers": [], "member_applicability": "PROPOSED_OWNER_REVIEW_REQUIRED",
                "owner_decision": "UNRATIFIED", "status": "EVIDENCE_BACKED_DECISION_QUESTION_NOT_ANSWER",
                "canonical_gaps_closed": 0, "completion_claim": False,
            })
    findings = boundary_findings()
    context = {
        "record_kind": "bounded_context_candidate",
        "context_id": "context.quality-reconciliation-controls-semantic-slice.v1",
        "as_of": AS_OF,
        "vision": "How can purpose-scoped data quality be measured and governed, and identified populations be reconciled under explicit truth roles and controls, without collapsing declarations, observations, signals, defects, breaks, repairs, attestations or business effects?",
        "inside": ["quality requirements, dimensions, metrics, rules, validation, profiling and fitness", "baselines, anomaly/shift/change signals and quality observability", "quality cases, defect adjudication, quarantine, waiver, remediation and certification", "reconciliation definitions, runs, matching/tolerance, breaks and bounded control completion", "quality/reconciliation evidence and correction proposals"],
        "outside": ["data-contract and schema declaration authority", "master/reference identity and entity merge/split authority", "general telemetry, lineage and notification delivery ownership", "industry accounting policy and book-of-record selection", "source mutation, restatement and unrelated business effect authority", "independent assurance and vertical acceptance"],
        "neighbors": [{"context_ref": "product.data_contract_registry", "relationship": "conformist_at_published_language"}, {"context_ref": "product.schema_registry", "relationship": "conformist_at_published_language"}, {"context_ref": "product.master_data_governance", "relationship": "anti_corruption_layer"}, {"context_ref": "product.reference_data_governance", "relationship": "anti_corruption_layer"}, {"context_ref": "context.statistical-inference-semantic-slice", "relationship": "conditional_customer_supplier"}, {"context_ref": "context.signal-condition-semantic-slice", "relationship": "conditional_customer_supplier"}, {"context_ref": "product.lineage_provenance", "relationship": "open_host_service"}, {"context_ref": "context.decision-effect-authority", "relationship": "anti_corruption_layer"}],
        "published_language": ["QualityRequirementEdition", "QualityMetricEdition", "RuleEdition", "EvaluationScope", "ValidationRun", "QualityMeasurement", "QualitySignal", "QualityCase", "DefectVerdict", "ReconciliationDefinitionEdition", "ReconciliationRun", "ReconciliationBreak", "CorrectionProposal", "Waiver", "QualityEvidenceReceipt", "QualityAttestation", "ControlOccurrenceReceipt"],
        "ratification": "WITHHELD", "completion_claim": False,
    }
    summary = {
        "program_id": "program.quality-reconciliation-controls-semantic-slice.v1", "as_of": AS_OF,
        "primary_or_official_sources": len(source_rows), "semantic_modules": len(module_rows),
        "non_collapse_laws": len(law_rows), "method_types": len(method_rows),
        "expert_learning_profiles": len(expert_rows), "recent_non_llm_innovations": len(innovation_rows),
        "bound_libraries": len(bindings), "declared_product_libraries": len(direct),
        "formalism_and_acl_neighbor_libraries": len(NEIGHBORS), "candidate_new_library_vacancies": len(VACANCIES),
        "libraries_without_declared_product_consumer": sum(not consumers[ref] for ref in LIBRARIES),
        "missing_downstream_contract_routes": sum(row["downstream_contract_route"].startswith("MISSING") for row in bindings),
        "library_axis_decision_candidates": len(axes), "product_capability_boundary_findings": len(findings),
        "owner_decisions": 0, "exact_contracts_selected": 0, "qualified_implementations": 0,
        "canonical_gaps_closed": 0, "completion_claim": False,
    }
    return {"context": context, "sources": source_rows, "modules": module_rows, "laws": law_rows,
            "methods": method_rows, "experts": expert_rows, "innovations": innovation_rows,
            "libraries": bindings, "axes": axes, "findings": findings, "summary": summary}


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "bounded-context.json": json.dumps(built["context"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "primary-sources.jsonl": "".join(canonical(row) + "\n" for row in built["sources"]),
        "semantic-modules.jsonl": "".join(canonical(row) + "\n" for row in built["modules"]),
        "non-collapse-laws.jsonl": "".join(canonical(row) + "\n" for row in built["laws"]),
        "quality-control-method-taxonomy.jsonl": "".join(canonical(row) + "\n" for row in built["methods"]),
        "expert-learning-profiles.jsonl": "".join(canonical(row) + "\n" for row in built["experts"]),
        "innovation-records.jsonl": "".join(canonical(row) + "\n" for row in built["innovations"]),
        "library-semantic-bindings.jsonl": "".join(canonical(row) + "\n" for row in built["libraries"]),
        "library-axis-decision-candidates.jsonl": "".join(canonical(row) + "\n" for row in built["axes"]),
        "product-capability-boundary-findings.jsonl": "".join(canonical(row) + "\n" for row in built["findings"]),
        "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    claims = {name: {"bytes": len(value.encode()), "sha256": hashlib.sha256(value.encode()).hexdigest()} for name, value in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.quality-reconciliation-controls-semantic-slice.v1", "as_of": AS_OF, "files": claims, "completion_claim": False}, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    for name, value in outputs().items():
        (HERE / name).write_text(value)
    summary = build()["summary"]
    print(f"BUILD PASS quality/reconciliation/controls slice: {summary['semantic_modules']} modules, {summary['method_types']} methods, {summary['bound_libraries']} libraries and {summary['library_axis_decision_candidates']} unresolved axis decisions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
