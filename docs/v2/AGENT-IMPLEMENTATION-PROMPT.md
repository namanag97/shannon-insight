# Shannon Insight v2 — Agent Implementation Prompt

> **MASTER PROMPT FOR CODING AGENT**
>
> This document contains everything needed to implement Shannon Insight v2.
> Follow it exactly. Do not deviate. Ask questions if anything is unclear.

---

## 0. Before You Start: Read Failure Modes

**CRITICAL**: Read `docs/v2/FAILURE-MODES.md` before writing any code.

It documents 22 specific ways implementation fails if you don't follow specs precisely:
- Signal name typos → finder silently never runs
- Instability=None not guarded → crash or NaN
- Wrong fusion order → WEAK_LINK produces garbage
- Polarity confusion → best files get flagged as worst
- Forgot tier check → ABSOLUTE tier finders silent
- Division by zero → crash on import-free files
- And 16 more...

Each failure mode has burned real projects. The document shows exact wrong code vs right code.

---

## 1. Project Context

### What is Shannon Insight?

Shannon Insight is a **codebase analysis tool** that uses information theory, graph algorithms, and git history to find architectural problems in code. It's on PyPI as `shannon-codebase-insight`, CLI is `shannon-insight`.

### Current State (v1)

- Working CLI tool with 247 tests
- 7 finders, 4 analyzers, 8 language scanners
- Blackboard pattern with `AnalysisStore`
- Located at: `/Users/namanagarwal/Projects/shannon-insight`

### What We're Building (v2)

- 62 signals (up from ~15)
- 22 finders (up from 7)
- Tree-sitter parsing (optional, with regex fallback)
- Architecture analysis (modules, layers, Martin metrics)
- Signal fusion with percentile normalization
- Health Laplacian for finding weak links

### Key Constraint

**Zero users** — we can break APIs freely. Aggressive refactoring is OK.

---

## 2. Git Management

### Branch Strategy

```
main                    ← production, always passing
  └── feature/v2-phase-N  ← one branch per phase
        └── (work here, squash merge to main)
```

### Before Starting Any Work

```bash
git checkout main
git pull origin main
git checkout -b feature/v2-phase-0  # or appropriate phase
```

### Commit Convention

```
[Phase N] Short description (imperative mood)

- What changed
- Why it changed
- Any edge cases handled

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Commit frequency**: After each file or logical unit. Small commits.

### Before Every Commit

```bash
make all  # MUST pass: format + check + test
```

If `make all` fails:
1. Fix the issue
2. Do NOT use `--no-verify`
3. Do NOT skip tests

### PR Process

1. Push branch: `git push -u origin feature/v2-phase-N`
2. Create PR with summary of changes
3. All tests must pass
4. Squash merge to main

### Git Safety Rules

- NEVER force push to main
- NEVER use `git reset --hard` without asking
- NEVER delete branches without asking
- ALWAYS commit before switching branches

---

## 3. Development Workflow

### Daily Rhythm

```
1. git pull origin main
2. Pick next item from phase checklist
3. Write test file FIRST
4. Implement until tests pass
5. make all
6. Commit with proper message
7. Repeat
```

### Test-First Development (Mandatory)

For every new file `foo.py`, create `tests/test_foo.py` FIRST.

```python
# tests/signals/test_registry.py (write this FIRST)
def test_signal_enum_has_62_entries():
    from signals.registry import Signal
    assert len(Signal) == 62

def test_pagerank_is_percentileable():
    from signals.registry import REGISTRY, Signal
    assert REGISTRY[Signal.PAGERANK].percentileable == True

# THEN implement signals/registry.py
```

### Verification After Each File

```bash
# 1. Tests pass
pytest tests/path/to/test_file.py -v

# 2. Types check
mypy src/shannon_insight/path/to/file.py

# 3. Format clean
ruff check src/shannon_insight/path/to/file.py

