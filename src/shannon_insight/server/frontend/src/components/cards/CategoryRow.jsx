/**
 * Category summary row for the overview screen.
 * Shows category name, finding count, file count, and a proportional bar.
 */

export function CategoryRow({ catKey, label, cat, maxCount, onClick }) {
  const pct = maxCount > 0 ? (cat.count / maxCount) * 100 : 0;
  const barColor =
    cat.high_count > 0
      ? "var(--orange)"
      : cat.count > 0
        ? "var(--yellow)"
        : "var(--border)";

  // Count unique files across findings
  const fileSet = {};
  const catFindings = cat.findings || [];
  for (const finding of catFindings) {
    for (const f of finding.files || []) {
      fileSet[f] = true;
    }
  }
  const fileCount = Object.keys(fileSet).length;

  return (
    <div class="cat-row" data-cat={catKey} onClick={() => onClick && onClick(catKey)}>
      <span class="cat-name">{label}</span>
      <span
        class="cat-count"
        style={{ color: cat.count > 0 ? "var(--text)" : "var(--text-tertiary)" }}
      >
        {cat.count}
      </span>
      <span class="cat-file-count cat-changes-info">
        {fileCount > 0 ? fileCount + " files" : ""}
      </span>
      <div class="cat-bar-track">
        <div class="cat-bar-fill" style={{ width: pct + "%", background: barColor }} />
      </div>
    </div>
  );
}
