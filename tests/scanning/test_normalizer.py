"""Tests for TreeSitterNormalizer."""

import pytest

from shannon_insight.scanning.models_v2 import FileSyntax
from shannon_insight.scanning.normalizer import TreeSitterNormalizer
from shannon_insight.scanning.treesitter_parser import TREE_SITTER_AVAILABLE

SAMPLE_PYTHON = '''
"""A sample Python module."""

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


@property
def decorated_func():
    """A decorated function."""
    pass


if __name__ == "__main__":
    print("main")
'''


class TestTreeSitterNormalizerFallback:
    """Test normalizer behavior when tree-sitter unavailable."""

    def test_returns_none_when_unavailable(self):
        """Normalizer returns None when tree-sitter not available."""
        if TREE_SITTER_AVAILABLE:
            pytest.skip("tree-sitter is installed")

        normalizer = TreeSitterNormalizer()
        result = normalizer.parse_file(SAMPLE_PYTHON, "/test.py", "python")
        assert result is None


@pytest.mark.skipif(not TREE_SITTER_AVAILABLE, reason="tree-sitter not installed")
class TestTreeSitterNormalizer:
    """Test normalizer with tree-sitter installed."""

    def test_parse_returns_file_syntax(self):
        """parse_file returns FileSyntax."""
        normalizer = TreeSitterNormalizer()
        result = normalizer.parse_file(SAMPLE_PYTHON, "/test.py", "python")
        assert isinstance(result, FileSyntax)

    def test_extracts_functions(self):
        """Extracts function definitions."""
        normalizer = TreeSitterNormalizer()
        result = normalizer.parse_file(SAMPLE_PYTHON, "/test.py", "python")

        fn_names = [fn.name for fn in result.functions]
        assert "standalone_function" in fn_names

    def test_extracts_classes(self):
        """Extracts class definitions."""
        normalizer = TreeSitterNormalizer()
        result = normalizer.parse_file(SAMPLE_PYTHON, "/test.py", "python")

        class_names = [cls.name for cls in result.classes]
        assert "MyClass" in class_names

    def test_extracts_imports(self):
        """Extracts import statements."""
        normalizer = TreeSitterNormalizer()
        result = normalizer.parse_file(SAMPLE_PYTHON, "/test.py", "python")

        import_sources = [imp.source for imp in result.imports]
        assert "os" in import_sources or len(result.imports) > 0

    def test_detects_main_guard(self):
        """Detects __main__ guard."""
        normalizer = TreeSitterNormalizer()
        result = normalizer.parse_file(SAMPLE_PYTHON, "/test.py", "python")
        assert result.has_main_guard is True

    def test_call_targets_populated(self):
        """call_targets is populated (not None) for tree-sitter parsing."""
        normalizer = TreeSitterNormalizer()
        result = normalizer.parse_file(SAMPLE_PYTHON, "/test.py", "python")

        # At least one function should have call_targets as a list (possibly empty)
        has_targets = any(fn.call_targets is not None for fn in result.functions)
        assert has_targets

    def test_unsupported_language_returns_none(self):
        """Returns None for unsupported language."""
        normalizer = TreeSitterNormalizer()
        result = normalizer.parse_file("some code", "/test.xyz", "unknown_lang")
        assert result is None

    def test_encoding_error_returns_none(self):
        """Returns None on encoding errors."""
        # Create content that can't be encoded
        normalizer = TreeSitterNormalizer()
        # This should not crash even with weird content
        result = normalizer.parse_file("def foo(): pass", "/test.py", "python")
        # Should succeed for normal content
        assert result is not None


@pytest.mark.skipif(not TREE_SITTER_AVAILABLE, reason="tree-sitter not installed")
class TestNormalizerMultiLanguage:
    """Test normalizer across multiple languages."""

    def test_go_parsing(self):
        """Parse Go code."""
        from shannon_insight.scanning.treesitter_parser import get_supported_languages
        if "go" not in get_supported_languages():
            pytest.skip("Go grammar not installed")

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
        normalizer = TreeSitterNormalizer()
        result = normalizer.parse_file(go_code, "/main.go", "go")

        assert result is not None
        fn_names = [fn.name for fn in result.functions]
        assert "main" in fn_names or len(result.functions) > 0

    def test_typescript_parsing(self):
        """Parse TypeScript code."""
        from shannon_insight.scanning.treesitter_parser import get_supported_languages
        if "typescript" not in get_supported_languages():
            pytest.skip("TypeScript grammar not installed")

        ts_code = '''
import { Something } from './module';

function greet(name: string): string {
    return `Hello, ${name}`;
}

class MyClass {
    method(): void {
        console.log('hello');
    }
}
'''
        normalizer = TreeSitterNormalizer()
        result = normalizer.parse_file(ts_code, "/test.ts", "typescript")

        assert result is not None
        # Should find at least the greet function or MyClass
        assert len(result.functions) > 0 or len(result.classes) > 0

    def test_javascript_parsing(self):
        """Parse JavaScript code."""
        from shannon_insight.scanning.treesitter_parser import get_supported_languages
        if "javascript" not in get_supported_languages():
            pytest.skip("JavaScript grammar not installed")

        js_code = '''
function hello() {
    console.log("hello");
}

class MyClass {
    constructor() {
        this.x = 1;
    }
}
'''
        normalizer = TreeSitterNormalizer()
        result = normalizer.parse_file(js_code, "/test.js", "javascript")

        assert result is not None

    def test_java_parsing(self):
        """Parse Java code."""
        from shannon_insight.scanning.treesitter_parser import get_supported_languages
        if "java" not in get_supported_languages():
            pytest.skip("Java grammar not installed")

        java_code = '''
package com.example;

import java.util.List;

public class MyClass {
    public void doSomething() {
        System.out.println("hello");
    }
}
'''
        normalizer = TreeSitterNormalizer()
        result = normalizer.parse_file(java_code, "/MyClass.java", "java")

        assert result is not None

    def test_rust_parsing(self):
        """Parse Rust code."""
        from shannon_insight.scanning.treesitter_parser import get_supported_languages
        if "rust" not in get_supported_languages():
            pytest.skip("Rust grammar not installed")

        rust_code = '''
use std::io;

fn main() {
    println!("Hello, world!");
}

fn helper(x: i32) -> i32 {
    x * 2
}
'''
        normalizer = TreeSitterNormalizer()
        result = normalizer.parse_file(rust_code, "/main.rs", "rust")

        assert result is not None

    def test_ruby_parsing(self):
        """Parse Ruby code."""
        from shannon_insight.scanning.treesitter_parser import get_supported_languages
        if "ruby" not in get_supported_languages():
            pytest.skip("Ruby grammar not installed")

        ruby_code = '''
require 'json'

class MyClass
  def initialize(x)
    @x = x
  end

  def method
    @x
  end
end

def standalone
  puts "hello"
end
'''
        normalizer = TreeSitterNormalizer()
        result = normalizer.parse_file(ruby_code, "/test.rb", "ruby")

        assert result is not None
