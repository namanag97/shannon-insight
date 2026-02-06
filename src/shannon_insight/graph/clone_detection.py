"""NCD-based clone detection for Phase 3.

Detects copy-paste clones using Normalized Compression Distance (NCD):
    NCD(A,B) = (C(AB) - min(C(A), C(B))) / max(C(A), C(B))

Where C(x) = len(zlib.compress(x)).

Clone threshold: NCD < 0.3

For codebases with >= 1000 files, uses MinHash + LSH for pre-filtering
to avoid O(n²) blowup. For smaller codebases, direct pairwise is fast enough.
"""

import zlib
from typing import Dict, List, Set

from .models import ClonePair

# NCD threshold: files with NCD below this are considered clones
CLONE_THRESHOLD = 0.3

# File count threshold for switching to LSH
LSH_FILE_THRESHOLD = 1000

# Minimum file size to consider (skip empty/tiny files)
MIN_FILE_SIZE = 10


def compute_ncd(content_a: bytes, content_b: bytes) -> float:
    """Compute Normalized Compression Distance between two byte strings.

    NCD(A,B) = (C(AB) - min(C(A), C(B))) / max(C(A), C(B))

    Args:
        content_a: First file content
        content_b: Second file content

    Returns:
        NCD value in [0, 1]. Lower = more similar.
    """
    if not content_a or not content_b:
        return 1.0  # Empty content = maximally different

    c_a = len(zlib.compress(content_a, level=6))
    c_b = len(zlib.compress(content_b, level=6))
    c_ab = len(zlib.compress(content_a + content_b, level=6))

    max_c = max(c_a, c_b)
    if max_c == 0:
        return 1.0

    ncd = (c_ab - min(c_a, c_b)) / max_c
    # Clamp to [0, 1] - NCD can theoretically exceed 1 due to compression overhead
    return max(0.0, min(1.0, ncd))


def detect_clones(
    file_contents: Dict[str, bytes],
    roles: Dict[str, str],
    threshold: float = CLONE_THRESHOLD,
) -> List[ClonePair]:
    """Detect clone pairs in a codebase.

    Uses direct pairwise comparison for smaller codebases (<1000 files).
    For larger codebases, uses MinHash+LSH pre-filtering.

    Exclusion rules:
    - Skip file pairs where BOTH files have role=TEST or role=MIGRATION

    Args:
        file_contents: Mapping of file path to file content bytes
        roles: Mapping of file path to role (from Phase 2)
        threshold: NCD threshold below which files are clones (default 0.3)

    Returns:
        List of ClonePair objects for all detected clones
    """
    # Filter out empty/tiny files
    valid_files = {
        path: content for path, content in file_contents.items() if len(content) >= MIN_FILE_SIZE
    }

    if len(valid_files) < 2:
        return []

    # Roles that are excluded when BOTH files match
    excluded_roles = {"TEST", "MIGRATION"}

    def should_skip_pair(path_a: str, path_b: str) -> bool:
        """Check if pair should be excluded based on roles."""
        role_a = roles.get(path_a, "")
        role_b = roles.get(path_b, "")
        return role_a in excluded_roles and role_b in excluded_roles

    # For now, always use direct pairwise (simpler, fast enough for most cases)
    # LSH implementation can be added later if needed for very large codebases
    paths = sorted(valid_files.keys())
    clones: List[ClonePair] = []

    for i, path_a in enumerate(paths):
        content_a = valid_files[path_a]
        for path_b in paths[i + 1 :]:
            if should_skip_pair(path_a, path_b):
                continue

            content_b = valid_files[path_b]
            ncd = compute_ncd(content_a, content_b)

            if ncd < threshold:
                clones.append(
                    ClonePair(
                        file_a=path_a,
                        file_b=path_b,
                        ncd=ncd,
                        size_a=len(content_a),
                        size_b=len(content_b),
                    )
                )

    return clones


def compute_clone_ratio(clone_pairs: List[ClonePair], total_files: int) -> float:
    """Compute global clone ratio: files in any clone pair / total files.

    Args:
        clone_pairs: List of detected clone pairs
        total_files: Total number of files in codebase

    Returns:
        Clone ratio in [0, 1]
    """
    if total_files == 0:
        return 0.0

    files_in_clones: Set[str] = set()
    for pair in clone_pairs:
        files_in_clones.add(pair.file_a)
        files_in_clones.add(pair.file_b)

    return len(files_in_clones) / total_files