# 4. Full suite
make all
```

---

## 4. Spec Reference Map

### Where to Find What

| Need | File |
|------|------|
| Architecture overview | `docs/v2/SPEC-REFERENCE.md` |
| All 62 signal definitions | `docs/v2/registry/signals.md` |
| All 22 finder definitions | `docs/v2/registry/finders.md` |
| Composite formulas | `docs/v2/registry/composites.md` |
| Infrastructure patterns | `docs/v2/infrastructure.md` |
| Module contracts | `docs/v2/01-contracts.md` |
| Finder data flows | `docs/v2/FINDER-REHEARSAL.md` |
| Signal data flows | `docs/v2/SIGNAL-REHEARSAL.md` |
| Orchestration verification | `docs/v2/ORCHESTRATION-VERIFICATION.md` |
| **FAILURE MODES** | `docs/v2/FAILURE-MODES.md` ← **READ THIS FIRST** |
| Step-by-step guide | `docs/v2/IMPLEMENTATION-GUIDE.md` |
| Phase N details | `docs/v2/phases/phase-N-*.md` |

### When Implementing a Signal

1. Find signal in `registry/signals.md` (has #, formula, edge cases)
2. Check producer in `SIGNAL-REHEARSAL.md`
3. Check consumers in `SIGNAL-REHEARSAL.md`
4. Implement in producer module
5. Verify signal appears in SignalField

### When Implementing a Finder

1. Find finder in `registry/finders.md` (has condition, tier, hotspot)
2. Check data flow in `FINDER-REHEARSAL.md`
3. Check activation in `ORCHESTRATION-VERIFICATION.md` §4
4. Implement in `insights/finders/`
5. Register in kernel

---

## 5. Implementation Order (Critical)

### Phase 0: Infrastructure (~1 week)

**Build in this exact order:**

```
1. exceptions/taxonomy.py        ← Error codes
2. signals/registry.py           ← Signal enum + SignalMeta
3. insights/store.py             ← Slot[T] wrapper
4. insights/protocols.py         ← Enhanced Analyzer/Finder protocols
5. insights/kernel.py            ← graphlib topo-sort
6. insights/validation.py        ← Phase validators
7. insights/threshold.py         ← ThresholdStrategy
8. signals/fusion.py             ← FusionPipeline skeleton
```

**Checkpoint**: Run this test before proceeding:

```python
def test_infrastructure_complete():
    from signals.registry import Signal, REGISTRY
    from insights.store import AnalysisStore, Slot
    from insights.protocols import Analyzer, Finder
    from insights.kernel import InsightKernel
    from insights.validation import validate_after_scanning

    # Signal registry works
    assert len(Signal) == 62
    assert Signal.PAGERANK in REGISTRY

    # Slot works
    slot = Slot()
    assert not slot.available
    slot.set("value", "producer")
    assert slot.available
    assert slot.value == "value"

    # Store has all slots
    store = AnalysisStore()
    assert hasattr(store, 'signal_field')

    # Kernel can be instantiated
    kernel = InsightKernel(".")
```

### Phase 1: Tree-sitter Parsing (~3 weeks)

**Start with Python only. Other languages later.**

```
1. scanning/treesitter_parser.py  ← Core wrapper
2. scanning/queries/python.py     ← Python queries
3. scanning/normalizer.py         ← Captures → FileSyntax
4. scanning/fallback.py           ← Regex fallback
5. scanning/factory.py            ← Route tree-sitter/regex
6. Update scanning/models.py      ← Add FunctionDef.body_tokens, .calls
```

**Checkpoint**:

```python
def test_parsing_complete():
    from scanning import scan_file

    syntax = scan_file("tests/fixtures/sample.py")
    assert syntax.function_count > 0
    assert all(f.body_tokens >= 0 for f in syntax.functions)
    assert syntax.max_nesting >= 0
```

### Phase 2-7: Follow IMPLEMENTATION-GUIDE.md

Each phase has:
- Deliverable files
- Checkpoint test
- Acceptance criteria

**DO NOT start Phase N+1 until Phase N checkpoint passes.**

---

## 6. Code Patterns (Copy These)

### Signal Registration

```python
# signals/registry.py
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Set

class Signal(Enum):
    # IR1 scanning
    LINES = "lines"
    FUNCTION_COUNT = "function_count"
    # ... all 62 signals

@dataclass(frozen=True)
class SignalMeta:
    signal: Signal
    dtype: type
    scope: str  # "file" | "module" | "global"
    percentileable: bool
    polarity: str  # "high_is_bad" | "high_is_good" | "neutral"
    absolute_threshold: Optional[float]
    produced_by: str
    phase: int

