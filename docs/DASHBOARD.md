# Dashboard Guide

The Shannon Insight dashboard is a live, browser-based interface for exploring analysis results. Start it with:

```bash
pip install shannon-codebase-insight[serve]
shannon-insight serve
```

The dashboard runs at `http://127.0.0.1:8765` by default and auto-opens your browser. It watches for file changes and re-analyzes automatically, pushing updates via WebSocket.

## Overview Screen

The default screen provides a high-level assessment of codebase health.

### Health Score

A single number on a 1-10 scale, computed from `codebase_health` (internal 0-1 mapped to 1-10). Color-coded:

| Score | Color | Label |
|-------|-------|-------|
| 8-10 | Green | Healthy |
| 6-8 | Yellow | Moderate |
| 4-6 | Orange | At Risk |
| 1-4 | Red | Critical |

The score is surrounded by a subtle glow ring that inherits its color.

### Verdict Banner

A one-line assessment above the health score (e.g., "Moderate structural issues -- 1 file needs attention"). The verdict considers health score, focus point severity, and total finding count.

### Stats Strip

Four stat cards in a row:

| Stat | Source |
|------|--------|
| **Files** | Total files analyzed |
| **Modules** | Detected modules (top-level directories with code) |
| **Commits** | Git commits analyzed for temporal signals |
| **Issues** | Total findings across all categories |

### Issue Summary

A two-column layout with the left card showing issue counts grouped into four categories:

| Category | Finding Types Included |
|----------|----------------------|
| **Incomplete** | `hollow_code`, `phantom_imports`, `orphan_code`, `incomplete_implementation`, `duplicate_incomplete` |
| **Fragile** | `high_risk_hub`, `god_file`, `bug_magnet`, `thrashing_code`, `unstable_file`, `weak_link`, `bug_attractor`, `chronic_problem`, `directory_hotspot` |
| **Tangled** | `hidden_coupling`, `accidental_coupling`, `dead_dependency`, `copy_paste_clone`, `layer_violation`, `zone_of_pain`, `boundary_mismatch`, `flat_architecture`, `architecture_erosion`, `naming_drift` |
| **Team** | `knowledge_silo`, `truck_factor`, `review_blindspot`, `conway_violation` |

Each row shows the category name, count, file count, and a bar chart proportional to the maximum category count. Rows with high-severity findings are highlighted in orange. Click a category row to jump to the Issues screen filtered to that tab.

### Risk Distribution Histogram

Below the issue summary, a horizontal bar chart shows file counts in 5 risk buckets: 0-0.2, 0.2-0.4, 0.4-0.6, 0.6-0.8, 0.8-1.0. Each bar is colored from green (low risk) to red (high risk).

### Focus Point

The right card shows the single most actionable file -- the system's answer to "what should I work on first?"

Content includes:
- **File path** (clickable link to file detail)
- **Score breakdown** -- 2x2 grid showing risk, impact, tractability, and confidence scores (each 0-1)
- **Why** -- One-line explanation (e.g., "Central file with high churn and single owner")
- **Top findings** -- Up to 3 findings on this file with severity dots
- **Also consider** -- Up to 3 alternative files with links and short explanations

## Issues Screen

Detailed view of all findings organized by category.

### Category Tabs

Horizontal tabs across the top: **Incomplete**, **Fragile**, **Tangled**, **Team**. Each tab shows its finding count. Click to switch.

### Filter Bar

Above the tabs:
- **Sort dropdown**: Severity (high first), Severity (low first), Effort (low first), File count
- **Severity filter toggles**: CRITICAL, HIGH, MEDIUM, LOW, INFO -- click to toggle visibility

### Finding Cards

Each finding is rendered as a card with:

| Element | Description |
|---------|-------------|
| **Severity dot** | Color-coded circle: red (critical >=0.9), orange (high >=0.8), yellow (medium >=0.6), blue (low >=0.4), gray (info) |
| **Type label** | Human-readable name (e.g., "High Risk Hub") |
| **Effort badge** | LOW, MEDIUM, or HIGH in a bordered pill |
| **CHRONIC badge** | Red pill shown if finding persists 3+ snapshots |
| **Files** | Clickable file paths linking to file detail view |
| **Evidence** | Signal name, raw value, and percentile for each evidence item (e.g., "pagerank: **0.0847** (92nd pctl)") |
| **Interpretation** | Contextual explanation of what the finding means |
| **Suggestion** | Actionable next step (prefixed with arrow) |

Cards with confidence < 0.5 are dimmed (60% opacity).

Left border color matches severity level (red/orange/yellow/blue/gray).

## Files Screen

