# Phase 6 Implementation Guide for Opus

> **Purpose**: Implement 15 new finders that read from the unified `SignalField` to detect code health issues.
> **Estimated effort**: 6-8 hours (Opus-optimized)
> **Prerequisites**: Phases 0-5 complete ✅ (all integration gaps fixed)

---

## 🎯 What You're Building

**15 new Finder classes** organized in 3 batches:

| Batch | Count | Focus | Complexity |
|-------|-------|-------|------------|
| **Batch 1: Structural** | 5 finders | File-level structural issues | Low |
| **Batch 2: Architecture** | 5 finders | Module/layer violations | Medium |
| **Batch 3: Cross-Dimensional** | 5 finders | Temporal + structural fusion | High |

All finders:
- ✅ Read from `store.signal_field` (unified data source)
- ✅ Use percentile-based thresholds (tier-aware)
- ✅ Filter hotspots: `total_changes > median` for FILE scope
- ✅ Return `List[Finding]` with evidence and suggestions

---

## 📋 Pre-Implementation Checklist

### ✅ **Verify Phase 5 is Complete**

Run this command to confirm all Phase 5 data is available:

```bash
python3 -c "
from shannon_insight.signals.models import GlobalSignals, FileSignals
import inspect

# Check GlobalSignals has all 4 fixed fields
gs = GlobalSignals()
assert hasattr(gs, 'clone_ratio'), 'Missing clone_ratio'
assert hasattr(gs, 'violation_rate'), 'Missing violation_rate'
assert hasattr(gs, 'conway_alignment'), 'Missing conway_alignment'
assert hasattr(gs, 'team_size'), 'Missing team_size'

# Check FileSignals has percentiles dict
fs = FileSignals(path='test.py')
assert hasattr(fs, 'percentiles'), 'Missing percentiles'
assert hasattr(fs, 'raw_risk'), 'Missing raw_risk'

print('✅ Phase 5 complete - ready for Phase 6')
"
```

### ✅ **Read These Specs First**

**MUST READ** (in this order):
1. `docs/v2/phases/phase-6-finders.md` — Phase spec (what to build)
2. `docs/v2/registry/finders.md` — All 22 finder specs (formulas, thresholds)
3. `docs/v2/FINDER-REHEARSAL.md` — End-to-end data flow for each finder
4. `docs/v2/FAILURE-MODES.md` — 22 common bugs to avoid

**Reference** (keep open while coding):
5. `docs/v2/SPEC-REFERENCE.md` — Quick lookup for signal definitions
6. `docs/v2/modules/signals/composites.md` — Composite formula details

---

## 🏗️ Implementation Architecture

### **File Structure**

All finders go in `src/shannon_insight/insights/finders/`:

```
insights/finders/
├── __init__.py                    # Update get_default_finders()
│
├── orphan_code.py                 # Batch 1: Structural (5 finders)
├── phantom_dependency.py
├── hollow_code.py
├── copy_paste_clone.py
├── flat_architecture.py
│
├── zone_of_pain.py                # Batch 2: Architecture (5 finders)
├── accidental_coupling.py
├── conway_violation.py
├── layer_violation.py
├── interface_bloat.py
│
├── weak_link.py                   # Batch 3: Cross-dimensional (5 finders)
├── knowledge_island.py
├── temporal_coupling.py
├── toxic_file.py
└── architecture_erosion.py
```

### **Finder Template**

Every finder follows this structure:

