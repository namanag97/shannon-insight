#!/usr/bin/env python3
"""Reusable clean-start I/O campaign and receipt validation for one migration wave."""
from __future__ import annotations

import hashlib
import json
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def run(command: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if check and completed.returncode:
        raise SystemExit(f"command failed ({' '.join(command)}):\n{completed.stdout}{completed.stderr}")
    return completed


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_digest(root: Path, repository: Path) -> str:
    digest = hashlib.sha256()
    files = (p for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts and not p.name.endswith(".pyc"))
    for path in sorted(files):
        digest.update(path.relative_to(repository).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def restore_subject(worktree: Path, subject_commit: str) -> None:
    run(["git", "reset", "--hard", subject_commit], worktree)
    run(["git", "clean", "-fdx"], worktree)


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def run_campaign(wave: str, slug: str) -> int:
    if run(["git", "status", "--porcelain=v1", "--untracked-files=all"], ROOT).stdout.strip():
        raise SystemExit(f"{slug.upper()} campaign requires a clean canonical worktree")
    subject_commit = run(["git", "rev-parse", "HEAD"], ROOT).stdout.strip()
    selected = sorted(
        (row for row in load_jsonl(HERE / "contract-candidate-dockets.jsonl") if row["migration_wave_ref"] == wave),
        key=lambda row: row["root"],
    )
    if not selected:
        raise SystemExit(f"no package candidates found for {wave}")
    temp = Path(tempfile.mkdtemp(prefix=f"shannon-{slug}-io-"))
    worktree_added = False
    observations = []
    try:
        run(["git", "worktree", "add", "--detach", str(temp), subject_commit], ROOT)
        worktree_added = True
        tracer = "research/product_ontology/corpus_build_protocol/trace_package_io.py"
        for docket in selected:
            package_root = temp / docket["root"]
            builder_rows = []
            for builder in docket["observed_build_scripts"]:
                builder_sha = sha(temp / builder)
                traces, digests = [], []
                for _ in range(2):
                    restore_subject(temp, subject_commit)
                    completed = run(["python3", tracer, builder, "--package-root", docket["root"]], temp, check=False)
                    if not completed.stdout.strip():
                        raise SystemExit(f"trace produced no receipt for {builder}: {completed.stderr}")
                    traces.append(json.loads(completed.stdout))
                    digests.append(tree_digest(package_root, temp))
                first_io = (traces[0]["repository_read_paths"], traces[0]["repository_write_paths"])
                second_io = (traces[1]["repository_read_paths"], traces[1]["repository_write_paths"])
                builder_rows.append({
                    "builder_path": builder,
                    "builder_sha256": builder_sha,
                    "exit_codes": [row["exit_code"] for row in traces],
                    "repository_read_paths": traces[1]["repository_read_paths"],
                    "repository_write_paths": traces[1]["repository_write_paths"],
                    "outside_package_write_paths": traces[1]["outside_package_write_paths"],
                    "first_tree_sha256": digests[0],
                    "second_tree_sha256": digests[1],
                    "two_run_stable": digests[0] == digests[1] and first_io == second_io,
                })
            restore_subject(temp, subject_commit)
            before_validation = tree_digest(package_root, temp)
            validator_rows = []
            for validator in docket["observed_validate_scripts"]:
                completed = run(["python3", validator], temp, check=False)
                validator_rows.append({
                    "validator_path": validator,
                    "validator_sha256": sha(temp / validator),
                    "exit_code": completed.returncode,
                    "stdout_sha256": hashlib.sha256(completed.stdout.encode()).hexdigest(),
                })
            after_validation = tree_digest(package_root, temp)
            observations.append({
                "record_kind": "wave_package_io_determinism_observation",
                "observation_id": f"observation.{slug}." + docket["package_candidate_ref"].removeprefix("candidate."),
                "migration_wave_ref": wave,
                "subject_commit": subject_commit,
                "package_candidate_ref": docket["package_candidate_ref"],
                "package_root": docket["root"],
                "builder_observations": builder_rows,
                "validator_observations": validator_rows,
                "validators_read_only": before_validation == after_validation,
                "all_builders_two_run_stable": all(row["two_run_stable"] for row in builder_rows),
                "all_builders_exit_zero": all(row["exit_codes"] == [0, 0] for row in builder_rows),
                "all_writes_package_local": all(not row["outside_package_write_paths"] for row in builder_rows),
                "all_validators_pass": bool(validator_rows) and all(row["exit_code"] == 0 for row in validator_rows),
                "same_campaign_controlled": True,
                "independent_appraisal": False,
                "execution_authorized_for_canonical_orchestrator": False,
                "qualification_claim": False,
                "ratification_claim": False,
                "completion_claim": False,
            })
    finally:
        if worktree_added:
            run(["git", "worktree", "remove", "--force", str(temp)], ROOT, check=False)
        if temp.exists():
            shutil.rmtree(temp)

    output = "".join(canonical(row) + "\n" for row in observations)
    (HERE / f"{slug}-io-observations.jsonl").write_text(output, encoding="utf-8")
    summary = {
        "campaign_id": f"campaign.corpus-build.{slug}-io.v1",
        "migration_wave_ref": wave,
        "subject_commit": subject_commit,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "package_observations": len(observations),
        "builder_observations": sum(len(row["builder_observations"]) for row in observations),
        "validator_observations": sum(len(row["validator_observations"]) for row in observations),
        "stable_packages": sum(row["all_builders_two_run_stable"] for row in observations),
        "package_local_write_packages": sum(row["all_writes_package_local"] for row in observations),
        "validator_pass_packages": sum(row["all_validators_pass"] for row in observations),
        "independent_appraisals": 0,
        "execution_authorizations_created": 0,
        "qualification_claim": False,
        "ratification_claim": False,
        "completion_claim": False,
        "observations_sha256": hashlib.sha256(output.encode()).hexdigest(),
    }
    (HERE / f"{slug}-io-campaign-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


def validate_campaign(wave: str, slug: str) -> int:
    rows = load_jsonl(HERE / f"{slug}-io-observations.jsonl")
    summary = json.loads((HERE / f"{slug}-io-campaign-summary.json").read_text(encoding="utf-8"))
    dockets = load_jsonl(HERE / "contract-candidate-dockets.jsonl")
    expected = {row["package_candidate_ref"] for row in dockets if row["migration_wave_ref"] == wave}
    assert expected == {row["package_candidate_ref"] for row in rows}
    assert summary["migration_wave_ref"] == wave
    assert len(rows) == len({row["observation_id"] for row in rows}) == summary["package_observations"]
    assert subprocess.run(["git", "merge-base", "--is-ancestor", summary["subject_commit"], "HEAD"], cwd=ROOT).returncode == 0
    for row in rows:
        root_prefix = row["package_root"].rstrip("/") + "/"
        assert row["migration_wave_ref"] == wave
        assert row["same_campaign_controlled"] is True and row["independent_appraisal"] is False
        assert row["execution_authorized_for_canonical_orchestrator"] is False
        assert row["qualification_claim"] is False and row["ratification_claim"] is False and row["completion_claim"] is False
        assert row["all_builders_two_run_stable"] and row["all_builders_exit_zero"] and row["all_writes_package_local"]
        assert row["all_validators_pass"] and row["validators_read_only"]
        for builder in row["builder_observations"]:
            assert sha(ROOT / builder["builder_path"]) == builder["builder_sha256"]
            assert builder["first_tree_sha256"] == builder["second_tree_sha256"] and builder["two_run_stable"]
            assert builder["exit_codes"] == [0, 0] and not builder["outside_package_write_paths"]
            assert all(path.startswith(root_prefix) for path in builder["repository_write_paths"])
        for validator in row["validator_observations"]:
            assert sha(ROOT / validator["validator_path"]) == validator["validator_sha256"]
            assert validator["exit_code"] == 0
    payload = (HERE / f"{slug}-io-observations.jsonl").read_bytes()
    assert hashlib.sha256(payload).hexdigest() == summary["observations_sha256"]
    assert summary["stable_packages"] == summary["package_local_write_packages"] == summary["validator_pass_packages"] == len(rows)
    assert summary["independent_appraisals"] == summary["execution_authorizations_created"] == 0
    assert summary["qualification_claim"] is False and summary["ratification_claim"] is False and summary["completion_claim"] is False
    print(
        f"PASS {slug.upper()} I/O campaign: {len(rows)} packages rebuilt twice from clean state with package-local writes "
        "and passing read-only validators; same-campaign evidence only, execution authorization remains withheld"
    )
    return 0
