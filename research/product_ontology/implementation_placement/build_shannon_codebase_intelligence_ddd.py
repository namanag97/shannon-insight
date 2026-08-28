#!/usr/bin/env python3
"""Build the candidate DDD for the checked-in codebase-intelligence application."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PLACEMENT = HERE / "shannon-python-placement.json"
OUTPUT = HERE / "shannon-codebase-intelligence-ddd.json"
SUMMARY = HERE / "shannon-codebase-intelligence-ddd-summary.json"

PRODUCT_ID = "application_product.software_engineering.codebase_intelligence"


def digest(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def build_model(placement_digest: str) -> dict[str, Any]:
    bounded_contexts = [
        {
            "context_id": "ctx.codebase_intelligence.repository_intake",
            "name": "Repository Intake and Observation Cut",
            "sovereign_responsibility": "Admit a bounded repository/source-history scope and issue an immutable observation-cut identity without modifying the source.",
            "owned_artifacts": ["AnalysisMandate", "RepositoryLocator", "RepositoryObservationCut", "AdmissionRefusal"],
            "negative_charter": ["does not own source repository content", "does not own universal source-system or connector semantics", "does not parse or analyze admitted content"],
        },
        {
            "context_id": "ctx.codebase_intelligence.program_observation",
            "name": "Program Observation and Identity",
            "sovereign_responsibility": "Own stable code-file identities and syntax observations for the admitted cut.",
            "owned_artifacts": ["CodeFileIdentity", "SyntaxObservation", "ImportObservation", "DefinitionObservation"],
            "negative_charter": ["does not own language-standard authority", "does not infer diagnostic findings", "does not equate parser success with semantic correctness"],
        },
        {
            "context_id": "ctx.codebase_intelligence.relation_model",
            "name": "Structural and Historical Relation Model",
            "sovereign_responsibility": "Construct typed, evidence-linked relations among admitted software artifacts.",
            "owned_artifacts": ["CodeRelation", "DependencyGraph", "CochangeRelation", "IdentityHistory"],
            "negative_charter": ["does not own source observations", "does not publish final findings", "does not treat correlation as causation"],
        },
        {
            "context_id": "ctx.codebase_intelligence.analytical_methods",
            "name": "Codebase Analytical Methods",
            "sovereign_responsibility": "Execute bounded graph, temporal, statistical, information-theoretic and structural methods over admitted observations and relations.",
            "owned_artifacts": ["MethodInvocation", "MethodResult", "MethodRefusal", "Counterexample"],
            "negative_charter": ["does not own mathematical truth by implementation", "does not own universal method-product lifecycles", "does not turn a score into a finding or decision"],
        },
        {
            "context_id": "ctx.codebase_intelligence.signal_model",
            "name": "Codebase Signal and Metric Model",
            "sovereign_responsibility": "Own application-specific signal definitions, grains, polarity, composition and provenance.",
            "owned_artifacts": ["SignalDefinition", "CodebaseSignal", "SignalProvenance", "ThresholdProfile"],
            "negative_charter": ["does not own universal enterprise metrics", "does not silently impute missing observations", "does not authorize actions"],
        },
        {
            "context_id": "ctx.codebase_intelligence.finding_lifecycle",
            "name": "Diagnostic Finding and Evidence",
            "sovereign_responsibility": "Derive, identify, rank, explain, persist and invalidate advisory findings from exact evidence.",
            "owned_artifacts": ["DiagnosticFinding", "FindingIdentity", "FindingEvidence", "FindingLifecycle", "FindingInvalidation"],
            "negative_charter": ["does not modify code", "does not assign human accountability without authority", "does not present an inference as a source fact"],
        },
        {
            "context_id": "ctx.codebase_intelligence.snapshot_history",
            "name": "Snapshot, History and Comparison",
            "sovereign_responsibility": "Publish content-bound analytical snapshots and compare compatible editions without rewriting history.",
            "owned_artifacts": ["AnalysisSnapshot", "SnapshotIdentity", "SnapshotComparison", "BaselineDesignation"],
            "negative_charter": ["does not own source-system history", "does not compare incompatible semantic editions as equivalent", "does not keep stale verdicts current"],
        },
        {
            "context_id": "ctx.codebase_intelligence.experience",
            "name": "Codebase Intelligence Experience",
            "sovereign_responsibility": "Render and deliver admitted facts, results, findings, evidence and refusals without minting new analytical truth.",
            "owned_artifacts": ["ReportView", "DashboardView", "CLIResponse", "APIResponse", "EvidenceExport"],
            "negative_charter": ["does not own analytical meaning", "does not hide partiality or refusal", "does not authorize code or deployment changes"],
        },
        {
            "context_id": "ctx.codebase_intelligence.execution_control",
            "name": "Analysis Execution Control",
            "sovereign_responsibility": "Own run/attempt identity, phase ordering, budgets, cancellation, retries, partial outcomes and operational receipts.",
            "owned_artifacts": ["AnalysisRun", "AnalysisAttempt", "ResourceBudget", "ExecutionReceipt", "CancellationReceipt"],
            "negative_charter": ["does not own domain semantics", "does not substitute runtime success for analytical validity", "does not retry non-idempotent effects because this product has no source-mutating effects"],
        },
    ]

    artifacts = [
        {
            "artifact": "AnalysisMandate",
            "owner_context": "ctx.codebase_intelligence.repository_intake",
            "identity": "tenant_or_user + requested repository scope + requested analysis edition + mandate nonce",
            "grain": "one requested bounded analysis",
            "time": "request time and optional deadline",
            "equality": "exact canonical fields and authority scope",
        },
        {
            "artifact": "RepositoryObservationCut",
            "owner_context": "ctx.codebase_intelligence.repository_intake",
            "identity": "content digest of admitted paths, revisions, configuration and capture rules",
            "grain": "one immutable repository/history cut",
            "time": "source-valid interval, capture time and recording time remain distinct",
            "equality": "same cut digest and admission edition",
        },
        {
            "artifact": "CodeFileIdentity",
            "owner_context": "ctx.codebase_intelligence.program_observation",
            "identity": "stable lineage identity across observed rename history within one repository authority",
            "grain": "one logical file occurrence lineage",
            "time": "valid-from/valid-to revisions plus observation time",
            "equality": "same issued file identity, not merely same current path",
        },
        {
            "artifact": "SyntaxObservation",
            "owner_context": "ctx.codebase_intelligence.program_observation",
            "identity": "observation cut + file identity + content digest + parser/grammar edition",
            "grain": "one parsed or refused file occurrence",
            "time": "source revision and analysis observation time",
            "equality": "same input, parser edition and canonical observation",
        },
        {
            "artifact": "CodeRelation",
            "owner_context": "ctx.codebase_intelligence.relation_model",
            "identity": "cut + relation kind + ordered endpoint identities + relation evidence digest",
            "grain": "one typed relation occurrence",
            "time": "source-valid interval and derivation time",
            "equality": "same typed endpoints, relation edition and evidence",
        },
        {
            "artifact": "MethodResult",
            "owner_context": "ctx.codebase_intelligence.analytical_methods",
            "identity": "method contract/implementation/configuration digests + exact input population digest",
            "grain": "one bounded method invocation result",
            "time": "input-valid interval and execution time",
            "equality": "same exact scope and canonical output",
        },
        {
            "artifact": "CodebaseSignal",
            "owner_context": "ctx.codebase_intelligence.signal_model",
            "identity": "signal definition edition + entity grain + observation cut + computation digest",
            "grain": "one signal value at its declared entity/time grain",
            "time": "valid time, observation time and computation time",
            "equality": "same signal edition, population, grain and canonical value",
        },
        {
            "artifact": "DiagnosticFinding",
            "owner_context": "ctx.codebase_intelligence.finding_lifecycle",
            "identity": "finding kind edition + stable subject identities + bounded condition identity",
            "grain": "one advisory diagnostic condition",
            "time": "first observed, last observed, valid interval, invalidated time",
            "equality": "same finding definition and stable subject set, not same prose",
        },
        {
            "artifact": "AnalysisSnapshot",
            "owner_context": "ctx.codebase_intelligence.snapshot_history",
            "identity": "canonical digest of mandate, cut, semantic/method/config editions and published artifact set",
            "grain": "one published analysis occurrence",
            "time": "publication time plus bounded validity interval",
            "equality": "same complete snapshot digest",
        },
        {
            "artifact": "AnalysisRun",
            "owner_context": "ctx.codebase_intelligence.execution_control",
            "identity": "run ID plus immutable mandate and cut identities",
            "grain": "one ordered execution lifecycle",
            "time": "start, phase intervals, completion/cancellation time",
            "equality": "same issued run identity",
        },
    ]

    commands = [
        ["RequestAnalysis", "repository_intake", "AnalysisMandate"],
        ["AdmitRepositoryCut", "repository_intake", "RepositoryObservationCut or AdmissionRefusal"],
        ["ObserveProgramArtifacts", "program_observation", "syntax/identity observations or bounded refusals"],
        ["ConstructRelations", "relation_model", "typed relations and unresolved-edge evidence"],
        ["ExecuteMethod", "analytical_methods", "method result, counterexample or refusal"],
        ["ComputeSignals", "signal_model", "signals with provenance or partial/refusal outcome"],
        ["DeriveFindings", "finding_lifecycle", "findings and finding evidence"],
        ["PublishSnapshot", "snapshot_history", "immutable analysis snapshot"],
        ["CompareSnapshots", "snapshot_history", "compatible comparison or incompatibility refusal"],
        ["RenderExperience", "experience", "view/export carrying exact source artifact refs"],
        ["CancelAnalysis", "execution_control", "cancellation receipt and bounded partial outcome"],
        ["InvalidateEvidence", "finding_lifecycle", "stale/invalidated findings and downstream work"],
    ]
    command_rows = [
        {
            "command": command,
            "owner_context": f"ctx.codebase_intelligence.{context}",
            "outcomes": outcome,
        }
        for command, context, outcome in commands
    ]

    events = [
        ["AnalysisRequested", "repository_intake"],
        ["RepositoryCutAdmitted", "repository_intake"],
        ["RepositoryCutRefused", "repository_intake"],
        ["ProgramObservationRecorded", "program_observation"],
        ["ProgramObservationRefused", "program_observation"],
        ["RelationsConstructed", "relation_model"],
        ["MethodExecuted", "analytical_methods"],
        ["MethodRefused", "analytical_methods"],
        ["SignalsComputed", "signal_model"],
        ["FindingsDerived", "finding_lifecycle"],
        ["FindingInvalidated", "finding_lifecycle"],
        ["SnapshotPublished", "snapshot_history"],
        ["SnapshotComparisonRefused", "snapshot_history"],
        ["ExperienceRendered", "experience"],
        ["AnalysisCancelled", "execution_control"],
        ["AnalysisCompleted", "execution_control"],
        ["AnalysisPartiallyCompleted", "execution_control"],
        ["AnalysisRefused", "execution_control"],
    ]
    event_rows = [
        {"event": event, "owner_context": f"ctx.codebase_intelligence.{context}"}
        for event, context in events
    ]

    state_machine = {
        "aggregate": "AnalysisRun",
        "owner_context": "ctx.codebase_intelligence.execution_control",
        "states": [
            "REQUESTED",
            "DISCOVERING",
            "ADMITTING",
            "OBSERVING",
            "RELATING",
            "ANALYZING",
            "DERIVING_FINDINGS",
            "PUBLISHING",
            "COMPLETE",
            "PARTIAL",
            "REFUSED",
            "CANCELLED",
            "STALE",
        ],
        "terminal_states": ["COMPLETE", "PARTIAL", "REFUSED", "CANCELLED", "STALE"],
        "transitions": [
            ["REQUESTED", "StartAnalysis", "DISCOVERING"],
            ["DISCOVERING", "FinishDiscovery", "ADMITTING"],
            ["ADMITTING", "AdmitRepositoryCut", "OBSERVING"],
            ["ADMITTING", "RefuseAdmission", "REFUSED"],
            ["OBSERVING", "FinishObservation", "RELATING"],
            ["RELATING", "FinishRelationConstruction", "ANALYZING"],
            ["ANALYZING", "FinishMethodsAndSignals", "DERIVING_FINDINGS"],
            ["DERIVING_FINDINGS", "FinishFindingDerivation", "PUBLISHING"],
            ["PUBLISHING", "PublishCompleteSnapshot", "COMPLETE"],
            ["PUBLISHING", "PublishPartialSnapshot", "PARTIAL"],
            ["REQUESTED|DISCOVERING|ADMITTING|OBSERVING|RELATING|ANALYZING|DERIVING_FINDINGS|PUBLISHING", "CancelAnalysis", "CANCELLED"],
            ["COMPLETE|PARTIAL", "InvalidateEvidence", "STALE"],
        ],
        "ordering_law": "A successor phase names the exact predecessor receipt; phases may not be skipped, duplicated or silently reordered.",
    }

    model = {
        "schema_version": "1.0.0",
        "record_kind": "application_product_ddd_candidate",
        "product_id": PRODUCT_ID,
        "name": "Software Codebase Intelligence",
        "portfolio_disposition": "RETAIN_EXTERNAL_APPLICATION_PRODUCT_CANDIDATE",
        "product_plane": "application_domain_product",
        "canonical_platform_product_id": None,
        "domain": "software_engineering_and_developer_productivity",
        "sovereign_question": "What evidence-backed structural, temporal, semantic, ownership and operational risks exist in an exact bounded software codebase, and which advisory findings can be justified without modifying source or inventing authority?",
        "sovereign_responsibility": "Own the lifecycle from a bounded codebase-analysis mandate and immutable repository observation cut through software-domain observations, relations, methods, signals, diagnostic findings, evidence, snapshots and non-authoritative delivery.",
        "users_and_jobs": [
            {"actor": "software engineer", "jobs": ["understand architecture and coupling", "inspect change risk and code health", "trace a finding to source evidence"]},
            {"actor": "engineering leader", "jobs": ["inspect ownership concentration and systemic risk", "compare health across releases", "prioritize review or refactoring work"]},
            {"actor": "reviewer or auditor", "jobs": ["reproduce an analysis", "inspect method/configuration provenance", "challenge or invalidate a finding"]},
            {"actor": "automation operator", "jobs": ["run bounded analysis in CI", "enforce resource/time budgets", "publish or refuse a snapshot deterministically"]},
        ],
        "negative_charter": [
            "does not own universal enterprise source-system, connector, storage, query, semantic-layer, planning, decision, activation or presentation products",
            "does not promote source-code, Git, repository or developer-workflow vocabulary into universal business semantics",
            "does not modify source code, repositories, deployments or external systems",
            "does not make a diagnostic finding an authorized human or machine decision",
            "does not treat an algorithm implementation as mathematical, semantic or qualification authority",
            "does not claim horizontal portability or cross-industry acceptance from one software-domain implementation",
            "does not equate successful execution, a rendered dashboard or a passing validator with product ratification",
        ],
        "bounded_contexts": bounded_contexts,
        "owned_artifacts": artifacts,
        "commands": command_rows,
        "events": event_rows,
        "state_machine": state_machine,
        "invariants": [
            "Every analysis result, signal and finding is bound to one immutable repository observation cut, semantic/method/configuration editions and source evidence.",
            "The application never modifies the observed source and cannot issue deployment, code-change or human-authority effects.",
            "A finding is an inference with evidence and uncertainty, never a source fact or authorized decision.",
            "Stable file identity is not collapsed to path; rename history and re-creation are distinguished.",
            "Commit/source time, valid time, observation time, computation time and publication time remain distinct.",
            "Partial, refused, cancelled and stale outcomes cannot be represented as complete/current.",
            "A snapshot is append-only and content-bound; correction creates a successor rather than rewriting prior evidence.",
            "The experience layer may select and render admitted artifacts but may not mint facts, findings or authority.",
            "Identical admitted cut, editions, configuration, budgets and deterministic implementation inputs must produce the same canonical snapshot or an explicit nondeterminism refusal.",
            "Every durable artifact, command, transition and decision in this DDD has exactly one owner context.",
        ],
        "refusals": [
            {"code": "repository_scope_unauthorized", "precedence": 1},
            {"code": "repository_or_revision_unavailable", "precedence": 2},
            {"code": "observation_cut_unresolved", "precedence": 3},
            {"code": "unsupported_or_malformed_source", "precedence": 4},
            {"code": "identity_or_relation_ambiguity_unbounded", "precedence": 5},
            {"code": "method_preconditions_unsatisfied", "precedence": 6},
            {"code": "resource_or_time_budget_exhausted", "precedence": 7},
            {"code": "nondeterministic_or_nonreproducible_result", "precedence": 8},
            {"code": "snapshot_semantic_incompatibility", "precedence": 9},
            {"code": "evidence_stale_or_invalidated", "precedence": 10},
            {"code": "cancelled_by_authority", "precedence": 11},
        ],
        "authority_model": {
            "mandate_authority": "requesting user/tenant or CI policy selects scope and budgets",
            "source_authority": "repository/version-control authority owns source content and access",
            "semantic_authority": "application product edition owns only software-domain observation, signal and finding meanings",
            "method_authority": "editioned abstract method contracts remain distinct from Python implementations",
            "publication_authority": "execution control may publish only a complete or explicitly partial/refused snapshot",
            "effect_authority": "none; all findings are advisory and external action requires a separate product/actor authority",
            "ratification_authority": "accountable product authority, not this builder or implementation",
        },
        "time_model": [
            "source revision/commit time",
            "artifact valid time",
            "repository capture time",
            "analysis phase execution time",
            "snapshot publication time",
            "finding validity and invalidation interval",
        ],
        "concurrency_and_idempotency": [
            "Run ID and attempt ID are distinct; a retry cannot overwrite a prior attempt receipt.",
            "Content-addressed observations and snapshots deduplicate exact equality only.",
            "Concurrent runs may share immutable observations but not mutable attempt state.",
            "Publication is compare-and-append against exact predecessor/baseline identity.",
            "Cancellation is monotone for an attempt and preserves completed phase receipts.",
        ],
        "published_apis": [
            {"operation": "request_analysis", "returns": "run identity or mandate refusal"},
            {"operation": "get_run", "returns": "phase/state/partiality/resource receipts"},
            {"operation": "get_snapshot", "returns": "exact immutable snapshot"},
            {"operation": "list_findings", "returns": "bounded finding population"},
            {"operation": "explain_finding", "returns": "evidence/provenance/method chain"},
            {"operation": "compare_snapshots", "returns": "compatible diff or typed incompatibility refusal"},
            {"operation": "export_evidence", "returns": "portable evidence package, not implementation portability proof"},
            {"operation": "cancel_run", "returns": "cancellation or terminal-state refusal"},
        ],
        "dependencies": [
            {"dependency": "repository and version-control readers", "seam": "provider adapter behind admitted observation-cut contract"},
            {"dependency": "language parsers/grammars", "seam": "editioned parse observation with syntax refusal"},
            {"dependency": "graph, temporal, statistical and information-theory methods", "seam": "exact method invocation/result/refusal contract"},
            {"dependency": "local persistence/query implementations", "seam": "application snapshot/history ports; no storage-product sovereignty"},
            {"dependency": "CLI/API/report/dashboard renderers", "seam": "read-only delivery of admitted artifacts"},
        ],
        "economic_adoption_and_exit_seams": {
            "adoption": ["local CLI", "CI pipeline", "Python API", "read-only web experience"],
            "cost_drivers": ["repository size/history", "language/parser mix", "graph density", "method selection", "retention window", "concurrency and resource budgets"],
            "exit": ["export observation identities, signals, findings, snapshots and evidence as documented machine-readable artifacts", "retain source repository unchanged", "remove local cache/history without invalidating exported immutable evidence"],
            "lock_in_refusal": "No proprietary snapshot encoding may be the only representation of durable user evidence.",
        },
        "boundary_falsification_tests": [
            {"test": "merge_with_generic_data_platform", "verdict": "REFUSE", "reason": "the application owns software-domain observations and diagnostic lifecycle while horizontal platform products own reusable contracts and provider operations"},
            {"test": "demote_to_graph_library", "verdict": "REFUSE", "reason": "graph methods do not own repository intake, stable file identity, signal/finding lifecycle, snapshots or delivery"},
            {"test": "demote_to_dashboard", "verdict": "REFUSE", "reason": "presentation is downstream of evidence-bearing analysis and owns no finding meaning"},
            {"test": "merge_with_source_connector", "verdict": "REFUSE", "reason": "repository acquisition is one bounded context and does not own analysis semantics or findings"},
            {"test": "promote_all_modules_to_horizontal_libraries", "verdict": "REFUSE", "reason": "most modules are application-composed, effectful or software-domain-specific; extraction requires exact contract and qualification evidence"},
            {"test": "remove_python_implementation", "verdict": "BOUNDARY_SURVIVES", "reason": "product semantics and DDD can be implemented independently; the Python package is not semantic authority"},
        ],
        "non_collapse_laws": [
            "application product != universal data/analytics platform",
            "repository observation cut != source repository",
            "syntax observation != program meaning",
            "relation != causation",
            "method result != signal definition",
            "signal != diagnostic finding",
            "finding != source fact",
            "finding != authorized decision or action",
            "snapshot publication != product qualification",
            "Python implementation != semantic authority",
            "software-engineering domain acceptance != unrelated-industry horizontal acceptance",
        ],
        "implementation_binding": {
            "implementation_id": "implementation.shannon_python.codebase_insight",
            "placement_projection_digest": placement_digest,
            "status": "UNQUALIFIED_IMPLEMENTATION_CANDIDATE",
        },
        "compiler_and_solution_synthesis_binding": {
            "global_solution_compiler_stage": None,
            "status": "EXTERNAL_APPLICATION_PRODUCT_NOT_A_COMPILER_STAGE",
            "allowed_use": "May be selected as a software-engineering solution/application after its exact contracts and implementation are qualified; does not compile arbitrary enterprise solutions.",
        },
        "vertical_posture": {
            "native_vertical": "software engineering and developer productivity",
            "structural_examples": ["open-source repository analysis", "enterprise monorepo analysis", "multi-language service estate analysis"],
            "unrelated_vertical_acceptance_claim": False,
            "law": "These examples do not satisfy two-unrelated-industry acceptance for any promoted horizontal library.",
        },
        "evidence_and_readiness": {
            "candidate_ddd_complete": True,
            "semantic_ratified": False,
            "implementation_qualified": False,
            "independently_appraised": False,
            "portable_offer": False,
            "executed_vertical_acceptance": False,
            "build_ready": False,
            "product_ratified": False,
        },
        "remaining_gates": [
            "ontology-level portfolio authority must accept/rehome/reject this application product",
            "exact semantic editions and shared-library contracts must be ratified",
            "Python implementation identity, build and exact-scope execution must be qualified",
            "extracted reusable modules require independent appraisal and second implementations for portability",
            "application release/runtime/security/cost evidence must be bound to physical occurrences",
            "accountable product authority must ratify the bounded application product",
        ],
        "completion_claim": False,
    }
    model["ddd_digest"] = digest(model)
    return model


def main() -> int:
    placement = json.loads(PLACEMENT.read_text(encoding="utf-8"))
    model = build_model(placement["projection_digest"])
    OUTPUT.write_text(json.dumps(model, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    context_ids = {row["context_id"] for row in model["bounded_contexts"]}
    owned_artifact_names = {row["artifact"] for row in model["owned_artifacts"]}
    summary = {
        "report_id": "shannon_codebase_intelligence_ddd",
        "product_id": PRODUCT_ID,
        "portfolio_disposition": model["portfolio_disposition"],
        "bounded_context_count": len(context_ids),
        "owned_artifact_count": len(owned_artifact_names),
        "command_count": len(model["commands"]),
        "event_count": len(model["events"]),
        "invariant_count": len(model["invariants"]),
        "refusal_count": len(model["refusals"]),
        "candidate_ddd_complete": True,
        "semantic_ratified": False,
        "implementation_qualified": False,
        "build_ready": False,
        "product_ratified": False,
        "ddd_digest": model["ddd_digest"],
        "completion_claim": False,
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
