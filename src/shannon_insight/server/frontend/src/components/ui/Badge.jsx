/**
 * Badge component for labels like "changed", "CHRONIC", effort levels.
 * Variants: changed, chronic, effort, role
 */

const VARIANT_CLASSES = {
  changed: "changed-badge",
  chronic: "chronic-badge",
  effort: "effort-badge",
  role: "file-detail-role",
};

export function Badge({ variant = "effort", children }) {
  const cls = VARIANT_CLASSES[variant] || "effort-badge";
  return <span class={cls}>{children}</span>;
}
