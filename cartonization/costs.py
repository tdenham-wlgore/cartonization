# -*- coding: utf-8 -*-
"""Shipping cost models."""

from __future__ import annotations

import math
from typing import Tuple

from .validation import dimensions, number


def shipping_cost_zone4(
    shipper: Tuple[float, float, float],
    fixed_cost: float,
) -> float:
    """
    Compute shipping cost for Zone 4 based on dimensional weight.

    Args:
        shipper: Shipper dimensions in inches (dim1, dim2, dim3).
        fixed_cost: Fixed carton/material cost added to the shipping cost.

    Returns:
        Total cost (shipping + fixed_cost)
    """
    shipper = dimensions(shipper, "shipper")
    fixed_cost = number(fixed_cost, "fixed_cost", nonnegative=True)
    dim_weight_lbs = math.ceil(math.prod(math.ceil(x) for x in shipper) / 139.0)

    # The cost function is patchwork
    if dim_weight_lbs <= 7.0:
        ship_cost = 7.97
    elif dim_weight_lbs > 7.0 and dim_weight_lbs < 60.0:
        ship_cost = round((0.507425) * dim_weight_lbs + (4.433389), 2)
    elif dim_weight_lbs >= 60 and dim_weight_lbs < 85.0:
        ship_cost = round((0.337331) * dim_weight_lbs + (14.057385), 2)
    elif dim_weight_lbs >= 85.0 and dim_weight_lbs < 100.0:
        ship_cost = round((0.376321) * dim_weight_lbs + (11.988429), 2)
    else:
        ship_cost = round((0.558986) * dim_weight_lbs + (0.004261), 2)

    return ship_cost + fixed_cost
