# Release notes

## 0.2.0

- Added a separately named distribution without the optional Windows launcher,
  with command-based Windows setup instructions and matching package manifests.
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
- Added streaming readers, schema checks, Windows/Mac setup launchers, tests and
  an explicit release ZIP manifest.

### Compatibility

Existing imports and the legacy six-tuple scenario API remain available.
Correctness fixes can change capacities, shipper counts and reported costs.
Packing IDs are now run-local strings with a separator; do not parse the old format.
Input formulas must be supplied as values. Bad counts and missing selected IDs
now fail early rather than truncating or disappearing. New workflow totals are
observed totals; the legacy tuple preserves explicitly requested sample extrapolation.

## 0.1.0

Original library layout, example data and seven unit tests.