REGISTRY: Dict[Signal, SignalMeta] = {}

def register(meta: SignalMeta) -> None:
    if meta.signal in REGISTRY:
        existing = REGISTRY[meta.signal]
        if existing.produced_by != meta.produced_by:
            raise ValueError(f"Signal {meta.signal} already registered by {existing.produced_by}")
        return
    REGISTRY[meta.signal] = meta

# Register all signals
register(SignalMeta(Signal.LINES, int, "file", True, "high_is_bad", 500, "scanning/metrics", 0))
register(SignalMeta(Signal.PAGERANK, float, "file", True, "high_is_bad", 0.005, "graph/algorithms", 0))
# ... all 62
```

### Typed Slot

```python
# insights/store.py
from dataclasses import dataclass, field
from typing import TypeVar, Generic, Optional

T = TypeVar("T")

@dataclass
class Slot(Generic[T]):
    _value: Optional[T] = None
    _error: Optional[str] = None
    _produced_by: str = ""

    @property
    def available(self) -> bool:
        return self._value is not None

    @property
    def value(self) -> T:
        if self._value is None:
            raise LookupError(f"Slot not populated{f': {self._error}' if self._error else ''}")
        return self._value

    def get(self, default: T = None) -> Optional[T]:
        return self._value if self._value is not None else default

    def set(self, value: T, produced_by: str) -> None:
        self._value = value
        self._produced_by = produced_by

    def set_error(self, error: str, produced_by: str) -> None:
        self._error = error
        self._produced_by = produced_by
```

### Analyzer Protocol

```python
# insights/protocols.py
from typing import Protocol, Set, Optional, List

class Analyzer(Protocol):
    name: str
    api_version: str
    requires: Set[str]
    provides: Set[str]
    run_last: bool
    error_mode: str  # "fail" | "skip" | "degrade"

    def analyze(self, store: "AnalysisStore") -> None: ...
```

### Finder Protocol

```python
class Finder(Protocol):
    name: str
    api_version: str
    requires: Set[str]
    error_mode: str
    hotspot_filtered: bool
    tier_minimum: str  # "ABSOLUTE" | "BAYESIAN" | "FULL"

    def find(self, store: "AnalysisStore") -> List["Finding"]: ...
```

### Finder Implementation

```python
# insights/finders/zone.py
from insights.protocols import Finder
from insights.models import Finding

class ZoneOfPainFinder:
    name = "zone_of_pain"
    api_version = "2.0"
    requires = {"architecture", "signal_field"}
    error_mode = "skip"
    hotspot_filtered = False
    tier_minimum = "BAYESIAN"

    def find(self, store):
        if not store.architecture.available:
            return []

        findings = []
        for mod_path, mod in store.architecture.value.modules.items():
            # CRITICAL: guard for None instability
            if mod.instability is None:
                continue

            if mod.abstractness < 0.3 and mod.instability < 0.3:
                findings.append(Finding(
                    type="ZONE_OF_PAIN",
                    scope="MODULE",
                    targets=[mod_path],
                    severity=0.60,
                    confidence=self._compute_confidence(mod),
                    evidence=self._build_evidence(mod),
                    suggestion="Concrete and stable — hard to change. Extract interfaces.",
                ))
        return findings

    def _compute_confidence(self, mod) -> float:
        margin_a = (0.3 - mod.abstractness) / 0.3
        margin_i = (0.3 - mod.instability) / 0.3
        return (margin_a + margin_i) / 2
```

### Composite Formula

```python
# signals/composites.py
def compute_risk_score(fs: FileSignals, field: SignalField) -> float:
    """
    risk_score = 0.25×pctl(pagerank) + 0.20×pctl(blast_radius)
               + 0.20×pctl(cognitive_load) + 0.20×instability_factor
               + 0.15×(1 - bus_factor/max_bf)
    """
    pctl = fs.percentiles
    max_bf = field.global_signals.max_bus_factor or 1.0

    instability_factor = 1.0 if fs.churn_trajectory in ("CHURNING", "SPIKING") else 0.3

    return (
        0.25 * pctl.get("pagerank", 0) +
        0.20 * pctl.get("blast_radius_size", 0) +
        0.20 * pctl.get("cognitive_load", 0) +
        0.20 * instability_factor +
        0.15 * (1 - (fs.bus_factor or 1.0) / max_bf)
    )
