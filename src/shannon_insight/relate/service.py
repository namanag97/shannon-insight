"""RELATE service: R0→Q0 orchestration producing the published artifacts."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from shannon_insight.facts.classify import FileClass
from shannon_insight.facts.models import CommitFact, FileChangeFact
from shannon_insight.graphs.cochange_matrix import PairDynamics, build_pair_dynamics
from shannon_insight.relate.index import ModuleIndex
from shannon_insight.relate.kernel import BindingKernel
from shannon_insight.relate.manifests import ManifestFacts, read_manifests
from shannon_insight.relate.pairs import (
    PairFact,
    PairThresholds,
    conway_facts,
    dead_facts,
    hidden_facts,
    unreachable_from_entry,
)
from shannon_insight.relate.projections import stamp_and_collect
from shannon_insight.relate.protocols import (
    BindingRecord,
    EdgeRecord,
    ExternalPkg,
    PhantomFact,
    RelateMetrics,
    Verdict,
)
from shannon_insight.syntax.models import FileSyntax


@dataclass(frozen=True)
class RelateConfig:
    thresholds: PairThresholds = field(default_factory=PairThresholds)
    use_manifests: bool = True


@dataclass(frozen=True)
class RelateInputs:
    """The exact Phase-1 handoff slice RELATE may consume. Nothing else."""

    root: Path
    files: dict[str, FileSyntax]
    rel_to_id: dict[str, str]
    changes: list[FileChangeFact]
    commits: list[CommitFact]
    classes: dict[str, FileClass]


@dataclass
class RelateResult:
    binding_records: list[BindingRecord] = field(default_factory=list)
    edges: list[EdgeRecord] = field(default_factory=list)
    phantoms_internal: list[PhantomFact] = field(default_factory=list)
    unlisted_external: list[tuple[str, str]] = field(default_factory=list)
    unused_declared_deps: list[str] = field(default_factory=list)
    externals: list[ExternalPkg] = field(default_factory=list)
    unreachable: set[str] = field(default_factory=set)
    hidden_pairs: list[PairFact] = field(default_factory=list)
    dead_pairs: list[PairFact] = field(default_factory=list)
    conway_pairs: list[PairFact] = field(default_factory=list)
    metrics: RelateMetrics = field(default_factory=RelateMetrics)

    def summary(self) -> dict[str, object]:
        return {
            "specifiers": self.metrics.total_specifiers,
            "edges": len(self.edges),
            "phantoms_internal": len(self.phantoms_internal),
            "unlisted_external": len(self.unlisted_external),
            "unused_declared": len(self.unused_declared_deps),
            "unreachable_files": len(self.unreachable),
            "hidden_pairs": len(self.hidden_pairs),
            "dead_pairs": len(self.dead_pairs),
            "conway_pairs": len(self.conway_pairs),
            "resolution_rate": self.metrics.resolution_rate,
        }


def _entry_ids(files: dict[str, FileSyntax], rel_to_id: dict[str, str]) -> set[str]:
    out: set[str] = set()
    for rel, syn in files.items():
        is_entry = (
            syn.has_main_guard
            or rel.endswith("__main__.py")
            or syn.package == "main"
            or (rel.startswith("scripts/") and not syn.is_generated)
        )
        if is_entry:
            fid = rel_to_id.get(rel)
            if fid:
                out.add(fid)
    return out


def _authors_per_id(
    changes: list[FileChangeFact], commits: list[CommitFact]
) -> dict[str, set[str]]:
    author_of_commit = {c.commit_hash: c.author_id for c in commits}
    out: dict[str, set[str]] = defaultdict(set)
    for chg in changes:
        if chg.file_id and chg.commit_hash in author_of_commit:
            out[chg.file_id].add(author_of_commit[chg.commit_hash])
    return dict(out)


def _changes_per_id(changes: list[FileChangeFact]) -> dict[str, int]:
    out: dict[str, int] = {}
    for chg in changes:
        if chg.file_id:
            out[chg.file_id] = out.get(chg.file_id, 0) + 1
    return out


def _head_of_external(reason: str) -> str:
    body = reason.partition(":")[2]
    name = body.split(":", 1)[0]
    return name.split("/", 1)[0].split(".", 1)[0].lower()


def _used_external_heads(records: list[BindingRecord], ecosystems: set[str]) -> dict[str, set[str]]:
    used: dict[str, set[str]] = defaultdict(set)
    for rec in records:
        if rec.verdict is not Verdict.EXTERNAL or not rec.reason:
            continue
        eco = rec.reason.partition(":")[0]
        if eco in ecosystems:
            used[eco].add(_head_of_external(rec.reason))
    return used


class RelateService:
    def run(self, inputs: RelateInputs, cfg: RelateConfig | None = None) -> RelateResult:
        cfg = cfg or RelateConfig()
        result = RelateResult()

        mf = read_manifests(inputs.root) if cfg.use_manifests else ManifestFacts()
        index = ModuleIndex(inputs.files)
        kernel = BindingKernel(inputs.root, inputs.files, index, mf)

        records: list[BindingRecord] = []
        for rel in sorted(inputs.files):
            syntax = inputs.files[rel]
            table = kernel._table_for(syntax.language)  # noqa: SLF001 - same-package engine use
            for imp in syntax.imports:
                rec = _stamp_record(kernel._bind_one(rel, table, imp), table)
                records.append(rec)
        result.binding_records = records
        result.metrics = kernel.metrics

        edges, phantoms_internal, unlisted, external_counter = stamp_and_collect(
            records, inputs.rel_to_id, result.metrics
        )
        result.edges = edges
        result.phantoms_internal = phantoms_internal
        result.unlisted_external = unlisted

        for (eco, name), count in sorted(external_counter.items()):
            result.externals.append(ExternalPkg(eco, name, count))

        used = _used_external_heads(records, {"npm", "pypi", "gems", "crates"})
        unused_all: list[str] = []
        for eco, names in mf.declared.items():
            used_heads = used.get(eco, set())
            unused_all.extend(
                f"{eco}:{dep}"
                for dep in sorted(names)
                if dep.lower() not in used_heads and dep.lower() not in mf.self_names
            )
        result.unused_declared_deps = unused_all

        dynamics: dict[tuple[str, str], PairDynamics] = build_pair_dynamics(
            inputs.changes, cfg.thresholds.bulk_files
        )
        id_to_rel = {v: k for k, v in inputs.rel_to_id.items()}
        edge_pairs = {
            (min(e.src_file_id, e.dst_file_id), max(e.src_file_id, e.dst_file_id)) for e in edges
        }

        result.hidden_pairs = hidden_facts(
            dynamics,
            edge_pairs,
            inputs.files,
            inputs.classes,
            inputs.rel_to_id,
            id_to_rel,
            cfg.thresholds,
        )
        result.dead_pairs = dead_facts(
            [(e.src_file_id, e.dst_file_id) for e in edges],
            set(dynamics.keys()),
            _changes_per_id(inputs.changes),
            cfg.thresholds,
        )
        result.conway_pairs = conway_facts(
            [(e.src_file_id, e.dst_file_id) for e in edges],
            _authors_per_id(inputs.changes, inputs.commits),
            cfg.thresholds.conway_jaccard_max,
        )

        adjacency: dict[str, set[str]] = {}
        for e in edges:
            adjacency.setdefault(e.src_file_id, set()).add(e.dst_file_id)
        entries = _entry_ids(inputs.files, inputs.rel_to_id)
        result.unreachable = unreachable_from_entry(
            entries, adjacency, set(inputs.rel_to_id.values())
        )

        return result


__all__ = ["RelateConfig", "RelateInputs", "RelateResult", "RelateService"]


def _stamp_record(rec: BindingRecord, table) -> BindingRecord:
    from shannon_insight.relate.kernel import _stamp_language

    return _stamp_language(rec, table)
