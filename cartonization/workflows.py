"""Saved configuration workflows for Copilot and Python callers."""

from __future__ import annotations

import hashlib
import json
import math
import platform
from collections import Counter, defaultdict
from copy import deepcopy
from importlib.metadata import version
from pathlib import Path

from .analysis import analyze_loaded
from .costs import shipping_cost_zone4
from .io import build_shipment_profiles, iter_sheet_records
from .validation import InputError, dimensions, identifier, identifiers, integer, invalid, number

SCENARIO_KEYS = {
    "name",
    "history_file",
    "history_sheet",
    "frequency_column",
    "reference_file",
    "cartons",
    "shippers",
    "carton_sheet",
    "shipper_sheet",
    "carton_id_column",
    "shipper_id_column",
    "dimension_columns",
    "max_units_column",
    "fixed_cost",
    "carton_overrides",
    "shipper_overrides",
    "objective",
    "sample_ratio",
    "vector_length_limit",
    "vector_freq_limit",
    "random_seed",
    "interpolation_threshold",
    "packing_cap",
    "constrain_max_units",
    "solver_time_limit",
    "baseline",
}
PREPARE_KEYS = {
    "input_file",
    "sheets",
    "mapping_file",
    "mapping_sheet",
    "sku_column",
    "mapping_sku_column",
    "mapping_carton_column",
    "order_key_columns",
    "quantity_mode",
    "quantity_column",
    "exclude_skus",
}


def _keys(config, allowed, location):
    if not isinstance(config, dict):
        raise invalid(location, "Expected an object.")
    unknown = set(config) - allowed
    if unknown:
        raise invalid(location, f"Unknown settings: {sorted(unknown)}.")


def file_path(value, base_dir):
    path = Path(value).expanduser()
    return (Path(base_dir) / path).resolve() if not path.is_absolute() else path.resolve()


def load_config(path):
    """Read JSON. Paths inside it resolve relative to this configuration file."""
    path = Path(path).resolve()
    with path.open(encoding="utf-8-sig") as f:
        config = json.load(f)
    if not isinstance(config, dict):
        raise invalid(str(path), "Configuration must be a JSON object.")
    return config, path.parent


def file_digest(path):
    with Path(path).open("rb") as f:
        digest = hashlib.file_digest(f, "sha256") if hasattr(hashlib, "file_digest") else None
        if digest is not None:
            return digest.hexdigest()
        digest = hashlib.sha256()
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
        return digest.hexdigest()


def _catalog(config, path, kind, selected):
    sheet = config.get(f"{kind}_sheet", f"container_{kind}_dims")
    id_col = config.get(f"{kind}_id_column", kind.upper())
    dim_cols = config.get("dimension_columns", ["LENGTH", "WIDTH", "HEIGHT"])
    if not isinstance(dim_cols, list) or len(dim_cols) != 3 or len(set(dim_cols)) != 3:
        raise invalid("dimension_columns", "Provide three distinct column names.")
    max_col = config.get("max_units_column", "MAXUNITS")
    cols = [id_col] + dim_cols + ([max_col] if kind == "shipper" else [])
    overrides = config.get(f"{kind}_overrides", {})
    if not isinstance(overrides, dict) or set(overrides) - set(selected):
        raise invalid(f"{kind}_overrides", "Override keys must be selected IDs.")
    found = {}
    for row_num, row in iter_sheet_records(path, sheet, cols):
        rid = identifier(row[id_col], f"{sheet}!{id_col}{row_num}")
        if rid not in selected:
            continue
        if rid in found:
            raise invalid(f"{sheet}!{id_col}{row_num}", f"Duplicate ID {rid}.")
        found[rid] = (row_num, row)
    result = {}
    for rid in selected:
        row_num, row = found.get(rid, (None, {}))
        if rid not in found and rid not in overrides:
            raise invalid(sheet, f"Selected ID {rid!r} is missing and has no override.")
        location = f"{sheet}!row {row_num} ({rid})" if row_num else f"{kind}_overrides.{rid}"
        override = overrides.get(rid)
        if kind == "carton":
            result[rid] = dimensions(
                override if override is not None else [row[c] for c in dim_cols], location
            )
        else:
            override = override or {}
            _keys(override, {"dimensions", "max_units", "cost"}, f"shipper_overrides.{rid}")
            dims = dimensions(override.get("dimensions", [row.get(c) for c in dim_cols]), location)
            units = integer(override.get("max_units", row.get(max_col)), location + ".max_units")
            cost = override.get(
                "cost",
                shipping_cost_zone4(
                    dims, number(config.get("fixed_cost", 0), "fixed_cost", nonnegative=True)
                ),
            )
            result[rid] = dict(zip(("length", "width", "height"), dims)) | {
                "volume": math.prod(dims),
                "max_units": units,
                "cost": number(cost, location + ".cost", nonnegative=True),
            }
    return result


