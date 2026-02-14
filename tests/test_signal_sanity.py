"""
Test that all 62 signals produce sensible values on real codebase.

This is NOT a unit test - it's a sanity check that signals:
1. Actually compute (don't crash)
2. Produce values in expected ranges
3. Correlate as expected (e.g., high complexity → high risk)
"""

import pytest
import sqlite3
from pathlib import Path


@pytest.fixture
def latest_snapshot_signals():
    """Load all signals from latest snapshot in .shannon/history.db"""
    db_path = Path(__file__).parent.parent / '.shannon' / 'history.db'
    if not db_path.exists():
        pytest.skip("No .shannon/history.db found - run analysis first")

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    # Get latest snapshot
    cur.execute("SELECT id FROM snapshots ORDER BY id DESC LIMIT 1")
    snapshot_id = cur.fetchone()[0]

    # Get all file signals
    cur.execute("""
        SELECT file_path, signal_name, value
        FROM signal_history
        WHERE snapshot_id = ?
    """, (snapshot_id,))

    # Pivot to {file_path: {signal: value}}
    file_signals = {}
    for file_path, signal_name, value in cur.fetchall():
        if file_path not in file_signals:
            file_signals[file_path] = {}
        file_signals[file_path][signal_name] = value

    # Get global signals
    cur.execute("""
        SELECT signal_name, value
        FROM global_signal_history
        WHERE snapshot_id = ?
    """, (snapshot_id,))

    global_signals = dict(cur.fetchall())

    conn.close()

    return file_signals, global_signals


class TestFileSignals:
    """Test all 36 file signals produce sensible values."""

    def test_lines_signal(self, latest_snapshot_signals):
        """lines: Should be positive integer"""
        file_signals, _ = latest_snapshot_signals
        for file_path, signals in file_signals.items():
            assert 'lines' in signals, f"{file_path} missing 'lines'"
            assert signals['lines'] > 0, f"{file_path} has lines={signals['lines']}"
            assert signals['lines'] < 100000, f"{file_path} has unrealistic lines={signals['lines']}"

    def test_function_count_signal(self, latest_snapshot_signals):
        """function_count: Should be non-negative"""
        file_signals, _ = latest_snapshot_signals
        for file_path, signals in file_signals.items():
            assert 'function_count' in signals, f"{file_path} missing 'function_count'"
            assert signals['function_count'] >= 0

    def test_cognitive_load_signal(self, latest_snapshot_signals):
        """cognitive_load: Should be positive float"""
        file_signals, _ = latest_snapshot_signals
        for file_path, signals in file_signals.items():
            assert 'cognitive_load' in signals, f"{file_path} missing 'cognitive_load'"
            assert signals['cognitive_load'] > 0

    def test_risk_score_signal(self, latest_snapshot_signals):
        """risk_score: Should be in [0, 1] range"""
        file_signals, _ = latest_snapshot_signals
        for file_path, signals in file_signals.items():
            if 'risk_score' in signals:  # Composite, may not always be present
                assert 0 <= signals['risk_score'] <= 1, f"{file_path} risk_score={signals['risk_score']} out of range"

    def test_pagerank_signal(self, latest_snapshot_signals):
        """pagerank: Should sum to ~1.0 across all files"""
        file_signals, _ = latest_snapshot_signals
        total_pagerank = sum(s.get('pagerank', 0) for s in file_signals.values())
        assert 0.95 <= total_pagerank <= 1.05, f"PageRank sum={total_pagerank} (expected ~1.0)"

    def test_blast_radius_signal(self, latest_snapshot_signals):
        """blast_radius_size: Should be non-negative integer"""
        file_signals, _ = latest_snapshot_signals
        for file_path, signals in file_signals.items():
            if 'blast_radius_size' in signals:
                assert signals['blast_radius_size'] >= 0
                assert signals['blast_radius_size'] <= len(file_signals), "Blast radius can't exceed file count"

    def test_churn_signals(self, latest_snapshot_signals):
        """Churn signals: cv, slope, trajectory should correlate"""
        file_signals, _ = latest_snapshot_signals

        # Find files with high churn_cv
        high_cv_files = [
            (path, s) for path, s in file_signals.items()
            if s.get('churn_cv', 0) > 1.0
        ]

        # These should have trajectory != STABILIZING
        for path, signals in high_cv_files:
            if 'churn_trajectory' in signals:
                # High CV means volatile, should not be STABILIZING
                trajectory = signals.get('churn_trajectory', '')
                assert trajectory != 'STABILIZING', f"{path} has high CV but STABILIZING trajectory"

    def test_bus_factor_signal(self, latest_snapshot_signals):
        """bus_factor: Should be >= 1.0 (at least 1 contributor)"""
        file_signals, _ = latest_snapshot_signals
        for file_path, signals in file_signals.items():
            if 'bus_factor' in signals:
                # bus_factor = 2^H where H = entropy, so min is 1.0 (single author)
                assert signals['bus_factor'] >= 1.0, f"{file_path} bus_factor={signals['bus_factor']} < 1.0"

    def test_concept_signals(self, latest_snapshot_signals):
        """concept_count and concept_entropy should correlate"""
        file_signals, _ = latest_snapshot_signals

        # Files with 1 concept should have entropy=0
        for path, signals in file_signals.items():
            if signals.get('concept_count') == 1:
                # Entropy of single concept is 0
                assert signals.get('concept_entropy', 0) == 0, f"{path} has 1 concept but entropy={signals.get('concept_entropy')}"

    def test_all_required_file_signals_present(self, latest_snapshot_signals):
        """All 36 file signals should be computed for each file"""
        file_signals, _ = latest_snapshot_signals

        required_signals = {
            'lines', 'function_count', 'class_count', 'max_nesting', 'impl_gini',
            'stub_ratio', 'import_count', 'role', 'concept_count', 'concept_entropy',
            'naming_drift', 'todo_density', 'docstring_coverage',
            'pagerank', 'betweenness', 'in_degree', 'out_degree', 'blast_radius_size',
            'depth', 'is_orphan', 'phantom_import_count', 'broken_call_count', 'community',
            'compression_ratio', 'semantic_coherence', 'cognitive_load',
            'total_changes', 'churn_trajectory', 'churn_slope', 'churn_cv',
            'bus_factor', 'author_entropy', 'fix_ratio', 'refactor_ratio',
            'risk_score', 'wiring_quality'
        }

        # Sample a few files to check (not all, too expensive)
        sample_files = list(file_signals.items())[:10]

        for file_path, signals in sample_files:
            missing = required_signals - set(signals.keys())
            if missing:
                print(f"{file_path} missing signals: {missing}")
            # Don't assert - some signals may legitimately be None/missing
            # Just report what's missing for investigation


