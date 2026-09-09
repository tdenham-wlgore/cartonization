"""Packing heuristics with capacity interpolation and reproducible geometric checks."""

from __future__ import annotations

import itertools as it
import math
import random
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal
from functools import lru_cache
from typing import Sequence

from py3dbp import Bin, Item, Packer

from .validation import dimensions, integer


def max_cartons_four_quadrant(shipper, carton):
    """Constructive capacity using four disjoint rectangular regions; inches in, units out."""
    return _max_cartons_four_quadrant(
        tuple(Decimal(str(v)) for v in dimensions(shipper, "shipper")),
        tuple(Decimal(str(v)) for v in dimensions(carton, "carton")),
    )


@lru_cache(maxsize=8192)
def _max_cartons_four_quadrant(
    shipper: Sequence[float],
    carton: Sequence[float],
) -> int:
    """
    Function to find the best four quadrant cartonization for a carton and shipper.

    Args:
        shipper: Iterable with 3 numeric elements for shipper interior dimensions (dim1, dim2, dim3).
        carton: Iterable with 3 numeric elements for carton outer dimensions (dim1, dim2, dim3).

    Returns:
        Constructive four-quadrant capacity (not a proof of the global maximum).

    Notes:
        - Unique rotations are reused and results cached by dimension tuples.
        - Dependent on: import itertools as it
    """
    max_qty = 0  # initialize max_qty
    volume_bound = int(math.prod(shipper) / math.prod(carton))
    cartons = tuple(sorted(set(it.permutations(carton))))  # all rotations of the carton

    for rot0 in cartons:  # test each rotation
        # calculate cartons in main quadrant
        main_qty = int(shipper[0] / rot0[0]) * int(shipper[1] / rot0[1]) * int(shipper[2] / rot0[2])
        if main_qty == volume_bound:
            return main_qty

        if main_qty > 0:  # only proceed if a carton fit into the main quadrant
            # calculate unfilled space for each side
            side_remaining = [shipper[i] - rot0[i] * int(shipper[i] / rot0[i]) for i in range(3)]

            # Will attempt to fill each side in a particular order, as the order can make a difference
            for side_order in it.permutations([0, 1, 2]):
                # for each quadrant, try filling with each rotation of the carton
                for rot1 in it.product(cartons, repeat=3):
                    # reorder indexes according to the order in which sides are packed
                    first_side = side_order[0]  # index for the first side
                    second_side = side_order[1]  # index for the second side
                    third_side = side_order[2]  # index for the third side

                    side_dims = [
                        [shipper[i] if i != k else side_remaining[i] for i in range(3)]
                        for k in range(3)
                    ]

                    # seperate out the cartons to be packed into each respective side
                    first_carton = rot1[0]  # carton to pack into the first side
                    second_carton = rot1[1]  # carton to pack into the second side
                    third_carton = rot1[2]  # carton to pack into the third side

                    # calculate qty that fits into first side, using first carton
                    side_dim = side_dims[first_side]
                    first_side_qty = (
                        int(side_dim[0] / first_carton[0])
                        * int(side_dim[1] / first_carton[1])
                        * int(side_dim[2] / first_carton[2])
                    )

                    if (
                        first_side_qty > 0
                    ):  # if any quantity packed into the first side must check for intrusions
                        for s in [
                            i for i in side_order if i != first_side
                        ]:  # iterate over second and third sides
                            intrusion = first_carton[s] * int(side_dim[s] / first_carton[s])
                            if shipper[s] - intrusion < side_remaining[s]:
                                side_dims[s][first_side] = (
                                    shipper[first_side] - side_remaining[first_side]
                                )

                    # calculate qty that fits into second side, using second carton
                    side_dim = side_dims[second_side]
                    second_side_qty = (
                        int(side_dim[0] / second_carton[0])
                        * int(side_dim[1] / second_carton[1])
                        * int(side_dim[2] / second_carton[2])
                    )

                    if (
                        second_side_qty > 0
                    ):  # if any quantity packed into the second side must check for intrusions
                        for s in [i for i in side_order if i != first_side and i != second_side]:
                            intrusion = second_carton[s] * int(side_dim[s] / second_carton[s])
                            if shipper[s] - intrusion < side_remaining[s]:
                                side_dims[s][second_side] = (
                                    shipper[second_side] - side_remaining[second_side]
                                )

                    # calculate qty that fits into third side, using third carton
                    side_dim = side_dims[third_side]
                    third_side_qty = (
                        int(side_dim[0] / third_carton[0])
                        * int(side_dim[1] / third_carton[1])
                        * int(side_dim[2] / third_carton[2])
                    )

                    # add side quantities to main quantity and check against current max
                    if main_qty + first_side_qty + second_side_qty + third_side_qty > max_qty:
                        max_qty = main_qty + first_side_qty + second_side_qty + third_side_qty

    return max_qty


