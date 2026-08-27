#!/usr/bin/env python3
"""Validate the method/kernel research corpus without trusting its generator.

The structural checks use only the Python standard library.  When ``jsonschema``
is installed, the same run also validates every record against the local and
shared Draft 2020-12 schemas.  A convenient full invocation is:

    uv run --with jsonschema python validate_corpus.py
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent


def validate_manifest() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text())
    assert manifest["completion_claim"] is False
    for name, claim in manifest["files"].items():
        data = (ROOT / name).read_bytes()
        assert len(data) == claim["bytes"] and hashlib.sha256(data).hexdigest() == claim["sha256"], name
ATLAS_ROOT = ROOT.parent.parent


class CorpusError(AssertionError):
    """A deterministic corpus invariant failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CorpusError(message)


def load_json(name: str) -> Any:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def load_jsonl(name: str) -> list[dict[str, Any]]:
    path = ROOT / name
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CorpusError(f"{name}:{line_number}: invalid JSON: {exc}") from exc
        require(isinstance(value, dict), f"{name}:{line_number}: record must be an object")
        rows.append(value)
    require(rows, f"{name}: must not be empty")
    return rows


def unique_index(rows: Iterable[dict[str, Any]], key: str, label: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        value = row.get(key)
        require(isinstance(value, str) and value, f"{label}: missing {key}")
        require(value not in result, f"{label}: duplicate {key} {value}")
        result[value] = row
    return result


def check_refs(owner: str, refs: Any, known: set[str], kind: str, *, allow_empty: bool = True) -> None:
    require(isinstance(refs, list), f"{owner}: {kind} must be an array")
    if not allow_empty:
        require(bool(refs), f"{owner}: {kind} must not be empty")
    require(len(refs) == len(set(refs)), f"{owner}: duplicate {kind}")
    unknown = sorted(set(refs) - known)
    require(not unknown, f"{owner}: unknown {kind}: {unknown}")


def validate_with_jsonschema(file_rows: dict[str, list[dict[str, Any]]]) -> bool:
    try:
        import jsonschema
    except ImportError:
        print("JSON Schema engine unavailable; deterministic structural checks still ran.")
        return False

    schema_map = {
        "sources.jsonl": ROOT / "schema/source.schema.json",
        "method-families.jsonl": ROOT / "schema/method-family.schema.json",
        "implementation-records.jsonl": ROOT / "schema/implementation-record.schema.json",
        "qualification-receipts.jsonl": ROOT / "schema/qualification-receipt.schema.json",
        "artifact-result-contracts.jsonl": ROOT / "schema/artifact-result.schema.json",
        "decision-points.jsonl": ATLAS_ROOT / "compiler/decision-point.schema.json",
        "library-boundaries.jsonl": ATLAS_ROOT / "compiler/library-contribution.schema.json",
        "compiler-requirements-offers.jsonl": ATLAS_ROOT / "compiler/requirement-offer-binding.schema.json",
    }
    checker = jsonschema.FormatChecker()
    for filename, schema_path in schema_map.items():
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validator = jsonschema.Draft202012Validator(schema, format_checker=checker)
        for index, record in enumerate(file_rows[filename], 1):
            errors = sorted(validator.iter_errors(record), key=lambda error: list(error.path))
            if errors:
                detail = "; ".join(
                    f"{'.'.join(map(str, error.path)) or '<root>'}: {error.message}" for error in errors[:5]
                )
                raise CorpusError(f"{filename}:{index}: schema violation: {detail}")
    return True


def main() -> int:
    before_rebuild = {str(path.relative_to(ROOT)): path.read_bytes() for path in ROOT.rglob("*.json*")}
    rebuilt = subprocess.run([sys.executable, str(ROOT / "build_corpus.py")], capture_output=True, text=True, check=False)
    after_rebuild = {str(path.relative_to(ROOT)): path.read_bytes() for path in ROOT.rglob("*.json*")}
    require(rebuilt.returncode == 0 and before_rebuild == after_rebuild, "deterministic rebuild drift or builder failure")
    validate_manifest()
    filenames = [
        "sources.jsonl",
        "decision-points.jsonl",
        "method-families.jsonl",
        "implementation-records.jsonl",
        "library-boundaries.jsonl",
        "compiler-requirements-offers.jsonl",
        "qualification-receipts.jsonl",
        "artifact-result-contracts.jsonl",
        "innovations.jsonl",
    ]
    rows = {name: load_jsonl(name) for name in filenames}
    axes = load_json("classification-axes.json")
    gaps = load_json("gaps.json")

    sources = unique_index(rows["sources.jsonl"], "source_id", "source")
    decisions = unique_index(rows["decision-points.jsonl"], "decision_id", "decision")
    methods = unique_index(rows["method-families.jsonl"], "method_family_id", "method family")
    implementations = unique_index(rows["implementation-records.jsonl"], "record_id", "implementation")
    libraries = unique_index(rows["library-boundaries.jsonl"], "library_id", "library")
    receipts = unique_index(rows["qualification-receipts.jsonl"], "receipt_id", "qualification")
    artifact_contracts = unique_index(
        rows["artifact-result-contracts.jsonl"], "artifact_contract_id", "artifact/result contract"
    )
    innovations = unique_index(rows["innovations.jsonl"], "innovation_id", "innovation")

    compiler_rows = rows["compiler-requirements-offers.jsonl"]
    requirements = unique_index(
        [row for row in compiler_rows if row.get("record_kind") == "capability_requirement"],
        "requirement_id",
        "requirement",
    )
    offers = unique_index(
        [row for row in compiler_rows if row.get("record_kind") == "capability_offer"],
        "offer_id",
        "offer",
    )
    compiler_gaps = unique_index(
        [row for row in compiler_rows if row.get("record_kind") == "compiler_gap"],
        "gap_id",
        "compiler gap",
    )
    require(
        len(requirements) + len(offers) + len(compiler_gaps) == len(compiler_rows),
        "compiler corpus contains an unrecognized record_kind",
    )

    minimums = {
        "authoritative sources": (len(sources), 75),
        "method families": (len(methods), 150),
        "implementation records": (len(implementations), 100),
        "library boundaries": (len(libraries), 20),
        "decision points": (len(decisions), 30),
        "provider offers": (len(offers), 35),
        "qualification profiles": (len(receipts), 14),
        "artifact/result contracts": (len(artifact_contracts), 12),
        "recent innovations": (len(innovations), 15),
    }
    for label, (actual, minimum) in minimums.items():
        require(actual >= minimum, f"{label}: expected at least {minimum}, found {actual}")

    allowed_source_kinds = {
        "standard",
        "official_documentation",
        "official_specification",
        "primary_paper",
        "reference_implementation",
        "regulatory_guidance",
    }
    seen_urls: set[str] = set()
    for source_id, source in sources.items():
        require(source.get("primary_or_official") is True, f"{source_id}: source is not primary/official")
        require(source.get("kind") in allowed_source_kinds, f"{source_id}: unsupported source kind")
        url = source.get("url")
        require(isinstance(url, str) and url.startswith("https://"), f"{source_id}: URL must be HTTPS")
        require(url not in seen_urls, f"{source_id}: duplicate source URL {url}")
        seen_urls.add(url)
        require(bool(source.get("authority_scope")), f"{source_id}: authority scope missing")
        require(bool(source.get("limitations")), f"{source_id}: source limitations missing")

    required_domains = {
        "descriptive",
        "inferential",
        "experimental",
        "causal",
        "forecasting",
        "anomaly_change",
        "process",
        "data_quality",
        "reliability",
        "queue_simulation",
        "operations_research_bridge",
        "graph",
        "spatial",
        "text_search",
        "signal",
        "image",
        "semantic_metric",
    }
    domain_counts = Counter(method["domain_family"] for method in methods.values())
    require(set(domain_counts) == required_domains, f"method domain mismatch: {sorted(set(domain_counts) ^ required_domains)}")
    decision_ids = set(decisions)
    source_ids = set(sources)
    expected_result_states = {"invalid_input", "unsupported", "resource_exhausted", "cancelled"}
    for method_id, method in methods.items():
        require(method.get("llm_dependency") == "none", f"{method_id}: prohibited LLM dependency")
        check_refs(method_id, method.get("decision_refs"), decision_ids, "decision refs", allow_empty=False)
        check_refs(method_id, method.get("evidence_refs"), source_ids, "evidence refs", allow_empty=False)
        require(expected_result_states <= set(method.get("result_states", [])), f"{method_id}: incomplete result algebra")
        bridge_refs = method.get("or_bridge_refs", [])
        require(isinstance(bridge_refs, list), f"{method_id}: or_bridge_refs must be an array")
        if bridge_refs:
            require(
                method["domain_family"] in {"operations_research_bridge", "queue_simulation"},
                f"{method_id}: OR references cross the owned boundary",
            )
            require(all(ref.startswith("or.method.") for ref in bridge_refs), f"{method_id}: malformed OR bridge ref")

    implementation_kinds = Counter(record["record_kind"] for record in implementations.values())
    require(
        set(implementation_kinds) == {"formula", "model", "estimator", "algorithm", "numerical_kernel", "data_kernel"},
        "implementation roles are incomplete or unknown",
    )
    implementation_ids = set(implementations)
    method_ids = set(methods)
    for record_id, record in implementations.items():
        require(record.get("llm_dependency") == "none", f"{record_id}: prohibited LLM dependency")
        check_refs(record_id, record.get("decision_refs"), decision_ids, "decision refs", allow_empty=False)
        check_refs(record_id, record.get("evidence_refs"), source_ids, "evidence refs", allow_empty=False)
        check_refs(record_id, record.get("method_family_refs"), method_ids, "method family refs")
        check_refs(record_id, record.get("kernel_refs"), implementation_ids, "kernel refs")
        if record["record_kind"] in {"formula", "model", "estimator", "algorithm"}:
            require(bool(record["method_family_refs"]), f"{record_id}: semantic implementation has no method family")
        if record["record_kind"] in {"numerical_kernel", "data_kernel"}:
            require(not record["method_family_refs"], f"{record_id}: physical kernel owns analytical semantics")
        for kernel_ref in record["kernel_refs"]:
            require(
                implementations[kernel_ref]["record_kind"] in {"numerical_kernel", "data_kernel"},
                f"{record_id}: kernel ref {kernel_ref} is not a kernel",
            )

    required_anchors = {
        "formula.weighted_mean",
        "model.causal_graph",
        "estimator.doubleml",
        "algorithm.inductive_miner",
        "kernel.fft.dft",
        "kernel.graph.semiring_mxm",
        "kernel.arrow.compute_dispatch",
        "kernel.data.dictionary_encode",
        "kernel.compression.zstd",
        "kernel.compression.snappy",
    }
    require(required_anchors <= implementation_ids, f"missing implementation anchors: {sorted(required_anchors - implementation_ids)}")
    compression_ids = {"kernel.compression.zstd", "kernel.compression.snappy"}
    require(
        all(implementations[record_id]["record_kind"] == "data_kernel" for record_id in compression_ids),
        "compression must remain a physical data-kernel concern",
    )
    require(
        all("compression" not in method_id for method_id in method_ids),
        "compression was incorrectly promoted to an analytical method family",
    )

    library_ids = set(libraries)
    requirement_ids = set(requirements)
    offer_ids = set(offers)
    for library_id, library in libraries.items():
        check_refs(library_id, library.get("decision_refs"), decision_ids, "decision refs", allow_empty=False)
        check_refs(library_id, library.get("evidence_refs"), source_ids, "evidence refs", allow_empty=False)
        check_refs(library_id, library.get("requirement_refs"), requirement_ids, "requirement refs", allow_empty=False)
        check_refs(library_id, library.get("offer_refs"), offer_ids, "offer refs")
        require(bool(library.get("removal_seams")), f"{library_id}: provider removal seam missing")
        if library["library_kind"] in {"semantic_pure", "algorithm_pure", "test_oracle"}:
            require(library["effect_boundary"] == "pure_no_io", f"{library_id}: pure library permits effects")
        if library["library_kind"] == "semantic_pure":
            require(len(library["semantic_owner_refs"]) == 1, f"{library_id}: semantic owner must be singular")
        if library["library_kind"] == "provider_adapter":
            require(bool(library["unsafe_ffi_generated_policy"]), f"{library_id}: adapter lacks unsafe/FFI policy")

    required_process_libraries = {
        "library.method_kernels.process_event_projection",
        "library.method_kernels.process_case_projection",
        "library.method_kernels.process_state_aware_projection",
        "library.method_kernels.process_temporal_graph_projection",
        "library.method_kernels.process_discovery_methods",
        "library.method_kernels.process_conformance_methods",
        "library.method_kernels.process_performance_methods",
    }
    require(
        required_process_libraries <= library_ids,
        f"process projection/analysis boundary closure missing: {sorted(required_process_libraries - library_ids)}",
    )
    required_analytical_split_libraries = {
        "library.method_kernels.probability_distribution_algebra",
        "library.method_kernels.descriptive_statistics",
        "library.method_kernels.inferential_tests_resampling",
        "library.method_kernels.regression_glm_estimators",
        "library.method_kernels.survival_event_history_estimators",
        "library.method_kernels.probabilistic_inference",
        "library.method_kernels.causal_graph_identification",
        "library.method_kernels.causal_effect_estimators",
        "library.method_kernels.causal_refutation_sensitivity",
        "library.method_kernels.time_series_semantics",
        "library.method_kernels.forecast_estimators",
        "library.method_kernels.forecast_evaluation",
        "library.method_kernels.forecast_reconciliation",
        "library.method_kernels.anomaly_baseline",
        "library.method_kernels.anomaly_detectors",
        "library.method_kernels.change_point_detectors",
        "library.method_kernels.analytical_finding_contract",
    }
    require(
        required_analytical_split_libraries <= library_ids,
        f"statistical/causal/forecast/anomaly split missing: {sorted(required_analytical_split_libraries - library_ids)}",
    )
    required_graph_spatial_libraries = {
        "library.method_kernels.graph_semantics",
        "library.method_kernels.graph_traversal_path_methods",
        "library.method_kernels.graph_centrality_methods",
        "library.method_kernels.graph_community_methods",
        "library.method_kernels.graph_semiring_kernel_facade",
        "library.method_kernels.spatial_reference_semantics",
        "library.method_kernels.coordinate_transform_methods",
        "library.method_kernels.vector_geometry_topology",
        "library.method_kernels.raster_grid_methods",
        "library.method_kernels.spatial_statistics_methods",
    }
    require(
        required_graph_spatial_libraries <= library_ids,
        f"graph/spatial split missing: {sorted(required_graph_spatial_libraries - library_ids)}",
    )
    required_experiment_libraries = {
        "library.method_kernels.experiment_protocol_semantics",
        "library.method_kernels.experiment_assignment_state",
        "library.method_kernels.experiment_randomization_methods",
        "library.method_kernels.experiment_exposure_occurrence",
        "library.method_kernels.experiment_analysis_cut_stopping",
    }
    require(
        required_experiment_libraries <= library_ids,
        f"experiment protocol/assignment/exposure/cut split missing: {sorted(required_experiment_libraries - library_ids)}",
    )
    required_document_libraries = {
        "library.method_kernels.document_container_semantics",
        "library.method_kernels.document_content_graph",
        "library.method_kernels.document_parser_adapters",
        "library.method_kernels.document_layout_methods",
        "library.method_kernels.document_ocr_methods",
        "library.method_kernels.document_table_extraction",
        "library.method_kernels.document_form_extraction",
        "library.method_kernels.document_provenance_loss",
        "library.method_kernels.document_classification_methods",
        "library.method_kernels.document_information_extraction",
        "library.method_kernels.document_extraction_evaluation",
    }
    require(
        required_document_libraries <= library_ids,
        f"document extraction split missing: {sorted(required_document_libraries - library_ids)}",
    )

    for requirement_id, requirement in requirements.items():
        require(requirement.get("subject_ref") in library_ids, f"{requirement_id}: unknown subject library")
        require(requirement.get("status") == "declared", f"{requirement_id}: premature requirement status")
        require(requirement.get("fallback_law") == "refuse", f"{requirement_id}: unsafe fallback law")
        require(bool(requirement.get("evidence_gates")), f"{requirement_id}: evidence gates missing")

    for offer_id, offer in offers.items():
        require(offer.get("status") == "declared", f"{offer_id}: unqualified offer claims a stronger status")
        require(offer.get("conformance_receipts") == [], f"{offer_id}: invented conformance receipt")
        check_refs(offer_id, offer.get("decision_refs"), decision_ids, "decision refs", allow_empty=False)
        check_refs(offer_id, offer.get("evidence_refs"), source_ids, "evidence refs", allow_empty=False)
        check_refs(offer_id, offer.get("operation_refs"), implementation_ids, "operation refs", allow_empty=False)
        require(
            all(implementations[ref]["record_kind"] in {"numerical_kernel", "data_kernel"} for ref in offer["operation_refs"]),
            f"{offer_id}: provider offer directly owns a method/formula/estimator",
        )
        require(bool(offer.get("limits")) and bool(offer.get("exclusions")), f"{offer_id}: limits/exclusions missing")
        require(
            set(offer.get("contract_refs", []))
            <= {library_id.replace("library.method_kernels.", "contract.method_kernel.") for library_id in library_ids},
            f"{offer_id}: offer references an unknown concrete contract",
        )

    for gap_id, gap in compiler_gaps.items():
        require(gap.get("status") == "open", f"{gap_id}: compiler gap improperly closed")
        require(gap.get("blocking") is True, f"{gap_id}: unresolved compiler gap is not blocking")
        require(gap.get("subject_ref") in library_ids, f"{gap_id}: unknown subject library")
        require(gap.get("attempted_bindings") == [], f"{gap_id}: invented binding attempt")
        require(bool(gap.get("prohibited_fallbacks")), f"{gap_id}: prohibited fallbacks missing")

    for receipt_id, receipt in receipts.items():
        require(receipt.get("record_kind") == "qualification_profile", f"{receipt_id}: not a qualification profile")
        require(receipt.get("status") == "template_not_executed", f"{receipt_id}: invented qualification result")
        require(receipt.get("results") == [], f"{receipt_id}: unexecuted profile contains results")
        require(receipt.get("subject_ref") in library_ids, f"{receipt_id}: unknown subject library")
        require(bool(receipt.get("fixtures")) and bool(receipt.get("oracles")), f"{receipt_id}: profile is not executable")
        require(any("proves no provider capability" in item for item in receipt.get("limitations", [])), f"{receipt_id}: missing non-claim")

    required_process_profiles = {
        "receipt.method_kernel.process_event_projection",
        "receipt.method_kernel.process_case_projection",
        "receipt.method_kernel.process_state_aware_projection",
        "receipt.method_kernel.process_temporal_graph_projection",
        "receipt.method_kernel.process_discovery",
        "receipt.method_kernel.process_conformance",
        "receipt.method_kernel.process_performance",
    }
    require(
        required_process_profiles <= set(receipts),
        f"process qualification profiles missing: {sorted(required_process_profiles - set(receipts))}",
    )
    required_analytical_split_profiles = {
        "receipt.method_kernel.probability_distribution",
        "receipt.method_kernel.descriptive_statistics",
        "receipt.method_kernel.inferential_tests_resampling",
        "receipt.method_kernel.regression_glm",
        "receipt.method_kernel.survival_event_history",
        "receipt.method_kernel.probabilistic_inference",
        "receipt.method_kernel.causal_identification",
        "receipt.method_kernel.causal_estimation",
        "receipt.method_kernel.causal_refutation",
        "receipt.method_kernel.time_series_semantics",
        "receipt.method_kernel.forecast_estimators",
        "receipt.method_kernel.forecast_evaluation",
        "receipt.method_kernel.forecast_reconciliation",
        "receipt.method_kernel.anomaly_baseline",
        "receipt.method_kernel.anomaly_detection",
        "receipt.method_kernel.change_point_detection",
        "receipt.method_kernel.analytical_finding",
    }
    require(
        required_analytical_split_profiles <= set(receipts),
        f"statistical/causal/forecast/anomaly profiles missing: {sorted(required_analytical_split_profiles - set(receipts))}",
    )
    required_graph_spatial_profiles = {
        "receipt.method_kernel.graph_semantics",
        "receipt.method_kernel.graph_traversal_paths",
        "receipt.method_kernel.graph_centrality",
        "receipt.method_kernel.graph_community",
        "receipt.method_kernel.graph_semiring_kernels",
        "receipt.method_kernel.spatial_reference",
        "receipt.method_kernel.coordinate_transform",
        "receipt.method_kernel.vector_geometry_topology",
        "receipt.method_kernel.raster_grid",
        "receipt.method_kernel.spatial_statistics",
    }
    require(
        required_graph_spatial_profiles <= set(receipts),
        f"graph/spatial profiles missing: {sorted(required_graph_spatial_profiles - set(receipts))}",
    )
    required_experiment_profiles = {
        "receipt.method_kernel.analysis_design",
        "receipt.method_kernel.experiment_protocol",
        "receipt.method_kernel.experiment_assignment_state",
        "receipt.method_kernel.experiment_randomization",
        "receipt.method_kernel.experiment_exposure",
        "receipt.method_kernel.experiment_analysis_cut_stopping",
    }
    require(
        required_experiment_profiles <= set(receipts),
        f"experiment qualification profiles missing: {sorted(required_experiment_profiles - set(receipts))}",
    )
    required_document_profiles = {
        "receipt.method_kernel.document_container",
        "receipt.method_kernel.document_content_graph",
        "receipt.method_kernel.document_parser",
        "receipt.method_kernel.document_layout",
        "receipt.method_kernel.document_ocr",
        "receipt.method_kernel.document_table",
        "receipt.method_kernel.document_form",
        "receipt.method_kernel.document_provenance",
        "receipt.method_kernel.document_classification",
        "receipt.method_kernel.document_information_extraction",
        "receipt.method_kernel.document_extraction_evaluation",
    }
    require(
        required_document_profiles <= set(receipts),
        f"document qualification profiles missing: {sorted(required_document_profiles - set(receipts))}",
    )
    required_provider_offers = {
        "offer.method_kernels.dowhy",
        "offer.method_kernels.econml",
        "offer.method_kernels.sktime",
        "offer.method_kernels.statsforecast",
        "offer.method_kernels.river",
        "offer.method_kernels.lagraph",
        "offer.method_kernels.growthbook",
        "offer.method_kernels.statsig",
        "offer.method_kernels.tika",
        "offer.method_kernels.pdfbox",
        "offer.method_kernels.tesseract",
        "offer.method_kernels.table_transformer",
        "offer.method_kernels.spacy",
        "offer.method_kernels.opennlp",
    }
    require(
        required_provider_offers <= set(offers),
        f"independent provider observations missing: {sorted(required_provider_offers - set(offers))}",
    )

    known_contracts = {
        library_id.replace("library.method_kernels.", "contract.method_kernel.") for library_id in library_ids
    }
    required_artifact_kinds = {
        "study_design",
        "estimand",
        "resolved_method_plan",
        "fitted_model",
        "fitted_transform",
        "forecast",
        "simulation_run",
        "search_index",
        "process_model",
        "analytical_result",
        "evaluation_receipt",
        "evidence_bundle",
    }
    require(
        {record["artifact_kind"] for record in artifact_contracts.values()} == required_artifact_kinds,
        "artifact/result lifecycle coverage is incomplete or unknown",
    )
    for artifact_id, artifact in artifact_contracts.items():
        check_refs(artifact_id, artifact.get("producer_contracts"), known_contracts, "producer contracts", allow_empty=False)
        check_refs(artifact_id, artifact.get("decision_refs"), decision_ids, "decision refs", allow_empty=False)
        check_refs(artifact_id, artifact.get("evidence_refs"), source_ids, "evidence refs", allow_empty=False)
        require(expected_result_states <= set(artifact.get("result_states", [])), f"{artifact_id}: incomplete result algebra")
        require(bool(artifact.get("provenance_requirements")), f"{artifact_id}: provenance requirements missing")
        require(bool(artifact.get("invalidation_triggers")), f"{artifact_id}: invalidation law missing")
        require(bool(artifact.get("replay_contract")), f"{artifact_id}: replay contract missing")
        require(bool(artifact.get("portability", {}).get("conditions")), f"{artifact_id}: portability conditions missing")

    for innovation_id, innovation in innovations.items():
        require(2021 <= innovation.get("year", 0) <= 2026, f"{innovation_id}: outside the requested 2021-2026 window")
        require(innovation.get("non_llm") is True, f"{innovation_id}: LLM/generative innovation admitted")
        check_refs(innovation_id, innovation.get("evidence_refs"), source_ids, "evidence refs", allow_empty=False)
        require(bool(innovation.get("limits")), f"{innovation_id}: innovation limits missing")
        require(bool(innovation.get("compiler_implications")), f"{innovation_id}: compiler implications missing")

    require(isinstance(axes, dict) and isinstance(axes.get("axes"), list), "classification axes malformed")
    require(len(axes["axes"]) >= 18, "classification coverage is too narrow")
    axis_ids = [axis.get("axis_id") for axis in axes["axes"]]
    require(len(axis_ids) == len(set(axis_ids)), "duplicate classification axis")
    require(
        {"semantic_role", "analytical_purpose", "evidence_design", "data_structure", "artifact_state", "ownership_boundary"} <= set(axis_ids),
        "classification lacks required orthogonal axes",
    )
    require(bool(axes.get("unit_law")), "classification unit law missing")
    require(bool(axes.get("forbidden_cross_product_examples")), "anti-cross-product examples missing")

    require(gaps.get("completion_claim") is False, "research corpus must not claim universal completion")
    open_gaps = gaps.get("open_gaps")
    require(isinstance(open_gaps, list) and len(open_gaps) >= 12, "known gaps are missing or too narrow")
    gap_ids = {gap.get("gap_id") for gap in open_gaps}
    require(len(gap_ids) == len(open_gaps), "duplicate open gap")
    require(
        {
            "enumeration_open_world",
            "theorem_preconditions",
            "executed_receipts",
            "or_crosswalk",
            "study_to_method_selection",
            "operation_crosswalk",
            "two_verticals",
        }
        <= gap_ids,
        "open-world or adjudication gates are incomplete",
    )

    schema_validated = validate_with_jsonschema(rows)

    print("METHOD-KERNEL CORPUS VALID")
    print(
        json.dumps(
            {
                "sources": len(sources),
                "method_families": len(methods),
                "domains": dict(sorted(domain_counts.items())),
                "implementations": dict(sorted(implementation_kinds.items())),
                "library_boundaries": len(libraries),
                "decision_points": len(decisions),
                "requirements": len(requirements),
                "provider_offers": len(offers),
                "compiler_gaps": len(compiler_gaps),
                "qualification_profiles_unexecuted": len(receipts),
                "artifact_result_contracts": len(artifact_contracts),
                "innovations_2021_2026": len(innovations),
                "json_schema_validated": schema_validated,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CorpusError as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
