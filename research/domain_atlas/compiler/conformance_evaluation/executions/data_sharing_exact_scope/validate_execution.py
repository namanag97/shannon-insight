from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RECEIPT = HERE / "runs" / "run-20260827-linux-x86_64-python3_13-001" / "receipt.json"
MANIFEST = HERE / "manifest.json"
REPO_ROOT = HERE.parents[5]
CANONICAL_CONTRACTS = REPO_ROOT / "research" / "product_ontology" / "adjudications" / "lakehouse" / "library-contracts.jsonl"
QUALIFICATION_SUBJECTS = REPO_ROOT / "research" / "product_ontology" / "qualification_program" / "library-qualification-subjects.jsonl"


def sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def execute() -> tuple[bytes, bytes]:
    # The retained receipt is immutable evidence from a named Linux/CPython occurrence.
    # Execute a byte-identical copy so validation on another host cannot overwrite it.
    with tempfile.TemporaryDirectory(prefix="data-sharing-execution-") as temp:
        copy = Path(temp) / HERE.name
        shutil.copytree(HERE, copy)
        run = subprocess.run([sys.executable, str(copy / "run_execution.py")], cwd=copy, text=True, capture_output=True)
        if run.returncode:
            raise RuntimeError(run.stdout.strip() or run.stderr.strip())
        receipt = copy / "runs" / RECEIPT.parent.name / RECEIPT.name
        return receipt.read_bytes(), (copy / "manifest.json").read_bytes()


def find_jsonl(path: Path, key: str, value: str) -> dict:
    records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    matches = [record for record in records if record.get(key) == value]
    if len(matches) != 1:
        raise ValueError(f"expected one {key}={value} in {path}, found {len(matches)}")
    return matches[0]


def main() -> int:
    errors: list[str] = []
    retained_receipt = RECEIPT.read_bytes()
    retained_manifest = MANIFEST.read_bytes()
    try:
        first_receipt, first_manifest = execute()
        second_receipt, second_manifest = execute()
    except Exception as exc:
        print("ERROR: execution failed: " + str(exc))
        return 1

    if first_receipt != second_receipt:
        errors.append("receipt is not byte-for-byte deterministic")
    if first_manifest != second_manifest:
        errors.append("manifest is not byte-for-byte deterministic")
    if RECEIPT.read_bytes() != retained_receipt or MANIFEST.read_bytes() != retained_manifest:
        errors.append("validation mutated retained execution evidence")

    receipt = json.loads(second_receipt)
    manifest = json.loads(second_manifest)
    retained = json.loads(retained_receipt)
    if retained.get("environment", {}).get("python") != "3.13.5" or "Linux" not in retained.get("environment", {}).get("platform", ""):
        errors.append("retained occurrence identity no longer matches its path")
    if receipt["verdict"] != "PASS_EXECUTED_TESTS_NOT_QUALIFIED":
        errors.append("unexpected execution verdict")
    if any(receipt["promotion_claims"].values()):
        errors.append("execution illegally promoted qualification/build-ready/ratification")
    if receipt["implementation_controls"]["independently_controlled"]:
        errors.append("same-campaign implementations cannot claim independent control")
    if len(receipt["implementations"]) != 2 or any(row["verdict"] != "PASS" or row["case_count"] != 12 for row in receipt["implementations"]):
        errors.append("both 12-case implementation suites must pass")
    if len(receipt["differential"]) != 3 or any(row["verdict"] != "PASS" for row in receipt["differential"]):
        errors.append("three cross-implementation differential cases must pass")
    expected_refusals = {"provider_authority_missing", "shared_cut_unresolved", "recipient_unresolved", "purpose_unbound", "policy_refused", "grant_expired_or_revoked", "recall_incomplete", "export_incomplete"}
    if set(receipt["scope"]["refusals_exercised"]) != expected_refusals:
        errors.append("refusal coverage drift")
    for name, recorded in receipt["source_digests"].items():
        if sha(HERE / name) != recorded:
            errors.append(f"source digest mismatch: {name}")

    if manifest.get("qualification_claim") is not False:
        errors.append("manifest made an unsupported qualification claim")
    expected_counts = {"implementations": 2, "implementation_cases": 24, "differential_cases": 3, "refusal_classes": 8}
    if manifest.get("counts") != expected_counts:
        errors.append("manifest execution counts drift")
    for name, metadata in manifest.get("files", {}).items():
        data = second_receipt if name == str(RECEIPT.relative_to(HERE)) else (HERE / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != metadata["sha256"] or len(data) != metadata["bytes"]:
            errors.append(f"manifest digest drift: {name}")

    retained_manifest_value = json.loads(retained_manifest)
    for name, metadata in retained_manifest_value.get("files", {}).items():
        path = HERE / name
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != metadata["sha256"] or len(data) != metadata["bytes"]:
            errors.append(f"retained manifest digest drift: {name}")

    protocol = json.loads((HERE / "protocol.json").read_text(encoding="utf-8"))
    try:
        canonical_contract = find_jsonl(CANONICAL_CONTRACTS, "library_id", protocol["abstract_contract_ref"])
        subject = find_jsonl(QUALIFICATION_SUBJECTS, "subject_id", "subject.qp.data_sharing.data_sharing_contract")
    except (KeyError, ValueError) as exc:
        errors.append("canonical scope resolution failed: " + str(exc))
    else:
        exercised_axes = ("decisions", "operations", "invariants", "refusals")
        if any(protocol["exact_contract"].get(axis) != canonical_contract.get(axis) for axis in exercised_axes):
            errors.append("protocol exercised scope differs from canonical abstract contract")
        if any(subject.get("contract", {}).get(axis) != canonical_contract.get(axis) for axis in ("types", "decisions", "operations", "invariants", "refusals", "dependencies")):
            errors.append("qualification subject differs from canonical abstract contract")
        projection_refs = subject.get("compiler_projection", {}).get("concrete_library_refs")
        if subject.get("product_ref") != protocol.get("product_ref") or projection_refs != [protocol.get("canonical_projection_ref")]:
            errors.append("protocol product or concrete projection differs from qualification subject")

    binding = json.loads((HERE / "qualification-binding.json").read_text(encoding="utf-8"))
    if binding["gate_effect"] != "EVIDENCE_PRESENT_PREREQUISITES_OPEN_NOT_A_PASS":
        errors.append("qualification binding must not promote the exact-scope gate")
    if any(binding[key] for key in ("independent_appraisal", "portable_offer", "build_ready", "ratified")) or binding["qualified_implementation_count"] != 0:
        errors.append("qualification binding contains an unsupported promotion")

    if errors:
        for error in errors:
            print("ERROR: " + error)
        return 1
    print("PASS data-sharing exact-scope execution: 24 implementation cases + 3 differential cases + 8 refusal classes; deterministic; not qualified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
