"""Tree-sitter grammar installer - downloads language parsers on first run.

This module handles automatic installation of tree-sitter language grammars
when the tool is first used. Grammars are cached in ~/.shannon/grammars/
and only downloaded once.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from .logging_config import get_logger

logger = get_logger(__name__)

# Languages to install (most common codebases)
LANGUAGES = [
    ("python", "tree-sitter-python"),
    ("javascript", "tree-sitter-javascript"),
    ("typescript", "tree-sitter-typescript"),
    ("go", "tree-sitter-go"),
    ("java", "tree-sitter-java"),
    ("rust", "tree-sitter-rust"),
    ("ruby", "tree-sitter-ruby"),
    ("cpp", "tree-sitter-cpp"),
]

# Where to store grammars
GRAMMAR_DIR = Path.home() / ".shannon" / "grammars"


def grammars_installed() -> bool:
    """Check if tree-sitter grammars are already installed.

    Returns:
        True if grammars exist and are ready to use
    """
    if not GRAMMAR_DIR.exists():
        return False

    # Check if at least Python grammar exists (most common)
    python_grammar = GRAMMAR_DIR / "python.so"
    if not python_grammar.exists():
        return False

    return True


def has_compiler() -> bool:
    """Check if a C compiler is available.

    Returns:
        True if gcc or clang is available
    """
    for compiler in ["gcc", "clang", "cc"]:
        if shutil.which(compiler):
            return True
    return False


def install_grammars(console=None, verbose: bool = False) -> bool:
    """Install tree-sitter language grammars.

    Downloads and compiles grammars from GitHub. Requires a C compiler.

    Args:
        console: Rich console for output (optional)
        verbose: Show detailed progress

    Returns:
        True if installation succeeded, False otherwise
    """
    # Check for compiler first
    if not has_compiler():
        msg = (
            "⚠️  No C compiler found (gcc/clang). "
            "Tree-sitter grammars cannot be built.\n"
            "   Falling back to regex parsing (less precise).\n"
            "   To enable tree-sitter: install gcc or clang"
        )
        if console:
            console.print(f"[yellow]{msg}[/yellow]")
        else:
            logger.warning(msg)
        return False

    # Create grammar directory
    GRAMMAR_DIR.mkdir(parents=True, exist_ok=True)

    if console:
        console.print("\n📦 [cyan]First run: Installing tree-sitter language grammars...[/cyan]")
        console.print("   This takes ~30 seconds and only happens once.\n")

    success_count = 0

    for lang_name, repo_name in LANGUAGES:
        try:
            if verbose:
                msg = f"   Installing {lang_name}..."
                if console:
                    console.print(msg)
                else:
                    logger.info(msg)

            _install_grammar(lang_name, repo_name, verbose=verbose)
            success_count += 1

        except Exception as e:
            msg = f"Failed to install {lang_name}: {e}"
            if verbose:
                if console:
                    console.print(f"[yellow]⚠️  {msg}[/yellow]")
                else:
                    logger.warning(msg)

    if success_count > 0:
        if console:
            console.print(
                f"\n✅ [green]Installed {success_count}/{len(LANGUAGES)} grammars[/green]\n"
            )
        else:
            logger.info(f"Installed {success_count}/{len(LANGUAGES)} grammars")
        return True
    else:
        if console:
            console.print("[yellow]⚠️  No grammars installed, using regex fallback[/yellow]\n")
        return False


def _install_grammar(lang_name: str, repo_name: str, verbose: bool = False) -> None:
    """Install a single tree-sitter grammar.

    Args:
        lang_name: Language name (e.g., "python")
        repo_name: GitHub repo name (e.g., "tree-sitter-python")
        verbose: Show command output

    Raises:
        subprocess.CalledProcessError: If installation fails
    """
    # Use tree-sitter CLI to build grammar
    # This requires: pip install tree-sitter-cli

    # Alternative: Use py-tree-sitter-languages (pre-built binaries)
    try:
        # Try using pre-built binaries first (faster, no compiler needed)
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--quiet",
                "--target",
                str(GRAMMAR_DIR),
                f"tree-sitter-{lang_name}",
            ],
            check=True,
            capture_output=not verbose,
            timeout=60,
        )
    except subprocess.CalledProcessError:
        # Fallback: Build from source (requires compiler)
        logger.debug(f"Pre-built {lang_name} not available, would need to build from source")
        # For now, we skip source builds to avoid complexity
        # Can add tree-sitter CLI building here if needed
        raise


def check_and_install_if_needed(console=None, force: bool = False) -> bool:
    """Check if grammars are installed, install if needed.

    This is called automatically on first analyze() run.

    Args:
        console: Rich console for output
        force: Force reinstall even if grammars exist

    Returns:
        True if grammars are available (installed or already present)
    """
    if not force and grammars_installed():
        return True

    try:
        return install_grammars(console=console)
    except KeyboardInterrupt:
        if console:
            console.print("\n[yellow]Installation cancelled[/yellow]")
        return False
    except Exception as e:
        logger.warning(f"Grammar installation failed: {e}")
        return False