```python
"""FINDER_NAME — Description from registry/finders.md.

Scope: FILE | MODULE | CODEBASE
Severity: 0.3-1.0 (registry defines range)
"""

from typing import List

from ..models import Finding
from ..protocols_v2 import Finder
from ..store_v2 import AnalysisStore


class FinderNameFinder:
    """Implements Finder protocol for FINDER_NAME detection."""

    name = "finder_name"
    requires = frozenset({"signal_field"})  # All finders read from signal_field

    def find(self, store: AnalysisStore) -> List[Finding]:
        """Detect FINDER_NAME issues.

        Returns:
            List of Finding instances, sorted by severity desc.
        """
        if not store.signal_field.available:
            return []

        field = store.signal_field.value
        findings: List[Finding] = []

        # Tier-aware threshold from registry
        tier = field.tier
        threshold = self._get_threshold(tier)

        # Hotspot filter for FILE-scoped finders (if applicable)
        if self._applies_hotspot_filter():
            median_changes = self._compute_median_changes(field)

        # Detection logic
        for path, fs in field.per_file.items():
            # Apply hotspot filter if needed
            if self._applies_hotspot_filter():
                if fs.total_changes <= median_changes:
                    continue  # Skip cold files

            # Detection condition from registry
            if self._meets_condition(fs, threshold):
                findings.append(
                    Finding(
                        finding_type=self.name,
                        severity=self._compute_severity(fs),
                        title=self._make_title(fs),
                        files=[path],
                        evidence=self._build_evidence(fs),
                        suggestion=self._make_suggestion(fs),
                    )
                )

        return sorted(findings, key=lambda f: f.severity, reverse=True)

    def _get_threshold(self, tier: str) -> float:
        """Return tier-aware threshold from registry."""
        thresholds = {
            "ABSOLUTE": 0.0,  # No thresholds for <15 files
            "BAYESIAN": 0.5,  # Conservative for 15-50 files
            "FULL": 0.7,      # Standard for 50+ files
        }
        return thresholds.get(tier, 0.7)

    def _applies_hotspot_filter(self) -> bool:
        """Whether this finder requires hotspot filtering."""
        # Return False if finder is structural-only (orphan, phantom, clone, flat_arch)
        # Return True for all other FILE-scoped finders
        return True  # Most finders need this

    def _compute_median_changes(self, field) -> int:
        """Compute median total_changes for hotspot filter."""
        changes = [fs.total_changes for fs in field.per_file.values()]
        if not changes:
            return 0
        changes_sorted = sorted(changes)
        n = len(changes_sorted)
        return changes_sorted[n // 2] if n % 2 == 1 else changes_sorted[n // 2 - 1]

    def _meets_condition(self, fs, threshold: float) -> bool:
        """Check if file/module meets finder condition."""
        # Implement condition from registry/finders.md
        raise NotImplementedError

    def _compute_severity(self, fs) -> float:
        """Compute severity in [0, 1] based on signal strength."""
        # Higher signal values → higher severity
        # Clamp to finder's severity range from registry
        raise NotImplementedError

    def _make_title(self, fs) -> str:
        """Generate human-readable title."""
        # e.g., "Orphan file with no imports: {basename}"
        raise NotImplementedError

    def _build_evidence(self, fs) -> List[str]:
        """Build evidence list from signals."""
        # e.g., ["PageRank: 0.85 (top 5%)", "Blast radius: 42 files"]
        raise NotImplementedError

    def _make_suggestion(self, fs) -> str:
        """Generate actionable suggestion."""
        # From registry/finders.md "Suggestion" field
        raise NotImplementedError
```

---

## 📊 Data Flow: How Finders Read Signals

### **The Signal Hierarchy**

```
store.signal_field: SignalField
├── tier: str                           # "ABSOLUTE" | "BAYESIAN" | "FULL"
├── per_file: Dict[str, FileSignals]    # 36 per-file signals
│   └── path: str
│       ├── pagerank: float
│       ├── percentiles: Dict[str, float]  ← USE THIS for thresholds
│       ├── risk_score: float              ← Composite (percentile-based)
│       ├── raw_risk: float                ← Used by WEAK_LINK finder
│       └── ...
├── per_module: Dict[str, ModuleSignals] # 15 per-module signals
│   └── path: str
│       ├── instability: Optional[float]
│       ├── health_score: float
│       └── ...
└── global_signals: GlobalSignals        # 11 global signals
    ├── clone_ratio: float               ← Fixed in Phase 5 ✅
    ├── violation_rate: float            ← Fixed in Phase 5 ✅
    ├── conway_alignment: float          ← Fixed in Phase 5 ✅
    ├── team_size: int                   ← Fixed in Phase 5 ✅
    └── ...
```

