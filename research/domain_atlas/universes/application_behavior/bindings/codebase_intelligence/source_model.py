"""Authoritative source model for the Shannon code-intelligence application binding.

This file binds the executable Python package to the provider-neutral application-behavior
universe.  It does not promote Python, this repository, or the code-intelligence product into
universal data-and-analytics semantics.
"""
from __future__ import annotations

from typing import Any

AS_OF = "2026-08-28"
EDITION = 1
PARENT_AUTHORITY = "research/domain_atlas/universes/application_behavior"

EVIDENCE: list[dict[str, Any]] = [
    {
        "evidence_id": "evidence.code_intelligence.repository_architecture",
        "role": "architecture",
        "locator": "docs/architecture/README.md",
        "claim": "The executable package analyzes software repositories through structural, temporal, semantic and relationship models.",
        "does_not_prove": ["enterprise data-platform completeness", "provider qualification", "vertical acceptance"],
    },
    {
        "evidence_id": "evidence.python.packaging_pyproject",
        "role": "standard",
        "locator": "https://packaging.python.org/en/latest/guides/writing-pyproject-toml/",
        "claim": "pyproject.toml declares Python build-system, project metadata, dependencies, scripts and tool configuration.",
        "does_not_prove": ["product sovereignty", "runtime portability", "semantic authority"],
    },
    {
        "evidence_id": "evidence.arrow.language_independent_format",
        "role": "standard",
        "locator": "https://arrow.apache.org/docs/format/Columnar.html",
        "claim": "Apache Arrow specifies a language-agnostic columnar representation and transport protocol, demonstrating that portable data contracts must not be owned by one Python implementation.",
        "does_not_prove": ["business meaning", "query semantics", "implementation qualification"],
    },
    {
        "evidence_id": "evidence.substrait.cross_language_plan",
        "role": "standard",
        "locator": "https://substrait.io/spec/specification/",
        "claim": "Substrait specifies cross-language relational plan types, expressions, relations, serialization and extensions, demonstrating that a Python planner is one producer or consumer rather than plan authority by default.",
        "does_not_prove": ["all analytical methods", "physical-engine equivalence", "application authority"],
    },
    {
        "evidence_id": "evidence.opentelemetry.signals",
        "role": "standard",
        "locator": "https://opentelemetry.io/docs/concepts/signals/",
        "claim": "OpenTelemetry distinguishes traces, metrics, logs and baggage as telemetry signals, so code-intelligence observations must not collapse those signal kinds into domain events or business facts.",
        "does_not_prove": ["domain event meaning", "business metric authority", "outcome correctness"],
    },
    {
        "evidence_id": "evidence.parent.application_behavior",
        "role": "architecture",
        "locator": f"{PARENT_AUTHORITY}/README.md",
        "claim": "The application-behavior universe owns provider-neutral commands, queries, state transitions, coordination, effects and execution-evidence contracts while imported universes retain their meanings.",
        "does_not_prove": ["this product is qualified", "this implementation is portable", "this product is ratified"],
    },
]