def comingle_tester(cartons, shipper, attempts=1000, scale=100, random_seed=0):
    """Find a geometric arrangement using a repeatable heuristic.

    False means no arrangement was found, not proof of impossibility. Rounding
    is conservative: cartons round up, shipper dimensions down at 1/scale units.
    There is no weight model in this geometry-only helper.
    """
    dims = dimensions(shipper[1:4], "shipper")
    attempts = integer(attempts, "attempts", minimum=1)
    scale = integer(scale, "scale", minimum=1)
    cartons = [(c[0], *dimensions(c[1:4], str(c[0])), integer(c[4], "quantity")) for c in cartons]
    cartons = [c for c in cartons if c[4]]
    if not cartons:
        return True
    volume = math.prod(dims)
    if sum(math.prod(c[1:4]) * c[4] for c in cartons) > volume + 1e-9:
        return False
    if any(any(a > b + 1e-10 for a, b in zip(sorted(c[1:4]), sorted(dims))) for c in cartons):
        return False
    if sum(c[4] for c in cartons) == 1:
        return True
    rng = random.Random(random_seed)

    def scaled(value, rounding):
        return int((Decimal(str(value)) * scale).to_integral_value(rounding=rounding))

    bin_dims = tuple(scaled(v, ROUND_FLOOR) for v in dims)
    specs = [
        (c[0], sorted(set(it.permutations(tuple(scaled(v, ROUND_CEILING) for v in c[1:4])))), c[4])
        for c in cartons
    ]
    quantity = sum(c[4] for c in cartons)
    for _ in range(attempts):
        shuffled = list(specs)
        rng.shuffle(shuffled)
        for bigger_first in (True, False):
            packer = Packer()
            packer.add_bin(Bin(shipper[0], *bin_dims, 0))
            for cid, orientations, qty in shuffled:
                for i in range(qty):
                    packer.add_item(Item(f"{cid}:{i}", *rng.choice(orientations), 0))
            packer.pack(bigger_first=bigger_first, number_of_decimals=0)
            if len(packer.bins[0].items) == quantity:
                return True
    return False


def _candidate_combinations(bases, volumes, volume, max_units, vectors):
    """Enumerate only the narrow capacity-score band, pruning bounds early."""
    n = len(bases)
    for vector in sorted(set(tuple(v) for v in vectors)):
        active = [i for i, v in enumerate(vector) if v and bases[i] > 0]
        if not active:
            continue
        low = min((bases[i] - 1) / bases[i] for i in active)
        high = min((bases[i] + 1) / bases[i] for i in active)
        counts = [0] * n

        def walk(pos, score, used_volume, units):
            i = active[pos]
            rest = active[pos + 1 :]
            rest_score = sum(1 / bases[j] for j in rest)
            rest_volume = sum(volumes[j] for j in rest)
            upper = min(
                bases[i],
                math.floor((high - score - rest_score + 1e-10) * bases[i]),
                math.floor((volume - used_volume - rest_volume + 1e-9) / volumes[i]),
                max_units - units - len(rest),
            )
            lower = 1
            if not rest:
                lower = max(1, math.floor((low - score + 1e-10) * bases[i]) + 1)
            for qty in range(lower, upper + 1):
                value = score + qty / bases[i]
                if value + rest_score >= high - 1e-10:
                    break
                counts[i] = qty
                if rest:
                    yield from walk(pos + 1, value, used_volume + qty * volumes[i], units + qty)
                elif value > low + 1e-10:
                    yield tuple(counts), value
            counts[i] = 0

        yield from walk(0, 0.0, 0.0, 0)


