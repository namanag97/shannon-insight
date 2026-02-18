# UAT Test Suite for Phase 1 & Phase 2

This directory contains scripts to download and test shannon-insight against 10 opensource codebases.

## Codebases

| # | Project | Languages | Size | Description |
|---|---------|-----------|------|-------------|
| 1 | **Sentry** | Python + TypeScript/React | Large | Error tracking platform |
| 2 | **Grafana** | Go + TypeScript/React | Large | Observability platform |
| 3 | **Mattermost** | Go + TypeScript/React | Large | Team collaboration |
| 4 | **Cal.com** | TypeScript (fullstack) | Large | Scheduling platform |
| 5 | **Supabase** | TypeScript + Go | Large | Firebase alternative |
| 6 | **FastAPI** | Python | Medium | Modern web framework |
| 7 | **httpx** | Python | Medium | Async HTTP client |
| 8 | **Pydantic** | Python | Medium | Data validation |
| 9 | **Rich** | Python | Small | Terminal formatting |
| 10 | **Typer** | Python | Small | CLI framework |

## Quick Start

```bash
# Step 1: Download all codebases (~5-10 min)
./download_codebases.sh

# Step 2: Run Phase 1 & 2 QA on all codebases
python run_phase1_phase2_qa.py

# Results will be in ./results/
```

## Commands

### Download Codebases

```bash
# Download to default location (./codebases)
./download_codebases.sh

# Download to custom location
./download_codebases.sh /path/to/codebases
```

### Run QA Tests

```bash
# Run on all codebases in ./codebases
python run_phase1_phase2_qa.py

# Custom paths
python run_phase1_phase2_qa.py \
  --codebases-dir /path/to/codebases \
  --output-dir /path/to/results
```

### Run on Single Codebase

```bash
# Quick test on one project
python -c "
from pathlib import Path
from run_phase1_phase2_qa import run_qa_on_codebase, print_summary

result = run_qa_on_codebase(
    Path('./codebases/fastapi'),
    Path('./results')
)
print_summary([result])
"
```

## Output

After running `run_phase1_phase2_qa.py`:

```
./results/
├── sentry_qa.db          # SQLite database with all facts + graph
├── grafana_qa.db
├── ...
└── qa_report.json        # Full JSON report with all metrics
```

## Metrics Collected

### Phase 1 (Parsing)
- Files scanned
- Functions, classes, imports extracted
- Import resolution (internal/stdlib/phantom)
- Type annotation coverage (return_type, param_types, field_types)

### Phase 2 (Graph)
- Node counts (files, functions, classes, types)
- Edge counts (imports, calls, inherits, contains, returns, param_type, field_type)
- Analysis (cycles, dead functions, communities, modularity)

### Performance
- Scan time, resolve time, store time, build time, algo time
- Files per second throughput

### Storage
- Database size (KB)
- KB per file

## Expected Results

| Metric | Expected Range |
|--------|----------------|
| Files/second | 10-50 |
| KB/file | 20-50 |
| Return type coverage | 30-90% (depends on project) |
| Phantom imports | <10% (well-configured) |
| Modularity | 0.3-0.6 |
