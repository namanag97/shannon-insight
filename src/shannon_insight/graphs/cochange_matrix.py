"""PairDynamics from the id-stamped change stream (Phase-1 handoff).

Pure lift/confidence computation over file_id pairs — the behavioral layer
that set-algebra disagrees against. Bulk commits (>bulk_files touched) are
excluded: they are merge/squash artifacts, not coupling evidence.
"""

from __future__ import annotations

from dataclasses import dataclass

from shannon_insight.facts.models import FileChangeFact


@dataclass(frozen=True)
class PairDynamics:
    lift: float
    confidence: float
    co_commits: int


def build_pair_dynamics(
    changes: list[FileChangeFact],
    bulk_files: int = 50,
) -> dict[tuple[str, str], PairDynamics]:
    by_commit: dict[str, set[str]] = {}
    for chg in changes:
        fid = chg.file_id
        if fid:
            by_commit.setdefault(chg.commit_hash, set()).add(fid)

    marginals: dict[str, int] = {}
    joint: dict[tuple[str, str], int] = {}
    n_commits = 0
    for _hash, ids in by_commit.items():
        if len(ids) > bulk_files or not ids:
            continue
        ordered = sorted(ids)
        n_commits += 1
        for fid in ordered:
            marginals[fid] = marginals.get(fid, 0) + 1
        for i, a in enumerate(ordered):
            for b in ordered[i + 1:]:
                key = (a, b) if a < b else (b, a)
                joint[key] = joint.get(key, 0) + 1

    out: dict[tuple[str, str], PairDynamics] = {}
    denom = max(n_commits, 1)
    for (a, b), co in joint.items():
        pa = marginals.get(a, 0) / denom
        pb = marginals.get(b, 0) / denom
        if pa <= 0 or pb <= 0:
            continue
        pab = co / denom
        lift = pab / (pa * pb)
        conf_a = co / max(marginals.get(a, 1), 1)
        conf_b = co / max(marginals.get(b, 1), 1)
        out[(a, b)] = PairDynamics(lift=round(lift, 4), confidence=round(min(conf_a, conf_b), 4), co_commits=co)
    return out


__all__ = ["PairDynamics", "build_pair_dynamics"]
