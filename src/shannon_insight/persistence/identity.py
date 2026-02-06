"""Stable identity keys for findings.

A finding's identity key stays the same across runs as long as the *same*
structural issue is detected on the *same* file(s).  This lets the history
layer track findings over time even when severity fluctuates.

Rules (by finding type):
  FILE scope (single file):
    high_risk_hub, god_file, unstable_file, orphan_code, hollow_code,
    phantom_imports, naming_drift, knowledge_silo, review_blindspot,
    weak_link, bug_attractor -> (type, primary_file=files[0])

  FILE_PAIR scope (two files):
    hidden_coupling, dead_dependency, copy_paste_clone,
    accidental_coupling -> (type, sorted(files[:2]))

  MODULE scope:
    boundary_mismatch, layer_violation, zone_of_pain -> (type, files[0])

  CODEBASE scope:
    flat_architecture, conway_violation -> (type, "codebase")

  Persistence-aware:
    chronic_problem, architecture_erosion -> (type, wrapped_key or "codebase")
"""

import hashlib
from typing import Optional

# Types whose identity is the single primary file.
_SINGLE_FILE_TYPES = frozenset(
    {
        "high_risk_hub",
        "god_file",
        "unstable_file",
        # Phase 6 FILE scope finders
        "orphan_code",
        "hollow_code",
        "phantom_imports",
        "naming_drift",
        "knowledge_silo",
        "review_blindspot",
        "weak_link",
        "bug_attractor",
    }
)

# Types whose identity is based on the first two files (sorted).
_PAIR_FILE_TYPES = frozenset(
    {
        "hidden_coupling",
        "dead_dependency",
        # Phase 6 FILE_PAIR scope finders
        "copy_paste_clone",
        "accidental_coupling",
    }
)

# Types whose identity is based on files[0] only (MODULE scope).
_PRIMARY_FILE_TYPES = frozenset(
    {
        "boundary_mismatch",
        # Phase 6 MODULE scope finders
        "layer_violation",
        "zone_of_pain",
    }
)

# Types whose identity is based on "codebase" literal (CODEBASE scope).
_CODEBASE_TYPES = frozenset(
    {
        "flat_architecture",
        "conway_violation",
        # Phase 7 persistence-aware finders (codebase scope)
        "architecture_erosion",
    }
)

# Types that wrap other findings (use wrapped finding's key).
_WRAPPER_TYPES = frozenset(
    {
        "chronic_problem",
    }
)


def compute_identity_key(
    finding_type: str,
    files: list[str],
    wrapped_key: Optional[str] = None,
) -> str:
    """Return a stable SHA-256[:16] hex digest for a finding.

    Parameters
    ----------
    finding_type:
        The finding's type string (e.g. ``"high_risk_hub"``).
    files:
        The ordered list of files involved in the finding.
    wrapped_key:
        For wrapper findings (chronic_problem), the identity key of the
        wrapped finding. This ensures chronic findings track the original.

    Returns
    -------
    str
        16-character hex digest that uniquely identifies this finding.
    """
    if finding_type in _WRAPPER_TYPES:
        # Wrapper findings use the wrapped finding's key
        key_parts = [finding_type, wrapped_key or ""]
    elif finding_type in _CODEBASE_TYPES:
        # Codebase-scope findings use "codebase" literal
        key_parts = [finding_type, "codebase"]
    elif finding_type in _SINGLE_FILE_TYPES:
        key_parts = [finding_type, files[0] if files else ""]
    elif finding_type in _PAIR_FILE_TYPES:
        pair = sorted(files[:2]) if len(files) >= 2 else sorted(files)
        key_parts = [finding_type] + pair
    elif finding_type in _PRIMARY_FILE_TYPES:
        key_parts = [finding_type, files[0] if files else ""]
    else:
        # Fallback: use all files, sorted for stability.
        key_parts = [finding_type] + sorted(files)

    raw = "|".join(key_parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
