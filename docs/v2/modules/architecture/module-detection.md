# architecture/ --- Module Boundary Detection

How Shannon Insight identifies module boundaries without user configuration, with graceful fallbacks for flat projects and monorepos, and config override for when heuristics are wrong.

Based on the research in `docs/solutions.md` (W7).

## Algorithm Overview

```
Step 1: Detect project roots (monorepo awareness)
Step 2: Determine module granularity (depth histogram)
Step 3: Assign files to modules (directory | Louvain | config)
Step 4: Compute boundary alignment (directory vs. dependency community)
```

## Step 1: Detect Project Roots

Scan the repository for package markers that indicate project roots:

| Marker file | Language/ecosystem |
|-------------|-------------------|
| `pyproject.toml` | Python |
| `setup.py`, `setup.cfg` | Python (legacy) |
| `package.json` | JavaScript/TypeScript |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `pom.xml`, `build.gradle` | Java |
| `*.gemspec` | Ruby |
| `CMakeLists.txt` | C/C++ |

### Monorepo Detection

If multiple package markers are found at different directory levels:

```
repo/
  services/
    auth/
      pyproject.toml    # root 1
      src/auth/
    billing/
      pyproject.toml    # root 2
      src/billing/
  libs/
    common/
      pyproject.toml    # root 3
      src/common/
```

Each marker defines a **project root**. Module detection runs independently within each project root. The project roots themselves become top-level modules.

**Workspace detection** (supplementary):

| Ecosystem | Config |
|-----------|--------|
| npm | `workspaces` field in root `package.json` |
| Yarn | `workspaces` in `package.json` |
| pnpm | `pnpm-workspace.yaml` |
| Python | namespace packages (multiple `pyproject.toml` under common root) |
| Go | `go.work` |
| Nx | `project.json` files |

If workspace config exists, use it as the authoritative source of project roots rather than scanning for markers.

### Single-Root Projects

If exactly one marker is found (or none), the entire repository is a single project root. Proceed to Step 2.

## Step 2: Determine Module Granularity

For each project root, determine the directory depth at which modules live.

### Depth Histogram

Count source files at each directory depth relative to the project root:

```python
depth_histogram = Counter()
for file in source_files:
    relative = file.path.relative_to(project_root)
    depth = len(relative.parts) - 1   # -1 for the filename
    depth_histogram[depth] += 1
```

Example for a typical Python project:

```
src/
  __init__.py           depth=1  (1 file)
  models.py             depth=1  (1 file)
  auth/
    __init__.py          depth=2  (4 files)
    service.py           depth=2
    middleware.py         depth=2
    utils.py             depth=2
  payments/
    __init__.py          depth=2  (3 files)
    processor.py         depth=2
    models.py            depth=2
  utils/
    helpers.py           depth=2  (2 files)
    validators.py        depth=2

Histogram: {1: 2, 2: 9}
```

### Granularity Selection

```
module_depth = shallowest depth where:
  - at least 2 directories exist at that depth
  - most directories at that depth contain 2+ files
```

In the example above: `module_depth = 2` (auth/, payments/, utils/ are the modules).

### Edge Cases

| Case | Behavior |
|------|----------|
| All files at depth 0 (flat project) | No directory structure. Fall through to Louvain fallback in Step 3. |
| Deep nesting with few files per directory | Increase `module_depth` until directories have enough files. If no level works, use the shallowest level with >= 2 directories. |
| Single deep path (e.g., `src/com/example/app/...`) | Skip common prefixes where only one directory exists at that depth. Module depth starts where branching occurs. |

## Step 3: Assign Files to Modules

Three strategies, applied in priority order:

### Strategy A: User Configuration (highest priority)

If `shannon-insight.toml` contains a `[modules]` section, use it as the authoritative source:

```toml
[modules]
custom = [
    { name = "auth", paths = ["src/auth/", "src/middleware/auth*"] },
    { name = "payments", paths = ["src/payments/", "src/billing/"] },
    { name = "core", paths = ["src/core/", "src/models.py"] },
]
```

Config rules:
- `paths` supports glob patterns (resolved relative to project root).
- A file matching multiple modules is assigned to the first match.
- Files not matching any pattern are grouped into an `_unassigned` module.
- Config modules completely override auto-detection. No mixing.

### Strategy B: Directory Structure (default)

Assign each file to the directory at `module_depth`:

