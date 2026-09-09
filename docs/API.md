# Python API

Import public functions from the `cartonization` package. The workflow API uses
saved configurations and returns complete scenario results and reports.

## Workflow API

```python
from cartonization import export_report, run_scenario
from cartonization.workflows import load_config

config, base = load_config("examples/scenario.json")
result = run_scenario(config, base_dir=base, progress=print)
export_report([result], "outputs/my_result")
```

The runnable [Python example](../examples/run_scenario.py) uses the same practice
scenario and workbooks as the command-line workflow and creates a fresh output
folder each time.

`run_scenario(config, base_dir=".", progress=None, *, shipping_cost_function=None)`
returns `ScenarioResult` with observed total_cost, total_count, packing_efficiency
(0–100), coverage, settings, packings, max_fits, shipment_profiles, profile solutions
and provenance. `to_dict()` returns JSON-compatible data. Sampled results remain
observed totals; they are not extrapolated to full-history estimates.

`run_scenarios(batch, base_dir=".", progress=None, *, shipping_cost_function=None)`
returns results, comparison rows and usage-change rows. Pass all three to
`export_report`. `compare_scenarios(results, specs)` can compare existing results
with named baselines, subject to matching demand and sample/filter settings.

`prepare_shipment_history(config, base_dir=".")` returns profile sheets,
preparation statistics, carton IDs and provenance. `export_prepared` writes
its Excel/JSON outputs.

`validate_scenario_inputs(config, base_dir=".", *, shipping_cost_function=None)`
reads and validates selected data and costs without packing or solving. It returns
profiles, carton data, shipper data and resolved input paths; most callers only
need to know whether it completes without error.

CLI `run`, `compare` and `prepare` commands create new output directories. Direct
exporter calls write named files in the supplied directory; use a fresh directory
when preserving prior results is required.

## Custom shipping cost functions

Python workflows accept a keyword-only `shipping_cost_function` callback. It is
called as `shipping_cost_function(shipper=(length, width, height), fixed_cost=value)`.
Dimensions are a three-item tuple of floats in inches; fixed_cost is a nonnegative
float. Return the complete modeled per-shipper cost as a finite nonnegative number.
The callback controls how fixed_cost contributes to that amount.

For example, after loading the practice configuration above:

```python
def practice_cost(*, shipper, fixed_cost):
    length, width, height = shipper
    return 0.05 * length * width * height + fixed_cost


# Let the callback price S_BIG instead of its explicit practice cost.
config["shipper_overrides"]["S_BIG"].pop("cost", None)
result = run_scenario(config, base_dir=base, shipping_cost_function=practice_cost)
```

This is an illustrative formula. An explicit `shipper_overrides` cost takes
precedence over the callback. Without either, the built-in Zone 4 estimate applies.
In a batch, the callback uses each scenario's dimensions, fixed cost and overrides.
Validation and batch execution can evaluate the callback more than once, so it
must be deterministic and have no side effects.

The evaluated numeric cost for every selected shipper is saved in
`result.provenance["config"]` along with the scenario's other settings. This
configuration can be rerun without the callback and reproduce the same modeled
costs for the same data. Preserve its input paths relative to the original
configuration folder, or make them absolute before saving elsewhere. Callable
objects and dynamic imports are not accepted in JSON configurations.

Reported cost uses the configured costs for either objective. Set
`objective="shipping_cost"` in the configuration only when the solver should
minimize those costs; the default remains `volume_penalty`.

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
| shipping_cost_zone4(shipper, fixed_cost) | Built-in dimensional-weight cost estimate |
| solve_min_integer(...) | Integer covering optimization |
| upper_bounds_for_solve_min_integer(b, a) | Safe bounds for nonnegative covering inputs |

`calculate_cost_count` returns (total_cost, total_count), with optional objective
and progress parameters. A failed profile raises `AnalysisError`.
Non-optimal feasible incumbents produce a warning.

Packing IDs contain a separator between shipper ID and numeric index. Treat them
as run-local identifiers, not permanent business IDs.

## Errors and interpretation

`InputError` is a `ValueError` containing an issues list with location/message fields.
`AnalysisError` is a `RuntimeError` containing affected profile details. Other invalid
Python API shapes or settings can raise `ValueError`, `KeyError` or `TypeError`.
The CLI converts expected input/run failures into issue reports and nonzero exits.

A negative geometric result means the heuristic did not find a fit; it does not
prove impossibility. An Optimal solver status applies to the generated candidate
model. See [model behavior](MODELING.md) for the full assumptions and limitations.
