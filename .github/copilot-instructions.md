# Using cartonization with the user

This is a Python analysis library for non-programmers. Use the installed package
and saved JSON configurations to answer analysis requests. Do not rewrite packing
algorithms or invent replacement calculations to work around an error.

Read START_HERE.md for setup, docs/WORKFLOWS.md for configurations, and
docs/MODELING.md for interpretation. First check the active .venv interpreter.
Run `python -m cartonization doctor` if setup is uncertain. Use the full path to
the .venv Python executable when terminal activation is uncertain.

For analyses:
1. Inspect the user's input sheet names and headers. Preserve IDs as text.
2. Create a named JSON configuration with paths relative to that configuration.
   Keep user work in local_data/ and configurations in a user-owned folder.
3. Run `python -m cartonization validate CONFIG.json`, then prepare, run, or compare.
4. Read the actual generated results.json and report.xlsx; report cost, usage,
   efficiency, coverage, objective and any solver limitations. Link the output.
5. Keep source workbooks intact. Every run writes a new output directory.

Default behavior: full eligible demand, seed 0, volume_penalty objective, capacity
interpolation when any active carton has single-type capacity >= 10. This is
intentional: do not replace it with slow 3D verification for high-capacity cases.
Use interpolation_threshold=null only when the user requests geometric checking.
Both modes retain cheap volume, single-item-fit and enabled MAXUNITS checks.

Stop on invalid inputs, missing mappings or an unsolved order. Explain the issue
report and correct the configuration/data with the user; do not quietly drop IDs,
exclude demand, change quantities, lower fidelity, or report partial totals.
Sampling/exclusions require an explicit user instruction and must appear in the
reported coverage. Do not present preview totals as full-history estimates.

For raw order lines, confirm the order-key columns and quantity interpretation
from the user's supplied schema. Do not infer duplicate removal or SKU classifier
rules. The preparation workflow accepts an explicit SKU-to-carton mapping.
Explicit excluded SKUs quarantine whole orders, not individual lines.

The Zone 4 function is a legacy estimate, not live shipping rates. Geometric fit
does not include weight, inserts, fragility, supplier availability or pack testing.
Use shipping_cost only when the user requests cost optimization. Preserve
volume_penalty when reproducing the existing model.

For changes to code, add relevant regression tests and run pytest and Ruff.
Do not claim that cross-platform checks ran merely because a CI workflow exists.
