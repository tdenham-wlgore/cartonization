# Input formats

All IDs are text, including numeric-looking order numbers, SKUs, carton IDs and
shipper IDs. Store values such as `00123` as text in Excel before exporting.
The library preserves existing text but cannot recover zeros already lost upstream.
Headers are case-sensitive and must be unique after surrounding whitespace is trimmed.

Input sheets must contain values, not formulas. Paste calculated input cells as
values before running; this avoids relying on missing or stale formula caches.
Entirely blank rows are ignored. Workbooks are opened read-only and closed after use.

## Shipment profiles

One column per selected carton plus a frequency column (default `FREQUENCY`).
Each row describes a carton-count vector and the number of times it occurred.

| C_A | C_B | FREQUENCY |
|---:|---:|---:|
| 1 | 0 | 3 |
| 2 | 0 | 2 |
| 0 | 4 | 2 |
| 1 | 2 | 1 |

Counts and frequencies must be finite nonnegative whole numbers. Blank values
are zero. Zero-frequency rows do not contribute demand. Equal profiles are
aggregated. Orders containing none of the selected cartons are outside the scope.

Carton selection projects an order onto the selected carton group. Do not sum
group-level order frequencies to obtain a count of unique orders across groups.

## Reference workbook

Default carton sheet: `container_carton_dims`.

| CARTON | LENGTH | WIDTH | HEIGHT |
|---|---:|---:|---:|
| C_A | 4 | 3 | 2 |

Default shipper sheet: `container_shipper_dims`.

| SHIPPER | LENGTH | WIDTH | HEIGHT | MAXUNITS |
|---|---:|---:|---:|---:|
| S_BIG | 8 | 6 | 4 | 999 |

Dimensions must be positive finite numbers in inches. Use carton outer dimensions
and usable shipper interior dimensions. The same shipper dimensions feed the
legacy dimensional-weight estimate; supply an explicit cost override if actual
rated outer dimensions/costs differ.

MAXUNITS is a nonnegative integer and is read even if enforcement is disabled.
Zero means the shipper is unavailable when enforcement is enabled. Selected IDs
must exist once in the reference, or be supplied with a complete scenario override.

## Raw order lines and SKU mapping

Order-line sheets contain order-key columns, a SKU column and optionally a quantity
column. Preparation requires an explicit mapping sheet with one row per SKU and
its carton ID. No classifier or prefix rules are inferred.

The sheet name is part of order identity. Within each sheet, configure every
column needed to distinguish orders, such as ORDER and SHIP_TO together.

- `quantity_mode: "column"`: use the named quantity column; quantities must be positive integers.
- `quantity_mode: "one_per_row"`: every row is one unit; the quantity column is ignored.

Duplicate-looking rows are retained and counted in preparation statistics.
Unmapped SKUs and invalid data stop preparation. Explicit `exclude_skus` settings
exclude the entire affected order, including its otherwise mapped lines. Review
excluded-order counts before using the output.

The prepared workbook retains source sheet names, places carton headers and
FREQUENCY in row 1, and adds a preparation-statistics sheet. The accompanying JSON
contains the mapping/input hashes, settings and reconciliation counts.
