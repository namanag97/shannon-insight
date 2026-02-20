"""Level 4: Cross-layer analysis — hidden coupling, Conway violations, mutual info."""
from .hidden_coupling import find_hidden_coupling, hidden_coupling_count
from .conway import find_conway_violations, conway_alignment
from .mutual_info import edge_mutual_info

__all__ = [
    "find_hidden_coupling",
    "hidden_coupling_count",
    "find_conway_violations",
    "conway_alignment",
    "edge_mutual_info",
]
