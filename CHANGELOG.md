# Changelog

All notable changes to Shannon Insight will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2025-02-03

### Added
- Summary dashboard with Rich Panel and Table in default output
- `--format` flag: `rich` (default), `json`, `csv`, `quiet` output modes
- `--explain` flag for deep-dive analysis of specific files
- `--fail-above` flag for CI gating (exit 1 if max score exceeds threshold)
- Comprehensive unit tests for math layer (entropy, graph, statistics, robust, fusion)
- Test fixtures in `tests/conftest.py`
- Publish workflow (`.github/workflows/publish.yml`) for PyPI trusted publishing
- Build job in CI (runs after lint + test pass)
- `publish-test` and `publish` Makefile targets

### Fixed
- Version is now dynamic from `__init__.py` (no more hardcoded strings)
- JSON export is opt-in via `-o` flag (no longer writes `analysis_report.json` unconditionally)
- "No anomalies" exits 0 with green message (clean codebase is success, not error)
- Test for unsupported language uses `rust` instead of `python` (Python IS supported)
- CI matrix: removed Python 3.8, added Python 3.13
- Updated `actions/setup-python` from v4 to v5
- Linter configs target Python 3.9+ (not 3.8)

### Changed
- Consolidated tool configs (`black.toml`, `ruff.toml`, `mypy.ini`) into `pyproject.toml`
- Replaced `requirements.txt` with `pip install -e ".[dev]"` everywhere
- Replaced `black` with `ruff format` for code formatting
- Simplified Makefile (removed stale targets, added publish targets)
- Rewrote CI workflow: single lint job (ruff + mypy), matrix test job, build job
- Rewrote README with badges, output format docs, CI integration guide
- Updated CONTRIBUTING.md for new tooling

### Removed
- `package.py` (broken, called nonexistent `setup.py`)
- `requirements.txt` (deps managed via `pyproject.toml`)
- `black.toml`, `ruff.toml`, `mypy.ini` (consolidated into `pyproject.toml`)
- `test_analyzer.py`, `analyze.py` (stale scripts)
- `install.sh`, `quick-run.sh`, `run.sh`, `install-test-run.sh` (stale scripts)
- `install-log.txt`, `install-log-full.txt` (build artifacts)
- `MANIFEST.in` (setuptools handles this via pyproject.toml)
- `INSTALL.md`, `QUICKSTART.md`, `README_USAGE.md` (consolidated into README)
- `MATHEMATICAL_FOUNDATIONS.md` from root (kept in `docs/`)
- `run-tests` Makefile target (stale)

## [0.3.0] - 2025-01-15

### Added
- Python language scanner
- Pydantic-based configuration management
- SQLite-based caching with diskcache
- Security validation for root directories
- Custom exception hierarchy

### Fixed
- 8 mathematical bugs in entropy, statistics, and graph modules

## [0.2.0] - 2024-02-03

### Added
- Complete test suite with integration tests
- CI/CD pipeline with GitHub Actions
- Code quality tools: ruff, mypy, black
- Makefile for common development tasks

### Fixed
- Semantic coherence algorithm
- Consistency formula using coefficient of variation
- Minimum sample size validation
- Dependency graph accuracy

## [0.1.0] - Initial Release

### Added
- Initial release of Shannon Insight
- 5 orthogonal quality primitives
- Support for Go and TypeScript/JavaScript
- CLI interface with multiple options
- Configuration via TOML and environment variables
- Cache support

[Unreleased]: https://github.com/namanagarwal/shannon-insight/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/namanagarwal/shannon-insight/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/namanagarwal/shannon-insight/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/namanagarwal/shannon-insight/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/namanagarwal/shannon-insight/releases/tag/v0.1.0
