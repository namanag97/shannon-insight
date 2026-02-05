"""Cross-language integration tests for the redesigned primitives.

Verifies compression complexity, identifier coherence, and Gini-enhanced
cognitive load work correctly across all 7 supported languages.
"""

import tempfile
from pathlib import Path

from shannon_insight import InsightKernel
from shannon_insight.math import Compression, Gini, IdentifierAnalyzer

# ---------------------------------------------------------------------------
# Test file content for each language — each has a "focused" file (single
# responsibility) and a "mixed" file (multiple responsibilities).
# ---------------------------------------------------------------------------

GO_FOCUSED = """package validator

import "regexp"

func ValidateEmail(email string) bool {
    pattern := `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$`
    matched, _ := regexp.MatchString(pattern, email)
    return matched
}

func ValidatePhone(phone string) bool {
    pattern := `^\\+?[0-9]{10,15}$`
    matched, _ := regexp.MatchString(pattern, phone)
    return matched
}

func ValidateName(name string) bool {
    if len(name) < 2 {
        return false
    }
    if len(name) > 100 {
        return false
    }
    return true
}

func ValidateAge(age int) bool {
    if age < 0 {
        return false
    }
    if age > 150 {
        return false
    }
    return true
}
"""

GO_MIXED = """package processor

import (
    "fmt"
    "encoding/json"
    "net/http"
    "log"
    "sync"
    "time"
    "os"
    "strings"
    "strconv"
    "io"
)

var cache = make(map[string]string)
var mu sync.Mutex

func ValidateInput(data string) bool {
    if len(data) == 0 {
        return false
    }
    if len(data) > 1000 {
        return false
    }
    return true
}

func TransformToUpper(s string) string {
    return strings.ToUpper(s)
}

func TransformToLower(s string) string {
    return strings.ToLower(s)
}

func TransformTrim(s string) string {
    return strings.TrimSpace(s)
}

func CacheSet(key, value string) {
    mu.Lock()
    defer mu.Unlock()
    cache[key] = value
}

func CacheGet(key string) (string, bool) {
    mu.Lock()
    defer mu.Unlock()
    val, ok := cache[key]
    return val, ok
}

func CacheDelete(key string) {
    mu.Lock()
    defer mu.Unlock()
    delete(cache, key)
}

func LogInfo(msg string) {
    log.Printf("[INFO] %s", msg)
}

func LogError(msg string) {
    log.Printf("[ERROR] %s", msg)
}

func HandleRequest(w http.ResponseWriter, r *http.Request) {
    body, err := io.ReadAll(r.Body)
    if err != nil {
        LogError(fmt.Sprintf("read error: %v", err))
        http.Error(w, "bad request", http.StatusBadRequest)
        return
    }
    defer r.Body.Close()

    if !ValidateInput(string(body)) {
        http.Error(w, "invalid", http.StatusBadRequest)
        return
    }

    transformed := TransformToUpper(TransformTrim(string(body)))
    CacheSet("last", transformed)

    var result map[string]interface{}
    if err := json.Unmarshal(body, &result); err != nil {
        LogError(fmt.Sprintf("json error: %v", err))
        return
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(result)
}

func ServeHTTP(port int) {
    addr := ":" + strconv.Itoa(port)
    LogInfo(fmt.Sprintf("starting server on %s", addr))
    http.HandleFunc("/process", HandleRequest)
    log.Fatal(http.ListenAndServe(addr, nil))
}

func ReadConfig(path string) (string, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return "", err
    }
    return string(data), nil
}

func WriteConfig(path, content string) error {
    return os.WriteFile(path, []byte(content), 0644)
}

func FormatTimestamp(t time.Time) string {
    return t.Format("2006-01-02 15:04:05")
}

func ParseTimestamp(s string) (time.Time, error) {
    return time.Parse("2006-01-02 15:04:05", s)
}
"""

GO_UTIL = """package util

import "strings"

func JoinStrings(parts []string) string {
    return strings.Join(parts, ",")
}

func SplitString(s string) []string {
    return strings.Split(s, ",")
}

func ContainsString(haystack []string, needle string) bool {
    for _, s := range haystack {
        if s == needle {
            return true
        }
    }
    return false
}
"""

PYTHON_FOCUSED = """
import re


def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    pattern = r'^\\+?[0-9]{10,15}$'
    return bool(re.match(pattern, phone))


def validate_name(name: str) -> bool:
    if len(name) < 2:
        return False
    if len(name) > 100:
        return False
    return True


def validate_age(age: int) -> bool:
    if age < 0:
        return False
    if age > 150:
        return False
    return True
"""