### **Reading Signals: Examples**

```python
# Example 1: ORPHAN_CODE (structural, no percentile)
def _meets_condition(self, fs, threshold: float) -> bool:
    return fs.is_orphan  # Boolean signal, no threshold needed

# Example 2: TOXIC_FILE (uses percentiles)
def _meets_condition(self, fs, threshold: float) -> bool:
    pctl_pr = fs.percentiles.get("pagerank", 0.0)
    pctl_churn = fs.percentiles.get("total_changes", 0.0)
    return pctl_pr > threshold and pctl_churn > threshold

# Example 3: WEAK_LINK (uses raw_risk, not percentile)
def _meets_condition(self, fs, threshold: float) -> bool:
    delta_h = fs.delta_h.get(fs.path, 0.0)  # From health Laplacian
    return delta_h > 0.4  # Absolute threshold, not percentile

# Example 4: ZONE_OF_PAIN (module-level, guards None)
def find(self, store: AnalysisStore) -> List[Finding]:
    field = store.signal_field.value
    findings = []

    for mod_path, ms in field.per_module.items():
        # CRITICAL: Guard instability=None
        if ms.instability is None:
            continue  # Isolated module, skip

        # Check Zone of Pain condition
        if ms.instability > 0.7 and ms.abstractness < 0.3:
            findings.append(...)

    return findings
```

---

## 🔑 Critical Implementation Rules

### **1. Hotspot Filter (FILE Scope)**

**Rule**: FILE-scoped finders MUST filter out low-activity files UNLESS finder is structural-only.

**Structural-only exceptions** (NO hotspot filter):
- ORPHAN_CODE
- PHANTOM_DEPENDENCY
- COPY_PASTE_CLONE
- FLAT_ARCHITECTURE

**All other FILE finders** (USE hotspot filter):
```python
median_changes = self._compute_median_changes(field)
for path, fs in field.per_file.items():
    if fs.total_changes <= median_changes:
        continue  # Skip cold files
```

**Why**: Avoid noise from rarely-touched files.

### **2. Tier-Aware Thresholds**

**Rule**: Use stricter thresholds for smaller codebases.

```python
def _get_threshold(self, tier: str) -> float:
    # Example: percentile threshold for "high-risk" condition
    thresholds = {
        "ABSOLUTE": 0.0,   # <15 files: no percentiles, use raw values
        "BAYESIAN": 0.5,   # 15-50 files: conservative (top 50%)
        "FULL": 0.7,       # 50+ files: standard (top 30%)
    }
    return thresholds.get(tier, 0.7)
```

**Tier determination** (already done in Phase 5):
- `tier = "ABSOLUTE"` if `file_count < 15`
- `tier = "BAYESIAN"` if `15 <= file_count < 50`
- `tier = "FULL"` if `file_count >= 50`

### **3. None Handling for instability**

**Rule**: Always guard `instability` before using it in conditions.

```python
# WRONG ❌
if ms.instability > 0.7:  # Crashes if None

# RIGHT ✅
if ms.instability is not None and ms.instability > 0.7:

# OR skip isolated modules entirely
if ms.instability is None:
    continue
```

**Why**: Isolated modules (no imports in/out) have `instability = None`.

### **4. Evidence Format**

**Rule**: Evidence must be actionable, include signal values + percentiles.

```python
def _build_evidence(self, fs) -> List[str]:
    """Build evidence from signals."""
    evidence = []

    # Signal value + percentile
    pctl_pr = fs.percentiles.get("pagerank", 0.0)
    evidence.append(f"PageRank: {fs.pagerank:.3f} (top {(1-pctl_pr)*100:.0f}%)")

    # Absolute counts
    evidence.append(f"Blast radius: {fs.blast_radius_size} files")

    # Trajectory
    evidence.append(f"Churn: {fs.churn_trajectory}")

    return evidence
```

### **5. Severity Computation**

**Rule**: Map signal strength to severity in finder's range.