PRODUCT: dict[str, Any] = {
    "product_id": "application_product.software_codebase_intelligence",
    "name": "Software / Codebase Intelligence and Engineering Analytics",
    "edition": EDITION,
    "status": "implemented_candidate_unqualified",
    "completion_claim": False,
    "product_kind": "application_domain_analytical_product",
    "application_domain": "software_engineering",
    "implementation_language": "python",
    "parent_semantic_authority": PARENT_AUTHORITY,
    "sovereign_question": "What evidence-backed structural, temporal, semantic and architectural conditions exist in an observed software repository, and what bounded findings can be presented to software-engineering decision makers?",
    "users": [
        "software engineer",
        "technical lead",
        "software architect",
        "engineering manager",
        "maintainer",
        "assurance or review practitioner",
    ],
    "jobs": [
        "observe a repository at an exact cut",
        "derive syntax, identity, dependency, temporal and semantic facts",
        "compute reproducible software-engineering signals",
        "detect bounded architectural and maintainability findings",
        "compare retained repository snapshots",
        "present evidence without automatically authorizing remediation",
    ],
    "owned_artifacts": [
        {"artifact": "RepositoryObservation", "owner": "application_product.software_codebase_intelligence", "meaning": "An admitted observation of one repository occurrence at a bounded cut."},
        {"artifact": "SoftwareFileIdentity", "owner": "application_product.software_codebase_intelligence", "meaning": "Application identity for a file across observed repository change, including rename history."},
        {"artifact": "SoftwareSyntaxFact", "owner": "application_product.software_codebase_intelligence", "meaning": "Observed language syntax facts such as functions, classes and imports."},
        {"artifact": "SoftwareRelationGraph", "owner": "application_product.software_codebase_intelligence", "meaning": "Typed software relationships derived from admitted observations."},
        {"artifact": "SoftwareRelationTensor", "owner": "application_product.software_codebase_intelligence", "meaning": "Multi-layer analytical representation of software relationships; not a universal graph or tensor contract."},
        {"artifact": "EngineeringSignal", "owner": "application_product.software_codebase_intelligence", "meaning": "A versioned software-engineering measurement with formula and provenance."},
        {"artifact": "EngineeringFinding", "owner": "application_product.software_codebase_intelligence", "meaning": "A bounded evidence-backed diagnostic result; not an authorized code change."},
        {"artifact": "CodebaseSnapshot", "owner": "application_product.software_codebase_intelligence", "meaning": "A retained analytical state for comparison and trend analysis."},
        {"artifact": "EngineeringReportProjection", "owner": "application_product.software_codebase_intelligence", "meaning": "A presentation projection over product facts and findings."},
    ],
    "commands": ["DiscoverRepository", "AdmitRepositoryCut", "ParseSoftwareFiles", "PopulateSoftwareRelations", "ComputeEngineeringSignals", "EvaluateEngineeringFindings", "RetainCodebaseSnapshot", "CompareCodebaseSnapshots", "RenderEngineeringReport"],
    "queries": ["GetFileEvidence", "GetRelationNeighborhood", "GetEngineeringSignals", "ListEngineeringFindings", "GetSnapshotDifference", "ExplainFinding"],
    "events": ["RepositoryCutAdmitted", "SoftwareFileObserved", "SoftwareRelationDerived", "EngineeringSignalComputed", "EngineeringFindingEmitted", "CodebaseSnapshotRetained"],
    "state_machine": {
        "states": ["declared", "observing", "observed", "analyzing", "analyzed", "reported", "refused", "superseded"],
        "transitions": [
            ["declared", "observing", "DiscoverRepository"],
            ["observing", "observed", "RepositoryCutAdmitted"],
            ["observed", "analyzing", "ComputeEngineeringSignals"],
            ["analyzing", "analyzed", "EngineeringFindingEmitted"],
            ["analyzed", "reported", "RenderEngineeringReport"],
            ["*", "refused", "RefusalRecorded"],
            ["observed|analyzed|reported", "superseded", "NewRepositoryCutAdmitted"],
        ],
    },
    "invariants": [
        "every result names one admitted repository cut and implementation edition",
        "file identity evolution is distinct from path text",
        "observed facts are distinct from derived signals and findings",
        "a finding carries evidence and cannot authorize or perform remediation",
        "missing parser or relation coverage is represented as partiality or refusal",
        "identical admitted inputs and configuration produce deterministic contract outputs where the declared method is deterministic",
        "imported horizontal contracts retain their semantic owners",
    ],
    "refusals": [
        "refuse unreadable, unbounded or unsupported repository observations",
        "refuse to infer business truth from source-code structure",
        "refuse to label a heuristic finding as proof",
        "refuse automatic remediation without a separate authorized application workflow",
        "refuse provider qualification from package installation or unit tests",
        "refuse Python object identity as a portable artifact identity",
    ],
    "time_model": ["commit_time", "author_time", "observation_time", "analysis_time", "snapshot_effective_time"],
    "concurrency_model": ["repository cut is immutable during one run", "parallel parsing must preserve deterministic merge order", "snapshot publication uses explicit identity and replacement rules"],
    "authority_model": {
        "product": "owns software-intelligence interpretation only",
        "repository": "repository owner controls access and accepted source cut",
        "policy": "security and policy contexts control admission and disclosure",
        "remediation": "human or external change-management authority controls effects",
        "qualification": "independent qualification authority remains absent",
    },
    "evidence_model": ["source cut", "configuration digest", "toolchain and package identity", "fact lineage", "formula/version", "counterexample or refusal", "snapshot identity"],
    "published_interfaces": ["Python API", "command-line interface", "server/API projection", "snapshot/event serialization", "HTML/report projections"],
    "negative_charter": [
        "does not own universal enterprise source-system classes or connector semantics",
        "does not own generic data contracts, master data, catalog, lineage, data quality or governance",
        "does not own warehouse, lakehouse, stream, query or orchestration platform semantics",
        "does not own universal business metrics or analytical-method meaning",
        "does not own a general notebook, BI, planning or presentation product",
        "does not make research generators into a production compiler or control plane",
        "does not make Python the semantic authority for portable data, plans, telemetry or evidence",
    ],
    "non_collapse_laws": [
        "repository occurrence != universal source-system registry",
        "parser or AST library != analytical product",
        "relationship graph or tensor != product boundary",
        "engineering signal != universal business metric",
        "engineering finding != authorized remediation",
        "report projection != underlying evidence",
        "Python package != enterprise data-and-analytics platform",
        "research builder != production compiler",
        "passing unit tests != provider qualification",
    ],
    "economic_adoption_exit_seams": [
        "repository hosting and access remain replaceable inputs",
        "language parsers and storage adapters require explicit compatibility editions",
        "retained facts and snapshots require documented export before implementation substitution",
        "algorithm or threshold changes invalidate affected comparisons unless migrated",
        "product adoption evidence and product boundary ratification remain open",
    ],
    "falsification_tests": [
        "If another product can own repository observation, software identities, engineering signals and findings without importing this product's lifecycle, merge or demote the boundary.",
        "If a component is useful without software-domain meaning, classify it as an imported horizontal library or infrastructure adapter rather than product semantics.",
        "If a Python-specific object leaks into a published portable contract, reject the contract or add a language-independent carrier.",
        "If remediation occurs from a finding without an admitted authority handoff, fail conformance.",
    ],
    "qualification": {"semantic_ratified": False, "implementation_qualified": False, "independent_appraisal": False, "portable": False, "executed_vertical_acceptance": False, "build_ready": False, "ratified": False},
    "evidence_refs": [row["evidence_id"] for row in EVIDENCE],
}