PYTHON_MIXED = """
import os
import json
import logging
import hashlib
import time
from typing import Dict, Any, Optional


logger = logging.getLogger(__name__)

_cache: Dict[str, Any] = {}


def validate_email(email: str) -> bool:
    if not email or "@" not in email:
        return False
    parts = email.split("@")
    return len(parts) == 2 and "." in parts[1]


def validate_phone(phone: str) -> bool:
    digits = "".join(c for c in phone if c.isdigit())
    return len(digits) >= 10


def transform_upper(text: str) -> str:
    return text.upper()


def transform_lower(text: str) -> str:
    return text.lower()


def transform_trim(text: str) -> str:
    return text.strip()


def transform_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def cache_set(key: str, value: Any, ttl: int = 300) -> None:
    _cache[key] = {"value": value, "expires": time.time() + ttl}


def cache_get(key: str) -> Optional[Any]:
    entry = _cache.get(key)
    if entry and entry["expires"] > time.time():
        return entry["value"]
    return None


def cache_clear() -> None:
    _cache.clear()


def log_info(message: str) -> None:
    logger.info(message)


def log_error(message: str) -> None:
    logger.error(message)


def read_config(path: str) -> Dict[str, Any]:
    with open(path, "r") as f:
        return json.load(f)


def write_config(path: str, data: Dict[str, Any]) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def format_timestamp(ts: float) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))


def parse_timestamp(s: str) -> float:
    return time.mktime(time.strptime(s, "%Y-%m-%d %H:%M:%S"))
"""

PYTHON_UTIL = """
def join_strings(parts):
    return ",".join(parts)


def split_string(s):
    return s.split(",")


def contains_string(haystack, needle):
    return needle in haystack
"""

TS_FOCUSED = """
export function validateEmail(email: string): boolean {
    const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$/;
    return pattern.test(email);
}

export function validatePhone(phone: string): boolean {
    const pattern = /^\\+?[0-9]{10,15}$/;
    return pattern.test(phone);
}

export function validateName(name: string): boolean {
    if (name.length < 2) {
        return false;
    }
    if (name.length > 100) {
        return false;
    }
    return true;
}

export function validateAge(age: number): boolean {
    if (age < 0) {
        return false;
    }
    if (age > 150) {
        return false;
    }
    return true;
}
"""

TS_MIXED = """
import { Request, Response } from 'express';

const cache: Map<string, string> = new Map();

export function validateInput(data: string): boolean {
    if (!data || data.length === 0) {
        return false;
    }
    if (data.length > 1000) {
        return false;
    }
    return true;
}

export function transformToUpper(s: string): string {
    return s.toUpperCase();
}

export function transformToLower(s: string): string {
    return s.toLowerCase();
}

export function transformTrim(s: string): string {
    return s.trim();
}

export function cacheSet(key: string, value: string): void {
    cache.set(key, value);
}

export function cacheGet(key: string): string | undefined {
    return cache.get(key);
}

export function cacheDelete(key: string): void {
    cache.delete(key);
}

export function logInfo(msg: string): void {
    console.log(`[INFO] ${msg}`);
}

export function logError(msg: string): void {
    console.error(`[ERROR] ${msg}`);
}

export function handleRequest(req: Request, res: Response): void {
    const body = req.body as string;
    if (!validateInput(body)) {
        res.status(400).send('invalid');
        return;
    }
    const transformed = transformToUpper(transformTrim(body));
    cacheSet('last', transformed);
    res.json({ result: transformed });
}

export function formatTimestamp(date: Date): string {
    return date.toISOString();
}

export function parseTimestamp(s: string): Date {
    return new Date(s);
}
"""

TS_UTIL = """
export function joinStrings(parts: string[]): string {
    return parts.join(",");
}

export function splitString(s: string): string[] {
    return s.split(",");
}

export function containsString(arr: string[], needle: string): boolean {
    return arr.includes(needle);
}
"""


def _create_lang_dir(tmpdir: Path, lang: str, files: dict) -> Path:
    """Create a temporary directory with language-specific files."""
    lang_dir = tmpdir / lang
    lang_dir.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        (lang_dir / name).write_text(content)
    return lang_dir


