# Release notes

## 0.2.0

- Consolidated all public functions in the cartonization package and removed the
  standalone compatibility module. Python scripts import from cartonization.
- Removed the larger bundled history/reference dataset and its configuration.
  All runnable examples now use the small synthetic workbooks in examples/data/.

- Consolidated setup and first-use instructions in README.md for GitHub users.
- Removed both Windows and Mac double-click setup files. Users run the shared
  Python setup utility from the VS Code terminal on either platform.
- Kept the generated file-and-checksum manifest inside release ZIPs; it is not
  maintained as a source file in GitHub.
- Added saved JSON workflows for validation, shipment preparation, single scenarios,
  batches and baseline comparisons, with Excel/JSON reports and input provenance.
- Preserved capacity interpolation by default at single-type capacity >= 10.
  Geometric checking throughout remains an explicit option.
- Preserved the volume_penalty objective and added shipping_cost.
- Fixed acceptance of infeasible/fractional/bound-violating solver answers and
  zero objectives reported as infinity. Retained validated feasible incumbents
  with an explicit non-optimal status.
- Replaced skipped failed profiles with strict errors and issue reports.
- Added single-type capacities so mixed orders can split across shippers.
- Fixed false fits from rounding and unintended weight limits in the geometric helper.
- Fixed decimal-grid undercounting in four-quadrant capacity.
- Added cheap volume and individual-fit bounds to interpolated candidates.
- Made sampling/packing repeatable and reported coverage explicitly.
- Accelerated capped packing selection with incremental nearest distances, pruned
  candidate enumeration, removed redundant frontier scans and cached capacities.
- Aligned legacy and saved-config model ordering with the user's selected ID order.
- Added streaming readers, schema checks, a shared Windows/Mac setup utility,
  tests and an explicit release ZIP manifest.

### Analytical API and result changes

The cartonization package exposes both workflow APIs and analytical helpers,
including the six-item scenario_analysis result.
Correctness fixes can change capacities, shipper counts and reported costs.
Packing IDs are now run-local strings with a separator; do not parse the old format.
Input formulas must be supplied as values. Bad counts and missing selected IDs
now fail early rather than truncating or disappearing. New workflow totals are
observed totals; the legacy tuple preserves explicitly requested sample extrapolation.

## 0.1.0

Original library layout, example data and seven unit tests.
