# Phase 6 Quick Start (For Opus)

> **1-page reference** to keep open while implementing finders. Full details in `PHASE-6-IMPLEMENTATION-GUIDE.md`.

---

## ⚡ Implementation Checklist

```bash
# 1. Verify Phase 5 complete
python3 -c "from shannon_insight.signals.models import GlobalSignals; gs = GlobalSignals(); assert hasattr(gs, 'clone_ratio')"

# 2. Run tests before starting
pytest tests/signals/ -v

# 3. Implement finders in batches (use template below)
# 4. Test after each batch
# 5. Update get_default_finders() in __init__.py
# 6. Final check: make all
```

---

## 📋 15 Finders to Implement

| # | Name | File | Scope | Complexity |
|---|------|------|-------|------------|
| **Batch 1: Structural** ||||
| 1 | ORPHAN_CODE | `orphan_code.py` | FILE | ⭐ Easy |
| 2 | PHANTOM_DEPENDENCY | `phantom_dependency.py` | FILE | ⭐ Easy |
| 3 | HOLLOW_CODE | `hollow_code.py` | FILE | ⭐⭐ Medium |
| 4 | COPY_PASTE_CLONE | `copy_paste_clone.py` | FILE | ⭐⭐ Medium |
| 5 | FLAT_ARCHITECTURE | `flat_architecture.py` | CODEBASE | ⭐⭐ Medium |
| **Batch 2: Architecture** ||||
| 6 | ZONE_OF_PAIN | `zone_of_pain.py` | MODULE | ⭐⭐ Medium |
| 7 | ACCIDENTAL_COUPLING | `accidental_coupling.py` | FILE | ⭐⭐⭐ Hard |
| 8 | CONWAY_VIOLATION | `conway_violation.py` | MODULE | ⭐⭐⭐ Hard |
| 9 | LAYER_VIOLATION | `layer_violation.py` | MODULE | ⭐⭐ Medium |
| 10 | INTERFACE_BLOAT | `interface_bloat.py` | FILE | ⭐⭐ Medium |
| **Batch 3: Cross-Dimensional** ||||
| 11 | WEAK_LINK | `weak_link.py` | FILE | ⭐⭐⭐ Hard |
| 12 | KNOWLEDGE_ISLAND | `knowledge_island.py` | FILE | ⭐⭐ Medium |
| 13 | TEMPORAL_COUPLING | `temporal_coupling.py` | FILE | ⭐⭐⭐ Hard |
| 14 | TOXIC_FILE | `toxic_file.py` | FILE | ⭐⭐ Medium |
| 15 | ARCHITECTURE_EROSION | `architecture_erosion.py` | CODEBASE | ⭐⭐⭐ Hard |

---

## 🏗️ Finder Template (Copy & Modify)

