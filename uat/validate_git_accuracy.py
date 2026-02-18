#!/usr/bin/env python3
"""Validate git extraction accuracy against actual git commands.

Compares extracted data against direct git queries to ensure accuracy.

Usage:
    python uat/validate_git_accuracy.py
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from shannon_insight.persistence.git_facts import GitFactDatabase
from shannon_insight.persistence.git_models import GitExtractionSession
from shannon_insight.temporal.git_raw_extractor import GitRawExtractor


def run_git(repo_path: str, args: list[str]) -> str:
    """Run git command and return output."""
    result = subprocess.run(
        ["git", "-C", repo_path] + args,
        capture_output=True,
        text=True,
    )
    return result.stdout


def validate_commit_count(repo_path: str, extracted_count: int) -> tuple[bool, str]:
    """Validate commit count matches git rev-list."""
    output = run_git(repo_path, ["rev-list", "--count", "HEAD"])
    actual_count = int(output.strip())

    # We limit to max_commits (10000), so extracted should be <= actual
    if extracted_count <= actual_count:
        return True, f"Extracted {extracted_count} <= actual {actual_count}"
    return False, f"Extracted {extracted_count} > actual {actual_count}"


def validate_file_churn(repo_path: str, db: GitFactDatabase, file_path: str) -> tuple[bool, str]:
    """Validate file churn against git log --numstat."""
    # Get from database
    db_churn = db.get_file_churn(file_path)

    # Get from git directly
    output = run_git(repo_path, [
        "log", "--numstat", "--format=", "--follow", "--", file_path
    ])

    # Parse git output
    additions = 0
    deletions = 0
    changes = 0
    for line in output.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) >= 3:
            changes += 1
            try:
                if parts[0] != "-":
                    additions += int(parts[0])
                if parts[1] != "-":
                    deletions += int(parts[1])
            except ValueError:
                pass

    # Compare
    if db_churn["change_count"] == changes and db_churn["additions"] == additions and db_churn["deletions"] == deletions:
        return True, f"Match: {changes} changes, +{additions}/-{deletions}"

    return False, (
        f"Mismatch: DB({db_churn['change_count']} changes, +{db_churn['additions']}/-{db_churn['deletions']}) "
        f"vs Git({changes} changes, +{additions}/-{deletions})"
    )


def validate_authors(repo_path: str, db: GitFactDatabase, file_path: str) -> tuple[bool, str]:
    """Validate file authors against git shortlog."""
    # Get from database
    db_authors = db.get_file_authors(file_path)
    db_emails = {a[0] for a in db_authors}

    # Get from git directly
    output = run_git(repo_path, [
        "log", "--format=%ae", "--follow", "--", file_path
    ])
    git_emails = set(output.strip().split("\n")) - {""}

    if db_emails == git_emails:
        return True, f"Match: {len(db_emails)} unique authors"

    missing = git_emails - db_emails
    extra = db_emails - git_emails
    return False, f"Mismatch: missing={missing}, extra={extra}"


def validate_rename_detection(repo_path: str, db: GitFactDatabase) -> tuple[bool, str]:
    """Validate rename detection."""
    # Get renames from DB
    db_renames = db.get_renames()

    # Get renames from git
    output = run_git(repo_path, [
        "log", "--diff-filter=R", "--name-status", "-M", "--format="
    ])

    git_renames = []
    for line in output.strip().split("\n"):
        if not line.strip() or not line.startswith("R"):
            continue
        parts = line.split("\t")
        if len(parts) >= 3:
            git_renames.append((parts[1], parts[2]))

    if len(db_renames) == len(git_renames):
        return True, f"Match: {len(db_renames)} renames detected"

    return False, f"Mismatch: DB={len(db_renames)}, Git={len(git_renames)}"


def main():
    """Run validation tests."""
    repo_path = str(Path(__file__).parent.parent)
    print(f"Validating git extraction accuracy for: {repo_path}")
    print("=" * 60)

    # Extract data
    print("\n[1/5] Extracting git data...")
    extractor = GitRawExtractor(repo_path, max_commits=10000)
    data = extractor.extract()

    if data is None:
        print("ERROR: Failed to extract git data")
        return 1

    # Store in temp DB
    with tempfile.TemporaryDirectory() as tmpdir:
        db = GitFactDatabase(Path(tmpdir) / "test.db")
        session = GitExtractionSession(
            id=str(uuid4()),
            repo_path=repo_path,
            started_at=datetime.now(timezone.utc),
            completed_at=None,
            head_sha=data.head_sha,
            oldest_sha=data.oldest_sha,
            commit_count=0,
            file_change_count=0,
            status="running",
        )
        db.create_session(session)
        db.store_commits_batch(data.commits, session.id)
        db.store_file_changes_batch(data.file_changes)

        results = []

        # Validate commit count
        print("\n[2/5] Validating commit count...")
        ok, msg = validate_commit_count(repo_path, data.commit_count)
        results.append(("Commit count", ok, msg))
        print(f"  {'✓' if ok else '✗'} {msg}")

        # Validate file churn for specific files
        print("\n[3/5] Validating file churn...")
        test_files = [
            "src/shannon_insight/insights/kernel.py",
            "src/shannon_insight/graph/builder.py",
            "src/shannon_insight/temporal/churn.py",
        ]
        for f in test_files:
            ok, msg = validate_file_churn(repo_path, db, f)
            results.append((f"Churn: {f}", ok, msg))
            print(f"  {'✓' if ok else '✗'} {f}: {msg}")

        # Validate authors
        print("\n[4/5] Validating authors...")
        for f in test_files[:1]:  # Just one file
            ok, msg = validate_authors(repo_path, db, f)
            results.append((f"Authors: {f}", ok, msg))
            print(f"  {'✓' if ok else '✗'} {f}: {msg}")

        # Validate rename detection
        print("\n[5/5] Validating rename detection...")
        ok, msg = validate_rename_detection(repo_path, db)
        results.append(("Rename detection", ok, msg))
        print(f"  {'✓' if ok else '✗'} {msg}")

        # Summary
        print("\n" + "=" * 60)
        passed = sum(1 for _, ok, _ in results if ok)
        total = len(results)
        print(f"SUMMARY: {passed}/{total} validations passed")

        if passed < total:
            print("\nFailed validations:")
            for name, ok, msg in results:
                if not ok:
                    print(f"  - {name}: {msg}")
            return 1

        print("\n✓ All validations passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