```python
def _compute_severity(self, fs) -> float:
    """Compute severity for TOXIC_FILE."""
    # Finder range from registry: 0.80-0.95
    pctl_pr = fs.percentiles.get("pagerank", 0.0)
    pctl_churn = fs.percentiles.get("total_changes", 0.0)

    # Average percentiles, map to range
    avg_pctl = (pctl_pr + pctl_churn) / 2
    severity = 0.80 + (avg_pctl * 0.15)  # Maps [0,1] → [0.80, 0.95]

    return max(0.80, min(0.95, severity))
```

---

## 📝 Implementation Workflow (Batch-by-Batch)

### **Batch 1: Structural Finders** (Start Here)

**Goal**: Get familiar with finder structure using simple boolean conditions.

**Order** (easiest → hardest):
1. **ORPHAN_CODE** (`orphan_code.py`)
   - Condition: `fs.is_orphan == True`
   - No percentile, no hotspot filter
   - Severity: constant 0.40

2. **PHANTOM_DEPENDENCY** (`phantom_dependency.py`)
   - Condition: `fs.phantom_import_count > 0`
   - No percentile, no hotspot filter
   - Severity: `0.30 + 0.10 * min(phantom_count / 5, 1.0)`

3. **HOLLOW_CODE** (`hollow_code.py`)
   - Condition: `fs.stub_ratio > 0.5`
   - Uses percentile for severity boost
   - NEEDS hotspot filter ✅

4. **COPY_PASTE_CLONE** (`copy_paste_clone.py`)
   - Reads `store.clone_pairs` (not signal_field!)
   - Groups files by clone clusters
   - No hotspot filter (structural)

5. **FLAT_ARCHITECTURE** (`flat_architecture.py`)
   - Condition: `depth == 0 AND !is_orphan`
   - No percentile, no hotspot filter
   - CODEBASE scope (different pattern)

**Test after Batch 1**:
```bash
pytest tests/signals/test_batch1_finders.py -v
```

### **Batch 2: Architecture Finders**

**Goal**: Work with module-level signals and architecture violations.

**Order**:
6. **ZONE_OF_PAIN** (`zone_of_pain.py`)
   - Module scope, uses `instability` + `abstractness`
   - Guard `instability is None` ✅
   - Severity from main_seq_distance

7. **ACCIDENTAL_COUPLING** (`accidental_coupling.py`)
   - Reads `store.semantics` for concepts
   - Computes Jaccard similarity
   - FILE scope with hotspot filter

8. **CONWAY_VIOLATION** (`conway_violation.py`)
   - Reads `store.author_distances`
   - Cross-references `store.architecture.module_graph`
   - MODULE scope

9. **LAYER_VIOLATION** (`layer_violation.py`)
   - Reads `store.architecture.violations`
   - Groups by source module
   - MODULE scope

10. **INTERFACE_BLOAT** (`interface_bloat.py`)
    - FILE scope, role == "INTERFACE"
    - Checks `out_degree` (implementers)
    - Uses percentiles

**Test after Batch 2**:
```bash
pytest tests/signals/test_batch2_finders.py -v
```

### **Batch 3: Cross-Dimensional Finders**

**Goal**: Complex finders that fuse temporal + structural signals.

**Order**:
11. **WEAK_LINK** (`weak_link.py`)
    - Uses `delta_h` from health Laplacian
    - NO percentile (absolute threshold 0.4)
    - Detects files worse than neighbors

12. **KNOWLEDGE_ISLAND** (`knowledge_island.py`)
    - Uses `bus_factor` + `betweenness`
    - Detects single-author bottlenecks

13. **TEMPORAL_COUPLING** (`temporal_coupling.py`)
    - Reads `store.cochange` matrix
    - Finds files that co-change but lack import
    - Requires cross-referencing dependency graph

14. **TOXIC_FILE** (`toxic_file.py`)
    - Combines 4 percentiles: pagerank, churn, cognitive_load, risk_score
    - High-severity finder (0.80-0.95)

15. **ARCHITECTURE_EROSION** (`architecture_erosion.py`)
    - Reads `store.finding_history` (time series)
    - Detects increasing violation_rate
    - CODEBASE scope, needs 3+ snapshots

