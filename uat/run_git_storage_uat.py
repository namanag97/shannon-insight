#!/usr/bin/env python3
"""Run git storage UAT on all test codebases.

Tests:
1. Extraction accuracy (commit count, file churn, authors)
2. Performance benchmarks
3. Database storage and query performance

Usage:
    python uat/run_git_storage_uat.py
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from shannon_insight.persistence.git_facts import GitFactDatabase
from shannon_insight.persistence.git_models import GitExtractionSession
from shannon_insight.temporal.git_raw_extractor import GitRawExtractor


@dataclass
class UATResult:
    """Result for a single codebase."""
    name: str
    commit_count: int
    file_change_count: int
    extraction_time: float
    db_insert_time: float
    total_additions: int
    total_deletions: int
    rename_count: int
    binary_count: int
    unique_authors: int
    churn_query_ms: float
    passed: bool
    error: str | None = None


def run_git(repo_path: str, args: list[str]) -> str:
    """Run git command and return output."""
    result = subprocess.run(
        ["git", "-C", repo_path] + args,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return result.stdout


def test_codebase(repo_path: Path, max_commits: int = 5000) -> UATResult:
    """Run UAT on a single codebase."""
    name = repo_path.name

    try:
        # Extract git data
        extractor = GitRawExtractor(str(repo_path), max_commits=max_commits)

        t0 = time.perf_counter()
        data = extractor.extract()
        extraction_time = time.perf_counter() - t0

        if data is None:
            return UATResult(
                name=name,
                commit_count=0,
                file_change_count=0,
                extraction_time=0,
                db_insert_time=0,
                total_additions=0,
                total_deletions=0,
                rename_count=0,
                binary_count=0,
                unique_authors=0,
                churn_query_ms=0,
                passed=False,
                error="Failed to extract git data",
            )

        # Calculate stats
        total_additions = sum(
            fc.additions or 0 for fc in data.file_changes if fc.additions is not None
        )
        total_deletions = sum(
            fc.deletions or 0 for fc in data.file_changes if fc.deletions is not None
        )
        rename_count = sum(1 for fc in data.file_changes if fc.old_path is not None)
        binary_count = sum(1 for fc in data.file_changes if fc.is_binary)
        unique_authors = len({c.author_email for c in data.commits})

        # Store in temp DB
        with tempfile.TemporaryDirectory() as tmpdir:
            db = GitFactDatabase(Path(tmpdir) / "test.db")
            session = GitExtractionSession(
                id=str(uuid4()),
                repo_path=str(repo_path),
                started_at=datetime.now(timezone.utc),
                completed_at=None,
                head_sha=data.head_sha,
                oldest_sha=data.oldest_sha,
                commit_count=0,
                file_change_count=0,
                status="running",
            )
            db.create_session(session)

            t0 = time.perf_counter()
            db.store_commits_batch(data.commits, session.id)
            db.store_file_changes_batch(data.file_changes)
            db_insert_time = time.perf_counter() - t0

            # Test query performance
            if data.file_changes:
                sample_files = list({fc.file_path for fc in data.file_changes})[:10]
                t0 = time.perf_counter()
                for f in sample_files:
                    db.get_file_churn(f)
                churn_query_ms = (time.perf_counter() - t0) * 1000 / len(sample_files)
            else:
                churn_query_ms = 0

            # Validate commit count against git
            actual_count = int(run_git(str(repo_path), ["rev-list", "--count", "HEAD"]).strip())
            commit_count_valid = data.commit_count <= actual_count

            # Validate a sample file's churn
            churn_valid = True
            if sample_files:
                sample_file = sample_files[0]
                db_churn = db.get_file_churn(sample_file)

                # Get from git
                output = run_git(str(repo_path), [
                    "log", "--numstat", "--format=", "--follow", "--", sample_file
                ])
                git_changes = sum(1 for line in output.strip().split("\n") if line.strip() and "\t" in line)
                churn_valid = db_churn["change_count"] == git_changes

        return UATResult(
            name=name,
            commit_count=data.commit_count,
            file_change_count=data.file_change_count,
            extraction_time=extraction_time,
            db_insert_time=db_insert_time,
            total_additions=total_additions,
            total_deletions=total_deletions,
            rename_count=rename_count,
            binary_count=binary_count,
            unique_authors=unique_authors,
            churn_query_ms=churn_query_ms,
            passed=commit_count_valid and churn_valid,
            error=None if (commit_count_valid and churn_valid) else "Validation failed",
        )

    except Exception as e:
        return UATResult(
            name=name,
            commit_count=0,
            file_change_count=0,
            extraction_time=0,
            db_insert_time=0,
            total_additions=0,
            total_deletions=0,
            rename_count=0,
            binary_count=0,
            unique_authors=0,
            churn_query_ms=0,
            passed=False,
            error=str(e),
        )


def print_results(results: list[UATResult]) -> None:
    """Print UAT results table."""
    print("\n" + "=" * 120)
    print("GIT STORAGE UAT RESULTS")
    print("=" * 120)

    # Header
    print(f"\n{'Codebase':<15} {'Commits':>8} {'Changes':>8} {'Extract':>8} {'DB Insert':>9} "
          f"{'Adds':>10} {'Dels':>10} {'Renames':>8} {'Binary':>7} {'Authors':>8} {'Query':>8} {'Status':>8}")
    print("-" * 120)

    for r in results:
        status = "✓ PASS" if r.passed else "✗ FAIL"
        print(f"{r.name:<15} {r.commit_count:>8} {r.file_change_count:>8} "
              f"{r.extraction_time:>7.2f}s {r.db_insert_time:>8.3f}s "
              f"{r.total_additions:>10,} {r.total_deletions:>10,} "
              f"{r.rename_count:>8} {r.binary_count:>7} {r.unique_authors:>8} "
              f"{r.churn_query_ms:>6.2f}ms {status:>8}")

    print("-" * 120)

    # Totals
    total_commits = sum(r.commit_count for r in results)
    total_changes = sum(r.file_change_count for r in results)
    total_adds = sum(r.total_additions for r in results)
    total_dels = sum(r.total_deletions for r in results)
    total_renames = sum(r.rename_count for r in results)
    total_binary = sum(r.binary_count for r in results)
    total_authors = sum(r.unique_authors for r in results)
    avg_extract = sum(r.extraction_time for r in results) / len(results)
    avg_insert = sum(r.db_insert_time for r in results) / len(results)
    avg_query = sum(r.churn_query_ms for r in results) / len(results)
    passed = sum(1 for r in results if r.passed)

    print(f"{'TOTAL':<15} {total_commits:>8} {total_changes:>8} "
          f"{avg_extract:>7.2f}s {avg_insert:>8.3f}s "
          f"{total_adds:>10,} {total_dels:>10,} "
          f"{total_renames:>8} {total_binary:>7} {total_authors:>8} "
          f"{avg_query:>6.2f}ms {passed}/{len(results):>5}")

    print("\n" + "=" * 120)

    # Failed tests
    failed = [r for r in results if not r.passed]
    if failed:
        print("\nFailed tests:")
        for r in failed:
            print(f"  - {r.name}: {r.error}")
    else:
        print(f"\n✓ All {len(results)} codebases passed!")


def main():
    """Run UAT on all codebases."""
    uat_dir = Path(__file__).parent
    codebases_dir = uat_dir / "codebases"

    if not codebases_dir.exists():
        print(f"ERROR: Codebases directory not found: {codebases_dir}")
        return 1

    codebases = sorted([d for d in codebases_dir.iterdir() if d.is_dir()])
    if not codebases:
        print("ERROR: No codebases found")
        return 1

    print(f"Running git storage UAT on {len(codebases)} codebases...")
    print(f"Codebases: {', '.join(c.name for c in codebases)}")

    results = []
    for i, codebase in enumerate(codebases, 1):
        print(f"\n[{i}/{len(codebases)}] Testing {codebase.name}...", end=" ", flush=True)
        result = test_codebase(codebase)
        results.append(result)
        print(f"{'✓' if result.passed else '✗'} ({result.commit_count} commits, {result.extraction_time:.2f}s)")

    print_results(results)

    return 0 if all(r.passed for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