def validate_scenario_inputs(config, base_dir="."):
    """Read and validate selected data/settings without packing or solving."""
    _keys(config, SCENARIO_KEYS, "scenario")
    for key in ("history_file", "history_sheet", "reference_file", "cartons", "shippers"):
        if key not in config:
            raise invalid("scenario", f"Required setting {key!r} is missing.")
    cartons = identifiers(config["cartons"], "cartons")
    shippers = identifiers(config["shippers"], "shippers")
    history = file_path(config["history_file"], base_dir)
    reference = file_path(config["reference_file"], base_dir)
    profiles = build_shipment_profiles(
        history, config["history_sheet"], cartons, config.get("frequency_column", "FREQUENCY")
    )
    cs = _catalog(config, reference, "carton", cartons)
    ss = _catalog(config, reference, "shipper", shippers)
    if not profiles:
        raise invalid(
            config["history_sheet"], "No positive-frequency demand for the selected cartons."
        )
    ratio = number(config.get("sample_ratio", 1), "sample_ratio", positive=True)
    if ratio > 1:
        raise invalid("sample_ratio", "Must be <= 1.")
    if config.get("objective", "volume_penalty") not in ("volume_penalty", "shipping_cost"):
        raise invalid("objective", "Use volume_penalty or shipping_cost.")
    for key, default, minimum in [
        ("random_seed", 0, 0),
        ("vector_freq_limit", 0, 0),
        ("vector_length_limit", len(cartons), 1),
        ("interpolation_threshold", 10, 1),
        ("packing_cap", 100, 1),
        ("solver_time_limit", 60, 1),
    ]:
        value = config.get(key, default)
        if value is not None or key in ("random_seed", "vector_freq_limit"):
            integer(value, key, minimum=minimum)
    if not isinstance(config.get("constrain_max_units", False), bool):
        raise invalid("constrain_max_units", "Use true or false.")
    return profiles, cs, ss, history, reference


def run_scenario(config, base_dir=".", progress=None):
    """Run one saved scenario; return observed totals with reproducible provenance."""
    _keys(config, SCENARIO_KEYS, "scenario")
    for key in ("history_file", "reference_file"):
        if key not in config:
            raise invalid("scenario", f"Required setting {key!r} is missing.")
    sources = [file_path(config[k], base_dir) for k in ("history_file", "reference_file")]
    hashes = {path: file_digest(path) for path in sources}
    profiles, cartons, shippers, history, reference = validate_scenario_inputs(config, base_dir)
    result = analyze_loaded(
        profiles,
        cartons,
        shippers,
        name=config.get("name", "Scenario"),
        sample_ratio=config.get("sample_ratio", 1),
        vector_length_limit=config.get("vector_length_limit"),
        vector_freq_limit=config.get("vector_freq_limit", 0),
        random_seed=config.get("random_seed", 0),
        objective=config.get("objective", "volume_penalty"),
        threshold=config.get("interpolation_threshold", 10),
        packing_cap=config.get("packing_cap", 100),
        constrain_max_units=config.get("constrain_max_units", False),
        solver_time_limit=config.get("solver_time_limit", 60),
        progress=progress,
    )
    if any(file_digest(path) != digest for path, digest in hashes.items()):
        raise invalid(
            "source workbooks",
            "An input changed while the analysis was running; rerun with unchanged inputs.",
        )
    result.provenance = {
        "input_files": [
            {"name": history.name, "sha256": hashes[history]},
            {"name": reference.name, "sha256": hashes[reference]},
        ],
        "history_sheet": config["history_sheet"],
        "config": deepcopy(config),
        "python": platform.python_version(),
        "dependencies": {
            n: version(n) for n in ("cartonization", "numpy", "openpyxl", "py3dbp", "pulp")
        },
        "cost_model": "Legacy Zone 4 dimensional-weight estimate + fixed cost; explicit shipper cost overrides take precedence.",
    }
    return result


