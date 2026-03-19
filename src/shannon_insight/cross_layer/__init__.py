"""Level 4: Cross-layer analysis — hidden coupling, Conway violations, mutual info, dead imports, clone coupling."""

from .clone_coupling import find_active_clones, find_diverged_clones
from .conway import conway_alignment, find_conway_violations
from .dead_imports import dead_import_count, find_dead_imports
from .hidden_coupling import find_hidden_coupling, hidden_coupling_count
from .mutual_info import edge_mutual_info

__all__ = [
    "find_hidden_coupling",
    "hidden_coupling_count",
    "find_conway_violations",
    "conway_alignment",
    "edge_mutual_info",
    "find_dead_imports",
    "dead_import_count",
    "find_active_clones",
    "find_diverged_clones",
]
