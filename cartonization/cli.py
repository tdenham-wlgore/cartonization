"""Small command interface; doctor stays usable even if optional imports are missing."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from datetime import datetime
from importlib.metadata import version
from pathlib import Path
from uuid import uuid4


def doctor():
    """Print environment checks and solve a tiny CBC model; never install anything."""
    ok = (3, 10) <= sys.version_info[:2] <= (3, 13)
    print(
        f"Python {sys.version.split()[0]}: {'supported' if ok else 'use Python 3.10 through 3.13'}"
    )
    for name in ("numpy", "openpyxl", "py3dbp", "pulp"):
        try:
            importlib.import_module(name)
            print(f"{name}: {version(name)}")
        except ImportError as exc:
            print(f"{name}: unavailable ({exc})")
            ok = False
    if ok:
        try:
            from .solver import solve_min_integer

            x, cost, status = solve_min_integer([2], [[1]], [3], upper_bounds=[2])
            ok = (x, cost, status) == ([2], 6.0, "Optimal")
            print(f"CBC: {'tiny solve passed' if ok else 'unexpected result'}")
        except Exception as exc:
            print(f"CBC: unavailable or failed ({exc})")
            ok = False
    print("Ready to run cartonization." if ok else "Rerun setup or see docs/TROUBLESHOOTING.md.")
    return 0 if ok else 1


def _output(root, command):
    path = Path(root).resolve() / f"{command}-{datetime.now():%Y%m%d-%H%M%S}-{uuid4().hex[:6]}"
    path.mkdir(parents=True, exist_ok=False)
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run reproducible cartonization workflows.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="Check dependencies and the CBC solver.")
    for name, help_text in [
        ("validate", "Validate a scenario, batch, or preparation configuration."),
        ("prepare", "Convert order lines into carton shipment profiles."),
        ("run", "Run one scenario."),
        ("compare", "Run a named scenario batch and baseline comparisons."),
    ]:
        p = sub.add_parser(name, help=help_text)
        p.add_argument("config", type=Path)
        p.add_argument(
            "--output-dir",
            type=Path,
            default=Path("outputs"),
            help="Parent folder for a new result directory (default: ./outputs).",
        )
    args = parser.parse_args(argv)
    if args.command == "doctor":
        return doctor()
    directory = None
    try:
        from .reporting import export_issue_report, export_prepared, export_report, write_json
        from .workflows import (
            expand_batch,
            load_config,
            prepare_shipment_history,
            run_scenario,
            run_scenarios,
            validate_scenario_inputs,
        )

        config, base = load_config(args.config)

        def progress(message):
            print(message, flush=True)

        if args.command == "validate":
            if "scenarios" in config:
                for spec in expand_batch(config):
                    validate_scenario_inputs(spec, base)
            elif "input_file" in config:
                prepare_shipment_history(config, base)
            else:
                validate_scenario_inputs(config, base)
            print("Inputs and configuration are valid. Packing and solving have not been run.")
            return 0
        if args.command == "prepare":
            prepared = prepare_shipment_history(config, base)
            directory = _output(args.output_dir, "prepare")
            path = export_prepared(prepared, directory)
        else:
            if args.command == "compare":
                results, comparison, usage = run_scenarios(config, base, progress)
            else:
                results, comparison, usage = [run_scenario(config, base, progress)], [], []
            directory = _output(args.output_dir, args.command)
            path = export_report(results, directory, comparison, usage)
            for r in results:
                print(
                    f"{r.name}: cost ${r.total_cost:,.2f}; {sum(r.total_count.values()):,} shippers; "
                    f"efficiency {r.packing_efficiency:.1f}%; demand coverage {r.coverage['included_fraction']:.1%}"
                )
                for notice in r.warnings:
                    print(f"Note: {notice}")

        # A saved run can be invoked from its output folder without breaking
        # source paths that were relative to the original configuration.
        def resolved(value):
            if isinstance(value, dict):
                return {
                    k: str((base / Path(v).expanduser()).resolve())
                    if k in ("history_file", "reference_file", "input_file", "mapping_file")
                    else resolved(v)
                    for k, v in value.items()
                }
            if isinstance(value, list):
                return [resolved(v) for v in value]
            return value

        write_json(directory / "configuration.json", resolved(config))
        print(f"Saved: {path}")
        return 0
    except (
        ValueError,
        TypeError,
        OverflowError,
        KeyError,
        RuntimeError,
        OSError,
        ImportError,
    ) as exc:
        issues = getattr(exc, "issues", [{"location": str(args.config), "message": str(exc)}])
        try:
            directory = directory or _output(args.output_dir, "issues")
            # JSON issue output works even when the Excel dependency is unavailable.
            (directory / "issues.json").write_text(
                json.dumps({"issues": issues}, indent=2, default=str), encoding="utf-8"
            )
            try:
                from .reporting import export_issue_report

                export_issue_report(issues, directory)
            except (ImportError, OSError, ValueError):
                pass
            print(f"Stopped: {exc}\nIssue report: {directory}", file=sys.stderr)
        except OSError as report_error:
            print(
                f"Stopped: {exc}\nCould not write the issue report: {report_error}", file=sys.stderr
            )
        return 2
