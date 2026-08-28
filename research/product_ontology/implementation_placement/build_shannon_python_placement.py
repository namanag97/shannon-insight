#!/usr/bin/env python3
"""Build the authoritative placement projection for the current Python package.

The checked-in Python implementation is classified as a software-engineering
analytics application and qualification candidate. It is not promoted into the
universal enterprise data/analytics platform or made semantic authority merely
because an implementation exists.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SRC = ROOT / "src" / "shannon_insight"
FAMILY_ROOT = ROOT / "research" / "analytics_landscape" / "product_families"

APPLICATION_PRODUCT_ID = "application_product.software_engineering.codebase_intelligence"

# Implementation roles are deliberately narrower than product-family ownership.
# The default retains an unknown module inside the application boundary until an
# exact reusable contract and sovereign owner are separately adjudicated.
ROLE_RULES: dict[str, tuple[str, tuple[str, ...], str]] = {
    "facts": (
        "domain_observation_and_identity",
        ("hpf_source_acquisition", "hpf_measurement_semantics"),
        "Owns code/Git observation carriers and stable application identities.",
    ),
    "intake": (
        "application_acquisition",
        ("hpf_source_acquisition", "hpf_contract_admission"),
        "Admits bounded repository inputs into the application pipeline.",
    ),
    "extract": (
        "application_acquisition",
        ("hpf_source_acquisition",),
        "Extracts source-code observations; it is not a general enterprise connector framework.",
    ),
    "scanning": (
        "application_acquisition",
        ("hpf_source_acquisition", "hpf_contract_admission"),
        "Parses source-language inputs under application-specific admission rules.",
    ),
    "syntax": (
        "domain_semantic_library_candidate",
        ("hpf_domain_semantics", "hpf_measurement_semantics"),
        "Models program syntax observations for the software-engineering domain.",
    ),
    "relate": (
        "domain_relation_construction",
        ("hpf_graph_network", "hpf_analytics_engineering"),
        "Constructs codebase relations from admitted observations.",
    ),
    "temporal": (
        "analytical_method_kernel_candidate",
        ("hpf_temporal_forecast", "hpf_diagnostic_rca"),
        "Computes repository-history temporal evidence; does not own universal time-series semantics.",
    ),
    "graphs": (
        "analytical_method_kernel_candidate",
        ("hpf_graph_network", "hpf_diagnostic_rca"),
        "Provides graph analyses specialized by the application.",
    ),
    "graph": (
        "analytical_method_kernel_candidate",
        ("hpf_graph_network", "hpf_diagnostic_rca"),
        "Provides graph analyses specialized by the application.",
    ),
    "tensor": (
        "analytical_method_kernel_candidate",
        ("hpf_graph_network", "hpf_descriptive_statistics"),
        "Provides multilayer graph/tensor methods as an implementation candidate, not semantic authority.",
    ),
    "algorithms": (
        "analytical_method_kernel_candidate",
        ("hpf_descriptive_statistics", "hpf_diagnostic_rca"),
        "Contains reusable algorithm implementations whose exact contracts still require qualification.",
    ),
    "math": (
        "analytical_method_kernel_candidate",
        ("hpf_descriptive_statistics", "hpf_measurement_semantics"),
        "Implements mathematical procedures; equations and tests define candidate behavior, not product sovereignty.",
    ),
    "semantics": (
        "domain_semantic_library_candidate",
        ("hpf_domain_semantics", "hpf_measurement_semantics"),
        "Derives software-domain concepts and roles from observations.",
    ),
    "signals": (
        "application_measurement_and_scoring",
        ("hpf_semantic_metrics", "hpf_diagnostic_rca"),
        "Owns application signal composition and scoring, not a universal metric system.",
    ),
    "cross_layer": (
        "application_diagnostic_analysis",
        ("hpf_diagnostic_rca", "hpf_graph_network"),
        "Combines admitted evidence across software-analysis layers.",
    ),
    "architecture": (
        "application_diagnostic_analysis",
        ("hpf_diagnostic_rca", "hpf_graph_network"),
        "Analyzes software architecture as application-domain meaning.",
    ),
    "insights": (
        "application_finding_lifecycle",
        ("hpf_diagnostic_rca", "hpf_investigation_decision_ops"),
        "Owns application findings and diagnostic interpretation.",
    ),
    "finders": (
        "application_finding_lifecycle",
        ("hpf_diagnostic_rca",),
        "Detects bounded software-engineering conditions.",
    ),
    "scope": (
        "application_decision_support",
        ("hpf_investigation_decision_ops",),
        "Bounds change impact and decision-support scope without authorizing external effects.",
    ),
    "events": (
        "application_evidence_eventing",
        ("hpf_trust_assurance_ops",),
        "Publishes application evidence events; it is not the universal event backbone.",
    ),
    "persistence": (
        "application_infrastructure",
        ("hpf_data_products", "hpf_runtime_control"),
        "Persists application artifacts under local implementation semantics.",
    ),
    "storage": (
        "application_infrastructure",
        ("hpf_data_products", "hpf_runtime_control"),
        "Stores application snapshots and facts; not a general lakehouse/storage product.",
    ),
    "query": (
        "application_infrastructure",
        ("hpf_query_compute",),
        "Serves application queries; not a general analytical query engine.",
    ),
    "cache": (
        "application_infrastructure",
        ("hpf_query_compute", "hpf_runtime_control"),
        "Provides local acceleration with application-bounded invalidation semantics.",
    ),
    "kernel": (
        "application_orchestration",
        ("hpf_orchestration_dataflow", "hpf_runtime_control"),
        "Coordinates codebase analysis; it is not the global solution compiler, planner, or reconciler.",
    ),
    "core": (
        "application_support",
        (),
        "Shared application implementation support with no independent product claim.",
    ),
    "infrastructure": (
        "application_runtime_support",
        ("hpf_runtime_control", "hpf_trust_assurance_ops"),
        "Supplies application runtime, provenance, and operational support.",
    ),
    "environment": (
        "application_runtime_support",
        ("hpf_runtime_control",),
        "Detects and binds the local application environment.",
    ),
    "server": (
        "experience_delivery",
        ("hpf_data_apps_embedded", "hpf_dashboards_scorecards"),
        "Delivers the application experience and API.",
    ),
    "visualization": (
        "experience_delivery",
        ("hpf_visual_presentation",),
        "Renders application views; renderer behavior does not own analytical meaning.",
    ),
    "reporting": (
        "experience_delivery",
        ("hpf_reporting_narrative",),
        "Publishes bounded analytical reports.",
    ),
    "cli": (
        "experience_delivery",
        ("hpf_data_apps_embedded",),
        "Exposes the application through a command-line experience.",
    ),
    "api": (
        "experience_delivery",
        ("hpf_data_apps_embedded",),
        "Exposes application operations; it is not a universal platform API.",
    ),
    "config": (
        "application_control",
        ("hpf_runtime_control",),
        "Configures the application without becoming domain or provider authority.",
    ),
    "exceptions": (
        "application_control",
        ("hpf_trust_assurance_ops",),
        "Defines bounded application refusal/error carriers.",
    ),
    "file_ops": (
        "application_support",
        (),
        "File-system support retained inside the application boundary.",
    ),
    "debug_export": (
        "experience_delivery",
        ("hpf_reporting_narrative",),
        "Exports diagnostic evidence for inspection.",
    ),
}

NON_COLLAPSE_LAWS = [
    "shannon_python_package != universal_enterprise_data_platform",
    "codebase_analysis_application != horizontal_analytics_product_family",
    "implementation_module != semantic_authority",
    "algorithm_implementation != qualified_method_contract",
    "local_storage_or_query_support != storage_or_query_product",
    "application_kernel != solution_compiler_or_reconciler",
    "Git_or_source_code_observation != universal_source_system_contract",
    "renderer_or_dashboard != analytical_result_meaning",
    "same_campaign_tests != independent_qualification",
]


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def discover_modules() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(SRC.iterdir(), key=lambda item: item.name):
        if path.name.startswith("__pycache__"):
            continue
        if path.is_dir():
            py_files = sorted(path.rglob("*.py"))
            module_name = path.name
            source_kind = "package"
        elif path.suffix == ".py" and path.name != "__init__.py":
            py_files = [path]
            module_name = path.stem
            source_kind = "module"
        else:
            continue
        role, families, rationale = ROLE_RULES.get(
            module_name,
            (
                "application_support",
                (),
                "No independent product or horizontal claim is permitted until an explicit contract and owner are adjudicated.",
            ),
        )
        file_rows = [
            {
                "path": str(source.relative_to(ROOT)),
                "sha256": sha256_file(source),
                "line_count": len(
                    source.read_text(encoding="utf-8", errors="replace").splitlines()
                ),
            }
            for source in py_files
        ]
        rows.append(
            {
                "record_kind": "python_module_placement",
                "module": module_name,
                "source_kind": source_kind,
                "implementation_role": role,
                "application_product_id": APPLICATION_PRODUCT_ID,
                "horizontal_coverage_coordinates": list(families),
                "rationale": rationale,
                "file_count": len(file_rows),
                "line_count": sum(item["line_count"] for item in file_rows),
                "source_files": file_rows,
                "semantic_authority": False,
                "implementation_qualified": False,
                "product_ratified": False,
            }
        )
    return rows


def existing_family_ids() -> set[str]:
    manifest = json.loads((FAMILY_ROOT / "manifest.json").read_text(encoding="utf-8"))
    ids: set[str] = set()
    for shard in manifest["shards"]:
        body = json.loads((FAMILY_ROOT / shard).read_text(encoding="utf-8"))
        ids.update(family["id"] for family in body["families"])
    return ids


def main() -> int:
    modules = discover_modules()
    family_ids = existing_family_ids()
    unknown_families = sorted(
        {
            family_id
            for row in modules
            for family_id in row["horizontal_coverage_coordinates"]
            if family_id not in family_ids
        }
    )
    product = {
        "schema_version": "1.0.0",
        "record_kind": "implementation_product_placement",
        "implementation_id": "implementation.shannon_python.codebase_insight",
        "implementation_root": "src/shannon_insight",
        "application_product": {
            "product_id": APPLICATION_PRODUCT_ID,
            "name": "Software Codebase Intelligence",
            "product_plane": "application_domain_product_candidate",
            "domain": "software_engineering_and_developer_productivity",
            "sovereign_question": "What evidence-backed structural, temporal, semantic, ownership, and operational risks exist in a bounded software codebase, and which findings can be justified without inventing effects or authority?",
            "users_and_jobs": [
                "software engineers inspect architecture, coupling, change risk, and maintainability",
                "engineering leaders inspect codebase health, ownership, and change concentration",
                "reviewers trace findings to source observations, calculations, and retained snapshots",
            ],
            "owned_artifacts": [
                "RepositoryObservationCut",
                "CodeFileIdentity",
                "SyntaxObservation",
                "CodeRelation",
                "TemporalChangeSeries",
                "CodebaseSignal",
                "DiagnosticFinding",
                "AnalysisSnapshot",
                "FindingEvidence",
            ],
            "lifecycle": [
                "DISCOVERED",
                "ADMITTED",
                "OBSERVED",
                "RELATED",
                "ANALYZED",
                "FINDINGS_EMITTED",
                "SNAPSHOT_PUBLISHED",
                "STALE_OR_INVALIDATED",
                "REFUSED_OR_PARTIAL",
            ],
            "negative_charter": [
                "does not own universal source-system, connector, storage, query, semantic-layer, planning, decision, activation, or presentation products",
                "does not promote source-code or Git vocabulary into universal enterprise semantics",
                "does not make algorithm implementations semantic authority or qualification evidence",
                "does not authorize production changes, deployments, or human decisions",
                "does not claim provider portability, vertical acceptance, build readiness, or ratification",
            ],
        },
        "placement_verdict": "RETAIN_AS_APPLICATION_PRODUCT_AND_QUALIFICATION_PROVING_IMPLEMENTATION",
        "placement_rationale": [
            "The package has an application-specific acquisition-to-finding lifecycle and software-domain artifacts.",
            "Its graph, temporal, statistical, semantic, persistence, query, runtime, and experience modules are composed implementation parts, not sovereign horizontal products.",
            "Selected pure modules may qualify against exact abstract contracts only through digest-bound scope, reproducible builds, adversarial execution, and independent appraisal.",
        ],
        "non_collapse_laws": NON_COLLAPSE_LAWS,
        "module_count": len(modules),
        "source_file_count": sum(row["file_count"] for row in modules),
        "source_line_count": sum(row["line_count"] for row in modules),
        "module_crosswalk_path": "research/product_ontology/implementation_placement/shannon-python-module-crosswalk.jsonl",
        "unknown_horizontal_coverage_coordinates": unknown_families,
        "qualification_posture": {
            "status": "UNQUALIFIED_IMPLEMENTATION_CANDIDATE",
            "eligible_candidate_roles": [
                "application proving implementation",
                "method-kernel candidate for exact-scope qualification",
                "software-engineering vertical acceptance fixture",
            ],
            "prohibited_claims": [
                "universal platform implementation",
                "semantic ratification",
                "independent qualification",
                "portable provider offer",
                "executed cross-industry acceptance",
                "build-ready product",
            ],
            "required_next_evidence": [
                "exact product-ontology binding for the application product",
                "exact abstract contract IDs for every extracted reusable library",
                "source, artifact, dependency, toolchain, and configuration digests",
                "deterministic and adversarial exact-scope execution",
                "independent appraisal and a second independently controlled implementation wherever portability is claimed",
                "two unrelated executed vertical acceptances for any promoted horizontal contract",
            ],
        },
        "completion_claim": False,
    }
    crosswalk_text = "".join(json.dumps(row, sort_keys=True) + "\n" for row in modules)
    (HERE / "shannon-python-module-crosswalk.jsonl").write_text(
        crosswalk_text, encoding="utf-8"
    )
    digest = hashlib.sha256(canonical_json(product) + crosswalk_text.encode("utf-8")).hexdigest()
    product["projection_digest"] = f"sha256:{digest}"
    (HERE / "shannon-python-placement.json").write_text(
        json.dumps(product, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    summary = {
        "report_id": "shannon_python_implementation_placement",
        "application_product_id": APPLICATION_PRODUCT_ID,
        "placement_verdict": product["placement_verdict"],
        "module_count": product["module_count"],
        "source_file_count": product["source_file_count"],
        "source_line_count": product["source_line_count"],
        "unknown_horizontal_coverage_coordinate_count": len(unknown_families),
        "implementation_qualified": False,
        "product_ratified": False,
        "completion_claim": False,
        "projection_digest": product["projection_digest"],
    }
    (HERE / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
