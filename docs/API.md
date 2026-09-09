# Python API

Import public functions from the `cartonization` package. Use the workflow API
for saved configurations, complete scenario results and reports.

## Recommended workflow API

```python
from cartonization import export_report, run_scenario
from cartonization.workflows import load_config

config, base = load_config("examples/scenario.json")
result = run_scenario(config, base_dir=base, progress=print)
export_report([result], "outputs/my_result")
```

The runnable [Python example](../examples/scenario_analysis_example.py) uses
the same scenario and small practice workbooks as the command-line workflow,
and creates a fresh output folder on each run.

run_scenario returns ScenarioResult with observed total_cost, total_count,
packing_efficiency (0–100), coverage, settings, packings, max_fits, shipment_profiles,
profile solutions and provenance. to_dict() returns JSON-compatible data.

run_scenarios(batch, base_dir, progress) returns results, comparison rows and usage
change rows. Pass all three to export_report. compare_scenarios(results, specs)
can compare already-calculated results with named baselines.

prepare_shipment_history(config, base_dir) returns sheets of profiles, preparation
statistics, carton IDs and provenance. export_prepared writes its Excel/JSON outputs.

validate_scenario_inputs(config, base_dir) reads and validates scenario data without
packing or solving. It returns profiles, carton data, shipper data and resolved
input paths; callers usually need only whether it completes without error.

The CLI always creates new output directories. Direct exporter calls write the
named files in the directory supplied by the caller; use a fresh directory when
preserving prior results is required.

## Analytical helpers

| Function | Purpose |
|---|---|
| max_cartons_four_quadrant(shipper, carton) | Constructive single-type capacity |
| generate_max_fits_dict(shippers, cartons, constrained) | Capacity matrix |
| comingle_tester(cartons, shipper, attempts, scale, random_seed) | Repeatable geometric fit heuristic |
| comingle_frontier_points(...) | Mixed capacity frontier, interpolation default |
| generate_packings(...) | Capacity records including fit_method |
| build_shipment_profiles(...) | Aggregate frequency-weighted Excel profiles |
| stream_xlsx_as_dicts(...) | Stream worksheet dictionaries |
| read_xlsx_as_dicts(...) | List wrapper |
| load_reference_mapping(...) | Selected reference ID lookup |
| shipping_cost_zone4(shipper, fixed_cost) | Legacy modeled cost |
| solve_min_integer(...) | Integer covering optimization |
| upper_bounds_for_solve_min_integer(b, a) | Safe bounds for nonnegative covering inputs |

calculate_cost_count returns (total_cost, total_count), with optional objective
and progress parameters. A failed profile raises AnalysisError.
Non-optimal feasible incumbents produce a warning.

scenario_analysis provides a direct-argument interface with a six-item return:
(total_cost, total_count, packing_efficiency, packings, max_fits, shipment_profiles).
random_seed, objective and progress are keyword-only options.
shipping_cost_funtion remains accepted as the historical misspelling.
Explicit sampling/filtering retains legacy extrapolation and emits a warning.

Packing IDs include a separator between shipper ID and numeric index.
Treat them as run-local identifiers, not permanent business IDs.

## Errors

InputError is a ValueError containing an issues list with location/message fields.
AnalysisError is a RuntimeError containing affected profile details. Other invalid
Python API shapes/settings can raise ValueError, KeyError or TypeError.
The CLI converts expected input/run failures into issue reports and nonzero exits.

Geometric negative results mean the heuristic did not find a fit; they do not
prove impossibility. An Optimal solver status applies to the generated candidate
model, not to all physically possible packings.
