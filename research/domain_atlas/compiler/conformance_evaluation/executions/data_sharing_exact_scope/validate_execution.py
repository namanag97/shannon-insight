from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RECEIPT = HERE / "runs" / "run-20260827-linux-x86_64-python3_13-001" / "receipt.json"
MANIFEST = HERE / "manifest.json"


def sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def execute() -> tuple[bytes, bytes]:
    run = subprocess.run([sys.executable, str(HERE / "run_execution.py")], cwd=HERE, text=True, capture_output=True)
    if run.returncode:
        raise RuntimeError(run.stdout.strip() or run.stderr.strip())
    return RECEIPT.read_bytes(), MANIFEST.read_bytes()


def main() -> int:
    errors: list[str] = []
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

    receipt = json.loads(second_receipt)
    manifest = json.loads(second_manifest)
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
        path = HERE / name
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != metadata["sha256"] or len(data) != metadata["bytes"]:
            errors.append(f"manifest digest drift: {name}")

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
