"""Build hierarchical JSON for a d3-style treemap from flat file signals.

The output structure is designed for direct consumption by a squarified
treemap layout.  Leaf nodes carry ``value`` (for area sizing), a
``color_value`` percentile (for heatmap colouring), and the full
``signals`` dict so tooltips can display any metric.
"""

from bisect import bisect_left
from typing import Any, Dict


def build_treemap_data(
    file_signals: Dict[str, Dict[str, float]],
    color_metric: str = "cognitive_load",
) -> Dict[str, Any]:
    """Convert flat file signals into d3-treemap hierarchical JSON.

    Structure::

        {
            "name": "root",
            "children": [
                {
                    "name": "src",
                    "children": [
                        {
                            "name": "main.py",
                            "path": "src/main.py",
                            "value": 120,
                            "color_value": 0.85,
                            "signals": { ... }
                        }
                    ]
                }
            ]
        }

    Leaf nodes get:

    * **value** -- ``lines`` signal (or 1), used for rectangle area sizing.
    * **color_value** -- percentile rank of *color_metric* across all files
      (0.0 = lowest, 1.0 = highest).
    * **signals** -- the full signal dict, rounded to 4 decimal places.

    Parameters
    ----------
    file_signals:
        Mapping of ``filepath -> { signal_name -> value }``.
    color_metric:
        Which signal to use for the colour percentile.

    Returns
    -------
    Dict[str, Any]
        A nested dictionary suitable for JSON serialisation.
    """
    # Pre-compute sorted colour values for percentile calculation.
    color_values = sorted(
        sigs.get(color_metric, 0.0) for sigs in file_signals.values()
    )

    root: Dict[str, Any] = {"name": "root", "children": []}

    for filepath, signals in sorted(file_signals.items()):
        parts = filepath.split("/")
        node = root

        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                # ── Leaf node ──────────────────────────────────────
                raw_color = signals.get(color_metric, 0.0)
                if color_values:
                    rank = bisect_left(color_values, raw_color)
                    percentile = rank / len(color_values)
                else:
                    percentile = 0.0

                leaf: Dict[str, Any] = {
                    "name": part,
                    "path": filepath,
                    "value": max(1, int(signals.get("lines", 1))),
                    "color_value": round(percentile, 3),
                    "signals": {k: round(v, 4) for k, v in signals.items()},
                }
                node["children"].append(leaf)
            else:
                # ── Directory node (find or create) ────────────────
                existing = None
                for child in node.get("children", []):
                    if child.get("name") == part and "children" in child:
                        existing = child
                        break
                if existing is None:
                    existing = {"name": part, "children": []}
                    node.setdefault("children", []).append(existing)
                node = existing

    return root
