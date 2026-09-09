# Cartonization analysis

Use GitHub Copilot in Visual Studio Code to run cartonization analyses in plain
language. This repository handles carton and shipper capacities, shipment profiles,
scenario comparisons, and Excel reports. You do not need to write Python to use it.

## What you can do

- Prepare shipment profiles from order lines and an explicit SKU-to-carton mapping.
- Compare named scenarios using the same shipment demand.
- Measure modeled shipping cost, shipper consumption and packing efficiency.
- Inspect single-carton capacities and packing choices.
- Export Excel reports and reproducible JSON results.

## 1. Get the repository

Open the [private GitHub repository](https://github.com/tdenham-wlgore/cartonization)
and sign in with a GitHub account that has access. Choose **Code → Download ZIP**,
then extract it into a local folder you can write to. If you use Git, clone the
repository instead. Git is optional for local use.

Keep the complete folder together. Do not run setup inside the ZIP viewer. If the
ZIP is on a shared drive, copy and extract it locally first; each person should
have their own working folder.

Create `local_data` inside the folder for your workbooks and `my_scenarios` for
saved configurations. These folders and generated outputs are excluded from Git.

## 2. Install the prerequisites

You need:

- [Visual Studio Code](https://code.visualstudio.com/).
- [Python 3.10–3.13](https://www.python.org/downloads/); **3.12 is recommended**.
- A GitHub account with access to this repository and GitHub Copilot.

Ask company IT for help if installation or Copilot is managed centrally.
This workflow uses **GitHub Copilot in VS Code**; Microsoft 365 Copilot is a
different product. See the [VS Code setup guide](https://code.visualstudio.com/docs/setup/setup-overview).

On Windows, include the Python launcher during installation. On Mac, use the
Python installer from python.org if a supported Python is not already installed.

## 3. Run setup in VS Code

Choose **File → Open Folder** and open your extracted or cloned folder. Accept
workspace trust only for the company-approved copy. Choose **Terminal → New Terminal**,
then run the command for your computer.

**Windows, with the recommended Python 3.12:**

```powershell
py -3.12 tools\setup_environment.py
```

If you installed Python 3.10, 3.11 or 3.13, replace `-3.12` with that version.
If `py` is unavailable but a supported Python is on your PATH, use
`python tools\setup_environment.py`.

**Mac:**

```sh
python3 tools/setup_environment.py
```

If `python3` selects an unsupported version, use a supported interpreter explicitly,
such as `python3.12 tools/setup_environment.py`.

Setup creates a separate `.venv` Python environment inside this folder, installs
the tested dependencies and runs a small solver check. It needs internet access
for package installation and does not install Python itself. Success ends with
**“Ready to run cartonization.”**

Do not move or copy `.venv` to another computer. Rerun setup after moving the
source folder or installing a new release.

## 4. Connect GitHub Copilot

Install the recommended Python and GitHub Copilot extensions in VS Code and sign
in to your GitHub account. Open the Command Palette, choose **Python: Select
Interpreter**, and select this folder's `.venv` if it is not already selected.

Open Copilot Chat and select its agent mode so it can run the supplied commands.
Company policy may require approval for terminal runs. Repository instructions
in [.github/copilot-instructions.md](.github/copilot-instructions.md) tell Copilot
which workflows and defaults to use. See the
[VS Code custom-instructions guide](https://code.visualstudio.com/docs/agent-customization/custom-instructions)
for how these are applied.

## 5. Try the practice analysis

Paste this into Copilot:

> Run the environment diagnostic, then run examples/comparison.json using the
> cartonization comparison workflow. Open the generated Excel report and explain
> cost, packing efficiency, shipper usage and demand coverage.

The practice example compares the same **eight orders**. Expected modeled cost
is **$144 before and $120 after**, with **eight shippers** in both cases.
Efficiency improves from approximately **17.7% to 26.4%**. These are fictional
practice costs.

Each run creates a new folder under `outputs`. Open `report.xlsx`; detailed
JSON results and the configuration snapshot are alongside it. Reports are
snapshots: change the inputs or configuration and rerun to update them.

For manual commands, use `.venv\Scripts\python.exe` on Windows or
`.venv/bin/python` on Mac. For example, on Mac:

```sh
.venv/bin/python -m cartonization compare examples/comparison.json
```

You do not need to activate the environment when using its Python executable.

## 6. Use your own data

Copy your input workbooks into `local_data`. Ask Copilot to inspect their sheet
names and column headers, create a configuration in `my_scenarios` using the
[workflow guide](docs/WORKFLOWS.md), and validate it before running an analysis.
Paths in a configuration are resolved relative to that configuration's folder.

If each input row describes a SKU/order line, use the preparation workflow first.
Specify which columns identify an order and whether quantity comes from a column
or each row represents one unit. Unmapped SKUs produce an issue report.

Results include **full eligible history by default**. Mixed packings automatically
use capacity interpolation when any active carton has a single-type capacity of
**10 or more**, with a configurable threshold. This avoids expensive 3D searches
in high-capacity cases. Geometric checking throughout is an explicit option.

The default optimization objective preserves the original volume-and-quantity
formula; minimum modeled shipping cost is another option. Invalid inputs or an
order that cannot be analyzed stop the run and produce an issue report.
See [model assumptions](docs/MODELING.md) for interpretation and limitations.

## Guides

- [Workflows, configurations and Copilot requests](docs/WORKFLOWS.md)
- [Input formats](docs/DATA_FORMATS.md)
- [Model assumptions and interpolation](docs/MODELING.md)
- [Python API](docs/API.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Maintenance, verification and future capabilities](docs/MAINTENANCE.md)
- [Release notes](CHANGELOG.md)

## Updating or asking for help

For a downloaded release, extract the new copy into a new folder and run setup
there. Copy your own data and configurations across and keep old results with
old releases. If you use Git, update your checkout and rerun setup when package
requirements change; preserve local changes before updating.

When requesting help, provide the release version, configuration and issue report.
The [troubleshooting guide](docs/TROUBLESHOOTING.md) explains common failures.
