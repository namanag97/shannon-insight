/**
 * Treemap visualization for file sizes colored by risk.
 * Uses the squarify layout algorithm.
 */

import { esc, hColor } from "../../utils/helpers.js";

function squarify(items, x, y, w, h) {
  if (!items.length) return [];
  if (items.length === 1) {
    items[0].x = x;
    items[0].y = y;
    items[0].w = w;
    items[0].h = h;
    return items;
  }

  let total = 0;
  for (let i = 0; i < items.length; i++) total += items[i].area;
  if (total <= 0) return items;

  const vertical = w >= h;
  const side = vertical ? h : w;
  let sum = 0;
  let best = Infinity;
  let split = 1;

  for (let i = 0; i < items.length - 1; i++) {
    sum += items[i].area;
    const frac = sum / total;
    const strip = vertical ? w * frac : h * frac;
    if (strip <= 0) continue;

    let worst = 0;
    let rowSum = 0;
    for (let j = 0; j <= i; j++) rowSum += items[j].area;
    for (let j = 0; j <= i; j++) {
      const rh = (items[j].area / rowSum) * side;
      const asp = rh > 0 ? Math.max(strip / rh, rh / strip) : Infinity;
      if (asp > worst) worst = asp;
    }
    if (worst < best) {
      best = worst;
      split = i + 1;
    }
  }

  let leftSum = 0;
  for (let i = 0; i < split; i++) leftSum += items[i].area;
  const frac = leftSum / total;
  const left = items.slice(0, split);
  const right = items.slice(split);

  if (vertical) {
    const lw = w * frac;
    let off = y;
    for (let i = 0; i < left.length; i++) {
      const ih = leftSum > 0 ? (left[i].area / leftSum) * h : 0;
      left[i].x = x;
      left[i].y = off;
      left[i].w = lw;
      left[i].h = ih;
      off += ih;
    }
    squarify(right, x + lw, y, w - lw, h);
  } else {
    const lh = h * frac;
    let off = x;
    for (let i = 0; i < left.length; i++) {
      const iw = leftSum > 0 ? (left[i].area / leftSum) * w : 0;
      left[i].x = off;
      left[i].y = y;
      left[i].w = iw;
      left[i].h = lh;
      off += iw;
    }
    squarify(right, x, y + lh, w, h - lh);
  }
  return items;
}

export function Treemap({ entries, onFileClick }) {
  const tmW = 800;
  const tmH = 500;

  const tmItems = [];
  const limit = Math.min(entries.length, 300);
  for (let i = 0; i < limit; i++) {
    const area = Math.max(entries[i][1].lines || 1, 1);
    tmItems.push({
      path: entries[i][0],
      area,
      color_value: entries[i][1].risk_score || 0,
    });
  }
  tmItems.sort((a, b) => b.area - a.area);
  squarify(tmItems, 0, 0, tmW, tmH);

  function handleClick(e) {
    const rect = e.target.closest("rect[data-path]");
    if (rect && onFileClick) {
      onFileClick(rect.dataset.path);
    }
  }

  return (
    <svg
      viewBox={`0 0 ${tmW} ${tmH}`}
      width="100%"
      style={{ maxHeight: "500px", cursor: "pointer" }}
      onClick={handleClick}
    >
      {tmItems.map((t, i) => {
        if (!t.w || !t.h || t.w < 1 || t.h < 1) return null;
        const rc = hColor(10 - t.color_value * 10);
        const name = t.path.split("/").pop();
        const showLabel = t.w > 60 && t.h > 14;
        return (
          <g key={i}>
            <rect
              x={t.x.toFixed(1)}
              y={t.y.toFixed(1)}
              width={t.w.toFixed(1)}
              height={t.h.toFixed(1)}
              fill={rc}
              opacity="0.6"
              stroke="var(--bg)"
              stroke-width="1"
              data-path={t.path}
            >
              <title>
                {t.path} ({Math.round(t.area)} lines, risk {t.color_value.toFixed(3)})
              </title>
            </rect>
            {showLabel && (
              <text
                x={(t.x + 3).toFixed(1)}
                y={(t.y + 11).toFixed(1)}
                font-size="9"
                font-family="var(--mono)"
                fill="var(--text)"
                pointer-events="none"
              >
                {name.slice(0, Math.floor(t.w / 6))}
              </text>
            )}
          </g>
        );
      })}
    </svg>
  );
}
