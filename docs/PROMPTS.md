# Example Copilot requests

## First run

> Check that this folder is set up correctly, run the synthetic comparison example,
> and explain the results in plain language. Open the Excel report.

## Prepare shipment data

> Inspect the workbook in local_data and help me configure shipment preparation.
> Use ORDER_NUMBER and SHIP_TO together to identify an order within each location
> sheet. SKU maps to CARTON using the mapping tab. QUANTITY is the number of units.
> Preserve all rows; do not deduplicate them. Validate before writing profiles.

Replace these column names with those in your actual workbook. Specify explicitly
if each row is one unit instead.

## Compare shipper choices

> Create a baseline with the current shippers and a second scenario that also
> allows the new shipper. Use the same shipment history and carton group for both.
> Keep the usual interpolation and volume_penalty objective. Report cost,
> efficiency, usage changes and demand coverage in Excel.

## Optimize modeled cost

> Rerun the same scenarios with objective shipping_cost. Keep all other inputs
> unchanged. Explain whether the chosen shippers differ from volume_penalty.

## Check an input problem

> Read the issue report and show exactly which rows or IDs need attention.
> Do not discard affected orders or alter the analysis scope.

## Request an explicit preview

> Run a reproducible preview covering 20% of shipment frequency with seed 42.
> Keep the default capacity interpolation. Report coverage and observed totals;
> do not present them as full-history totals.

## Request expensive geometric checking

> For this small scenario only, set interpolation_threshold to null and compare
> it with the default. Explain any changed capacities and runtime.

## Update dimensions

> Create a scenario override for this shipper's dimensions while keeping the source
> reference workbook unchanged. Compare it against the current dimensions using
> identical demand and settings.
