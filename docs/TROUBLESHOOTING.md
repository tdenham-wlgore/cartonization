# Troubleshooting

Follow the [README setup instructions](../README.md#3-run-setup-in-vs-code) in
the VS Code terminal on both Windows and Mac.

| Symptom | What to do |
|---|---|
| Python command is missing | Install Python 3.10–3.13 with company IT's approved method. On Windows include the Python launcher. |
| `py` is not recognized on Windows | If a supported Python is on your PATH, run `python tools\setup_environment.py` in the extracted folder. Otherwise ask IT to install the Python launcher. |
| `py -3.12` cannot find Python 3.12 | Install the recommended Python 3.12 or replace `-3.12` with your installed supported version: `-3.10`, `-3.11` or `-3.13`. |
| Setup selected Python 3.14 or newer | Run tools/setup_environment.py explicitly with a supported interpreter, preferably Python 3.12: `py -3.12 tools\setup_environment.py` on Windows or `python3.12 tools/setup_environment.py` on Mac. |
| pip cannot download packages | Check proxy/network access with IT. The repository does not change company network settings. |
| Wrong interpreter / module not found | Select this folder's .venv in VS Code, or use its Python executable explicitly. |
| CBC unavailable or blocked | Rerun setup and doctor. Check antivirus/application-control policy with IT. The pinned PuLP distribution supplies CBC on supported platforms. |
| `python3` is not recognized on Mac | Install a supported Python using company IT's approved method, then reopen the VS Code terminal and run `python3 tools/setup_environment.py`. |
| Worksheet or column is missing | Read the issue report, correct the JSON sheet/header settings, then validate again. Names are case-sensitive. |
| Selected ID missing | Correct the selected list, reference workbook or explicit override. Do not silently omit the ID. |
| Formula input rejected | Paste the calculated values into a separate input workbook, preserving the original. |
| Unmapped SKU | Update the explicit mapping. Rerun preparation. If an exclusion is intended, configure it explicitly and inspect excluded orders. |
| Fractional / negative quantity | Verify the source system's quantity meaning; counts must be whole units. |
| No remaining demand | Check selected cartons, zero frequencies, sheet selection and explicit vector filters. |
| Order cannot be solved | Review the affected profile and whether selected shippers can carry each carton under enabled limits. No final totals were produced. |
| Feasible but not proven optimal | A time-limited solution was found. Review the profile status and increase solver_time_limit if needed. |
| Run is slow | Keep the default interpolation. Start with a smaller explicit preview if appropriate; progress identifies the current stage. A per-profile solver limit is not an overall run-time limit. |
| Windows reports file is in use | Close the output workbook in Excel before manually replacing it. CLI runs normally write fresh folders. |
| Results differ after an update | Check input hashes, objective, dimensions, interpolation threshold, sample seed, cap and software versions. Read release notes for correctness changes. |

If setup is interrupted, rerun it. If .venv was copied or the folder moved, remove
only the generated .venv folder and rerun setup; keep your input/configuration files.

See [maintenance and verification](MAINTENANCE.md) for platform checks and current
GitHub Actions results. Company network and application policies should also be
checked on a recipient's computer.
