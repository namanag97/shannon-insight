"""Regex-based fallback scanner.

Used when tree-sitter is unavailable or fails to parse a file.
Produces FileSyntax with call_targets=None to indicate fallback mode.

Supports: Python, Go, TypeScript, JavaScript, Java, Rust, Ruby, C/C++
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .syntax import ClassDef, FileSyntax, FunctionDef, ImportDecl


@dataclass
class RegexFallbackScanner:
    """Regex-based scanner that produces FileSyntax.

    This is a best-effort scanner for when tree-sitter is unavailable.
    Results are approximate but sufficient for basic analysis.
    """

    def parse(self, content: str, path: str, language: str) -> FileSyntax:
        """Parse file content and return FileSyntax.

        Args:
            content: File content as string
            path: File path
            language: Detected language

        Returns:
            FileSyntax with call_targets=None for all functions
        """
        functions = self._extract_functions(content, language)
        classes = self._extract_classes(content, language)
        imports = self._extract_imports(content, language)
        has_main = self._detect_main_guard(content, language)

        return FileSyntax(
            path=path,
            functions=functions,
            classes=classes,
            imports=imports,
            language=language,
            has_main_guard=has_main,
        )

    def _extract_functions(self, content: str, language: str) -> list[FunctionDef]:
        """Extract function definitions using regex."""
        functions: list[FunctionDef] = []

        patterns = self._get_function_patterns(language)
        for pattern in patterns:
            for match in re.finditer(pattern, content, re.MULTILINE):
                name = self._extract_name_from_match(match)
                if not name:
                    continue

                # Find line numbers
                start_pos = match.start()
                start_line = content[:start_pos].count("\n") + 1

                # Estimate function body (simple heuristic)
                body_start = match.end()
                body_tokens, end_line = self._estimate_body(
                    content, body_start, start_line, language
                )

                # Estimate signature tokens
                signature_tokens = len(match.group().split())

                functions.append(
                    FunctionDef(
                        name=name,
                        params=self._extract_params(match, language),
                        body_tokens=body_tokens,
                        signature_tokens=max(signature_tokens, 1),
                        nesting_depth=self._estimate_nesting(content, start_line, end_line),
                        start_line=start_line,
                        end_line=end_line,
                        call_targets=None,  # Always None for regex fallback
                        decorators=[],  # Cannot reliably extract with regex
                    )
                )

        return functions

    def _extract_classes(self, content: str, language: str) -> list[ClassDef]:
        """Extract class definitions using regex."""
        classes: list[ClassDef] = []

        patterns = self._get_class_patterns(language)
        for pattern in patterns:
            for match in re.finditer(pattern, content, re.MULTILINE):
                name = self._extract_class_name(match, language)
                if not name:
                    continue

                bases = self._extract_bases(match, language)

                classes.append(
                    ClassDef(
                        name=name,
                        bases=bases,
                        methods=[],  # Would need nested parsing
                        fields=[],  # Would need nested parsing
                        is_abstract=self._detect_abstract(match, content, language),
                    )
                )

        return classes

    def _extract_imports(self, content: str, language: str) -> list[ImportDecl]:
        """Extract import declarations using regex."""
        imports: list[ImportDecl] = []

        patterns = self._get_import_patterns(language)
        for pattern in patterns:
            for match in re.finditer(pattern, content, re.MULTILINE):
                source, names = self._parse_import_match(match, language)
                if source:
                    imports.append(
                        ImportDecl(
                            source=source,
                            names=names,
                            resolved_path=None,  # Resolution happens later
                        )
                    )

        return imports

    def _detect_main_guard(self, content: str, language: str) -> bool:
        """Detect if __name__ == '__main__' or equivalent."""
        if language == "python":
            return bool(re.search(r'if\s+__name__\s*==\s*["\']__main__["\']', content))
        return False

    def _get_function_patterns(self, language: str) -> list[str]:
        """Get regex patterns for function definitions."""
        patterns: dict[str, list[str]] = {
            "python": [r"^\s*(?:async\s+)?def\s+(\w+)\s*\([^)]*\)"],
            "go": [r"^func\s+(\w+)\s*\([^)]*\)"],
            "typescript": [
                r"^(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\([^)]*\)",
                r"^\s*(\w+)\s*\([^)]*\)\s*{",  # method shorthand
            ],
            "javascript": [
                r"^(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\([^)]*\)",
                r"^\s*(\w+)\s*\([^)]*\)\s*{",
            ],
            "java": [
                r"(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+\w+)?\s*{"
            ],
            "rust": [r"^(?:pub\s+)?(?:async\s+)?fn\s+(\w+)"],
            "ruby": [r"^\s*def\s+(\w+)"],
            "c": [r"^\w+\s+(\w+)\s*\([^)]*\)\s*{"],
            "cpp": [r"^\w+(?:::\w+)*\s+(\w+)\s*\([^)]*\)\s*(?:const)?\s*{"],
        }
        return patterns.get(language, patterns.get("python", []))

    def _get_class_patterns(self, language: str) -> list[str]:
        """Get regex patterns for class definitions."""
        patterns: dict[str, list[str]] = {
            "python": [r"^\s*class\s+(\w+)(?:\s*\([^)]*\))?:"],
            "go": [r"^type\s+(\w+)\s+struct\s*{"],
            "typescript": [r"^(?:export\s+)?class\s+(\w+)"],
            "javascript": [r"^(?:export\s+)?class\s+(\w+)"],
            "java": [r"(?:public\s+)?class\s+(\w+)"],
            "rust": [r"^(?:pub\s+)?struct\s+(\w+)"],
            "ruby": [r"^\s*class\s+(\w+)"],
            "cpp": [r"^class\s+(\w+)"],
        }
        return patterns.get(language, [])

    def _get_import_patterns(self, language: str) -> list[str]:
        """Get regex patterns for import declarations."""
        patterns: dict[str, list[str]] = {
            "python": [
                r"^import\s+([\w.]+)",
                r"^from\s+([\w.]+)\s+import",
            ],
            "go": [r'^import\s+"([^"]+)"', r'^import\s+\w+\s+"([^"]+)"'],
            "typescript": [r"^import\s+.*from\s+['\"]([^'\"]+)['\"]"],
            "javascript": [
                r"^import\s+.*from\s+['\"]([^'\"]+)['\"]",
                r"require\(['\"]([^'\"]+)['\"]\)",
            ],
            "java": [r"^import\s+([\w.]+);"],
            "rust": [r"^use\s+([\w:]+)"],
            "ruby": [r"^require\s+['\"]([^'\"]+)['\"]", r"^require_relative\s+['\"]([^'\"]+)['\"]"],
        }
        return patterns.get(language, [])

    def _extract_name_from_match(self, match: re.Match[str]) -> str | None:
        """Extract function name from regex match."""
        if match.groups():
            name: str = match.group(1)
            return name
        return None

    def _extract_class_name(self, match: re.Match[str], language: str) -> str | None:
        """Extract class name from regex match."""
        if match.groups():
            name: str = match.group(1)
            return name
        return None

    def _extract_params(self, match: re.Match, language: str) -> list[str]:
        """Extract parameter names (best effort)."""
        # This is very approximate
        full_match = match.group(0)
        paren_match = re.search(r"\(([^)]*)\)", full_match)
        if paren_match:
            params_str = paren_match.group(1)
            # Simple split, doesn't handle complex types
            params = [p.strip().split()[0] for p in params_str.split(",") if p.strip()]
            return [p.split(":")[0].strip() for p in params if p]
        return []

    def _extract_bases(self, match: re.Match, language: str) -> list[str]:
        """Extract base class names."""
        full_match = match.group(0)
        if language == "python":
            paren_match = re.search(r"\(([^)]+)\)", full_match)
            if paren_match:
                return [b.strip() for b in paren_match.group(1).split(",")]
        return []

    def _detect_abstract(self, match: re.Match, content: str, language: str) -> bool:
        """Detect if class is abstract."""
        if language == "python":
            full_match = match.group(0)
            return "ABC" in full_match or "Protocol" in full_match
        if language == "java":
            return "abstract" in match.group(0).lower()
        return False

    def _parse_import_match(self, match: re.Match, language: str) -> tuple[str, list[str]]:
        """Parse import match to get source and names."""
        if match.groups():
            source = match.group(1)
            return source, []
        return "", []

    def _estimate_body(
        self, content: str, start: int, start_line: int, language: str
    ) -> tuple[int, int]:
        """Estimate function body tokens and end line."""
        # Simple heuristic: count tokens until we see dedent or matching brace
        lines = content[start:].split("\n")

        if language == "python":
            # Look for dedent
            body_lines = 0
            for line in lines:
                if line.strip() and not line.startswith(" ") and not line.startswith("\t"):
                    break
                body_lines += 1
            body_tokens = sum(len(line.split()) for line in lines[:body_lines])
            return body_tokens, start_line + body_lines

        # For brace-based languages, count until closing brace
        brace_count = 1
        token_count = 0
        line_count = 0

        for line in lines:
            line_count += 1
            brace_count += line.count("{") - line.count("}")
            token_count += len(line.split())
            if brace_count <= 0:
                break

        return token_count, start_line + line_count

    def _estimate_nesting(self, content: str, start_line: int, end_line: int) -> int:
        """Estimate nesting depth in function."""
        lines = content.split("\n")[start_line - 1 : end_line]
        max_indent = 0
        base_indent = None

        for line in lines:
            if not line.strip():
                continue
            indent = len(line) - len(line.lstrip())
            if base_indent is None:
                base_indent = indent
            relative_indent = indent - (base_indent or 0)
            # Estimate nesting: 4 spaces or 1 tab = 1 level
            nesting = relative_indent // 4
            max_indent = max(max_indent, nesting)

        return max_indent
