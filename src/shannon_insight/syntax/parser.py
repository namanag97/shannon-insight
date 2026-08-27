"""Generic tree-sitter walker producing FileSyntax from any PackSpec.

Token convention: a "token" is a leaf node (named or anonymous); comments are
tracked separately and excluded from token counts. body_tokens counts
non-comment leaves inside the function body; signature_tokens = function
leaves minus body leaves.

Captured here (max information transfer downstream — consumers never re-parse):
functions w/ spans/tokens/nesting/cyclomatic/calls/decorators/params/qualified
names/visibility/exported/async/docstrings/hard-stubs/return types |
classes w/ bases/methods/fields/abstract/interface | imports w/ aliases,
levels, system/dynamic flags | exports | top-level names | packages |
identifier vocabulary | comment texts.
"""

from __future__ import annotations

import hashlib
import re
from bisect import bisect_left
from collections.abc import Sequence
from dataclasses import dataclass, field

from tree_sitter import Node, Parser

from shannon_insight.core.errors import ErrorCode, ShannonError
from shannon_insight.syntax.models import (
    SYNTAX_PARSER_VERSION,
    ClassDef,
    ExportDecl,
    FileSyntax,
    FunctionDef,
    ImportDecl,
    compute_impl_gini,
    compute_stub_ratio,
)
from shannon_insight.syntax.packs import PackSpec, detect_language, pack_for_language

_MAX_IDENTIFIERS = 5000
_MAX_OCCURRENCES = 4000


@dataclass
class _FnBuilder:
    name: str = ""
    start_line: int = 0
    end_line: int = 0
    node_start: int = 0
    node_end: int = 0
    body_start: int = 0
    body_end: int = 0
    body_text: str = ""
    params: list[str] = field(default_factory=list)
    decorators: list[str] = field(default_factory=list)
    calls: list[str] = field(default_factory=list)
    control_count: int = 0
    max_nesting: int = 0
    is_method: bool = False
    class_name: str | None = None
    exported: bool = False
    is_async: bool = False
    has_docstring: bool = False
    return_type_raw: str | None = None

    def touch_control(self, depth: int) -> None:
        self.control_count += 1
        self.max_nesting = max(self.max_nesting, depth)


@dataclass
class _ClsBuilder:
    name: str
    start_line: int
    end_line: int
    node_start: int
    node_end: int
    bases: list[str] = field(default_factory=list)
    methods: list[str] = field(default_factory=list)
    fields: list[str] = field(default_factory=list)
    decorators: list[str] = field(default_factory=list)
    is_interface: bool = False
    exported: bool = False
    abstract_keyword: bool = False


def _scan_leaves(
    root: Node,
) -> tuple[list[tuple[int, int]], list[tuple[int, int]], list[str]]:
    code_spans: list[tuple[int, int]] = []
    comment_spans: list[tuple[int, int]] = []
    stack = [root]
    while stack:
        n = stack.pop()
        children = n.children
        if not children:
            s, e = n.start_byte, n.end_byte
            if e <= s:
                continue
            if "comment" in n.type:
                comment_spans.append((s, e))
            else:
                code_spans.append((s, e))
        else:
            stack.extend(children)
    code_spans.sort()
    comment_spans.sort()
    return code_spans, comment_spans, []


class _TokenIndex:
    def __init__(self, spans: list[tuple[int, int]]) -> None:
        self.starts = [s for s, _ in spans]

    def count_within(self, lo: int, hi: int) -> int:
        if hi <= lo:
            return 0
        return max(0, bisect_left(self.starts, hi) - bisect_left(self.starts, lo))


def _clean_param(txt: str) -> str:
    txt = txt.split("=")[0].split(":")[0]
    return txt.strip("*&() ").replace("final ", "").strip()