ROLE_DEFINITIONS: dict[str, dict[str, Any]] = {
    "package_contract": {"ownership_kind": "implementation_packaging", "imports": ["Python packaging and typing specifications"], "cannot_own": ["product semantics", "portable IR"]},
    "acquisition_observation": {"ownership_kind": "product_library", "imports": ["source occurrence", "immutable cut", "security admission", "data shape"], "cannot_own": ["generic connector semantics", "all source systems"]},
    "relationship_modeling": {"ownership_kind": "product_library", "imports": ["graph and tensor mathematics", "identity", "provenance"], "cannot_own": ["universal graph semantics", "business ontology"]},
    "analytical_method_kernel": {"ownership_kind": "method_implementation", "imports": ["mathematical method contracts", "measurement semantics"], "cannot_own": ["method theory", "business decision authority"]},
    "product_analytics": {"ownership_kind": "product_library", "imports": ["method kernels", "evidence", "measurement semantics"], "cannot_own": ["universal metrics", "automatic remediation"]},
    "persistence_query_adapter": {"ownership_kind": "infrastructure_adapter", "imports": ["persistence", "query", "schema evolution", "resource budgets"], "cannot_own": ["durability theory", "generic warehouse or lakehouse product"]},
    "runtime_control": {"ownership_kind": "application_runtime", "imports": ["runtime resources", "cancellation", "configuration", "security", "observability"], "cannot_own": ["physical provider qualification", "generic orchestration product"]},
    "experience_delivery": {"ownership_kind": "application_experience", "imports": ["presentation", "accessibility", "delivery", "API transport"], "cannot_own": ["underlying analytical truth", "general BI platform"]},
    "support_assurance": {"ownership_kind": "implementation_support", "imports": ["error taxonomy", "logging", "debug evidence"], "cannot_own": ["semantic authority", "independent assurance"]},
}

