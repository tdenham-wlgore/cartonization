# -*- coding: utf-8 -*-
"""Backward-compatible re-exports.

This module is deprecated. Prefer importing from the `cartonization` package.
"""

from __future__ import annotations

import warnings

from cartonization import (
    build_shipment_profiles,
    calculate_cost_count,
    comingle_frontier_points,
    comingle_tester,
    generate_max_fits_dict,
    generate_packings,
    load_reference_mapping,
    max_cartons_four_quadrant,
    read_xlsx_as_dicts,
    read_xlsx_sheet_rows,
    scenario_analysis,
    shipping_cost_zone4,
    solve_min_integer,
    upper_bounds_for_solve_min_integer,
)

__all__ = [
    "solve_min_integer",
    "upper_bounds_for_solve_min_integer",
    "read_xlsx_sheet_rows",
    "read_xlsx_as_dicts",
    "load_reference_mapping",
    "build_shipment_profiles",
    "max_cartons_four_quadrant",
    "comingle_tester",
    "comingle_frontier_points",
    "generate_max_fits_dict",
    "generate_packings",
    "shipping_cost_zone4",
    "calculate_cost_count",
    "scenario_analysis",
]

warnings.warn(
    "cartonization_functions is deprecated. Import from `cartonization` instead.",
    DeprecationWarning,
    stacklevel=2,
)
