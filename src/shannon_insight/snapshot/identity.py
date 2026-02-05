"""Stable identity keys for findings.

A finding's identity key stays the same across runs as long as the *same*
structural issue is detected on the *same* file(s).  This lets the history
layer track findings over time even when severity fluctuates.

Rules (by finding type):
  high_risk_hub, god_file, unstable_file  -> (type, primary_file=files[0])
  hidden_coupling, dead_dependency        -> (type, sorted(files[:2]))
  boundary_mismatch                       -> (type, files[0])
  fallback                                -> (type, sorted(all files))
"""

import hashlib
from typing import List

# Types whose identity is the single primary file.
_SINGLE_FILE_TYPES = frozenset({"high_risk_hub", "god_file", "unstable_file"})

# Types whose identity is based on the first two files (sorted).
_PAIR_FILE_TYPES = frozenset({"hidden_coupling", "dead_dependency"})

# Types whose identity is based on files[0] only (but not a hub/god).
_PRIMARY_FILE_TYPES = frozenset({"boundary_mismatch"})


def compute_identity_key(finding_type: str, files: List[str]) -> str:
    """Return a stable SHA-256[:16] hex digest for a finding.

    Parameters
    ----------
    finding_type:
        The finding's type string (e.g. ``"high_risk_hub"``).
    files:
        The ordered list of files involved in the finding.

    Returns
    -------
    str
        16-character hex digest that uniquely identifies this finding.
    """
    if finding_type in _SINGLE_FILE_TYPES:
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