def expand_batch(config):
    """Merge common defaults into explicitly named scenarios."""
    _keys(config, {"defaults", "scenarios"}, "batch")
    defaults = config.get("defaults", {})
    _keys(defaults, SCENARIO_KEYS - {"name", "baseline"}, "defaults")
    specs = config.get("scenarios", [])
    if not isinstance(specs, list) or not specs:
        raise invalid("scenarios", "Provide a nonempty list of named scenarios.")
    merged = []
    for scenario in specs:
        _keys(scenario, SCENARIO_KEYS, "scenario")
        item = deepcopy(defaults)
        # Override objects replace the common object; there is no hidden nested merge.
        item.update(deepcopy(scenario))
        item["name"] = identifier(item.get("name"), "scenario.name")
        merged.append(item)
    names = [s["name"] for s in merged]
    if len(set(names)) != len(names):
        raise invalid("scenarios", "Scenario names must be unique.")
    for spec in merged:
        if "baseline" in spec and (
            spec["baseline"] not in names or spec["baseline"] == spec["name"]
        ):
            raise invalid(spec["name"], "baseline must name a different scenario in this batch.")
    return merged


def _demand_key(result):
    return [(p["frequency"], sorted(p["counts"].items())) for p in result.shipment_profiles]


def compare_scenarios(results, specs):
    """Compare observed totals only when baseline demand and sampling settings match."""
    by_name = {r.name: r for r in results}
    rows, usage = [], []
    for spec in specs:
        if "baseline" not in spec:
            continue
        current, baseline = by_name[spec["name"]], by_name[spec["baseline"]]
        if (
            _demand_key(current) != _demand_key(baseline)
            or current.coverage["total_frequency"] != baseline.coverage["total_frequency"]
            or any(
                current.settings[k] != baseline.settings[k]
                for k in ("sample_ratio", "random_seed", "vector_length_limit", "vector_freq_limit")
            )
        ):
            raise invalid(
                current.name,
                "Comparison requires identical demand, filters, sampling ratio and seed. Run different demand as separate scenarios.",
            )
        rows.append(
            {
                "scenario": current.name,
                "baseline": baseline.name,
                "cost_before": baseline.total_cost,
                "cost_after": current.total_cost,
                "cost_change": current.total_cost - baseline.total_cost,
                "cost_change_fraction": (current.total_cost / baseline.total_cost - 1)
                if baseline.total_cost
                else None,
                "efficiency_before": baseline.packing_efficiency / 100,
                "efficiency_after": current.packing_efficiency / 100,
                "efficiency_change_pp": current.packing_efficiency - baseline.packing_efficiency,
                "shippers_before": sum(baseline.total_count.values()),
                "shippers_after": sum(current.total_count.values()),
            }
        )
        for sid in sorted(set(current.total_count) | set(baseline.total_count)):
            before, after = baseline.total_count.get(sid, 0), current.total_count.get(sid, 0)
            usage.append(
                {
                    "scenario": current.name,
                    "baseline": baseline.name,
                    "shipper": sid,
                    "before": before,
                    "after": after,
                    "change": after - before,
                }
            )
    return rows, usage


def run_scenarios(config, base_dir=".", progress=None):
    """Run a batch strictly: no combined final report if any scenario fails."""
    specs = expand_batch(config)
    for spec in specs:
        validate_scenario_inputs(spec, base_dir)
    results = []
    for i, spec in enumerate(specs):
        if progress:
            progress(f"Scenario {i + 1} of {len(specs)}: {spec['name']}")
        results.append(run_scenario(spec, base_dir, progress))
    comparison, usage = compare_scenarios(results, specs)
    return results, comparison, usage