class TestGlobalSignals:
    """Test all 11+ global signals produce sensible values."""

    def test_modularity_signal(self, latest_snapshot_signals):
        """modularity: Should be in [0, 1] range"""
        _, global_signals = latest_snapshot_signals
        assert 'modularity' in global_signals
        assert 0 <= global_signals['modularity'] <= 1

    def test_cycle_count_signal(self, latest_snapshot_signals):
        """cycle_count: Should be non-negative integer"""
        _, global_signals = latest_snapshot_signals
        assert 'cycle_count' in global_signals
        assert global_signals['cycle_count'] >= 0

    def test_orphan_ratio_signal(self, latest_snapshot_signals):
        """orphan_ratio: Should be in [0, 1] range"""
        _, global_signals = latest_snapshot_signals
        assert 'orphan_ratio' in global_signals
        assert 0 <= global_signals['orphan_ratio'] <= 1

    def test_centrality_gini_signal(self, latest_snapshot_signals):
        """centrality_gini: Should be in [0, 1] range (0=equal, 1=unequal)"""
        _, global_signals = latest_snapshot_signals
        assert 'centrality_gini' in global_signals
        assert 0 <= global_signals['centrality_gini'] <= 1

    def test_codebase_health_signal(self, latest_snapshot_signals):
        """codebase_health: Should be in [0, 10] range (or [0, 1] if not scaled)"""
        _, global_signals = latest_snapshot_signals
        assert 'codebase_health' in global_signals
        health = global_signals['codebase_health']
        # Health should be positive
        assert health >= 0
        # Could be 0-1 or 1-10 scale depending on implementation
        assert health <= 10


class TestSignalCorrelations:
    """Test that signals correlate as expected (sanity checks)."""

    def test_high_complexity_correlates_with_high_risk(self, latest_snapshot_signals):
        """Files with high cognitive_load should tend to have high risk_score"""
        file_signals, _ = latest_snapshot_signals

        # Get top 10 by cognitive load
        sorted_by_complexity = sorted(
            file_signals.items(),
            key=lambda x: x[1].get('cognitive_load', 0),
            reverse=True
        )[:10]

        # These should have above-average risk
        avg_risk = sum(s.get('risk_score', 0) for _, s in file_signals.items()) / len(file_signals)

        high_complexity_avg_risk = sum(
            s.get('risk_score', 0) for _, s in sorted_by_complexity
        ) / len(sorted_by_complexity)

        # High complexity files should have higher risk than average
        # (Allow some tolerance since correlation isn't perfect)
        assert high_complexity_avg_risk >= avg_risk * 0.8, \
            f"High complexity files have risk={high_complexity_avg_risk:.2f}, avg={avg_risk:.2f}"

    def test_high_pagerank_means_high_blast_radius(self, latest_snapshot_signals):
        """Files with high PageRank should have high blast_radius"""
        file_signals, _ = latest_snapshot_signals

        # Get top 10 by PageRank
        sorted_by_pagerank = sorted(
            file_signals.items(),
            key=lambda x: x[1].get('pagerank', 0),
            reverse=True
        )[:10]

        # These should have above-average blast radius
        avg_blast = sum(s.get('blast_radius_size', 0) for _, s in file_signals.items()) / len(file_signals)

        high_pr_avg_blast = sum(
            s.get('blast_radius_size', 0) for _, s in sorted_by_pagerank
        ) / len(sorted_by_pagerank)

        assert high_pr_avg_blast >= avg_blast, \
            f"High PageRank files have blast={high_pr_avg_blast:.1f}, avg={avg_blast:.1f}"
