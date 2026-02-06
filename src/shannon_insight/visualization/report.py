"""Generate a self-contained HTML report with interactive treemap.

The report embeds all data as a JSON blob inside a ``<script>`` tag and
uses a pure-SVG squarified treemap (zero external dependencies) so it
can be opened from any local file:// path or served statically.
"""

import json
from pathlib import Path
from typing import Optional

from ..persistence.models import Snapshot
from .treemap import build_treemap_data


def generate_report(
    snapshot: Snapshot,
    diff=None,
    trends: Optional[dict[str, list]] = None,
    output_path: str = "shannon-report.html",
    default_metric: str = "cognitive_load",
) -> str:
    """Generate a self-contained HTML report with interactive treemap.

    Parameters
    ----------
    snapshot:
        The analysis snapshot to visualise.
    diff:
        Reserved for future diff overlay support.
    trends:
        Optional mapping of ``filepath -> List[TrendPoint]`` for
        sparkline trend display.
    output_path:
        Where to write the HTML file.
    default_metric:
        Which signal to colour the treemap by on first render.

    Returns
    -------
    str
        Absolute path to the generated HTML file.
    """
    treemap_data = build_treemap_data(snapshot.file_signals, default_metric)

    # ── Findings data ──────────────────────────────────────────────
    findings_data = [
        {
            "type": f.finding_type,
            "severity": f.severity,
            "title": f.title,
            "files": f.files,
            "evidence": [
                {
                    "signal": e.signal,
                    "value": e.value,
                    "percentile": e.percentile,
                    "description": e.description,
                }
                for e in f.evidence
            ],
            "suggestion": f.suggestion,
        }
        for f in snapshot.findings
    ]

    # ── Trend data ─────────────────────────────────────────────────
    trend_data: dict[str, list[dict]] = {}
    if trends:
        for fp, points in trends.items():
            trend_data[fp] = [{"timestamp": p.timestamp, "value": p.value} for p in points]

    # ── Summary data ───────────────────────────────────────────────
    summary_data = {
        "file_count": snapshot.file_count,
        "module_count": snapshot.module_count,
        "timestamp": snapshot.timestamp,
        "commit_sha": snapshot.commit_sha,
        "finding_count": len(snapshot.findings),
        "codebase_signals": snapshot.codebase_signals,
    }

    # ── Available metrics for dropdown ─────────────────────────────
    metrics: set[str] = set()
    for sigs in snapshot.file_signals.values():
        metrics.update(sigs.keys())
    metrics_list = sorted(metrics)

    data_json = json.dumps(
        {
            "treemap": treemap_data,
            "findings": findings_data,
            "trends": trend_data,
            "summary": summary_data,
            "metrics": metrics_list,
            "default_metric": default_metric,
        }
    )

    html = _build_html(data_json)

    out = Path(output_path).resolve()
    out.write_text(html, encoding="utf-8")
    return str(out)


# ── Private helpers ──────────────────────────────────────────────────