class Walker:
    def __init__(self, content: bytes, pack: PackSpec, parser: Parser) -> None:
        self.content = content
        self.pack = pack
        self.tree = parser.parse(content)
        self.functions: list[FunctionDef] = []
        self.classes: list[_ClsBuilder] = []
        self.exports: list[ExportDecl] = []
        self.top_level_names: list[str] = []
        self.identifiers: set[str] = set()
        self._occurrences: list[tuple[str, int]] = []

        newlines = content.count(b"\n") + 1
        avg_line = len(content) / max(newlines, 1)
        self.is_generated: bool = avg_line > 250 or len(content) > 512_000

        code_spans, comment_spans, _ = _scan_leaves(self.tree.root_node)
        self.tokens = _TokenIndex(code_spans)
        self.total_tokens = len(code_spans)
        self.comment_tokens = len(comment_spans)
        self.comments = (
            []
            if self.is_generated
            else [
                self.content[s:e].decode("utf-8", "replace").strip() for s, e in comment_spans[:200]
            ]
        )

        self._builders: list[_FnBuilder] = []
        self._class_stack: list[_ClsBuilder] = []
        self._package: str | None = None

    def text(self, node: Node) -> str:
        return self.content[node.start_byte : node.end_byte].decode("utf-8", "replace")

    def analyze(self) -> tuple[list[FunctionDef], list[_ClsBuilder]]:
        self._visit(self.tree.root_node, 0, False)
        fns = sorted(self.functions, key=lambda f: f.start_line)
        cls = sorted(self.classes, key=lambda c: c.start_line)
        return fns, cls

    def _visit(
        self,
        node: Node,
        control_depth: int,
        in_export: bool,
        children: Sequence[Node] | None = None,
    ) -> None:
        ntype = node.type
        spec = self.pack
        if children is None:
            children = node.children

        if spec.package_type is not None and ntype == spec.package_type and self._package is None:
            target = node.child_by_field_name("name") or (
                node.named_children[-1] if node.named_child_count > 0 else None
            )
            if target is not None:
                self._package = self.text(target).removeprefix("package ").strip() or None
            return

        if ntype in spec.identifier_types and not self.is_generated:
            word = self.text(node)
            if word.isidentifier() and len(word) > 1:
                if len(self.identifiers) < _MAX_IDENTIFIERS:
                    self.identifiers.add(word)
                if len(self._occurrences) < _MAX_OCCURRENCES:
                    self._occurrences.append((word, node.start_point[0] + 1))

        if ntype in ("visibility_modifier", "modifiers") and self._builders:
            txt = self.text(node)
            if "public" in txt or txt.startswith("pub"):
                self._builders[-1].exported = True
            return

        if ntype in spec.function_types:
            self._visit_function(node, in_export)
            return

        if ntype in spec.class_types or ntype in spec.interface_types:
            self._visit_class(node, control_depth, ntype in spec.interface_types, in_export)
            return

        if ntype.startswith("export_"):
            self._capture_export_list(node)
            for ch in children:
                self._visit(ch, control_depth, True)
            return

        if ntype in spec.control_types and self._builders:
            inner = control_depth + 1
            self._builders[-1].touch_control(inner)
            for ch in node.children:
                self._visit(ch, inner, in_export)
            return

        if ntype in spec.call_types and self._builders:
            callee = node.child_by_field_name("function")
            if callee is not None:
                raw = self.text(callee)
                name = raw.rsplit(".", 1)[-1].rsplit("::", 1)[-1].strip("() ")
                if name:
                    self._builders[-1].calls.append(name)

        if ntype in spec.field_types and self._class_stack and not self._builders:
            fname = self._extract_field_name(node)
            if fname:
                self._class_stack[-1].fields.append(fname)

        for ch in children:
            self._visit(ch, control_depth, in_export)

    def _extract_field_name(self, node: Node) -> str | None:
        named = node.child_by_field_name("name")
        if named is not None:
            return self.text(named).lstrip("#")
        left = node.child_by_field_name("left")
        if left is not None:
            return self.text(left)
        for ch in node.named_children:
            t = ch.type
            if t in (
                "identifier",
                "property_identifier",
                "field_identifier",
                "shorthand_property_identifier",
            ):
                return self.text(ch)
            if t == "variable_declarator":
                inner = ch.child_by_field_name("name")
                if inner is not None:
                    return self.text(inner)
            if t == "assignment":
                l2 = ch.child_by_field_name("left")
                if l2 is not None:
                    return self.text(l2)
        return None

    def _capture_export_list(self, node: Node) -> None:
        line = node.start_point[0] + 1
        for ch in node.named_children:
            if "clause" not in ch.type:
                continue
            for tok in ch.named_children:
                txt = self.text(tok).split(" as ")[0].strip("{} \n,")
                if txt and txt != ",":
                    self.exports.append(
                        ExportDecl(name=txt.split(",")[0].strip(), kind="symbol", line=line)
                    )

    def _visit_function(self, node: Node, in_export: bool) -> None:
        name_node = node.child_by_field_name("name")
        if name_node is not None:
            display_name: str = self.text(name_node)
        else:
            display_name = self._declarator_name(node) or "<anonymous>"
        params_node = node.child_by_field_name("parameters")
        body = node.child_by_field_name("body")

        bstart = body.start_byte if body is not None else node.end_byte
        bend = body.end_byte if body is not None else node.end_byte

        builder = _FnBuilder(
            name=display_name,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            node_start=node.start_byte,
            node_end=node.end_byte,
            body_start=bstart,
            body_end=bend,
            body_text=self.content[bstart:bend].decode("utf-8", "replace"),
            params=self._param_names(params_node),
            decorators=[
                self.text(s).lstrip("@").strip()
                for s in self._preceding_siblings(node)
                if getattr(s, "type", "") == "decorator"
            ],
            is_method=bool(self._class_stack),
            class_name=self._class_stack[-1].name if self._class_stack else None,
            exported=in_export,
        )

        if self.pack.name == "python" and body is not None and body.named_child_count > 0:
            first = body.named_children[0]
            if first.type == "expression_statement" and first.named_child_count > 0:
                inner = first.named_children[0]
                if inner.type == "string":
                    builder.has_docstring = True

        for fname in self.pack.return_type_fields:
            rt = node.child_by_field_name(fname)
            if rt is not None:
                cleaned = self.text(rt).lstrip(":-> ").strip()
                if cleaned:
                    builder.return_type_raw = cleaned
                break

        self._builders.append(builder)
        fn_children = node.children
        builder.is_async = any(getattr(ch, "type", "") == "async" for ch in fn_children)
        for ch in fn_children:
            self._visit(ch, 0, in_export)
        self._finish_function(builder)

    @staticmethod
    def _param_names(params_node: Node | None) -> list[str]:
        out: list[str] = []
        if params_node is None:
            return out
        for ch in params_node.named_children:
            t = ch.type
            if t in ("comment", ",", "this"):
                continue
            named = ch.child_by_field_name("name")
            pattern = ch.child_by_field_name("pattern")
            target = named or pattern
            if target is not None:
                out.append(_clean_param(Walker._static_text(target)))
            elif t in (
                "identifier",
                "shorthand_property_identifier",
                "pattern_identifier",
                "required_parameter",
                "optional_parameter",
            ):
                out.append(_clean_param(Walker._static_text(ch)))
            elif t.endswith("parameter") and t != "formal_parameters":
                head = _clean_param(Walker._static_text(ch).split(":")[0])
                if head:
                    out.append(head)
        return out

    @staticmethod
    def _static_text(node: Node) -> str:
        raw = node.text
        return raw.decode("utf-8") if raw is not None else ""

    def _finish_function(self, b: _FnBuilder) -> None:
        total = self.tokens.count_within(b.node_start, b.node_end)
        body_tokens = self.tokens.count_within(b.body_start, min(b.body_end, b.node_end))
        signature_tokens = max(0, total - body_tokens)

        stripped = b.body_text.strip().rstrip(";").rstrip(":").strip()
        hard_stub = stripped in self.pack.hard_stub_markers
        if not hard_stub:
            for marker in self.pack.hard_stub_markers:
                if marker in b.body_text and body_tokens <= 6:
                    hard_stub = True
                    break
        if self.pack.name == "python" and "NotImplementedError" in b.body_text and body_tokens <= 6:
            hard_stub = True

        name = b.name
        visibility = "internal"
        exported = b.exported
        if self.pack.name == "python":
            exported = not name.startswith("_") and not b.is_method
            visibility = "private" if name.startswith("_") else "public"
        elif self.pack.name == "go":
            exported = bool(name) and name[0].isupper()
            visibility = "public" if exported else "private"
        elif self.pack.name in ("javascript", "typescript", "tsx"):
            visibility = "public" if exported else "internal"
            if name.startswith("#"):
                visibility = "private"

        qualified = f"{b.class_name}.{name}" if b.class_name else name
        self.functions.append(
            FunctionDef(
                name=name,
                params=tuple(
                    p
                    for p in b.params
                    if p and not (b.is_method and p in ("self", "cls") and p == b.params[0])
                ),
                start_line=b.start_line,
                end_line=b.end_line,
                body_tokens=body_tokens,
                signature_tokens=signature_tokens,
                nesting_depth=b.max_nesting,
                cyclomatic=1 + b.control_count,
                qualified_name=qualified,
                calls=tuple(dict.fromkeys(b.calls)),
                decorators=tuple(b.decorators),
                is_method=b.is_method,
                class_name=b.class_name,
                exported=exported,
                visibility=visibility,
                is_async=b.is_async,
                has_docstring=b.has_docstring,
                is_hard_stub=hard_stub,
                return_type_raw=b.return_type_raw,
            )
        )
        if b.class_name:
            for cls in reversed(self._class_stack):
                if cls.name == b.class_name:
                    cls.methods.append(name)
                    break
        elif not name.startswith("<"):
            self.top_level_names.append(name)
        self._builders.pop()

    def _declarator_name(self, node: Node) -> str | None:
        """C/C++: name hides inside declarator -> function_declarator -> declarator."""
        decl = node.child_by_field_name("declarator")
        depth = 0
        while decl is not None and depth < 4:
            t = getattr(decl, "type", "")
            if t == "identifier":
                return self.text(decl)
            inner = decl.child_by_field_name("declarator")
            if inner is None:
                return None
            decl = inner
            depth += 1
        return None

    def _visit_class(
        self, node: Node, control_depth: int, is_interface: bool, in_export: bool
    ) -> None:
        name_node = node.child_by_field_name("name")
        bases: list[str] = []

        sup = node.child_by_field_name("superclass") or node.child_by_field_name("superclasses")
        if sup is not None:
            targets = sup.named_children if sup.named_child_count > 0 else [sup]
            bases.extend(self.text(t) for t in targets)
        interfaces = node.child_by_field_name("interfaces")
        if interfaces is not None:
            bases.extend(self.text(t) for t in interfaces.named_children)
        if not bases:
            for ch in node.named_children:
                ct = ch.type
                if ct == "superclasses" or "heritage" in ct:
                    for sub in ch.named_children:
                        if sub.type == "argument_list":
                            bases.extend(self.text(t2) for t2 in sub.named_children)
                        elif "comment" not in sub.type:
                            bases.append(self.text(sub))

        decorators = [
            self.text(s).lstrip("@").strip()
            for s in self._preceding_siblings(node)
            if getattr(s, "type", "") == "decorator"
        ]

        cleaned_bases = []
        for b in bases:
            b = b.strip()
            for kw in ("extends ", "implements ", ": "):
                if b.startswith(kw):
                    b = b[len(kw) :].strip()
            if b:
                cleaned_bases.append(b)

        cls = _ClsBuilder(
            name=self.text(name_node) if name_node is not None else "<anonymous>",
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            node_start=node.start_byte,
            node_end=node.end_byte,
            bases=cleaned_bases,
            decorators=decorators,
            is_interface=is_interface,
            exported=in_export,
            abstract_keyword=any(getattr(ch, "type", "") == "abstract" for ch in node.children),
        )
        self.classes.append(cls)
        self._class_stack.append(cls)
        cls_children = node.children
        for ch in cls_children:
            self._visit(ch, control_depth, in_export)
        self._class_stack.pop()
        if cls.name != "<anonymous>":
            self.top_level_names.append(cls.name)

    def extract_imports(self) -> tuple[ImportDecl, ...]:
        seen: dict[tuple[str, int, int, bool], ImportDecl] = {}
        for imp in self.pack.import_extractor(self.tree.root_node, self.text):
            seen[(imp.module, imp.level, imp.line, imp.is_dynamic)] = imp
        return tuple(seen.values())

    def build_exports(
        self, functions: list[FunctionDef], classes: list[_ClsBuilder]
    ) -> tuple[ExportDecl, ...]:
        out: list[ExportDecl] = []
        seen: set[tuple[str, str]] = set()

        def add(name: str, kind: str, line: int) -> None:
            key = (name, kind)
            if name and key not in seen:
                seen.add(key)
                out.append(ExportDecl(name=name, kind=kind, line=line))

        for f in functions:
            if f.exported:
                add(
                    f.qualified_name or f.name,
                    "method" if f.is_method else "function",
                    f.start_line,
                )
        for c in classes:
            if c.exported or c.abstract_keyword:
                add(c.name, "interface" if c.is_interface else "class", c.start_line)

        if self.pack.name == "python":
            source = self.content.decode("utf-8", "replace")
            for match in re.finditer(r"__all__\s*=\s*\[(.*?)\]", source, re.S):
                for quoted in re.findall(r"[\"']([\w.]+)[\"']", match.group(1)):
                    add(quoted, "symbol", 0)
        return tuple(out)

    def has_main_guard(self) -> bool:
        if self.pack.name != "python":
            return False
        stack = [self.tree.root_node]
        while stack:
            n = stack.pop()
            if n.type == "if_statement" and "__main__" in self.text(n):
                return True
            stack.extend(n.named_children)
        return False

    @staticmethod
    def _preceding_siblings(node: Node) -> list[Node]:
        sibs: list[Node] = []
        cur = getattr(node, "prev_sibling", None)
        while cur is not None:
            sibs.append(cur)
            cur = getattr(cur, "prev_sibling", None)
        return sibs