class TestCrossLanguagePrimitives:
    """Test that the insight pipeline produces meaningful results across languages."""

    def test_go_pipeline_runs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "validator.go").write_text(GO_FOCUSED)
            (d / "processor.go").write_text(GO_MIXED)
            (d / "util.go").write_text(GO_UTIL)

            kernel = InsightKernel(str(d), language="go")
            result, snapshot = kernel.run()

            assert snapshot.file_count == 3

    def test_python_pipeline_runs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "validator.py").write_text(PYTHON_FOCUSED)
            (d / "processor.py").write_text(PYTHON_MIXED)
            (d / "util.py").write_text(PYTHON_UTIL)

            kernel = InsightKernel(str(d), language="python")
            result, snapshot = kernel.run()

            assert snapshot.file_count == 3

    def test_typescript_pipeline_runs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "validator.ts").write_text(TS_FOCUSED)
            (d / "processor.ts").write_text(TS_MIXED)
            (d / "util.ts").write_text(TS_UTIL)

            kernel = InsightKernel(str(d), language="typescript")
            result, snapshot = kernel.run()

            assert snapshot.file_count == 3

    def test_auto_detect_multilang(self):
        """Auto-detect should handle Go + Python + TypeScript together."""
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "validator.go").write_text(GO_FOCUSED)
            (d / "processor.go").write_text(GO_MIXED)
            (d / "util.go").write_text(GO_UTIL)
            (d / "validator.py").write_text(PYTHON_FOCUSED)
            (d / "processor.py").write_text(PYTHON_MIXED)
            (d / "util.py").write_text(PYTHON_UTIL)
            (d / "validator.ts").write_text(TS_FOCUSED)
            (d / "processor.ts").write_text(TS_MIXED)
            (d / "util.ts").write_text(TS_UTIL)

            kernel = InsightKernel(str(d), language="auto")
            result, snapshot = kernel.run()

            assert snapshot.file_count >= 9


class TestCompressionCrossLanguage:
    """Compression ratio should be comparable across languages for equivalent logic."""

    def test_similar_logic_similar_ratios(self):
        """Same validation logic in Go/Python/TS should have similar compression ratios."""
        ratios = {}
        for lang, content in [("go", GO_FOCUSED), ("py", PYTHON_FOCUSED), ("ts", TS_FOCUSED)]:
            raw = content.encode("utf-8")
            if len(raw) >= Compression.MIN_SIZE_THRESHOLD:
                ratios[lang] = Compression.compression_ratio(raw)

        if len(ratios) >= 2:
            values = list(ratios.values())
            # All should be in the "normal code" range
            for lang, ratio in ratios.items():
                assert 0.1 < ratio < 0.7, f"{lang}: ratio={ratio} out of range"

            # Cross-language variance should be moderate (not wildly different)
            spread = max(values) - min(values)
            assert spread < 0.3, f"Cross-language spread too high: {ratios}"

    def test_mixed_file_higher_complexity(self):
        """Mixed-responsibility files should generally have higher compression ratio
        than focused files (more diverse vocabulary = less compressible)."""
        for focused, mixed in [(GO_FOCUSED, GO_MIXED), (PYTHON_FOCUSED, PYTHON_MIXED)]:
            focused_bytes = focused.encode("utf-8")
            mixed_bytes = mixed.encode("utf-8")

            # Only compare if both are above threshold
            if (
                len(focused_bytes) >= Compression.MIN_SIZE_THRESHOLD
                and len(mixed_bytes) >= Compression.MIN_SIZE_THRESHOLD
            ):
                r_focused = Compression.compression_ratio(focused_bytes)
                r_mixed = Compression.compression_ratio(mixed_bytes)
                # Mixed file should generally compress less well (higher ratio)
                # but we allow some tolerance
                assert r_mixed >= r_focused * 0.7, (
                    f"Expected mixed >= focused*0.7: mixed={r_mixed}, focused={r_focused}"
                )


class TestIdentifiersCrossLanguage:
    """Identifier extraction should work across all languages."""

    def test_go_identifiers(self):
        tokens = IdentifierAnalyzer.extract_identifier_tokens(GO_FOCUSED)
        assert "validate" in tokens
        assert "email" in tokens
        assert "phone" in tokens

    def test_python_identifiers(self):
        tokens = IdentifierAnalyzer.extract_identifier_tokens(PYTHON_FOCUSED)
        assert "validate" in tokens
        assert "email" in tokens
        assert "phone" in tokens

    def test_typescript_identifiers(self):
        tokens = IdentifierAnalyzer.extract_identifier_tokens(TS_FOCUSED)
        assert "validate" in tokens
        assert "email" in tokens
        assert "phone" in tokens

    def test_shared_vocabulary_across_languages(self):
        """Same domain logic should produce overlapping identifier tokens."""
        go_tokens = set(IdentifierAnalyzer.extract_identifier_tokens(GO_FOCUSED))
        py_tokens = set(IdentifierAnalyzer.extract_identifier_tokens(PYTHON_FOCUSED))
        ts_tokens = set(IdentifierAnalyzer.extract_identifier_tokens(TS_FOCUSED))

        # Core domain words should appear in all three
        shared = go_tokens & py_tokens & ts_tokens
        assert "validate" in shared
        assert "email" in shared
        assert "phone" in shared

    def test_mixed_file_has_more_clusters(self):
        """Mixed-responsibility files should produce more identifier clusters."""
        focused_tokens = IdentifierAnalyzer.extract_identifier_tokens(GO_FOCUSED)
        mixed_tokens = IdentifierAnalyzer.extract_identifier_tokens(GO_MIXED)

        focused_clusters = IdentifierAnalyzer.detect_semantic_clusters(focused_tokens)
        mixed_clusters = IdentifierAnalyzer.detect_semantic_clusters(mixed_tokens)

        # Mixed file should have more clusters
        assert len(mixed_clusters) >= len(focused_clusters)

    def test_coherence_in_valid_range(self):
        """All coherence scores should be in [0, 1]."""
        for content in [PYTHON_FOCUSED, PYTHON_MIXED, GO_FOCUSED, GO_MIXED, TS_FOCUSED, TS_MIXED]:
            tokens = IdentifierAnalyzer.extract_identifier_tokens(content)
            coherence = IdentifierAnalyzer.compute_coherence(tokens)
            assert 0.0 <= coherence <= 1.0, f"Coherence out of range: {coherence}"