**Test after Batch 3**:
```bash
pytest tests/signals/test_batch3_finders.py -v
```

---

## 🧪 Testing Strategy

### **Test File Template**

Create `tests/signals/test_{finder_name}.py` for each finder:

```python
"""Tests for FINDER_NAME detection."""

import pytest

from shannon_insight.insights.finders.finder_name import FinderNameFinder
from shannon_insight.insights.store_v2 import AnalysisStore, Slot
from shannon_insight.signals.models import FileSignals, SignalField


class TestFinderNameDetection:
    """Test FINDER_NAME finder."""

    def test_detects_when_condition_met(self):
        """Should detect when condition from registry is met."""
        # Setup: Create SignalField with file meeting condition
        field = SignalField()
        fs = FileSignals(path="test.py")
        fs.is_orphan = True  # or whatever condition
        field.per_file["test.py"] = fs

        # Store
        store = AnalysisStore(root_dir="/tmp")
        store.signal_field = Slot[SignalField]()
        store.signal_field.set(field, "test")

        # Execute
        finder = FinderNameFinder()
        findings = finder.find(store)

        # Assert
        assert len(findings) == 1
        assert findings[0].finding_type == "finder_name"
        assert "test.py" in findings[0].files

    def test_no_detection_when_condition_not_met(self):
        """Should not detect when condition is not met."""
        field = SignalField()
        fs = FileSignals(path="test.py")
        fs.is_orphan = False  # Condition NOT met
        field.per_file["test.py"] = fs

        store = AnalysisStore(root_dir="/tmp")
        store.signal_field = Slot[SignalField]()
        store.signal_field.set(field, "test")

        finder = FinderNameFinder()
        findings = finder.find(store)

        assert len(findings) == 0

    def test_hotspot_filter_excludes_cold_files(self):
        """Should skip files with total_changes <= median."""
        field = SignalField()

        # Hot file (above median)
        fs_hot = FileSignals(path="hot.py")
        fs_hot.is_orphan = True
        fs_hot.total_changes = 100
        field.per_file["hot.py"] = fs_hot

        # Cold file (below median)
        fs_cold = FileSignals(path="cold.py")
        fs_cold.is_orphan = True
        fs_cold.total_changes = 1
        field.per_file["cold.py"] = fs_cold

        store = AnalysisStore(root_dir="/tmp")
        store.signal_field = Slot[SignalField]()
        store.signal_field.set(field, "test")

        finder = FinderNameFinder()
        findings = finder.find(store)

        # Only hot file should be detected
        assert len(findings) == 1
        assert findings[0].files == ["hot.py"]

    def test_tier_aware_threshold(self):
        """Should use stricter thresholds for BAYESIAN tier."""
        # Test with different tiers
        for tier, expected_count in [("ABSOLUTE", 0), ("BAYESIAN", 1), ("FULL", 2)]:
            field = SignalField(tier=tier)
            # Add test data...
            # Assert findings match expected count

    def test_severity_in_range(self):
        """Severity should be within registry-defined range."""
        # Create field with extreme values
        field = SignalField()
        fs = FileSignals(path="test.py")
        # Set signals to max values
        fs.pagerank = 1.0
        fs.percentiles = {"pagerank": 1.0}
        field.per_file["test.py"] = fs

        store = AnalysisStore(root_dir="/tmp")
        store.signal_field = Slot[SignalField]()
        store.signal_field.set(field, "test")

        finder = FinderNameFinder()
        findings = finder.find(store)

        # Check severity range from registry
        assert 0.3 <= findings[0].severity <= 0.95  # Adjust to finder's range

    def test_evidence_contains_signal_values(self):
        """Evidence should include key signal values."""
        # Setup...
        findings = finder.find(store)

        assert len(findings[0].evidence) > 0
        assert any("PageRank" in e for e in findings[0].evidence)

    def test_empty_signal_field_returns_no_findings(self):
        """Should return empty list if no files."""
        field = SignalField()
        store = AnalysisStore(root_dir="/tmp")
        store.signal_field = Slot[SignalField]()
        store.signal_field.set(field, "test")

        finder = FinderNameFinder()
        findings = finder.find(store)

        assert findings == []
```