Browse and search all analyzed files.

### Filter Bar

Enclosed in a card with:
- **Search input** -- Real-time substring filter on file paths. Press `Esc` to unfocus.
- **Filter chips** -- Toggle buttons: Has Issues, Orphans, MODEL, SERVICE, ENTRY_POINT, TEST
- **View toggle** -- Switch between Table and Treemap views

A count line shows "Showing X of Y files".

### Table View (default)

Sortable columns:

| Column | Description | Sort Default |
|--------|-------------|-------------|
| **File** | Relative path (monospace, right-truncated for long paths) | Ascending |
| **Risk** | `risk_score` (0-1), colored by health scale | Descending |
| **Churn** | `total_changes` commit count | Descending |
| **Complexity** | `cognitive_load` value | Descending |
| **Blast R.** | `blast_radius_size` -- files affected if this breaks | Descending |
| **Issues** | Count of findings involving this file | Descending |

Click a column header to sort. Click again to reverse. Click a row to open file detail.

Recently changed files (when using `--changed`) show a blue "changed" badge.

Keyboard selection: `j`/`k` moves a blue highlight, `Enter` opens the selected row.

Table limited to 200 rows with a note if more exist.

### Treemap View

A squarified treemap where:
- **Area** = lines of code
- **Color** = risk score (green=low, red=high)
- Hover shows filename, line count, and risk score
- Click a cell to open file detail

Limited to 300 files for performance.

### File Detail View

Accessed by clicking a file in the table/treemap or navigating to `#files/<path>`.

**Header**: File path, role badge (if not UNKNOWN), health score (colored).

**Metrics Grid** (4x2):

| Metric | Signal |
|--------|--------|
| Lines | `lines` |
| Functions | `function_count` |
| Risk Score | `risk_score` |
| PageRank | `pagerank` |
| Churn | `total_changes` |
| Bus Factor | `bus_factor` |
| Blast Radius | `blast_radius_size` |
| Cognitive Load | `cognitive_load` |

**Findings Section**: All findings involving this file, rendered as cards identical to the Issues screen.

**Signals Section**: All signals grouped by category, in collapsible sections (first two open by default):

| Category | Signals |
|----------|---------|
| **Size & Complexity** | `lines`, `function_count`, `class_count`, `max_nesting`, `cognitive_load` |
| **Graph Position** | `pagerank`, `betweenness`, `in_degree`, `out_degree`, `blast_radius_size`, `depth` |
| **Code Health** | `stub_ratio`, `is_orphan`, `phantom_import_count`, `compression_ratio`, `semantic_coherence` |
| **Change History** | `total_changes`, `churn_trajectory`, `churn_cv`, `bus_factor`, `fix_ratio`, `change_entropy` |
| **Team Context** | `author_entropy`, `bus_factor` |
| **Computed Risk** | `risk_score`, `wiring_quality`, `file_health_score`, `raw_risk` |
| **Other** | Any uncategorized signals |

Signal values are colored by polarity:
- **Red-scaled** (higher is worse): `risk_score`, `cognitive_load`, `churn_cv`, `stub_ratio`, `fix_ratio`, `blast_radius_size`
- **Green-scaled** (higher is better): `wiring_quality`, `file_health_score`, `semantic_coherence`, `bus_factor`, `compression_ratio`
- **Blue** (neutral): `pagerank`, `betweenness`, `in_degree`, `lines`, `total_changes`

Click `<- Files` to return to the file list.

## Modules Screen

### Module Table

Sortable columns:

| Column | Description |
|--------|-------------|
| **Module** | Module path (top-level directory) |
| **Health** | Module `health_score` (1-10 scale, colored) |
| **Instability** | Martin's instability metric (Ce / (Ca + Ce)) |
| **Abstractness** | Ratio of abstract/interface files |
| **Files** | Number of files in module |
| **Velocity** | Commits per week touching module |

Click a column header to sort, click a row to drill into module detail.

### Module Detail View

Accessed by clicking a module row or navigating to `#modules/<path>`.

- **Header**: Module path and health score (colored)
- **Stats grid**: Files, Instability, Abstractness, Velocity
- **File list**: All files in the module (clickable links to file detail)
- **Violations**: Architecture violations involving this module (if any)

## Health Screen

Historical analysis requires saved snapshots in `.shannon/history.db`.

### Health Trend Chart

A sparkline chart showing `codebase_health` over the last 20 snapshots. Uses accent blue color with a filled area underneath.

Only visible when trend data exists (2+ snapshots).

### Top Movers

Files with the largest `risk_score` delta between the oldest and newest of the last 5 snapshots. Each entry shows the file path (clickable) and a signed delta value colored red (increasing risk) or green (decreasing risk).