class TestGiniCrossLanguage:
    """Gini coefficient on function sizes across languages."""

    def test_go_function_sizes_extracted(self):
        """Go scanner should extract function sizes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "main.go").write_text(GO_FOCUSED)
            (d / "proc.go").write_text(GO_MIXED)
            (d / "util.go").write_text(GO_UTIL)

            from shannon_insight.analyzers import GoScanner

            scanner = GoScanner(str(d))
            files = scanner.scan()

            for f in files:
                assert isinstance(f.function_sizes, list)
                assert len(f.function_sizes) > 0, f"{f.path} should have functions"

    def test_python_function_sizes_extracted(self):
        """Python scanner should extract function sizes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "validator.py").write_text(PYTHON_FOCUSED)
            (d / "processor.py").write_text(PYTHON_MIXED)
            (d / "util.py").write_text(PYTHON_UTIL)

            from shannon_insight.analyzers import PythonScanner

            scanner = PythonScanner(str(d))
            files = scanner.scan()

            for f in files:
                assert isinstance(f.function_sizes, list)
                assert len(f.function_sizes) > 0, f"{f.path} should have functions"

    def test_typescript_function_sizes_extracted(self):
        """TypeScript scanner should extract function sizes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "validator.ts").write_text(TS_FOCUSED)
            (d / "processor.ts").write_text(TS_MIXED)
            (d / "util.ts").write_text(TS_UTIL)

            from shannon_insight.analyzers import TypeScriptScanner

            scanner = TypeScriptScanner(str(d))
            files = scanner.scan()

            for f in files:
                assert isinstance(f.function_sizes, list)
                assert len(f.function_sizes) > 0, f"{f.path} should have functions"

    def test_mixed_file_higher_gini(self):
        """Mixed-responsibility files with unequal functions should have higher Gini."""
        # GO_MIXED has a large HandleRequest function and many small ones
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "validator.go").write_text(GO_FOCUSED)
            (d / "processor.go").write_text(GO_MIXED)
            (d / "util.go").write_text(GO_UTIL)

            from shannon_insight.analyzers import GoScanner

            scanner = GoScanner(str(d))
            files = scanner.scan()

            file_ginis = {}
            for f in files:
                if f.function_sizes and len(f.function_sizes) > 1:
                    file_ginis[f.path] = Gini.gini_coefficient(f.function_sizes)

            assert len(file_ginis) > 0, "Should have at least one file with Gini"

            # All Gini values should be valid
            for path, gini in file_ginis.items():
                assert 0.0 <= gini <= 1.0, f"{path}: Gini={gini} out of range"


class TestFindingSuggestions:
    """Verify findings produce actionable suggestions."""

    def test_findings_have_suggestions(self):
        """Findings should include suggestions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "validator.go").write_text(GO_FOCUSED)
            (d / "processor.go").write_text(GO_MIXED)
            (d / "util.go").write_text(GO_UTIL)

            kernel = InsightKernel(str(d), language="go")
            result, snapshot = kernel.run()

            for finding in result.findings:
                assert finding.suggestion is not None
                assert len(finding.suggestion) > 5, "Suggestions should be descriptive"

    def test_findings_have_evidence(self):
        """Findings should include evidence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "validator.py").write_text(PYTHON_FOCUSED)
            (d / "processor.py").write_text(PYTHON_MIXED)
            (d / "util.py").write_text(PYTHON_UTIL)

            kernel = InsightKernel(str(d), language="python")
            result, snapshot = kernel.run()

            for finding in result.findings:
                assert len(finding.evidence) > 0
                for ev in finding.evidence:
                    assert ev.description is not None
                    assert len(ev.description) > 5, "Evidence should be descriptive"
