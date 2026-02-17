# Temporal Module Architectural Analysis and Redesign

**Document Version:** 1.0  
**Date:** 2026-02-17  
**Status:** Design Phase

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Phase 1: Current Architecture Assessment](#phase-1-current-architecture-assessment)
3. [Phase 2: Requirements Analysis](#phase-2-requirements-analysis)
4. [Phase 3: Proposed Architecture](#phase-3-proposed-architecture)
5. [Phase 4: Migration Strategy](#phase-4-migration-strategy)
6. [Extension Points](#extension-points)
7. [Key Design Decisions](#key-design-decisions)

---

## Executive Summary

The Shannon Insight temporal module provides git-based temporal analysis capabilities including churn trajectories, co-change patterns, author distributions, and various temporal signals. The current implementation (~1,450 lines across 6 files) is functional but exhibits significant architectural limitations that hinder extensibility and performance for advanced temporal operations like line-level churn, fix traceability, graph evolution, and historical reconstruction.

This document proposes a comprehensive redesign that introduces:

- **Event-driven architecture** for capturing fine-grained git events
- **Pluggable analyzer framework** for extensibility
- **Incremental processing** with proper caching strategies
- **Time-series data structures** optimized for temporal queries
- **Entity identity management** for tracking files across renames/moves
- **Layered abstraction** separating concerns (extraction → analysis → storage → query)

The redesign maintains backward compatibility while enabling advanced capabilities identified in the v2 spec, including historical reconstruction, temporal operators, and finding lifecycle tracking.

---

## Phase 1: Current Architecture Assessment

### 1.1 Module Structure

```
temporal/
├── __init__.py                 (18 lines) - Public API exports
├── models.py                   (97 lines) - Data models
├── git_extractor.py           (221 lines) - Git log parsing
├── cache.py                   (272 lines) - SQLite commit cache
├── churn.py                   (223 lines) - Churn time series computation
├── cochange.py                (104 lines) - Co-change matrix computation
└── Temporal Module Architecture.md (514 lines) - Documentation
```

**Total:** ~1,450 lines of Python code

### 1.2 Current Data Models

```python
# Core Entities
@dataclass
class Commit:
    hash: str
    timestamp: int  # unix seconds
    author: str
    files: list[str]  # relative paths changed
    subject: str  # commit message subject

@dataclass
class GitHistory:
    commits: list[Commit]  # newest first
    file_set: set[str]  # all files ever seen
    span_days: int  # time range covered

# Analysis Results
@dataclass
class ChurnSeries:
    file_path: str
    window_counts: list[int]  # changes per time window
    total_changes: int
    trajectory: str  # DORMANT|STABILIZING|STABLE|CHURNING|SPIKING
    slope: float
    cv: float  # coefficient of variation
    bus_factor: float  # 2^H where H = author entropy
    author_entropy: float
    fix_ratio: float  # fraction of fix commits
    refactor_ratio: float  # fraction of refactor commits
    change_entropy: float  # entropy of change distribution

@dataclass
class CoChangePair:
    file_a: str
    file_b: str
    cochange_count: int  # raw count
    total_a: int | float  # weighted count
    total_b: int | float
    confidence_a_b: float  # P(B | A changed)
    confidence_b_a: float  # P(A | B changed)
    lift: float  # observed / expected
    weight: float  # temporal-decay-weighted

@dataclass
class CoChangeMatrix:
    pairs: dict[tuple[str, str], CoChangePair]
    total_commits: int
    file_change_counts: dict[str, int]

# Classification Enum
class Trajectory(str, Enum):
    DORMANT = "DORMANT"
    STABILIZING = "STABILIZING"
    STABLE = "STABLE"
    CHURNING = "CHURNING"
    SPIKING = "SPIKING"
```

### 1.3 Current Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   TemporalAnalyzer                         │
│                   (orchestrator)                           │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   GitExtractor                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │_is_git_  │───▶│_run_git_ │───▶│_parse_   │          │
│  │repo      │    │log       │    │log       │          │
│  └──────────┘    └──────────┘    └──────────┘          │
│                                            │             │
│                                            ▼             │
│                                    ┌───────────┐        │
│                                    │GitHistory │        │
│                                    └───────────┘        │
└─────────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│build_churn_    │ │build_cochange_  │ │compute_author_  │
│series          │ │matrix          │ │distances       │
└─────────────────┘ └─────────────────┘ └─────────────────┘
          │               │               │
          ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│Dict[path,       │ │CoChangeMatrix   │ │List[Author     │
│ChurnSeries]     │ │                 │ │Distance]       │
└─────────────────┘ └─────────────────┘ └─────────────────┘
                          │
                          └───────────────┬───────────────┘
                                          ▼
                            ┌─────────────────────────┐
                            │    AnalysisStore       │
                            │  (blackboard pattern)  │
                            │ ────────────────────   │
                            │ • git_history          │
                            │ • churn                │
                            │ • cochange            │
                            │ • author_distances     │
                            └─────────────────────────┘
```

### 1.4 Integration Points

**Dependencies FROM temporal:**
- `infrastructure.entities` - EntityId, EntityType for FactStore integration
- `infrastructure.signals` - Signal enum for writing to FactStore
- `graph.distance` - compute_author_distances() function
- `graph.models` - AuthorDistance model
- `insights.store` - AnalysisStore (blackboard)
- `persistence` - For future historical reconstruction

**Dependencies ON temporal:**
- `insights.analyzers.temporal` - TemporalAnalyzer orchestrates temporal module
- `signals.models` - SignalField for churn signals
- `finders` - Various patterns finders consume churn/cochange data
- `persistence.capture` - Emits churn data to snapshots

### 1.5 What Works Well

1. **Clean separation of concerns**: Git extraction, churn computation, co-change computation are separate modules
2. **Graceful degradation**: Handles non-git repos, shallow clones, single-author projects
3. **Incremental caching**: CommitCache avoids re-parsing git history on subsequent runs
4. **Rich temporal signals**: Computes 8 signals per file (total_changes, trajectory, slope, cv, bus_factor, author_entropy, fix_ratio, refactor_ratio, change_entropy)
5. **Type safety**: Uses dataclasses with clear field types
6. **Well-tested**: Comprehensive test coverage for churn, trajectory, co-change

### 1.6 Limitations and Technical Debt

#### Critical Limitations

**1. No Entity Identity Management**
- Files are tracked by string paths only
- No support for file renames (git mv, path changes)
- Cannot track a file's identity across its entire lifecycle
- Breaks historical reconstruction when files are moved

**2. Coarse-Grained Events**
- Only captures commit-level changes (which files changed in a commit)
- No line-level granularity: cannot determine WHICH lines changed
- Cannot implement line-level churn analysis
- Cannot support "hotspot" analysis (which specific lines change frequently)

**3. No Historical Reconstruction**
- Cannot reconstruct file/graph state at past commits
- Requires full re-parsing of git history for each historical query
- No support for on-demand historical analysis (git show <sha>:<path>)
- Cannot fill the temporal tensor for CP/Tucker decomposition

**4. Monolithic Pipeline**
- Single TemporalAnalyzer orchestrates everything
- No plugin architecture for adding new analyzers
- Hard to extend with new temporal computations (line-level churn, fix traceability)
- All analysis runs on every invocation, even if only need specific signals

**5. Limited Temporal Queries**
- No time-range filtering (get commits between t1 and t2)
- No efficient temporal indexing for queries like "what changed in last 30 days?"
- Churn uses fixed 4-week windows, cannot adapt to different granularities
- No support for rolling windows or exponential weighting

#### Performance Issues

**6. Memory Pressure**
- Loads entire commit list into memory (GitExtractor._MAX_OUTPUT_BYTES = 50MB)
- Churn builds full time series for every file even if not queried
- Co-change computes all pairs upfront (O(n²) complexity for files in same commit)

**7. No Lazy Evaluation**
- Computes all churn series before any query
- Cannot stream results for large codebases
- No support for progressive rendering in web UI

#### Maintainability Issues

**8. Tight Coupling**
- TemporalAnalyzer directly calls build_churn_series, build_cochange_matrix
- No clear interfaces/protocols for analyzers
- Hard to unit test individual components in isolation

**9. Hardcoded Configuration**
- Time window size (4 weeks) is hardcoded
- Temporal decay lambda (90-day half-life) is hardcoded
- Trajectory thresholds (slope=0.1, cv=0.5) are hardcoded
- No way to customize for different use cases

**10. Error Handling Inconsistency**
- Some functions return empty dict/list on error
- Some return None
- No unified error types for temporal operations

#### Missing Capabilities (per v2 spec)

**11. No Temporal Operators Framework**
- While the spec defines delta, velocity, acceleration, trajectory, volatility, trend
- Only trajectory is implemented
- No reusable operator implementations that can apply to any signal
- Each signal must implement its own temporal logic

**12. No Finding Lifecycle Tracking**
- Cannot track when a finding first appeared
- Cannot track if a finding was resolved and reappeared
- No persistence of finding evolution over time

**13. No Graph Evolution Support**
- Cannot track how dependency graph changes over time
- Cannot detect "architectural drift"
- No support for temporal graph analysis (when did edges appear/disappear?)

**14. Limited Fix Traceability**
- fix_ratio only uses commit subject keywords
- No link between specific code changes and the bugs they fix
- Cannot analyze "bug fix patterns" (which files/lines cause most bugs)

---

## Phase 2: Requirements Analysis

### 2.1 Data Capture Requirements

Based on v2 spec and future capabilities:

| Category | Data Source | Current | Needed | Priority |
|----------|-------------|---------|--------|----------|
| **Commit Events** | git log | ✓ (commit-level) | ✓ | P0 |
| **File Changes** | git show --name-status | ✓ (file-level) | ✓ | P0 |
| **Line Changes** | git blame / git diff | ✗ | ✓ | P1 |
| **Renames/Moves** | git log --follow | ✗ | ✓ | P1 |
| **Merge Commits** | git log --merges | ✗ (filtered out) | ✓ | P2 |
| **Branch History** | git branch -a | ✗ | ✓ | P3 |

**Granularity Required:**
```
Current:  Commit → [files_changed]  (coarse)
Desired:  Commit → {file: [lines_changed]}  (fine-grained)
Ultimate: Commit → {file: {line: (old_content, new_content, author, timestamp)}}  (full)
```

### 2.2 Computation Requirements

| Computation | Current | Needed | Use Case |
|------------|---------|--------|----------|
| **Churn Series** | ✓ (file-level) | ✓ + line-level | File churn, hotspot analysis |
| **Co-Change** | ✓ | ✓ | Architectural coupling |
| **Author Distribution** | ✓ | ✓ | Bus factor, Conway's Law |
| **Trajectory Classification** | ✓ | ✓ | File lifecycle tracking |
| **Temporal Operators** | Partial | Full (Δ, v, a, traj, vol, trend) | Signal evolution |
| **Fix Traceability** | Partial (keyword-based) | Full | Bug pattern analysis |
| **Graph Evolution** | ✗ | ✓ | Architectural drift detection |
| **Pattern Detection** | ✗ | ✓ | Anomaly detection in evolution |

### 2.3 Query Requirements

| Query Type | Current | Needed | Complexity |
|------------|---------|--------|------------|
| **Get commits for file** | O(n) scan | O(log n) with index | Simple |
| **Get time series for signal** | O(1) (pre-computed) | O(1) (cached) | Simple |
| **Get changes in time range** | O(n) scan | O(log n) + k | Medium |
| **Get line-level churn for file** | ✗ | O(log n) + k | Medium |
| **Get co-change pairs above threshold** | O(1) (pre-computed) | O(log n) + k | Medium |
| **Compare two historical states** | ✗ | O(n) reconstruction | Complex |
| **Track file across renames** | ✗ | O(k) (follow chain) | Medium |
| **Find bug-introducing commits** | ✗ | O(n) search + git bisect | Complex |

### 2.4 Extension Points Required

1. **Temporal Analyzers**: Pluggable analyzers for different temporal computations
2. **Temporal Operators**: Reusable operators applicable to any time series
3. **Event Processors**: Process git events at different granularities (commit, file, line)
4. **Time Series Backends**: Different storage strategies (in-memory, SQLite, TimescaleDB)
5. **Identity Resolvers**: Track entity identity across renames/moves
6. **Query Builders**: Composable query DSL for temporal queries

### 2.5 Performance Considerations

| Metric | Target | Current | Gap |
|--------|--------|---------|-----|
| **Git parsing time** | < 5s for 10k commits | ~2-10s | Needs optimization for line-level |
| **Memory usage** | < 500MB for 100k commits | ~50MB limit | Will explode with line-level |
| **Query latency** | < 100ms for time series | < 10ms (cached) | Acceptable |
| **Incremental update** | < 1s for 100 new commits | N/A | Not implemented |
| **Historical reconstruction** | < 5s per commit | N/A | Not implemented |

**Optimization Strategies Needed:**
- Streaming git log processing (don't load all into memory)
- Lazy computation (compute time series on demand)
- Time-series database with efficient temporal indexes
- Incremental updates (only process new commits)
- Caching strategies for expensive computations
- Parallel processing for independent analyzers

---

## Phase 3: Proposed Architecture

### 3.1 Design Principles

1. **Layered Abstraction**: Clear separation between extraction, analysis, storage, and query layers
2. **Plugin Architecture**: Extensible analyzer and operator plugins
3. **Entity-Centric**: Track entities (files, commits, authors, lines) with canonical identities
4. **Event-Driven**: Capture events at appropriate granularity for analysis
5. **Incremental Processing**: Only process new data on subsequent runs
6. **Lazy Evaluation**: Compute expensive results on demand, cache aggressively
7. **Type Safety**: Use protocols/dataclasses with clear contracts
8. **Testability**: Each component independently testable with clear dependencies

### 3.2 Module Structure

```
temporal/
├── __init__.py                      # Public API (minimal)
│
├── core/                            # Core abstractions and interfaces
│   ├── __init__.py
│   ├── models.py                   # Core entity models
│   ├── protocols.py                # Protocol interfaces
│   ├── identity.py                 # Entity identity management
│   └── time.py                    # Time utilities and ranges
│
├── extraction/                      # Git event extraction
│   ├── __init__.py
│   ├── base.py                     # Abstract extractor interface
│   ├── commit_extractor.py          # Commit-level extraction
│   ├── file_change_extractor.py     # File-level changes (git log --name-status)
│   ├── line_change_extractor.py     # Line-level changes (git blame/diff)
│   ├── rename_tracker.py           # Track file renames (git log --follow)
│   └── streaming.py                # Streaming git log processing
│
├── analysis/                        # Temporal analysis plugins
│   ├── __init__.py
│   ├── base.py                     # Base temporal analyzer protocol
│   ├── churn_analyzer.py           # Churn time series (file + line)
│   ├── cochange_analyzer.py        # Co-change patterns
│   ├── author_analyzer.py          # Author distribution and distances
│   ├── fix_traceability_analyzer.py # Fix pattern analysis
│   ├── graph_evolution_analyzer.py # Graph evolution tracking
│   └── registry.py                # Analyzer registration
│
├── operators/                       # Reusable temporal operators
│   ├── __init__.py
│   ├── base.py                     # Operator protocol
│   ├── delta.py                    # Δ operator
│   ├── velocity.py                 # Velocity operator
│   ├── acceleration.py             # Acceleration operator
│   ├── trajectory.py               # Trajectory classification
│   ├── volatility.py               # Volatility (CV)
│   ├── trend.py                   # Trend classification
│   └── registry.py                # Operator registration
│
├── storage/                         # Time series storage backends
│   ├── __init__.py
│   ├── base.py                     # Storage backend protocol
│   ├── memory_store.py             # In-memory (testing, small repos)
│   ├── sqlite_store.py            # SQLite-based (current, improved)
│   ├── index.py                    # Temporal indexes for fast queries
│   └── cache.py                   # LRU cache for expensive queries
│
├── query/                           # Temporal query DSL
│   ├── __init__.py
│   ├── builder.py                  # Query builder
│   ├── filters.py                 # Time range, entity filters
│   ├── aggregations.py            # Time series aggregations
│   └── executor.py               # Query executor
│
├── pipelines/                       # Processing pipelines
│   ├── __init__.py
│   ├── incremental.py             # Incremental update pipeline
│   ├── full_rebuild.py            # Full rebuild pipeline
│   └── scheduler.py               # Parallel task scheduling
│
├── utils/                           # Utilities
│   ├── __init__.py
│   ├── math.py                    # Statistical functions
│   ├── git.py                     # Git subprocess wrappers
│   └── config.py                  # Configuration management
│
└── legacy/                          # Backward compatibility layer
    ├── __init__.py
    ├── git_extractor.py           # Old GitExtractor (deprecated)
    ├── churn.py                   # Old build_churn_series (deprecated)
    ├── cochange.py                # Old build_cochange_matrix (deprecated)
    └── adapter.py                 # Convert old → new API
```

**Estimated Line Count:** ~3,000-4,000 lines (vs. current ~1,450)

### 3.3 Core Abstractions

#### 3.3.1 Entity Identity

```python
from dataclasses import dataclass
from typing import Optional
from enum import Enum

class EntityType(Enum):
    """Types of entities tracked in temporal system."""
    CODEBASE = "codebase"
    FILE = "file"
    LINE = "line"
    COMMIT = "commit"
    AUTHOR = "author"
    MODULE = "module"

@dataclass(frozen=True)
class CanonicalId:
    """Canonical identity for an entity.
    
    Tracks an entity across renames, moves, and other transformations.
    """
    type: EntityType
    key: str  # Stable identifier (commit SHA, author email, etc.)
    aliases: tuple[str, ...] = ()  # Alternative identifiers (file paths, etc.)

@dataclass
class EntityLineage:
    """Lineage of an entity over time.
    
    Tracks how an entity's identity changes (e.g., file renames).
    """
    canonical_id: CanonicalId
    timeline: list[tuple[int, str]]  # [(timestamp, alias), ...]
    created_at: int
    deleted_at: Optional[int] = None

class IdentityResolver:
    """Resolves entity identities across time.
    
    Given an identifier at a point in time, returns the canonical identity.
    """
    def resolve(self, entity_type: EntityType, identifier: str, at_timestamp: int) -> CanonicalId:
        """Resolve identifier to canonical identity at given timestamp."""
        ...
    
    def get_lineage(self, canonical_id: CanonicalId) -> EntityLineage:
        """Get full lineage of an entity."""
        ...
    
    def track_rename(self, old_path: str, new_path: str, commit_sha: str, timestamp: int) -> None:
        """Register a rename event."""
        ...
```

#### 3.3.2 Temporal Events

```python
from abc import ABC, abstractmethod
from typing import Protocol

@dataclass
class GitEvent:
    """Base class for all git events."""
    commit_sha: str
    timestamp: int
    author: str
    subject: str

@dataclass
class CommitEvent(GitEvent):
    """A commit event."""
    # Extracted from git log
    parent_shas: tuple[str, ...]
    is_merge: bool

@dataclass
class FileChangeEvent(GitEvent):
    """A file-level change event."""
    file_path: str
    old_path: Optional[str] = None  # For renames
    change_type: str  # 'A' (add), 'M' (modify), 'D' (delete), 'R' (rename)
    lines_added: int = 0
    lines_deleted: int = 0

@dataclass
class LineChangeEvent(GitEvent):
    """A line-level change event."""
    file_path: str
    line_number: int
    old_content: Optional[str]
    new_content: Optional[str]
    change_type: str  # 'ADD', 'DELETE', 'MODIFY'
```

#### 3.3.3 Event Stream Protocol

```python
class EventStream(Protocol):
    """Protocol for git event streams.
    
    Provides iterable access to git events with filtering capabilities.
    """
    
    def commits(self, since: Optional[int] = None, until: Optional[int] = None) -> Iterable[CommitEvent]:
        """Get commit events in time range."""
        ...
    
    def file_changes(self, since: Optional[int] = None, until: Optional[int] = None) -> Iterable[FileChangeEvent]:
        """Get file change events in time range."""
        ...
    
    def line_changes(self, file_path: str, since: Optional[int] = None, until: Optional[int] = None) -> Iterable[LineChangeEvent]:
        """Get line change events for a specific file."""
        ...
    
    def stream_commits(self, batch_size: int = 1000) -> Iterator[list[CommitEvent]]:
        """Stream commits in batches to avoid memory overload."""
        ...
```

#### 3.3.4 Temporal Analyzer Protocol

```python
from typing import Any

class TemporalAnalyzer(Protocol):
    """Protocol for temporal analysis plugins.
    
    Analyzers process events and produce temporal signals.
    """
    
    name: str
    requires: set[str]  # Required event types
    provides: set[str]  # Signals produced
    
    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize analyzer with optional configuration."""
        ...
    
    def process_event(self, event: GitEvent, storage: TimeSeriesStore) -> None:
        """Process a single event incrementally."""
        ...
    
    def finalize(self, storage: TimeSeriesStore) -> dict[str, Any]:
        """Finalize analysis after all events processed.
        
        Returns computed signals ready for storage.
        """
        ...
```

#### 3.3.5 Temporal Operator Protocol

```python
from typing import TypeVar, Callable

T = TypeVar('T')

class TemporalOperator(Protocol[T]):
    """Protocol for temporal operators.
    
    Operators transform time series into derived signals.
    """
    
    name: str
    
    def __call__(self, series: list[T]) -> Any:
        """Apply operator to time series."""
        ...

# Operator factory for type-safe operator composition
def operator(name: str) -> Callable[[type[T]], Type[TemporalOperator[T]]]:
    """Decorator to register temporal operators."""
    ...

@operator('delta')
class DeltaOperator(TemporalOperator[float]):
    """Δ(S) = S(t) - S(t-1)"""
    
    name = 'delta'
    
    def __call__(self, series: list[float]) -> list[float]:
        if len(series) < 2:
            return []
        return [series[i] - series[i-1] for i in range(1, len(series))]

@operator('velocity')
class VelocityOperator(TemporalOperator[float]):
    """v(S) = slope of linear regression of S(t)"""
    
    name = 'velocity'
    
    def __call__(self, series: list[float]) -> float:
        if len(series) < 2:
            return 0.0
        # Linear regression via OLS
        n = len(series)
        x = list(range(n))
        x_mean = (n - 1) / 2.0
        y_mean = sum(series) / n
        
        numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, series))
        denominator = sum((xi - x_mean) ** 2 for xi in x)
        
        return numerator / denominator if denominator != 0 else 0.0

@operator('trajectory')
class TrajectoryOperator(TemporalOperator[float]):
    """Classify trajectory based on velocity and volatility."""
    
    name = 'trajectory'
    
    def __call__(self, series: list[float]) -> str:
        total = sum(series)
        if total <= 1:
            return "DORMANT"
        
        velocity = VelocityOperator()(series)
        cv = VolatilityOperator()(series)
        
        slope_threshold = 0.1
        cv_threshold = 0.5
        
        if velocity < -slope_threshold and cv < cv_threshold:
            return "STABILIZING"
        elif velocity > slope_threshold and cv > cv_threshold:
            return "SPIKING"
        elif cv > cv_threshold:
            return "CHURNING"
        else:
            return "STABLE"

@operator('volatility')
class VolatilityOperator(TemporalOperator[float]):
    """volatility(S) = std(S) / mean(S) (coefficient of variation)"""
    
    name = 'volatility'
    
    def __call__(self, series: list[float]) -> float:
        n = len(series)
        if n < 2:
            return 0.0
        
        total = sum(series)
        if total == 0:
            return 0.0
        
        mean = total / n
        if mean == 0:
            return 0.0
        
        variance = sum((v - mean) ** 2 for v in series) / n
        std = variance ** 0.5
        return std / mean
```

#### 3.3.6 Time Series Storage Protocol

```python
@dataclass
class TimeSeriesPoint:
    """A single point in a time series."""
    timestamp: int
    value: float

@dataclass
class TimeSeries:
    """A complete time series."""
    entity_id: CanonicalId
    signal_name: str
    points: list[TimeSeriesPoint]
    metadata: dict[str, Any] = field(default_factory=dict)

class TimeSeriesStore(Protocol):
    """Protocol for time series storage backends.
    
    Provides efficient storage and querying of temporal signals.
    """
    
    def write_point(self, entity_id: CanonicalId, signal_name: str, timestamp: int, value: float) -> None:
        """Write a single data point."""
        ...
    
    def write_series(self, series: TimeSeries) -> None:
        """Write an entire time series (bulk write)."""
        ...
    
    def read_series(self, entity_id: CanonicalId, signal_name: str, 
                   since: Optional[int] = None, until: Optional[int] = None) -> TimeSeries:
        """Read a time series, optionally filtered by time range."""
        ...
    
    def read_latest(self, entity_id: CanonicalId, signal_name: str) -> Optional[float]:
        """Get the most recent value for a signal."""
        ...
    
    def query_range(self, entity_ids: set[CanonicalId], signal_names: set[str],
                   since: int, until: int) -> dict[CanonicalId, dict[str, TimeSeries]]:
        """Query multiple signals for multiple entities in time range."""
        ...
    
    def get_entities_in_range(self, since: int, until: int) -> set[CanonicalId]:
        """Get all entities that have data in time range."""
        ...
    
    def apply_operator(self, entity_id: CanonicalId, signal_name: str, 
                     operator: TemporalOperator) -> Any:
        """Apply a temporal operator to a time series."""
        series = self.read_series(entity_id, signal_name)
        values = [p.value for p in series.points]
        return operator(values)
```

### 3.4 Data Flow Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     Pipeline Orchestrator                       │
│  (schedules tasks, manages incremental updates, caching)        │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Event Stream Layer                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────┐ │
│  │ CommitExtractor  │  │FileChangeExtr.   │  │LineChangeE.│ │
│  └────────┬─────────┘  └────────┬─────────┘  └─────┬──────┘ │
│           │                     │                     │          │
│           └─────────────────────┴─────────────────────┘          │
│                              │                                │
│                              ▼                                │
│                    ┌─────────────────┐                       │
│                    │  EventStream    │                       │
│                    │  (unified API)  │                       │
│                    └────────┬────────┘                       │
└───────────────────────────────┼───────────────────────────────────┘
                                │
                                │ EventStream events
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                   Analysis Layer (Pluggable)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ ChurnAnalyzer│  │CoChangeAna.  │  │AuthorAnalyzer│          │
│  │             │  │              │  │             │          │
│  │ process()   │  │ process()    │  │ process()   │          │
│  │ finalize()  │  │ finalize()   │  │ finalize()  │          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
│         │                │                │                     │
│         │                │                │                     │
│         └────────────────┴────────────────┘                     │
                          │                                       │
                          │ TimeSeries data                        │
                          ▼                                       │
              ┌───────────────────────┐                           │
              │  TimeSeriesStore      │                           │
              │  ──────────────────── │                           │
              │  • write_point()      │                           │
              │  • write_series()    │                           │
              │  • read_series()     │                           │
              │  • apply_operator()   │                           │
              └───────────┬───────────┘                           │
└────────────────────────────┼───────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                   Query Layer                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ QueryBuilder│  │  Filters    │  │Aggregations │          │
│  │             │  │             │  │             │          │
│  │ .select()   │  │ .time_range()│  │ .rollup()   │          │
│  │ .where()    │  │ .entity()    │  │ .group_by() │          │
│  │ .execute()  │  │             │  │             │          │
│  └──────┬──────┘  └─────────────┘  └─────────────┘          │
│         │                                                       │
│         │ Query results                                          │
│         ▼                                                       │
└──────────────────────────────────────────────────────────────────┘
```

### 3.5 Incremental Processing Pipeline

```python
from typing import Iterable

class IncrementalPipeline:
    """Orchestrates incremental temporal analysis.
    
    On first run: processes all commits from git history.
    On subsequent runs: only processes new commits since last run.
    """
    
    def __init__(self, repo_path: str, store: TimeSeriesStore, 
                 analyzers: list[TemporalAnalyzer]):
        self.repo_path = repo_path
        self.store = store
        self.analyzers = analyzers
        self.state_store = SQLiteStateStore(repo_path)  # Tracks last processed SHA
    
    def run(self, force_full_rebuild: bool = False) -> AnalysisResult:
        """Run the pipeline."""
        
        # 1. Determine incremental range
        if force_full_rebuild:
            since_sha = None
        else:
            since_sha = self.state_store.get_last_processed_sha()
        
        # 2. Stream commits (memory-efficient)
        event_stream = GitEventStream(self.repo_path)
        for commit_batch in event_stream.stream_commits(batch_size=1000):
            
            # 3. Process each commit through all analyzers (incremental)
            for commit in commit_batch:
                for analyzer in self.analyzers:
                    if self._can_process_event(analyzer, commit):
                        analyzer.process_event(commit, self.store)
            
            # 4. Periodically checkpoint state (every N commits)
            if commit_batch[-1].commit_sha % 1000 == 0:
                self.state_store.checkpoint(commit_batch[-1])
        
        # 5. Finalize all analyzers (compute derived signals)
        results = {}
        for analyzer in self.analyzers:
            results[analyzer.name] = analyzer.finalize(self.store)
        
        # 6. Update checkpoint
        last_commit = event_stream.get_latest_commit()
        self.state_store.set_last_processed_sha(last_commit.commit_sha)
        
        return AnalysisResult(results)
    
    def _can_process_event(self, analyzer: TemporalAnalyzer, event: GitEvent) -> bool:
        """Check if analyzer can handle this event type."""
        return type(event).__name__ in analyzer.requires
```

### 3.6 Example: Line-Level Churn Analyzer

```python
class LineChurnAnalyzer(TemporalAnalyzer):
    """Computes line-level churn time series.
    
    Tracks how often each line in a file changes.
    Identifies "hot spots" - lines that change frequently.
    """
    
    name = "line_churn"
    requires = {"LineChangeEvent"}
    provides = {"line_churn_series", "hotspot_lines"}
    
    def __init__(self, config: dict[str, Any] | None = None):
        self.window_size = config.get("window_size", 7 * 86400) if config else 7 * 86400  # 1 week
        self.hotspot_threshold = config.get("hotspot_threshold", 5) if config else 5
        
        # Accumulators (in-memory for current batch)
        self._line_change_counts: dict[tuple[str, int], int] = {}
        self._line_windows: dict[str, list[int]] = {}
    
    def process_event(self, event: LineChangeEvent, storage: TimeSeriesStore) -> None:
        """Process a line change event."""
        key = (event.file_path, event.line_number)
        self._line_change_counts[key] = self._line_change_counts.get(key, 0) + 1
    
    def finalize(self, storage: TimeSeriesStore) -> dict[str, Any]:
        """Finalize and write line-level churn series."""
        
        # Build time series for each line
        line_series = {}
        hotspots = []
        
        for (file_path, line_num), change_count in self._line_change_counts.items():
            entity_id = CanonicalId(EntityType.LINE, f"{file_path}:{line_num}")
            
            # Write raw change count as a signal
            storage.write_point(entity_id, "line_change_count", 
                            event.timestamp, float(change_count))
            
            # Check if this is a hotspot
            if change_count >= self.hotspot_threshold:
                hotspots.append({
                    "file_path": file_path,
                    "line_number": line_num,
                    "change_count": change_count,
                })
            
            # Aggregate to file-level line churn
            if file_path not in line_series:
                line_series[file_path] = 0
            line_series[file_path] += change_count
        
        return {
            "line_churn_series": line_series,
            "hotspot_lines": hotspots,
        }
```

### 3.7 Example: Fix Traceability Analyzer

```python
class FixTraceabilityAnalyzer(TemporalAnalyzer):
    """Tracks fix commits and links them to code changes.
    
    Builds:
    1. fix_ratio (current implementation)
    2. fix_lines - which lines were changed in fix commits
    3. bug_introducing_commits - blame to find commits that introduced bugs
    """
    
    name = "fix_traceability"
    requires = {"FileChangeEvent", "CommitEvent"}
    provides = {"fix_ratio", "fix_lines", "bug_introducing_commits"}
    
    FIX_KEYWORDS = frozenset({"fix", "bug", "patch", "hotfix", "bugfix", "repair", "issue"})
    
    def __init__(self, config: dict[str, Any] | None = None):
        self._fix_commits: set[str] = set()
        self._file_fix_counts: dict[str, int] = {}
        self._file_fix_lines: dict[str, list[tuple[int, str]]] = {}  # {file: [(line, commit_sha), ...]}
        self._total_commits: dict[str, int] = {}
    
    def process_event(self, event: GitEvent, storage: TimeSeriesStore) -> None:
        """Process git events."""
        
        if isinstance(event, CommitEvent):
            # Track total commits per file
            is_fix = any(kw in event.subject.lower() for kw in self.FIX_KEYWORDS)
            
            if is_fix:
                self._fix_commits.add(event.commit_sha)
            
        elif isinstance(event, FileChangeEvent):
            # Track commits per file
            if event.file_path not in self._total_commits:
                self._total_commits[event.file_path] = 0
            self._total_commits[event.file_path] += 1
            
            # Track fix commits
            if event.commit_sha in self._fix_commits:
                if event.file_path not in self._file_fix_counts:
                    self._file_fix_counts[event.file_path] = 0
                self._file_fix_counts[event.file_path] += 1
    
    def finalize(self, storage: TimeSeriesStore) -> dict[str, Any]:
        """Finalize fix traceability signals."""
        
        fix_ratios = {}
        for file_path, total in self._total_commits.items():
            fix_count = self._file_fix_counts.get(file_path, 0)
            fix_ratios[file_path] = fix_count / total if total > 0 else 0.0
            
            # Write to storage
            entity_id = CanonicalId(EntityType.FILE, file_path)
            storage.write_point(entity_id, "fix_ratio", event.timestamp, fix_ratios[file_path])
        
        return {
            "fix_ratio": fix_ratios,
            "fix_lines": self._file_fix_lines,
        }
```

### 3.8 Query DSL Example

```python
from temporal.query import QueryBuilder, TimeRange, EntityFilter

# Example queries

# 1. Get churn trend for a file in the last 30 days
query = (
    QueryBuilder()
    .select("total_changes", "churn_trajectory")
    .from_entity(EntityType.FILE, "src/auth/login.py")
    .where(TimeRange(last_days=30))
    .execute(store)
)

# Result:
# {
#     "total_changes": [3, 0, 5, 2, ...],  # Weekly values
#     "churn_trajectory": "SPIKING"
# }

# 2. Find all files with churn_trajectory = CHURNING in last 90 days
query = (
    QueryBuilder()
    .select("file_path", "churn_trajectory", "total_changes")
    .from_entities(EntityType.FILE)
    .where(TimeRange(last_days=90))
    .where(EntityFilter("churn_trajectory", equals="CHURNING"))
    .execute(store)
)

# 3. Apply temporal operators
query = (
    QueryBuilder()
    .select("pagerank")
    .from_entity(EntityType.FILE, "src/auth/login.py")
    .apply_operator("velocity")  # Get velocity of pagerank
    .apply_operator("trend")     # Get trend classification
    .execute(store)
)

# Result: {"velocity": 0.02, "trend": "WORSENING"}

# 4. Compare two historical snapshots
query = (
    QueryBuilder()
    .compare_snapshots(
        base_id=123,       # Snapshot from 1 week ago
        target_id=130,     # Latest snapshot
    )
    .show_delta("pagerank", "cognitive_load")
    .execute(store)
)
```

---

## Phase 4: Migration Strategy

### 4.1 Phased Migration Approach

```
Phase 1: Foundation (Week 1-2)
├── Implement core abstractions (protocols, models)
├── Implement streaming git extractor (memory-efficient)
├── Implement identity resolver (rename tracking)
└── Unit tests for core components

Phase 2: Analysis Layer (Week 3-4)
├── Implement TemporalAnalyzer protocol
├── Migrate churn analyzer to new architecture
├── Migrate cochange analyzer to new architecture
├── Migrate author analyzer to new architecture
└── Integration tests

Phase 3: Storage Layer (Week 5-6)
├── Implement TimeSeriesStore protocol
├── Implement SQLite backend (improved schema)
├── Implement temporal indexes
├── Migrate data from legacy format
└── Performance tests

Phase 4: Query Layer (Week 7)
├── Implement QueryBuilder DSL
├── Implement filters and aggregations
├── Implement operator application
└── Query benchmarks

Phase 5: Advanced Features (Week 8-10)
├── Implement line-level churn analyzer
├── Implement fix traceability analyzer
├── Implement graph evolution analyzer
└── End-to-end tests

Phase 6: Integration (Week 11-12)
├── Update TemporalAnalyzer to use new pipeline
├── Update FactStore integration
├── Update CLI commands (--history, --diff)
├── Update web UI for temporal queries
└── Documentation

Phase 7: Cleanup (Week 13-14)
├── Deprecate legacy modules (mark as @deprecated)
├── Add migration guide for users
├── Update tests to use new API
└── Remove legacy code in next major version
```

### 4.2 Backward Compatibility

**Legacy API Support:**

```python
# Legacy API (deprecated but functional)
from shannon_insight.temporal.legacy import GitExtractor, build_churn_series, build_cochange_matrix

# New API (recommended)
from shannon_insight.temporal import (
    GitEventStream,
    IncrementalPipeline,
    ChurnAnalyzer,
    CoChangeAnalyzer,
    TimeSeriesStore,
)

# Adapter for migration
from shannon_insight.temporal.legacy.adapter import LegacyAdapter

# Convert legacy results to new format
adapter = LegacyAdapter()
new_store = adapter.migrate_legacy_churn(legacy_churn_series)
```

**Data Migration:**

```python
# Migrate existing cache
class CacheMigrator:
    """Migrate from legacy CommitCache to new storage."""
    
    def migrate(self, legacy_cache: CommitCache, new_store: TimeSeriesStore) -> None:
        """Migrate cached commits to new format."""
        commits = legacy_cache.get_all_commits()
        
        for commit in commits:
            # Write as CommitEvent
            event = CommitEvent(
                commit_sha=commit.hash,
                timestamp=commit.timestamp,
                author=commit.author,
                subject=commit.subject,
                parent_shas=(),  # Not tracked in legacy
                is_merge=False,
            )
            
            entity_id = CanonicalId(EntityType.COMMIT, commit.hash)
            new_store.write_point(entity_id, "timestamp", commit.timestamp, float(commit.timestamp))
```

### 4.3 Breaking Changes

**Breaking changes to be communicated:**

1. **GitExtractor API**: 
   - Old: `GitExtractor(repo_path).extract()` returns `GitHistory`
   - New: `GitEventStream(repo_path).commits()` returns `Iterable[CommitEvent]`
   - Migration: Use `LegacyAdapter` or migrate to new streaming API

2. **Churn Analysis Result Format**:
   - Old: `Dict[str, ChurnSeries]`
   - New: Query `TimeSeriesStore` for `churn_series` signal
   - Migration: Use `adapter.migrate_churn_series()`

3. **CoChange Matrix**:
   - Old: `CoChangeMatrix` with pre-computed pairs
   - New: Query `TimeSeriesStore` for `cochange` signal
   - Migration: Use `adapter.migrate_cochange_matrix()`

**Semver bump:** Major version bump (2.0 → 3.0) for breaking changes.

---

## Extension Points

### 1. Adding a New Temporal Analyzer

To add a new analyzer (e.g., for detecting refactoring patterns):

```python
# temporal/analysis/refactoring_analyzer.py

from .base import TemporalAnalyzer
from ..core.models import GitEvent, CanonicalId, EntityType
from ..storage.base import TimeSeriesStore
from typing import Any

class RefactoringAnalyzer(TemporalAnalyzer):
    """Detects refactoring patterns from commit messages and code changes."""
    
    name = "refactoring"
    requires = {"CommitEvent", "FileChangeEvent"}
    provides = {"refactor_ratio", "refactor_types"}
    
    REFACTOR_KEYWORDS = frozenset({"refactor", "cleanup", "reorganize", "restructure", "rename"})
    REFACTOR_TYPES = {
        "extract": ["extract method", "extract class"],
        "rename": ["rename", "mv"],
        "inline": ["inline method"],
    }
    
    def __init__(self, config: dict[str, Any] | None = None):
        self._refactor_commits: set[str] = set()
        self._file_refactor_counts: dict[str, dict[str, int]] = {}
        self._total_commits: dict[str, int] = {}
    
    def process_event(self, event: GitEvent, storage: TimeSeriesStore) -> None:
        """Process events to detect refactorings."""
        
        if isinstance(event, CommitEvent):
            subject_lower = event.subject.lower()
            is_refactor = any(kw in subject_lower for kw in self.REFACTOR_KEYWORDS)
            
            if is_refactor:
                self._refactor_commits.add(event.commit_sha)
        
        elif isinstance(event, FileChangeEvent):
            # Track commits per file
            if event.file_path not in self._total_commits:
                self._total_commits[event.file_path] = 0
            self._total_commits[event.file_path] += 1
            
            # Track refactor commits
            if event.commit_sha in self._refactor_commits:
                # Classify refactor type
                refactor_type = self._classify_refactor_type(event.subject)
                
                if event.file_path not in self._file_refactor_counts:
                    self._file_refactor_counts[event.file_path] = {}
                
                if refactor_type not in self._file_refactor_counts[event.file_path]:
                    self._file_refactor_counts[event.file_path][refactor_type] = 0
                
                self._file_refactor_counts[event.file_path][refactor_type] += 1
    
    def _classify_refactor_type(self, commit_message: str) -> str:
        """Classify the type of refactoring."""
        msg_lower = commit_message.lower()
        
        for refactor_type, keywords in self.REFACTOR_TYPES.items():
            if any(kw in msg_lower for kw in keywords):
                return refactor_type
        
        return "other"
    
    def finalize(self, storage: TimeSeriesStore) -> dict[str, Any]:
        """Finalize and write refactoring signals."""
        
        refactor_ratios = {}
        refactor_types = {}
        
        for file_path, total in self._total_commits.items():
            type_counts = self._file_refactor_counts.get(file_path, {})
            refactor_count = sum(type_counts.values())
            
            refactor_ratios[file_path] = refactor_count / total if total > 0 else 0.0
            refactor_types[file_path] = type_counts
            
            # Write to storage
            entity_id = CanonicalId(EntityType.FILE, file_path)
            storage.write_point(entity_id, "refactor_ratio", event.timestamp, refactor_ratios[file_path])
            
            for refactor_type, count in type_counts.items():
                signal_name = f"refactor_{refactor_type}_count"
                storage.write_point(entity_id, signal_name, event.timestamp, float(count))
        
        return {
            "refactor_ratio": refactor_ratios,
            "refactor_types": refactor_types,
        }

# Register the analyzer
from .registry import register_analyzer

register_analyzer(RefactoringAnalyzer)
```

**Usage:**

```python
# In pipeline
pipeline = IncrementalPipeline(
    repo_path="/path/to/repo",
    store=time_series_store,
    analyzers=[
        ChurnAnalyzer(),
        CoChangeAnalyzer(),
        RefactoringAnalyzer(),  # New analyzer
    ],
)
pipeline.run()
```

### 2. Adding a New Temporal Operator

To add a new operator (e.g., for detecting seasonality):

```python
# temporal/operators/seasonality.py

from .base import TemporalOperator
from ..utils.math import autocorrelation
from typing import Any

@operator('seasonality')
class SeasonalityOperator(TemporalOperator[float]):
    """Detect seasonal patterns in time series.
    
    Returns the lag with highest autocorrelation.
    """
    
    name = 'seasonality'
    
    def __call__(self, series: list[float], max_lag: int = 52) -> dict[str, Any]:
        """
        Detect seasonal patterns using autocorrelation.
        
        Args:
            series: Time series values
            max_lag: Maximum lag to check (e.g., 52 for weekly data over a year)
        
        Returns:
            {
                'seasonal_lag': int,  # The lag with highest autocorrelation
                'seasonality_strength': float,  # Autocorrelation at that lag
                'is_seasonal': bool,  # True if strength > 0.5
            }
        """
        if len(series) < max_lag * 2:
            return {
                'seasonal_lag': 0,
                'seasonality_strength': 0.0,
                'is_seasonal': False,
            }
        
        # Compute autocorrelation for all lags
        autocorrs = []
        for lag in range(1, min(max_lag, len(series) // 2)):
            ac = autocorrelation(series, lag)
            autocorrs.append((lag, ac))
        
        # Find lag with highest autocorrelation
        best_lag, best_ac = max(autocorrs, key=lambda x: x[1])
        
        return {
            'seasonal_lag': best_lag,
            'seasonality_strength': best_ac,
            'is_seasonal': best_ac > 0.5,
        }

# Register the operator
from .registry import register_operator

register_operator(SeasonalityOperator)
```

**Usage:**

```python
# Apply operator to a time series
result = store.apply_operator(
    entity_id=CanonicalId(EntityType.FILE, "src/auth/login.py"),
    signal_name="total_changes",
    operator=SeasonalityOperator(),
)

# Or use QueryBuilder
query = (
    QueryBuilder()
    .select("total_changes")
    .from_entity(EntityType.FILE, "src/auth/login.py")
    .apply_operator("seasonality", max_lag=52)
    .execute(store)
)

# Result:
# {
#     'seasonal_lag': 4,  # Weekly pattern (4-week lag)
#     'seasonality_strength': 0.72,
#     'is_seasonal': True
# }
```

### 3. Adding a New Storage Backend

To add support for TimescaleDB (for large-scale deployments):

```python
# temporal/storage/timescale_store.py

import psycopg2
from .base import TimeSeriesStore, TimeSeries, TimeSeriesPoint
from ..core.models import CanonicalId
from typing import Optional

class TimescaleDBStore(TimeSeriesStore):
    """TimescaleDB backend for time series storage.
    
    Efficiently handles large datasets (millions of points).
    """
    
    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self._init_schema()
    
    def _init_schema(self) -> None:
        """Initialize TimescaleDB schema."""
        with self.conn.cursor() as cur:
            # Create hypertable (time-optimized table)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS time_series (
                    entity_type TEXT NOT NULL,
                    entity_key TEXT NOT NULL,
                    signal_name TEXT NOT NULL,
                    timestamp BIGINT NOT NULL,
                    value DOUBLE PRECISION NOT NULL,
                    metadata JSONB,
                    PRIMARY KEY (entity_type, entity_key, signal_name, timestamp)
                );
            """)
            
            # Convert to hypertable for time optimization
            cur.execute("""
                SELECT create_hypertable('time_series', 'timestamp', 
                                       if_not_exists => TRUE);
            """)
            
            # Create indexes for common queries
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_time_series_entity 
                ON time_series (entity_type, entity_key, signal_name);
            """)
            
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_time_series_time 
                ON time_series (timestamp DESC);
            """)
        
        self.conn.commit()
    
    def write_point(self, entity_id: CanonicalId, signal_name: str, 
                   timestamp: int, value: float) -> None:
        """Write a single data point."""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO time_series (entity_type, entity_key, signal_name, 
                                       timestamp, value)
                VALUES (%s, %s, %s, %s, %s)
            """, (entity_id.type.value, entity_id.key, signal_name, timestamp, value))
        self.conn.commit()
    
    def write_series(self, series: TimeSeries) -> None:
        """Bulk write an entire time series."""
        with self.conn.cursor() as cur:
            cur.executemany("""
                INSERT INTO time_series (entity_type, entity_key, signal_name, 
                                       timestamp, value, metadata)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [
                (series.entity_id.type.value, series.entity_id.key, 
                 series.signal_name, point.timestamp, point.value, 
                 series.metadata)
                for point in series.points
            ])
        self.conn.commit()
    
    def read_series(self, entity_id: CanonicalId, signal_name: str,
                   since: Optional[int] = None, until: Optional[int] = None) -> TimeSeries:
        """Read a time series."""
        with self.conn.cursor() as cur:
            query = """
                SELECT timestamp, value
                FROM time_series
                WHERE entity_type = %s AND entity_key = %s AND signal_name = %s
            """
            params = [entity_id.type.value, entity_id.key, signal_name]
            
            if since is not None:
                query += " AND timestamp >= %s"
                params.append(since)
            
            if until is not None:
                query += " AND timestamp <= %s"
                params.append(until)
            
            query += " ORDER BY timestamp ASC"
            
            cur.execute(query, params)
            rows = cur.fetchall()
        
        points = [TimeSeriesPoint(timestamp=row[0], value=row[1]) for row in rows]
        
        return TimeSeries(
            entity_id=entity_id,
            signal_name=signal_name,
            points=points,
            metadata={},
        )
```

### 4. Line-Level Churn Analysis

Complete implementation for tracking line-level churn:

```python
# temporal/analysis/line_churn_analyzer.py

class LineChurnAnalyzer(TemporalAnalyzer):
    """Computes line-level churn to identify hot spots.
    
    Hot spots: Lines that change frequently (≥ N changes in time window).
    These are often indicators of:
    - Complex logic (hard to get right)
    - Unstable requirements (changing business rules)
    - Poor design (tight coupling)
    """
    
    name = "line_churn"
    requires = {"LineChangeEvent"}
    provides = {"line_churn_series", "hotspot_lines", "churn_heatmap"}
    
    def __init__(self, config: dict[str, Any] | None = None):
        # Configuration
        self.hotspot_threshold = config.get("hotspot_threshold", 5) if config else 5
        self.window_days = config.get("window_days", 30) if config else 30
        
        # State
        self._line_changes: dict[str, dict[int, list[int]]] = {}  # {file: {line: [timestamps]}}
        self._window_start: Optional[int] = None
    
    def process_event(self, event: LineChangeEvent, storage: TimeSeriesStore) -> None:
        """Process a line change event."""
        
        # Initialize line tracking for file
        if event.file_path not in self._line_changes:
            self._line_changes[event.file_path] = {}
        
        # Add line change with timestamp
        if event.line_number not in self._line_changes[event.file_path]:
            self._line_changes[event.file_path][event.line_number] = []
        
        self._line_changes[event.file_path][event.line_number].append(event.timestamp)
        
        # Write to storage (raw line change count)
        entity_id = CanonicalId(EntityType.LINE, f"{event.file_path}:{event.line_number}")
        current_count = len(self._line_changes[event.file_path][event.line_number])
        storage.write_point(entity_id, "line_change_count", event.timestamp, float(current_count))
    
    def finalize(self, storage: TimeSeriesStore) -> dict[str, Any]:
        """Finalize and compute hot spots."""
        
        hotspots = []
        heatmap = {}  # {file: [(line_num, intensity), ...]}
        
        for file_path, lines in self._line_changes.items():
            file_hotspots = []
            file_heatmap = []
            
            for line_num, timestamps in lines.items():
                # Count changes in time window
                if self._window_start:
                    window_changes = [ts for ts in timestamps if ts >= self._window_start]
                else:
                    window_changes = timestamps
                
                change_count = len(window_changes)
                
                # Check if hotspot
                if change_count >= self.hotspot_threshold:
                    hotspots.append({
                        "file_path": file_path,
                        "line_number": line_num,
                        "change_count": change_count,
                        "timestamps": timestamps,
                    })
                    file_hotspots.append((line_num, change_count))
                
                # Add to heatmap
                file_heatmap.append((line_num, change_count))
            
            # Sort heatmap by line number
            file_heatmap.sort(key=lambda x: x[0])
            heatmap[file_path] = file_heatmap
        
        # Sort hotspots by change count (descending)
        hotspots.sort(key=lambda x: x["change_count"], reverse=True)
        
        return {
            "line_churn_series": self._line_changes,
            "hotspot_lines": hotspots,
            "churn_heatmap": heatmap,
        }
```

**Integration with web UI:**

```javascript
// Frontend: Display churn heatmap

async function fetchChurnHeatmap(filePath) {
  const response = await fetch(`/api/temporal/line-churn?file=${encodeURIComponent(filePath)}`);
  return response.json();
}

// Render heatmap
function renderHeatmap(filePath, heatmap) {
  const canvas = document.getElementById('heatmap-canvas');
  const ctx = canvas.getContext('2d');
  
  const lineCount = heatmap.length;
  const maxChanges = Math.max(...heatmap.map(h => h[1]));
  
  heatmap.forEach(([lineNum, changes]) => {
    const intensity = changes / maxChanges;  // 0 to 1
    const y = (lineNum - 1) * lineHeight;
    
    // Color: green (low) → yellow (medium) → red (high)
    const color = interpolateColor('green', 'red', intensity);
    
    ctx.fillStyle = color;
    ctx.fillRect(0, y, canvas.width, lineHeight);
    
    // Highlight hotspots
    if (changes >= 5) {
      ctx.strokeStyle = 'black';
      ctx.lineWidth = 2;
      ctx.strokeRect(0, y, canvas.width, lineHeight);
    }
  });
}
```

### 5. Graph Evolution Tracking

```python
# temporal/analysis/graph_evolution_analyzer.py

class GraphEvolutionAnalyzer(TemporalAnalyzer):
    """Tracks how the dependency graph changes over time.
    
    Detects:
    - New dependencies (edge additions)
    - Removed dependencies (edge deletions)
    - Architectural drift (accumulated changes)
    - Cyclical dependencies appearing/disappearing
    """
    
    name = "graph_evolution"
    requires = {"FileChangeEvent"}
    provides = {"graph_evolution", "edge_timeline", "architectural_drift"}
    
    def __init__(self, config: dict[str, Any] | None = None):
        self._edges_at_commit: dict[str, set[tuple[str, str]]] = {}  # {sha: {(from, to), ...}}
        self._edge_timeline: list[tuple[int, str, str, str]] = []  # [(ts, action, from, to), ...]
        self._current_graph: DependencyGraph = DependencyGraph()
    
    def process_event(self, event: FileChangeEvent, storage: TimeSeriesStore) -> None:
        """Process file changes to detect graph evolution."""
        
        # Parse file to extract imports
        file_path = event.file_path
        try:
            imports = parse_imports(file_path)  # Uses tree-sitter
        except Exception:
            return
        
        # Detect edge changes
        old_imports = self._current_graph.adjacency.get(file_path, set())
        new_imports = set(imports)
        
        added = new_imports - old_imports
        removed = old_imports - new_imports
        
        # Record edge additions
        for target in added:
            self._edge_timeline.append((event.timestamp, "ADD", file_path, target))
        
        # Record edge removals
        for target in removed:
            self._edge_timeline.append((event.timestamp, "REMOVE", file_path, target))
        
        # Update current graph
        self._current_graph.adjacency[file_path] = new_imports
        for target in new_imports:
            if target not in self._current_graph.reverse:
                self._current_graph.reverse[target] = set()
            self._current_graph.reverse[target].add(file_path)
        
        # Snapshot graph state at this commit
        self._edges_at_commit[event.commit_sha] = set(
            (src, tgt) for src, tgts in self._current_graph.adjacency.items()
            for tgt in tgts
        )
    
    def finalize(self, storage: TimeSeriesStore) -> dict[str, Any]:
        """Finalize and compute graph evolution metrics."""
        
        # Compute architectural drift (sum of absolute changes)
        edge_additions = sum(1 for _, action, _, _ in self._edge_timeline if action == "ADD")
        edge_removals = sum(1 for _, action, _, _ in self._edge_timeline if action == "REMOVE")
        drift = edge_additions + edge_removals
        
        # Compute edge volatility (rate of change)
        if len(self._edge_timeline) > 1:
            time_span = self._edge_timeline[-1][0] - self._edge_timeline[0][0]
            volatility = len(self._edge_timeline) / time_span
        else:
            volatility = 0.0
        
        return {
            "graph_evolution": {
                "edge_timeline": self._edge_timeline,
                "edge_additions": edge_additions,
                "edge_removals": edge_removals,
            },
            "edge_timeline": self._edge_timeline,
            "architectural_drift": {
                "total_changes": drift,
                "volatility": volatility,
            },
        }
```

---

## Key Design Decisions

### 1. Event-Driven Architecture

**Decision:** Extract git events at multiple granularities (commit, file, line) and process them through a pluggable analyzer pipeline.

**Rationale:**
- **Flexibility:** Different analyzers need different event granularities. File churn needs file events, line churn needs line events, graph evolution needs both.
- **Efficiency:** Extract once, consume multiple times. Avoid re-parsing git history for each analyzer.
- **Extensibility:** New analyzers can be added without modifying extraction logic.
- **Testability:** Each analyzer can be tested in isolation with mock events.

**Trade-offs:**
- **Complexity:** More moving parts than monolithic approach.
- **Memory:** Need to store events (or stream them) until all analyzers process them.
- **Rejected alternative:** Monolithic TemporalAnalyzer that computes everything at once. Too hard to extend and test.

### 2. Pluggable Analyzer Framework

**Decision:** Define `TemporalAnalyzer` protocol with `process_event()` and `finalize()` methods. Register analyzers in a registry. Pipeline orchestrates execution.

**Rationale:**
- **Open/Closed Principle:** Open for extension (new analyzers), closed for modification (no changes to pipeline).
- **Separation of Concerns:** Each analyzer owns its logic and state.
- **Parallel Processing:** Independent analyzers can run in parallel on the same event stream.
- **Configuration:** Each analyzer can be customized via config dict.

**Trade-offs:**
- **Coordination Overhead:** Need to manage state across analyzers.
- **Rejected alternative:** Single analyzer with conditional branches. Would become unmaintainable.

### 3. Entity Identity Management

**Decision:** Introduce `CanonicalId` and `IdentityResolver` to track entities across renames/moves.

**Rationale:**
- **Correctness:** A file renamed from `foo.py` to `bar.py` should have continuous history.
- **Lineage Tracking:** Can trace full lifecycle of an entity (created → renamed → modified → deleted).
- **Historical Reconstruction:** When reconstructing state at past commit, need to resolve what a path referred to at that time.
- **Performance:** Identity resolution happens once, cached for reuse.

**Trade-offs:**
- **Complexity:** Need to maintain lineage data and resolve queries.
- **Storage:** Additional storage for lineage metadata.
- **Rejected alternative:** Track entities by current path only. Breaks on renames.

### 4. Time Series Storage Abstraction

**Decision:** Define `TimeSeriesStore` protocol with multiple backends (memory, SQLite, TimescaleDB).

**Rationale:**
- **Scalability:** Different use cases need different storage. Small repos → in-memory. Large repos → TimescaleDB.
- **Performance:** Optimized backends for temporal queries (indexes, compression).
- **Portability:** Easy to swap backends without changing analysis code.
- **Testing:** In-memory backend for fast unit tests.

**Trade-offs:**
- **Least Common Denominator:** Protocol must support all backends, limiting advanced features.
- **Implementation Overhead:** Multiple backends to maintain.
- **Rejected alternative:** Direct SQLite access. Not scalable for large datasets.

### 5. Streaming Git Log Processing

**Decision:** Process git log in batches (e.g., 1000 commits at a time) instead of loading entire history into memory.

**Rationale:**
- **Memory Efficiency:** Can process repos with 100k+ commits without OOM.
- **Incremental Processing:** Can checkpoint state after each batch.
- **Responsiveness:** Can emit results incrementally for web UI.
- **Scalability:** Linear memory usage with batch size, not commit count.

**Trade-offs:**
- **Complexity:** Need to manage batch boundaries and checkpointing.
- **State Management:** Some analyzers need global state across batches.
- **Rejected alternative:** Load all commits into memory (current approach). Fails for large repos.

### 6. Lazy Evaluation

**Decision:** Compute time series on demand, not eagerly for all signals.

**Rationale:**
- **Performance:** Only compute what the user queries.
- **Caching:** Cache computed results for reuse.
- **Flexibility:** Can support ad-hoc queries not anticipated in advance.

**Trade-offs:**
- **Latency:** First query is slower (need to compute). Subsequent queries are fast (cached).
- **Complexity:** Need cache invalidation when new data arrives.
- **Rejected alternative:** Eagerly compute all signals on every run. Wastes computation on unused signals.

### 7. Temporal Operators as First-Class Citizens

**Decision:** Implement reusable temporal operators (delta, velocity, etc.) that can apply to any time series.

**Rationale:**
- **Code Reuse:** Don't reimplement velocity for every signal.
- **Consistency:** Same operator behavior across all signals.
- **Composability:** Can chain operators (e.g., `velocity(acceleration(pagerank))`).
- **Declarative Queries:** QueryBuilder can apply operators without knowing implementation.

**Trade-offs:**
- **Type Safety:** Need to ensure operator types match signal types.
- **Rejected alternative:** Each signal implements its own temporal logic. Violates DRY.

### 8. Incremental Processing with Checkpointing

**Decision:** Track last processed commit SHA and only process new commits on subsequent runs. Periodically checkpoint state.

**Rationale:**
- **Performance:** Avoid reprocessing entire git history every time.
- **Efficiency:** Typical dev workflow: analyze, make small changes, analyze again. Should only reanalyze changes.
- **Resilience:** If pipeline crashes, can resume from checkpoint.

**Trade-offs:**
- **State Management:** Need to handle invalid checkpoints (e.g., git reset).
- **Complexity:** Need to track which signals need recomputation.
- **Rejected alternative:** Always reprocess from scratch. Too slow for iterative development.

### 9. Protocol-Based Interfaces

**Decision:** Use Python protocols (`Protocol`) instead of abstract base classes (`ABC`) for interfaces.

**Rationale:**
- **Duck Typing:** No inheritance hierarchy, just structural compatibility.
- **Flexibility:** Can use concrete classes that match protocol without explicit inheritance.
- **Type Safety:** Mypy checks protocol compliance.
- **Simplicity:** Less boilerplate than ABC.

**Trade-offs:**
- **Runtime Checks:** No runtime verification (mypy-only).
- **Rejected alternative:** ABC with abstract methods. Too rigid.

### 10. Backward Compatibility Layer

**Decision:** Provide legacy adapters and deprecate old API gradually instead of breaking immediately.

**Rationale:**
- **Migration Path:** Users can migrate incrementally.
- **Stability:** Existing code doesn't break immediately.
- **Testing:** Can verify new implementation against old results.

**Trade-offs:**
- **Code Bloat:** Maintain legacy code temporarily.
- **Confusion:** Two APIs coexist.
- **Rejected alternative:** Immediate breaking change. Too disruptive for users.

---

## Conclusion

This architectural redesign transforms the Shannon Insight temporal module from a monolithic, limited implementation into a flexible, extensible platform for advanced temporal analysis. The key improvements are:

1. **Event-driven architecture** for multi-granularity git event capture
2. **Pluggable analyzer framework** for easy extension
3. **Entity identity management** for tracking across renames
4. **Time series storage abstraction** for scalability
5. **Incremental processing** for performance
6. **Reusable temporal operators** for consistency

The design enables advanced capabilities like line-level churn, fix traceability, graph evolution, and historical reconstruction while maintaining backward compatibility. The phased migration approach minimizes disruption while delivering incremental value.

The architecture is designed for:
- **Extensibility:** New analyzers, operators, and storage backends can be added without modifying core
- **Performance:** Streaming processing, lazy evaluation, and incremental updates enable handling large repos
- **Correctness:** Entity identity management and proper event handling handle edge cases
- **Maintainability:** Clear separation of concerns and protocol-based interfaces make code understandable
- **Testability:** Each component is independently testable with mock dependencies

This redesign positions Shannon Insight to become a comprehensive temporal analysis tool capable of supporting the advanced research and engineering use cases envisioned in the v2 specification.
