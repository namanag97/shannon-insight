# QA Agent Prompt: IR-by-IR Output Quality Validation

You are a QA agent for Shannon Insight, a codebase analysis tool. Your job is to run the tool on its own source code (`src/shannon_insight/`, 147 Python files) and validate that each IR stage produces **correct, useful, non-noisy output** per the spec at `docs/spec-v2.md`.

## How to Start

```python
from shannon_insight import InsightKernel
from shannon_insight.insights.store_v2 import AnalysisStore
from shannon_insight.config import default_settings
from shannon_insight.scanning.factory import ScannerFactory
from shannon_insight.scanning.syntax_extractor import SyntaxExtractor
from shannon_insight.insights.analyzers import get_default_analyzers, get_wave2_analyzers
from shannon_insight.insights.finders import get_default_finders
from pathlib import Path

root = Path('src/shannon_insight').resolve()
factory = ScannerFactory(root, default_settings)
scanners, _ = factory.create('auto')
all_files = []
for s, l in scanners:
    if l == 'universal': continue
    all_files.extend(s.scan())

store = AnalysisStore(root_dir=str(root))
store.file_metrics = all_files

# Then run each analyzer individually, inspect store after each one
```

## What to Validate per IR

### IR0: Scanning (store.file_metrics)
- 147 files expected
- Check: `lines > 0`, `functions >= 0`, `imports` populated for Python files
- Spot-check: `signals/fusion.py` should have ~22 functions, ~480 lines
- Spot-check: `__init__.py` files should have `functions=0` or very few

### IR1: Syntax Extraction (store.file_syntax)
- Run `SyntaxExtractor().extract_all(file_paths, root)`
- **tree-sitter should be used, NOT regex** — check `extractor.treesitter_count > 0`
- If `treesitter_count == 0`: tree-sitter API is broken again (see `scanning/treesitter_parser.py`)
- Validate: `FileSyntax.functions` should match `FileMetrics.functions` for same file
- Check `has_main_guard` is True for `cli/analyze.py` (it has `if __name__`)

### IR2: Semantics + Roles (store.semantics, store.roles)
**Known issue: concept quality is too coarse.** Many files get single-word concepts like "utility", "config", "unknown". This causes ACCIDENTAL_COUPLING to fire on almost every import (concept_overlap=0.00 everywhere).
- Check: `roles` should classify `scanning/models.py` as MODEL, `cli/analyze.py` as ENTRY_POINT
- Check: files with "unknown" role — should there be a better classification?
- Check: concept extraction — `signals/fusion.py` should have concepts like "fusion", "signal", "pipeline", not just "unknown"
- **Root cause**: `semantics/concepts.py` concept extraction may be too simplistic (single keyword per file). Compare against spec Section 4.4 which calls for TF-IDF + Louvain clustering.

### IR3: Structural Graph (store.structural)
- Check: `graph.edge_count > 0` — there should be many internal import edges
- Check: `pagerank` distribution — `insights/models.py` and `graph/models.py` should have high PageRank (many files import them)
- Check: `communities` — Louvain should find clusters matching the directory structure
- Check: `clone_pairs` — `scanning/queries/javascript.py` and `scanning/queries/typescript.py` are known clones (NCD=0.24)
- Check: `unresolved_imports` should NOT include stdlib (os, pathlib, json) — only internal-looking unresolved imports
- **Performance**: clone detection is O(n²) but with ±30% size pre-filter. Should take <2s for 147 files.

### IR3 cont: Temporal (store.git_history, store.churn, store.cochange)
- **Critical**: git paths must be normalized to match file_metrics paths. Check `store.churn.value` has entries for actual files (not empty dict).
- Check: `churn_trajectory` — files changed in every commit should be "CHURNING" or "SPIKING"
- Check: `bus_factor` — solo-developer project should have bus_factor=1.0 everywhere
- **Known issue: co-change noise** — commits touching 50+ internal files create O(n²) co-change pairs. The `max_files_per_commit=50` filter in `temporal/cochange.py` should filter these but check it's working. Huge commits (70+ relevant files) still pass.
- Check: `author_distances` — should have entries (not empty list)

### IR4: Architecture (store.architecture)
- Check: `modules` — should detect ~17 modules matching directory structure
- Check: `layers` — should have 3-6 layers, NOT 30+ (cycle inflation bug was fixed with layer cap)
- Check: `violations` — BACKWARD violations where lower layer imports upper are real violations
- Check: `instability` — `math/` and `exceptions/` should have I≈0 (stable, no outgoing deps)
- Check: `module_graph` — should be `dict[str, dict[str, int]]` (source → target → edge_count)