```

---

## 7. Edge Case Handling (Mandatory)

### Always Check These

```python
# Before using instability
if mod.instability is None:
    continue  # or skip, don't use 0.0

# Before dividing
result = numerator / denominator if denominator != 0 else 0.0

# Before using percentiles
if field.tier == "ABSOLUTE":
    # Use absolute thresholds, not percentiles
    return

# Before using temporal signals
if not store.git_history.available:
    # Use defaults or skip
    return

# Before using architecture
if not store.architecture.available or len(store.architecture.value.modules) < 2:
    # Skip architecture finders
    return
```

### Fallback Values

| Signal | Edge Case | Fallback |
|--------|-----------|----------|
| impl_gini | ≤1 function | 0.0 |
| stub_ratio | 0 functions | 0.0 |
| concept_entropy | <3 functions | 0.0 |
| naming_drift | generic filename | 0.0 |
| depth | no entry points | 0 for all |
| bus_factor | single commit | 1.0 |
| instability | Ca+Ce=0 | None (not 0.0) |
| delta_h | orphan file | 0.0 |

---

## 8. Verification Checklist

### After Each File

- [ ] Tests pass: `pytest tests/path/to/test.py -v`
- [ ] Types check: `mypy src/shannon_insight/path/to/file.py`
- [ ] Format clean: `ruff check src/shannon_insight/path/to/file.py`
- [ ] No new warnings

### After Each Phase

- [ ] Phase checkpoint test passes
- [ ] `make all` passes
- [ ] Commit with `[Phase N]` prefix
- [ ] Push to feature branch

### Before PR

- [ ] All phase checkpoints pass
- [ ] Full `make all` passes
- [ ] No TODO/FIXME in new code
- [ ] Spec references match implementation

---

## 9. Troubleshooting

### "Signal not found in registry"

```python
# Ensure signal is registered at module load time
# In signals/registry.py, add:
register(SignalMeta(Signal.YOUR_SIGNAL, ...))
```

### "Analyzer dependency cycle"

```python
# Check requires/provides don't form a cycle
# graphlib.CycleError message shows the cycle
# Fix by adjusting requires or splitting analyzer
```

### "Slot not populated"

```python
# Check that the producing analyzer ran
# Check that analyzer didn't fail (look at slot._error)
# Check topo-sort order
```

### "Finder didn't fire"

```python
# Check tier: finder may need BAYESIAN but you're in ABSOLUTE
# Check hotspot: total_changes may be below median
# Check requires: store slots may be missing
# Check edge case guards: instability=None, etc.
```

### "Test fails on CI but passes locally"

```python
# Check for ordering assumptions (use sorted())
# Check for floating point precision (use pytest.approx())
# Check for path separators (use pathlib)
```

---

## 10. Communication Protocol

### When to Ask Questions

- Spec is ambiguous or contradictory
- Implementation choice not covered by spec
- Test is failing and you don't understand why
- You want to deviate from spec (always ask first)

### How to Ask

```
I'm implementing [specific thing] in Phase [N].

The spec says: [quote from spec]

But I'm encountering: [issue]

Options I see:
1. [option A]
2. [option B]

Which should I do?
```

### When to Stop and Report

- `make all` fails and you can't fix it
- Spec has a clear bug/contradiction
- Performance is unexpectedly bad (>10s for small codebase)
- You've spent >1 hour on one issue

---

## 11. Success Criteria

### Phase 0 Complete When

- [ ] All 62 signals in Signal enum
- [ ] Signal registry validates single-owner
- [ ] Slot[T] provides error context
- [ ] Topo-sort handles diamonds and detects cycles
- [ ] Validation catches phase contract violations
- [ ] `make all` passes

### Phase 1 Complete When

- [ ] Python files parse with tree-sitter
- [ ] FunctionDef has body_tokens, calls
- [ ] max_nesting computed correctly
- [ ] stub_ratio uses formula from spec
- [ ] Regex fallback works when tree-sitter fails
- [ ] `make all` passes

### v2 Complete When

- [ ] All 62 signals computed
- [ ] All 22 finders implemented
- [ ] All 3 tiers work (ABSOLUTE, BAYESIAN, FULL)
- [ ] All edge cases handled per spec
- [ ] `shannon-insight -C .` runs on this repo
- [ ] `make all` passes

---

## 12. Quick Reference Commands

```bash
# Development
make install          # pip install -e ".[dev]"
make all              # format + check + test
make test             # pytest with coverage
make check            # mypy + ruff

