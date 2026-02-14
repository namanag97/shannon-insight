/**
 * TrendChart - Enhanced line chart with axes, labels, gridlines, and hover tooltips.
 * Built on top of the same SVG approach as Sparkline but with full axis support.
 * Pure component -- no side effects, no store access.
 *
 * Props:
 *   values     - Array of numbers (y-axis values)
 *   xLabels    - Array of strings for x-axis labels (same length as values)
 *   width      - Chart width (default 600)
 *   height     - Chart height (default 200)
 *   color      - Line/fill color (default "var(--accent)")
 *   yMin       - Y-axis minimum (default: auto from data)
 *   yMax       - Y-axis maximum (default: auto from data)
 *   ySteps     - Number of y-axis gridlines (default 5)
 *   yFormat    - Function to format y-axis labels (default: (v) => v.toFixed(1))
 *   tooltipFormat - Function to format tooltip value (default: yFormat)
 *   showDots   - Show dots at data points (default true)
 *   showGrid   - Show horizontal gridlines (default true)
 *   showFill   - Show fill area under line (default true)
 */

import { useState, useRef } from "preact/hooks";

const MARGIN = { top: 12, right: 16, bottom: 36, left: 44 };

export function TrendChart({
  values,
  xLabels,
  width = 600,
  height = 200,
  color = "var(--accent)",
  yMin: yMinProp,
  yMax: yMaxProp,
  ySteps = 5,
  yFormat = (v) => v.toFixed(1),
  tooltipFormat,
  showDots = true,
  showGrid = true,
  showFill = true,
}) {
  const [hoverIndex, setHoverIndex] = useState(null);
  const svgRef = useRef(null);

  if (!values || values.length < 1) return null;

  const fmtTooltip = tooltipFormat || yFormat;

  // Compute data bounds
  let mn = Infinity;
  let mx = -Infinity;
  for (let i = 0; i < values.length; i++) {
    if (values[i] < mn) mn = values[i];
    if (values[i] > mx) mx = values[i];
  }

  const yMin = yMinProp != null ? yMinProp : mn;
  const yMax = yMaxProp != null ? yMaxProp : mx;
  const yRange = yMax - yMin || 1;

  // Plot area dimensions
  const plotW = width - MARGIN.left - MARGIN.right;
  const plotH = height - MARGIN.top - MARGIN.bottom;

  // Map data to pixel coordinates
  function xPos(i) {
    if (values.length === 1) return plotW / 2;
    return (i / (values.length - 1)) * plotW;
  }

  function yPos(v) {
    return plotH - ((v - yMin) / yRange) * plotH;
  }

  // Build polyline points
  const pts = [];
  for (let i = 0; i < values.length; i++) {
    pts.push(xPos(i).toFixed(1) + "," + yPos(values[i]).toFixed(1));
  }
  const linePath = pts.join(" ");
  const fillPath = linePath + " " + plotW.toFixed(1) + "," + plotH.toFixed(1) + " 0," + plotH.toFixed(1);

  // Y-axis gridlines and labels
  const yGridLines = [];
  for (let i = 0; i <= ySteps; i++) {
    const v = yMin + (yRange * i) / ySteps;
    const y = yPos(v);
    yGridLines.push({ y, label: yFormat(v) });
  }

  // X-axis labels - show a sensible subset to avoid overlap
  const maxXLabels = Math.floor(plotW / 56);
  const xLabelPositions = [];
  if (xLabels && xLabels.length > 0) {
    const step = Math.max(1, Math.ceil(xLabels.length / maxXLabels));
    for (let i = 0; i < xLabels.length; i += step) {
      xLabelPositions.push({ i, x: xPos(i), label: xLabels[i] });
    }
    // Always include last label
    const last = xLabels.length - 1;
    if (xLabelPositions.length === 0 || xLabelPositions[xLabelPositions.length - 1].i !== last) {
      xLabelPositions.push({ i: last, x: xPos(last), label: xLabels[last] });
    }
  }

  // Handle mouse/touch interaction for tooltips
  function handleMouseMove(e) {
    if (!svgRef.current) return;
    const rect = svgRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left - MARGIN.left;
    if (x < 0 || x > plotW) {
      setHoverIndex(null);
      return;
    }
    const idx = values.length === 1
      ? 0
      : Math.round((x / plotW) * (values.length - 1));
    const clamped = Math.max(0, Math.min(values.length - 1, idx));
    setHoverIndex(clamped);
  }

  function handleMouseLeave() {
    setHoverIndex(null);
  }

  return (
    <div class="trend-chart-container" style={{ position: "relative" }}>
      <svg
        ref={svgRef}
        width={width}
        height={height}
        style={{ display: "block", maxWidth: "100%" }}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
      >
        <g transform={`translate(${MARGIN.left},${MARGIN.top})`}>
          {/* Y-axis gridlines */}
          {showGrid &&
            yGridLines.map((g, i) => (
              <line
                key={"yg" + i}
                x1="0"
                y1={g.y.toFixed(1)}
                x2={plotW.toFixed(1)}
                y2={g.y.toFixed(1)}
                stroke="var(--border)"
                stroke-width="0.5"
                stroke-dasharray={i === 0 ? "none" : "2,3"}
              />
            ))}

          {/* Y-axis labels */}
          {yGridLines.map((g, i) => (
            <text
              key={"yl" + i}
              x="-8"
              y={(g.y + 3).toFixed(1)}
              text-anchor="end"
              font-size="10"
              font-family="var(--mono)"
              fill="var(--text-tertiary)"
            >
              {g.label}
            </text>
          ))}

          {/* X-axis baseline */}
          <line
            x1="0"
            y1={plotH.toFixed(1)}
            x2={plotW.toFixed(1)}
            y2={plotH.toFixed(1)}
            stroke="var(--border)"
            stroke-width="0.5"
          />

          {/* X-axis labels */}
          {xLabelPositions.map((lp, i) => (
            <g key={"xl" + i}>
              {/* Tick mark */}
              <line
                x1={lp.x.toFixed(1)}
                y1={plotH.toFixed(1)}
                x2={lp.x.toFixed(1)}
                y2={(plotH + 4).toFixed(1)}
                stroke="var(--border)"
                stroke-width="0.5"
              />
              <text
                x={lp.x.toFixed(1)}
                y={(plotH + 16).toFixed(1)}
                text-anchor="middle"
                font-size="9"
                font-family="var(--mono)"
                fill="var(--text-tertiary)"
              >
                {lp.label}
              </text>
            </g>
          ))}

          {/* Fill area */}
          {showFill && (
            <polyline points={fillPath} fill={color} opacity="0.08" />
          )}

          {/* Line */}
          <polyline
            points={linePath}
            fill="none"
            stroke={color}
            stroke-width="1.5"
            stroke-linejoin="round"
            stroke-linecap="round"
          />

          {/* Dots at each data point (subtle) */}
          {showDots && values.length <= 30 &&
            values.map((v, i) => (
              <circle
                key={"d" + i}
                cx={xPos(i).toFixed(1)}
                cy={yPos(v).toFixed(1)}
                r={hoverIndex === i ? "4" : "2.5"}
                fill={hoverIndex === i ? color : "var(--surface)"}
                stroke={color}
                stroke-width="1.5"
                style={{ transition: "r 0.1s ease" }}
              />
            ))}

          {/* Hover vertical line + tooltip */}
          {hoverIndex != null && (
            <g>
              <line
                x1={xPos(hoverIndex).toFixed(1)}
                y1="0"
                x2={xPos(hoverIndex).toFixed(1)}
                y2={plotH.toFixed(1)}
                stroke="var(--text-tertiary)"
                stroke-width="0.5"
                stroke-dasharray="3,3"
              />
            </g>
          )}
        </g>
      </svg>

      {/* Floating tooltip (positioned via CSS) */}
      {hoverIndex != null && (
        <div
          class="trend-chart-tooltip"
          style={{
            left: Math.min(
              MARGIN.left + xPos(hoverIndex),
              width - 120
            ) + "px",
            top: Math.max(
              MARGIN.top + yPos(values[hoverIndex]) - 40,
              0
            ) + "px",
          }}
        >
          <div class="trend-chart-tooltip-value">{fmtTooltip(values[hoverIndex])}</div>
          {xLabels && xLabels[hoverIndex] && (
            <div class="trend-chart-tooltip-label">{xLabels[hoverIndex]}</div>
          )}
        </div>
      )}
    </div>
  );
}
