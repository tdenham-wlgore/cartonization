# Start here

This folder lets you ask GitHub Copilot to run cartonization analyses in plain language.
You do not need to write Python or create a GitHub repository.

## 1. Put the folder on your computer

Open the [private repository](https://github.com/tdenham-wlgore/cartonization)
and sign in with a GitHub account that has access. Choose **Code → Download ZIP**,
then extract the ZIP into a local folder you can write to. If you use Git, you
can clone the repository instead and use that local folder.

Do not run setup from inside the ZIP viewer. If the ZIP is on a shared drive,
copy and extract it locally first. Avoid having several people run setup in the
same shared folder.

Keep the complete folder together. Use a separate `local_data` folder inside it
for your workbooks; use `my_scenarios` for your saved configurations.

## 2. Install the prerequisites

You need Visual Studio Code, Python 3.10–3.13 (3.12 recommended), and a GitHub account
with access to GitHub Copilot. Ask company IT for help if installation or Copilot
is managed centrally. Ordinary Microsoft 365 Copilot is a different product.

- Python downloads: https://www.python.org/downloads/
- VS Code: https://code.visualstudio.com/
- GitHub Copilot setup: https://code.visualstudio.com/docs/setup/setup-overview

On Windows, include the Python launcher during installation. On Mac, use the
Python installer from python.org if a suitable Python is not already installed.

## 3. Run setup

**Windows:** open the extracted folder in VS Code using **File → Open Folder**.
Choose **Terminal → New Terminal**, then paste this command and press Enter
(using the recommended Python 3.12):

```powershell
py -3.12 tools\setup_environment.py
```

If you installed Python 3.10, 3.11 or 3.13, replace `-3.12` with that version.
If the `py` command is unavailable but a supported Python is on your PATH, use
`python tools\setup_environment.py` instead. You do not need a Windows launcher file.

**Mac:** double-click `setup_mac.command`. If macOS blocks the launcher or it has
lost its executable permission after extraction, open Terminal in this folder and run:

```sh
python3 tools/setup_environment.py
```

Setup creates a private `.venv` environment in this folder, installs the tested
dependencies and runs a small solver check. It needs internet access for package
installation. Success ends with **“Ready to run cartonization.”**

Do not move or copy the `.venv` directory to another computer. Rerun setup after
moving the source folder or installing a new release.

## 4. Open the folder in VS Code

Choose **File → Open Folder** and select this extracted folder. Accept workspace
trust only for the company-approved copy. Install the recommended Python and
GitHub Copilot extensions and sign in to your GitHub account.

Use **Python: Select Interpreter** from the Command Palette if needed and select
this folder's `.venv`. Open Copilot Chat and select its agent mode so it can run
the supplied commands. Your company policy may require you to approve terminal runs.

Repository instructions are in `.github/copilot-instructions.md`. They tell
Copilot to use the provided workflows and the intended interpolation default.
See https://code.visualstudio.com/docs/agent-customization/custom-instructions.

## 5. Try the practice analysis

Paste this into Copilot:

> Run the environment diagnostic, then run examples/comparison.json using the
> cartonization comparison workflow. Open the generated Excel report and explain
> cost, packing efficiency, shipper usage and demand coverage.

The synthetic example compares the same eight orders. Expected modeled cost is
**$144 before and $120 after**, with eight shippers in both cases. Efficiency
improves from approximately **17.7% to 26.4%**. These are fictional practice costs.

Each run gets its own new folder under `outputs`. Open `report.xlsx`; detailed
results and the configuration snapshot are alongside it.

## 6. Use your own data

Copy input workbooks into `local_data`. Ask Copilot to inspect their sheet names
and column headers and make a configuration using [WORKFLOWS.md](docs/WORKFLOWS.md).
Have it validate the configuration before running the analysis.

If your data is one row per SKU/order line, first use the preparation workflow.
You must specify which columns identify an order and whether quantity is in a
column or each row represents one unit. Unmapped SKUs produce an issue report.

Results use full eligible history by default. Large-capacity mixed packings use
interpolation automatically; no extra approval or slow geometric proof is needed.
The model stops if an order cannot be analyzed, rather than returning incomplete totals.

## Updating or asking for help

Extract a new release into a new folder and run setup there. Copy your own data
and configurations across; keep old results with the old release. Relative paths
in a configuration are resolved from that configuration's folder.

When requesting help, provide the release version, configuration and issue report.
The [troubleshooting guide](docs/TROUBLESHOOTING.md) explains common failures.