class ParserManager:
    """Caches Parser instances per language."""

    def __init__(self) -> None:
        self._parsers: dict[str, Parser] = {}

    def parser_for(self, pack: PackSpec) -> Parser:
        cached = self._parsers.get(pack.name)
        if cached is not None:
            return cached
        parser = pack.get_parser()
        self._parsers[pack.name] = parser
        return parser


_DEFAULT_MANAGER = ParserManager()


def analyze_source(
    path: str,
    content: bytes,
    language: str | None = None,
    manager: ParserManager | None = None,
) -> FileSyntax:
    """Parse ``content`` into the IR1 FileSyntax record."""
    mgr = manager or _DEFAULT_MANAGER
    name = language or detect_language(path)
    if name is None:
        ext = ("." + path.rsplit(".", 1)[-1].lower()) if "." in path else "<none>"
        raise ShannonError(
            message=f"no syntax pack for extension '{ext}' (file {path})",
            code=ErrorCode.SYNTAX_UNSUPPORTED_LANGUAGE,
        )
    pack = pack_for_language(name)

    # Generated-artifact fast path: bundles/minified blobs get counts-only IR1.
    newlines = content.count(b"\n") + 1
    avg_line = len(content) / max(newlines, 1)
    if avg_line > 250 or len(content) > 512_000:
        return FileSyntax(
            path=path,
            language=pack.name,
            content_hash=hashlib.sha256(content).hexdigest(),
            lines=len(content.decode("utf-8", "replace").splitlines()),
            is_generated=True,
            encoding="utf-8",
        )

    parser = mgr.parser_for(pack)

    walker = Walker(content, pack, parser)
    functions, cls_builders = walker.analyze()

    try:
        text_full = content.decode("utf-8")
        encoding = "utf-8"
    except UnicodeDecodeError:
        text_full = content.decode("latin-1")
        encoding = "latin-1"

    exports = walker.build_exports(functions, cls_builders)
    top_names = tuple(dict.fromkeys(walker.top_level_names + [e.name for e in exports]))

    classes = tuple(
        ClassDef(
            name=c.name,
            start_line=c.start_line,
            end_line=c.end_line,
            bases=tuple(c.bases),
            method_names=tuple(c.methods),
            field_names=tuple(dict.fromkeys(c.fields)),
            is_abstract=c.abstract_keyword
            or any(b.rsplit(".", 1)[-1].strip("<>") in pack.abstract_bases for b in c.bases)
            or any("abstract" in d.lower() for d in c.decorators),
            is_interface=c.is_interface,
            decorators=tuple(c.decorators),
            exported=c.exported,
        )
        for c in cls_builders
    )

    return FileSyntax(
        path=path,
        language=pack.name,
        content_hash=hashlib.sha256(content).hexdigest(),
        lines=len(text_full.splitlines()),
        functions=tuple(functions),
        classes=classes,
        imports=walker.extract_imports(),
        exports=exports,
        top_level_names=top_names,
        package=walker._package,
        has_errors=bool(walker.tree.root_node.has_error),
        has_main_guard=walker.has_main_guard(),
        parse_mode="tree-sitter",
        parser_version=SYNTAX_PARSER_VERSION,
        stub_ratio=compute_stub_ratio(tuple(functions)),
        impl_gini=compute_impl_gini(tuple(functions)),
        cyclomatic=sum(f.cyclomatic for f in functions) if functions else 1,
        total_tokens=walker.total_tokens,
        comment_tokens=walker.comment_tokens,
        identifiers=frozenset(walker.identifiers),
        comments=tuple(walker.comments[:200]),
        occurrences=tuple(walker._occurrences),
        encoding=encoding,
        is_generated=walker.is_generated,
    )


__all__ = ["ParserManager", "Walker", "analyze_source"]
