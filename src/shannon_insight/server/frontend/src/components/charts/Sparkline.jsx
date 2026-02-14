/**
 * Sparkline SVG chart. Renders a line+fill area chart from an array of values.
 * Pure component -- no side effects, no store access.
 */

export function Sparkline({ values, width = 80, height = 20, color = "var(--accent)" }) {
  if (!values || values.length < 2) return null;

  let mn = Infinity;
  let mx = -Infinity;
  for (let i = 0; i < values.length; i++) {
    if (values[i] < mn) mn = values[i];
    if (values[i] > mx) mx = values[i];
  }
  const range = mx - mn || 1;

  const pts = [];
  for (let i = 0; i < values.length; i++) {
    const x = (i / (values.length - 1)) * width;
    const y = height - ((values[i] - mn) / range) * (height - 2) - 1;
    pts.push(x.toFixed(1) + "," + y.toFixed(1));
  }

  const line = pts.join(" ");
  const fill = line + " " + width + "," + height + " 0," + height;

  return (
    <svg width={width} height={height} style={{ verticalAlign: "middle" }}>
      <polyline points={fill} fill={color} opacity="0.1" />
      <polyline points={line} fill="none" stroke={color} stroke-width="1.5" />
    </svg>
  );
}