COMPONENT_ROLE: dict[str, str] = {
    "__init__.py": "package_contract", "py.typed": "package_contract",
    "extract": "acquisition_observation", "facts": "acquisition_observation", "file_ops.py": "acquisition_observation", "grammar_installer.py": "acquisition_observation", "scanning": "acquisition_observation", "syntax": "acquisition_observation", "temporal": "acquisition_observation",
    "cross_layer": "relationship_modeling", "graph": "relationship_modeling", "graphs": "relationship_modeling", "populate": "relationship_modeling", "relate": "relationship_modeling", "tensor": "relationship_modeling",
    "algorithms": "analytical_method_kernel", "math": "analytical_method_kernel", "semantics": "analytical_method_kernel",
    "architecture": "product_analytics", "finders": "product_analytics", "insights": "product_analytics", "signals": "product_analytics",
    "cache.py": "persistence_query_adapter", "events": "persistence_query_adapter", "persistence": "persistence_query_adapter", "query": "persistence_query_adapter", "storage": "persistence_query_adapter",
    "config.py": "runtime_control", "core": "runtime_control", "environment.py": "runtime_control", "infrastructure": "runtime_control", "intake": "runtime_control", "kernel": "runtime_control", "security.py": "runtime_control", "session.py": "runtime_control",
    "api.py": "experience_delivery", "cli": "experience_delivery", "server": "experience_delivery", "visualization": "experience_delivery",
    "debug_export.py": "support_assurance", "exceptions": "support_assurance", "logging_config.py": "support_assurance",
}