```python
"""FINDER_NAME — One-line description from registry/finders.md."""

from typing import List

from ..models import Finding
from ..protocols_v2 import Finder
from ..store_v2 import AnalysisStore


class FinderNameFinder:
    """Detects FINDER_NAME pattern."""

    name = "finder_name"  # Lowercase, snake_case
    requires = frozenset({"signal_field"})

    def find(self, store: AnalysisStore) -> List[Finding]:
        """Main detection logic."""
        if not store.signal_field.available:
            return []

        field = store.signal_field.value
        findings: List[Finding] = []

        # 1. Get tier and threshold
        tier = field.tier
        threshold = self._get_threshold(tier)

        # 2. For FILE scope: compute hotspot filter (unless structural-only)
        if self._is_file_scope() and not self._is_structural_only():
            median_changes = self._median_changes(field)

        # 3. Iterate and detect
        for path, fs in field.per_file.items():
            # Apply hotspot filter
            if self._is_file_scope() and not self._is_structural_only():
                if fs.total_changes <= median_changes:
                    continue

            # Check condition
            if self._condition(fs, threshold):
                findings.append(
                    Finding(
                        finding_type=self.name,
                        severity=self._severity(fs),
                        title=self._title(fs),
                        files=[path],
                        evidence=self._evidence(fs),
                        suggestion=self._suggestion(fs),
                    )
                )

        return sorted(findings, key=lambda f: f.severity, reverse=True)

    def _get_threshold(self, tier: str) -> float:
        """Tier-aware threshold."""
        return {"ABSOLUTE": 0.0, "BAYESIAN": 0.5, "FULL": 0.7}.get(tier, 0.7)

    def _is_file_scope(self) -> bool:
        """Is this a FILE-scoped finder?"""
        return True  # False for MODULE/CODEBASE finders

    def _is_structural_only(self) -> bool:
        """Is this one of 4 structural-only finders?"""
        # orphan, phantom, clone, flat_arch don't use hotspot filter
        return False

    def _median_changes(self, field) -> int:
        """Compute median total_changes for hotspot filter."""
        changes = [fs.total_changes for fs in field.per_file.values()]
        if not changes:
            return 0
        changes = sorted(changes)
        n = len(changes)
        return changes[n // 2] if n % 2 == 1 else changes[n // 2 - 1]

    def _condition(self, fs, threshold: float) -> bool:
        """Detection condition from registry."""
        raise NotImplementedError  # ← IMPLEMENT FROM REGISTRY

    def _severity(self, fs) -> float:
        """Severity in [min, max] from registry."""
        raise NotImplementedError  # ← MAP SIGNAL TO SEVERITY RANGE

    def _title(self, fs) -> str:
        """Human-readable title."""
        raise NotImplementedError  # ← E.G., "Orphan file: {basename}"

    def _evidence(self, fs) -> List[str]:
        """Evidence list with signal values."""
        raise NotImplementedError  # ← INCLUDE PERCENTILES

    def _suggestion(self, fs) -> str:
        """Actionable suggestion."""
        raise NotImplementedError  # ← FROM REGISTRY
```

---

## 🔑 Critical Rules

### **Hotspot Filter (FILE Scope)**

```python
# Apply ONLY if:
# 1. FILE scope AND
# 2. NOT one of {orphan, phantom, clone, flat_arch}

if fs.total_changes <= median_changes:
    continue  # Skip cold files
```

### **instability=None Guard (MODULE Scope)**

```python
# ALWAYS guard before using instability
if ms.instability is None:
    continue  # Skip isolated modules
```

### **Percentile vs Raw Value**

```python
# Most finders: use percentiles
pctl = fs.percentiles.get("pagerank", 0.0)
if pctl > threshold:  # threshold from tier

# WEAK_LINK only: use raw_risk
delta_h = fs.delta_h.get(fs.path, 0.0)
if delta_h > 0.4:  # absolute threshold
```

---

## 📊 Signal Access Patterns

### **File Signals (Most Common)**

```python
fs.is_orphan                  # bool
fs.phantom_import_count       # int
fs.stub_ratio                 # float [0,1]
fs.depth                      # int (-1 if unreachable)
fs.total_changes              # int
fs.pagerank                   # float
fs.percentiles["pagerank"]    # float [0,1] ← USE FOR THRESHOLDS
fs.churn_trajectory           # str: "DORMANT"|"STABILIZING"|"CHURNING"|"SPIKING"
fs.bus_factor                 # float (≥1.0)
fs.risk_score                 # float [0,1] composite
fs.raw_risk                   # float [0,1] for Laplacian
```

### **Module Signals (Architecture)**

```python
ms.instability         # Optional[float] ⚠️ CAN BE NONE
ms.abstractness        # float [0,1]
ms.main_seq_distance   # float [0,1]
ms.health_score        # float [0,1]
ms.layer_violation_count  # int
```

### **Global Signals (Codebase)**

```python
g.clone_ratio          # float [0,1]
g.violation_rate       # float [0,1]
g.conway_alignment     # float [0,1]
g.team_size            # int
```

### **Store Slots (Non-SignalField)**

```python
store.clone_pairs.value         # List[ClonePair] for COPY_PASTE_CLONE
store.semantics.value          # Dict[str, FileSemantics] for ACCIDENTAL_COUPLING
store.author_distances.value   # List[AuthorDistance] for CONWAY_VIOLATION
store.architecture.value       # Architecture for LAYER_VIOLATION
store.cochange.value           # CoChangeMatrix for TEMPORAL_COUPLING
store.finding_history          # For ARCHITECTURE_EROSION
```

