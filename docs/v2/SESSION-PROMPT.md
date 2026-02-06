# Shannon Insight v2 — Session Prompt

Copy and paste this at the start of each implementation session.

---

## Prompt

```
I'm implementing Shannon Insight v2. This is enterprise-grade production software, not an MVP.

## Current State
- v1 working CLI on PyPI (shannon-codebase-insight)
- v2 specs complete in docs/v2/ (~15,000 lines, 59 files)
- Zero users — can break APIs freely

## Before You Code
READ THESE IN ORDER:
1. docs/v2/FAILURE-MODES.md — 22 ways implementation fails silently
2. docs/v2/AGENT-IMPLEMENTATION-PROMPT.md — Master implementation guide
3. docs/v2/ORCHESTRATION-VERIFICATION.md — Pipeline verification

## Key Rules
- Use Signal enum, never string signal names
- Always guard `instability is None` before computing D
- Fusion order: raw_risk BEFORE percentiles
- Check polarity in signals.md (some are HIGH=GOOD)
- ABSOLUTE tier has no percentiles — use absolute thresholds
- Test-first: write test before implementation
- Run `make all` after every change

## Phase Order
0. Infrastructure (Signal enum, Slot[T], topo-sort, validation)
1. Tree-sitter Python parsing
2. Semantics (roles, concepts)
3. Graph enrichment (depth, orphans, clones)
4. Architecture (modules, layers, Martin metrics)
5. Signal fusion (percentiles, composites, Laplacian)
6. Finders (15 new)
7. Persistence (TensorSnapshot)

## Git
- Branch: feature/v2-phase-N
- Commit prefix: [Phase N]
- Never force push, never skip tests

## Current Task
[FILL IN: What phase/task you're working on]

## Questions
Ask if ANYTHING is unclear. Don't guess. The specs are precise.
```

---

## Quick Reference

| Need | File |
|------|------|
| What could fail | `docs/v2/FAILURE-MODES.md` |
| Full implementation guide | `docs/v2/AGENT-IMPLEMENTATION-PROMPT.md` |
| Pipeline verification | `docs/v2/ORCHESTRATION-VERIFICATION.md` |
| All 62 signals | `docs/v2/registry/signals.md` |
| All 22 finders | `docs/v2/registry/finders.md` |
| Composite formulas | `docs/v2/registry/composites.md` |
| Signal data flows | `docs/v2/SIGNAL-REHEARSAL.md` |
| Finder data flows | `docs/v2/FINDER-REHEARSAL.md` |
| Phase N details | `docs/v2/phases/phase-N-*.md` |
| Test fixtures | `tests/fixtures/` |

## Checkpoint Commands

```bash
make all          # Must pass before commit
make test         # Run tests
make check        # Type check + lint
pytest tests/path/to/test.py -v  # Single test file
```