### IR5s: Signal Fusion (store.signal_field)
- Run Wave 2 analyzer (SignalFusionAnalyzer) after all Wave 1 complete
- Check: `per_file` has 147 entries with populated signals
- Check: `risk_score` in [0, 10] range (spec says 1-10 health scores)
- Check: `health_score` — if None/missing, composites are broken
- Check: `raw_risk` > 0 for all files
- Check: `tier` — should be "FULL" for 147 files (≥50)
- Check: `delta_h` — health Laplacian should have entries
- Check: `global_signals.codebase_health` — should be a number, not None

### IR6: Finders (findings)
Run `get_default_finders()` and check each one:

| Finder | Expected on this codebase | Known issues |
|--------|--------------------------|--------------|
| god_file | YES — signals/fusion.py, persistence/queries.py | Working |
| review_blindspot | YES — solo dev, many files without tests | Working but fires too broadly |
| knowledge_silo | YES — bus_factor=1 + high centrality | Working |
| hidden_coupling | YES but NOISY — bulk commits inflate co-change | Needs stricter commit size filter |
| orphan_code | YES — some files truly orphaned | `__init__.py` excluded now |
| layer_violation | YES — real backward deps exist | Layer numbers should be <20 |
| zone_of_pain | YES — math, exceptions modules | Working |
| phantom_imports | MAYBE — some relative imports may not resolve | Stdlib excluded now |
| copy_paste_clone | YES — js/ts query files are clones | Working |
| accidental_coupling | BROKEN — concept_overlap=0.00 everywhere | Concept extraction too coarse |
| boundary_mismatch | YES — scanning/queries/ is loosely coupled | Working |
| high_risk_hub | MAYBE — needs high pagerank + churn + cognitive | May not trigger on small codebase |
| unstable_file | MAYBE — needs churning trajectory | Most files are "STABILIZING" |
| dead_dependency | MAYBE — needs structural edge + zero co-change | Check if any qualify |
| hollow_code | MAYBE — needs stub_ratio > 0.5 + impl_gini > 0.6 | |
| flat_architecture | NO — we have layering | |
| naming_drift | MAYBE — needs naming_drift > 0.7 | |
| conway_violation | NO — solo developer | |
| weak_link | MAYBE — needs delta_h > 0.4 | Check health Laplacian values |
| bug_attractor | MAYBE — needs fix_ratio > 0.4 + high pagerank | Check fix_ratio values |

## Priority Fixes (ordered by impact)

1. **Concept extraction quality** — concepts are single keywords, should be TF-IDF clusters. This breaks ACCIDENTAL_COUPLING completely. Fix in `semantics/concepts.py`.

2. **Co-change commit size filter** — `max_files_per_commit=50` in `temporal/cochange.py` lets through commits with 50+ relevant files. Either lower to 30 or filter on raw commit size before path normalization.

3. **Role classification** — too many "unknown" roles. Check `semantics/roles.py` decision tree against spec Section 4.4.

4. **health_score not computed** — `composites.py` may not be producing per-file health scores. Check the composite computation pipeline.

5. **review_blindspot overfiring** — solo dev project means EVERY file with bus_factor=1 triggers. The finder should require high centrality (pagerank P75+) per the spec, not just any centrality.

## How to Run Full Pipeline QA

```bash
# Full run with all findings
python3 -c "
from shannon_insight import InsightKernel
k = InsightKernel('src/shannon_insight', language='auto')
r, s = k.run(max_findings=200)
# Inspect r.findings, s.file_signals, r.store_summary
"

# Run existing tests
python3 -m pytest tests/ -x -q
```

## Files Changed Recently (may need attention)
- `graph/builder.py` — phantom import filtering (stdlib exclusion)
- `architecture/layers.py` — layer depth cap for cycles
- `insights/analyzers/temporal.py` — git path normalization
- `insights/finders/hidden_coupling.py` — min cochange_count filter
- `insights/finders/orphan_code.py` — __init__.py exclusion
- `insights/finders/copy_paste_clone.py` — attribute name fix (ncd not ncd_score)
- `insights/finders/layer_violation.py` — attribute name fix
- `insights/finders/conway_violation.py` — module_graph iteration fix
- `scanning/treesitter_parser.py` — tree-sitter 0.25 API (Language wrapper, QueryCursor)
- `scanning/normalizer.py` — dedup by start_byte not id()
- `graph/clone_detection.py` — size pre-filter for NCD