---

## 🧪 Test Template

```python
"""Test for FINDER_NAME."""

from shannon_insight.insights.finders.finder_name import FinderNameFinder
from shannon_insight.insights.store_v2 import AnalysisStore, Slot
from shannon_insight.signals.models import FileSignals, SignalField


def test_detects_condition():
    """Should detect when condition met."""
    field = SignalField()
    fs = FileSignals(path="test.py")
    # Set condition to trigger
    fs.is_orphan = True  # or whatever
    field.per_file["test.py"] = fs

    store = AnalysisStore(root_dir="/tmp")
    store.signal_field = Slot[SignalField]()
    store.signal_field.set(field, "test")

    finder = FinderNameFinder()
    findings = finder.find(store)

    assert len(findings) == 1
    assert findings[0].finding_type == "finder_name"


def test_no_detection_when_not_met():
    """Should not detect when condition not met."""
    # Same setup but condition false
    fs.is_orphan = False
    # ... rest same

    findings = finder.find(store)
    assert len(findings) == 0
```

---

## 📖 Registry Specs (Line Numbers)

Quick lookup for each finder spec in `docs/v2/registry/finders.md`:

| Finder | Lines | Condition | Severity Range |
|--------|-------|-----------|----------------|
| ORPHAN_CODE | 45-56 | `is_orphan == true` | 0.40 |
| PHANTOM_DEPENDENCY | 58-69 | `phantom_import_count > 0` | 0.30-0.40 |
| HOLLOW_CODE | 71-82 | `stub_ratio > 0.5` | 0.40-0.55 |
| COPY_PASTE_CLONE | 84-95 | NCD < 0.3 | 0.35-0.50 |
| FLAT_ARCHITECTURE | 97-108 | `depth==0 AND !orphan` | 0.30-0.40 |
| ZONE_OF_PAIN | 110-121 | `I>0.7 AND A<0.3` | 0.60-0.75 |
| ACCIDENTAL_COUPLING | 123-134 | `concept_overlap>0.6 AND !import` | 0.50-0.65 |
| CONWAY_VIOLATION | 136-147 | `author_dist>0.6 AND structural_coupling` | 0.55-0.70 |
| LAYER_VIOLATION | 149-160 | `violation exists` | 0.50-0.65 |
| INTERFACE_BLOAT | 162-173 | `role==INTERFACE AND out_degree<3` | 0.45-0.60 |
| WEAK_LINK | 175-186 | `delta_h > 0.4` | 0.55-0.70 |
| KNOWLEDGE_ISLAND | 188-199 | `bf<2 AND betw>pctl(0.7)` | 0.60-0.75 |
| TEMPORAL_COUPLING | 201-212 | `cochange>0.5 AND !import` | 0.50-0.65 |
| TOXIC_FILE | 214-225 | `pctl(pr)>0.7 AND pctl(churn)>0.7` | 0.80-0.95 |
| ARCHITECTURE_EROSION | 227-238 | `violation_rate increasing 3+ snapshots` | 0.65-0.80 |

---

## ⚠️ Top 5 Pitfalls

1. **Forgot hotspot filter** → FILE finders (except 4) need it
2. **instability=None crash** → Always guard before using
3. **Wrong percentile direction** → semantic_coherence is HIGH=GOOD
4. **Used percentile for WEAK_LINK** → It uses raw_risk, not percentile
5. **Forgot to sort findings** → Always sort by severity descending

---

## ✅ Done When

- [ ] All 15 finders implemented
- [ ] Updated `get_default_finders()` in `__init__.py`
- [ ] Tests pass: `pytest tests/signals/ -v`
- [ ] `make all` passes
- [ ] Smoke test: `shannon-insight -C ./src` runs without errors

---

**Time Budget**: 6-8 hours total
- Batch 1: 2h (easy warmup)
- Batch 2: 3h (architecture complexity)
- Batch 3: 3h (cross-dimensional fusion)

**Next**: Open `PHASE-6-IMPLEMENTATION-GUIDE.md` for full template and start with `orphan_code.py`!
