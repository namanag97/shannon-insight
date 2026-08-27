# Query, compute and kernel universe

This corpus closes the compiler boundary between a typed analytical operation and executable work.
It is provider-neutral and excludes LLM, generative and agentic semantics.

```text
declared query / analytical operation
             |
             v
language syntax -> binding -> typed semantic expression
             |                    |
             |                    v
             +------------> logical operator graph
                                   |
                     equivalence-preserving rewrites
                                   |
                    statistics + cardinality + cost
                                   |
                                   v
                            physical plan
                                   |
                  algorithm + kernel + layout choices
                                   |
             target + provider + resource capability binding
                                   |
                                   v
           execution -> diagnostics -> result and resource receipts
```

## Five identities that must never be collapsed

| Identity | Owns | Does not own |
|---|---|---|
| semantic operation | result meaning, types, null/missing, ordering, time and exactness | implementation algorithm |
| algorithm | method and complexity family | compiled code or provider identity |
| kernel | executable contract over concrete layouts and targets | user-facing query meaning |
| engine/provider | offered operator, kernel and runtime capabilities with scoped evidence | canonical semantics |
| target | ISA/device/runtime/resource constraints | operation selection policy |

`join` is therefore not one thing. An inner equi-join is a logical operation; hash join and merge
join are algorithms; a SIMD hash-probe loop is a kernel; DataFusion or Velox is an implementation;
and `x86_64+AVX2` is a target. Compiler bindings must retain all five identities.

## Compression boundary

Compression is represented at three boundaries:

1. **semantic encoding** — a reversible or explicitly lossy mapping with equality, ordering and
   missing-value laws;
2. **codec kernel** — encode/decode implementation over a concrete page, block or stream layout;
3. **physical policy** — choose codec, level, block size, dictionary policy and placement from
   workload, target, latency, memory, energy, network and random-access requirements.

A codec may not be selected by name alone. Its offer must state logical-type coverage,
losslessness, framing, splittability, random access, pushdown compatibility, memory bounds,
target support, determinism and fallback behavior.

## Exactness and reproducibility

The corpus separates four guarantees:

```text
semantic exactness     same mathematical/relational result under declared semantics
value tolerance        result within a declared absolute/relative/ULP/error bound
run determinism        same observable result for repeated runs on one qualified target
cross-target bitwise   identical bits across qualified targets and parallelism settings
```

The compiler must not infer the strongest guarantee from a weaker one. Floating-point reduction
order, collation, time zone database edition, random seeds, approximate sketches, parallel race
order and UDF effects are explicit binding inputs.

## Fallback and refusal law

Fallback is legal only when the replacement is proven semantically equivalent or when the
degradation was declared by the analytical intent and is carried in the result receipt. Otherwise
the compiler refuses.

```text
unsupported logical operation      -> refuse or bind an equivalent decomposition with proof
unsupported kernel on target        -> choose another qualified kernel/target
insufficient memory                 -> proven spill/external algorithm or refuse
pushdown semantic mismatch          -> execute locally; never silently push down
approximation not authorized        -> exact execution or refuse
numeric reproducibility unavailable -> weaker declared posture or refuse
cancel not safely resumable         -> terminate with explicit partial-effect receipt
```

## Artifacts

- `metamodel.json` — closed distinctions, stages and laws.
- `context-candidates.jsonl` — bounded-context hypotheses for ownership adjudication.
- `logical-operators.jsonl` — provider-neutral semantic operators.
- `kernel-contracts.jsonl` — algorithm/kernel contracts over concrete layouts and targets.
- `provider-capabilities.jsonl` and `target-profiles.jsonl` — offers and target constraints.
- `compiler-mappings.jsonl` — requirement/offer matching and refusal patterns.
- `library-boundaries.jsonl` — pure and runtime library contribution boundaries.
- `sources.jsonl` — primary standards, papers and official implementation evidence.
- `innovations.jsonl` — non-LLM advances from 2021–2026.
- `gaps.jsonl` — explicit unresolved questions.
- `schema/` — record schemas.
- `validate_corpus.py` — structural, referential and constitutional checks.

Run:

```bash
python3 research/domain_atlas/universes/query_compute_kernels/build_corpus.py
python3 research/domain_atlas/universes/query_compute_kernels/validate_corpus.py
```

All records are research candidates unless separately qualified. Enumeration is not proof of
completeness; unknown semantics and missing offers remain typed compiler gaps.