def _build_html(data_json: str) -> str:
    """Build self-contained HTML with embedded visualisation code.

    Uses a pure-SVG squarified treemap layout so the report has **zero
    external dependencies** — no CDN, no d3.js download.  The treemap
    re-renders when the user switches the colour metric in the dropdown.
    """
    # We use a raw string for the template and manually embed data_json.
    # The f-string uses {{ / }} to produce literal braces in the JS.
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Shannon Insight Report</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0d1117; color: #c9d1d9; }}
#header {{ padding: 24px 32px; border-bottom: 1px solid #21262d; }}
#header h1 {{ font-size: 24px; color: #58a6ff; margin-bottom: 8px; }}
#summary {{ display: flex; gap: 24px; font-size: 14px; color: #8b949e; flex-wrap: wrap; }}
.stat {{ background: #161b22; padding: 8px 16px; border-radius: 6px; border: 1px solid #21262d; }}
.stat-value {{ font-size: 20px; font-weight: 600; color: #c9d1d9; }}
.stat-label {{ font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }}
#controls {{ padding: 16px 32px; display: flex; gap: 16px; align-items: center; }}
#controls label {{ font-size: 14px; color: #8b949e; }}
#metric-select {{ background: #161b22; color: #c9d1d9; border: 1px solid #30363d; padding: 6px 12px; border-radius: 6px; font-size: 14px; }}
#treemap-container {{ padding: 0 32px; }}
#treemap {{ width: 100%; height: 500px; background: #161b22; border-radius: 8px; border: 1px solid #21262d; overflow: hidden; position: relative; }}
#treemap rect {{ stroke: #0d1117; stroke-width: 1px; cursor: pointer; }}
#treemap text {{ fill: #fff; font-size: 11px; pointer-events: none; text-shadow: 0 1px 2px rgba(0,0,0,0.8); }}
.tooltip {{ position: absolute; background: #1c2128; border: 1px solid #30363d; padding: 12px; border-radius: 8px; font-size: 13px; pointer-events: none; z-index: 100; max-width: 320px; box-shadow: 0 4px 12px rgba(0,0,0,0.4); }}
.tooltip .tt-path {{ color: #58a6ff; font-weight: 600; margin-bottom: 6px; }}
.tooltip .tt-metric {{ color: #8b949e; }}
.tooltip .tt-value {{ color: #c9d1d9; font-weight: 500; }}
#findings {{ padding: 24px 32px; }}
#findings h2 {{ font-size: 18px; color: #58a6ff; margin-bottom: 16px; }}
.finding-card {{ background: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 16px; margin-bottom: 12px; border-left: 4px solid #f85149; }}
.finding-card.medium {{ border-left-color: #d29922; }}
.finding-card.low {{ border-left-color: #3fb950; }}
.finding-type {{ font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #8b949e; margin-bottom: 4px; }}
.finding-title {{ font-size: 15px; font-weight: 600; margin-bottom: 8px; }}
.finding-files {{ font-size: 13px; color: #58a6ff; margin-bottom: 6px; }}
.finding-evidence {{ font-size: 13px; color: #8b949e; }}
.finding-suggestion {{ font-size: 13px; color: #3fb950; margin-top: 8px; }}
#trends {{ padding: 24px 32px; }}
#trends h2 {{ font-size: 18px; color: #58a6ff; margin-bottom: 16px; }}
.trend-row {{ display: flex; align-items: center; gap: 16px; padding: 8px 0; border-bottom: 1px solid #21262d; }}
.trend-file {{ width: 300px; font-size: 13px; color: #58a6ff; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
.trend-spark {{ font-size: 16px; letter-spacing: 1px; }}
footer {{ padding: 24px 32px; text-align: center; color: #484f58; font-size: 12px; border-top: 1px solid #21262d; margin-top: 32px; }}
</style>
</head>
<body>
<div id="header">
  <h1>Shannon Insight Report</h1>
  <div id="summary"></div>
</div>
<div id="controls">
  <label for="metric-select">Color by:</label>
  <select id="metric-select"></select>
</div>
<div id="treemap-container"><div id="treemap"></div></div>
<div id="findings"><h2>Findings</h2><div id="finding-cards"></div></div>
<div id="trends"><h2>File Trends</h2><div id="trend-rows"></div></div>
<footer>Generated by Shannon Insight</footer>

<script>
// All report data embedded at generation time.
const DATA = {data_json};

// ── Summary ──────────────────────────────────────────────────────
(function() {{
  var s = DATA.summary;
  var el = document.getElementById("summary");
  var stats = [
    ["Files", s.file_count],
    ["Modules", s.module_count],
    ["Findings", s.finding_count],
    ["Commit", s.commit_sha ? s.commit_sha.substring(0, 7) : "N/A"],
  ];
  el.innerHTML = stats.map(function(pair) {{
    return '<div class="stat"><div class="stat-value">' + pair[1] + '</div><div class="stat-label">' + pair[0] + '</div></div>';
  }}).join("");
}})();

// ── Metric selector ──────────────────────────────────────────────
(function() {{
  var sel = document.getElementById("metric-select");
  DATA.metrics.forEach(function(m) {{
    var opt = document.createElement("option");
    opt.value = m;
    opt.textContent = m.replace(/_/g, " ");
    if (m === DATA.default_metric) opt.selected = true;
    sel.appendChild(opt);
  }});
  sel.addEventListener("change", function() {{ renderTreemap(sel.value); }});
}})();

// ── Treemap rendering (pure SVG, zero deps) ──────────────────────
function renderTreemap(metric) {{
  var container = document.getElementById("treemap");
  var W = container.clientWidth;
  var H = container.clientHeight;
  container.innerHTML = "";

  // Flatten tree to leaf nodes.
  var leaves = [];
  function flatten(node, prefix) {{
    if (node.children) {{
      node.children.forEach(function(c) {{
        flatten(c, prefix ? prefix + "/" + node.name : node.name);
      }});
    }} else {{
      var sig = node.signals || {{}};
      var raw = sig[metric] || 0;
      leaves.push({{
        name: node.name,
        fullPath: node.path || (prefix + "/" + node.name),
        value: node.value || 1,
        colorRaw: raw,
        signals: sig,
        colorPct: 0
      }});
    }}
  }}
  if (DATA.treemap.children) {{
    DATA.treemap.children.forEach(function(c) {{ flatten(c, ""); }});
  }}

  if (leaves.length === 0) return;

  // Compute percentiles for the current colour metric.
  var colorVals = leaves.map(function(l) {{ return l.colorRaw; }}).sort(function(a, b) {{ return a - b; }});
  leaves.forEach(function(l) {{
    var rank = 0;
    for (var i = 0; i < colorVals.length; i++) {{
      if (colorVals[i] < l.colorRaw) rank++;
      else break;
    }}
    l.colorPct = colorVals.length > 0 ? rank / colorVals.length : 0;
  }});

  // Sort largest first for layout.
  var totalValue = leaves.reduce(function(s, l) {{ return s + l.value; }}, 0);
  leaves.sort(function(a, b) {{ return b.value - a.value; }});

  // Compute rectangle positions with a strip-based treemap layout.
  var rects = squarify(
    leaves.map(function(l) {{ return l.value / totalValue * W * H; }}),
    0, 0, W, H
  );

  // Create SVG.
  var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("width", W);
  svg.setAttribute("height", H);

  // Shared tooltip element.
  var existingTip = document.querySelector(".tooltip");
  if (existingTip) existingTip.remove();
  var tooltip = document.createElement("div");
  tooltip.className = "tooltip";
  tooltip.style.display = "none";
  document.body.appendChild(tooltip);

  rects.forEach(function(r, i) {{
    if (i >= leaves.length) return;
    var leaf = leaves[i];
    var rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    rect.setAttribute("x", r.x);
    rect.setAttribute("y", r.y);
    rect.setAttribute("width", Math.max(0, r.w));
    rect.setAttribute("height", Math.max(0, r.h));
    rect.setAttribute("fill", pctToColor(leaf.colorPct));
    rect.setAttribute("stroke", "#0d1117");
    rect.setAttribute("stroke-width", "1");

    rect.addEventListener("mousemove", function(e) {{
      var sigs = Object.keys(leaf.signals).map(function(k) {{
        var v = leaf.signals[k];
        return '<div class="tt-metric">' + k + ': <span class="tt-value">' + (typeof v === "number" ? v.toFixed(4) : v) + '</span></div>';
      }}).join("");
      tooltip.innerHTML = '<div class="tt-path">' + leaf.fullPath + '</div>' + sigs;
      tooltip.style.display = "block";
      tooltip.style.left = (e.pageX + 12) + "px";
      tooltip.style.top = (e.pageY + 12) + "px";
    }});
    rect.addEventListener("mouseleave", function() {{
      tooltip.style.display = "none";
    }});
    svg.appendChild(rect);

    // Add text label if the rectangle is large enough to read.
    if (r.w > 50 && r.h > 14) {{
      var text = document.createElementNS("http://www.w3.org/2000/svg", "text");
      text.setAttribute("x", r.x + 4);
      text.setAttribute("y", r.y + 13);
      text.setAttribute("fill", "#fff");
      text.setAttribute("font-size", "11");
      text.setAttribute("style", "text-shadow: 0 1px 2px rgba(0,0,0,0.8)");
      var maxChars = Math.floor(r.w / 7);
      text.textContent = leaf.name.length > maxChars ? leaf.name.substring(0, maxChars) + "..." : leaf.name;
      svg.appendChild(text);
    }}
  }});

  container.appendChild(svg);
}}

function pctToColor(pct) {{
  // Green (low/good) -> Yellow -> Red (high/bad)
  var r = pct < 0.5 ? Math.floor(255 * pct * 2) : 255;
  var g = pct < 0.5 ? 255 : Math.floor(255 * (1 - pct) * 2);
  return "rgb(" + r + "," + g + ",0)";
}}

function squarify(areas, x, y, w, h) {{
  var rects = [];
  if (areas.length === 0 || w <= 0 || h <= 0) return rects;

  var total = areas.reduce(function(s, a) {{ return s + a; }}, 0);
  if (total <= 0) return rects;

  var cx = x, cy = y, cw = w, ch = h;

  for (var i = 0; i < areas.length; i++) {{
    var ratio = areas[i] / total;
    if (cw >= ch) {{
      var rw = cw * ratio;
      rects.push({{ x: cx, y: cy, w: Math.max(0, rw), h: Math.max(0, ch) }});
      cx += rw;
      cw -= rw;
    }} else {{
      var rh = ch * ratio;
      rects.push({{ x: cx, y: cy, w: Math.max(0, cw), h: Math.max(0, rh) }});
      cy += rh;
      ch -= rh;
    }}
  }}
  return rects;
}}

// ── Finding cards ────────────────────────────────────────────────
(function() {{
  var el = document.getElementById("finding-cards");
  if (!DATA.findings.length) {{
    el.innerHTML = '<p style="color:#3fb950">No significant findings.</p>';
    return;
  }}
  el.innerHTML = DATA.findings.map(function(f) {{
    var sev = f.severity > 0.7 ? "" : (f.severity > 0.4 ? " medium" : " low");
    var evidence = f.evidence.map(function(e) {{
      return '<div class="finding-evidence">&bull; ' + escapeHtml(e.description) + '</div>';
    }}).join("");
    var filesHtml = f.files.map(function(fp) {{ return escapeHtml(fp); }}).join(", ");
    return '<div class="finding-card' + sev + '">' +
      '<div class="finding-type">' + escapeHtml(f.type.replace(/_/g, " ")) + '</div>' +
      '<div class="finding-title">' + escapeHtml(f.title) + '</div>' +
      '<div class="finding-files">' + filesHtml + '</div>' +
      evidence +
      '<div class="finding-suggestion">&rarr; ' + escapeHtml(f.suggestion) + '</div>' +
    '</div>';
  }}).join("");
}})();

// ── Trend sparklines ─────────────────────────────────────────────
(function() {{
  var el = document.getElementById("trend-rows");
  var trendEntries = Object.keys(DATA.trends || {{}}).map(function(k) {{
    return [k, DATA.trends[k]];
  }});
  if (!trendEntries.length) {{
    el.innerHTML = '<p style="color:#8b949e">No trend data available.</p>';
    return;
  }}
  var blocks = " \\u2581\\u2582\\u2583\\u2584\\u2585\\u2586\\u2587\\u2588";
  el.innerHTML = trendEntries.map(function(pair) {{
    var fp = pair[0], pts = pair[1];
    var vals = pts.map(function(p) {{ return p.value; }});
    var mn = Math.min.apply(null, vals);
    var mx = Math.max.apply(null, vals);
    var spark = vals.map(function(v) {{
      var idx = mx === mn ? 4 : Math.min(8, Math.floor((v - mn) / (mx - mn) * 8));
      return blocks[idx];
    }}).join("");
    return '<div class="trend-row"><span class="trend-file">' + escapeHtml(fp) + '</span><span class="trend-spark">' + spark + '</span></div>';
  }}).join("");
}})();

// ── Utility ──────────────────────────────────────────────────────
function escapeHtml(str) {{
  var div = document.createElement("div");
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}}

// Initial render.
renderTreemap(DATA.default_metric);
</script>
</body>
</html>"""
