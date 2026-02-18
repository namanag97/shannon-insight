#!/usr/bin/env python3
"""Performance benchmark and QA for raw git storage.

Compares:
1. Old GitExtractor (--name-only) vs New GitRawExtractor (--numstat)
2. In-memory processing vs Database-backed queries
3. Accuracy of churn/cochange results

Usage:
    python uat/bench_git_storage.py
"""

from __future__ import annotations

import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from shannon_insight.persistence.git_facts import GitFactDatabase
from shannon_insight.persistence.git_models import GitExtractionSession
from shannon_insight.temporal import (
    GitExtractor,
    GitRawExtractor,
    build_churn_series,
    build_churn_series_from_db,
    build_cochange_matrix,
    build_cochange_matrix_from_db,
)


def benchmark_extraction(repo_path: str, max_commits: int = 5000) -> dict:
    """Benchmark old vs new git extraction."""
    results = {}

    # Old extractor (--name-only)
    print("\n[1/4] Benchmarking old GitExtractor (--name-only)...")
    old_extractor = GitExtractor(repo_path, max_commits=max_commits)

    t0 = time.perf_counter()
    old_history = old_extractor.extract()
    t1 = time.perf_counter()

    results["old_extraction_time"] = t1 - t0
    results["old_commit_count"] = old_history.total_commits if old_history else 0
    results["old_file_set_size"] = len(old_history.file_set) if old_history else 0

    # New extractor (--numstat)
    print("[2/4] Benchmarking new GitRawExtractor (--numstat)...")
    new_extractor = GitRawExtractor(repo_path, max_commits=max_commits)

    t0 = time.perf_counter()
    new_data = new_extractor.extract()
    t1 = time.perf_counter()

    results["new_extraction_time"] = t1 - t0
    results["new_commit_count"] = new_data.commit_count if new_data else 0
    results["new_file_change_count"] = new_data.file_change_count if new_data else 0

    # Calculate extracted data size
    if new_data:
        total_additions = sum(
            fc.additions or 0 for fc in new_data.file_changes if fc.additions is not None
        )
        total_deletions = sum(
            fc.deletions or 0 for fc in new_data.file_changes if fc.deletions is not None
        )
        results["total_additions"] = total_additions
        results["total_deletions"] = total_deletions

    return results, old_history, new_data


def benchmark_database_storage(new_data, db_path: str) -> dict:
    """Benchmark database storage and retrieval."""
    results = {}

    db = GitFactDatabase(db_path)

    # Create session
    session = GitExtractionSession(
        id=str(uuid4()),
        repo_path="/tmp/test",
        started_at=datetime.now(timezone.utc),
        completed_at=None,
        head_sha=new_data.head_sha,
        oldest_sha=new_data.oldest_sha,
        commit_count=0,
        file_change_count=0,
        status="running",
    )
    db.create_session(session)

    # Benchmark batch insert
    print("[3/4] Benchmarking database batch insert...")
    t0 = time.perf_counter()
    db.store_commits_batch(new_data.commits, session.id)
    db.store_file_changes_batch(new_data.file_changes)
    t1 = time.perf_counter()

    results["db_insert_time"] = t1 - t0

    db.complete_session(
        session.id, new_data.commit_count, new_data.file_change_count
    )

    # Benchmark queries
    print("[4/4] Benchmarking database queries...")

    # File churn query
    if new_data.file_changes:
        sample_file = new_data.file_changes[0].file_path
        t0 = time.perf_counter()
        for _ in range(100):
            db.get_file_churn(sample_file)
        t1 = time.perf_counter()
        results["file_churn_query_avg_ms"] = (t1 - t0) * 10  # 100 queries -> ms

    # Co-change pairs query
    t0 = time.perf_counter()
    pairs = db.get_cochange_pairs(min_cochanges=2)
    t1 = time.perf_counter()
    results["cochange_query_time"] = t1 - t0
    results["cochange_pairs_found"] = len(pairs)

    # Get stats
    stats = db.get_stats()
    results.update(stats)

    return results, db


