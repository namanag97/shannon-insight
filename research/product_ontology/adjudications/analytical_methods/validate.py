#!/usr/bin/env python3
"""Validate the analytical-method/product boundary adjudication bundle."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict

from build_bundle import HERE, OUTPUTS, load_source, materialize
from experimentation_enrichment import (
    ALL_KEYS as EXPERIMENT_KEYS,
    DDD_FIELDS as EXPERIMENT_DDD_FIELDS,
    EXACT as EXPERIMENT_EXACT,
    GAP_KEYS as EXPERIMENT_GAP_KEYS,
    EXACT_COMPILER_OVERRIDES as EXPERIMENT_OVERRIDES,
    PRODUCT as EXPERIMENT_PRODUCT,
    PRODUCT_FIELDS as EXPERIMENT_PRODUCT_FIELDS,
    local_library as experiment_local_library,
)
from forecasting_enrichment import (
    ALL_KEYS as FORECAST_KEYS,
    DDD_FIELDS as FORECAST_DDD_FIELDS,
    EXACT as FORECAST_EXACT,
    EXACT_COMPILER_OVERRIDES as FORECAST_OVERRIDES,
    GAP_KEYS as FORECAST_GAP_KEYS,
    PRODUCT as FORECAST_PRODUCT,
    PRODUCT_FIELDS as FORECAST_PRODUCT_FIELDS,
    local_library as forecast_local_library,
)
from geospatial_enrichment import (
    ALL_KEYS as GEOSPATIAL_KEYS,
    DDD_FIELDS as GEOSPATIAL_DDD_FIELDS,
    EXACT as GEOSPATIAL_EXACT,
    EXACT_COMPILER_OVERRIDES as GEOSPATIAL_OVERRIDES,
    GAP_KEYS as GEOSPATIAL_GAP_KEYS,
    PRODUCT as GEOSPATIAL_PRODUCT,
    PRODUCT_FIELDS as GEOSPATIAL_PRODUCT_FIELDS,
    local_library as geospatial_local_library,
)
from graph_workbench_enrichment import (
    CONCRETE as GRAPH_WORKBENCH_CONCRETE,
    DDD_FIELDS as GRAPH_WORKBENCH_DDD_FIELDS,
    KEYS as GRAPH_WORKBENCH_KEYS,
    PRODUCT as GRAPH_WORKBENCH_PRODUCT,
    PRODUCT_FIELDS as GRAPH_WORKBENCH_PRODUCT_FIELDS,
    local_library as graph_workbench_local_library,
)
from optimization_enrichment import (
    CONCRETE as OPTIMIZATION_CONCRETE,
    DDD_FIELDS as OPTIMIZATION_DDD_FIELDS,
    PRODUCT as OPTIMIZATION_PRODUCT,
    PRODUCT_FIELDS,
    local_library as optimization_local_library,
    source_bytes as enriched_source_bytes,
)
from planning_enrichment import (
    DDD_FIELDS as PLANNING_DDD_FIELDS,
    KEYS as PLANNING_KEYS,
    PRODUCT as PLANNING_PRODUCT,
    PRODUCT_FIELDS as PLANNING_PRODUCT_FIELDS,
    local_library as planning_local_library,
)
from project_controls_enrichment import (
    DDD_FIELDS as PROJECT_CONTROLS_DDD_FIELDS,
    KEYS as PROJECT_CONTROLS_KEYS,
    PRODUCT as PROJECT_CONTROLS_PRODUCT,
    PRODUCT_FIELDS as PROJECT_CONTROLS_PRODUCT_FIELDS,
    local_library as project_controls_local_library,
)
from process_mining_enrichment import (
    CONCRETE as PROCESS_CONCRETE,
    DDD_FIELDS as PROCESS_DDD_FIELDS,
    PRODUCT as PROCESS_PRODUCT,
    PRODUCT_FIELDS as PROCESS_PRODUCT_FIELDS,
    local_library as process_local_library,
)
from simulation_enrichment import (
    CONCRETE as SIMULATION_CONCRETE,
    DDD_FIELDS as SIMULATION_DDD_FIELDS,
    PRODUCT as SIMULATION_PRODUCT,
    PRODUCT_FIELDS as SIMULATION_PRODUCT_FIELDS,
    local_library as simulation_local_library,
)


ID = re.compile(r"^[a-z][a-z0-9_]*(?:[.-][a-z0-9_]+)+$")
AXES = {"user", "job", "adoption", "semantics", "authority", "lifecycle", "operation", "economics", "interface", "market_evidence"}


def rows(name: str) -> list[dict]:
    return [json.loads(line) for line in (HERE / name).read_text(encoding="utf-8").splitlines() if line.strip()]


def identity(row: dict) -> str:
    for key in ("source_id", "artifact_id", "decision_id", "meaning_id", "library_id", "requirement_id", "offer_id", "binding_map_id", "gap_id", "relation_id", "legacy_ref", "test_id", "dossier_id", "kind"):
        if key in row:
            return str(row[key])
    return "<missing>"


def main() -> int:
    errors: list[str] = []

    def require(ok: bool, message: str) -> None:
        if not ok:
            errors.append(message)

    source = load_source()
    require((HERE / "source.json").read_bytes() == enriched_source_bytes(), "source differs from canonical optimization enrichment")
    payloads, expected_manifest = materialize(source)
    manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
    metamodel = json.loads((HERE / "metamodel.json").read_text(encoding="utf-8"))
    require(manifest == expected_manifest, "manifest differs from deterministic projection")
    for filename, content in payloads.items():
        path = HERE / filename
        require(path.is_file() and path.read_bytes() == content, f"missing or stale {filename}")
    for filename, expected in manifest.get("file_sha256", {}).items():
        path = HERE / filename
        if path.is_file():
            require(hashlib.sha256(path.read_bytes()).hexdigest() == expected, f"digest mismatch {filename}")

    registry = rows("registry.jsonl")
    require(Counter(row["record_kind"] for row in registry) == Counter(manifest["counts"]), "manifest counts differ")
    keys = [(row["record_kind"], identity(row)) for row in registry]
    require(len(keys) == len(set(keys)), "duplicate record identity")
    for row in registry:
        ident = identity(row)
        pattern = r"^[a-z][a-z0-9_]*$" if row["record_kind"] == "artifact_kind_definition" else ID.pattern
        require(bool(re.fullmatch(pattern, ident)), f"invalid identity {ident}")

    data = {section: rows(filename) for section, filename in OUTPUTS.items()}
    evidence = {row["source_id"]: row for row in data["sources"]}
    artifacts = {row["artifact_id"]: row for row in data["artifacts"]}
    libraries = {row["library_id"]: row for row in data["libraries"]}
    nodes = set(artifacts) | set(libraries)
    require(len(evidence) >= 25, "fewer than twenty-five primary/official sources")
    require(all(row.get("claim") and row.get("scope_limit") and row.get("uri", "").startswith("https://") for row in evidence.values()), "unscoped evidence")

    kinds = {row["kind"] for row in data["artifact_kinds"]}
    require(kinds == set(metamodel["artifact_kinds"]), "artifact-kind drift")
    for ident, row in artifacts.items():
        require(row["kind"] in kinds, f"unknown kind {ident}")
        require(all(ref in evidence for ref in row.get("evidence_refs", [])), f"unresolved evidence {ident}")
        if row["kind"] == "product":
            require(row["adoption_unit"] and row["operated"], f"product boundary flags missing {ident}")
        if row["kind"] in {"suite", "architecture_pattern"}:
            require(row.get("semantic_owner_ref") is None, f"suite/pattern claims meaning {ident}")
        owner = row.get("semantic_owner_ref")
        if owner:
            require(owner in artifacts and artifacts[owner]["kind"] == "semantic_contract", f"bad semantic owner {ident}")

    product_ids = {ident for ident, row in artifacts.items() if row["kind"] == "product"}
    expected_products = {
        "product.experimentation_platform", "product.forecasting_workbench",
        "product.optimization_solver", "product.process_mining_workbench",
        "product.geospatial_workbench", "product.simulation_environment",
        "product.graph_analysis_workbench",
        "product.integrated_planning_workbench",
        "product.project_portfolio_controls",
    }
    require(product_ids == expected_products, "analytical product identity set drifted")

    decisions = {row["decision_id"]: row for row in data["boundary_decisions"]}
    decided_products: set[str] = set()
    for ident, row in decisions.items():
        require(row["subject_ref"] in nodes, f"unknown decision subject {ident}")
        require(all(ref in evidence for ref in row["evidence_refs"]), f"unresolved decision evidence {ident}")
        if row["subject_ref"] in product_ids:
            decided_products.add(row["subject_ref"])
            require(set(row.get("split_test", {})) == AXES, f"incomplete split test {ident}")
            split = row.get("split_test", {})
            require(all(axis.get("score") in {0, 1, 2} and axis.get("evidence_refs") for axis in split.values()), f"invalid split evidence {ident}")
            total = sum(axis["score"] for axis in split.values())
            require(17 <= total <= 20, f"strong score out of range {ident}={total}")
    require(decided_products == product_ids, "not every product is adjudicated")
    required_decisions = {
        "decision.methods.statistical_method_not_product", "decision.methods.causal_method_split",
        "decision.methods.anomaly_not_product", "decision.methods.graph_not_product",
        "decision.methods.text_media_not_products", "decision.methods.library_product_split",
        "decision.methods.ai_prefix",
    }
    require(required_decisions <= set(decisions), "constitutional analytical decisions missing")

    optimizer = artifacts[OPTIMIZATION_PRODUCT]
    require(all(optimizer.get(field) not in (None, [], {}) for field in PRODUCT_FIELDS), "optimization product truth incomplete")
    require(optimizer["automation_modality"]["default"] == "DETERMINISTIC_CORE_ONLY", "ambient model/agent default in optimizer")
    require("removal_law" in optimizer["automation_modality"] and "hard_work_law" in optimizer["automation_modality"], "optimizer automation doctrine incomplete")
    process_product = artifacts[PROCESS_PRODUCT]
    require(all(process_product.get(field) not in (None, [], {}) for field in PROCESS_PRODUCT_FIELDS), "process product truth incomplete")
    require(process_product["automation_modality"]["default"] == "DETERMINISTIC_CORE_ONLY", "ambient model/agent default in process mining")
    require("removal_law" in process_product["automation_modality"] and "hard_work_law" in process_product["automation_modality"], "process automation doctrine incomplete")
    simulation_product = artifacts[SIMULATION_PRODUCT]
    require(all(simulation_product.get(field) not in (None, [], {}) for field in SIMULATION_PRODUCT_FIELDS), "simulation product truth incomplete")
    require(simulation_product["automation_modality"]["default"] == "DETERMINISTIC_CORE_ONLY", "ambient model/agent default in simulation")
    require("removal_law" in simulation_product["automation_modality"] and "hard_work_law" in simulation_product["automation_modality"], "simulation automation doctrine incomplete")
    forecast_product = artifacts[FORECAST_PRODUCT]
    require(all(forecast_product.get(field) not in (None, [], {}) for field in FORECAST_PRODUCT_FIELDS), "forecast product truth incomplete")
    require(forecast_product["automation_modality"]["default"] == "DETERMINISTIC_CORE_ONLY", "ambient model/agent default in forecasting")
    require("removal_law" in forecast_product["automation_modality"] and "hard_work_law" in forecast_product["automation_modality"], "forecast automation doctrine incomplete")
    experiment_product = artifacts[EXPERIMENT_PRODUCT]
    require(all(experiment_product.get(field) not in (None, [], {}) for field in EXPERIMENT_PRODUCT_FIELDS), "experiment product truth incomplete")
    require(experiment_product["automation_modality"]["default"] == "DETERMINISTIC_CORE_ONLY", "ambient model/agent default in experimentation")
    require("removal_law" in experiment_product["automation_modality"] and "hard_work_law" in experiment_product["automation_modality"], "experiment automation doctrine incomplete")
    geospatial_product = artifacts[GEOSPATIAL_PRODUCT]
    require(all(geospatial_product.get(field) not in (None, [], {}) for field in GEOSPATIAL_PRODUCT_FIELDS), "geospatial product truth incomplete")
    require(geospatial_product["automation_modality"]["default"] == "DETERMINISTIC_CORE_ONLY", "ambient model/agent default in geospatial")
    require("removal_law" in geospatial_product["automation_modality"] and "hard_work_law" in geospatial_product["automation_modality"], "geospatial automation doctrine incomplete")
    graph_workbench_product = artifacts[GRAPH_WORKBENCH_PRODUCT]
    require(all(graph_workbench_product.get(field) not in (None, [], {}) for field in GRAPH_WORKBENCH_PRODUCT_FIELDS), "graph workbench product truth incomplete")
    require(graph_workbench_product["automation_modality"]["default"] == "DETERMINISTIC_CORE_ONLY", "ambient model/agent default in graph workbench")
    require("removal_law" in graph_workbench_product["automation_modality"] and "hard_work_law" in graph_workbench_product["automation_modality"], "graph workbench automation doctrine incomplete")
    planning_product = artifacts[PLANNING_PRODUCT]
    require(all(planning_product.get(field) not in (None, [], {}) for field in PLANNING_PRODUCT_FIELDS), "planning product truth incomplete")
    require(planning_product["automation_modality"]["default"] == "DETERMINISTIC_CORE_ONLY", "ambient model/agent default in planning")
    require("removal_law" in planning_product["automation_modality"] and "hard_work_law" in planning_product["automation_modality"], "planning automation doctrine incomplete")
    project_controls_product = artifacts[PROJECT_CONTROLS_PRODUCT]
    require(all(project_controls_product.get(field) not in (None, [], {}) for field in PROJECT_CONTROLS_PRODUCT_FIELDS), "project controls product truth incomplete")
    require(project_controls_product["automation_modality"]["default"] == "DETERMINISTIC_CORE_ONLY", "ambient model/agent default in project controls")
    require("removal_law" in project_controls_product["automation_modality"] and "hard_work_law" in project_controls_product["automation_modality"], "project controls automation doctrine incomplete")

    graph: dict[str, list[str]] = defaultdict(list)
    for ident, row in libraries.items():
        require(row["owner_ref"] in artifacts and artifacts[row["owner_ref"]]["kind"] == "semantic_contract", f"bad library owner {ident}")
        for field in ("types", "operations", "decisions", "invariants", "refusals", "provides"):
            require(bool(row.get(field)), f"empty {field} {ident}")
        for ref in row["provides"]:
            require(ref in artifacts and artifacts[ref]["kind"] == "capability", f"bad capability {ident}:{ref}")
        for ref in row["dependencies"]:
            require(ref in libraries, f"unknown dependency {ident}:{ref}")
            graph[ident].append(ref)
        require(all(ref in evidence for ref in row["evidence_refs"]), f"unresolved library evidence {ident}")
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            errors.append(f"library cycle {node}")
            return
        if node in visited:
            return
        visiting.add(node)
        for dep in graph[node]:
            visit(dep)
        visiting.remove(node)
        visited.add(node)

    for node in libraries:
        visit(node)

    for row in data["ownership"]:
        require(row["owner_ref"] in artifacts and artifacts[row["owner_ref"]]["kind"] == "semantic_contract", f"bad meaning owner {row['meaning_id']}")
        require(row.get("invariant"), f"missing meaning invariant {row['meaning_id']}")
        require(all(ref in artifacts for ref in row["must_not_be_owned_by"]), f"bad excluded owner {row['meaning_id']}")
    for row in data["requirements"]:
        require(row["consumer_ref"] in product_ids and row["capability_ref"] in artifacts, f"bad requirement {row['requirement_id']}")
        require(row["status"] == "unbound" and row["minimum_qualified_offers"] >= 1, f"dishonest requirement binding {row['requirement_id']}")
    for row in data["offers"]:
        require(row["provider_ref"] in artifacts and artifacts[row["provider_ref"]]["kind"] == "implementation", f"bad offer provider {row['offer_id']}")
        require(row["qualified_implementation_count"] == 0 and row["portable"] is False, f"unverified offer promoted {row['offer_id']}")
        require(all(ref in artifacts and artifacts[ref]["kind"] == "capability" for ref in row["capability_refs"]), f"bad offered capability {row['offer_id']}")
        require(all(ref in evidence for ref in row["evidence_refs"]), f"unresolved offer evidence {row['offer_id']}")

    atlas = HERE.parents[2] / "domain_atlas"
    method_libraries = {
        row["library_id"]
        for row in (
            json.loads(line)
            for line in (atlas / "universes/method_kernels/library-boundaries.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }
    method_requirements = {
        row["requirement_id"]
        for row in (
            json.loads(line)
            for line in (atlas / "universes/method_kernels/compiler-requirements-offers.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
        if row.get("record_kind") == "capability_requirement"
    }
    or_libraries = {
        row["library_id"]
        for row in (
            json.loads(line)
            for line in (atlas / "universes/operations_research/library-boundaries.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }
    or_requirements = {
        row["requirement_id"]
        for row in (
            json.loads(line)
            for line in (atlas / "universes/operations_research/compiler-requirements-offers.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
        if row.get("record_kind") == "capability_requirement"
    }
    eiac_libraries = {
        row["library_id"]
        for row in (
            json.loads(line)
            for line in (atlas / "universes/experiment_integrity_analysis_conclusion/library-contracts.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }
    eiac_compiler_rows = [
        json.loads(line)
        for line in (atlas / "universes/experiment_integrity_analysis_conclusion/compiler-contracts.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    eiac_requirements = {row["requirement_id"] for row in eiac_compiler_rows if row.get("record_kind") == "capability_requirement"}
    eiac_profiles = {
        row["receipt_id"]
        for row in (
            json.loads(line)
            for line in (atlas / "universes/experiment_integrity_analysis_conclusion/qualification-profiles.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }
    fgl_libraries = {
        row["library_id"]
        for row in (
            json.loads(line)
            for line in (atlas / "universes/forecast_governance_lifecycle/library-contracts.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }
    fgl_compiler_rows = [
        json.loads(line)
        for line in (atlas / "universes/forecast_governance_lifecycle/compiler-contracts.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    fgl_requirements = {row["requirement_id"] for row in fgl_compiler_rows if row.get("record_kind") == "capability_requirement"}
    fgl_profiles = {
        row["receipt_id"]
        for row in (
            json.loads(line)
            for line in (atlas / "universes/forecast_governance_lifecycle/qualification-profiles.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }
    gsw_libraries = {
        row["library_id"]
        for row in (
            json.loads(line)
            for line in (atlas / "universes/geospatial_specialized_workbench/library-contracts.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }
    gsw_compiler_rows = [json.loads(line) for line in (atlas / "universes/geospatial_specialized_workbench/compiler-contracts.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    gsw_requirements = {row["requirement_id"] for row in gsw_compiler_rows if row.get("record_kind") == "capability_requirement"}
    gsw_profiles = {row["receipt_id"] for row in (json.loads(line) for line in (atlas / "universes/geospatial_specialized_workbench/qualification-profiles.jsonl").read_text(encoding="utf-8").splitlines() if line.strip())}
    qualification_profiles = {
        row["receipt_id"]
        for row in (
            json.loads(line)
            for line in (atlas / "universes/method_kernels/qualification-receipts.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }
    qualification_profiles |= {
        row["receipt_id"]
        for row in (
            json.loads(line)
            for line in (atlas / "universes/operations_research/qualification-receipts.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }
    qualification_profiles |= eiac_profiles
    qualification_profiles |= fgl_profiles
    qualification_profiles |= gsw_profiles
    core_libraries = method_libraries | or_libraries | eiac_libraries | fgl_libraries | gsw_libraries
    core_requirements = method_requirements | or_requirements | eiac_requirements | fgl_requirements | gsw_requirements
    extension_libraries = {
        row["library_id"]
        for row in (
            json.loads(line)
            for line in (atlas / "universes/model_agent_extension/library-boundaries.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }
    extension_compiler_rows = [
        json.loads(line)
        for line in (atlas / "universes/model_agent_extension/compiler-requirements-offers.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    extension_requirements = {
        row["requirement_id"] for row in extension_compiler_rows if row.get("record_kind") == "capability_requirement"
    }
    extension_offers = {
        row["offer_id"]: row for row in extension_compiler_rows if row.get("record_kind") == "capability_offer"
    }
    extension_profiles = {
        row["receipt_id"]
        for row in (
            json.loads(line)
            for line in (atlas / "universes/model_agent_extension/qualification-receipts.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }
    qualification_profiles |= extension_profiles
    binding_maps = {row["binding_map_id"]: row for row in data["binding_maps"]}
    binding_gaps = {row["gap_id"]: row for row in data["binding_gaps"]}
    require(len(binding_maps) == len(libraries) == 65 + len(PLANNING_KEYS) + len(PROJECT_CONTROLS_KEYS), "every abstract analytical library group must have exactly one binding map")
    require({row["abstract_library_ref"] for row in binding_maps.values()} == set(libraries), "analytical binding-map coverage drift")
    expected_graph_gap_ids = {
        f"gap.analytics_graph_workbench.{key}"
        for key in GRAPH_WORKBENCH_KEYS if not GRAPH_WORKBENCH_CONCRETE[key]
    }
    expected_planning_gap_ids = {f"gap.analytics_planning.{key}" for key in PLANNING_KEYS}
    expected_project_controls_gap_ids = {f"gap.project_controls.{key}" for key in PROJECT_CONTROLS_KEYS}
    require(set(binding_gaps) == expected_graph_gap_ids | expected_planning_gap_ids | expected_project_controls_gap_ids, "analytical binding gaps are not the exact graph-workbench, integrated-planning and project-controls vacancies")
    require(
        len(extension_offers) == 6
        and all(row.get("status") == "declared" and row.get("conformance_receipts") == [] for row in extension_offers.values()),
        "optional extension provider observations claim qualification or drifted",
    )
    allowed_bindability = {
        "structurally_bindable_unqualified",
        "structurally_partial_blocking_gap",
        "optional_extension_structurally_mapped",
    }
    for ident, row in binding_maps.items():
        require(row.get("product_refs") == libraries[row["abstract_library_ref"]].get("product_refs"), f"binding/library product attribution drift {ident}")
        require(row["bindability"] in allowed_bindability, f"unknown bindability {ident}")
        require(row["status"] == "candidate_not_bound", f"binding map falsely claims binding {ident}")
        require(row["minimum_qualified_implementations_per_required_contract"] >= 1, f"qualification gate missing {ident}")
        require(row["portable_claim_minimum_independent_implementations"] >= 2, f"portable gate too weak {ident}")
        require(bool(row["composition_law"]), f"composition law missing {ident}")
        require(bool(row["substitution_law"]), f"substitution law missing {ident}")
        require(row["cross_provider_differential_required"] is True, f"cross-provider differential gate missing {ident}")
        require(bool(row["fallback_law"]), f"fallback law missing {ident}")
        require(set(row["qualification_profile_refs"]) <= qualification_profiles, f"unknown qualification profile {ident}")
        refs = set(row["concrete_library_refs"])
        if row["modality_posture"] == "optional":
            require(row["abstract_library_ref"] == "library.analytical_assistance_port", f"optional modality leaked into core {ident}")
            require(refs <= extension_libraries and refs, f"assistance map contains non-extension libraries {ident}")
            require(set(row["concrete_requirement_refs"]) <= extension_requirements and row["concrete_requirement_refs"], f"missing or invented extension requirements {ident}")
            require(set(row["qualification_profile_refs"]) <= extension_profiles and row["qualification_profile_refs"], f"missing or invented extension qualification profile {ident}")
            require("without_weakening_core" in row["fallback_law"], f"assistance fallback weakens core {ident}")
        else:
            require(row["modality_posture"] == "deterministic_core", f"unknown core modality {ident}")
            require(refs <= core_libraries, f"core map contains unknown concrete libraries {ident}")
            require(set(row["concrete_requirement_refs"]) <= core_requirements, f"unknown concrete requirement {ident}")
            if row["bindability"] == "structurally_bindable_unqualified":
                require(bool(refs), f"structurally bindable core map lacks a concrete library {ident}")
                require(bool(row["qualification_profile_refs"]), f"structurally bindable core map lacks a qualification profile {ident}")
            elif refs:
                require(bool(row["qualification_profile_refs"]), f"partially mapped core map hides qualification profiles {ident}")
            else:
                require(not row["concrete_requirement_refs"] and not row["qualification_profile_refs"], f"unmapped core gap invents concrete requirements or qualification {ident}")
            require(row["fallback_law"] == "refuse", f"core map permits silent fallback {ident}")
        gap_refs = set(row["blocking_gap_refs"])
        require(gap_refs <= set(binding_gaps), f"unknown blocking gap {ident}")
        if row["modality_posture"] == "optional":
            require(not gap_refs, f"optional extension has a structural blocking gap {ident}")
        elif row["bindability"] == "structurally_bindable_unqualified":
            require(not gap_refs, f"structurally bindable map has blocking gaps {ident}")
        else:
            require(bool(gap_refs), f"partial/extension map hides its gap {ident}")
    for gap_id, row in binding_gaps.items():
        require(row["status"] == "open" and row["missing_contracts"], f"invalid gap {gap_id}")
        require(set(row["abstract_library_refs"]) <= set(libraries), f"gap references unknown abstract library {gap_id}")
        require(row["compiler_disposition"], f"gap lacks compiler disposition {gap_id}")

    media_map = binding_maps["binding.analytics.media_signal"]
    require(
        {"library.method_kernels.signal_methods", "library.method_kernels.image_methods"}
        <= set(media_map["concrete_library_refs"]),
        "media/signal abstract group did not split into signal and image contracts",
    )
    text_map = binding_maps["binding.analytics.text"]
    require(
        {
            "library.method_kernels.text_semantics",
            "library.method_kernels.search_methods",
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
        <= set(text_map["concrete_library_refs"])
        and text_map["bindability"] == "structurally_bindable_unqualified"
        and not text_map["blocking_gap_refs"],
        "text/search/document extraction boundaries collapsed",
    )
    require(
        "binding.analytics.process_projection" not in binding_maps
        and "binding.analytics.process_analysis" not in binding_maps
        and "binding.analytics.simulation" not in binding_maps
        and "binding.analytics.forecasting" not in binding_maps
        and "binding.analytics.experiment_assignment" not in binding_maps
        and "binding.analytics.geospatial" not in binding_maps,
        "retired broad process, simulation, forecasting, experimentation or geospatial facade bindings survived",
    )
    required_closed_analytical_splits = {
        "binding.analytics.statistical_inference": {
            "library.method_kernels.probability_distribution_algebra",
            "library.method_kernels.descriptive_statistics",
            "library.method_kernels.inferential_tests_resampling",
            "library.method_kernels.regression_glm_estimators",
            "library.method_kernels.survival_event_history_estimators",
            "library.method_kernels.probabilistic_inference",
        },
        "binding.analytics.causal_inference": {
            "library.method_kernels.causal_graph_identification",
            "library.method_kernels.causal_effect_estimators",
            "library.method_kernels.causal_refutation_sensitivity",
        },
        "binding.analytics.anomaly_change": {
            "library.method_kernels.anomaly_baseline",
            "library.method_kernels.anomaly_detectors",
            "library.method_kernels.change_point_detectors",
            "library.method_kernels.analytical_finding_contract",
        },
        "binding.analytics.graph": {
            "library.method_kernels.graph_semantics",
            "library.method_kernels.graph_traversal_path_methods",
            "library.method_kernels.graph_centrality_methods",
            "library.method_kernels.graph_community_methods",
            "library.method_kernels.graph_semiring_kernel_facade",
        },
    }
    for map_id, required_refs in required_closed_analytical_splits.items():
        row = binding_maps[map_id]
        require(
            required_refs <= set(row["concrete_library_refs"])
            and row["bindability"] == "structurally_bindable_unqualified"
            and not row["blocking_gap_refs"],
            f"analytical concrete-library split regressed: {map_id}",
        )
    forbidden_facade_bindings = {
        "binding.analytics.statistical_inference": "library.method_kernels.statistical_estimators",
        "binding.analytics.causal_inference": "library.method_kernels.causal_methods",
        "binding.analytics.graph": "library.method_kernels.graph_methods",
    }
    for map_id, facade_ref in forbidden_facade_bindings.items():
        require(
            facade_ref not in binding_maps[map_id]["concrete_library_refs"],
            f"coarse compatibility facade used as exact binding: {map_id}",
        )
    optimizer_libraries = {optimization_local_library(ref) for ref in OPTIMIZATION_CONCRETE}
    optimizer_maps = {
        row["abstract_library_ref"]: row
        for row in binding_maps.values()
        if OPTIMIZATION_PRODUCT in row.get("product_refs", [])
    }
    require(set(optimizer_maps) == optimizer_libraries and len(optimizer_maps) == 9, "optimizer product-library map coverage drift")
    require({row["concrete_library_refs"][0] for row in optimizer_maps.values()} == set(OPTIMIZATION_CONCRETE), "optimizer exact concrete-library split drift")
    require("library.operations_research.decision_problem_semantics" not in {ref for row in optimizer_maps.values() for ref in row["concrete_library_refs"]}, "solver product absorbed business decision-problem semantics")
    optimizer_requirements = {row["capability_ref"] for row in data["requirements"] if row["consumer_ref"] == OPTIMIZATION_PRODUCT}
    optimizer_provides = {ref for ident in optimizer_libraries for ref in libraries[ident]["provides"]}
    require(optimizer_requirements == optimizer_provides and len(optimizer_requirements) == 10, "optimizer requirement/library capability coverage drift")

    process_libraries = {process_local_library(ref) for ref in PROCESS_CONCRETE}
    process_maps = {
        row["abstract_library_ref"]: row
        for row in binding_maps.values()
        if PROCESS_PRODUCT in row.get("product_refs", [])
    }
    require(set(process_maps) == process_libraries and len(process_maps) == 7, "process product-library map coverage drift")
    require({row["concrete_library_refs"][0] for row in process_maps.values()} == set(PROCESS_CONCRETE), "process exact concrete-library split drift")
    imported_process_support = {"artifact_envelope", "result_algebra", "provider_qualification"}
    require(
        not any(
            any(term in ref for term in imported_process_support)
            for row in process_maps.values()
            for ref in row["concrete_library_refs"]
        ),
        "process product absorbed generic artifact/result/qualification support",
    )
    process_requirements = {row["capability_ref"] for row in data["requirements"] if row["consumer_ref"] == PROCESS_PRODUCT}
    process_provides = {ref for ident in process_libraries for ref in libraries[ident]["provides"]}
    require(process_requirements == process_provides and len(process_requirements) == 10, "process requirement/library capability coverage drift")

    simulation_libraries = {simulation_local_library(ref) for ref in SIMULATION_CONCRETE}
    simulation_maps = {
        row["abstract_library_ref"]: row
        for row in binding_maps.values()
        if SIMULATION_PRODUCT in row.get("product_refs", [])
    }
    require(set(simulation_maps) == simulation_libraries and len(simulation_maps) == 6, "simulation product-library map coverage drift")
    require({row["concrete_library_refs"][0] for row in simulation_maps.values()} == set(SIMULATION_CONCRETE), "simulation exact concrete-library split drift")
    require("library.method_kernels.operations_research_bridge" not in {ref for row in simulation_maps.values() for ref in row["concrete_library_refs"]}, "simulation product bound through generic operations-research facade")
    simulation_requirements = {row["capability_ref"] for row in data["requirements"] if row["consumer_ref"] == SIMULATION_PRODUCT}
    simulation_provides = {ref for ident in simulation_libraries for ref in libraries[ident]["provides"]}
    require(simulation_requirements == simulation_provides and len(simulation_requirements) == 7, "simulation requirement/library capability coverage drift")

    forecast_libraries = {forecast_local_library(key) for key in FORECAST_KEYS}
    forecast_maps = {
        row["abstract_library_ref"]: row
        for row in binding_maps.values()
        if FORECAST_PRODUCT in row.get("product_refs", [])
    }
    require(set(forecast_maps) == forecast_libraries and len(forecast_maps) == 8, "forecast product-library map coverage drift")
    exact_forecast_refs = {ref for row in forecast_maps.values() for ref in row["concrete_library_refs"]}
    require(exact_forecast_refs == set(FORECAST_EXACT) | {ref for refs in FORECAST_OVERRIDES.values() for ref in refs}, "forecast exact method-library split drift")
    for key, refs in FORECAST_OVERRIDES.items():
        require(forecast_maps[forecast_local_library(key)]["concrete_library_refs"] == refs, f"forecast compiler override drift: {key}")
    forecast_gap_maps = {
        ident: row for ident, row in forecast_maps.items()
        if row["bindability"] == "structurally_partial_blocking_gap"
    }
    require(not forecast_gap_maps, "closed forecast lifecycle seam regressed to a structural gap")
    forecast_gaps = {ident: row for ident, row in binding_gaps.items() if FORECAST_PRODUCT in row.get("product_refs", [])}
    require(not forecast_gaps, "closed forecast gap reappeared")
    imported_forecast_support = {"library.method_kernels.analysis_design", "library.method_kernels.method_contracts", "library.method_kernels.result_algebra", "library.method_kernels.artifact_envelope", "library.method_kernels.forecasting_methods"}
    require(not ({ref for row in forecast_maps.values() for ref in row["concrete_library_refs"]} & imported_forecast_support), "forecast product absorbed generic support or compatibility facade")
    forecast_requirements = {row["capability_ref"] for row in data["requirements"] if row["consumer_ref"] == FORECAST_PRODUCT}
    forecast_provides = {ref for ident in forecast_libraries for ref in libraries[ident]["provides"]}
    require(forecast_requirements == forecast_provides and len(forecast_requirements) == 9, "forecast requirement/library capability coverage drift")

    experiment_libraries = {experiment_local_library(key) for key in EXPERIMENT_KEYS}
    experiment_maps = {
        row["abstract_library_ref"]: row
        for row in binding_maps.values()
        if EXPERIMENT_PRODUCT in row.get("product_refs", [])
    }
    require(set(experiment_maps) == experiment_libraries and len(experiment_maps) == 8, "experiment product-library map coverage drift")
    exact_experiment_refs = {ref for row in experiment_maps.values() for ref in row["concrete_library_refs"]}
    require(exact_experiment_refs == set(EXPERIMENT_EXACT) | {ref for refs in EXPERIMENT_OVERRIDES.values() for ref in refs}, "experiment exact lifecycle-library split drift")
    for key, refs in EXPERIMENT_OVERRIDES.items():
        require(experiment_maps[experiment_local_library(key)]["concrete_library_refs"] == refs, f"experiment compiler override drift: {key}")
    experiment_gap_maps = {
        ident: row for ident, row in experiment_maps.items()
        if row["bindability"] == "structurally_partial_blocking_gap"
    }
    require(not experiment_gap_maps, "closed experiment lifecycle seam regressed to a structural gap")
    experiment_gaps = {ident: row for ident, row in binding_gaps.items() if EXPERIMENT_PRODUCT in row.get("product_refs", [])}
    require(not experiment_gaps, "closed experiment gap reappeared")
    imported_experiment_support = {"library.method_kernels.analysis_design", "library.method_kernels.inferential_tests_resampling", "library.method_kernels.causal_effect_estimators", "library.method_kernels.result_algebra", "library.method_kernels.causal_methods"}
    require(not ({ref for row in experiment_maps.values() for ref in row["concrete_library_refs"]} & imported_experiment_support), "experiment product absorbed generic analysis/causal support")
    experiment_requirements = {row["capability_ref"] for row in data["requirements"] if row["consumer_ref"] == EXPERIMENT_PRODUCT}
    experiment_provides = {ref for ident in experiment_libraries for ref in libraries[ident]["provides"]}
    require(experiment_requirements - {"capability.estimate_causal_effect"} == experiment_provides and len(experiment_requirements) == 10 and len(experiment_provides) == 9, "experiment requirement/library capability coverage drift")

    geospatial_libraries = {geospatial_local_library(key) for key in GEOSPATIAL_KEYS}
    geospatial_maps = {
        row["abstract_library_ref"]: row
        for row in binding_maps.values()
        if GEOSPATIAL_PRODUCT in row.get("product_refs", [])
    }
    require(set(geospatial_maps) == geospatial_libraries and len(geospatial_maps) == 13, "geospatial product-library map coverage drift")
    exact_geospatial_refs = {ref for row in geospatial_maps.values() for ref in row["concrete_library_refs"]}
    require(exact_geospatial_refs == set(GEOSPATIAL_EXACT) | {ref for refs in GEOSPATIAL_OVERRIDES.values() for ref in refs}, "geospatial exact foundation/specialized-library split drift")
    for key, refs in GEOSPATIAL_OVERRIDES.items():
        require(geospatial_maps[geospatial_local_library(key)]["concrete_library_refs"] == refs, f"geospatial compiler override drift: {key}")
    geospatial_gap_maps = {
        ident: row for ident, row in geospatial_maps.items()
        if row["bindability"] == "structurally_partial_blocking_gap"
    }
    require(not geospatial_gap_maps, "closed geospatial seam regressed to a structural gap")
    geospatial_gaps = {ident: row for ident, row in binding_gaps.items() if GEOSPATIAL_PRODUCT in row.get("product_refs", [])}
    require(not geospatial_gaps, "closed geospatial gap reappeared")
    imported_geospatial_support = {"library.method_kernels.result_algebra", "library.method_kernels.spatial_methods", "library.method_kernels.image_methods", "library.method_kernels.graph_methods"}
    require(not ({ref for row in geospatial_maps.values() for ref in row["concrete_library_refs"]} & imported_geospatial_support), "geospatial product absorbed generic compatibility or image/graph support")
    geospatial_requirements = {row["capability_ref"] for row in data["requirements"] if row["consumer_ref"] == GEOSPATIAL_PRODUCT}
    geospatial_provides = {ref for ident in geospatial_libraries for ref in libraries[ident]["provides"]}
    require(geospatial_requirements == geospatial_provides and len(geospatial_requirements) == 14, "geospatial requirement/library capability coverage drift")

    graph_workbench_libraries = {graph_workbench_local_library(key) for key in GRAPH_WORKBENCH_KEYS}
    graph_workbench_maps = {
        row["abstract_library_ref"]: row
        for row in binding_maps.values()
        if GRAPH_WORKBENCH_PRODUCT in row.get("product_refs", [])
    }
    require(set(graph_workbench_maps) == graph_workbench_libraries and len(graph_workbench_maps) == 7, "graph workbench product-library map coverage drift")
    for key in GRAPH_WORKBENCH_KEYS:
        row = graph_workbench_maps[graph_workbench_local_library(key)]
        require(row["concrete_library_refs"] == GRAPH_WORKBENCH_CONCRETE[key], f"graph workbench compiler binding drift: {key}")
        if GRAPH_WORKBENCH_CONCRETE[key]:
            require(row["bindability"] == "structurally_bindable_unqualified" and not row["blocking_gap_refs"], f"mapped graph workbench seam falsely blocked: {key}")
        else:
            require(row["bindability"] == "structurally_partial_blocking_gap" and row["blocking_gap_refs"] == [f"gap.analytics_graph_workbench.{key}"], f"graph workbench vacancy hidden: {key}")
    graph_workbench_requirements = {row["capability_ref"] for row in data["requirements"] if row["consumer_ref"] == GRAPH_WORKBENCH_PRODUCT}
    graph_workbench_provides = {ref for ident in graph_workbench_libraries for ref in libraries[ident]["provides"]}
    require(graph_workbench_requirements == graph_workbench_provides and len(graph_workbench_requirements) == 7, "graph workbench requirement/library capability coverage drift")
    require(
        not any(
            GRAPH_WORKBENCH_PRODUCT in row.get("product_refs", [])
            for row in libraries.values()
            if row["library_id"] == "library.graph_analysis_core"
        ),
        "graph workbench absorbed the legacy graph-method facade",
    )

    planning_libraries = {planning_local_library(key) for key in PLANNING_KEYS}
    planning_maps = {
        row["abstract_library_ref"]: row
        for row in binding_maps.values()
        if PLANNING_PRODUCT in row.get("product_refs", [])
    }
    require(set(planning_maps) == planning_libraries and len(planning_maps) == len(PLANNING_KEYS), "integrated-planning product-library map coverage drift")
    require(
        all(
            row["bindability"] == "structurally_partial_blocking_gap"
            and not row["concrete_library_refs"]
            and row["blocking_gap_refs"] == [f"gap.analytics_planning.{key}"]
            for key, row in ((key, planning_maps[planning_local_library(key)]) for key in PLANNING_KEYS)
        ),
        "integrated-planning vacancy was hidden or bound to an invented compiler implementation",
    )
    planning_requirements = {row["capability_ref"] for row in data["requirements"] if row["consumer_ref"] == PLANNING_PRODUCT}
    planning_provides = {ref for ident in planning_libraries for ref in libraries[ident]["provides"]}
    require(planning_requirements == planning_provides and len(planning_requirements) == len(PLANNING_KEYS), "integrated-planning requirement/library capability coverage drift")

    project_controls_libraries = {project_controls_local_library(key) for key in PROJECT_CONTROLS_KEYS}
    project_controls_maps = {
        row["abstract_library_ref"]: row
        for row in binding_maps.values()
        if PROJECT_CONTROLS_PRODUCT in row.get("product_refs", [])
    }
    require(set(project_controls_maps) == project_controls_libraries and len(project_controls_maps) == len(PROJECT_CONTROLS_KEYS), "project-controls product-library map coverage drift")
    require(
        all(
            row["bindability"] == "structurally_partial_blocking_gap"
            and not row["concrete_library_refs"]
            and row["blocking_gap_refs"] == [f"gap.project_controls.{key}"]
            for key, row in ((key, project_controls_maps[project_controls_local_library(key)]) for key in PROJECT_CONTROLS_KEYS)
        ),
        "project-controls vacancy was hidden or bound to an invented compiler implementation",
    )
    project_controls_requirements = {row["capability_ref"] for row in data["requirements"] if row["consumer_ref"] == PROJECT_CONTROLS_PRODUCT}
    project_controls_provides = {ref for ident in project_controls_libraries for ref in libraries[ident]["provides"]}
    require(project_controls_requirements == project_controls_provides and len(project_controls_requirements) == len(PROJECT_CONTROLS_KEYS), "project-controls requirement/library capability coverage drift")

    dossiers = data["ddd_dossiers"]
    dossier_by_product = {row.get("product_ref"): row for row in dossiers}
    require(len(dossiers) == 9 and set(dossier_by_product) == {OPTIMIZATION_PRODUCT, PROCESS_PRODUCT, SIMULATION_PRODUCT, FORECAST_PRODUCT, EXPERIMENT_PRODUCT, GEOSPATIAL_PRODUCT, GRAPH_WORKBENCH_PRODUCT, PLANNING_PRODUCT, PROJECT_CONTROLS_PRODUCT}, "analytical DDD dossier identity drift")
    for product_ref, fields, label in (
        (OPTIMIZATION_PRODUCT, OPTIMIZATION_DDD_FIELDS, "optimizer"),
        (PROCESS_PRODUCT, PROCESS_DDD_FIELDS, "process"),
        (SIMULATION_PRODUCT, SIMULATION_DDD_FIELDS, "simulation"),
        (FORECAST_PRODUCT, FORECAST_DDD_FIELDS, "forecast"),
        (EXPERIMENT_PRODUCT, EXPERIMENT_DDD_FIELDS, "experiment"),
        (GEOSPATIAL_PRODUCT, GEOSPATIAL_DDD_FIELDS, "geospatial"),
        (GRAPH_WORKBENCH_PRODUCT, GRAPH_WORKBENCH_DDD_FIELDS, "graph workbench"),
        (PLANNING_PRODUCT, PLANNING_DDD_FIELDS, "integrated planning"),
        (PROJECT_CONTROLS_PRODUCT, PROJECT_CONTROLS_DDD_FIELDS, "project controls"),
    ):
        dossier = dossier_by_product.get(product_ref, {})
        ddd = dossier.get("strategic_and_tactical_ddd", {})
        require(set(ddd) == fields and all(ddd.get(field) not in (None, [], {}) for field in fields), f"{label} 29-field DDD incomplete")
        require(dossier.get("status") == "candidate_not_ratified", f"{label} DDD prematurely ratified")
        require(any("removing every optional" in law.lower() for law in ddd.get("nonfunctional_laws", [])), f"{label} model/agent removal law missing")
    for row in data["relations"]:
        require(row["from_ref"] in nodes and row["to_ref"] in nodes, f"bad relation refs {row['relation_id']}")
        require(row["predicate"] in metamodel["relation_predicates"] and row["binding_phase"] in metamodel["binding_phases"], f"bad relation semantics {row['relation_id']}")
    for row in data["crosswalks"]:
        require(all(ref in nodes for ref in row["canonical_refs"]), f"bad crosswalk {row['legacy_ref']}")

    negative_ids = {row["test_id"] for row in data["negative_tests"]}
    require({"negative.method.equals.product", "negative.library.equals.product", "negative.ai_prefix", "negative.ai_required", "negative.agent_replaces_execution"} <= negative_ids, "missing analytical or automation negative twins")
    require(len(negative_ids) >= 19, "negative-test surface too small")
    require({f"negative.optimizer.{key}" for key in ["decision_model", "hard_soft", "success_status", "feasible_optimal", "heuristic_proof", "timeout_terminal", "diagnosis_relaxation", "provider_name", "solution_effect", "agent_authority"]} <= negative_ids, "optimizer negative twins missing")
    require({f"negative.process.{key}" for key in ["person_semantics", "oced_ocel", "case_truth", "state_source", "ekg_tekg", "model_truth", "deviation_cause", "bottleneck_cause", "predictive_core", "agent_authority"]} <= negative_ids, "process negative twins missing")
    require({f"negative.simulation.{key}" for key in ["model_reality", "scenario_forecast", "seed_stream", "run_validity", "verification_validation", "calibration_truth", "comparison_cause", "simulation_optimization", "provider_name", "agent_authority"]} <= negative_ids, "simulation negative twins missing")
    require({f"negative.forecast.{key}" for key in ["observation_forecast", "scenario_forecast", "point_distribution", "leakage", "provider_method", "selection_truth", "coherence_accuracy", "override_authority", "publication_action", "agent_authority"]} <= negative_ids, "forecast negative twins missing")
    require({f"negative.experiment.{key}" for key in ["hypothesis_protocol", "assignment_exposure", "flag_experiment", "randomization_persistence", "monitoring_authority", "interim_peeking", "estimate_conclusion", "conclusion_release", "provider_name", "agent_authority"]} <= negative_ids, "experiment negative twins missing")
    require({f"negative.geospatial.{key}" for key in ["territory_geometry", "crs_drop", "axis_epoch", "repair_truth", "raster_resolution", "proximity_reachability", "match_identity", "association_cause", "map_action", "agent_authority"]} <= negative_ids, "geospatial negative twins missing")
    require({f"negative.graph_workbench.{key}" for key in ["method_product", "ontology_truth", "projection_truth", "path_cause", "centrality_authority", "community_identity", "run_success", "benchmark_universal", "publication_action", "agent_authority"]} <= negative_ids, "graph workbench negative twins missing")
    require({f"negative.planning.{key}" for key in ["fact_forecast_plan", "scenario_plan", "objective_authority", "feasibility_selection", "comparison_approval", "consensus_authority", "approval_effect", "variance_rewrite", "vertical_ownership", "agent_authority"]} <= negative_ids, "integrated-planning negative twins missing")
    require({f"negative.project_controls.{key}" for key in ["planning_baseline", "baseline_current", "progress_earned", "variance_cause", "forecast_change", "approval_revision", "cost_ledger", "payment_effect", "analytics_control", "rollup_mutation", "agent_authority"]} <= negative_ids, "project-controls negative twins missing")
    assistance = libraries.get("library.analytical_assistance_port", {})
    require(assistance.get("class") == "optional_modality_port", "model/agent assistance is not optional")
    require("proposal_has_no_authority" in assistance.get("invariants", []), "model/agent port lacks non-authority law")
    require(manifest["derived"]["portable_offers"] == 0 and manifest["derived"]["qualified_offers"] == 0, "unearned portability or qualification")
    require(manifest["derived"]["unbound_requirements"] == len(data["requirements"]), "requirements not explicitly unbound")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "PASS analytical-method adjudication: "
        f"{len(evidence)} sources; {len(artifacts)} artifacts; {len(product_ids)} product candidates; "
        f"{len(libraries)} library contracts; {len(data['ownership'])} owned meanings; "
        f"{len(data['requirements'])} unbound requirements; {len(data['offers'])} unqualified offers; "
        f"{len(data['binding_maps'])} compiler binding maps including 9 optimizer, 7 process, 6 simulation, 8 forecast, 8 experiment, 13 geospatial, 7 graph-workbench, 13 integrated-planning and 13 project-controls maps; 9 complete product DDDs; {len(data['binding_gaps'])} explicit graph-workbench/planning/project-controls binding gaps; "
        f"{len(data['crosswalks'])} legacy crosswalks"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