def comingle_frontier_points(
    shipper,
    cartons,
    vectors,
    shipper_constrained_by_max_units=False,
    simple_frontier_max_fit_threshold=10,
    packings_per_shipper_cap=100,
    random_seed=0,
):
    """Return candidate capacity frontiers, using interpolation at high capacity.

    If any active carton has single-type capacity >= threshold, use the normalized
    capacity band instead of a 3D search. None requests geometric checks throughout.
    Positive dimensions, individual fit, total volume and enabled unit limits apply
    in both modes. Four-quadrant capacities and the frontier are heuristics.
    """
    dims = dimensions(shipper[1:4], "shipper")
    if simple_frontier_max_fit_threshold is not None:
        simple_frontier_max_fit_threshold = integer(
            simple_frontier_max_fit_threshold, "threshold", minimum=1
        )
    if packings_per_shipper_cap is not None:
        packings_per_shipper_cap = integer(packings_per_shipper_cap, "packing cap", minimum=1)
    if any(len(v) != len(cartons) or any(x not in (0, 1) for x in v) for v in vectors):
        raise ValueError("Presence vectors must be binary and match the carton order.")
    old = list(cartons)
    for c in old:
        dimensions(c[1:4], str(c[0]))
        integer(c[4], "max_fit")
    indices = [
        i
        for i, c in enumerate(old)
        if c[4] > 0 and all(a <= b + 1e-10 for a, b in zip(sorted(c[1:4]), sorted(dims)))
    ]
    cartons = [old[i] for i in indices]
    if not cartons:
        return []
    vectors = [tuple(v[i] for i in indices) for v in vectors]
    # Always allow underfilled single-type shippers, including split mixed orders.
    vectors += [tuple(int(i == j) for i in range(len(cartons))) for j in range(len(cartons))]
    bases = [c[4] for c in cartons]
    volumes = [math.prod(c[1:4]) for c in cartons]
    volume = math.prod(dims)
    max_units = integer(shipper[4], "max_units") if shipper_constrained_by_max_units else sum(bases)
    candidates = list(_candidate_combinations(bases, volumes, volume, max_units, vectors))
    candidates.sort(key=lambda p: (-p[1], p[0]))
    accepted = []
    # Single-type capacities are constructive geometric lower bounds, even when
    # the caller's observed vectors contain only multi-type orders.
    for i, base in enumerate(bases):
        qty = min(base, max_units, math.floor((volume + 1e-9) / volumes[i]))
        if qty:
            accepted.append(tuple(qty if j == i else 0 for j in range(len(bases))))
    for combo, _ in candidates:
        if any(all(x <= y for x, y in zip(combo, p)) for p in accepted):
            continue
        active = [i for i, x in enumerate(combo) if x]
        interpolate = simple_frontier_max_fit_threshold is not None and any(
            bases[i] >= simple_frontier_max_fit_threshold for i in active
        )
        if not interpolate:
            specs = [(cartons[i][0], *cartons[i][1:4], combo[i]) for i in active]
            if not comingle_tester(
                specs, (shipper[0], *dims, volume), attempts=150, random_seed=random_seed
            ):
                continue
        # Descending positive score means later candidates cannot dominate accepted
        # candidates. No quadratic final all-pairs frontier pass is necessary.
        accepted.append(combo)
    results = [dict(zip([c[0] for c in cartons], p)) for p in accepted]
    if packings_per_shipper_cap is not None:
        results = _select_spread_packings(
            results,
            [c[0] for c in cartons],
            dict(zip([c[0] for c in cartons], bases)),
            packings_per_shipper_cap,
        )
    return results