# Testing
pytest tests/test_foo.py -v           # Single file
pytest tests/ -k "test_name" -v       # Single test
pytest tests/ --tb=short              # Short traceback

# Git
git status                            # Check state
git diff                              # See changes
git add <file>                        # Stage specific file
git commit -m "[Phase N] message"     # Commit
git push -u origin feature/v2-phase-N # Push

# CLI (after implementation)
shannon-insight -C .                  # Analyze current dir
shannon-insight -C . --verbose        # Debug output
shannon-insight -C . --json           # JSON output
```

---

## 13. File Layout Reference

```
src/shannon_insight/
├── exceptions/
│   └── taxonomy.py          ← Error codes (Phase 0)
├── signals/
│   ├── registry.py          ← Signal enum + SignalMeta (Phase 0)
│   ├── fusion.py            ← FusionPipeline (Phase 0 skeleton, Phase 5 full)
│   ├── normalization.py     ← Percentiles (Phase 5)
│   ├── composites.py        ← Composite formulas (Phase 5)
│   └── health_laplacian.py  ← Δh computation (Phase 5)
├── scanning/
│   ├── treesitter_parser.py ← Core parser (Phase 1)
│   ├── queries/python.py    ← Python queries (Phase 1)
│   ├── normalizer.py        ← Captures → FileSyntax (Phase 1)
│   └── fallback.py          ← Regex fallback (Phase 1)
├── semantics/
│   ├── analyzer.py          ← SemanticAnalyzer (Phase 2)
│   ├── roles.py             ← Role classification (Phase 2)
│   └── concepts.py          ← TF-IDF + Louvain (Phase 2)
├── graph/
│   ├── algorithms.py        ← + depth, orphans (Phase 3)
│   ├── clone_detection.py   ← MinHash + NCD (Phase 3)
│   └── distance.py          ← G5 author distance (Phase 3)
├── architecture/
│   ├── analyzer.py          ← ArchitectureAnalyzer (Phase 4)
│   ├── modules.py           ← Module detection (Phase 4)
│   ├── metrics.py           ← Martin metrics (Phase 4)
│   └── layers.py            ← Layer inference (Phase 4)
├── insights/
│   ├── protocols.py         ← Enhanced protocols (Phase 0)
│   ├── store.py             ← Slot[T] + AnalysisStore (Phase 0)
│   ├── kernel.py            ← + topo-sort (Phase 0)
│   ├── validation.py        ← Phase validators (Phase 0)
│   ├── threshold.py         ← ThresholdStrategy (Phase 0)
│   └── finders/             ← 15 new finders (Phase 6)
└── persistence/
    └── models.py            ← TensorSnapshot (Phase 7)
```

---

## 14. First-Time-Right Commitments

### What the Spec Guarantees

1. **No undefined behavior** — Every edge case documented
2. **No orphan signals** — All have producers and consumers
3. **No dependency cycles** — DAG verified
4. **No type ambiguity** — All contracts explicit
5. **No missing handoffs** — Full orchestration traced

### What You Must Do

1. **Follow the spec exactly** — Don't improvise
2. **Test first** — Write test before implementation
3. **Check edge cases** — Use fallback values from spec
4. **Validate constantly** — `make all` after every change
5. **Ask when unsure** — Don't guess

### What We Accept May Need Iteration

1. **Composite weights** — Marked as "beta", will calibrate later
2. **Non-Python languages** — Start with Python only
3. **Performance tuning** — Correctness first, optimize later
4. **UI/output format** — Can refine based on usage

---

*This prompt is the single source of truth for implementation. All spec documents support this prompt. If there's a conflict, ask before proceeding.*