def prepare_shipment_history(config, base_dir="."):
    """Map order lines to carton profiles. Any invalid/unmapped row stops preparation.

    Sheet identity is always part of the order key. Quantity mode and order keys
    are required. Explicit excluded SKUs quarantine the entire affected order.
    Duplicate-looking rows are counted and retained; no deduplication is inferred.
    """
    _keys(config, PREPARE_KEYS, "preparation")
    required = (
        "input_file",
        "sheets",
        "mapping_file",
        "mapping_sheet",
        "sku_column",
        "mapping_sku_column",
        "mapping_carton_column",
        "order_key_columns",
        "quantity_mode",
    )
    for key in required:
        if key not in config:
            raise invalid("preparation", f"Required setting {key!r} is missing.")
    sheets = identifiers(config["sheets"], "sheets")
    keys = identifiers(config["order_key_columns"], "order_key_columns")
    mode = config["quantity_mode"]
    if mode not in ("column", "one_per_row") or (
        mode == "column" and not config.get("quantity_column")
    ):
        raise invalid("quantity_mode", "Use column with quantity_column, or one_per_row.")
    source, mapping_path = (
        file_path(config["input_file"], base_dir),
        file_path(config["mapping_file"], base_dir),
    )
    sku_col, carton_col = config["mapping_sku_column"], config["mapping_carton_column"]
    mapping, issues = {}, []
    for row_num, row in iter_sheet_records(
        mapping_path, config["mapping_sheet"], [sku_col, carton_col]
    ):
        try:
            sku = identifier(row[sku_col], f"{config['mapping_sheet']}!{sku_col}{row_num}")
            carton = identifier(row[carton_col], f"{config['mapping_sheet']}!{carton_col}{row_num}")
            if sku in mapping:
                raise invalid(
                    f"{config['mapping_sheet']}!row {row_num}", f"Duplicate SKU mapping {sku!r}."
                )
            mapping[sku] = carton
        except InputError as exc:
            issues.extend(exc.issues)
    excluded = (
        set(identifiers(config["exclude_skus"], "exclude_skus"))
        if config.get("exclude_skus")
        else set()
    )
    prepared, stats = {}, []
    cartons = sorted(set(mapping.values()))
    for sheet in sheets:
        orders, excluded_orders, seen_rows = defaultdict(Counter), set(), set()
        cols = list(
            dict.fromkeys(
                keys
                + [config["sku_column"]]
                + ([config["quantity_column"]] if mode == "column" else [])
            )
        )
        input_rows = input_units = duplicate_rows = excluded_rows = 0
        for row_num, row in iter_sheet_records(source, sheet, cols):
            input_rows += 1
            try:
                order = tuple(identifier(row[k], f"{sheet}!{k}{row_num}") for k in keys)
                sku = identifier(
                    row[config["sku_column"]], f"{sheet}!{config['sku_column']}{row_num}"
                )
                qty = (
                    integer(
                        row[config["quantity_column"]],
                        f"{sheet}!{config['quantity_column']}{row_num}",
                        minimum=1,
                    )
                    if mode == "column"
                    else 1
                )
                input_units += qty
                signature = (order, sku, qty)
                duplicate_rows += int(signature in seen_rows)
                seen_rows.add(signature)
                if sku in excluded:
                    excluded_orders.add(order)
                    excluded_rows += 1
                elif sku not in mapping:
                    raise invalid(
                        f"{sheet}!row {row_num}", f"Unmapped SKU {sku!r}; order {order!r}."
                    )
                else:
                    orders[order][mapping[sku]] += qty
            except InputError as exc:
                issues.extend(exc.issues)
        retained = {key: value for key, value in orders.items() if key not in excluded_orders}
        profiles = Counter(tuple(counts.get(c, 0) for c in cartons) for counts in retained.values())
        prepared[sheet] = [
            {"frequency": f, "counts": dict(zip(cartons, counts))}
            for counts, f in sorted(profiles.items())
        ]
        stats.append(
            {
                "sheet": sheet,
                "input_rows": input_rows,
                "input_units": input_units,
                "included_orders": len(retained),
                "included_units": sum(sum(c.values()) for c in retained.values()),
                "excluded_orders": len(excluded_orders),
                "explicitly_excluded_rows": excluded_rows,
                "duplicate_looking_rows_retained": duplicate_rows,
                "profiles": len(profiles),
            }
        )
    if issues:
        raise InputError(
            f"Preparation stopped: {len(issues)} input issue(s). No partial profiles were written.",
            issues,
        )
    if not any(prepared.values()):
        raise invalid("preparation", "No orders remain after explicit exclusions.")
    return {
        "sheets": prepared,
        "statistics": stats,
        "cartons": cartons,
        "provenance": {
            "config": deepcopy(config),
            "input_sha256": file_digest(source),
            "mapping_sha256": file_digest(mapping_path),
        },
    }
