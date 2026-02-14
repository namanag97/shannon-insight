/**
 * Risk distribution histogram. Renders a horizontal bar chart
 * showing file count per risk bucket.
 */

export function RiskHistogram({ files }) {
  if (!files) return null;

  const bins = [0, 0, 0, 0, 0];
  const binLabels = ["0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0"];
  const binColors = ["var(--green)", "var(--yellow)", "var(--yellow)", "var(--orange)", "var(--red)"];

  for (const p in files) {
    const rs = files[p].risk_score || 0;
    const bi = Math.min(Math.floor(rs * 5), 4);
    bins[bi]++;
  }

  const maxBin = Math.max(...bins) || 1;

  return (
    <div>
      <div class="section-title risk-histogram-title">Risk Distribution</div>
      <svg width="100%" height="100" viewBox="0 0 300 100" preserveAspectRatio="none">
        {bins.map((count, i) => {
          const bw = (count / maxBin) * 240;
          const by = i * 20;
          return (
            <g key={i}>
              <rect x="50" y={by} width={bw} height="14" fill={binColors[i]} opacity="0.7" />
              <text x="0" y={by + 11} fill="var(--text-tertiary)" font-size="8" font-family="var(--mono)">
                {binLabels[i]}
              </text>
              <text x={55 + bw} y={by + 11} fill="var(--text-secondary)" font-size="8" font-family="var(--mono)">
                {count}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
