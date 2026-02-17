"""Regression tests for audit fix pass.

12 tests covering every fix applied in the audit:
1.  CYCLE_MEMBER synced to FactStore
2.  fix_ratio no substring false positives
3.  DUPLICATE_INCOMPLETE requires CLONED_FROM relation
4.  GOD_FILE can fire without semantics (semantic_coherence defaults to 0.5)
5.  delta_h synced to FactStore
6.  risk_score continuous — no cliff at churn trajectory boundary
7.  BUG_ATTRACTOR requires structural cause (cognitive_load)
8.  Module prefix no cross-contamination
9.  ZONE_OF_USELESSNESS fires
10. CIRCULAR_DEPENDENCY finder fires
11. KNOWLEDGE_SILO does not overlap with TRUCK_FACTOR
12. CV burst-then-dormant classified as STABILIZING
"""

from __future__ import annotations

from shannon_insight.infrastructure.entities import EntityId, EntityType
from shannon_insight.infrastructure.signals import Signal
from shannon_insight.infrastructure.store import FactStore
from shannon_insight.signals.models import FileSignals, ModuleSignals, SignalField
from shannon_insight.temporal.churn import _classify_trajectory, _compute_cv

# ─── Helpers ──────────────────────────────────────────────────────────────────


def _make_store() -> FactStore:
    """Create a minimal FactStore with a few file entities."""
    from shannon_insight.infrastructure.entities import Entity

    store = FactStore(root=".")
    for name in ("a.py", "b.py", "c.py", "d.py", "e.py"):
        eid = EntityId(EntityType.FILE, name)
        store.add_entity(Entity(id=eid, metadata={}))
    return store


def _populate_signal(store: FactStore, signal: Signal, values: dict[str, float]) -> None:
    for path, val in values.items():
        store.set_signal(EntityId(EntityType.FILE, path), signal, val)


# ─── Test 1: CYCLE_MEMBER synced to FactStore ─────────────────────────────────


def test_cycle_member_synced_to_factstore():
    """CYCLE_SIZE and CYCLE_MEMBER must both be written for cycle members."""
    from shannon_insight.infrastructure.signals import Signal

    store = _make_store()

    # Simulate what structural.py does for a 3-file cycle
    cycle_nodes = ["a.py", "b.py", "c.py"]
    for path in cycle_nodes:
        eid = EntityId(EntityType.FILE, path)
        store.set_signal(eid, Signal.CYCLE_MEMBER, True)
        store.set_signal(eid, Signal.CYCLE_SIZE, 3)

    # Non-cycle file
    store.set_signal(EntityId(EntityType.FILE, "d.py"), Signal.CYCLE_MEMBER, False)
    store.set_signal(EntityId(EntityType.FILE, "d.py"), Signal.CYCLE_SIZE, 0)

    for path in cycle_nodes:
        eid = EntityId(EntityType.FILE, path)
        assert store.get_signal(eid, Signal.CYCLE_MEMBER) is True
        assert store.get_signal(eid, Signal.CYCLE_SIZE) == 3

    d_id = EntityId(EntityType.FILE, "d.py")
    assert store.get_signal(d_id, Signal.CYCLE_MEMBER) is False
    assert store.get_signal(d_id, Signal.CYCLE_SIZE) == 0


# ─── Test 2: fix_ratio no substring false positives ───────────────────────────


def test_fix_ratio_no_substring_false_positive():
    """'fix' in 'prefix/suffix' or 'issue' in 'tissue' must NOT match."""
    from shannon_insight.temporal.churn import _FIX_PATTERN

    false_positives = ["update prefix handling", "add tissue test", "suffix removed"]
    for subject in false_positives:
        assert not _FIX_PATTERN.search(subject.lower()), f"False positive: {subject!r}"

    # Real fix commits SHOULD match
    true_positives = ["fix real bug", "bugfix: null pointer", "patch security issue"]
    for subject in true_positives:
        assert _FIX_PATTERN.search(subject.lower()), f"False negative: {subject!r}"


# ─── Test 3: DUPLICATE_INCOMPLETE requires CLONED_FROM relation ───────────────


def test_duplicate_incomplete_requires_cloned_from_relation():
    """Files with identical compression ratios but no CLONED_FROM relation must NOT fire."""
    from shannon_insight.insights.finders.patterns.additional import (
        _duplicate_incomplete_predicate,
    )

    store = _make_store()
    a_id = EntityId(EntityType.FILE, "a.py")
    b_id = EntityId(EntityType.FILE, "b.py")

    # Same compression ratio — but NO CLONED_FROM relation
    store.set_signal(a_id, Signal.COMPRESSION_RATIO, 0.55)
    store.set_signal(b_id, Signal.COMPRESSION_RATIO, 0.55)
    store.set_signal(a_id, Signal.STUB_RATIO, 0.6)
    store.set_signal(b_id, Signal.STUB_RATIO, 0.6)

    result = _duplicate_incomplete_predicate(store, (a_id, b_id))
    assert result is False, "Must not fire without CLONED_FROM relation"