### **Integration Test**

Create `tests/signals/test_all_finders_integration.py`:

```python
"""Integration test: all 15 new finders work together."""

from shannon_insight.insights.kernel import InsightKernel


def test_phase6_finders_in_kernel():
    """All Phase 6 finders should be registered and findable."""
    from shannon_insight.insights.finders import get_default_finders

    finders = get_default_finders()
    finder_names = {f.name for f in finders}

    # Phase 6 finders (15 new)
    expected_new = {
        "orphan_code",
        "phantom_dependency",
        "hollow_code",
        "copy_paste_clone",
        "flat_architecture",
        "zone_of_pain",
        "accidental_coupling",
        "conway_violation",
        "layer_violation",
        "interface_bloat",
        "weak_link",
        "knowledge_island",
        "temporal_coupling",
        "toxic_file",
        "architecture_erosion",
    }

    # Should include old + new finders
    assert expected_new.issubset(finder_names)


def test_kernel_runs_all_finders():
    """Kernel should run all finders without errors."""
    # This is a smoke test - use real codebase
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create minimal Python project
        Path(tmpdir, "test.py").write_text("def foo(): pass")

        kernel = InsightKernel(path=tmpdir)
        result = kernel.run()

        # Should complete without errors
        assert result is not None
        assert result.findings is not None
```

---

## 🚨 Common Pitfalls (From FAILURE-MODES.md)

### **Top 10 Bugs to Avoid**

1. **Signal name typos**: Use `Signal.PAGERANK` enum (once registry_v2 is imported)
2. **instability=None not guarded**: Always check before using
3. **Wrong percentile polarity**: semantic_coherence is HIGH=GOOD
4. **Forgot hotspot filter**: FILE finders (except 4 structural) need it
5. **Division by zero**: Use `max(x, 1)` for denominators
6. **Forgot tier check**: ABSOLUTE tier has no percentiles
7. **Used percentile instead of raw_risk**: WEAK_LINK uses raw_risk
8. **Circular import**: Import `Finding` from `models`, not from finders
9. **Forgot to sort findings**: Always `sorted(findings, key=lambda f: f.severity, reverse=True)`
10. **Evidence not actionable**: Include signal values + percentiles, not just "high risk"

---

## 📦 Final Integration

### **Update `insights/finders/__init__.py`**

After implementing all finders:

```python
"""Finder implementations."""

from .boundary_mismatch import BoundaryMismatchFinder
from .dead_dependency import DeadDependencyFinder
from .god_file import GodFileFinder
from .hidden_coupling import HiddenCouplingFinder
from .high_risk_hub import HighRiskHubFinder
from .unstable_file import UnstableFileFinder

# Phase 6: Batch 1 (Structural)
from .orphan_code import OrphanCodeFinder
from .phantom_dependency import PhantomDependencyFinder
from .hollow_code import HollowCodeFinder
from .copy_paste_clone import CopyPasteCloneFinder
from .flat_architecture import FlatArchitectureFinder

# Phase 6: Batch 2 (Architecture)
from .zone_of_pain import ZoneOfPainFinder
from .accidental_coupling import AccidentalCouplingFinder
from .conway_violation import ConwayViolationFinder
from .layer_violation import LayerViolationFinder
from .interface_bloat import InterfaceBloatFinder

# Phase 6: Batch 3 (Cross-dimensional)
from .weak_link import WeakLinkFinder
from .knowledge_island import KnowledgeIslandFinder
from .temporal_coupling import TemporalCouplingFinder
from .toxic_file import ToxicFileFinder
from .architecture_erosion import ArchitectureErosionFinder


def get_default_finders() -> list:
    """Return all default finders (old + new)."""
    return [
        # Phase 0-5 (existing)
        HighRiskHubFinder(),
        HiddenCouplingFinder(),
        GodFileFinder(),
        UnstableFileFinder(),
        BoundaryMismatchFinder(),
        DeadDependencyFinder(),
        # Phase 6: Batch 1
        OrphanCodeFinder(),
        PhantomDependencyFinder(),
        HollowCodeFinder(),
        CopyPasteCloneFinder(),
        FlatArchitectureFinder(),
        # Phase 6: Batch 2
        ZoneOfPainFinder(),
        AccidentalCouplingFinder(),
        ConwayViolationFinder(),
        LayerViolationFinder(),
        InterfaceBloatFinder(),
        # Phase 6: Batch 3
        WeakLinkFinder(),
        KnowledgeIslandFinder(),
        TemporalCouplingFinder(),
        ToxicFileFinder(),
        ArchitectureErosionFinder(),
    ]
```

