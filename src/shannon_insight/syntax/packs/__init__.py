"""Language packs: declarative grammar bindings for the syntax context.

Grammar backend: ``tree-sitter-language-pack`` (prebuilt abi3 wheels, 370+
languages, MIT). One dependency replaces per-grammar packages; direct
``tree_sitter_<lang>`` modules remain a fallback.

A pack is pure configuration: node-type tables + two small extractors
(imports) + markers. The generic walker in parser.py consumes any pack, so
adding a language never touches shared code.

Tier S (deep fidelity): python, typescript/tsx, javascript, go.
Tier A (lean): java, rust. Extension tier: ruby, c, cpp.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import cast

from tree_sitter import Node, Parser

from shannon_insight.core.errors import ErrorCode, ShannonError, grammar_missing
from shannon_insight.syntax.models import ImportDecl

_DEFAULT_IDENTIFIER_TYPES = frozenset({"identifier"})


@dataclass(frozen=True)
class PackSpec:
    name: str
    extensions: tuple[str, ...]

    function_types: frozenset[str]
    class_types: frozenset[str]
    call_types: frozenset[str]
    control_types: frozenset[str]

    import_extractor: Callable[[Node, Callable[[Node], str]], list[ImportDecl]]

    interface_types: frozenset[str] = frozenset()
    field_types: frozenset[str] = frozenset()
    package_type: str | None = None
    comment_marker: str = "comment"
    identifier_types: frozenset[str] = _DEFAULT_IDENTIFIER_TYPES
    hard_stub_markers: frozenset[str] = frozenset()
    return_type_fields: tuple[str, ...] = ("return_type", "return_annotation", "result", "results")
    abstract_bases: frozenset[str] = frozenset()
    export_ancestor_prefixes: tuple[str, ...] = ()
    fallback_module: str | None = None

    def get_parser(self) -> Parser:
        try:
            from tree_sitter_language_pack import get_parser as _gp

            return cast(Parser, _gp(self.name))
        except Exception:
            pass
        if self.fallback_module is None:
            raise grammar_missing(self.name)
        try:
            module = __import__(self.fallback_module, fromlist=["language"])
            from tree_sitter import Language

            lang = Language(module.language())
            try:
                return Parser(lang)
            except TypeError:
                parser = Parser()
                parser.language = lang
                return parser
        except ImportError as exc:
            raise grammar_missing(self.name) from exc


def _strip_quotes(text: str) -> str:
    text = text.strip()
    if len(text) >= 2 and text[0] in "\"'" and text[-1] == text[0]:
        return text[1:-1]
    return text


def python_imports(node: Node, text_of: Callable[[Node], str]) -> list[ImportDecl]:
    out: list[ImportDecl] = []
    stack = [node]
    while stack:
        n = stack.pop()
        t = n.type
        if t == "import_statement":
            for ch in n.named_children:
                if ch.type == "aliased_import":
                    raw = text_of(ch)
                    module, _, alias_text = raw.partition(" as ")
                    out.append(
                        ImportDecl(
                            module=module.strip(),
                            alias=alias_text.strip() or None,
                            line=n.start_point[0] + 1,
                        )
                    )
                elif ch.type == "dotted_name":
                    out.append(ImportDecl(module=text_of(ch), line=n.start_point[0] + 1))
        elif t == "import_from_statement":
            module = ""
            level = 0
            names: list[str] = []
            alias: str | None = None
            for ch in n.named_children:
                ct = ch.type
                txt = text_of(ch)
                if ct == "relative_import":
                    level = len(txt) - len(txt.lstrip("."))
                    module = txt.lstrip(".")
                elif ct == "aliased_import":
                    before, _, after = txt.partition(" as ")
                    names.append(before.strip())
                    alias = after.strip() or None
                elif ct in ("identifier", "dotted_name"):
                    if not module and level == 0 and ch.prev_named_sibling is None:
                        module = txt
                    else:
                        names.append(txt)
            out.append(
                ImportDecl(
                    module=module,
                    names=tuple(names),
                    alias=alias,
                    level=level,
                    line=n.start_point[0] + 1,
                )
            )
        else:
            stack.extend(n.named_children)
    return out


def go_imports(node: Node, text_of: Callable[[Node], str]) -> list[ImportDecl]:
    out: list[ImportDecl] = []
    stack = [node]
    while stack:
        n = stack.pop()
        if n.type == "import_spec":
            path_node = n.child_by_field_name("path")
            if path_node is not None:
                raw = _strip_quotes(text_of(path_node))
                module = raw.rsplit("/", 1)[-1] or raw
                out.append(ImportDecl(module=module, names=(raw,), line=n.start_point[0] + 1))
        stack.extend(n.named_children)
    return out


def js_ts_imports(node: Node, text_of: Callable[[Node], str]) -> list[ImportDecl]:
    out: list[ImportDecl] = []
    stack = [node]
    while stack:
        n = stack.pop()
        t = n.type
        if t == "import_statement":
            src = n.child_by_field_name("source")
            if src is None:
                continue
            names: list[str] = []
            alias: str | None = None
            for ch in n.named_children:
                if ch.type != "import_clause":
                    continue
                for sub in ch.named_children:
                    st = sub.type
                    if st == "identifier":
                        alias = text_of(sub)
                    elif st == "namespace_import":
                        raw = text_of(sub)
                        alias = raw.split(" as ")[-1].strip()
                        names.append("*")
                    elif st == "named_imports":
                        for spec in sub.named_children:
                            raw = text_of(spec)
                            names.append(
                                raw.split(" as ")[0].replace("{", "").replace("}", "").strip()
                            )
            out.append(
                ImportDecl(
                    module=_strip_quotes(text_of(src)),
                    names=tuple(n2 for n2 in names if n2),
                    alias=alias,
                    line=n.start_point[0] + 1,
                )
            )
        elif t == "call_expression":
            fn = n.child_by_field_name("function")
            args = n.child_by_field_name("arguments")
            if fn is None or args is None or args.named_child_count == 0:
                continue
            callee = text_of(fn)
            first = args.named_children[0]
            if callee == "require":
                out.append(
                    ImportDecl(module=_strip_quotes(text_of(first)), line=n.start_point[0] + 1)
                )
            elif callee == "import":
                out.append(
                    ImportDecl(
                        module=_strip_quotes(text_of(first)),
                        line=n.start_point[0] + 1,
                        is_dynamic=True,
                    )
                )
        elif t == "export_statement":
            src = n.child_by_field_name("source")
            if src is not None:
                out.append(
                    ImportDecl(module=_strip_quotes(text_of(src)), line=n.start_point[0] + 1)
                )
        stack.extend(n.named_children)
    return out


def java_imports(node: Node, text_of: Callable[[Node], str]) -> list[ImportDecl]:
    out: list[ImportDecl] = []
    stack = [node]
    while stack:
        n = stack.pop()
        if n.type == "import_declaration":
            raw = text_of(n).removeprefix("import").removesuffix(";").replace("static", "").strip()
            out.append(ImportDecl(module=raw, line=n.start_point[0] + 1))
        stack.extend(n.named_children)
    return out


def rust_imports(node: Node, text_of: Callable[[Node], str]) -> list[ImportDecl]:
    out: list[ImportDecl] = []
    stack = [node]
    while stack:
        n = stack.pop()
        t = n.type
        if t == "use_declaration":
            arg = n.named_children[0] if n.named_child_count > 0 else None
            raw = (
                text_of(arg if arg is not None else n)
                .removeprefix("use ")
                .removesuffix(";")
                .strip()
            )
            flattened = raw.replace("{", "").replace("}", "")
            for part in (p.strip().lstrip(":") for p in flattened.split(",")):
                if part:
                    out.append(ImportDecl(module=part, line=n.start_point[0] + 1))
        elif t == "mod_declaration":
            name_node = n.child_by_field_name("name")
            if name_node is not None:
                out.append(ImportDecl(module=text_of(name_node), line=n.start_point[0] + 1))
        stack.extend(n.named_children)
    return out


def ruby_imports(node: Node, text_of: Callable[[Node], str]) -> list[ImportDecl]:
    out: list[ImportDecl] = []
    stack = [node]
    while stack:
        n = stack.pop()
        if n.type == "call":
            method = n.child_by_field_name("method")
            if method is not None and text_of(method) in ("require", "require_relative"):
                args = n.child_by_field_name("arguments")
                if args is not None and args.named_child_count > 0:
                    first = args.named_children[0]
                    rel = text_of(method) == "require_relative"
                    out.append(
                        ImportDecl(
                            module=_strip_quotes(text_of(first)),
                            level=1 if rel else 0,
                            line=n.start_point[0] + 1,
                        )
                    )
        stack.extend(n.named_children)
    return out


def c_imports(node: Node, text_of: Callable[[Node], str]) -> list[ImportDecl]:
    out: list[ImportDecl] = []
    stack = [node]
    while stack:
        n = stack.pop()
        if n.type in ("preproc_include", "system_lib_string"):
            raw = text_of(n)
            for token in raw.replace("#include", "").split():
                system = token.startswith("<")
                out.append(
                    ImportDecl(
                        module=token.strip('<>"'),
                        is_system=system,
                        line=n.start_point[0] + 1,
                    )
                )
        stack.extend(n.named_children)
    return out


_PY_CONTROLS = frozenset(
    {
        "if_statement",
        "for_statement",
        "while_statement",
        "try_statement",
        "with_statement",
        "elif_clause",
        "except_clause",
        "match_statement",
        "case_clause",
        "conditional_expression",
        "boolean_operator",
    }
)

_JS_CONTROLS = frozenset(
    {
        "if_statement",
        "for_statement",
        "for_in_statement",
        "while_statement",
        "do_statement",
        "switch_statement",
        "switch_case",
        "try_statement",
        "catch_clause",
        "ternary_expression",
    }
)


PYTHON = PackSpec(
    name="python",
    extensions=(".py",),
    function_types=frozenset({"function_definition"}),
    class_types=frozenset({"class_definition"}),
    call_types=frozenset({"call"}),
    control_types=_PY_CONTROLS,
    import_extractor=python_imports,
    field_types=frozenset({"assignment"}),
    package_type=None,
    hard_stub_markers=frozenset({"pass", "...", "NotImplementedError"}),
    abstract_bases=frozenset({"ABC", "Protocol"}),
    export_ancestor_prefixes=(),
    fallback_module="tree_sitter_python",
)

GO = PackSpec(
    name="go",
    extensions=(".go",),
    function_types=frozenset({"function_declaration", "method_declaration"}),
    class_types=frozenset(),
    call_types=frozenset({"call_expression"}),
    control_types=frozenset(
        {
            "if_statement",
            "for_statement",
            "switch_statement",
            "type_switch_statement",
            "select_statement",
            "case_clause",
            "communication_clause",
        }
    ),
    import_extractor=go_imports,
    package_type="package_clause",
    fallback_module="tree_sitter_go",
)

JAVASCRIPT = PackSpec(
    name="javascript",
    extensions=(".js", ".jsx", ".mjs", ".cjs"),
    function_types=frozenset(
        {"function_declaration", "method_definition", "function_expression", "arrow_function"}
    ),
    class_types=frozenset({"class_declaration"}),
    call_types=frozenset({"call_expression"}),
    control_types=_JS_CONTROLS,
    import_extractor=js_ts_imports,
    field_types=frozenset({"property_definition", "public_field_definition", "field_definition"}),
    export_ancestor_prefixes=("export_",),
    fallback_module="tree_sitter_javascript",
)

TYPESCRIPT = PackSpec(
    name="typescript",
    extensions=(".ts",),
    function_types=frozenset({"function_declaration", "method_definition", "arrow_function"}),
    class_types=frozenset({"class_declaration", "abstract_class_declaration"}),
    call_types=frozenset({"call_expression"}),
    control_types=_JS_CONTROLS,
    import_extractor=js_ts_imports,
    interface_types=frozenset({"interface_declaration"}),
    field_types=JAVASCRIPT.field_types,
    export_ancestor_prefixes=("export_",),
    fallback_module="tree_sitter_typescript",
)

TSX = PackSpec(
    name="tsx",
    extensions=(".tsx",),
    function_types=TYPESCRIPT.function_types,
    class_types=TYPESCRIPT.class_types | frozenset({"interface_declaration"}),
    call_types=TYPESCRIPT.call_types,
    control_types=TYPESCRIPT.control_types,
    import_extractor=js_ts_imports,
    field_types=TYPESCRIPT.field_types,
    export_ancestor_prefixes=TYPESCRIPT.export_ancestor_prefixes,
    fallback_module="tree_sitter_typescript",
)

JAVA = PackSpec(
    name="java",
    extensions=(".java",),
    function_types=frozenset({"method_declaration", "constructor_declaration"}),
    class_types=frozenset({"class_declaration", "enum_declaration"}),
    call_types=frozenset({"method_invocation"}),
    control_types=frozenset(
        {
            "if_statement",
            "for_statement",
            "enhanced_for_statement",
            "while_statement",
            "do_statement",
            "switch_statement",
            "switch_case",
            "try_statement",
            "catch_clause",
            "ternary_expression",
        }
    ),
    import_extractor=java_imports,
    interface_types=frozenset({"interface_declaration"}),
    field_types=frozenset({"field_declaration"}),
    package_type="package_declaration",
    identifier_types=frozenset({"identifier", "type_identifier"}),
    fallback_module="tree_sitter_java",
)

RUST = PackSpec(
    name="rust",
    extensions=(".rs",),
    function_types=frozenset({"function_item"}),
    class_types=frozenset({"struct_item", "enum_item", "trait_item"}),
    call_types=frozenset({"call_expression"}),
    control_types=frozenset(
        {
            "if_expression",
            "if_let_expression",
            "match_expression",
            "match_arm",
            "for_expression",
            "while_expression",
            "while_let_expression",
            "loop_expression",
        }
    ),
    import_extractor=rust_imports,
    interface_types=frozenset({"trait_item"}),
    field_types=frozenset({"field_declaration"}),
    hard_stub_markers=frozenset({"todo!()", "unimplemented!()"}),
    fallback_module="tree_sitter_rust",
)

RUBY = PackSpec(
    name="ruby",
    extensions=(".rb",),
    function_types=frozenset({"method", "singleton_method"}),
    class_types=frozenset({"class", "module"}),
    call_types=frozenset({"call"}),
    control_types=frozenset(
        {"if", "unless", "while", "until", "case", "when", "for", "begin", "rescue", "ensure"}
    ),
    import_extractor=ruby_imports,
    identifier_types=frozenset({"identifier", "constant"}),
    fallback_module="tree_sitter_ruby",
)

C = PackSpec(
    name="c",
    extensions=(".c", ".h"),
    function_types=frozenset({"function_definition"}),
    class_types=frozenset(),
    call_types=frozenset({"call_expression"}),
    control_types=frozenset(
        {
            "if_statement",
            "for_statement",
            "while_statement",
            "do_statement",
            "switch_statement",
            "case_statement",
        }
    ),
    import_extractor=c_imports,
    fallback_module="tree_sitter_c",
)

CPP = PackSpec(
    name="cpp",
    extensions=(".cpp", ".cc", ".cxx", ".hpp", ".hh"),
    function_types=C.function_types,
    class_types=frozenset({"class_specifier", "struct_specifier"}),
    call_types=C.call_types,
    control_types=C.control_types,
    import_extractor=c_imports,
    field_types=frozenset({"field_declaration"}),
    fallback_module="tree_sitter_cpp",
)

PACKS_BY_LANGUAGE: dict[str, PackSpec] = {
    p.name: p for p in (PYTHON, GO, JAVASCRIPT, TYPESCRIPT, TSX, JAVA, RUST, RUBY, C, CPP)
}

_PACKS_BY_EXTENSION: dict[str, PackSpec] = {}
for _p in PACKS_BY_LANGUAGE.values():
    for _ext in _p.extensions:
        _PACKS_BY_EXTENSION.setdefault(_ext, _p)


def pack_for_extension(ext: str) -> PackSpec | None:
    return _PACKS_BY_EXTENSION.get(ext.lower())


def pack_for_language(name: str) -> PackSpec:
    pack = PACKS_BY_LANGUAGE.get(name)
    if pack is None:
        raise ShannonError(
            message=f"no syntax pack registered for language '{name}'",
            code=ErrorCode.SYNTAX_UNSUPPORTED_LANGUAGE,
            recovery_hint="register a PackSpec in syntax.packs",
        )
    return pack


def detect_language(path: str) -> str | None:
    ext = ("." + path.rsplit(".", 1)[-1].lower()) if "." in path else ""
    pack = pack_for_extension(ext)
    return pack.name if pack else None


__all__ = [
    "CPP",
    "C",
    "GO",
    "JAVA",
    "JAVASCRIPT",
    "PYTHON",
    "RUBY",
    "RUST",
    "TYPESCRIPT",
    "TSX",
    "PackSpec",
    "detect_language",
    "pack_for_extension",
    "pack_for_language",
]
