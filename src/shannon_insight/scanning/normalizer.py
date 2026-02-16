"""Normalizer: converts raw tree-sitter captures to FileSyntax.

This module takes tree-sitter parse trees and produces language-agnostic
FileSyntax objects. It handles the language-specific differences internally.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from .queries import get_query
from .syntax import ClassDef, FileSyntax, FunctionDef, ImportDecl
from .treesitter_parser import TREE_SITTER_AVAILABLE, TreeSitterParser

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class TreeSitterNormalizer:
    """Converts tree-sitter parse trees to FileSyntax.

    Usage:
        normalizer = TreeSitterNormalizer()
        syntax = normalizer.parse_file(content, path, language)
        if syntax is not None:
            # tree-sitter parsing succeeded
        else:
            # fallback to regex
    """

    def __init__(self) -> None:
        """Initialize normalizer with tree-sitter parser."""
        self._parser = TreeSitterParser() if TREE_SITTER_AVAILABLE else None

    def parse_file(
        self, content: str, path: str, language: str, mtime: float = 0.0
    ) -> FileSyntax | None:
        """Parse file content and return FileSyntax.

        Args:
            content: File content as string
            path: File path for the result
            language: Detected language
            mtime: Last modified timestamp

        Returns:
            FileSyntax with call_targets populated, or None if parsing failed
        """
        if self._parser is None:
            return None

        if not self._parser.is_language_supported(language):
            return None

        try:
            code_bytes = content.encode("utf-8")
        except UnicodeEncodeError:
            logger.debug(f"Encoding error for {path}, falling back to regex")
            return None

        tree = self._parser.parse(code_bytes, language)
        if tree is None:
            return None

        functions = self._extract_functions(tree, code_bytes, language)
        classes = self._extract_classes(tree, code_bytes, language)
        imports = self._extract_imports(tree, code_bytes, language)
        has_main = self._detect_main_guard(tree, code_bytes, language)

        # Compute cached metrics
        lines = content.count("\n") + 1 if content else 0
        tokens = self._count_file_tokens(tree)
        complexity = self._compute_complexity(functions)

        return FileSyntax(
            path=path,
            functions=functions,
            classes=classes,
            imports=imports,
            language=language,
            has_main_guard=has_main,
            mtime=mtime,
            _lines=lines,
            _tokens=tokens,
            _complexity=complexity,
        )

    def _extract_functions(self, tree: Any, code_bytes: bytes, language: str) -> list[FunctionDef]:
        """Extract function definitions from parse tree."""
        functions: list[FunctionDef] = []

        query_str = get_query(language, "function")
        if query_str is None:
            return functions

        captures = self._parser.query(tree, query_str, language)  # type: ignore[union-attr]
        if not captures:
            return functions

        # Group captures by function node
        processed_nodes: set[int] = set()

        for node, capture_name in captures:
            # Only process @function, @method, @decorated_function captures
            if not capture_name.endswith((".name", "function", "method", "decorated_function")):
                if "function" not in capture_name and "method" not in capture_name:
                    continue

            # Skip if we've already processed this function
            func_node = self._get_function_node(node, capture_name)
            if func_node is None:
                continue

            # Dedup by position (start_byte), not Python object id,
            # since QueryCursor may return distinct objects for the same node
            node_key = func_node.start_byte
            if node_key in processed_nodes:
                continue
            processed_nodes.add(node_key)

            func = self._node_to_function(func_node, code_bytes, language, captures)
            if func is not None:
                functions.append(func)

        return functions

    def _get_function_node(self, node: Any, capture_name: str) -> Any | None:
        """Get the function definition node from a capture."""
        if capture_name.endswith(".name"):
            # Walk up to find the function node
            parent = node.parent
            while parent is not None:
                if parent.type in (
                    "function_definition",
                    "function_declaration",
                    "method_declaration",
                    "method_definition",
                    "function_item",
                    "method",
                ):
                    return parent
                parent = parent.parent
            return None
        # It's the function node itself
        if node.type in (
            "function_definition",
            "function_declaration",
            "method_declaration",
            "method_definition",
            "function_item",
            "method",
            "decorated_definition",
        ):
            return node
        return None

    def _node_to_function(
        self, node: Any, code_bytes: bytes, language: str, all_captures: list[Any]
    ) -> FunctionDef | None:
        """Convert a tree-sitter node to FunctionDef."""
        # Find function name
        name = self._find_child_text(node, "identifier", code_bytes)
        if name is None:
            name = self._find_child_text(node, "field_identifier", code_bytes)
        if name is None:
            return None

        # Calculate tokens
        body_node = self._find_child_by_type(
            node, ("block", "compound_statement", "statement_block")
        )
        body_tokens = self._count_tokens(body_node, code_bytes) if body_node else 0

        signature_tokens = self._count_signature_tokens(node, body_node, code_bytes)

        # Get line numbers
        start_line = node.start_point[0] + 1
        end_line = node.end_point[0] + 1

        # Calculate nesting depth
        nesting_depth = self._calculate_nesting_depth(body_node) if body_node else 0

        # Extract parameters
        params = self._extract_params(node, code_bytes, language)

        # Extract call targets
        call_targets = self._extract_call_targets(body_node, code_bytes, language)

        # Extract decorators (Python only)
        decorators = self._extract_decorators(node, code_bytes, language)

        return FunctionDef(
            name=name,
            params=params,
            body_tokens=body_tokens,
            signature_tokens=max(signature_tokens, 1),
            nesting_depth=nesting_depth,
            start_line=start_line,
            end_line=end_line,
            call_targets=call_targets,
            decorators=decorators,
        )

    def _extract_classes(self, tree: Any, code_bytes: bytes, language: str) -> list[ClassDef]:
        """Extract class definitions from parse tree."""
        classes: list[ClassDef] = []

        query_str = get_query(language, "class")
        if query_str is None:
            return classes

        captures = self._parser.query(tree, query_str, language)  # type: ignore[union-attr]
        if not captures:
            return classes

        processed_nodes: set[int] = set()

        for node, capture_name in captures:
            # Only process class-level captures
            class_node = self._get_class_node(node, capture_name, language)
            if class_node is None:
                continue

            node_id = id(class_node)
            if node_id in processed_nodes:
                continue
            processed_nodes.add(node_id)

            cls = self._node_to_class(class_node, code_bytes, language)
            if cls is not None:
                classes.append(cls)

        return classes

    def _get_class_node(self, node: Any, capture_name: str, language: str) -> Any | None:
        """Get the class definition node from a capture."""
        class_types = {
            "python": ("class_definition",),
            "go": ("type_spec",),
            "typescript": (
                "class_declaration",
                "interface_declaration",
                "abstract_class_declaration",
            ),
            "javascript": ("class_declaration",),
            "java": ("class_declaration", "interface_declaration", "enum_declaration"),
            "rust": ("struct_item", "enum_item", "trait_item"),
            "ruby": ("class", "module"),
            "c": ("struct_specifier", "union_specifier", "enum_specifier"),
            "cpp": ("struct_specifier", "class_specifier", "union_specifier", "enum_specifier"),
        }
        allowed = class_types.get(language, ())

        if capture_name.endswith(".name"):
            parent = node.parent
            while parent is not None:
                if parent.type in allowed:
                    return parent
                # For Go, check parent of parent (type_declaration -> type_spec)
                if parent.type == "type_spec":
                    return parent
                parent = parent.parent
            return None

        if node.type in allowed or node.type == "type_spec":
            return node
        return None

    def _node_to_class(self, node: Any, code_bytes: bytes, language: str) -> ClassDef | None:
        """Convert a tree-sitter node to ClassDef."""
        # Find class name
        name = self._find_child_text(node, "identifier", code_bytes)
        if name is None:
            name = self._find_child_text(node, "type_identifier", code_bytes)
        if name is None:
            name = self._find_child_text(node, "constant", code_bytes)  # Ruby
        if name is None:
            return None

        # Extract base classes
        bases = self._extract_bases(node, code_bytes, language)

        # Detect if abstract
        is_abstract = self._detect_abstract_class(node, code_bytes, language)

        # Methods would require nested parsing - skip for now
        methods: list[FunctionDef] = []
        fields: list[str] = []

        return ClassDef(
            name=name,
            bases=bases,
            methods=methods,
            fields=fields,
            is_abstract=is_abstract,
        )

    def _extract_imports(self, tree: Any, code_bytes: bytes, language: str) -> list[ImportDecl]:
        """Extract import declarations from parse tree."""
        imports: list[ImportDecl] = []

        query_str = get_query(language, "import")
        if query_str is None:
            return imports

        captures = self._parser.query(tree, query_str, language)  # type: ignore[union-attr]
        if not captures:
            return imports

        processed_sources: set[str] = set()

        for node, capture_name in captures:
            source = self._extract_import_source(node, capture_name, code_bytes, language)
            if source and source not in processed_sources:
                processed_sources.add(source)
                imports.append(
                    ImportDecl(
                        source=source,
                        names=[],
                        resolved_path=None,
                    )
                )

        return imports

    def _detect_main_guard(self, tree: Any, code_bytes: bytes, language: str) -> bool:
        """Detect if __name__ == '__main__' guard exists."""
        if language != "python":
            return False

        # Simple text search is more reliable than complex queries
        content = code_bytes.decode("utf-8", errors="ignore")
        return "__name__" in content and "__main__" in content and "if" in content

    def _find_child_text(self, node: Any, child_type: str, code_bytes: bytes) -> str | None:
        """Find first child of type and return its text."""
        for child in node.children:
            if child.type == child_type:
                if child.text:
                    return str(child.text.decode("utf-8", errors="ignore"))
            # Check grandchildren (for decorated definitions)
            result = self._find_child_text(child, child_type, code_bytes)
            if result:
                return result
        return None

    def _find_child_by_type(self, node: Any, types: tuple[str, ...]) -> Any | None:
        """Find first child matching one of the types."""
        for child in node.children:
            if child.type in types:
                return child
            # Recurse
            result = self._find_child_by_type(child, types)
            if result:
                return result
        return None

    def _count_tokens(self, node: Any, code_bytes: bytes) -> int:
        """Count tokens in a node (approximate by whitespace split)."""
        if node is None or node.text is None:
            return 0
        text = node.text.decode("utf-8", errors="ignore")
        return len(text.split())

    def _count_signature_tokens(self, node: Any, body_node: Any | None, code_bytes: bytes) -> int:
        """Count tokens in function signature (excluding body)."""
        if node.text is None:
            return 1

        full_text = node.text.decode("utf-8", errors="ignore")
        if body_node and body_node.text:
            body_text = body_node.text.decode("utf-8", errors="ignore")
            # Signature is everything before body
            sig_text = full_text.replace(body_text, "")
            return len(sig_text.split())
        return len(full_text.split())

    def _calculate_nesting_depth(self, node: Any) -> int:
        """Calculate maximum nesting depth in a node."""
        if node is None:
            return 0

        nesting_types = {
            "if_statement",
            "for_statement",
            "while_statement",
            "try_statement",
            "with_statement",
            "match_statement",
            "for_in_statement",
            "if_expression",
            "while_expression",
            "loop_expression",
        }

        def count_depth(n: Any, current_depth: int) -> int:
            max_depth = current_depth
            for child in n.children:
                child_depth = current_depth
                if child.type in nesting_types:
                    child_depth = current_depth + 1
                max_depth = max(max_depth, count_depth(child, child_depth))
            return max_depth

        return count_depth(node, 0)

    def _extract_params(self, node: Any, code_bytes: bytes, language: str) -> list[str]:
        """Extract parameter names from function node."""
        params: list[str] = []

        param_node = self._find_child_by_type(
            node, ("parameters", "formal_parameters", "parameter_list", "method_parameters")
        )
        if param_node is None:
            return params

        for child in param_node.children:
            if child.type == "identifier":
                if child.text:
                    params.append(child.text.decode("utf-8", errors="ignore"))
            # Handle typed parameters
            name_node = self._find_child_by_type(child, ("identifier",))
            if name_node and name_node.text:
                param_name = name_node.text.decode("utf-8", errors="ignore")
                if param_name not in params:
                    params.append(param_name)

        return params

    def _extract_call_targets(
        self, body_node: Any | None, code_bytes: bytes, language: str
    ) -> list[str]:
        """Extract call targets from function body."""
        if body_node is None:
            return []

        targets: list[str] = []

        def collect_calls(n: Any) -> None:
            if n.type in ("call", "call_expression", "method_invocation"):
                # Try to get function/method name
                for child in n.children:
                    if child.type == "identifier" and child.text:
                        targets.append(child.text.decode("utf-8", errors="ignore"))
                        break
                    if child.type in ("attribute", "member_expression", "field_expression"):
                        # Get the method name
                        for gc in child.children:
                            if gc.type in ("identifier", "property_identifier", "field_identifier"):
                                if gc.text:
                                    targets.append(gc.text.decode("utf-8", errors="ignore"))
                                    break

            for child in n.children:
                collect_calls(child)

        collect_calls(body_node)
        return targets

    def _extract_decorators(self, node: Any, code_bytes: bytes, language: str) -> list[str]:
        """Extract decorator names (Python only)."""
        if language != "python":
            return []

        decorators: list[str] = []

        # For decorated_definition, decorators are siblings
        if node.type == "decorated_definition":
            for child in node.children:
                if child.type == "decorator":
                    dec_text = self._get_decorator_name(child, code_bytes)
                    if dec_text:
                        decorators.append(dec_text)
        else:
            # Check parent for decorators
            parent = node.parent
            if parent and parent.type == "decorated_definition":
                for child in parent.children:
                    if child.type == "decorator":
                        dec_text = self._get_decorator_name(child, code_bytes)
                        if dec_text:
                            decorators.append(dec_text)

        return decorators

    def _get_decorator_name(self, node: Any, code_bytes: bytes) -> str | None:
        """Get decorator name from decorator node."""
        for child in node.children:
            if child.type == "identifier" and child.text:
                return str(child.text.decode("utf-8", errors="ignore"))
            if child.type == "attribute" and child.text:
                return str(child.text.decode("utf-8", errors="ignore"))
            if child.type == "call":
                # Get the function being called
                for gc in child.children:
                    if gc.type in ("identifier", "attribute") and gc.text:
                        return str(gc.text.decode("utf-8", errors="ignore"))
        return None

    def _extract_bases(self, node: Any, code_bytes: bytes, language: str) -> list[str]:
        """Extract base class names."""
        bases: list[str] = []

        if language == "python":
            # argument_list under class_definition
            for child in node.children:
                if child.type == "argument_list":
                    for gc in child.children:
                        if gc.type == "identifier" and gc.text:
                            bases.append(gc.text.decode("utf-8", errors="ignore"))
                        if gc.type == "attribute" and gc.text:
                            bases.append(gc.text.decode("utf-8", errors="ignore"))

        elif language in ("typescript", "javascript"):
            # extends_clause
            for child in node.children:
                if child.type == "class_heritage":
                    for gc in child.children:
                        if gc.type == "extends_clause":
                            for ggc in gc.children:
                                if ggc.type == "identifier" and ggc.text:
                                    bases.append(ggc.text.decode("utf-8", errors="ignore"))

        elif language == "java":
            for child in node.children:
                if child.type == "superclass":
                    for gc in child.children:
                        if gc.type == "type_identifier" and gc.text:
                            bases.append(gc.text.decode("utf-8", errors="ignore"))

        return bases

    def _detect_abstract_class(self, node: Any, code_bytes: bytes, language: str) -> bool:
        """Detect if class is abstract."""
        if language == "python":
            bases = self._extract_bases(node, code_bytes, language)
            return "ABC" in bases or "Protocol" in bases

        if language == "java":
            # Check for abstract modifier
            for child in node.children:
                if child.type == "modifiers":
                    if child.text and b"abstract" in child.text:
                        return True

        if language == "typescript":
            return bool(node.type == "abstract_class_declaration")

        if language == "rust":
            return bool(node.type == "trait_item")

        return False

    def _extract_import_source(
        self, node: Any, capture_name: str, code_bytes: bytes, language: str
    ) -> str | None:
        """Extract import source from capture."""
        if node.text is None:
            return None

        text: str = str(node.text.decode("utf-8", errors="ignore"))

        # Strip quotes for string paths
        if text.startswith(("'", '"', "<")):
            text = text.strip("'\"<>")

        # For dotted names, return as-is
        if "." in text or "/" in text:
            return text

        # Skip if it's just a name capture
        if capture_name.endswith(".name") or capture_name.endswith(".alias"):
            return None

        return text if text else None

    def _count_file_tokens(self, tree: Any) -> int:
        """Count tokens in entire file from tree-sitter tree."""
        if tree is None or tree.root_node is None:
            return 0

        # Count leaf nodes (tokens) in the tree
        def count_leaves(node: Any) -> int:
            if not node.children:
                return 1
            return sum(count_leaves(child) for child in node.children)

        return count_leaves(tree.root_node)

    def _compute_complexity(self, functions: list[FunctionDef]) -> float:
        """Compute cyclomatic complexity from functions."""
        if not functions:
            return 1.0

        # Sum of nesting depths + 1 per function, averaged
        total_complexity = sum(fn.nesting_depth + 1 for fn in functions)
        return total_complexity / len(functions)
