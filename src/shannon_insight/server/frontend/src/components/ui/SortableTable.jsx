/**
 * Generic sortable table component. Renders thead with sort arrows
 * and tbody with row click handlers.
 *
 * Props:
 *   columns:  [{key, label, numeric?, cls?}]
 *   rows:     [{key, cells: [value, ...], data?: any}]
 *   sortKey:  current sort column key
 *   sortAsc:  boolean
 *   onSort:   (key) => void
 *   onRowClick: (row) => void
 *   selectedIndex: number (for keyboard navigation highlighting)
 *   tableClass: CSS class for the table element
 */

export function SortableTable({
  columns,
  rows,
  sortKey,
  sortAsc,
  onSort,
  onRowClick,
  selectedIndex = -1,
  tableClass = "file-table",
}) {
  return (
    <table class={tableClass}>
      <thead>
        <tr>
          {columns.map((col) => {
            const arrow =
              sortKey === col.key
                ? sortAsc
                  ? <span class="sort-arrow">&#9650;</span>
                  : <span class="sort-arrow">&#9660;</span>
                : null;
            return (
              <th
                key={col.key}
                class={col.numeric ? "num" : undefined}
                data-sort={col.key}
                onClick={() => onSort && onSort(col.key)}
              >
                {col.label}
                {arrow}
              </th>
            );
          })}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, idx) => (
          <tr
            key={row.key}
            class={idx === selectedIndex ? "kbd-selected" : undefined}
            data-path={row.dataPath}
            data-mod={row.dataMod}
            onClick={() => onRowClick && onRowClick(row)}
          >
            {row.cells}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
