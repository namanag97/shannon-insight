"""Set-algebra facts: the first cross-layer truth (seam ④).

hidden  = CoChange∖Import   (behavioral coupling without static edge)
dead    = Import∖CoChange   (static edge without shared behavior)
conway  = Import×¬Authors   (structural coupling, disjoint owners)

All three are suppressed where the coupling is EXPECTED (test↔source twins,
__init__ glue, same-directory config) — expected pairs stay in the graph,
they just never become facts.
"""

from __future__ import annotations

from dataclasses import dataclass

from shannon_insight.facts.classify import FileClass
from shannon_insight.graphs.cochange_matrix import PairDynamics
from shannon_insight.syntax.models import FileSyntax


@dataclass(frozen=True)
class PairFact:
    src_file_id: str
    dst_file_id: str
    evidence: dict[str, float]


@dataclass(frozen=True)
class PairThresholds:
    lift_min: float = 2.0
    confidence_min: float = 0.5
    min_co_commits: int = 3
    dead_min_changes: int = 50
    conway_jaccard_max: float = 0.3
    bulk_files: int = 50


def _stem(name: str) -> str:
    n = name.lower()
    for prefix in ("test_",):
        if n.startswith(prefix):
            n = n[len(prefix) :]
    for suffix in ("_test", ".test", ".spec", "_spec"):
        for ext in (
            ".py",
            ".go",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".rs",
            ".rb",
            ".java",
            ".cc",
            ".cpp",
            "",
        ):
            if n.endswith(suffix + ext):
                n = n[: -len(suffix + ext)]
                break
    return n


def build_twins(
    files: dict[str, FileSyntax],
    classes: dict[str, FileClass],
    rel_to_id: dict[str, str],
) -> dict[str, set[str]]:
    sources: dict[str, set[str]] = {}
    for rel, cls in classes.items():
        fid = rel_to_id.get(rel)
        if not fid or cls is not FileClass.SOURCE:
            continue
        stem = _stem(rel.rpartition("/")[2])
        sources.setdefault(stem, set()).add(fid)

    twins: dict[str, set[str]] = {}
    for rel, cls in classes.items():
        if cls is not FileClass.TEST:
            continue
        fid = rel_to_id.get(rel)
        if not fid:
            continue
        stem = _stem(rel.rpartition("/")[2])
        for target in sources.get(stem, ()):
            if target != fid:
                twins.setdefault(fid, set()).add(target)
                twins.setdefault(target, set()).add(fid)
    return twins


def is_expected_pair(
    a_id: str,
    b_id: str,
    a_rel: str,
    b_rel: str,
    a_syn: FileSyntax,
    b_syn: FileSyntax,
    classes: dict[str, FileClass],
    twins: dict[str, set[str]],
) -> bool:
    if b_id in twins.get(a_id, ()):
        return True
    a_name = a_rel.rpartition("/")[2].lower()
    b_name = b_rel.rpartition("/")[2].lower()
    if a_name in ("__init__.py", "index.ts", "index.js", "__init__.rb") or b_name in (
        "__init__.py",
        "index.ts",
        "index.js",
    ):
        return True
    if classes.get(a_rel) in (FileClass.CONFIG, FileClass.DATA) or classes.get(b_rel) in (
        FileClass.CONFIG,
        FileClass.DATA,
    ):
        return True
    del a_syn, b_syn
    return False


def hidden_facts(
    dynamics: dict[tuple[str, str], PairDynamics],
    edge_pairs: set[tuple[str, str]],
    files: dict[str, FileSyntax],
    classes: dict[str, FileClass],
    rel_to_id: dict[str, str],
    id_to_rel: dict[str, str],
    thresholds: PairThresholds,
) -> list[PairFact]:
    twins = build_twins(files, classes, rel_to_id)
    out: list[PairFact] = []
    for (a, b), dyn in sorted(dynamics.items()):
        if dyn.lift < thresholds.lift_min or dyn.confidence < thresholds.confidence_min:
            continue
        if dyn.co_commits < thresholds.min_co_commits:
            continue
        pair = (min(a, b), max(a, b))
        if pair in edge_pairs:
            continue
        a_rel, b_rel = id_to_rel.get(a, ""), id_to_rel.get(b, "")
        a_syn, b_syn = files.get(a_rel), files.get(b_rel)
        if a_syn is None or b_syn is None:
            continue
        if is_expected_pair(a, b, a_rel, b_rel, a_syn, b_syn, classes, twins):
            continue
        out.append(
            PairFact(
                src_file_id=a,
                dst_file_id=b,
                evidence={
                    "lift": dyn.lift,
                    "confidence": dyn.confidence,
                    "co_commits": float(dyn.co_commits),
                },
            )
        )
    return out


def dead_facts(
    edges: list[tuple[str, str]],
    dynamics_keys: set[tuple[str, str]],
    changes_per_id: dict[str, int],
    thresholds: PairThresholds,
) -> list[PairFact]:
    out: list[PairFact] = []
    seen: set[tuple[str, str]] = set()
    for src, dst in edges:
        pair = (min(src, dst), max(src, dst))
        if pair in seen or pair in dynamics_keys:
            continue
        if changes_per_id.get(src, 0) < thresholds.dead_min_changes:
            continue
        if changes_per_id.get(dst, 0) < thresholds.dead_min_changes:
            continue
        seen.add(pair)
        out.append(
            PairFact(
                src,
                dst,
                {
                    "changes_src": float(changes_per_id[src]),
                    "changes_dst": float(changes_per_id[dst]),
                },
            )
        )
    return out


def conway_facts(
    edges: list[tuple[str, str]],
    authors_per_id: dict[str, set[str]],
    jaccard_max: float = 0.3,
) -> list[PairFact]:
    out: list[PairFact] = []
    seen: set[tuple[str, str]] = set()
    for src, dst in edges:
        pair = (min(src, dst), max(src, dst))
        if pair in seen:
            continue
        seen.add(pair)
        a_authors = authors_per_id.get(src, set())
        b_authors = authors_per_id.get(dst, set())
        union = a_authors | b_authors
        jac = len(a_authors & b_authors) / len(union) if union else 1.0
        if jac <= jaccard_max:
            out.append(PairFact(src, dst, {"author_jaccard": round(jac, 4)}))
    return out


def unreachable_from_entry(
    entry_ids: set[str], adjacency: dict[str, set[str]], all_ids: set[str]
) -> set[str]:
    reachable: set[str] = set(entry_ids)
    frontier = list(entry_ids)
    while frontier:
        node = frontier.pop()
        for nxt in adjacency.get(node, ()):  # forward reachability
            if nxt not in reachable:
                reachable.add(nxt)
                frontier.append(nxt)
    return all_ids - reachable


__all__ = [
    "PairFact",
    "PairThresholds",
    "build_twins",
    "conway_facts",
    "dead_facts",
    "hidden_facts",
    "is_expected_pair",
    "unreachable_from_entry",
]
