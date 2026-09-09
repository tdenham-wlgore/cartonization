# Model behavior

## Default interpolation

The default threshold is 10. When any active carton in a mixed packing has a
single-carton capacity **greater than or equal to 10**, the algorithm uses a
normalized capacity estimate instead of searching for a 3D arrangement.

For carton quantities q and single-type capacities b, the candidate score is:

`score = sum(q_i / b_i)`

Candidates fall in the existing narrow band:

`min((b_i - 1) / b_i) < score < min((b_i + 1) / b_i)`

The minima use included carton types. This approximately interpolates between
single-type capacities. Small errors in high-capacity cases are an accepted
speed/accuracy tradeoff. The trigger is **single-type capacity**, not total units
on the current order. A mixed packing can therefore use interpolation if only one
included carton has a high capacity.

Cheap checks still reject excess total carton volume, individually oversized
cartons and enabled MAXUNITS violations. They do not search for arrangements.

Set `interpolation_threshold` to a different positive integer to change the
crossover. Set it to `null` only when geometric checking is explicitly desired
throughout. Low-capacity mixed packings use the repeatable py3dbp heuristic.
Single-type capacities use the constructive four-quadrant method.

Packing records identify `four_quadrant`, `interpolated` or `3d_checked`.
No repeated confirmation is needed to use the default interpolation.

## What the solver minimizes

The default `volume_penalty` objective is the existing business model:

`sum(shipper_quantity * (rounded_shipper_volume + largest_candidate_shipper_volume))`

It balances volume and shipper count. It does **not** strictly minimize shipper
count first, nor does it guarantee minimum shipping cost. Adding an unused large
shipper can change the penalty because the largest candidate volume changes.

`shipping_cost` instead minimizes the configured per-shipper modeled costs.
Reported costs always use those costs, regardless of objective. The built-in
Zone 4 curve is the repository's legacy dimensional-weight approximation, with
a divisor of 139 and a configurable fixed cost. It is not a current carrier
tariff and does not include actual weight, destination variation or surcharges.
An explicit per-shipper cost override is treated as the complete cost, not an
additional charge on top of fixed_cost.

## Packing capacities and bounds

Packing variables describe available capacity. A selected shipper may be underfilled;
the solver does not add extra products to an order. Single-type packings are always
included so mixed orders can be split across shippers.

Candidate generation uses observed carton presence patterns plus single-type
patterns. It is a heuristic candidate set, not every possible mixed packing.
The packing cap defaults to 100 per shipper. It is soft when retaining all
single-type maxima requires more than the cap. Set the cap to null to retain the
entire generated frontier. This can increase memory and solve time.

Neither four-quadrant capacities nor a failed 3D heuristic proves global packing
optimality or impossibility. The integer solver's Optimal status applies only to
the generated capacity model. A time-limited integer incumbent is marked feasible
but not proven optimal. Missing, fractional, infeasible or bound-violating answers
stop analysis. No shipment profile is silently skipped.

Geometric checks round carton dimensions upward and shipper dimensions downward
at the configured scale (default 0.01 inch), so rounding cannot create a false fit.
No weight limit is imposed by the geometry-only helper.

## Coverage and repeatability

Normal workflows use all positive-frequency profiles involving selected cartons.
Seed 0 controls previews and packing attempts. Stable input ordering, a fixed
dependency set and deterministic selection improve repeatability. Equal optima
can still choose different shippers across solver/platform versions.

Sampling is an explicit opt-in. The weighted sample covers at least the requested
fraction of shipment frequency, sometimes more because complete profiles are kept.
Vector filters are also explicit: length limits the number of distinct carton
types; frequency filters on the aggregated frequency of each presence pattern.

New workflow results report observed totals and included/excluded demand. They
do not extrapolate. Comparing a baseline and scenario requires matching demand
and sampling/filter settings. Efficiency uses total carton volume divided by
total used shipper volume, not an unweighted average of profile efficiencies.

The legacy six-tuple scenario_analysis API retains its frequency-scaled estimates
for explicitly sampled/filtered calls, with a warning. That scaling assumes omitted
orders behave like included orders; it is not an unbiased estimator guarantee.

## Physical and operational scope

Use cases are analytical, not production routing. The model does not enforce
weight, fragility, restricted orientations, inserts, cushioning, supplier availability,
regional aliases or physical qualification rules. Units must be consistent.
A modeled fit does not replace physical pack testing.
