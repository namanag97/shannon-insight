#!/usr/bin/env python3
"""Execute the M01 universe/evidence I/O and determinism campaign in a disposable worktree."""
from __future__ import annotations

import hashlib
import json
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WAVE = "M01_UNIVERSE_AND_EVIDENCE_PRODUCERS"


def run(command: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if check and completed.returncode:
        raise SystemExit(f"command failed ({' '.join(command)}):\n{completed.stdout}{completed.stderr}")
    return completed


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_digest(root: Path, repository: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts and not p.name.endswith(".pyc")):
        digest.update(path.relative_to(repository).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def restore_subject(worktree: Path, subject_commit: str) -> None:
    """Restore the disposable worktree before every observed execution.

    Comparing two executions over the same mutated tree would establish only
    idempotence.  Starting both executions at the identical commit binds the
    observation to clean-start reproducibility instead.
    """
    run(["git", "reset", "--hard", subject_commit], worktree)
    run(["git", "clean", "-fdx"], worktree)


def main() -> int:
    if run(["git", "status", "--porcelain=v1", "--untracked-files=all"], ROOT).stdout.strip():
        raise SystemExit("M01 campaign requires a clean canonical worktree")
    subject_commit = run(["git", "rev-parse", "HEAD"], ROOT).stdout.strip()
    dockets = [
        json.loads(line)
        for line in (HERE / "contract-candidate-dockets.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    selected = sorted((row for row in dockets if row["migration_wave_ref"] == WAVE), key=lambda row: row["root"])
    temp = Path(tempfile.mkdtemp(prefix="shannon-m01-io-"))
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
                traces = []
                digests = []
                for _ in range(2):
                    restore_subject(temp, subject_commit)
                    completed = run(["python3", tracer, builder, "--package-root", docket["root"]], temp, check=False)
                    if not completed.stdout.strip():
                        raise SystemExit(f"trace produced no receipt for {builder}: {completed.stderr}")
                    receipt = json.loads(completed.stdout)
                    traces.append(receipt)
                    digests.append(tree_digest(package_root, temp))
                stable = digests[0] == digests[1] and {
                    (row["path"], row["access"])
                    for row in ([{"path": p, "access": "read"} for p in traces[0]["repository_read_paths"]] + [{"path": p, "access": "write"} for p in traces[0]["repository_write_paths"]])
                } == {
                    (row["path"], row["access"])
                    for row in ([{"path": p, "access": "read"} for p in traces[1]["repository_read_paths"]] + [{"path": p, "access": "write"} for p in traces[1]["repository_write_paths"]])
                }
                builder_rows.append({
                    "builder_path": builder,
                    "builder_sha256": builder_sha,
                    "exit_codes": [row["exit_code"] for row in traces],
                    "repository_read_paths": traces[1]["repository_read_paths"],
                    "repository_write_paths": traces[1]["repository_write_paths"],
                    "outside_package_write_paths": traces[1]["outside_package_write_paths"],
                    "first_tree_sha256": digests[0],
                    "second_tree_sha256": digests[1],
                    "two_run_stable": stable,
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
                "record_kind": "m01_package_io_determinism_observation",
                "observation_id": "observation.m01." + docket["package_candidate_ref"].removeprefix("candidate."),
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
    (HERE / "m01-io-observations.jsonl").write_text(output, encoding="utf-8")
    summary = {
        "campaign_id": "campaign.corpus-build.m01-io.v1",
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
    (HERE / "m01-io-campaign-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
