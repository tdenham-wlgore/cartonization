# Cartonization analysis

Run cartonization analyses from natural-language requests in GitHub Copilot for VS Code.
The package handles carton/shipper capacities, shipment profiles, scenario comparisons,
and Excel reports.

**New users: open [START_HERE.md](START_HERE.md).** Get the source from the
[private GitHub repository](https://github.com/tdenham-wlgore/cartonization):
choose **Code → Download ZIP**, or clone the repository if you use Git.
Sign in with a GitHub account that has repository access. Git is optional for local use.

## What you can do

- Prepare shipment profiles from order lines and an explicit SKU-to-carton mapping.
- Compare named scenarios using the same shipment demand.
- Measure modeled shipping cost, shipper consumption and packing efficiency.
- Inspect single-carton capacities and packing choices.
- Export Excel reports and reproducible JSON results.

The default uses capacity interpolation at a configurable single-carton capacity
threshold of **10**. It avoids expensive 3D searches in high-capacity cases.
The default optimization objective preserves the original volume-and-quantity
formula; minimum modeled shipping cost is an explicit option.

## Quick setup for Python users

Python 3.10–3.13 is supported by the pinned environment; 3.12 is recommended.

```sh
python tools/setup_environment.py
# Then use the environment executable, for example on Mac:
.venv/bin/python -m cartonization compare examples/comparison.json
```

On Windows with the recommended Python 3.12, run `py -3.12 tools\setup_environment.py`
for setup, then use `.venv\Scripts\python.exe` for subsequent commands. Setup does
not require manual environment activation. See START_HERE.md for other Python versions.

## Guides

- [Workflow configurations and examples](docs/WORKFLOWS.md)
- [Input formats](docs/DATA_FORMATS.md)
- [Model assumptions and interpolation](docs/MODELING.md)
- [Copyable Copilot prompts](docs/PROMPTS.md)
- [Python API](docs/API.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Audit and release verification](docs/VERIFICATION.md)
- [Future capabilities](docs/BACKLOG.md)
- [Release notes](CHANGELOG.md)

## Development

```sh
python -m pip install -c constraints.txt -e ".[dev]"
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
python -m build
python tools/build_release.py
```

To create the distribution without the optional Windows launcher, run:

```sh
python tools/build_release.py --without-windows-launcher
```

This writes `dist/cartonization-0.2.0-no-windows-launcher.zip` and its SHA-256
checksum. The archive includes command-based Windows setup instructions and an
updated file manifest. Rebuilding from this extracted variant also omits the launcher.

Run these with the virtual environment's Python. The GitHub Actions workflow
defines Windows, Mac and Linux checks. See the repository's **Actions** tab for
the results of each run.

The ZIP contains source, guides, tests, synthetic examples and the original
bundled reference/history example. It excludes local analysis outputs, user data,
temporary scripts, caches and virtual environments. Generated reports are snapshots;
change configuration/input files and rerun to update them.