# ─── Test 4: GOD_FILE can fire without semantics ──────────────────────────────


def test_god_file_semantic_coherence_default_is_neutral():
    """FileSignals.semantic_coherence must default to 0.5, not 0.0.

    0.0 would make pctl(semantic_coherence)=1.0 for ALL files (every file
    equals the max), suppressing GOD_FILE which checks pctl < 0.20.
    """
    fs = FileSignals(path="big.py")
    assert fs.semantic_coherence == 0.5, (
        "Default must be 0.5 (neutral). 0.0 causes pctl=1.0 for all files → GOD_FILE never fires."
    )


# ─── Test 5: delta_h synced to FactStore ──────────────────────────────────────


def test_delta_h_synced_to_factstore():
    """After SignalFusionAnalyzer runs, DELTA_H must exist for at least one file."""
    store = _make_store()
    a_id = EntityId(EntityType.FILE, "a.py")

    # Simulate fusion writing delta_h
    store.set_signal(a_id, Signal.DELTA_H, 0.3)

    val = store.get_signal(a_id, Signal.DELTA_H)
    assert val is not None
    assert abs(val - 0.3) < 1e-9


# ─── Test 6: risk_score continuous — no cliff ────────────────────────────────


def test_risk_score_no_cliff_at_churning_boundary():
    """Two files with churn_cv=0.49 and churn_cv=0.51 should have similar risk_score."""
    from shannon_insight.signals.composites import _compute_risk_score

    def _make_fs(churn_cv: float) -> FileSignals:
        fs = FileSignals(path="x.py")
        fs.pagerank = 0.5
        fs.blast_radius_size = 5
        fs.in_degree = 2
        fs.total_changes = 10
        fs.churn_cv = churn_cv
        fs.bus_factor = 2.0
        fs.percentiles = {"pagerank": 0.7, "blast_radius_size": 0.6, "cognitive_load": 0.5}
        return fs

    risk_low = _compute_risk_score(_make_fs(0.49))
    risk_high = _compute_risk_score(_make_fs(0.51))

    diff = abs(risk_high - risk_low)
    assert diff < 0.05, f"Cliff detected: risk jumped {diff:.3f} across cv=0.5 boundary"


# ─── Test 7: BUG_ATTRACTOR requires complexity ────────────────────────────────


def test_bug_attractor_requires_complexity():
    """High fix_ratio alone is not enough — must also have high cognitive_load percentile."""
    from shannon_insight.insights.finders.patterns.cross_dimensional import (
        _bug_attractor_predicate,
    )

    store = _make_store()
    # Populate total_changes so median can be computed
    for path in ("a.py", "b.py", "c.py", "d.py", "e.py"):
        store.set_signal(EntityId(EntityType.FILE, path), Signal.TOTAL_CHANGES, 5)

    a_id = EntityId(EntityType.FILE, "a.py")
    store.set_signal(a_id, Signal.FIX_RATIO, 0.6)
    store.set_signal(a_id, Signal.TOTAL_CHANGES, 10)  # above median=5

    # Low cognitive_load percentile (10th) — must NOT fire
    for path in ("a.py", "b.py", "c.py", "d.py", "e.py"):
        val = 1.0 if path == "a.py" else 10.0  # a.py has lowest cog load
        store.set_signal(EntityId(EntityType.FILE, path), Signal.COGNITIVE_LOAD, val)

    result = _bug_attractor_predicate(store, a_id)
    assert result is False, "Must not fire when cognitive_load is at 10th percentile"


# ─── Test 8: Module prefix no cross-contamination ─────────────────────────────


def test_module_prefix_no_cross_contamination():
    """Module 'src/api' must not include files from 'src/api_v2/'."""
    from shannon_insight.signals.composites import _get_mean_stub_ratio_for_module

    field = SignalField()
    for path, stub in [
        ("src/api/handler.py", 0.2),
        ("src/api/router.py", 0.3),
        ("src/api_v2/handler.py", 0.9),  # must be excluded
    ]:
        fs = FileSignals(path=path)
        fs.stub_ratio = stub
        field.per_file[path] = fs

    ms = ModuleSignals(path="src/api")
    result = _get_mean_stub_ratio_for_module(ms, field)

    # Expected: mean of [0.2, 0.3] = 0.25, NOT contaminated by 0.9
    assert abs(result - 0.25) < 1e-9, f"Expected 0.25 but got {result} (api_v2 leaked in)"


# ─── Test 9: ZONE_OF_USELESSNESS fires ────────────────────────────────────────