def benchmark_churn_cochange(old_history, db, analyzed_files: set[str]) -> dict:
    """Benchmark churn/cochange computation methods."""
    results = {}

    if not old_history:
        return results

    # Old method: in-memory churn
    print("\n[Churn] Benchmarking in-memory vs DB-backed churn...")
    t0 = time.perf_counter()
    old_churn = build_churn_series(old_history, analyzed_files)
    t1 = time.perf_counter()
    results["churn_memory_time"] = t1 - t0
    results["churn_memory_files"] = len(old_churn)

    # New method: DB-backed churn
    t0 = time.perf_counter()
    new_churn = build_churn_series_from_db(db, analyzed_files)
    t1 = time.perf_counter()
    results["churn_db_time"] = t1 - t0
    results["churn_db_files"] = len(new_churn)

    # Compare accuracy
    common_files = set(old_churn.keys()) & set(new_churn.keys())
    if common_files:
        matches = 0
        mismatches = []
        for f in common_files:
            # Compare total changes (should be identical)
            if old_churn[f].total_changes == new_churn[f].total_changes:
                matches += 1
            else:
                mismatches.append((f, old_churn[f].total_changes, new_churn[f].total_changes))
        results["churn_accuracy"] = matches / len(common_files)
        if mismatches:
            results["churn_mismatches"] = mismatches[:5]  # First 5

    # Old method: in-memory cochange
    print("[CoChange] Benchmarking in-memory vs DB-backed cochange...")
    t0 = time.perf_counter()
    old_cochange = build_cochange_matrix(old_history, analyzed_files, min_cochanges=2)
    t1 = time.perf_counter()
    results["cochange_memory_time"] = t1 - t0
    results["cochange_memory_pairs"] = len(old_cochange.pairs)

    # New method: DB-backed cochange
    t0 = time.perf_counter()
    new_cochange = build_cochange_matrix_from_db(db, analyzed_files, min_cochanges=2)
    t1 = time.perf_counter()
    results["cochange_db_time"] = t1 - t0
    results["cochange_db_pairs"] = len(new_cochange.pairs)

    return results


def print_results(extraction_results: dict, db_results: dict, churn_results: dict) -> None:
    """Pretty print benchmark results."""
    print("\n" + "=" * 60)
    print("BENCHMARK RESULTS")
    print("=" * 60)

    print("\n## Git Extraction")
    print(f"  Old (--name-only): {extraction_results['old_extraction_time']:.3f}s")
    print(f"    Commits: {extraction_results['old_commit_count']}")
    print(f"    Unique files: {extraction_results['old_file_set_size']}")

    print(f"  New (--numstat):   {extraction_results['new_extraction_time']:.3f}s")
    print(f"    Commits: {extraction_results['new_commit_count']}")
    print(f"    File changes: {extraction_results['new_file_change_count']}")
    if "total_additions" in extraction_results:
        print(f"    Total additions: {extraction_results['total_additions']:,}")
        print(f"    Total deletions: {extraction_results['total_deletions']:,}")

    speedup = extraction_results['old_extraction_time'] / extraction_results['new_extraction_time']
    print(f"  Speedup: {speedup:.2f}x")

    print("\n## Database Storage")
    print(f"  Batch insert time: {db_results['db_insert_time']:.3f}s")
    if "file_churn_query_avg_ms" in db_results:
        print(f"  File churn query (avg): {db_results['file_churn_query_avg_ms']:.3f}ms")
    print(f"  Co-change query: {db_results['cochange_query_time']:.3f}s")
    print(f"  Co-change pairs found: {db_results['cochange_pairs_found']}")

    print("\n## Churn Computation")
    print(f"  In-memory: {churn_results.get('churn_memory_time', 0):.3f}s ({churn_results.get('churn_memory_files', 0)} files)")
    print(f"  DB-backed: {churn_results.get('churn_db_time', 0):.3f}s ({churn_results.get('churn_db_files', 0)} files)")
    if "churn_accuracy" in churn_results:
        print(f"  Accuracy: {churn_results['churn_accuracy']*100:.1f}%")

    print("\n## Co-Change Computation")
    print(f"  In-memory: {churn_results.get('cochange_memory_time', 0):.3f}s ({churn_results.get('cochange_memory_pairs', 0)} pairs)")
    print(f"  DB-backed: {churn_results.get('cochange_db_time', 0):.3f}s ({churn_results.get('cochange_db_pairs', 0)} pairs)")

    print("\n" + "=" * 60)


def main():
    """Run benchmarks on the shannon-insight codebase."""
    repo_path = Path(__file__).parent.parent
    print(f"Running benchmarks on: {repo_path}")

    # Run extraction benchmarks
    extraction_results, old_history, new_data = benchmark_extraction(str(repo_path))

    if new_data is None:
        print("ERROR: Failed to extract git data")
        return 1

    # Run database benchmarks
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "bench.db"
        db_results, db = benchmark_database_storage(new_data, str(db_path))

        # Get analyzed files from old history
        analyzed_files = old_history.file_set if old_history else set()

        # Run churn/cochange benchmarks
        churn_results = benchmark_churn_cochange(old_history, db, analyzed_files)

        # Print results
        print_results(extraction_results, db_results, churn_results)

    return 0


if __name__ == "__main__":
    sys.exit(main())