```python
def assign_module(file_path: str, module_depth: int) -> str:
    parts = Path(file_path).parts
    if len(parts) <= module_depth:
        return "_root"   # file above module depth
    return str(Path(*parts[:module_depth]))
```

Files above `module_depth` (e.g., `src/__init__.py` when modules are at `src/auth/`) are grouped into a `_root` pseudo-module.

### Strategy C: Louvain Community Fallback

When directory structure is insufficient (flat project or all files in one directory):

```python
communities = graph_metrics.communities   # from graph/ Louvain output
modules = {}
for file_path, community_id in communities.items():
    module_name = f"community_{community_id}"
    modules.setdefault(module_name, []).append(file_path)
```

Louvain communities from the dependency graph become synthetic modules. This achieves 60--80% MoJoFM (similarity to ground truth) based on software architecture recovery literature.

When Louvain is used as the module source:
- `boundary_alignment` is 1.0 by definition (modules ARE the communities).
- Module names are synthetic (`community_0`, `community_1`, ...).
- A log message is emitted: "No directory structure detected; using dependency communities as modules."

### Fallback Chain

```
config override? ──yes──> use config
       |
      no
       |
directory branching at any depth? ──yes──> use directory at module_depth
       |
      no
       |
Louvain communities available? ──yes──> use communities
       |
      no
       |
single module (entire project) ──> all metrics trivial
```

## Step 4: Compute Boundary Alignment

For each module detected via directory structure (Strategy B), measure how well the directory boundary matches the actual dependency community structure from Louvain:

```
For module M:
  files_in_M = set of files in this module
  community_counts = Counter(communities[f] for f in files_in_M)
  dominant_community = community_counts.most_common(1)[0][0]
  dominant_count = community_counts[dominant_community]

  boundary_alignment(M) = dominant_count / len(files_in_M)
```

This is signal #42 from `registry/signals.md`.

### Interpretation

| Alignment | Meaning |
|-----------|---------|
| 1.0 | All files in this directory belong to the same dependency community. Directory boundary is perfect. |
| 0.7--0.9 | Mostly aligned. A few files might belong elsewhere. |
| 0.5--0.7 | Mixed. The directory contains files from multiple dependency clusters. Consider splitting. |
| < 0.5 | Directory boundary contradicts dependency structure. The module boundary is likely wrong. |

### Low Alignment Warning

When `boundary_alignment(M) < 0.5`:

```
warning: Module "src/utils/" has boundary alignment 0.35.
  Files cluster into 3 dependency communities:
    Community 2: helpers.py, validators.py, formatters.py (auth-related)
    Community 5: db_utils.py, migration.py (persistence-related)
    Community 8: cli_helpers.py (CLI-related)
  suggestion: Split src/utils/ into domain-aligned modules.
```

### Codebase-Level Alignment

```
codebase_alignment = mean(boundary_alignment(M) for M in modules)
```

This feeds into `ArchHealth.boundary_alignment`.

## Monorepo Handling

For monorepos with multiple project roots:

1. Each project root is a top-level module.
2. Within each project root, apply Steps 2--4 to detect sub-modules.
3. Cross-root dependencies are tracked as inter-module edges at the top level.
4. Martin's metrics (I, A, D) are computed at both levels:
   - Per sub-module within each project root.
   - Per project root across the monorepo.

```
monorepo/
  services/auth/     -> top-level module "services/auth"
    src/auth/         -> sub-module "services/auth/src/auth"
    src/middleware/    -> sub-module "services/auth/src/middleware"
  services/billing/  -> top-level module "services/billing"
    src/billing/      -> sub-module "services/billing/src/billing"
  libs/common/       -> top-level module "libs/common"
```

## Configuration Reference

Full `shannon-insight.toml` module configuration:

```toml
[modules]
# Explicit module definitions (overrides auto-detection)
custom = [
    { name = "auth", paths = ["src/auth/", "src/middleware/auth*"] },
    { name = "payments", paths = ["src/payments/", "src/billing/"] },
]

# Directories to exclude from module detection
exclude = ["tests/", "docs/", "scripts/", "vendor/", "node_modules/"]

# Override the auto-detected module depth
# depth = 2

# Minimum files for a directory to be considered a module (default: 2)
# min_files = 2
```

When no `[modules]` section exists, auto-detection runs with default exclusions (`tests/`, `docs/`, `vendor/`, `node_modules/`, `__pycache__/`, `.git/`).
