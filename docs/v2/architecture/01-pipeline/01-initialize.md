# Stage 1: Initialize

Build the runtime context and resolve configuration.

---

## Input

- CLI arguments (`--path`, `--language`, `--exclude`, etc.)
- Environment variables (`SHANNON_*`)
- Config files (`shannon-insight.toml`, `~/.config/shannon-insight/config.toml`)

---

## Output

### RuntimeContext

```python
@dataclass
class RuntimeContext:
    # Location
    root: Path                    # Resolved absolute path

    # Git state
    is_git_repo: bool
    branch: str | None            # Current branch name
    head_commit: str | None       # HEAD SHA (short)

    # Language detection
    languages: list[str]          # Detected languages, sorted by file count
    primary_language: str         # First in list

    # Scale (determines tier)
    file_count: int               # Source files matching filters
    tier: Tier                    # ABSOLUTE | BAYESIAN | FULL

    # Capabilities
    has_git: bool                 # Can run temporal analysis
    has_tests: bool               # Test files detected

    # Timing
    started_at: datetime
```

### Config

```python
@dataclass
class Config:
    # Scope
    include: list[str] = ["**/*"]
    exclude: list[str] = []       # Merged with built-in excludes

    # Thresholds (override defaults from registry)
    thresholds: dict[Signal, float] = {}

    # Feature toggles
    enable_git: bool = True
    enable_semantic: bool = True
    enable_team: bool = True

    # Output
    max_findings: int = 20
    format: OutputFormat = TERMINAL

    # Persistence
    save_snapshot: bool = False
    db_path: Path | None = None   # Default: .shannon/history.db
```

---

## Config Resolution Order

Priority (highest wins):

```
1. CLI flags              --exclude="*.test.py" --max-findings=10
2. Environment variables  SHANNON_MAX_FINDINGS=10
3. Project config         ./shannon-insight.toml
4. User config            ~/.config/shannon-insight/config.toml
5. Built-in defaults      (see below)
```

### Built-in Defaults

```python
DEFAULT_CONFIG = Config(
    include=["**/*"],
    exclude=[],
    thresholds={},
    enable_git=True,
    enable_semantic=True,
    enable_team=True,
    max_findings=20,
    format=OutputFormat.TERMINAL,
    save_snapshot=False,
    db_path=None,
)
```

### Built-in Exclude Patterns (always applied)

```python
BUILTIN_EXCLUDES = [
    # Version control
    ".git", ".svn", ".hg",

    # Dependencies
    "node_modules", "vendor", "venv", ".venv", "env",
    "__pycache__", ".pytest_cache", ".mypy_cache",

    # Build output
    "dist", "build", "target", "out", "bin", "obj",
    ".next", ".nuxt", ".output",

    # IDE
    ".idea", ".vscode", ".vs",

    # Generated
    "*.min.js", "*.min.css", "*.map",
    "*.pyc", "*.pyo", "*.class",

    # Lock files (not source)
    "package-lock.json", "yarn.lock", "Pipfile.lock",
    "poetry.lock", "Cargo.lock", "go.sum",
]
```

---

## Tier Determination

Based on source file count after filtering:

```python
def determine_tier(file_count: int) -> Tier:
    if file_count < 15:
        return Tier.ABSOLUTE
    elif file_count < 50:
        return Tier.BAYESIAN
    else:
        return Tier.FULL
```

### Tier Effects

| Tier | File Count | Percentiles | Composites | Finders |
|------|------------|-------------|------------|---------|
| ABSOLUTE | < 15 | Not computed | Not computed | 8 of 22 |
| BAYESIAN | 15-50 | Bayesian posterior | Computed | 22 of 22 |
| FULL | 50+ | Standard | Computed | 22 of 22 |

---

## Language Detection

```python
def detect_languages(root: Path, config: Config) -> list[str]:
    """
    Scan files, count by extension, return sorted by count.

    Returns list like: ["python", "typescript", "go"]
    """
    extension_counts: Counter[str] = Counter()

    for file in glob_files(root, config.include, config.exclude):
        ext = file.suffix.lower()
        if lang := EXTENSION_TO_LANGUAGE.get(ext):
            extension_counts[lang] += 1

    return [lang for lang, _ in extension_counts.most_common()]
```

### Extension Mapping

```python
EXTENSION_TO_LANGUAGE = {
    ".py": "python",
    ".pyi": "python",
    ".go": "go",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".java": "java",
    ".kt": "kotlin",
    ".rs": "rust",
    ".rb": "ruby",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".cc": "cpp",
    ".cs": "csharp",
    ".swift": "swift",
    ".scala": "scala",
    ".php": "php",
}
```

---

## Git Detection

```python
def detect_git(root: Path) -> tuple[bool, str | None, str | None]:
    """
    Check if root is in a git repo, get branch and HEAD.

    Returns: (is_git_repo, branch, head_commit)
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=root,
            capture_output=True,
            timeout=5,
        )
        if result.returncode != 0:
            return (False, None, None)

        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=root,
            capture_output=True,
        ).stdout.decode().strip()

        head = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=root,
            capture_output=True,
        ).stdout.decode().strip()

        return (True, branch or None, head or None)

    except (subprocess.TimeoutExpired, FileNotFoundError):
        return (False, None, None)
```

---

## Validation

Before proceeding to Collect:

```python
def validate_context(ctx: RuntimeContext) -> None:
    """Raise if context is invalid."""

    if not ctx.root.exists():
        raise ValueError(f"Path does not exist: {ctx.root}")

    if not ctx.root.is_dir():
        raise ValueError(f"Path is not a directory: {ctx.root}")

    if ctx.file_count == 0:
        raise ValueError(f"No source files found in {ctx.root}")

    # Warnings (non-fatal)
    if not ctx.has_git:
        logger.warning("Not a git repository. Temporal analysis disabled.")

    if ctx.tier == Tier.ABSOLUTE:
        logger.warning(f"Only {ctx.file_count} files. Using absolute thresholds only.")
```
