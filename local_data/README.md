# Put your input workbooks here

Copy the Excel workbooks you want to analyze into this folder. Use a descriptive
name such as `shipments.xlsx`. You can create subfolders for separate analyses.
Keep your original workbooks unchanged; generated reports go into `outputs`.

In GitHub Copilot Chat in VS Code, select agent mode and start with:

> Inspect `local_data/shipments.xlsx`, identify its sheets and columns, and help
> me configure a cartonization analysis. Save the configuration in `my_scenarios`
> and preserve the original workbook. Ask me for any missing mapping or column
> definitions before running the analysis.

Replace `shipments.xlsx` with your file's name. For required input formats, see
the [input guide](../docs/DATA_FORMATS.md).

Setup creates `my_scenarios` automatically. A configuration saved directly in
that folder can refer to this workbook as `../local_data/shipments.xlsx`.
Each analysis writes reports and results to a new folder under `outputs`.

Only this README is tracked in Git. Other files and subfolders here are ignored
by normal Git commits and excluded from the project's release packages. Keep
this README in place, and do not force-add real data to Git.

Git exclusions do not prevent Copilot from reading files you ask it to inspect.
Use company-approved data and Copilot settings.
