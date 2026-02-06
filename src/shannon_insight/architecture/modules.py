"""Module detection for Phase 4.

Detects module boundaries from directory structure. The algorithm:
1. Walk source tree - each directory with ≥1 source file is a candidate
2. Determine granularity: choose depth where most directories have 3-15 files
3. Assign files to modules at the chosen depth
4. Fallback for flat projects: use Louvain communities as synthetic modules
"""

from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional

from .models import Module


def determine_module_depth(file_paths: List[str], target_size: tuple[int, int] = (3, 15)) -> int:
    """Determine the optimal module depth based on file distribution.

    Finds the depth level where directories have an ideal number of files
    (default: 3-15 files per directory).

    Depth semantics:
    - depth 0: root directory (flat project)
    - depth 1: first-level subdirectories (e.g., src/graph for src/graph/file.py)
    - depth 2: second-level subdirectories (e.g., src/pkg/graph for src/pkg/graph/file.py)

    Args:
        file_paths: List of file paths to analyze
        target_size: (min, max) ideal file count per module

    Returns:
        Optimal depth level (0 = root, 1 = first subdirectory, etc.)
    """
    if not file_paths:
        return 0

    # Count files per directory at each depth
    # depth_stats[depth][dir_path] = file count in that directory subtree at that depth
    depth_stats: Dict[int, Counter] = defaultdict(Counter)
    max_depth = 0

    for path in file_paths:
        parts = Path(path).parts[:-1]  # Directory parts (exclude filename)
        max_depth = max(max_depth, len(parts))

        # At each depth, what "module" would this file belong to?
        for depth in range(len(parts) + 1):
            if depth == 0:
                dir_path = "."
            else:
                dir_path = str(Path(*parts[:depth]))
            depth_stats[depth][dir_path] += 1

    if max_depth == 0:
        return 0  # Flat project

    # Score each depth by how well it segments files into ideal module sizes
    min_size, max_size = target_size
    best_depth = max_depth  # Default to deepest
    best_score = -1

    for depth in range(1, max_depth + 1):  # Skip depth 0 unless all flat
        dirs_at_depth = depth_stats[depth]
        if not dirs_at_depth:
            continue

        # Want multiple directories in the target range
        in_range = sum(1 for count in dirs_at_depth.values() if min_size <= count <= max_size)
        num_dirs = len(dirs_at_depth)

        # Score: prefer depths with more directories and more in target range
        # Higher is better
        if num_dirs >= 2:  # Need at least 2 modules to be meaningful
            score = in_range * 2 + num_dirs
            if score > best_score:
                best_score = score
                best_depth = depth

    # If no good depth found, use the deepest non-trivial level
    if best_score <= 0:
        for depth in range(max_depth, 0, -1):
            if len(depth_stats[depth]) >= 2:
                return depth
        return max_depth

    return best_depth


def detect_modules(
    file_paths: List[str],
    root_dir: str = "",
    module_depth: Optional[int] = None,
    communities: Optional[Dict[str, int]] = None,
) -> Dict[str, Module]:
    """Detect modules from file paths.

    Args:
        file_paths: List of file paths to group into modules
        root_dir: Root directory of the project
        module_depth: Explicit depth (None = auto-detect)
        communities: Optional Louvain community assignments for flat projects

    Returns:
        Dict mapping module path to Module object
    """
    if not file_paths:
        return {}

    # Auto-detect depth if not specified
    if module_depth is None:
        module_depth = determine_module_depth(file_paths)

    # Group files by module
    module_files: Dict[str, List[str]] = defaultdict(list)

    for file_path in file_paths:
        parts = Path(file_path).parts[:-1]  # Directory parts

        if module_depth == 0 or len(parts) == 0:
            # Flat project: all files in root module
            module_path = "."
        elif len(parts) < module_depth:
            # File is above module depth - use its full directory path
            module_path = str(Path(*parts))
        else:
            # File is at or below module depth - use first N parts
            module_path = str(Path(*parts[:module_depth]))

        module_files[module_path].append(file_path)

    # Create Module objects
    modules: Dict[str, Module] = {}
    for mod_path, files in module_files.items():
        # Skip empty modules (only __init__.py or no real source files)
        real_files = [f for f in files if not f.endswith("__init__.py")]
        if not real_files and len(files) == 1:
            continue  # Skip directory with only __init__.py

        modules[mod_path] = Module(
            path=mod_path,
            files=files,
            file_count=len(files),
        )

    # Fallback for flat projects: use Louvain communities if provided
    if len(modules) == 1 and communities:
        modules = _create_community_modules(file_paths, communities)

    return modules


def _create_community_modules(
    file_paths: List[str],
    communities: Dict[str, int],
) -> Dict[str, Module]:
    """Create synthetic modules from Louvain communities for flat projects.

    Args:
        file_paths: List of file paths
        communities: Mapping of file path to community ID

    Returns:
        Dict mapping community-based module name to Module
    """
    community_files: Dict[int, List[str]] = defaultdict(list)

    for file_path in file_paths:
        comm_id = communities.get(file_path, 0)
        community_files[comm_id].append(file_path)

    modules: Dict[str, Module] = {}
    for comm_id, files in community_files.items():
        mod_path = f"community_{comm_id}"
        modules[mod_path] = Module(
            path=mod_path,
            files=files,
            file_count=len(files),
        )

    return modules
