#!/usr/bin/env python3
"""Build deterministic GPT Pro session bundles and the bootstrap context task ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
DEFAULT_SAN_ROOT = Path("/Users/namanagarwal/Projects/san")
PROGRAM_REL = Path("docs/spec-inputs/programs/2026-08-13")
ATLAS_REL = PROGRAM_REL / "non-data/05-atlas/SAN-UNIVERSAL-NON-DATA-DOMAIN-ATLAS-v0.1.0.zip"
ATLAS_CONTEXT_MEMBER = (
    "SAN-UNIVERSAL-NON-DATA-DOMAIN-ATLAS-v0.1.0/contexts/bounded_contexts.jsonl"
)
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)


def attachment(
    source: str, destination: str, role: str, posture: str = "candidate_evidence"
) -> dict[str, str]:
    return {
        "source": source,
        "destination": destination,
        "role": role,
        "authority_posture": posture,
    }


METHOD_ATTACHMENTS = [
    attachment(
        "docs/SOFTWARE-DOMAIN-LIBRARY-METHOD.html",
        "method/SOFTWARE-DOMAIN-LIBRARY-METHOD.html",
        "SAN domain-to-library method candidate",
    ),
    attachment(
        "docs/PURE-LIBRARY-CONSTITUTION.html",
        "method/PURE-LIBRARY-CONSTITUTION.html",
        "SAN pure-library constitutional candidate",
    ),
    attachment(
        "docs/COMPOSABLE-PRODUCT-KERNEL.html",
        "method/COMPOSABLE-PRODUCT-KERNEL.html",
        "SAN recursive product-composition candidate",
    ),
    attachment(
        "toolkit/FAMILY-SPECS.md",
        "method/FAMILY-SPECS.md",
        "Current SAN family specification guidance",
    ),
    attachment(
        "toolkit/identifier/docs/IDENTIFIER-FAMILY-SPEC.html",
        "identifier/IDENTIFIER-FAMILY-SPEC.html",
        "High-detail semantic-family stress example",
    ),
    attachment(
        "toolkit/identifier/spec/SEM-014-CONTEXT-SPEC.json",
        "identifier/SEM-014-CONTEXT-SPEC.json",
        "Machine-readable Identifier domain-specification stress example",
    ),
    attachment(
        "toolkit/identifier/spec/SEM-014-IMPLEMENTATION-POSTURE.json",
        "identifier/SEM-014-IMPLEMENTATION-POSTURE.json",
        "Identifier specification-to-implementation posture evidence",
    ),
]


REGISTRY = attachment(
    str(PROGRAM_REL / "shared/registry/SAN-GLOBAL-PROGRAM-REGISTRY-ARCHITECTURE-EDITION-1.zip"),
    "registry/SAN-GLOBAL-PROGRAM-REGISTRY-ARCHITECTURE-EDITION-1.zip",
    "Candidate global registry and crosswalk target; not ratification evidence",
)

ATLAS = attachment(
    str(ATLAS_REL),
    "atlas/SAN-UNIVERSAL-NON-DATA-DOMAIN-ATLAS-v0.1.0.zip",
    "Current non-data atlas rebase subject and stress corpus",
)


N1_ATTACHMENTS = [REGISTRY]
for name in (
    "session-assets-resources-operations-domain-atlas.zip",
    "session-commerce-value-finance-domain-atlas.zip",
    "session-content-knowledge-experience-domain-atlas.zip",
    "session-digital-systems-runtime-operations-domain-atlas.zip",
    "session-global-domain-universe-blind-domain-discovery.zip",
    "session-industry-vertical-universe-domain-atlas.zip",
    "session-party-authority-governance-domain-atlas.zip",
    "session-runtime-resource-operations-assurance-blind-domain-discovery.zip",
    "session-ui-human-experience-blind-domain-discovery.zip",
    "session-work-process-decision-domain-atlas.zip",
):
    N1_ATTACHMENTS.append(
        attachment(
            str(PROGRAM_REL / "non-data/00-source-corpora" / name),
            f"source-corpora/{name}",
            "Independent source corpus requiring direct record reingestion",
        )
    )

for name, role in (
    (
        "session-foundational-semantics-domain-atlas.zip",
        "Adjacent foundational-semantics discovery input",
    ),
    (
        "session-language-compiler-ir-blind-domain-discovery.zip",
        "Adjacent language/compiler/IR discovery input",
    ),
):
    N1_ATTACHMENTS.append(
        attachment(
            str(PROGRAM_REL / "non-data/01-adjacent-discovery" / name),
            f"adjacent-discovery/{name}",
            role,
        )
    )

N1_ATTACHMENTS.extend(
    [
        attachment(
            str(PROGRAM_REL / "non-data/02-reconciliation/session-09a-cross-domain-reconciliation.zip"),
            "adjudication/session-09a-cross-domain-reconciliation.zip",
            "Cross-domain reconciliation evidence",
        ),
        attachment(
            str(PROGRAM_REL / "non-data/03-audits/session-09b-independent-boundary-audit-r3-active.zip"),
            "adjudication/session-09b-independent-boundary-audit-r3-active.zip",
            "Latest independent boundary-audit candidate; supersedes r1/r2 for dispatch",
        ),
        attachment(
            str(PROGRAM_REL / "non-data/04-competency/session-09c-cross-domain-competency-suite.zip"),
            "adjudication/session-09c-cross-domain-competency-suite.zip",
            "Cross-domain competency and scenario candidate",
        ),
        ATLAS,
    ]
)


S2_EXTRA_ATTACHMENTS = [
    attachment(
        str(PROGRAM_REL / "shared/compiler/SAN-COMPILER-DOMAIN-MODELING-ADJUDICATION-SSPEC-EDITION-2-REVIEW-CANDIDATE.zip"),
        "compiler/SAN-COMPILER-DOMAIN-MODELING-ADJUDICATION-SSPEC-EDITION-2-REVIEW-CANDIDATE.zip",
        "Current compiler/domain-modeling adjudication candidate",
    ),
    attachment(
        str(PROGRAM_REL / "shared/compiler/SAN-CROSS-REGISTRY-COMPOSABILITY-IR-EXECUTION-CLOSURE-REVIEW-CANDIDATE-2026-08-12.zip"),
        "compiler/SAN-CROSS-REGISTRY-COMPOSABILITY-IR-EXECUTION-CLOSURE-REVIEW-CANDIDATE-2026-08-12.zip",
        "Cross-registry composition, IR, and execution-closure review candidate",
    ),
    attachment(
        str(PROGRAM_REL / "shared/compiler/SAN-CON-CMP-STAGE0-CORRECTION-PROPOSED-2026-08-12.zip"),
        "compiler/SAN-CON-CMP-STAGE0-CORRECTION-PROPOSED-2026-08-12.zip",
        "Proposed constitutional/compiler stage-zero correction",
    ),
    attachment(
        str(PROGRAM_REL / "shared/compiler/SAN-GPT-B-COMPILER-ADVERSARIAL-ADJUDICATION-2026-08-12.zip"),
        "compiler/SAN-GPT-B-COMPILER-ADVERSARIAL-ADJUDICATION-2026-08-12.zip",
        "Adversarial compiler adjudication candidate",
    ),
    attachment(
        str(PROGRAM_REL / "data-analytics/05-library-candidates/SAN-DATA-SOVEREIGN-LIBRARIES-EDITION-1-REVIEW-CANDIDATE.zip"),
        "stress-inputs/SAN-DATA-SOVEREIGN-LIBRARIES-EDITION-1-REVIEW-CANDIDATE.zip",
        "Non-authoritative data-library stress candidate",
    ),
    attachment(
        str(PROGRAM_REL / "data-analytics/05-library-candidates/SAN-DATA-SOVEREIGN-LIBRARIES-EDITION-1-REVIEW-CANDIDATE.zip.sha256"),
        "stress-inputs/SAN-DATA-SOVEREIGN-LIBRARIES-EDITION-1-REVIEW-CANDIDATE.zip.sha256",
        "Published checksum sidecar for the data-library stress candidate",
        "integrity_metadata",
    ),
]


SESSIONS = {
    "N1-atlas-rebase": {
        "purpose": "Globally researched non-data domain atlas v0.2.0 release candidate",
        "expected_return": "SAN-UNIVERSAL-NON-DATA-DOMAIN-ATLAS-v0.2.0-RC.zip",
        "attachments": N1_ATTACHMENTS,
    },
    "S1-semantic-contract": {
        "purpose": "Independent sovereign semantic-domain definition contract candidate",
        "expected_return": "candidate-a-sovereign-domain-semantic-contract-v0.1.0.zip",
        "attachments": METHOD_ATTACHMENTS + [REGISTRY, ATLAS],
    },
    "S2-library-compiler-contract": {
        "purpose": "Independent library, composition, and compiler contract candidate",
        "expected_return": "candidate-b-library-composition-compiler-contract-v0.1.0.zip",
        "attachments": METHOD_ATTACHMENTS + [REGISTRY, ATLAS] + S2_EXTRA_ATTACHMENTS,
    },
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def build_bootstrap_tasks(san_root: Path) -> int:
    atlas_path = san_root / ATLAS_REL
    task_path = ROOT / "planner/context-tasks.bootstrap.jsonl"
    records: list[dict[str, Any]] = []
    with zipfile.ZipFile(atlas_path) as archive:
        raw_lines = archive.read(ATLAS_CONTEXT_MEMBER).decode("utf-8").splitlines()
    for raw in raw_lines:
        if not raw.strip():
            continue
        context = json.loads(raw)
        issues = list(context.get("remaining_uncertainty", []))
        ownership = context.get("ownership_status")
        if ownership in {"UNRESOLVED", "CONTESTED"}:
            issues.append(f"Ownership posture is {ownership} in the v0.1.0 candidate.")
        boundary = context.get("boundary_evaluation", {})
        if boundary.get("partial_count", 0):
            issues.append(
                f"Boundary evaluation has {boundary['partial_count']} PARTIAL criterion/criteria."
            )
        if boundary.get("fail_count", 0):
            issues.append(
                f"Boundary evaluation has {boundary['fail_count']} FAIL criterion/criteria."
            )
        stages = []
        for name in STAGE_NAMES:
            if name == "research_intake":
                state = "complete"
                required = ["source_context_record"]
                result_refs = [context["id"]]
            elif name == "evidence_review":
                state = "ready"
                required = ["N1_rebase_evidence", "claim_level_source_lineage"]
                result_refs = []
            else:
                state = "not_started"
                required = []
                result_refs = []
            stages.append(
                {
                    "name": name,
                    "state": state,
                    "required_evidence": required,
                    "result_refs": result_refs,
                    "notes": "",
                }
            )
        task = {
            "task_id": f"task.bootstrap.{context['id']}",
            "task_kind": "bounded_context",
            "subject_id": context["id"],
            "subject_name": context.get("canonical_name", context["id"]),
            "source_edition": "SAN-UNIVERSAL-NON-DATA-DOMAIN-ATLAS-v0.1.0",
            "source_status": context.get("status"),
            "authority_posture": "discovered_candidate",
            "architecture_disposition": "unresolved",
            "current_gate": "evidence_review",
            "stages": stages,
            "dependencies": ["program.N1", "program.N2", "program.S3", "program.W1"],
            "evidence_refs": sorted(set(context.get("evidence_refs", []))),
            "open_issues": sorted(set(issues)),
            "lineage": [],
            "next_admissible_action": (
                "Reconcile this provisional v0.1.0 candidate with the N1 v0.2.0 record and "
                "the N2 disposition; preserve explicit merge, split, reject, or supersession lineage."
            ),
            "updated_at": None,
        }
        records.append(task)
    records.sort(key=lambda item: item["subject_id"])
    task_path.write_text(
        "".join(json.dumps(item, sort_keys=True, ensure_ascii=False) + "\n" for item in records),
        encoding="utf-8",
    )
    return len(records)


def deterministic_zip(source_dir: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(path for path in source_dir.rglob("*") if path.is_file())
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            relative = path.relative_to(source_dir.parent).as_posix()
            info = zipfile.ZipInfo(relative, FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compresslevel=9)


def build_session(san_root: Path, session_id: str, config: dict[str, Any]) -> dict[str, Any]:
    session_dir = ROOT / "sessions" / session_id
    attachments_dir = session_dir / "ATTACHMENTS"
    if attachments_dir.exists():
        shutil.rmtree(attachments_dir)
    attachments_dir.mkdir(parents=True)

    shutil.copy2(ROOT / "BASE-RESEARCH-CONSTITUTION.md", session_dir / "BASE-RESEARCH-CONSTITUTION.md")
    shutil.copy2(ROOT / "program/PROGRAM-DAG.md", session_dir / "PROGRAM-DAG.md")
    shutil.copy2(ROOT / "program/ARTIFACT-CONTRACT.md", session_dir / "ARTIFACT-CONTRACT.md")

    manifest_files = []
    for item in config["attachments"]:
        source = san_root / item["source"]
        if not source.is_file():
            raise FileNotFoundError(source)
        destination = attachments_dir / item["destination"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        manifest_files.append(
            {
                "path": str(destination.relative_to(session_dir)),
                "origin": item["source"],
                "role": item["role"],
                "authority_posture": item["authority_posture"],
                "bytes": destination.stat().st_size,
                "sha256": sha256(destination),
            }
        )

    manifest = {
        "manifest_version": "0.1.0",
        "session_id": session_id,
        "purpose": config["purpose"],
        "expected_return": config["expected_return"],
        "independence_rule": (
            "Use only this session package, globally researched Internet evidence, and no output "
            "from either parallel independent contract candidate session."
        ),
        "control_files": [
            {
                "path": name,
                "bytes": (session_dir / name).stat().st_size,
                "sha256": sha256(session_dir / name),
            }
            for name in (
                "PROMPT.md",
                "BASE-RESEARCH-CONSTITUTION.md",
                "PROGRAM-DAG.md",
                "ARTIFACT-CONTRACT.md",
            )
        ],
        "attachments": manifest_files,
    }
    write_json(session_dir / "ATTACHMENT-MANIFEST.json", manifest)

    upload_path = ROOT / "send" / f"SAN-GPT-PRO-{session_id}-2026-08-13.zip"
    deterministic_zip(session_dir, upload_path)
    return {
        "session_id": session_id,
        "purpose": config["purpose"],
        "expected_return": config["expected_return"],
        "directory": str(session_dir.relative_to(ROOT)),
        "upload_zip": str(upload_path.relative_to(ROOT)),
        "upload_zip_bytes": upload_path.stat().st_size,
        "upload_zip_sha256": sha256(upload_path),
        "attachment_count": len(manifest_files),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--san-root", type=Path, default=DEFAULT_SAN_ROOT)
    args = parser.parse_args()
    san_root = args.san_root.resolve()
    if not (san_root / ".git").exists():
        raise SystemExit(f"SAN root does not look like a repository: {san_root}")

    context_task_count = build_bootstrap_tasks(san_root)
    sessions = [build_session(san_root, key, value) for key, value in SESSIONS.items()]
    dispatch_manifest = {
        "manifest_version": "0.1.0",
        "program": "SAN domain-to-library-to-compiler research program",
        "dispatch_date": "2026-08-13",
        "bootstrap_context_task_count": context_task_count,
        "sessions": sessions,
    }
    write_json(ROOT / "DISPATCH-MANIFEST.json", dispatch_manifest)

    from verify_dispatch import verify

    verify(ROOT)
    print(json.dumps(dispatch_manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
