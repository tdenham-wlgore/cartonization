# Maintenance and verification

This guide covers development, release packaging, recorded verification, and
future work. Users can start with the [README](../README.md).

## Repository and package files

- `cartonization/` contains the analysis functions and workflows.
- `examples/` contains ready-to-run configurations and a Python example;
  `examples/data/` holds the small synthetic workbooks used by examples and checks.
  User workbooks belong in `local_data/` and configurations in `my_scenarios/`.
- `MANIFEST.in` tells Python's packaging tool which supporting files to include
  in a source distribution. The ZIP builder has its own explicit inclusion list.
- `MANIFEST.json` is generated only inside release ZIPs. It records packaged file
  names, sizes and SHA-256 hashes for checking file integrity. Setup and analysis
  do not read or automatically verify it. Comparing the hashes detects file changes.

## Development and releases

Run these with the virtual environment's Python:

```sh
python -m pip install -c constraints.txt -e ".[dev]"
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
python -m build
python tools/check_installed.py --install-wheel
python tools/build_release.py
```

The build command creates a Python wheel and source distribution. The installation
check verifies the wheel from outside the checkout. The final command creates
`dist/cartonization-0.2.0.zip` and its SHA-256 checksum, including source, guides,
tests and bundled examples. Local analysis outputs, user data, temporary scripts,
caches and virtual environments are excluded.

The GitHub Actions workflow checks Windows, Mac and Linux. See
[Actions for the main branch](https://github.com/tdenham-wlgore/cartonization/actions?query=branch%3Amain)
for the current results. Recorded checks below describe specific observations;
they do not establish correctness for every possible input.

## Verification coverage

The regression suite covers infeasible and fractional solver answers, variable
bounds, zero-cost objectives, time-limited incumbents, small exhaustive
optimization comparisons, decimal grid boundaries, oversized cartons, geometry
weight handling, default interpolation avoiding 3D calls, volume and unit limits,
and split mixed orders.

Workflow coverage includes strict failures, repeatable previews, alternative
objectives, invalid counts, duplicate headers, formula inputs, explicit SKU
mapping and exclusions, order keys, quantity modes, duplicate preservation,
comparison reconciliation, mismatched demand, configuration typos, output text
handling and paths with spaces. Custom-cost checks cover override precedence,
invalid prices, sampled observed totals, batch use and replay from saved prices.

### Reports

The bundled comparison matches a hand calculation: **$144 baseline and $120 with
the small shipper**, with **eight orders and eight shippers** in both scenarios.
Every report sheet was rendered for layout inspection and scanned for Excel errors.
Stored text identifiers, including leading zeros, were checked in the source files.

Source workbooks remain unchanged. Analysis and preparation commands write new
output folders. For model assumptions and physical limitations, see
[model behavior](MODELING.md).

### Installation

The setup utility installs the package normally. Recorded macOS checks include
extraction into a path with spaces, setup and the CBC diagnostic, installed-package
imports from outside the source folder, and comparison and preparation runs using
the extracted examples. A fresh temporary environment also passed wheel installation
with pinned dependencies and the installed-package solver check.

For company rollout, verify setup and the practice workflows on a recipient's
computer with its usual network and application policies. On Windows, extract to
a path with spaces, run `py -3.12 tools\setup_environment.py` in the VS Code terminal,
then run doctor, comparison and preparation. Confirm the $144/$120 comparison and
open the generated workbooks.

## Performance measurements

Measured locally on Apple silicon with Python 3.13.6 and the dependencies in
constraints.txt:

| Measurement | Observed result |
|---|---|
| Capped packing selection: 1,000 candidates, 6 carton types, cap 50; median of 3 runs | Original distance scan 0.502 s; incremental distances 0.0243 s; about 20.7x faster |
| Selection equivalence | Identical selected points and ordering |

Traced peak Python allocations were 280,500 bytes for the original scan and
464,816 bytes for incremental distances. The speed gain uses approximately
180 KiB of extra temporary memory to avoid repeated distance calculations on this
fixture. This is not whole-process memory usage or an end-to-end speedup claim.

Run `python -m tools.benchmark` from the source folder to repeat the focused
selection benchmark. Use `examples/comparison.json` for the workflow check.
Runtime varies with CPU, input patterns, solver load and settings. Interpolation
remains the default; geometric checking throughout can be much slower, and many
distinct carton types can still produce a large candidate set.

## Candidate future capabilities

| Priority | Capability | Purpose and implementation boundary |
|---|---|---|
| Next | Replacement-shipper ranking | Rank a supplied candidate catalog when a shipper is unavailable; distinguish modeled fit from confirmed supplier availability. |
| Next | Dimension sensitivity | Sweep named dimensions and show changes in capacities or usage while preserving source references. |
| Next | Explain unused shippers | Distinguish no-fit, cost, objective effects and equivalent solutions using evidence from the model. |
| Later | Shipper alias and container-group mapping | Use company-maintained mappings to reconcile regional and historical IDs, with ambiguity reports. |
| Later | Actual-versus-expected packing audit | Compare warehouse packing records with intended rules using confirmed order keys, quantities, duplicate handling and routing rules. |
| Later | Destination and weight inputs for carrier costs | Extend beyond dimension-based cost callbacks using company rate data and explicit rated dimensions and weight; the built-in Zone 4 estimate is not a live rate source. |

Ordinary dimension overrides and custom dimension-based cost functions are already
supported. The future items above add dedicated ranking, sweep, integration or
auditing workflows.
