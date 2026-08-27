"""Universal binding kernel (seam ② executor + seam ③ producer).

One algorithm, six data tables. Per Stack-Graphs discipline: candidate
generation for a file reads ONLY that file's IR1 plus the shared indexes —
never another file's internals. Verdicts are total: every specifier site
yields exactly one BindingRecord.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from shannon_insight.relate.index import ModuleIndex, normalize_base
from shannon_insight.relate.manifests import ManifestFacts
from shannon_insight.relate.protocols import (
    METHOD_RANK,
    BindMethod,
    BindingRecord,
    Candidate,
    Confidence,
    RelateMetrics,
    Verdict,
)
from shannon_insight.relate.tables import FamilyTable, table_for_language
from shannon_insight.syntax.models import FileSyntax, ImportDecl


class BindingKernel:
    def __init__(
        self,
        root: Path,
        files: dict[str, FileSyntax],
        index: ModuleIndex,
        mf: ManifestFacts,
    ) -> None:
        self.root = root
        self.files = files
        self.index = index
        self.mf = mf
        self.metrics = RelateMetrics()
        self._py_roots = self._probe_python_roots()
        self._rust_roots = self._probe_rust_roots()
        self._java_root = self._infer_java_root(files)
        self._include_dirs = self._collect_include_dirs()

    def _table_for(self, language: str) -> FamilyTable:
        return table_for_language(language)

    # ── index-query primitives (the ONLY ways kernels touch indexes) ──

    def _file_candidates(
        self, base: str, t: FamilyTable | tuple[str, ...], root: str = ""
    ) -> list[Candidate]:
        templates = t.file_templates if isinstance(t, FamilyTable) else t
        out: list[Candidate] = []
        for tmpl in templates:
            rel_path = tmpl.format(base=normalize_base(root, base))
            tail_is_index = tmpl.split("}", 1)[-1].startswith("/")
            if root and not tail_is_index:
                method, rank = BindMethod.ANCESTOR_WALK, METHOD_RANK[BindMethod.ANCESTOR_WALK]
            elif tail_is_index:
                method, rank = BindMethod.INDEX_PACKAGE, METHOD_RANK[BindMethod.INDEX_PACKAGE]
            else:
                method, rank = BindMethod.EXACT_FILE, METHOD_RANK[BindMethod.EXACT_FILE]
            out.append(Candidate(rel_path, method, rank))
        return out

    def _first_file(self, base: str, t: FamilyTable) -> Candidate | None:
        for cand in self._file_candidates(base, t):
            if self.index.has(cand.rel_path):
                return cand
        return None

    def _first_file_any(self, base: str, templates: tuple[str, ...]) -> str | None:
        for tmpl in templates:
            rel_path = tmpl.format(base=base)
            if self.index.has(rel_path):
                return rel_path
        return None

    def _alias_lookup(self, spec: str) -> str | None:
        best_key = ""
        best_vals: tuple[str, ...] = ()
        for key, vals in self.mf.tsconfig_paths.items():
            if key.endswith("*"):
                prefix = key[:-1]
                if spec.startswith(prefix) and len(prefix) > len(best_key):
                    best_key, best_vals = prefix, tuple(
                        v.replace("*", spec[len(prefix):]) for v in vals
                    )
            elif spec == key and len(key) > len(best_key):
                best_key, best_vals = key, vals
        for v in best_vals:
            if v:
                return normalize_base(v)
        return None

    def _casefold_rescue(
        self, rel: str, imp: ImportDecl, base: str, t: FamilyTable, roots: tuple[str, ...]
    ) -> BindingRecord | None:
        for root in roots:
            for tmpl in t.file_templates:
                rel_path = tmpl.format(base=normalize_base(root, base))
                folded = self.index.casefold_lookup(rel_path)
                if folded is not None:
                    return _resolved_c(rel, imp, folded,
                                       BindMethod.CASE_FOLD, Confidence.LOW)
        return None

    def _probe_python_roots(self) -> tuple[str, ...]:
        """'' plus dirs that structurally look like import roots.

        A dir qualifies when it directly holds *.py modules (flat project
        root / package parent) or is named 'src' with python anywhere below
        (src-layout). Ordered shallowest-first so general roots win ties.
        """
        direct_py: set[str] = set()
        src_hits: set[str] = set()
        for rel_path in self.files:
            if not rel_path.endswith(".py"):
                continue
            d = _parent(rel_path)
            direct_py.add(d)
            while d:
                seg = d.rpartition("/")[2]
                if seg == "src":
                    src_hits.add(d)
                d = d.rpartition("/")[0]
        roots = {""} | direct_py | src_hits
        return tuple(sorted(roots, key=lambda d: (d.count("/"), d)))

    def _probe_rust_roots(self) -> tuple[str, ...]:
        """'' plus every 'src' dir holding rust sources (crate-root convention)."""
        roots = {""}
        for rel_path in self.files:
            if not rel_path.endswith(".rs"):
                continue
            d = _parent(rel_path)
            while d:
                if d.rpartition("/")[2] == "src":
                    roots.add(d)
                d = d.rpartition("/")[0]
        return ("",) if len(roots) == 1 else ("", *sorted(roots - {""}, key=lambda x: (x.count("/"), x)))

    def _infer_java_root(self, files: dict[str, FileSyntax]) -> str | None:
        votes: Counter[str] = Counter()
        for rel, syn in files.items():
            if syn.language != "java" or not syn.package:
                continue
            d = _parent(rel)
            expected = syn.package.replace(".", "/")
            if d.endswith(expected):
                root = d[: -len(expected)].rstrip("/")
                votes[root] += 1
        return votes.most_common(1)[0][0] if votes else ""

    def _collect_include_dirs(self) -> tuple[str, ...]:
        return tuple(sorted(d for d in self.index.dirs if d.rpartition("/")[2] == "include"))

    def _crate_root_for(self, rel: str) -> str:
        best = ""
        for name, d in self.mf.workspaces.items():
            if self.mf.ws_kind.get(name) != "cargo" or not d:
                continue
            if rel.startswith(d + "/") and len(d) > len(best):
                best = d
        return best


    # ── pass-2 entry ──────────────────────────────────────────────────

    def bind_all(self) -> list[BindingRecord]:
        records: list[BindingRecord] = []
        for rel in sorted(self.files):
            syntax = self.files[rel]
            table = table_for_language(syntax.language)
            for imp in syntax.imports:
                records.append(_stamp_language(self._bind_one(rel, table, imp), table))
        return records

    def _bind_one(self, importer_rel: str, table: FamilyTable, imp: ImportDecl) -> BindingRecord:
        self.metrics.total_specifiers += 1
        record = self._dispatch(importer_rel, table, imp)
        if (
            record.verdict is Verdict.RESOLVED
            and imp.is_dynamic
            and record.confidence is Confidence.HIGH
        ):
            record = BindingRecord(
                source_rel=record.source_rel, specifier=record.specifier, line=record.line,
                language=record.language, is_dynamic=record.is_dynamic,
                verdict=record.verdict, target_rel=record.target_rel,
                target_file_id=record.target_file_id, method=record.method,
                confidence=Confidence.MEDIUM, ambiguous_with=record.ambiguous_with,
                reason=record.reason,
            )
        return _finalize_counters(record, self.metrics)

    # ── dispatch by family semantics ──────────────────────────────────

    def _dispatch(self, rel: str, t: FamilyTable, imp: ImportDecl) -> BindingRecord:
        spec = imp.module.strip()
        if not spec and not imp.names:
            return _record(rel, imp, Verdict.SKIPPED, reason="empty_specifier")

        if t.include_style and imp.is_system:
            return self._bind_system_include(rel, imp, spec)
        if t.relative_style == "dots":
            return self._bind_dots(rel, t, imp, spec)
        if t.relative_style == "slash":
            return self._bind_slash(rel, t, imp, spec)
        if t.relative_style == "crate":
            return self._bind_crate(rel, t, imp, spec)
        if t.family == "go":
            return self._bind_go(rel, t, imp, spec)
        if t.family == "jvm":
            return self._bind_jvm(rel, t, imp, spec)
        return self._bind_loadpath(rel, t, imp, spec)

    # ── python ────────────────────────────────────────────────────────

    def _bind_dots(self, rel: str, t: FamilyTable, imp: ImportDecl, spec: str) -> BindingRecord:
        head = spec.split(".")[0] if spec else ""
        if imp.level == 0 and head in t.stdlib:
            return _external(rel, imp, "pypi", head, note="stdlib")
        if imp.level > 0:
            ups = max(imp.level - 1, 0)
            base_dir = _up(_parent(rel), ups)
            base = normalize_base(base_dir, spec.replace(".", "/"))
        else:
            base = spec.replace(".", "/")

        streams_base: list[list[Candidate]] = []
        streams_names: list[list[Candidate]] = []
        for root in self._py_roots:
            streams_base.append(self._file_candidates(base, t, root=root))
            for nm in imp.names:
                if nm and nm != "*":
                    streams_names.append(
                        self._file_candidates(normalize_base(base, nm), t, root=root)
                    )
        # python `from pkg import name` prefers the submodule file over the
        # package __init__ attr — names are tried as their own ladder pass
        hit, others = _pick(streams_names, self.index)
        if hit is None:
            hit, others = _pick(streams_base, self.index)
        if hit is not None:
            return _resolved(rel, imp, hit)
        fold = self._casefold_rescue(rel, imp, base, t, self._py_roots)
        if fold is not None:
            return fold
        declared = head.lower() in self.mf.declared.get("pypi", frozenset())
        if declared or (head in self.mf.self_names):
            return _external(rel, imp, "pypi", head)
        return _phantom(rel, imp, f"unresolved_python:{spec or '.'}")

    # ── node ──────────────────────────────────────────────────────────

    def _bind_slash(self, rel: str, t: FamilyTable, imp: ImportDecl, spec: str) -> BindingRecord:
        first = spec.split("/")[0]
        tilde_alias = spec.startswith("@/") or spec.startswith("~/")
        if not spec.startswith("."):
            if not tilde_alias and (first in t.stdlib or spec in t.stdlib):
                return _external(rel, imp, "npm", first, note="builtin")
            alias_hit = self._alias_lookup(spec)
            if alias_hit is not None:
                cand = self._first_file(alias_hit, t)
                if cand is not None:
                    return _resolved_c(rel, imp, cand.rel_path,
                                       BindMethod.ALIAS_MAP, Confidence.HIGH)
            if not tilde_alias:
                ws_dir = (
                    self.mf.workspaces.get(first)
                    if self.mf.ws_kind.get(first) == "npm"
                    else None
                )
                if ws_dir is not None:
                    base = normalize_base(ws_dir, spec[len(first):].lstrip("/"))
                    cand = self._first_file(base, t)
                    if cand is not None:
                        return _resolved_c(rel, imp, cand, BindMethod.WORKSPACE_PKG, Confidence.HIGH)
                    return _phantom(rel, imp, f"workspace_member_missing_file:{spec}")
                if first in self.mf.declared.get("npm", frozenset()) or first.startswith("@"):
                    scoped_ok = first.startswith("@") and first in self.mf.declared.get("npm", frozenset())
                    if scoped_ok or not first.startswith("@"):
                        return _external(rel, imp, "npm", spec.split("/", 1)[0])
                return _phantom(rel, imp, f"unlisted_external:{first}")
            return _phantom(rel, imp, f"unresolved_alias:{spec}")

        ups = spec.count("..")
        base = normalize_base(_parent(rel), *([".."] * ups), spec.replace("./", ""))
        hit, others = _pick([self._file_candidates(base, t)], self.index)
        if hit is None:
            hit = self._casefold_rescue(rel, imp, base, t, ("",))
        if hit is not None:
            return _resolved(rel, imp, hit)
        return _phantom(rel, imp, f"unresolved_relative:{spec}")

    # ── rust ──────────────────────────────────────────────────────────

    def _bind_crate(self, rel: str, t: FamilyTable, imp: ImportDecl, spec: str) -> BindingRecord:
        segs = [s for s in spec.split("::") if s]
        head = segs[0] if segs else ""
        if head in ("crate", "self", "super"):
            return self._bind_crate_internal(rel, t, imp, segs, head)
        if len(segs) == 1:
            # bare `mod foo;` — module file lives beside the declaring file
            sib = normalize_base(_parent(rel), spec)
            hit = self._first_file(sib, t)
            if hit is not None:
                return _resolved(rel, imp, hit)
        if head in t.stdlib:
            return _external(rel, imp, "crates", head, note="core")
        if head in self.mf.workspaces and self.mf.ws_kind.get(head) == "cargo" and head != self._own_crate_name(rel):
            return _skipped(rel, imp, "cross_crate_workspace")
        if head in self.mf.declared.get("crates", frozenset()):
            return _external(rel, imp, "crates", head)
        return _phantom(rel, imp, f"unknown_extern_crate:{head}")

    def _bind_crate_internal(
        self, rel: str, t: FamilyTable, imp: ImportDecl, segs: list[str], head: str
    ) -> BindingRecord:
        rest = [s for s in segs if s not in ("crate", "self", "super")]
        ups = sum(1 for s in segs if s == "super")
        if head == "crate":
            starts = dict.fromkeys((*self._rust_roots, self._crate_root_for(rel)))
        else:
            starts = {_up(_parent(rel), ups)}
        # full path first …
        for start in starts:
            hit, _ = _pick([self._file_candidates(normalize_base(start, "/".join(rest)), t)], self.index)
            if hit is not None:
                return _resolved(rel, imp, hit)
        # … then progressive symbol-tail stripping (use-paths end in symbols)
        for k in range(len(rest) - 1, 0, -1):
            for start in starts:
                base = normalize_base(start, "/".join(rest[:k]))
                rel_path = self._first_file_any(base, t.file_templates)
                if rel_path is not None:
                    return _resolved_c(rel, imp, rel_path,
                                       BindMethod.PREFIX_STRIP, Confidence.LOW)
        return _phantom(rel, imp, f"unresolved_crate_path:{'::'.join(segs)}" if segs else "unresolved_crate_path:")

    def _own_crate_name(self, rel: str) -> str | None:
        best = ""
        for name, d in self.mf.workspaces.items():
            if self.mf.ws_kind.get(name) != "cargo":
                continue
            if d and rel.startswith(d + "/") and len(d) > len(best):
                best = d
        for name, d in self.mf.workspaces.items():
            if self.mf.ws_kind.get(name) == "cargo" and d == best and best:
                return name
        return None

    # ── go ────────────────────────────────────────────────────────────

    def _bind_go(self, rel: str, t: FamilyTable, imp: ImportDecl, spec: str) -> BindingRecord:
        full = imp.names[0] if imp.names else spec
        for module, mdir in sorted(
            self.mf.go_modules.items(), key=lambda kv: (-len(kv[0]), kv[0])
        ):
            if full == module or full.startswith(module + "/"):
                rem = full[len(module):].strip("/")
                hits = self.index.files_under(
                    normalize_base(mdir, rem), (".go",), cap=t.max_dir_files
                )
                if hits:
                    return _resolved_multi(
                        rel, imp, hits, BindMethod.GO_PACKAGE_DIR, Confidence.HIGH
                    )
                return _phantom(rel, imp, f"go_package_not_found:{full}")
        first = full.split("/")[0]
        if first in t.stdlib:
            return _external(rel, imp, "gomod", full, note="stdlib")
        if full in self.mf.workspaces and self.mf.ws_kind.get(full) == "cargo":
            return _skipped(rel, imp, "workspace_non_go")
        return _external(rel, imp, "gomod", full)

    # ── jvm ───────────────────────────────────────────────────────────

    def _bind_jvm(self, rel: str, t: FamilyTable, imp: ImportDecl, spec: str) -> BindingRecord:
        if any(spec.startswith(p) for p in ("java.", "javax.", "jdk.", "javafx.", "sun.", "com.sun.")):
            return _external(rel, imp, "maven", spec.split(".")[0], note="jdk")
        path_form = spec.replace(".", "/")
        if spec.endswith(".*"):
            pkg = path_form[:-2]
            hits: list[str] = []
            for root in dict.fromkeys(filter(None, [self._java_root, ""])):
                hits.extend(
                    self.index.files_under(
                        normalize_base(root, pkg), (".java", ".kt"), cap=t.max_dir_files
                    )
                )
            hits = sorted(set(hits))[: t.max_dir_files]
            if hits:
                return _resolved_multi(rel, imp, hits, BindMethod.JAVA_WILDCARD_DIR, Confidence.MEDIUM)
            return _phantom(rel, imp, f"jvm_package_missing:{pkg}")
        for root in dict.fromkeys(filter(None, [self._java_root, ""])):
            base = normalize_base(root, path_form)
            cand = self._first_file(base, ("{base}.java", "{base}.kt"))
            if cand is not None:
                return _resolved_c(rel, imp, cand.rel_path,
                                   BindMethod.ANCESTOR_WALK, Confidence.HIGH)
        return _phantom(rel, imp, f"jvm_class_missing:{spec}")

    # ── ruby / C loadpath family ─────────────────────────────────────

    _LOAD_TEMPLATES = ("{base}.rb", "{base}", "{base}.h")

    def _bind_loadpath(self, rel: str, t: FamilyTable, imp: ImportDecl, spec: str) -> BindingRecord:
        if imp.is_relative:
            base = normalize_base(_parent(rel), spec)
            hit = self._first_file_any(base, self._LOAD_TEMPLATES)
            if hit is not None:
                return _resolved_c(rel, imp, hit, BindMethod.EXACT_FILE, Confidence.HIGH)
            return _phantom(rel, imp, f"unresolved_require_relative:{spec}")
        head = spec.split("/")[0].split(".")[0]
        if head in t.stdlib:
            return _external(rel, imp, "gems", head, note="stdlib")
        if t.include_style and not imp.is_system:
            # C quoted includes resolve relative to the INCLUDING file first
            hit = self._first_file_any(normalize_base(_parent(rel), spec), self._LOAD_TEMPLATES)
            if hit is not None:
                return _resolved_c(rel, imp, hit, BindMethod.EXACT_FILE, Confidence.HIGH)
        for lp in t.loadpath_dirs:
            base = normalize_base(lp, spec)
            hit = self._first_file_any(base, self._LOAD_TEMPLATES)
            if hit is not None:
                return _resolved_c(rel, imp, hit, BindMethod.ANCESTOR_WALK, Confidence.MEDIUM)
        if head in self.mf.declared.get("gems", frozenset()):
            return _external(rel, imp, "gems", head)
        return _phantom(rel, imp, f"unlisted_or_missing:{spec}")

    def _bind_system_include(self, rel: str, imp: ImportDecl, spec: str) -> BindingRecord:
        name = spec.strip("<>").strip('"')
        for d in self._include_dirs:
            base = normalize_base(d, name)
            if self.index.has(base):
                return _resolved_c(rel, imp, base, BindMethod.ANCESTOR_WALK, Confidence.LOW)
        return _external(rel, imp, "system", name, note="system_header")


_DUMMY = ImportDecl(module="<casefold>")


# ── module-level record constructors (pure) ───────────────────────────


def _record(
    rel: str,
    imp: ImportDecl,
    verdict: Verdict,
    *,
    target: str | None = None,
    method: BindMethod | None = None,
    conf: Confidence | None = None,
    ambiguous: tuple[str, ...] = (),
    reason: str | None = None,
) -> BindingRecord:
    return BindingRecord(
        source_rel=rel,
        specifier=imp.module or ("<names:" + ",".join(imp.names) + ">"),
        line=imp.line,
        language="",
        is_dynamic=imp.is_dynamic,
        verdict=verdict,
        target_rel=target,
        method=method,
        confidence=conf,
        ambiguous_with=ambiguous,
        reason=reason,
    )


def _stamp_language(rec: BindingRecord, table: FamilyTable) -> BindingRecord:
    if rec.language:
        return rec
    return BindingRecord(
        source_rel=rec.source_rel, specifier=rec.specifier, line=rec.line,
        language=sorted(table.languages)[0], is_dynamic=rec.is_dynamic,
        verdict=rec.verdict, target_rel=rec.target_rel,
        target_file_id=rec.target_file_id, method=rec.method,
        confidence=rec.confidence, ambiguous_with=rec.ambiguous_with,
        reason=rec.reason,
    )


def _finalize_counters(rec: BindingRecord, m: RelateMetrics) -> BindingRecord:
    if rec.verdict is Verdict.RESOLVED:
        m.resolved += 1
    elif rec.verdict is Verdict.EXTERNAL:
        m.external += 1
    elif rec.verdict is Verdict.PHANTOM:
        m.phantom += 1
    else:
        m.skipped += 1
    if rec.ambiguous_with:
        m.ambiguous += 1
    if rec.method is BindMethod.CASE_FOLD:
        m.case_fold_rescues += 1
    return rec


def _resolved(rel: str, imp: ImportDecl, cand: Candidate) -> BindingRecord:
    return _resolved_c(rel, imp, cand.rel_path, cand.method, _conf_for(cand))


def _resolved_c(rel: str, imp: ImportDecl, target: str, method: BindMethod, conf: Confidence) -> BindingRecord:
    return _record(rel, imp, Verdict.RESOLVED, target=target, method=method, conf=conf)


def _resolved_multi(
    rel: str, imp: ImportDecl, targets: list[str], method: BindMethod, conf: Confidence
) -> BindingRecord:
    primary, extras = targets[0], tuple(targets[1:])
    return _record(rel, imp, Verdict.RESOLVED, target=primary, method=method, conf=conf, ambiguous=extras[:4])


def _external(rel: str, imp: ImportDecl, eco: str, name: str, note: str | None = None) -> BindingRecord:
    reason = f"{eco}:{name}" + (f":{note}" if note else "")
    return _record(rel, imp, Verdict.EXTERNAL, reason=reason)


def _phantom(rel: str, imp: ImportDecl, why: str) -> BindingRecord:
    return _record(rel, imp, Verdict.PHANTOM, reason=why)


def _skipped(rec_rel: str, imp: ImportDecl, why: str) -> BindingRecord:
    return _record(rec_rel, imp, Verdict.SKIPPED, reason=why)


def _conf_for(cand: Candidate) -> Confidence:
    if cand.rank <= 1:
        return Confidence.HIGH
    if cand.rank <= 4:
        return Confidence.MEDIUM
    return Confidence.LOW


def _parent(rel: str) -> str:
    return rel.rpartition("/")[0]


def _up(dir_rel: str, levels: int) -> str:
    d = dir_rel
    for _ in range(max(levels, 0)):
        d = d.rpartition("/")[0]
    return d


def _pick(streams: list[list[Candidate]], index: ModuleIndex) -> tuple[Candidate | None, list[str]]:
    """Rank-aware winner selection: lowest ladder rank wins; encounter order
    breaks ties. Every other distinct hit is reported as ambiguity."""
    seen: list[str] = []
    best: Candidate | None = None
    for stream in streams:
        for cand in stream:
            if not index.has(cand.rel_path):
                continue
            if cand.rel_path not in seen:
                seen.append(cand.rel_path)
            if best is None or cand.rank < best.rank:
                best = cand
    winner = best.rel_path if best else None
    return best, [p for p in seen if p != winner][:4]


__all__ = ["BindingKernel"]
