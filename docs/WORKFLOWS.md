# Running workflows

Use the local environment's Python:
- Windows: `.venv\Scripts\python.exe`
- Mac: `.venv/bin/python`

The commands below use `python` as shorthand for that executable. All file paths
inside JSON resolve relative to the JSON file's folder. An output-dir argument
resolves from the terminal's current folder.

## First commands

```sh
python -m cartonization doctor
python -m cartonization validate examples/scenario.json
python -m cartonization run examples/scenario.json
python -m cartonization compare examples/comparison.json
python -m cartonization prepare examples/preparation.json
```

Every successful run creates a new uniquely named output directory. Failed runs
produce issues.json and, when Excel support is available, issues.xlsx. Exit code
0 means success; 2 means workflow/input failure; doctor uses 1 for setup failures.

Validate detects scenario, batch or preparation configuration automatically.
It reads inputs but does not generate packings or invoke the optimizer. Preparation
validation performs the transformation in memory to check mappings and order keys.

## One scenario

Copy examples/scenario.json and change its paths and selected IDs.

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
| fixed_cost | 0 | Added to the legacy shipping estimate |
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

Dimension and cost overrides leave the source workbook intact:

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

## Batches and comparisons

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

## Shipment preparation

Copy examples/preparation.json. Set the input and mapping workbook paths, sheet
names, SKU headers, order-key columns and quantity mode. Use the mapping sheet
to assign every SKU explicitly. See DATA_FORMATS.md for row behavior.

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
