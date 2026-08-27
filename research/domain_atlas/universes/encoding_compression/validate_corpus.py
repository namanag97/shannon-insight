#!/usr/bin/env python3
"""Validate structural, referential and constitutional corpus laws."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load_json(name: str) -> dict:
    value = json.loads((ROOT / name).read_text())
    assert isinstance(value, dict), f"{name}: root must be object"
    return value


def load_jsonl(name: str) -> list[dict]:
    rows: list[dict] = []
    for line_no, line in enumerate((ROOT / name).read_text().splitlines(), 1):
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise AssertionError(f"{name}:{line_no}: invalid JSON: {exc}") from exc
        assert isinstance(value, dict), f"{name}:{line_no}: record must be object"
        rows.append(value)
    assert rows, f"{name}: must not be empty"
    return rows


def unique(rows: list[dict], field: str, name: str) -> set[str]:
    values = [row.get(field) for row in rows]
    assert all(isinstance(value, str) and value for value in values), f"{name}: missing {field}"
    duplicates = [value for value, count in Counter(values).items() if count > 1]
    assert not duplicates, f"{name}: duplicate {field}: {duplicates}"
    return set(values)


def require_fields(rows: list[dict], fields: set[str], name: str) -> None:
    for line_no, row in enumerate(rows, 1):
        missing = fields - row.keys()
        assert not missing, f"{name}:{line_no}: missing {sorted(missing)}"
        for field in fields:
            assert row[field] not in ("", [], None), f"{name}:{line_no}: empty {field}"


def refs_exist(rows: list[dict], field: str, known: set[str], name: str) -> None:
    for line_no, row in enumerate(rows, 1):
        refs = row.get(field, [])
        assert isinstance(refs, list), f"{name}:{line_no}: {field} must be list"
        unknown = set(refs) - known
        assert not unknown, f"{name}:{line_no}: unknown {field}: {sorted(unknown)}"


def main() -> None:
    manifest = load_json("manifest.json")
    gap_schema = load_json("gap.schema.json")
    axes = load_json("axes.json")
    qualification = load_json("library-provider-qualification.json")
    sources = load_jsonl("sources.jsonl")
    contexts = load_jsonl("bounded-context-candidates.jsonl")
    representations = load_jsonl("format-layout-codec-records.jsonl")
    operations = load_jsonl("typed-operations.jsonl")
    decisions = load_jsonl("decision-points.jsonl")
    mappings = load_jsonl("compiler-mappings.jsonl")
    libraries = load_jsonl("library-candidates.jsonl")
    kernels = load_jsonl("kernel-contracts.jsonl")
    innovations = load_jsonl("innovations.jsonl")
    gaps = load_jsonl("gaps.jsonl")
    required_gap_fields = set(gap_schema["required"])
    allowed_gap_fields = set(gap_schema["properties"])
    for gap in gaps:
        assert required_gap_fields <= set(gap) <= allowed_gap_fields
        assert gap["status"] == gap_schema["properties"]["status"]["const"]

    source_ids = unique(sources, "source_id", "sources")
    context_ids = unique(contexts, "context_id", "contexts")
    representation_ids = unique(representations, "representation_id", "representations")
    operation_ids = unique(operations, "operation_id", "operations")
    decision_ids = unique(decisions, "decision_id", "decisions")
    unique(mappings, "mapping_id", "mappings")
    unique(libraries, "library_id", "libraries")
    unique(kernels, "kernel_id", "kernels")
    unique(innovations, "innovation_id", "innovations")
    unique(gaps, "gap_id", "gaps")

    assert manifest["completion_claim"] is False
    assert manifest["status"] == "candidate_open_world"
    assert len(sources) >= 40, "research gate requires at least 40 primary/official sources"
    assert sum(row.get("primary_or_official") is True for row in sources) >= 40
    assert len({row["publisher"] for row in sources}) >= 25, "publisher diversity regressed"
    assert all(row["url"].startswith("https://") for row in sources)
    assert all(row["authority_limit"] for row in sources)

    assert len(axes["axes"]) >= 20
    axis_ids = [axis["axis_id"] for axis in axes["axes"]]
    assert len(axis_ids) == len(set(axis_ids))
    assert all(len(axis["values"]) >= 2 for axis in axes["axes"])

    assert len(contexts) >= 30
    require_fields(contexts, {
        "context_id", "edition", "status", "sovereign_question", "owns", "inside",
        "outside", "invariants", "compiler_surfaces", "evidence_refs", "gaps",
        "llm_dependency",
    }, "contexts")
    refs_exist(contexts, "evidence_refs", source_ids, "contexts")
    assert all(row["status"] == "candidate_not_adjudicated" for row in contexts)

    required_contexts = {
        "bc.representation.carrier", "bc.representation.byte_order",
        "bc.representation.character_encoding", "bc.representation.scalar_encoding",
        "bc.representation.schema_serialization", "bc.representation.framing",
        "bc.representation.canonicalization", "bc.representation.content_identity",
        "bc.representation.chunking", "bc.representation.physical_layout",
        "bc.representation.null_nested_layout", "bc.representation.column_encoding",
        "bc.representation.dictionary_lifecycle", "bc.representation.compression_algorithm",
        "bc.representation.codec", "bc.representation.container",
        "bc.representation.loss_contract", "bc.representation.compression_selection",
        "bc.representation.pipeline", "bc.representation.random_access",
        "bc.representation.splittability", "bc.representation.pruning_metadata",
        "bc.representation.integrity", "bc.representation.protection_envelope",
        "bc.representation.transcode", "bc.representation.corruption_recovery",
        "bc.representation.streaming", "bc.representation.target_capability",
        "bc.representation.kernel_contract", "bc.representation.provider_qualification",
        "bc.representation.edition_compatibility", "bc.representation.resource_model",
    }
    assert required_contexts <= context_ids, f"missing anchor contexts: {sorted(required_contexts - context_ids)}"

    assert len(representations) >= 110
    require_fields(representations, {
        "representation_id", "record_kind", "name", "definition",
        "semantic_owner_context_ref", "loss_class", "loss_contract", "capability_traits",
        "parameters", "access_contract", "integrity_contract", "compatibility_contract",
        "target_requirements", "forbidden_inferences", "evidence_refs",
        "compiler_implications", "dispatch_key", "llm_dependency",
    }, "representations")
    refs_exist(representations, "evidence_refs", source_ids, "representations")
    for row in representations:
        assert row["semantic_owner_context_ref"] in context_ids
        assert row["dispatch_key"] == "capability_signature_only"
        assert row["llm_dependency"] == "none"
        lc = row["loss_contract"]
        assert lc.get("error_contract") and lc.get("metric") and lc.get("verification")
        if row["loss_class"] in {"error_bounded_lossy", "perceptual_lossy", "mixed_declared"}:
            assert lc.get("approval_required") is True, f"loss approval missing: {row['representation_id']}"
            assert lc.get("bound") not in (None, "", "unknown", "unbounded"), f"loss bound missing: {row['representation_id']}"
            assert "loss/error profile" in row["parameters"]

    required_kinds = {
        "carrier", "scalar_encoding", "character_encoding", "schema_serialization", "framing",
        "physical_layout", "column_encoding", "compression_algorithm", "container_file_format",
        "domain_codec", "canonicalization_profile", "integrity_algorithm",
        "cryptographic_envelope", "chunking_scheme", "execution_target",
    }
    kinds = {row["record_kind"] for row in representations}
    assert required_kinds <= kinds, f"missing record kinds: {sorted(required_kinds - kinds)}"
    required_representations = {
        "rep.character.utf8", "rep.serialization.protobuf", "rep.serialization.avro_binary",
        "rep.layout.definition_repetition", "rep.layout.row_group", "rep.layout.stripe",
        "rep.layout.multidimensional_chunk", "rep.column.dictionary", "rep.column.run_length",
        "rep.column.delta_binary_packed", "rep.column.frame_of_reference",
        "rep.compression.deflate", "rep.compression.zstandard", "rep.compression.sz3",
        "rep.compression.zfp", "rep.container.parquet", "rep.container.orc",
        "rep.container.hdf5", "rep.container.zarr3", "rep.codec.png", "rep.codec.flac",
        "rep.codec.opus", "rep.canonical.jcs", "rep.integrity.crc32c",
        "rep.integrity.sha256", "rep.protection.aead", "rep.chunk.content_defined",
        "rep.target.gpu", "rep.target.hardware_offload",
    }
    assert required_representations <= representation_ids

    assert len(operations) >= 35
    require_fields(operations, {
        "operation_id", "family_id", "name", "operation_kind", "semantic_owner_candidate",
        "signature", "effect_class", "determinism", "idempotency", "totality",
        "information_loss", "loss_contract", "order_sensitivity", "statefulness",
        "execution_modes", "preconditions", "postconditions", "laws", "refusals",
        "failures", "resource_model", "provider_requirements", "evidence_refs",
        "llm_dependency", "gaps",
    }, "operations")
    refs_exist(operations, "evidence_refs", source_ids, "operations")
    for row in operations:
        assert row["semantic_owner_candidate"] in context_ids
        signature = row["signature"]
        assert signature["inputs"] and signature["outputs"] and signature["error_type"]
        assert "no vendor-name dispatch" in row["laws"]
        assert row["llm_dependency"] == "none"
        if row["information_loss"] == "lossy_declared":
            required = set(row["loss_contract"]["must_include"])
            assert {"metric", "scope", "approval", "verification"} <= required

    assert len(decisions) >= 30
    require_fields(decisions, {
        "decision_id", "owner_context_ref", "question", "value_contract", "allowed_values",
        "binding_phase", "authority_ref", "default_law", "constraints", "implications",
        "affects_contracts", "evidence_required", "change_semantics",
    }, "decisions")
    assert all("gaps" in row and isinstance(row["gaps"], list) for row in decisions)
    assert all(row["owner_context_ref"] in context_ids for row in decisions)
    assert all(row["default_law"] == "forbidden" and row["default_value"] is None for row in decisions)

    assert len(mappings) >= 18
    refs_exist(mappings, "operation_refs", operation_ids, "mappings")
    refs_exist(mappings, "decision_refs", decision_ids, "mappings")
    for row in mappings:
        assert "provider-name branches" in " ".join(row["binding_law"])
        assert row["typed_refusals"]

    assert len(libraries) >= 24
    for row in libraries:
        assert set(row["contributes_to_context_refs"]) <= context_ids
        assert set(row["operation_refs"]) <= operation_ids
        assert set(row["decision_refs"]) <= decision_ids
        assert "provider-name dispatch" in row["forbidden_responsibilities"]
        assert row["removal_seams"]

    assert len(kernels) >= 12
    for row in kernels:
        assert set(row["target_profile_refs"]) <= representation_ids
        assert set(row["operation_refs"]) <= operation_ids
        assert row["ports"]["inputs"] and row["ports"]["outputs"] and row["ports"]["errors"]
        assert row["fallback_contract"] and row["qualification"] and row["receipt_fields"]
        assert row["llm_dependency"] == "none"

    assert len(qualification["offer_required_fields"]) >= 20
    assert len(qualification["qualification_gates"]) >= 12
    assert "dispatch by crate/vendor/product name" in qualification["forbidden"]

    assert len(innovations) >= 15
    refs_exist(innovations, "evidence_refs", source_ids, "innovations")
    for row in innovations:
        assert 2021 <= row["year"] <= 2026
        assert row["non_llm"] is True
        assert row["limits"] and row["compiler_implications"]

    assert len(gaps) >= 15
    assert all(row["status"] == "open" for row in gaps)
    assert all("typed compiler gap" in row["compiler_behavior_until_closed"] for row in gaps)

    forbidden = {item.lower() for item in manifest["forbidden_core_dependencies"]}
    for name, rows in [
        ("contexts", contexts), ("representations", representations), ("operations", operations),
        ("libraries", libraries), ("kernels", kernels), ("innovations", innovations),
    ]:
        payload = json.dumps(rows).lower()
        # Words may occur only in the explicit llm_dependency/non_llm fields and README; no
        # core record may declare one as a dependency value.
        if name in {"contexts", "representations", "operations", "kernels"}:
            assert '"llm_dependency": "none"' in payload
        if name == "innovations":
            assert all(row["non_llm"] is True for row in rows)
        assert not any(f'"llm_dependency": "{term}"' in payload for term in forbidden)

    expected_counts = {
        "sources": len(sources), "axes": len(axes["axes"]), "contexts": len(contexts),
        "representations": len(representations), "operations": len(operations),
        "decision_points": len(decisions), "compiler_mappings": len(mappings),
        "library_candidates": len(libraries), "kernel_contracts": len(kernels),
        "innovations": len(innovations), "gaps": len(gaps),
    }
    assert manifest["counts"] == expected_counts, "manifest counts are stale; rebuild corpus"

    print(
        "PASS encoding-compression universe: "
        f"{len(sources)} sources, {len(contexts)} contexts, {len(representations)} representations, "
        f"{len(operations)} operations, {len(decisions)} decisions, {len(mappings)} compiler mappings, "
        f"{len(libraries)} library candidates, {len(kernels)} kernels, "
        f"{len(innovations)} innovations, {len(gaps)} explicit gaps"
    )


if __name__ == "__main__":
    main()
