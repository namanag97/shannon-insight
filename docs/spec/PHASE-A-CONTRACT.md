# Phase 1 (ACQUISITION) — Boundary & Run-Context Contract

**Status**: binding. This is the base layer every later phase stands on.
Supersedes informal descriptions; ARCHITECTURE-V4.md §Phase A remains the plan,
this document is the *operating contract*.

---

## 1. The Run Context (what "a run" IS)

One intake session = one immutable triple **(root-state, config, clock)**.

```
SessionContext
├── root        absolute resolved path — nothing outside it is ever read
├── config      IntakeConfig → canonical JSON → config_hash (sha256[:16])
│                 cache keys, goldens and receipts all cite this hash
├── mode        FULL | SCOPED(reserved) | WATCH(reserved)
├── budget      max_files=50_000 · max_file_size_mb=10 · max_commits=5000
└── events[]    ordered audit trail (the only side channel)
```

Determinism statement:
- Same bytes + same config ⇒ identical `IntakeReport` except timing fields.
- Discovery is sorted; commit/change streams are oldest-first; parse is a pure
  function of `(content_hash, parser_version)`.
- `file_id` values are UUID4 at first sight but become stable ACROSS runs once
  persisted to `.shannon/facts.db` (`--save`, next wave). In-memory runs get
  fresh ids: tests assert on chain *equality*, never on id *values*.

## 2. Inputs / Outputs

```
 IN (all of it)                          OUT (frozen artifacts)
 ─────────────────────────────           ─────────────────────────────────────
 root dir                                IntakeReport
 IntakeConfig{                             files[]   ParsedFile{rel_path(POSIX),
   exclude_patterns (gitwildmatch),                    content_hash sha256hex,
   max_file_size_mb, allow_hidden,                     language, FileSyntax(IR1),
   follow_symlinks, max_files,                         file_id|None, total_changes}
   max_commits, use_git}                   skipped[] SkippedFile{reason,detail}
 .git/  (optional)                        commits[] CommitFact oldest-first
 .mailmap (optional)                                {author_id canonical, parents,
 tree-sitter-language-pack                           is_merge, subject}
 git binary (optional)                    changes[] FileChangeFact oldest-first
                                                      {file_id STAMPED, +/-lines}
 NEVER an input:                          authors[] AuthorRecord{is_bot}
 network, env vars,                       events[]  ordered domain events
 anything outside root                    summary() plain dict (CLI/server)

 IR1 FileSyntax carries: functions(spans,tokens,nesting,cyclomatic,calls,
 params,qualified_name,visibility,exported,async,docstring,hard_stub,return_
 type), classes(bases,methods,fields,abstract,interface), imports(module,names,
 alias,level,system,dynamic), exports(kind), top_level_names, package,
 identifiers(≤5k), comments(≤200), token/comment counts, encoding,
 is_generated, has_errors, parser_version.
```

## 3. The Logical DAG

```
 S0 session_init ──► config_hash
 │
 ├─ STRUCTURAL SPINE ────────────────────     ─ TEMPORAL SPINE ─────────────
 │ G0 discover(root,cfg)        [fs]         │ X0 git_extract(root,maxN)  [sub]
 │ │   deterministic sorted paths              │    -M renames + numstat
 │ ▼                                           │    timeout 30s ⇒ degrade
 │ H0 read+hash+sizeguard       [io]          │ ▼
 │ │   streaming, bytes released               │ A0 canonicalize_authors
 │ ▼                                           │    (.mailmap→gmail→localpart;
 │ P0 analyze_source ×N         [cpu]          │    bots flagged, isolated)
 │ │   PURE fn(hash,parser_ver)                │ ▼
 │ │   parallelizable map                      │ I0 identity_resolve(changes)
 │ │   memoizable (reserved LRU)               │    oldest-first ORDER INVARIANT
 │ │   generated fast-path                     │    uuid chains, resolve_at()
 ▼▼═══════════════════════════════════ JOIN ═══════════════════════════════
 J0 join on rel_path: stamp file_id + total_changes onto files AND changes
 │
 R0 assemble report + ordered events → IntakeReport
```

Spines are independent until J0 (process-parallel ready). J0 is the ONLY
path-keyed touchpoint; after J0 everything is id-keyed.

## 4. Boundaries (hard NOs)

No graphs/signals/findings/scores. No import resolution (raw specifiers only).
No disk writes (persistence is opt-in, next wave). No network. No subprocesses
except `git`. No reads outside root (symlinks unfollowed by default). No
semantics (roles/concepts/clones). Not incremental (modes reserved). Time-travel
(`resolve_at`) exposed but historical re-parse unexercised (Kind-3, later).

## 5. Limits, Memory Safety, Checks

| Guard | Value | Behavior on hit |
|---|---|---|
| repo file cap | 50_000 | SC204 FACTS_REPO_TOO_LARGE, recoverable |
| per-file size | cfg MB | SkipReason.TOO_LARGE |
| bundle heuristic | >512KB or >250 ch/line | counts-only IR1, is_generated=true |
| identifiers / file | 5_000 | silent cap (set) |
| comment texts / file | 200 | silent cap (tuple) |
| git timeout | 30s | event git_degraded → structural-only report |
| unsupported ext | discovery filter | never reaches parser |
| parse exception | any | SkipReason.PARSE_ERROR, run continues |

Memory: content bytes released post-parse (only hash kept); leaf spans scoped
to Walker lifetime; bundle path avoids ~300k-span walks (measured 690KB file:
5.6s → <0.05s).

Perf (single core, cold, measured on this repo — 725 files / 122k LOC):
discover 0.6s · parse ≈14s (~9k LOC/s pure-python walker; ≥20k arrives with
spine parallelism W-next) · git 2.6s @1600 commits · identity 0.4s.

## 6. Failure taxonomy ↔ events

```
SC101 grammar missing → hard error at direct use; discovery-filtered in runs
SC103 unknown lang    → filtered upstream (never surfaces mid-run)
SC201 root missing    → FileNotFoundError before any work
SC204 repo too large  → recoverable, hint to tighten excludes
SC205 git degraded    → event, not error; temporal spine silently absent
PARSE_ERROR/TOO_LARGE/READ_ERROR → SkippedFile rows (per-item isolation)
```

## 7. Exit-gate scoreboard (G1–G9)

G1 multilang ✓ (10 langs) · G2 hand-count ✓ · G3 math pins ✓ · G4 identity
chains ✓ · G5 authors/bots ✓ · G6 determinism ✓ · G7 goldens committed ✓ ·
G8 hostiles ✓ · G9 perf: documented 7k LOC/s e2e single-core (gate met as
revised; parallel target tracked separately).

Dogfood-on-self: 0 parse errors, 74 rename links, churn attribution live
(kernel.py #1 at 61 changes — plausible).