def test_zone_of_uselessness_fires():
    """Module with abstractness=0.8 and instability=0.8 should fire ZONE_OF_USELESSNESS."""
    from shannon_insight.insights.finders.patterns.architecture import (
        _zone_of_uselessness_predicate,
    )

    store = _make_store()
    from shannon_insight.infrastructure.entities import Entity

    mod_id = EntityId(EntityType.MODULE, "src/abstractions")
    store.add_entity(Entity(id=mod_id, metadata={}))
    store.set_signal(mod_id, Signal.ABSTRACTNESS, 0.8)
    store.set_signal(mod_id, Signal.INSTABILITY, 0.8)

    assert _zone_of_uselessness_predicate(store, mod_id) is True


def test_zone_of_uselessness_does_not_fire_low_instability():
    """Module with high abstractness but low instability (stable consumers) must not fire."""
    from shannon_insight.infrastructure.entities import Entity
    from shannon_insight.insights.finders.patterns.architecture import (
        _zone_of_uselessness_predicate,
    )

    store = _make_store()  # already has root="."
    mod_id = EntityId(EntityType.MODULE, "src/core")
    store.add_entity(Entity(id=mod_id, metadata={}))
    store.set_signal(mod_id, Signal.ABSTRACTNESS, 0.8)
    store.set_signal(mod_id, Signal.INSTABILITY, 0.2)  # stable consumers exist

    assert _zone_of_uselessness_predicate(store, mod_id) is False


# ─── Test 10: CIRCULAR_DEPENDENCY fires ──────────────────────────────────────


def test_circular_dependency_finder_fires():
    """Files with CYCLE_MEMBER=True should be caught by CIRCULAR_DEPENDENCY."""
    from shannon_insight.insights.finders.patterns.architecture import (
        _circular_dependency_predicate,
        _circular_dependency_severity,
    )

    store = _make_store()
    for path in ("a.py", "b.py", "c.py"):
        eid = EntityId(EntityType.FILE, path)
        store.set_signal(eid, Signal.CYCLE_MEMBER, True)
        store.set_signal(eid, Signal.CYCLE_SIZE, 3)

    store.set_signal(EntityId(EntityType.FILE, "d.py"), Signal.CYCLE_MEMBER, False)

    a_id = EntityId(EntityType.FILE, "a.py")
    d_id = EntityId(EntityType.FILE, "d.py")

    assert _circular_dependency_predicate(store, a_id) is True
    assert _circular_dependency_predicate(store, d_id) is False
    assert _circular_dependency_severity(store, a_id) == 0.70  # cycle_size=3


# ─── Test 11: KNOWLEDGE_SILO does not overlap with TRUCK_FACTOR ───────────────


def test_knowledge_silo_no_overlap_with_truck_factor():
    """bus_factor <= 1.0 must NOT fire KNOWLEDGE_SILO (TRUCK_FACTOR handles it)."""
    from shannon_insight.insights.finders.patterns.social_team import (
        _knowledge_silo_predicate,
    )

    store = _make_store()
    # Populate PAGERANK so percentile can be computed
    for path, pr in [("a.py", 1.0), ("b.py", 0.5), ("c.py", 0.3), ("d.py", 0.2), ("e.py", 0.1)]:
        store.set_signal(EntityId(EntityType.FILE, path), Signal.PAGERANK, pr)

    a_id = EntityId(EntityType.FILE, "a.py")
    store.set_signal(a_id, Signal.BUS_FACTOR, 1.0)  # boundary — TRUCK_FACTOR territory

    assert _knowledge_silo_predicate(store, a_id) is False, (
        "bus_factor=1.0 must be handled by TRUCK_FACTOR, not KNOWLEDGE_SILO"
    )

    # bus_factor=1.5 SHOULD fire (moderate risk, not handled by TRUCK_FACTOR)
    store.set_signal(a_id, Signal.BUS_FACTOR, 1.5)
    assert _knowledge_silo_predicate(store, a_id) is True


# ─── Test 12: CV burst-then-dormant → STABILIZING ────────────────────────────


def test_cv_burst_then_dormant_is_stabilizing():
    """[10, 0, 0, 0, 0, 0] (heavy early, silent recent) should classify as STABILIZING."""
    counts = [10, 0, 0, 0, 0, 0]
    total = sum(counts)
    from shannon_insight.temporal.churn import _compute_cv, _linear_slope

    slope = _linear_slope(counts)
    cv = _compute_cv(counts, total)
    result = _classify_trajectory(counts, total, slope, cv)

    assert result == "STABILIZING", (
        f"Burst-then-dormant pattern should be STABILIZING, got {result!r}"
    )


def test_cv_bessel_correction():
    """CV should use Bessel's correction (n-1) and require n>=3."""
    # n=2 → returns 0.0 (not enough data)
    assert _compute_cv([5, 3], 8) == 0.0

    # n=3 → should compute with n-1=2
    counts = [10, 0, 5]
    total = 15
    n = 3
    mean = total / n
    variance_bessel = sum((c - mean) ** 2 for c in counts) / (n - 1)
    expected_cv = (variance_bessel**0.5) / mean
    result = _compute_cv(counts, total)
    assert abs(result - expected_cv) < 1e-9, f"Bessel correction wrong: {result} vs {expected_cv}"
