#!/usr/bin/env python3
"""Validate the data-modality gap audit, references, gates, and canonical snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CANONICAL = ROOT.parent / "data_shapes"
ERRORS: list[str] = []
WARNINGS: list[str] = []

try:
    import jsonschema  # type: ignore
except ImportError:
    jsonschema = None
    WARNINGS.append("jsonschema unavailable; reference, count, layer, and determinism gates still ran")


def fail(message: str) -> None:
    ERRORS.append(message)


def load_json(name: str) -> dict:
    try:
        value = json.loads((ROOT / name).read_text())
        if not isinstance(value, dict):
            fail(f"{name}: top-level value is not an object")
            return {}
        return value
    except Exception as exc:
        fail(f"{name}: cannot parse: {exc}")
        return {}


def load_jsonl(name: str) -> list[dict]:
    result = []
    try:
        lines = (ROOT / name).read_text().splitlines()
    except Exception as exc:
        fail(f"{name}: cannot read: {exc}")
        return result
    for lineno, line in enumerate(lines, 1):
        if not line.strip():
            fail(f"{name}:{lineno}: blank JSONL line")
            continue
        try:
            value = json.loads(line)
        except Exception as exc:
            fail(f"{name}:{lineno}: cannot parse: {exc}")
            continue
        if not isinstance(value, dict):
            fail(f"{name}:{lineno}: record is not an object")
            continue
        result.append(value)
    return result


def index(records: list[dict], key: str, label: str) -> dict[str, dict]:
    result = {}
    for lineno, record in enumerate(records, 1):
        value = record.get(key)
        if not isinstance(value, str) or not value:
            fail(f"{label}:{lineno}: missing {key}")
        elif value in result:
            fail(f"{label}: duplicate {key} {value}")
        else:
            result[value] = record
    return result


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def schema_validate(records: list[dict] | dict, schema_name: str, label: str) -> None:
    if jsonschema is None:
        return
    schema = json.loads((ROOT / "schemas" / schema_name).read_text())
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    instances = records if isinstance(records, list) else [records]
    for index_number, instance in enumerate(instances, 1):
        for error in sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path)):
            path = "/".join(str(part) for part in error.absolute_path) or "$"
            fail(f"{label}:{index_number}:{path}: {error.message}")


def require_refs(records: list[dict], field: str, allowed: set[str], label: str) -> set[str]:
    used: set[str] = set()
    for record in records:
        rid = next((record.get(k) for k in ("family_id", "crosswalk_id", "assertion_id", "innovation_id", "finding_id", "sample_id", "operation_gap_id") if record.get(k)), label)
        refs = record.get(field)
        if not isinstance(refs, list) or not refs:
            fail(f"{rid}: {field} must be a non-empty list")
            continue
        for ref in refs:
            used.add(ref)
            if ref not in allowed:
                fail(f"{rid}: unresolved {field} reference {ref}")
    return used


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-determinism", action="store_true", help="rerun the builder and require byte-identical outputs")
    args = parser.parse_args()

    axes_doc = load_json("classification-axes.json")
    summary = load_json("audit-summary.json")
    saturation = load_json("saturation-report.json")
    snapshot = load_json("canonical-snapshot.json")
    manifest = load_json("manifest.json")

    families_list = load_jsonl("modality-family-expectations.jsonl")
    tensor_list = load_jsonl("coverage-tensor.jsonl")
    crosswalk_list = load_jsonl("canonical-crosswalk.jsonl")
    operations_list = load_jsonl("operation-type-gaps.jsonl")
    assertions_list = load_jsonl("audit-assertions.jsonl")
    sources_list = load_jsonl("standards-sources.jsonl")
    innovations_list = load_jsonl("innovations-2021-2026.jsonl")
    findings_list = load_jsonl("gap-findings.jsonl")
    verticals_list = load_jsonl("vertical-case-samples.jsonl")
    representation_list = load_jsonl("representation-layer-findings.jsonl")
    canonical_rep_audit_list = load_jsonl("canonical-representation-audit.jsonl")
    schema_postures_list = load_jsonl("schema-posture-audit.jsonl")

    schema_validate(axes_doc, "classification-axes.schema.json", "classification-axes.json")
    schema_validate(families_list, "family-expectation.schema.json", "modality-family-expectations.jsonl")
    schema_validate(tensor_list, "coverage-tensor.schema.json", "coverage-tensor.jsonl")
    schema_validate(crosswalk_list, "crosswalk.schema.json", "canonical-crosswalk.jsonl")
    schema_validate(sources_list, "source.schema.json", "standards-sources.jsonl")
    schema_validate(assertions_list, "audit-assertion.schema.json", "audit-assertions.jsonl")
    schema_validate(innovations_list, "innovation.schema.json", "innovations-2021-2026.jsonl")
    schema_validate(operations_list, "operation-gap.schema.json", "operation-type-gaps.jsonl")
    schema_validate(findings_list, "finding.schema.json", "gap-findings.jsonl")
    schema_validate(verticals_list, "vertical-case.schema.json", "vertical-case-samples.jsonl")
    schema_validate(canonical_rep_audit_list, "canonical-representation-audit.schema.json", "canonical-representation-audit.jsonl")
    schema_validate(schema_postures_list, "schema-posture-audit.schema.json", "schema-posture-audit.jsonl")

    axes = index(axes_doc.get("axes", []), "axis_id", "classification-axes.json")
    families = index(families_list, "family_id", "modality-family-expectations.jsonl")
    tensors = index(tensor_list, "tensor_id", "coverage-tensor.jsonl")
    crosswalks = index(crosswalk_list, "crosswalk_id", "canonical-crosswalk.jsonl")
    operations = index(operations_list, "operation_gap_id", "operation-type-gaps.jsonl")
    assertions = index(assertions_list, "assertion_id", "audit-assertions.jsonl")
    sources = index(sources_list, "source_id", "standards-sources.jsonl")
    innovations = index(innovations_list, "innovation_id", "innovations-2021-2026.jsonl")
    findings = index(findings_list, "finding_id", "gap-findings.jsonl")
    verticals = index(verticals_list, "sample_id", "vertical-case-samples.jsonl")
    representation = index(representation_list, "finding_id", "representation-layer-findings.jsonl")
    canonical_rep_audits = index(canonical_rep_audit_list, "representation_audit_id", "canonical-representation-audit.jsonl")
    schema_postures = index(schema_postures_list, "posture_id", "schema-posture-audit.jsonl")

    gates = {
        "axes": (len(axes), 15),
        "candidate families": (len(families), 60),
        "coverage cells": (sum(r.get("cell_count", 0) for r in tensor_list), 500),
        "standards sources": (len(sources), 80),
        "audit assertions": (len(assertions), 100),
        "innovations 2021-2026": (len(innovations), 20),
        "vertical samples": (len(verticals), 16),
        "representation findings": (len(representation), 15),
        "canonical representation audits": (len(canonical_rep_audits), 15),
        "operation-by-type cells": (len(operations), 100),
        "schema posture records": (len(schema_postures), 3),
    }
    for gate, (actual, minimum) in gates.items():
        if actual < minimum:
            fail(f"{gate} gate: expected >= {minimum}, got {actual}")

    required_layers = {"semantic_meaning", "observation_record_shape", "modality", "logical_topology", "carrier", "encoding", "container_file_format", "physical_layout", "compression_protection"}
    layer_axis = axes.get("abstraction_layer", {})
    if set(layer_axis.get("values", [])) != required_layers:
        fail("abstraction_layer axis must preserve exactly the nine required layers")
    unstructured_law = axes_doc.get("unstructured_law", "").lower()
    if "weak" not in unstructured_law or "never absence of structure" not in unstructured_law:
        fail("unstructured posture law is missing or weakened")
    modality_values = set(axes.get("modality", {}).get("values", []))
    if "unstructured" in modality_values:
        fail("unstructured must not be a modality value")
    if {r.get("input_label") for r in schema_postures_list} != {"structured", "semi-structured", "so-called unstructured"}:
        fail("schema-posture audit must explicitly cover structured, semi-structured, and so-called unstructured")
    if any(r.get("is_modality") is not False or r.get("structure_absent") is not False for r in schema_postures_list):
        fail("schema-posture records must reject posture-as-modality and structure-free data")

    required_clusters = {"core", "tables", "documents", "email", "messages", "graphs", "events", "telemetry", "time_series", "signals", "media", "geospatial", "arrays", "scientific", "engineering", "genomics", "health", "finance", "packaging", "code_config", "metadata"}
    clusters = {r.get("domain_cluster") for r in families_list}
    missing_clusters = sorted(required_clusters - clusters)
    if missing_clusters:
        fail(f"required modality clusters absent: {missing_clusters}")

    source_ids = set(sources)
    evidence_used = set()
    for records, label in [
        (families_list, "families"), (crosswalk_list, "crosswalks"), (operations_list, "operations"),
        (assertions_list, "assertions"), (innovations_list, "innovations"), (findings_list, "findings"),
        (verticals_list, "verticals"), (representation_list, "representation findings"),
        (schema_postures_list, "schema postures"),
    ]:
        evidence_used |= require_refs(records, "evidence_refs", source_ids, label)
    if len(evidence_used) < 80:
        fail(f"primary evidence-use gate: expected >=80 referenced sources, got {len(evidence_used)}")
    if len({r.get("publisher") for r in sources_list}) < 35:
        fail("publisher diversity gate: expected >=35 distinct official publishers")
    if len({r.get("standard_family") for r in sources_list}) < 25:
        fail("standards-family diversity gate: expected >=25")
    if len({r.get("url") for r in sources_list}) != len(sources_list):
        WARNINGS.append("Some official URLs are intentionally duplicated between the canonical evidence mirror and audit-specific evidence records")
    for source_id, record in sources.items():
        if not str(record.get("url", "")).startswith("https://"):
            fail(f"{source_id}: source URL must use https")
        if not record.get("limitations"):
            fail(f"{source_id}: evidence limitations absent")

    axis_ids = set(axes)
    allowed_by_axis = {axis_id: set(rec.get("values", [])) for axis_id, rec in axes.items()}
    tensor_by_family = {}
    for tensor_id, record in tensors.items():
        fid = record.get("family_id")
        if fid not in families:
            fail(f"{tensor_id}: unknown family {fid}")
            continue
        if fid in tensor_by_family:
            fail(f"family {fid}: duplicate tensor")
        tensor_by_family[fid] = record
        cells = record.get("axis_cells", [])
        cell_axis_ids = [c.get("axis_id") for c in cells]
        if len(cells) != record.get("cell_count"):
            fail(f"{tensor_id}: cell_count mismatch")
        if len(cell_axis_ids) != len(set(cell_axis_ids)):
            fail(f"{tensor_id}: repeated axis cell")
        if set(cell_axis_ids) != axis_ids:
            fail(f"{tensor_id}: does not cover exactly all axes")
        for cell in cells:
            aid = cell.get("axis_id")
            for value in cell.get("expected_values", []):
                if value not in allowed_by_axis.get(aid, set()):
                    fail(f"{tensor_id}/{aid}: invalid value {value}")
    if set(tensor_by_family) != set(families):
        fail("tensor does not contain exactly one record per family")

    canonical_shapes = index([json.loads(line) for line in (CANONICAL / "shape-records.jsonl").read_text().splitlines()], "shape_id", "canonical shapes")
    canonical_types = index([json.loads(line) for line in (CANONICAL / "type-records.jsonl").read_text().splitlines()], "type_id", "canonical types")
    canonical_ops = index([json.loads(line) for line in (CANONICAL / "operation-totality-matrix.jsonl").read_text().splitlines()], "operation_id", "canonical operations")
    canonical_rep_crosswalks = index([json.loads(line) for line in (CANONICAL / "representation-crosswalks.jsonl").read_text().splitlines()], "crosswalk_id", "canonical representation crosswalks")
    canonical_invalid_inferences = index([json.loads(line) for line in (CANONICAL / "invalid-inference-matrix.jsonl").read_text().splitlines()], "inference_id", "canonical invalid inferences")
    crosswalk_by_family = {}
    relation_counts = Counter()
    for cwid, record in crosswalks.items():
        fid = record.get("family_id")
        if fid not in families:
            fail(f"{cwid}: unknown family {fid}")
        if fid in crosswalk_by_family:
            fail(f"{fid}: duplicate crosswalk")
        crosswalk_by_family[fid] = record
        relation = record.get("relation")
        relation_counts[relation] += 1
        target_id = record.get("target_id")
        target_kind = record.get("target_kind")
        if relation == "missing":
            if target_id is not None or target_kind != "none":
                fail(f"{cwid}: missing relation must have null target and target_kind none")
        elif target_kind == "shape_record" and target_id not in canonical_shapes:
            fail(f"{cwid}: unresolved canonical shape {target_id}")
        elif target_kind == "type_record" and target_id not in canonical_types:
            fail(f"{cwid}: unresolved canonical type {target_id}")
        if record.get("name_equivalence_used") is not False:
            fail(f"{cwid}: name-based equivalence is forbidden")
        law_comparison = record.get("law_comparison", {})
        if law_comparison.get("conclusion") != relation:
            fail(f"{cwid}: law-comparison conclusion differs from relation")
        if relation == "equivalent":
            if not record.get("equivalence_justification"):
                fail(f"{cwid}: equivalence requires an explicit law justification")
            if law_comparison.get("abstraction_layer") != "match":
                fail(f"{cwid}: equivalent records must match abstraction layer")
        elif record.get("equivalence_justification") is not None:
            fail(f"{cwid}: non-equivalent relation must not carry equivalence justification")
        basis = {str(x).lower() for x in record.get("comparison_basis", [])}
        if not {"element/grain contract", "topology", "order/time/change laws"} <= basis:
            fail(f"{cwid}: comparison basis is not law-deep enough")
    if set(crosswalk_by_family) != set(families):
        fail("crosswalk does not contain exactly one record per family")
    required_relations = {"equivalent", "narrower", "broader", "overlap", "disjoint", "missing"}
    if not required_relations <= set(relation_counts):
        fail(f"crosswalk is missing required relations: {sorted(required_relations - set(relation_counts))}")

    ops_by_family: dict[str, list[dict]] = defaultdict(list)
    invalid_op_cells = 0
    for opid, record in operations.items():
        fid = record.get("family_id")
        if fid not in families:
            fail(f"{opid}: unknown family {fid}")
            continue
        ops_by_family[fid].append(record)
        cid = record.get("canonical_operation_id")
        if cid is not None and cid not in canonical_ops:
            fail(f"{opid}: unresolved canonical operation {cid}")
        if record.get("canonical_operation_exists") != (cid in canonical_ops if cid else False):
            fail(f"{opid}: canonical_operation_exists is inconsistent")
        if str(record.get("expected_validity", "")).startswith("invalid"):
            invalid_op_cells += 1
            if not record.get("invalid_inference"):
                fail(f"{opid}: invalid operation has no invalid inference")
    for fid in families:
        if len(ops_by_family[fid]) < 3:
            fail(f"{fid}: fewer than three operation-by-type cells")
    if invalid_op_cells < 20:
        fail(f"invalid-operation coverage gate: expected >=20, got {invalid_op_cells}")

    for aid, record in assertions.items():
        if record.get("subject_family_id") not in families:
            fail(f"{aid}: unknown subject family")
        for ref in record.get("canonical_refs", []):
            if ref not in canonical_shapes and ref not in canonical_types and ref not in canonical_ops:
                fail(f"{aid}: unresolved canonical ref {ref}")
    if len({record.get("claim") for record in assertions_list}) != len(assertions_list):
        fail("audit assertions must be explicit unique claims")

    rep_audit_findings = set()
    for audit_id, record in canonical_rep_audits.items():
        finding_id = record.get("finding_id")
        if finding_id not in representation:
            fail(f"{audit_id}: unknown representation-layer finding {finding_id}")
        rep_audit_findings.add(finding_id)
        links = record.get("canonical_crosswalk_ids", [])
        for link in links:
            if link not in canonical_rep_crosswalks:
                fail(f"{audit_id}: unresolved canonical representation crosswalk {link}")
        if record.get("coverage") == "missing" and links:
            fail(f"{audit_id}: missing coverage cannot cite canonical crosswalks")
        if record.get("coverage") != "missing" and not links:
            fail(f"{audit_id}: covered representation audit needs a canonical crosswalk")
        if record.get("name_equivalence_used") is not False:
            fail(f"{audit_id}: name-based equivalence is forbidden")
    if rep_audit_findings != set(representation):
        fail("canonical representation audit must cover every representation-layer finding exactly once")

    finding_types = {r.get("finding_type") for r in findings_list}
    if {"missing", "split", "merge", "overlap"} - finding_types:
        fail("gap findings must include missing, split, merge, and overlap")
    for collection, key, label in [(findings_list, "family_ids", "finding"), (verticals_list, "family_ids", "vertical"), (innovations_list, "family_ids", "innovation")]:
        for record in collection:
            for fid in record.get(key, []):
                if fid not in families:
                    fail(f"{label}: unknown family {fid}")
    if len({r.get("vertical") for r in verticals_list}) < 12:
        fail("vertical diversity gate: expected >=12 unrelated verticals")
    if any(not (2021 <= r.get("year", 0) <= 2026) or r.get("non_llm") is not True for r in innovations_list):
        fail("innovation records must be non-LLM and dated 2021-2026")

    forbidden = ("large language model", "llm", "generative model", "prompt data", "rag corpus", "agent memory")
    for record in families_list + innovations_list:
        searchable = " ".join(str(record.get(k, "")) for k in ("label", "description", "innovation")).lower()
        if any(term in searchable for term in forbidden):
            fail(f"generative/LLM scope leak in {record.get('family_id') or record.get('innovation_id')}")

    if saturation.get("claim") != "not_saturated" or saturation.get("independent_review_complete") is not False:
        fail("saturation report must not claim closure before independent review")
    if saturation.get("absence_of_new_category_cycles") != 0:
        fail("this first sweep cannot claim an absence-of-new-category cycle")
    if saturation.get("unseen_mass_estimate") is not None:
        fail("purposive standards sampling cannot support an unseen-mass number")
    if len(saturation.get("search_strata", [])) < 15:
        fail("saturation evidence must include >=15 search strata")

    canonical_files = snapshot.get("files", {})
    for name, details in canonical_files.items():
        path = CANONICAL / name
        if not path.exists():
            fail(f"canonical snapshot file disappeared: {name}")
        elif sha256(path) != details.get("sha256"):
            fail(f"canonical snapshot stale for {name}; rerun build_audit.py")
    expected_counts = {
        "types": len(canonical_types), "shapes": len(canonical_shapes), "operations": len(canonical_ops),
        "representation_crosswalks": len(canonical_rep_crosswalks), "invalid_inferences": len(canonical_invalid_inferences),
        "sources": len((CANONICAL / "sources.jsonl").read_text().splitlines()),
    }
    if snapshot.get("counts") != expected_counts:
        fail(f"canonical snapshot counts stale: {snapshot.get('counts')} != {expected_counts}")

    computed_counts = {
        "axes": len(axes), "candidate_families": len(families), "coverage_cells": sum(r.get("cell_count", 0) for r in tensor_list),
        "sources": len(sources), "unique_source_urls": len({record.get("url") for record in sources_list}), "canonical_crosswalks": len(crosswalks), "audit_assertions": len(assertions),
        "operation_type_cells": len(operations), "schema_posture_records": len(schema_postures), "representation_findings": len(representation), "canonical_representation_audits": len(canonical_rep_audits), "gap_findings": len(findings),
        "vertical_samples": len(verticals), "innovations_2021_2026": len(innovations),
    }
    if summary.get("counts") != computed_counts:
        fail(f"audit-summary counts do not match corpus: {summary.get('counts')} != {computed_counts}")
    if summary.get("is_competing_registry") is not False or summary.get("saturation_claim") != "not_saturated":
        fail("audit summary overclaims registry or saturation status")

    for name, expected_hash in manifest.get("files", {}).items():
        path = ROOT / name
        if not path.exists():
            fail(f"manifest file missing: {name}")
        elif sha256(path) != expected_hash:
            fail(f"manifest digest mismatch: {name}")

    if args.check_determinism and not ERRORS:
        before = {name: sha256(ROOT / name) for name in manifest.get("files", {})}
        before["manifest.json"] = sha256(ROOT / "manifest.json")
        run = subprocess.run([sys.executable, str(ROOT / "build_audit.py")], cwd=ROOT, text=True, capture_output=True)
        if run.returncode:
            fail(f"determinism rebuild failed: {run.stderr.strip() or run.stdout.strip()}")
        else:
            after = {name: sha256(ROOT / name) for name in manifest.get("files", {})}
            after["manifest.json"] = sha256(ROOT / "manifest.json")
            if before != after:
                changed = sorted(name for name in before if before[name] != after.get(name))
                fail(f"determinism gate: rebuild changed {changed}")

    report = {
        "status": "PASS" if not ERRORS else "FAIL",
        "counts": computed_counts,
        "crosswalk_relations": dict(sorted(relation_counts.items())),
        "referenced_sources": len(evidence_used),
        "distinct_publishers": len({r.get("publisher") for r in sources_list}),
        "invalid_operation_cells": invalid_op_cells,
        "canonical_snapshot": expected_counts,
        "warnings": WARNINGS,
        "errors": ERRORS,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if ERRORS else 0


if __name__ == "__main__":
    raise SystemExit(main())
