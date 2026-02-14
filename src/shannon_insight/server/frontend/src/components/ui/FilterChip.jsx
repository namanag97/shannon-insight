/**
 * Toggle filter chip button. Used in file list and issue filter bars.
 */

export function FilterChip({ label, active, onClick }) {
  return (
    <button class={`filter-chip${active ? " active" : ""}`} onClick={onClick}>
      {label}
    </button>
  );
}
