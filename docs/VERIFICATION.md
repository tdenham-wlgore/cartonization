# Verification for 0.2.0

This is a record of observed checks, not a claim that every possible input has
been validated.

## Correctness and regression coverage

The suite currently contains 49 passing cases, including the seven original tests.
It covers infeasible and fractional solver answers, variable bounds, zero-cost
objectives, time-limited incumbents, small exhaustive optimization comparisons,
decimal grid boundaries, oversized cartons, geometry weight handling, default
interpolation avoiding 3D calls, physical volume, unit limits and split mixed orders.

Workflow cases cover strict failures, repeatable previews, alternative objectives,
bad counts, duplicate headers, formula inputs, explicit SKU mapping/exclusions,
order keys, quantity modes, duplicate preservation, comparison reconciliation,
mismatched demand, configuration typos, output text handling and paths with spaces.

## Performance measurements

Measured locally on Apple silicon with Python 3.13.6 and constraints.txt dependencies.

| Measurement | Observed result |
|---|---|
| Capped packing selection: 1,000 candidates, 6 carton types, cap 50; median of 3 runs | Original distance scan 0.502 s; incremental distances 0.0243 s; about 20.7x faster |
| Selection equivalence in that benchmark | Identical selected points and ordering |
| Bundled full example, 551 profiles / 82,887 frequency-weighted orders | 56.1 s; all eligible demand included |
| Full example outputs | Modeled cost $1,080,624.23; 83,385 shippers; efficiency 51.1541% |

Traced peak Python allocations in the focused selection benchmark were 280,500
bytes for the original scan and 464,816 bytes for incremental distances. The
speed gain trades approximately 180 KiB of extra temporary memory for avoiding
repeated distance work on this fixture. This is not whole-process memory usage.

These are specific local measurements, not a universal end-to-end speedup.
The old example exceeded a 45-second exploratory cutoff, so no complete old/new
runtime ratio is claimed. Interpolation remains the default; checked-only mode
can be much slower. Many distinct carton types can still create a large candidate set.

Run `python -m tools.benchmark` from the source folder to repeat the focused
selection benchmark. Run examples/full_example.json to repeat the full example.
Runtime varies with CPU, input patterns, solver load and settings.

## Report verification

The synthetic comparison matches a hand calculation: $144 baseline, $120 with
the small shipper, eight orders and eight shippers in both scenarios.
Every report sheet was rendered for layout inspection and scanned for Excel errors.
The synthetic source files retain text IDs including leading zeros in their saved
Excel cells. The preview renderer can display these IDs without leading zeros;
stored values were checked separately.

Source inputs remain unchanged. Every CLI run writes a fresh output folder.
The release archive is built from an explicit inclusion list with per-file hashes.
Temporary scripts, virtual environments, caches and past outputs are excluded.

## Platform and installation checks

The release uses normal package installation, not an editable installation.
This avoids dependence on the source folder being on Python's import path.
The wheel includes the deprecated cartonization_functions compatibility module.

A fresh macOS extraction into a path with spaces passed setup and the CBC
diagnostic. The installed package and deprecated compatibility import were checked
from outside the source folder, followed by successful comparison and preparation
commands using the extracted examples. Windows execution cannot be exercised on this Mac.
Windows setup instructions and a Windows/Mac/Linux CI matrix are included.
Remote CI had not run at the time of the original ZIP verification recorded here.
See the GitHub repository's **Actions** tab for subsequent hosted check results.

Before broad company rollout, a Windows recipient should extract the archive into
a path with spaces, open that folder's VS Code terminal and run
`py -3.12 tools\setup_environment.py`, then ask Copilot to run doctor, the
comparison example and the preparation example. Confirm the expected $144/$120
comparison and open the generated workbooks.

## Model limitations

The model uses a heuristic capacity set. Interpolation, omitted unobserved mixed
patterns and a capped frontier can affect allocations. The legacy Zone 4 formula
is not a current carrier tariff. Weight, fragility, inserts, supplier availability
and physical qualification are outside this release. See MODELING.md.
