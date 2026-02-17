# Documentation Generation Prompt

Use this prompt with Claude Code (or paste into Claude.ai with the codebase attached) to generate complete documentation for Shannon Insight.

---

## The Prompt

```
You are documenting Shannon Insight, a codebase analysis tool that uses information theory, graph algorithms, and git history to surface structural problems in codebases.

PyPI: `shannon-codebase-insight` | CLI: `shannon-insight`

Read the following source files to understand the full system, then produce the documentation sections listed below.

### Files to read (in order):
1. `CLAUDE.md` — Architecture overview
2. `src/shannon_insight/cli/__init__.py` — CLI entry point, all commands
3. `src/shannon_insight/cli/analyze.py` — Main analyze command + flags
4. `src/shannon_insight/cli/explain.py` — Explain command
5. `src/shannon_insight/cli/serve.py` — Dashboard serve command
6. `src/shannon_insight/config.py` — All configuration options
7. `src/shannon_insight/insights/kernel.py` — Analyzer orchestration
8. `src/shannon_insight/insights/finders/*.py` — Every finder (read all)
9. `src/shannon_insight/signals/models.py` — Signal definitions
10. `src/shannon_insight/scanning/factory.py` — Supported languages
11. `src/shannon_insight/persistence/models.py` — Snapshot schema
12. `src/shannon_insight/persistence/queries.py` — History queries
13. `src/shannon_insight/server/api.py` — Dashboard API state builder
14. `src/shannon_insight/server/app.py` — API endpoints
15. `src/shannon_insight/server/static/app.js` — Dashboard frontend features
16. `src/shannon_insight/server/static/style.css` — Visual design system
17. `src/shannon_insight/server/templates/index.html` — Dashboard structure
18. `pyproject.toml` — Entry points, dependencies, metadata

### Documentation to produce:

---

## Section 1: README.md (public-facing, for PyPI/GitHub)

Write a README.md with:

### Header
- Project name, one-line description, badges (PyPI version, Python 3.9+, License MIT)
- 2-sentence value proposition: what it does, who it's for

### Quick Start
```bash
pip install shannon-codebase-insight
cd your-project
shannon-insight .
```
- Show example output (abbreviated, 10 lines max)
- Link to dashboard: `shannon-insight serve`

### What It Finds
Table with columns: Finding | What It Detects | Severity | Example
List ALL finders grouped by category:
- **Structural** (god_file, high_risk_hub, orphan_code, hollow_code, phantom_imports, dead_dependency)
- **Architecture** (hidden_coupling, boundary_mismatch, layer_violation, zone_of_pain, flat_architecture)
- **Stability** (unstable_file, chronic_problem, thrashing_code, bug_magnet)
- **Team** (knowledge_silo, review_blindspot, truck_factor, conway_violation)
- **Code Quality** (copy_paste_clone, incomplete_implementation, naming_drift, directory_hotspot)

### How It Works (3 paragraphs max)
1. Scans source files for structural metrics (LOC, complexity, imports)
2. Builds dependency graph, runs PageRank/SCC/Louvain, extracts git history
3. Fuses signals into per-file risk scores, runs 28 finders, ranks by actionability

### Supported Languages
Table: Language | Extensions | Import Detection | Full Support

### CLI Reference
For each command (analyze, explain, diff, health, history, report, serve):
- One-line description
- Usage example
- Key flags table (flag, default, description)

### Dashboard
- Screenshot placeholder: `![Dashboard](docs/dashboard.png)`
- Feature list: 5 screens, real-time updates, keyboard shortcuts, export
- API endpoints table

### Configuration
- Show example `shannon-insight.toml` with all sections
- Explain precedence: CLI flags > env vars (SHANNON_*) > config file > defaults

### CI Integration
- GitHub Actions workflow example using `--fail-on high`
- Quality gate endpoint: `curl /api/gate`
- Exit codes: 0 = clean, 1 = findings above threshold

### Signals Reference
Table with columns: Signal | Description | Range | Higher Is
Group by: Size & Complexity, Graph Position, Code Health, Change History, Team Context, Computed Risk

### How Scoring Works (brief)
- Per-file: signals → percentiles → weighted fusion → risk_score (0-1)
- Codebase: file scores + global metrics → codebase_health (0-1) → display (1-10)
- Focus point: risk × impact × tractability × confidence

---

## Section 2: docs/DASHBOARD.md

Document the live dashboard (`shannon-insight serve`):

### Overview Screen
- Health score display (1-10 scale, color-coded)
- Verdict banner (one-line assessment)
- Stats strip (files, modules, commits, issues)
- Issue summary by category (incomplete, fragile, tangled, team)
- Risk distribution histogram
- Focus point with score breakdown (risk, impact, tractability, confidence)

### Issues Screen
- Category tabs with counts
- Sort options (severity, effort, file count)
- Severity filter toggles (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- Finding cards: type, severity dot, files, evidence (signal + value + percentile), suggestion, effort badge

### Files Screen
- Search input (real-time filter)
- Filter chips: Has Issues, Orphans, role filters (MODEL, SERVICE, ENTRY_POINT, TEST)
- Sortable columns: Path, Health, Risk, Lines, Changes, Centrality, Issues
- Table/Treemap toggle (squarified treemap colored by risk)
- File detail view:
  - Metrics grid (lines, functions, risk, pagerank, churn, bus factor, blast radius, cognitive load)
  - Findings on this file
  - Signals grouped by category (Size & Complexity, Graph Position, Code Health, Change History, Team Context, Computed Risk)
  - Signal values colored by polarity (red for bad-high, green for good-high, blue for neutral)

### Modules Screen
- Sortable table: Module, Health, Instability, Abstractness, Files, Velocity
- Module detail: stats, file list, violations

### Health Screen
- Health trend chart (if history exists)
- Top movers (files with largest risk delta)
- Chronic findings (persisting 3+ snapshots)
- Concern radar chart (hexagonal SVG)
- Global signals table

### Keyboard Shortcuts
Document all: 1-5 (tabs), / (search), j/k (navigate), Enter (drill), Esc (back), ? (help)

### API Endpoints
| Method | Path | Description | Response |
For: /api/state, /api/export/json, /api/export/csv, /api/gate, /ws

### Export
- JSON: full state download
- CSV: file table (path, risk, changes, complexity, blast_radius, findings, role, health, lines)

---

## Section 3: docs/SIGNALS.md

Document every signal in the system:

### Per-File Signals (36)
For each signal:
- **Name** (snake_case)
- **Human Label** (from SIGNAL_LABELS)
- **Category** (Size & Complexity | Graph Position | Code Health | Change History | Team Context | Computed Risk)
- **Type** (int | float | bool | str)
- **Range** (e.g., 0.0-1.0, 0-∞, true/false)
- **Polarity** (higher_is_worse | higher_is_better | neutral)
- **Description** (1-2 sentences: what it measures, why it matters)
- **Source** (which analyzer produces it)

### Per-Module Signals (15)
Same format as above.

### Global Signals
Same format. Include: codebase_health, modularity, fiedler_value, cycle_count, centrality_gini, orphan_ratio, phantom_ratio, wiring_score, architecture_health, team_risk, violation_rate, spectral_gap, conway_alignment.

### Signal Fusion
Explain how raw signals become risk_score:
1. Percentile normalization across all files
2. Weighted combination (compression 0.20, centrality 0.25, churn 0.20, coherence 0.15, cognitive 0.20)
3. Health Laplacian (delta_h) for graph-propagated risk

---

## Section 4: docs/FINDERS.md

Document every finder:

### For each finder:
- **Type** (snake_case identifier)
- **Name** (human-readable)
- **Category** (Structural | Architecture | Stability | Team | Code Quality)
- **Default Severity** (0.0-1.0)
- **Effort** (LOW | MEDIUM | HIGH)
- **Scope** (FILE | FILE_PAIR | MODULE | CODEBASE)
- **What It Detects** (2-3 sentences)
- **Signals Used** (which signals trigger this finder, with thresholds if available)
- **Example** (what a finding of this type looks like in output)
- **Why It Matters** (1-2 sentences on impact)
- **What To Do** (suggestion text)

---

## Section 5: docs/CONFIGURATION.md

Document all configuration:

### Configuration Precedence
CLI flags > SHANNON_* env vars > shannon-insight.toml > defaults

### Full Example Config
```toml
# shannon-insight.toml
[section]
key = value  # description (default: X)
```

### For each option:
- Key name
- Type
- Default value
- Valid range
- Description
- Environment variable override (SHANNON_*)

---

## Writing Style Guidelines:
- Technical but accessible — assume the reader is a senior developer
- Use concrete examples, not abstract descriptions
- Show actual CLI output where possible
- Tables for reference material, prose for concepts
- No marketing language — just facts about what the tool does
- Keep explanations under 3 sentences unless the concept requires more
- Use monospace for signal names, file paths, CLI commands
- Cross-reference between sections (e.g., "See [Signals Reference](SIGNALS.md) for full list")
```

---

## Usage

1. **With Claude Code:** Open the project and paste this prompt
2. **With Claude.ai:** Attach the source files listed above and paste the prompt
3. **Incremental:** Generate one section at a time by using just that section's instructions

The prompt produces 5 documents:
- `README.md` — Public-facing project documentation
- `docs/DASHBOARD.md` — Live dashboard user guide
- `docs/SIGNALS.md` — Complete signal reference
- `docs/FINDERS.md` — Complete finder reference
- `docs/CONFIGURATION.md` — Configuration reference