LIBRARIES: list[dict[str, Any]] = [
    {"library_id": "library.code_intelligence.repository_observation", "role": "acquisition_observation", "types": ["RepositoryOccurrence", "RepositoryCut", "ObservedFile"], "operations": ["discover", "admit_cut", "read_file"], "decisions": ["include_or_skip", "supported_or_refused"], "invariants": ["cut is bounded", "skips retain reasons"], "refusals": ["unreadable", "unsupported", "budget_exhausted"], "dependencies": ["source occurrence", "security admission"], "compiler_binding": "application observation declaration -> repository observation plan"},
    {"library_id": "library.code_intelligence.software_identity", "role": "acquisition_observation", "types": ["SoftwareFileIdentity", "PathHistory", "CommitIdentity"], "operations": ["register", "rename", "delete", "resolve_at"], "decisions": ["same_identity_or_new"], "invariants": ["rename preserves identity", "re-add after delete creates new identity"], "refusals": ["ambiguous history"], "dependencies": ["repository observation"], "compiler_binding": "identity policy -> identity resolver"},
    {"library_id": "library.code_intelligence.syntax_fact", "role": "acquisition_observation", "types": ["FunctionFact", "ClassFact", "ImportFact", "FileSyntax"], "operations": ["parse", "normalize", "extract"], "decisions": ["grammar_selection", "fallback_or_refusal"], "invariants": ["facts name source location", "fallback is observable"], "refusals": ["unsupported_language", "parse_failure"], "dependencies": ["language grammar", "data shape"], "compiler_binding": "language declaration -> parser pack"},
    {"library_id": "library.code_intelligence.relationship_model", "role": "relationship_modeling", "types": ["SoftwareRelation", "RelationGraph", "RelationTensor"], "operations": ["resolve_import", "populate_relation", "slice_tensor"], "decisions": ["resolved_external_phantom", "edge_admission"], "invariants": ["edge endpoints use admitted identities", "relation type is explicit"], "refusals": ["untracked_endpoint", "ambiguous_binding"], "dependencies": ["software identity", "syntax fact"], "compiler_binding": "relationship declaration -> relation population plan"},
    {"library_id": "library.code_intelligence.temporal_evolution", "role": "relationship_modeling", "types": ["CommitFact", "ChangeFact", "ChurnSeries", "CochangeRelation"], "operations": ["extract_history", "build_churn", "compute_cochange"], "decisions": ["history_partiality", "rename_link"], "invariants": ["time role is explicit", "partial history is flagged"], "refusals": ["history_unavailable", "timeout"], "dependencies": ["repository cut", "software identity"], "compiler_binding": "history request -> temporal observation plan"},
    {"library_id": "library.code_intelligence.method_kernel", "role": "analytical_method_kernel", "types": ["MethodInput", "MethodConfiguration", "MethodResult"], "operations": ["compute_graph_metric", "compute_statistic", "decompose_tensor"], "decisions": ["applicability", "convergence"], "invariants": ["method edition and parameters retained"], "refusals": ["insufficient_population", "non_convergence", "invalid_input"], "dependencies": ["mathematical contracts"], "compiler_binding": "analytical method selection -> method invocation"},
    {"library_id": "library.code_intelligence.signal_semantics", "role": "product_analytics", "types": ["EngineeringSignal", "SignalMetadata", "ThresholdPolicy"], "operations": ["compute", "normalize", "compare"], "decisions": ["polarity", "threshold_tier"], "invariants": ["one producer per signal edition", "formula and provenance retained"], "refusals": ["missing_inputs", "invalid_threshold"], "dependencies": ["method kernel", "measurement semantics"], "compiler_binding": "signal declaration -> deterministic signal graph"},
    {"library_id": "library.code_intelligence.finding_evaluation", "role": "product_analytics", "types": ["EngineeringFinding", "FindingEvidence", "FindingSeverity"], "operations": ["evaluate", "rank", "explain"], "decisions": ["emit_or_refuse", "severity"], "invariants": ["finding names evidence", "finding performs no remediation"], "refusals": ["evidence_insufficient", "rule_not_applicable"], "dependencies": ["engineering signals", "policy"], "compiler_binding": "finding rule -> evaluation plan"},
    {"library_id": "library.code_intelligence.snapshot_history", "role": "persistence_query_adapter", "types": ["CodebaseSnapshot", "SnapshotIdentity", "SnapshotDifference"], "operations": ["retain", "load", "compare", "invalidate"], "decisions": ["replacement", "compatibility"], "invariants": ["snapshot identifies cut and tool edition"], "refusals": ["incompatible_edition", "missing_snapshot"], "dependencies": ["persistence", "schema evolution"], "compiler_binding": "retention declaration -> snapshot persistence plan"},
    {"library_id": "library.code_intelligence.report_projection", "role": "experience_delivery", "types": ["EngineeringReportProjection", "DashboardState", "ExportArtifact"], "operations": ["project", "render", "export"], "decisions": ["disclosure", "representation"], "invariants": ["projection cannot mint facts", "source evidence remains addressable"], "refusals": ["unauthorized_disclosure", "unsupported_representation"], "dependencies": ["presentation", "accessibility", "delivery"], "compiler_binding": "experience declaration -> report projection plan"},
]
