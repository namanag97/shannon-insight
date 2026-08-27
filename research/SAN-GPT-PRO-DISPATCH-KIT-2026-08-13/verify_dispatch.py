#!/usr/bin/env python3
"""Dependency-free verification for the SAN GPT Pro dispatch kit."""

from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path
from typing import Any


REQUIRED_TASK_KEYS = {
    "task_id",
    "task_kind",
    "subject_id",
    "subject_name",
    "authority_posture",
    "architecture_disposition",
    "current_gate",
    "stages",
    "dependencies",
    "evidence_refs",
    "open_issues",
    "next_admissible_action",
}
ALLOWED_TASK_KEYS = REQUIRED_TASK_KEYS | {
    "source_edition",
    "source_status",
    "lineage",
    "updated_at",
}
TASK_KINDS = {
    "program_gate",
    "domain_family",
    "bounded_context",
    "library_family",
    "proof_vertical",
}
AUTHORITY_POSTURES = {
    "hypothesis",
    "discovered_candidate",
    "source_supported",
    "boundary_qualified",
    "adjudicated",
    "specified",
    "implemented",
    "structurally_verified",
    "semantically_verified",
    "compiler_integrated",
    "runtime_observed",
    "independently_audited",
    "ratified",
    "certified",
    "rejected",
    "superseded",
}
ARCHITECTURE_DISPOSITIONS = {
    "unresolved",
    "semantic_library_family",
    "effect_or_mechanism_library",
    "interface_or_contract_only",
    "profile",
    "composition_or_card",
    "application_or_product_package",
    "provider_adapter",
    "compiler_or_tooling_unit",
    "research_only",
    "reject",
}
STAGE_NAMES = [
    "research_intake",
    "evidence_review",
    "boundary_adjudication",
    "atlas_acceptance",
    "domain_forge",
    "domain_audit",
    "architecture_disposition",
    "library_forge",
    "library_audit",
    "reference_implementation",
    "conformance",
    "registry_admission",
    "compiler_contribution",
    "portable_closure",
    "target_lowering",
    "runtime_provider_binding",
    "vertical_proof",
    "independent_audit",
    "ratification",
]
STAGE_STATES = {
    "not_started",
    "ready",
    "in_progress",
    "complete",
    "deferred",
    "blocked",
    "rejected",
    "not_applicable",
}
ALLOWED_STAGE_KEYS = {"name", "state", "required_evidence", "result_refs", "notes"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as error:
            raise ValueError(f"{path}:{line_number}: {error}") from error
        missing = REQUIRED_TASK_KEYS - set(value)
        if missing:
            raise ValueError(f"{path}:{line_number}: missing task keys {sorted(missing)}")
        extra = set(value) - ALLOWED_TASK_KEYS
        if extra:
            raise ValueError(f"{path}:{line_number}: unknown task keys {sorted(extra)}")
        if value["task_kind"] not in TASK_KINDS:
            raise ValueError(f"{path}:{line_number}: invalid task kind {value['task_kind']}")
        if value["authority_posture"] not in AUTHORITY_POSTURES:
            raise ValueError(
                f"{path}:{line_number}: invalid authority posture {value['authority_posture']}"
            )
        if value["architecture_disposition"] not in ARCHITECTURE_DISPOSITIONS:
            raise ValueError(
                f"{path}:{line_number}: invalid architecture disposition "
                f"{value['architecture_disposition']}"
            )
        stage_names = [stage["name"] for stage in value["stages"]]
        if len(stage_names) != len(set(stage_names)):
            raise ValueError(f"{path}:{line_number}: duplicate task stages")
        if value["current_gate"] not in stage_names:
            raise ValueError(f"{path}:{line_number}: current gate not present in stages")
        if unknown_stages := set(stage_names) - set(STAGE_NAMES):
            raise ValueError(f"{path}:{line_number}: unknown stages {sorted(unknown_stages)}")
        stage_positions = [STAGE_NAMES.index(name) for name in stage_names]
        if stage_positions != sorted(stage_positions):
            raise ValueError(f"{path}:{line_number}: task stages are not in canonical order")
        for stage in value["stages"]:
            if extra_stage_keys := set(stage) - ALLOWED_STAGE_KEYS:
                raise ValueError(
                    f"{path}:{line_number}: unknown stage keys {sorted(extra_stage_keys)}"
                )
            if stage.get("state") not in STAGE_STATES:
                raise ValueError(
                    f"{path}:{line_number}: invalid state {stage.get('state')} for {stage['name']}"
                )
            if not isinstance(stage.get("required_evidence"), list):
                raise ValueError(
                    f"{path}:{line_number}: required_evidence must be an array for {stage['name']}"
                )
        for key in ("dependencies", "evidence_refs", "open_issues"):
            if not isinstance(value[key], list) or len(value[key]) != len(set(value[key])):
                raise ValueError(f"{path}:{line_number}: {key} must be a unique array")
        if not str(value["next_admissible_action"]).strip():
            raise ValueError(f"{path}:{line_number}: next_admissible_action is empty")
        records.append(value)
    ids = [record["task_id"] for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{path}: duplicate task IDs")
    return records


def verify_session(root: Path, session: dict[str, Any]) -> None:
    session_dir = root / session["directory"]
    manifest_path = session_dir / "ATTACHMENT-MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["session_id"] != session["session_id"]:
        raise ValueError(f"session ID mismatch in {manifest_path}")
    declared = set()
    for section in ("control_files", "attachments"):
        for item in manifest[section]:
            path = session_dir / item["path"]
            if not path.is_file():
                raise FileNotFoundError(path)
            if path.stat().st_size != item["bytes"]:
                raise ValueError(f"size mismatch: {path}")
            if sha256(path) != item["sha256"]:
                raise ValueError(f"digest mismatch: {path}")
            declared.add(item["path"])
    actual_attachments = {
        str(path.relative_to(session_dir))
        for path in (session_dir / "ATTACHMENTS").rglob("*")
        if path.is_file()
    }
    declared_attachments = {item["path"] for item in manifest["attachments"]}
    if actual_attachments != declared_attachments:
        raise ValueError(
            f"attachment manifest mismatch in {session_dir}: "
            f"missing={sorted(actual_attachments - declared_attachments)} "
            f"extra={sorted(declared_attachments - actual_attachments)}"
        )
    upload = root / session["upload_zip"]
    if sha256(upload) != session["upload_zip_sha256"]:
        raise ValueError(f"upload ZIP digest mismatch: {upload}")
    with zipfile.ZipFile(upload) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"bad ZIP member {bad} in {upload}")
        zip_files = {name for name in archive.namelist() if not name.endswith("/")}
    expected_files = {
        f"{session_dir.name}/{path.name}"
        for path in session_dir.iterdir()
        if path.is_file()
    }
    expected_files.update(
        f"{session_dir.name}/{path.relative_to(session_dir).as_posix()}"
        for path in (session_dir / "ATTACHMENTS").rglob("*")
        if path.is_file()
    )
    if zip_files != expected_files:
        raise ValueError(
            f"upload ZIP content mismatch: {upload}: "
            f"missing={sorted(expected_files - zip_files)} extra={sorted(zip_files - expected_files)}"
        )


def verify(root: Path) -> None:
    required = [
        root / "README.md",
        root / "BASE-RESEARCH-CONSTITUTION.md",
        root / "program/PROGRAM-DAG.md",
        root / "program/ARTIFACT-CONTRACT.md",
        root / "planner/task-ledger.schema.json",
        root / "planner/program-tasks.jsonl",
        root / "planner/context-tasks.bootstrap.jsonl",
        root / "DISPATCH-MANIFEST.json",
    ]
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(path)
    json.loads((root / "planner/task-ledger.schema.json").read_text(encoding="utf-8"))
    program_tasks = load_jsonl(root / "planner/program-tasks.jsonl")
    context_tasks = load_jsonl(root / "planner/context-tasks.bootstrap.jsonl")
    if len(context_tasks) != 275:
        raise ValueError(f"expected 275 bootstrap context tasks, found {len(context_tasks)}")
    manifest = json.loads((root / "DISPATCH-MANIFEST.json").read_text(encoding="utf-8"))
    if manifest["bootstrap_context_task_count"] != len(context_tasks):
        raise ValueError("dispatch manifest bootstrap task count mismatch")
    for session in manifest["sessions"]:
        verify_session(root, session)
    print(
        json.dumps(
            {
                "status": "PASS",
                "program_tasks": len(program_tasks),
                "bootstrap_context_tasks": len(context_tasks),
                "sessions": len(manifest["sessions"]),
                "session_attachments": {
                    session["session_id"]: session["attachment_count"]
                    for session in manifest["sessions"]
                },
            },
            indent=2,
            sort_keys=True,
        )
    )


def main() -> None:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent
    verify(root)


if __name__ == "__main__":
    main()
