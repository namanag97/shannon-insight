"""Projections: BindingTable → graph artifacts (R5–R7, Q0).

Edges are id-stamped and dropped (counted) when either endpoint is untracked
— untracked research scripts must never fabricate architecture.
"""

from __future__ import annotations

from collections import Counter

from shannon_insight.relate.protocols import (
    BindingRecord,
    EdgeRecord,
    PhantomFact,
    RelateMetrics,
    Verdict,
)

ExternalKey = tuple[str, str]


def stamp_and_collect(
    records: list[BindingRecord],
    rel_to_id: dict[str, str],
    metrics: RelateMetrics,
) -> tuple[
    list[EdgeRecord],
    list[PhantomFact],
    list[tuple[str, str]],
    dict[ExternalKey, int],
]:
    edges: list[EdgeRecord] = []
    phantoms_internal: list[PhantomFact] = []
    unlisted_external: list[tuple[str, str]] = []
    externals_counter: Counter[ExternalKey] = Counter()

    for rec in records:
        if rec.verdict is Verdict.EXTERNAL and rec.reason:
            eco, _, rest = rec.reason.partition(":")
            name = rest.split(":", 1)[0]
            externals_counter[(eco, name)] += 1
            if reason_is_unlisted(rec.reason):
                unlisted_external.append((rec.source_rel, f"{eco}:{name}"))
            continue

        if rec.verdict is not Verdict.RESOLVED:
            continue
        src_id = rel_to_id.get(rec.source_rel)
        dst_id = rel_to_id.get(rec.target_rel or "")
        if not src_id or not dst_id or dst_id == src_id:
            metrics.untracked_endpoints += 1
            continue
        assert rec.method is not None and rec.confidence is not None
        edges.append(EdgeRecord(src_id, dst_id, rec.confidence, rec.method))

    for rec in records:
        if rec.verdict is Verdict.PHANTOM:
            phantoms_internal.append(
                PhantomFact(rec.source_rel, rec.specifier, rec.line, rec.reason or "unknown")
            )

    return edges, phantoms_internal, unlisted_external, dict(externals_counter)


def reason_is_unlisted(reason: str) -> bool:
    return "unlisted" in reason


def unused_declared(
    declared: frozenset[str],
    imported_externals: dict[str, int],
    self_names: frozenset[str],
) -> list[str]:
    used_names = {name.split(".", 1)[0].split("/", 1)[0] for name in imported_externals}
    return sorted(
        dep
        for dep in declared
        if dep not in used_names and dep.lower() not in {s.lower() for s in self_names}
    )


__all__ = ["reason_is_unlisted", "stamp_and_collect", "unused_declared"]