### **Verify All Finders Registered**

```bash
python3 -c "
from shannon_insight.insights.finders import get_default_finders

finders = get_default_finders()
print(f'Total finders: {len(finders)}')  # Should be 21 (6 old + 15 new)

for f in finders:
    print(f'  ✓ {f.name}')
"
```

---

## ✅ Acceptance Criteria

Phase 6 is **COMPLETE** when:

- [ ] All 15 new finder classes implemented
- [ ] All finders registered in `get_default_finders()`
- [ ] Tests pass: `pytest tests/signals/ -v` (all batches)
- [ ] Integration test passes: `test_phase6_finders_in_kernel()`
- [ ] `make all` passes (format + type-check + tests)
- [ ] Manual smoke test on real codebase: `shannon-insight -C ./src`
- [ ] All finders return sorted findings (severity desc)
- [ ] All evidence includes signal values + percentiles
- [ ] Hotspot filter applied correctly (4 structural exceptions)
- [ ] No `instability=None` crashes

---

## 📚 Quick Reference Cards

### **Signal Lookup Cheat Sheet**

```python
# File signals (36 total)
fs.lines                    # int
fs.pagerank                 # float
fs.is_orphan                # bool
fs.total_changes            # int
fs.churn_trajectory         # str: "DORMANT"|"STABILIZING"|"CHURNING"|"SPIKING"
fs.percentiles["pagerank"]  # float [0,1] - USE THIS for thresholds
fs.risk_score               # float [0,1] - composite
fs.raw_risk                 # float [0,1] - for health Laplacian

# Module signals (15 total)
ms.instability              # Optional[float] - None if isolated ⚠️
ms.abstractness             # float [0,1]
ms.health_score             # float [0,1]
ms.layer_violation_count    # int

# Global signals (11 total)
g.clone_ratio               # float [0,1]
g.violation_rate            # float [0,1]
g.conway_alignment          # float [0,1]
g.team_size                 # int
```

### **Threshold Quick Reference**

| Finder | Tier | Threshold | Signal |
|--------|------|-----------|--------|
| ORPHAN | All | N/A | is_orphan (boolean) |
| TOXIC | FULL | 0.7 | pctl(pagerank), pctl(churn) |
| TOXIC | BAYESIAN | 0.5 | Same |
| WEAK_LINK | All | 0.4 | delta_h (absolute, not percentile) |
| ZONE_OF_PAIN | All | I>0.7, A<0.3 | instability, abstractness |

---

## 🎓 Learning Resources

Before starting, read these in order:

1. **FINDER-REHEARSAL.md** - Trace all 22 finders end-to-end
2. **FAILURE-MODES.md** - Learn from 22 common mistakes
3. **registry/finders.md** - Authoritative specs for all finders
4. **registry/composites.md** - How composite scores are built

---

## 🚀 You're Ready!

**Next step**: Start with Batch 1, `orphan_code.py`. Use the template above, read `registry/finders.md` line 45-56 for the ORPHAN_CODE spec, and implement.

**Time estimate**:
- Batch 1: 2 hours (5 finders × 24min)
- Batch 2: 3 hours (5 finders × 36min, more complex)
- Batch 3: 3 hours (5 finders × 36min, most complex)
- Integration + polish: 1 hour

**Total: 6-8 hours** for all 15 finders + tests + integration.

Good luck! 🎯
