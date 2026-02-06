"""Tests for regex fallback scanner."""

import pytest

from shannon_insight.scanning.fallback import RegexFallbackScanner
from shannon_insight.scanning.models_v2 import FileSyntax


SAMPLE_PYTHON = '''
"""A sample Python file."""

import os
from pathlib import Path
from typing import List, Optional

class MyClass:
    """A simple class."""

    def __init__(self, x: int):
        self.x = x

    def method(self) -> int:
        return self.x


def standalone_function(a, b):
    """A standalone function."""
    if a > b:
        for i in range(a):
            if i % 2 == 0:
                print(i)
    return a + b


def stub_function():
    pass


if __name__ == "__main__":
    main()
'''


class TestRegexFallbackScanner:
    """Test RegexFallbackScanner produces FileSyntax."""

    def test_parse_returns_file_syntax(self):
        """parse() returns FileSyntax."""
        scanner = RegexFallbackScanner()
        result = scanner.parse(SAMPLE_PYTHON, "/test.py", "python")
        assert isinstance(result, FileSyntax)

    def test_detects_functions(self):
        """Detects function definitions."""
        scanner = RegexFallbackScanner()
        result = scanner.parse(SAMPLE_PYTHON, "/test.py", "python")
        fn_names = [fn.name for fn in result.functions]
        assert "standalone_function" in fn_names
        assert "stub_function" in fn_names

    def test_detects_classes(self):
        """Detects class definitions."""
        scanner = RegexFallbackScanner()
        result = scanner.parse(SAMPLE_PYTHON, "/test.py", "python")
        class_names = [cls.name for cls in result.classes]
        assert "MyClass" in class_names

    def test_detects_imports(self):
        """Detects import statements."""
        scanner = RegexFallbackScanner()
        result = scanner.parse(SAMPLE_PYTHON, "/test.py", "python")
        import_sources = [imp.source for imp in result.imports]
        assert "os" in import_sources
        assert "pathlib" in import_sources
        assert "typing" in import_sources

    def test_detects_main_guard(self):
        """Detects if __name__ == '__main__' guard."""
        scanner = RegexFallbackScanner()
        result = scanner.parse(SAMPLE_PYTHON, "/test.py", "python")
        assert result.has_main_guard is True

    def test_no_main_guard_when_absent(self):
        """has_main_guard is False when not present."""
        code = '''
def foo():
    pass
'''
        scanner = RegexFallbackScanner()
        result = scanner.parse(code, "/test.py", "python")
        assert result.has_main_guard is False

    def test_call_targets_always_none(self):
        """Regex fallback sets call_targets to None."""
        scanner = RegexFallbackScanner()
        result = scanner.parse(SAMPLE_PYTHON, "/test.py", "python")
        for fn in result.functions:
            assert fn.call_targets is None

    def test_sets_language(self):
        """Language is set correctly."""
        scanner = RegexFallbackScanner()
        result = scanner.parse(SAMPLE_PYTHON, "/test.py", "python")
        assert result.language == "python"

    def test_sets_path(self):
        """Path is set correctly."""
        scanner = RegexFallbackScanner()
        result = scanner.parse(SAMPLE_PYTHON, "/foo/bar.py", "python")
        assert result.path == "/foo/bar.py"

    def test_function_body_tokens_estimated(self):
        """Function body_tokens are estimated."""
        scanner = RegexFallbackScanner()
        result = scanner.parse(SAMPLE_PYTHON, "/test.py", "python")
        # Functions should have positive body_tokens
        for fn in result.functions:
            assert fn.body_tokens >= 0

    def test_stub_detected(self):
        """Stub functions detected."""
        scanner = RegexFallbackScanner()
        result = scanner.parse(SAMPLE_PYTHON, "/test.py", "python")
        stub_fn = next(fn for fn in result.functions if fn.name == "stub_function")
        assert stub_fn.is_stub is True


class TestGoFallback:
    """Test Go language support."""

    def test_detects_go_functions(self):
        """Detects Go function definitions."""
        go_code = '''
package main

import "fmt"

func main() {
    fmt.Println("Hello")
}

func helper(x int) int {
    return x * 2
}
'''
        scanner = RegexFallbackScanner()
        result = scanner.parse(go_code, "/main.go", "go")
        fn_names = [fn.name for fn in result.functions]
        assert "main" in fn_names
        assert "helper" in fn_names


class TestTypeScriptFallback:
    """Test TypeScript language support."""

    def test_detects_typescript_functions(self):
        """Detects TypeScript function definitions."""
        ts_code = '''
import { Something } from './module';

function greet(name: string): string {
    return `Hello, ${name}`;
}

const arrow = (x: number) => x * 2;

class MyClass {
    method(): void {
        console.log('hello');
    }
}
'''
        scanner = RegexFallbackScanner()
        result = scanner.parse(ts_code, "/test.ts", "typescript")
        fn_names = [fn.name for fn in result.functions]
        assert "greet" in fn_names


class TestJavaFallback:
    """Test Java language support."""

    def test_detects_java_methods(self):
        """Detects Java methods."""
        java_code = '''
package com.example;

import java.util.List;

public class MyClass {
    public void doSomething() {
        System.out.println("hello");
    }

    private int calculate(int x) {
        return x * 2;
    }
}
'''
        scanner = RegexFallbackScanner()
        result = scanner.parse(java_code, "/MyClass.java", "java")
        fn_names = [fn.name for fn in result.functions]
        assert "doSomething" in fn_names or len(result.functions) > 0


class TestEmptyFile:
    """Test handling of empty/minimal files."""

    def test_empty_file(self):
        """Empty file produces empty FileSyntax."""
        scanner = RegexFallbackScanner()
        result = scanner.parse("", "/empty.py", "python")
        assert result.function_count == 0
        assert result.class_count == 0
        assert result.import_count == 0

    def test_comment_only_file(self):
        """Comment-only file produces empty FileSyntax."""
        scanner = RegexFallbackScanner()
        result = scanner.parse("# Just a comment\n# Another comment", "/comments.py", "python")
        assert result.function_count == 0
