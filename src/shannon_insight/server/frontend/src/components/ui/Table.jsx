/**
 * Canonical reusable table component with sorting, formatting, and row click support.
 *
 * Props:
 *   columns:       [{key, label, align?, format?, cellClass?, cellStyle?}]
 *                    - key: data field name
 *                    - label: header text
 *                    - align: 'left' (default) | 'right'
 *                    - format: (value, row) => string|node (optional formatter)
 *                    - cellClass: (value, row) => string (optional class)
 *                    - cellStyle: (value, row) => object (optional inline style)
 *   data:          Array of row objects
 *   rowKey:        (row) => string — unique key for each row
 *   sortable:      boolean — enable column header click sorting (default false)
 *   sortKey:       current sort column key (controlled)
 *   sortAsc:       current sort direction (controlled)
 *   onSort:        (key) => void — called when a sortable header is clicked
 *   onRowClick:    (row) => void — called when a row is clicked
 *   selectedIndex: number — index of keyboard-selected row (-1 = none)
 *   tableClass:    CSS class for the <table> element (default "data-table")
 *   maxRows:       number — limit displayed rows (default: show all)
 *   stickyHeader:  boolean — make header sticky (default true)
 *   striped:       boolean — alternating row backgrounds (default true)
 */

export function Table({
  columns,
  data,
  rowKey,
  sortable = false,
  sortKey,
  sortAsc,
  onSort,
  onRowClick,
  selectedIndex = -1,
  tableClass = "data-table",
  maxRows,
  stickyHeader = true,
  striped = true,
}) {
  const displayData = maxRows ? data.slice(0, maxRows) : data;
  const clickable = typeof onRowClick === "function";

  return (
    <table class={tableClass + (striped ? " data-table--striped" : "") + (clickable ? " data-table--clickable" : "")}>
      <thead>
        <tr>
          {columns.map((col) => {
            const isRight = col.align === "right";
            const isSortable = sortable && onSort;
            const isActive = sortable && sortKey === col.key;
            const arrow = isActive
              ? sortAsc
                ? <span class="sort-arrow">&#9650;</span>
                : <span class="sort-arrow">&#9660;</span>
              : null;
            return (
              <th
                key={col.key}
                class={
                  (isRight ? "num" : "") +
                  (isSortable ? " sortable" : "") +
                  (stickyHeader ? " sticky-header" : "")
                }
                onClick={isSortable ? () => onSort(col.key) : undefined}
              >
                {col.label}
                {arrow}
              </th>
            );
          })}
        </tr>
      </thead>
      <tbody>
        {displayData.map((row, idx) => {
          const key = rowKey ? rowKey(row) : idx;
          return (
            <tr
              key={key}
              class={idx === selectedIndex ? "kbd-selected" : undefined}
              onClick={clickable ? () => onRowClick(row) : undefined}
            >
              {columns.map((col) => {
                const raw = row[col.key];
                const isRight = col.align === "right";
                const content = col.format ? col.format(raw, row) : (raw != null ? raw : "--");
                const cls = col.cellClass ? col.cellClass(raw, row) : (isRight ? "td-num" : undefined);
                const style = col.cellStyle ? col.cellStyle(raw, row) : undefined;
                return (
                  <td key={col.key} class={cls} style={style}>
                    {content}
                  </td>
                );
              })}
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
