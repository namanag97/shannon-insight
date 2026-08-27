#!/usr/bin/env python3
"""Validate lossless coverage and fail-closed claims in the presentation audit."""

from __future__ import annotations

import hashlib
import json

from build_bundle import FILES, HERE, INPUTS, build, load_jsonl, outputs


def main() -> int:
    errors: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    expected = outputs()
    for name, text in expected.items():
        path = HERE / name
        require(path.is_file() and path.read_text() == text, f"stale {name}")

    manifest = json.loads((HERE / "manifest.json").read_text())
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        require(len(data) == claim["bytes"], f"byte count mismatch {name}")
        require(hashlib.sha256(data).hexdigest() == claim["sha256"], f"hash mismatch {name}")

    snapshot = json.loads((HERE / "input-snapshot.json").read_text())
    claims = {row["role"]: row for row in snapshot["files"]}
    require(set(claims) == set(INPUTS), "input snapshot roles drift")
    for role, path in INPUTS.items():
        data = path.read_bytes()
        require(claims[role]["sha256"] == hashlib.sha256(data).hexdigest(), f"input hash stale {role}")

    built = build()
    sources = built["evidence"]
    axes = built["semantic_axes"]
    artifacts = built["artifact_kinds"]
    results = built["result_kinds"]
    hypotheses = built["product_hypotheses"]
    libraries = built["library_hypotheses"]
    laws = built["noncollapse_laws"]
    obligations = built["artifact_axis_obligations"]
    cells = built["compatibility_cells"]
    gaps = built["open_gaps"]
    summary = built["summary"]

    require(len(sources) >= 35, "primary/official source floor not met")
    require(len({row["source_id"] for row in sources}) == len(sources), "duplicate source id")
    require(all(row["bounded_claim"] and row["authority_limit"] for row in sources), "unbounded evidence claim")
    evidence_ids = {row["source_id"] for row in sources}
    require(len(axes) == 16, "presentation semantic axes drift")
    require(len(artifacts) >= 35, "artifact ontology underdecomposed")
    require(len(results) >= 21, "analytical result ontology underdecomposed")
    require(len(hypotheses) >= 12, "product hypothesis frontier underdecomposed")
    require(len(libraries) >= 45, "library frontier underdecomposed")
    require(len(laws) >= 30, "non-collapse law floor not met")
    require(len(obligations) == len(artifacts) * len(axes), "artifact-axis tensor is not lossless")
    require(len(cells) == len(artifacts) * len(results), "result-artifact tensor is not lossless")
    require(len({row["obligation_id"] for row in obligations}) == len(obligations), "duplicate axis obligation")
    require(len({row["cell_id"] for row in cells}) == len(cells), "duplicate compatibility cell")
    require(all(row["decision"] == "UNRATIFIED" and row["exact_contract_ref"] is None for row in obligations), "artifact-axis authority fabricated")
    require(all(row["status"] == "UNRATIFIED" and row["profile_ref"] is None for row in cells), "compatibility profile fabricated")
    require(all(row["ratification"] == "WITHHELD" for row in hypotheses), "product ratification fabricated")
    require(all(len(row["evidence_refs"]) >= 3 and set(row["evidence_refs"]) <= evidence_ids for row in hypotheses), "product hypothesis evidence is weak or unresolved")
    require(all(len(row["evidence_refs"]) >= 2 and set(row["evidence_refs"]) <= evidence_ids for row in artifacts), "artifact evidence is weak or unresolved")
    require(all(row["evidence_refs"] and set(row["evidence_refs"]) <= evidence_ids for row in libraries), "library evidence is missing or unresolved")
    require(all(not row["unresolved_retained_product_refs"] for row in hypotheses), "product hypothesis references unknown retained products")
    require(all(row["compiler_binding"].startswith("REFUSED") for row in libraries), "compiler binding bypassed")
    require(all(row["blocking_for_promotion_or_compilation"] and row["status"] == "OPEN" for row in gaps), "gap closed without evidence")
    require(summary["ratified_products"] == summary["ratified_contracts"] == summary["qualified_implementations"] == 0, "physical or semantic proof fabricated")
    require(summary["completion_claim"] is False and summary["status"].endswith("INCOMPLETE"), "audit overclaims completion")
    require({row["name"] for row in artifacts} >= {"dashboard", "paginated_report", "regulatory_report", "notebook", "spreadsheet_workbook", "map_view", "graph_view", "waveform_view", "volume_3d_view", "embedded_view", "alert_occurrence", "accessible_equivalent"}, "critical presentation artifacts missing")
    require({row["name"] for row in results} >= {"forecast", "causal_effect", "optimization_solution", "simulation_ensemble", "process_model", "geospatial_feature", "image_inspection", "signal_window_spectrum", "scientific_mesh_volume"}, "critical analytical results missing")
    require({row["law_id"] for row in laws} >= {"law.presentation.dashboard_alert", "law.presentation.selection_decision", "law.presentation.embed_authority", "law.presentation.render_conformance"}, "critical non-collapse laws missing")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "PASS presentation-experience gap audit: "
        f"{len(sources)} sources; {len(artifacts)} artifacts x {len(results)} result kinds = {len(cells)} compatibility cells; "
        f"{len(obligations)} artifact-axis obligations; {len(hypotheses)} product hypotheses; "
        f"{len(libraries)} library seams; {len(laws)} non-collapse laws; {len(gaps)} open gaps; "
        "0 ratified products/contracts/implementations"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