def generate_max_fits_dict(shippers, cartons, shipper_constrained_by_max_units=False):
    """Map (shipper ID, carton ID) to four-quadrant capacity, optionally unit-capped."""
    result = {}
    for sid, sv in shippers.items():
        for cid, cv in cartons.items():
            value = max_cartons_four_quadrant(sv[:3], cv[:3])
            if shipper_constrained_by_max_units:
                value = min(value, integer(sv[3], f"{sid}.max_units"))
            result[(sid, cid)] = value
    return result


def _select_spread_packings(count_dicts, carton_list, bases, max_per_shipper):
    """Farthest-first selection with incremental nearest distances: O(N*K*D).

    Retains the existing tie order and all single-type maxima, so the cap is soft
    when there are more single-type maxima than the configured cap.
    """
    max_per_shipper = integer(max_per_shipper, "packing cap", minimum=1)
    unique = {}
    for counts in count_dicts:
        unique.setdefault(tuple(counts.get(cid, 0) for cid in carton_list), counts)
    count_dicts = list(unique.values())
    if len(count_dicts) <= max_per_shipper:
        return count_dicts
    singles, remaining = [], []
    for counts in count_dicts:
        nz = [cid for cid in carton_list if counts.get(cid, 0)]
        target = singles if len(nz) == 1 and counts[nz[0]] == bases.get(nz[0], 0) else remaining
        target.append(counts)
    if len(singles) >= max_per_shipper:
        return singles

    def vec(counts):
        return [counts.get(cid, 0) / (bases.get(cid, 0) or 1) for cid in carton_list]

    def distance(a, b):
        return sum(abs(x - y) for x, y in zip(a, b))

    vectors = [vec(c) for c in remaining]
    kept = list(singles)
    if kept:
        nearest = [min(distance(v, vec(s)) for s in kept) for v in vectors]
    elif remaining:
        centroid = [sum(v[j] for v in vectors) / len(vectors) for j in range(len(carton_list))]
        first = max(range(len(vectors)), key=lambda i: distance(vectors[i], centroid))
        kept.append(remaining.pop(first))
        seed = vectors.pop(first)
        nearest = [distance(v, seed) for v in vectors]
    else:
        return kept
    while remaining and len(kept) < max_per_shipper:
        i = max(range(len(nearest)), key=nearest.__getitem__)
        kept.append(remaining.pop(i))
        selected = vectors.pop(i)
        nearest.pop(i)
        nearest = [min(old, distance(v, selected)) for old, v in zip(nearest, vectors)]
    return kept


def generate_packings(
    shippers,
    cartons,
    carton_list,
    max_fits,
    vectors,
    shipper_constrained_by_max_units=False,
    simple_frontier_max_fit_threshold=10,
    packings_per_shipper_cap=100,
    random_seed=0,
):
    """Build packing capacities with 'four_quadrant', 'interpolated', or '3d_checked' provenance."""
    missing = [c for c in carton_list if c not in cartons]
    if missing:
        raise ValueError(f"Missing carton dimensions: {missing}")
    packings = []
    for sid, sv in shippers.items():
        cs = tuple((cid, *cartons[cid], max_fits.get((sid, cid), 0)) for cid in carton_list)
        points = comingle_frontier_points(
            (sid, sv["length"], sv["width"], sv["height"], sv["max_units"], sv["volume"]),
            cs,
            vectors,
            shipper_constrained_by_max_units,
            simple_frontier_max_fit_threshold,
            packings_per_shipper_cap,
            random_seed,
        )
        for i, point in enumerate(points):
            counts = {cid: int(point.get(cid, 0)) for cid in carton_list}
            nz = [cid for cid in carton_list if counts[cid]]
            method = (
                "four_quadrant"
                if len(nz) == 1
                else (
                    "interpolated"
                    if simple_frontier_max_fit_threshold is not None
                    and any(max_fits[(sid, cid)] >= simple_frontier_max_fit_threshold for cid in nz)
                    else "3d_checked"
                )
            )
            packings.append(
                {
                    "packing_id": f"{sid}:{i:04d}",
                    "shipper_id": sid,
                    "counts": counts,
                    "fit_method": method,
                }
            )
    return packings
