/**
 * Radar (spider) chart for health dimension visualization.
 * Pure component -- renders SVG from an array of { name, score } items.
 */

import { esc } from "../../utils/helpers.js";

function polarToXY(cx, cy, radius, angleIdx, total, score) {
  const angle = (Math.PI * 2 * angleIdx) / total - Math.PI / 2;
  const r = radius * Math.min(score / 10, 1);
  return { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) };
}

export function RadarChart({ items, size = 300, radius = 120 }) {
  if (!items || items.length < 3) return null;

  const cx = size / 2;
  const cy = size / 2;
  const n = items.length;

  // Grid rings
  const rings = [];
  for (let ring = 2; ring <= 10; ring += 2) {
    const pts = [];
    for (let i = 0; i < n; i++) {
      const p = polarToXY(cx, cy, radius, i, n, ring);
      pts.push(p.x.toFixed(1) + "," + p.y.toFixed(1));
    }
    rings.push(
      <polygon key={ring} points={pts.join(" ")} fill="none" stroke="var(--border)" stroke-width="0.5" />
    );
  }

  // Axes and labels
  const axes = [];
  for (let i = 0; i < n; i++) {
    const p = polarToXY(cx, cy, radius, i, n, 10);
    const lp = polarToXY(cx, cy, radius + 16, i, n, 10);
    axes.push(
      <g key={i}>
        <line x1={cx} y1={cy} x2={p.x.toFixed(1)} y2={p.y.toFixed(1)} stroke="var(--border)" stroke-width="0.5" />
        <text x={lp.x.toFixed(1)} y={lp.y.toFixed(1)} text-anchor="middle" font-size="9" font-family="var(--mono)" fill="var(--text-secondary)">
          {items[i].name}
        </text>
      </g>
    );
  }

  // Data polygon
  const dataPts = [];
  for (let i = 0; i < n; i++) {
    const p = polarToXY(cx, cy, radius, i, n, items[i].score);
    dataPts.push(p.x.toFixed(1) + "," + p.y.toFixed(1));
  }

  // Data dots
  const dots = items.map((item, i) => {
    const p = polarToXY(cx, cy, radius, i, n, item.score);
    return <circle key={i} cx={p.x.toFixed(1)} cy={p.y.toFixed(1)} r="3" fill="var(--accent)" />;
  });

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      {rings}
      {axes}
      <polygon
        points={dataPts.join(" ")}
        fill="var(--accent)"
        fill-opacity="0.15"
        stroke="var(--accent)"
        stroke-width="1.5"
      />
      {dots}
    </svg>
  );
}
