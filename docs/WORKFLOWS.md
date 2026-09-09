# Workflows and Copilot requests

Use the local environment's Python:

- Windows: `.venv\Scripts\python.exe`
- Mac: `.venv/bin/python`

The commands below use `python` as shorthand for that executable. All file paths
inside JSON resolve relative to the JSON file's folder. An output-dir argument
resolves from the terminal's current folder.

## First commands and validation

The [README practice analysis](../README.md#5-try-the-practice-analysis) walks
through the first run with Copilot. The equivalent commands are:

```sh
python -m cartonization doctor
python -m cartonization validate examples/scenario.json
python -m cartonization run examples/scenario.json
python -m cartonization compare examples/comparison.json
python -m cartonization prepare examples/preparation.json
```

Successful `run`, `compare` and `prepare` commands create new output directories.
Successful `doctor` and `validate` commands print their checks without creating
reports. Workflow/input failures produce issues.json and, when Excel support is
available, issues.xlsx. Exit code 0 means success; 2 means workflow/input failure;
doctor uses 1 for setup failures.

Validate detects scenario, batch or preparation configuration automatically.
It reads inputs but does not generate packings or invoke the optimizer. Preparation
validation performs the transformation in memory to check mappings and order keys.

For an input problem, ask Copilot:

> Read the issue report and show exactly which rows or IDs need attention.
> Do not discard affected orders or alter the analysis scope.

## One scenario

Copy examples/scenario.json into my_scenarios and change its paths and selected
IDs. Paths must be relative to the new configuration location or absolute.

Required settings:

- history_file and history_sheet
- reference_file
- cartons and shippers: nonempty lists of selected IDs

Optional settings:

| Setting | Default | Meaning |
|---|---|---|
| name | Scenario | Report label |
| frequency_column | FREQUENCY | Shipment frequency |
| carton_sheet / shipper_sheet | container_carton_dims / container_shipper_dims | Reference tabs |
| carton_id_column / shipper_id_column | CARTON / SHIPPER | ID headers |
| dimension_columns | LENGTH, WIDTH, HEIGHT | Three header names as a JSON list |
| max_units_column | MAXUNITS | Maximum unit count |
| fixed_cost | 0 | Added to the built-in shipping estimate |
| objective | volume_penalty | Or shipping_cost |
| interpolation_threshold | 10 | Positive capacity threshold; null requests geometry |
| packing_cap | 100 | Soft per-shipper candidate cap; null removes it |
| constrain_max_units | false | Enforce the MAXUNITS field |
| sample_ratio | 1 | Fraction of eligible shipment frequency; >0 through 1 |
| random_seed | 0 | Nonnegative integer |
| vector_length_limit | Number of selected cartons | Distinct carton types per retained profile |
| vector_freq_limit | 0 | Minimum aggregated frequency of a presence pattern |
| solver_time_limit | 60 | Positive integer seconds per profile; null removes it |

Unknown settings are errors so spelling mistakes do not silently use defaults.

### Dimension and cost overrides

Overrides leave the source workbook intact:

```json
{
  "carton_overrides": {"C_A": [4, 3, 2]},
  "shipper_overrides": {
    "S_SMALL": {"dimensions": [4, 3, 2], "max_units": 999, "cost": 10}
  }
}
```

Override IDs must be selected. A new carton requires all three dimensions; a new
shipper requires dimensions and max_units. Existing shipper records can override
only cost, dimensions or maximum units. Cost is a complete per-shipper value.
Python integrations can also supply a [custom cost function](API.md#custom-shipping-cost-functions).

> Create a scenario override for this shipper's dimensions while keeping the source
> reference workbook unchanged. Compare it against the current dimensions using
> identical demand and settings.

### Previews and geometric checking

Full eligible history and the usual capacity interpolation are the defaults.
Request a preview explicitly when needed:

> Run a reproducible preview covering 20% of shipment frequency with seed 42.
> Keep the default capacity interpolation. Report coverage and observed totals;
> do not present them as full-history totals.

For a deliberate comparison with slower geometric checking:

> For this small scenario only, set interpolation_threshold to null and compare
> it with the default. Explain any changed capacities and runtime.

See [model behavior](MODELING.md) for the meaning of these settings.

## Batches and comparisons

> Create a baseline with the current shippers and a second scenario that also
> allows the new shipper. Use the same shipment history and carton group for both.
> Keep the usual interpolation and volume_penalty objective. Report cost,
> efficiency, usage changes and demand coverage in Excel.

A batch has defaults and a list of named scenarios. Each scenario can override
any setting; override objects replace the common object, without nested merging.
Set baseline to another scenario's name to request before/after tables.
See examples/comparison.json.

For multiple sites/groups, give each scenario a distinct name and its own
history_sheet, carton and shipper lists. Point each alternative at the matching
site/group baseline. Different demand can be reported in the same batch, but is
not automatically treated as a valid savings comparison.

All scenarios validate before solving. Any failure stops the combined report.
Comparisons require identical included demand, total eligible frequency,
sample ratio, seed and vector filters. Objective/capacity/cost changes are allowed
and recorded because these can be the intended experiment.

To compare optimization objectives:

> Rerun the same scenarios with objective shipping_cost. Keep all other inputs
> unchanged. Explain whether the chosen shippers differ from volume_penalty.

## Shipment preparation

> Inspect the workbook in local_data and help me configure shipment preparation.
> Use ORDER_NUMBER and SHIP_TO together to identify an order within each location
> sheet. SKU maps to CARTON using the mapping tab. QUANTITY is the number of units.
> Preserve all rows; do not deduplicate them. Validate before writing profiles.

Replace the example column names with those in your workbook. Specify explicitly
if each row is one unit instead.

Copy examples/preparation.json. Set the input and mapping workbook paths, sheet
names, SKU headers, order-key columns and quantity mode. Use the mapping sheet
to assign every SKU explicitly. See [input formats](DATA_FORMATS.md) for row behavior.

The output shipment_profiles.xlsx can become history_file for subsequent scenarios.
Use one of its location sheet names as history_sheet; FREQUENCY is the frequency
header. A separate preparation.json captures settings and reconciliation statistics.

## Results

report.xlsx contains a summary, comparison tables when requested, shipper usage,
capacities, packing provenance, per-profile results, settings/sources and model notes.
results.json contains the same calculation data at full precision. Cost and
efficiency displayed in Excel are rounded only for presentation.

The configuration snapshot records the run settings. Input hashes identify the
exact source workbooks. Keep source workbooks alongside saved configurations for
future reproduction. Results are snapshots; editing report cells does not rerun
packing or optimization.
