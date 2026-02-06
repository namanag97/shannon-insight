# Git Extraction

How temporal/ reads git history. This is the I/O boundary of the module -- everything beyond this point is pure computation on in-memory data.

## Git Log Format

### Current format

```
git log --format=%H|%at|%ae --name-only -n5000
```

Fields:
- `%H` -- full commit hash (40 hex chars)
- `%at` -- author timestamp (unix epoch seconds)
- `%ae` -- author email

Output structure:
```
abc123...|1700000000|alice@example.com

src/foo.py
src/bar.py

def456...|1699999000|bob@example.com

src/baz.py
```

Each commit is a header line followed by blank line, then file paths, then blank line. The parser handles edge cases: merge commits with no files, consecutive headers without intervening blanks.

### v2 format

```
git log --format=%H|%at|%ae|%s --name-only -n5000
```

Adds `%s` (commit subject line) for intent classification. The pipe delimiter is safe because commit subjects cannot contain the `|` character in the `--format` string -- the parser splits on the first 3 pipes only.

**Parser change**: `line.split("|", 3)` instead of `line.split("|", 2)`. The header regex becomes:

```python
_HEADER_RE = re.compile(r"^[0-9a-f]{40}\|\d+\|[^|]+\|.*$")
```

## Parsing Algorithm

The current parser works line-by-line:

```
for each line in output:
    if line matches HEADER_RE:
        flush previous commit (if it had files)
        extract sha, timestamp, author[, message] from header
        reset current_files to empty
    elif line is non-empty and we have a current commit:
        append line as file path
flush final commit
```

Key behaviors:
- **Merge commits** (no files listed): silently dropped because the flush condition requires `current_files` to be non-empty
- **Consecutive headers**: handled correctly because each header triggers a flush of the previous commit
- **File paths with spaces**: handled (entire non-header line is treated as a file path)

## Commit Filtering

### Bulk commits (>50 files)

Commits touching more than `max_files_per_commit` files (default 50) are excluded from co-change analysis. These are typically:

- Mass reformats (running black/prettier across the codebase)
- Dependency updates (lockfile changes)
- Initial commits
- Large refactors that rename entire directories

**Where filtering happens**: In `build_cochange_matrix()`, not in the parser. The raw `GitHistory` retains all commits. Churn analysis also sees all commits (a mass reformat touching a file is a real change for churn purposes). Only co-change pair counting filters them, because a single bulk commit would create O(F^2) spurious pairs.

**Status**: EXISTS. No change in v2.

### No other filtering

The current implementation does not filter by:
- File extension (all files in git log are included)
- Author (bot commits are included)
- Date range (the `-n5000` limit is a count limit, not time limit)

v2 does not add additional filtering. The `analyzed_files` parameter passed to `build_churn_series()` and `build_cochange_matrix()` naturally limits results to files that exist in the current codebase.

## Performance

### Target: 400ms for 5000 commits

Breakdown:
- `git log` subprocess: ~200ms (I/O bound, depends on repo size)
- Parse log into `CommitRef` list: ~20ms (string splitting)
- Build churn series: ~50ms (O(commits x files_per_commit))
- Build co-change matrix: ~100ms (O(commits x F^2) with F capped at 50)
- Author analysis (v2): ~30ms (O(commits x files_per_commit))
- Intent classification (v2): ~10ms (regex on commit messages)

### Subprocess timeout

The git log subprocess has a 30-second timeout (`subprocess.run(..., timeout=30)`). If exceeded, `_run_git_log()` returns `None` and the entire temporal model is empty.

The `_is_git_repo()` check has a separate 5-second timeout on `git rev-parse --git-dir`.

## Shallow Clone Handling

Shallow clones (`git clone --depth N`) provide only the last N commits. The module handles this gracefully:

- `GitExtractor` works unchanged -- `git log` returns whatever history exists
- `span_days` reflects the actual available range (may be short)
- Churn trajectories may have fewer windows, making slope less reliable
- Co-change lift may be inflated (fewer total commits = higher co-occurrence rates)
- Bus factor and author entropy are computed from available data

No special detection of shallow clones is performed. The data is simply less reliable, which is acceptable -- better to give approximate temporal signals than none.

## What Current Code Does vs What Changes

### No changes

- Subprocess approach (no libgit2)
- Header regex parsing strategy
- `max_commits` parameter (default 5000)
- Timeout values (30s log, 5s rev-parse)
- Merge commit dropping
- Error handling (return None on failure)

### Changes in v2

| Change | Reason |
|--------|--------|
| Add `%s` to format string | Intent classification needs commit messages |
| Split on 3 pipes instead of 2 | Extra field in header |
| Updated header regex | Must match 4-field headers |
| `Commit` -> `CommitRef` naming | Avoid shadowing, align with v2 models |
| `hash` -> `sha` field rename | `hash` shadows Python builtin |