### Chronic Findings

Findings persisting across 3+ consecutive snapshots. Shows finding type and snapshot count.

### Concern Radar Chart

When 3+ concerns have data, renders as a hexagonal SVG radar chart with:
- Concentric rings at intervals of 2 (scale 0-10)
- Axes labeled with concern names
- Data polygon filled with accent blue at 15% opacity
- Dots at each data point

Concerns measured: Complexity, Coupling, Architecture, Stability, Team, Broken.

Falls back to horizontal bar charts when fewer than 3 concerns have data.

### Global Signals Table

Two-column table listing all global signals and their values:

| Signal | Description |
|--------|-------------|
| `architecture_health` | Composite architecture score |
| `centrality_gini` | Inequality of centrality distribution |
| `clone_ratio` | Fraction of files with clones |
| `codebase_health` | The master health metric |
| `conway_alignment` | Team-structure alignment (1.0 = perfect) |
| `cycle_count` | Strongly connected components |
| `fiedler_value` | Algebraic connectivity (spectral) |
| `glue_deficit` | Missing orchestration/coordination files |
| `modularity` | Louvain modularity score |
| `orphan_ratio` | Fraction of files with no importers |
| `phantom_ratio` | Fraction of imports that resolve to nothing |
| `spectral_gap` | Difference between first two eigenvalues |
| `team_risk` | Social/organizational risk composite |
| `violation_rate` | Fraction of cross-module edges that violate layers |
| `wiring_score` | Codebase-level wiring quality |

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `1` | Switch to Overview |
| `2` | Switch to Issues |
| `3` | Switch to Files |
| `4` | Switch to Modules |
| `5` | Switch to Health |
| `/` | Focus file search input |
| `j` | Move selection down in tables |
| `k` | Move selection up in tables |
| `Enter` | Open selected item |
| `Esc` | Go back (detail -> list) or unfocus search |
| `?` | Toggle keyboard shortcuts overlay |

Shortcuts are disabled when a text input is focused.

## API Endpoints

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| `GET` | `/` | Dashboard HTML page | `text/html` |
| `GET` | `/api/state` | Full dashboard state JSON | `application/json` (202 if analyzing) |
| `GET` | `/api/export/json` | Download full state as JSON file | `application/json` attachment |
| `GET` | `/api/export/csv` | Download file table as CSV | `text/csv` attachment |
| `GET` | `/api/gate` | Quality gate for CI | `{"status":"PASS\|FAIL", "health":N, ...}` |
| `WS` | `/ws` | Real-time updates | Messages: `complete` (full state), `progress` (phase update), `ping` (keepalive) |

### WebSocket Messages

**Server -> Client**:
- `{"type": "complete", "state": {...}}` -- Full state update after analysis completes
- `{"type": "progress", "message": "...", "percent": 0.5}` -- Analysis progress
- `{"type": "ping"}` -- Keepalive (every 30 seconds)

The client auto-reconnects on disconnect with exponential backoff (1s initial, 15s max).

### Quality Gate Response

```json
{
  "status": "PASS",
  "health": 7.2,
  "critical_count": 0,
  "finding_count": 12,
  "reason": "Health 7.2, no critical issues"
}
```

Fails (`"FAIL"`) when:
- Health score < 4.0
- Any finding with severity >= 0.9 (critical)

## Export

### JSON Export

`GET /api/export/json` downloads the complete dashboard state as a JSON file named `shannon-insight-{timestamp}.json`. Contains all data visible in the dashboard: files, findings, signals, modules, trends.

### CSV Export

`GET /api/export/csv` downloads the file table as a CSV with columns:

| Column | Source |
|--------|--------|
| `path` | File path |
| `risk_score` | Per-file risk score |
| `total_changes` | Git commit count |
| `cognitive_load` | Cognitive complexity |
| `blast_radius` | Files affected if this breaks |
| `finding_count` | Number of findings |
| `role` | Detected file role (MODEL, SERVICE, etc.) |
| `health` | Per-file health score (1-10) |
| `lines` | Lines of code |

## Configuration

Dashboard-specific flags:

```bash
shannon-insight serve --port 9000        # Custom port
shannon-insight serve --host 0.0.0.0     # Bind to all interfaces
shannon-insight serve --no-browser       # Don't auto-open browser
shannon-insight serve -v                 # Verbose server logs
shannon-insight serve -w 4               # Parallel analysis workers
shannon-insight serve -c config.toml     # Custom config file
```

The dashboard inherits all settings from `shannon-insight.toml` and `SHANNON_*` environment variables.
