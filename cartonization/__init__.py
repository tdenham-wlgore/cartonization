"""Cartonization analysis package. Imports are lazy so diagnostics work before setup."""

from importlib import import_module

__version__ = "0.2.0"

_EXPORTS = {
    "solve_min_integer": "solver",
    "upper_bounds_for_solve_min_integer": "solver",
    "read_xlsx_sheet_rows": "io",
    "read_xlsx_as_dicts": "io",
    "stream_xlsx_as_dicts": "io",
    "load_reference_mapping": "io",
    "build_shipment_profiles": "io",
    "max_cartons_four_quadrant": "packing",
    "comingle_tester": "packing",
    "comingle_frontier_points": "packing",
    "generate_max_fits_dict": "packing",
    "generate_packings": "packing",
    "shipping_cost_zone4": "costs",
    "calculate_cost_count": "analysis",
    "scenario_analysis": "analysis",
    "ScenarioResult": "analysis",
    "validate_scenario_inputs": "workflows",
    "prepare_shipment_history": "workflows",
    "run_scenario": "workflows",
    "run_scenarios": "workflows",
    "compare_scenarios": "workflows",
    "export_report": "reporting",
    "export_prepared": "reporting",
    "InputError": "validation",
    "AnalysisError": "validation",
}
__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    value = getattr(import_module(f".{_EXPORTS[name]}", __name__), name)
    globals()[name] = value
    return value
