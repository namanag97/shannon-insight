# SAN GPT Pro research dispatch kit

This is the portable control package for the current SAN domain-program research.
It preserves the program intent, the active three-session dispatch, the downstream
DAG, and a task ledger that follows every candidate bounded context from research
through a proved compiler/runtime composition.

## Send now

Open three independent GPT Pro sessions. Send one session directory to each session:

| Session | Directory | Expected return |
|---|---|---|
| N1 | `sessions/N1-atlas-rebase/` | Globally researched non-data domain atlas v0.2.0 release candidate |
| S1 | `sessions/S1-semantic-contract/` | Independent sovereign semantic-domain definition contract candidate |
| S2 | `sessions/S2-library-compiler-contract/` | Independent library, composition, and compiler contract candidate |

Each directory contains a self-contained `PROMPT.md`, `ATTACHMENT-MANIFEST.json`,
and only the input files intended for that session. Do not cross-attach another
session's prompt or candidate output. Independence is deliberate.

The `send/` directory contains one upload ZIP per session after running:

```bash
python3 research/SAN-GPT-PRO-DISPATCH-KIT-2026-08-13/build_dispatch.py
```

## When the three sessions return

Do not begin mass domain or library generation. Put the returned archives in the
return directories named in `program/PROGRAM-DAG.md`, verify their hashes and
internal validation, then run the next ready gates in the task ledger:

1. independent acceptance audit of N1;
2. independent adjudication of S1 and S2 after the atlas is accepted;
3. generation of the sovereign-domain work-package registry;
4. representative Domain Forges;
5. Library Forges only for accepted semantic owners and explicit technical/effect roles;
6. compiler, lowering, runtime, and mixed-vertical proofs.

## Authority posture

Every included SAN artifact is evidence or a candidate unless its own manifest says
otherwise. Passing a bundled validator proves only what that validator actually
checks. The current non-data atlas is a research candidate, not a canonical domain
map. The global registry is a candidate registry, not proof that its entries are
implemented or compiler-admissible.

## Durable program files

- `BASE-RESEARCH-CONSTITUTION.md` — common intent and epistemic rules.
- `program/PROGRAM-DAG.md` — concise authoritative sequence and gates.
- `program/ARTIFACT-CONTRACT.md` — artifact kinds and non-equivalence rules.
- `planner/task-ledger.schema.json` — machine-readable task-state contract.
- `planner/program-tasks.jsonl` — program-level gates and future sessions.
- `planner/context-tasks.bootstrap.jsonl` — provisional tasks for all 275 v0.1 atlas contexts.
- `planner/README.md` — how the ledger is rebased after N1.
- `program/future-prompts/` — outcome-focused prompt templates for later DAG nodes.

## Scope

The program targets reusable software semantics and mechanisms needed to assemble
enterprise applications and data/analytics systems. It studies regulated or legal
domain semantics only where software must represent or enforce them; it does not
claim to solve legal policy itself. It separates horizontal reusable ownership from
industry profiles and from product/application composition.

