"""Scenario orchestration with explicit objectives, coverage and solver diagnostics."""

from __future__ import annotations

import math
import random
import warnings
from collections import Counter
from dataclasses import dataclass, field

from .packing import generate_max_fits_dict, generate_packings
from .solver import solve_min_integer, upper_bounds_for_solve_min_integer
from .validation import AnalysisError, dimensions, identifiers, integer, number


@dataclass
class ScenarioResult:
    """Observed totals over the included demand; never silently extrapolated."""

    name: str
    total_cost: float
    total_count: dict[str, int]
    packing_efficiency: float
    packings: list[dict]
    max_fits: dict[tuple[str, str], int]
    shipment_profiles: list[dict]
    coverage: dict
    settings: dict
    profiles: list[dict] = field(default_factory=list)
    shippers: dict = field(default_factory=dict)
    cartons: dict = field(default_factory=dict)
    provenance: dict = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self):
        from dataclasses import asdict

        result = asdict(self)
        result["max_fits"] = [
            {"shipper_id": sid, "carton_id": cid, "capacity": v}
            for (sid, cid), v in self.max_fits.items()
        ]
        return result


def _solve_profiles(
    shipment_profiles,
    shippers,
    carton_list,
    packings,
    solver_time_limit=60,
    objective="volume_penalty",
    progress=None,
):
    if objective not in ("volume_penalty", "shipping_cost"):
        raise ValueError("objective must be 'volume_penalty' or 'shipping_cost'.")
    if not packings:
        raise AnalysisError("No packings were generated for the selected demand.")
    carton_list = identifiers(carton_list, "carton_list")
    for sid, s in shippers.items():
        number(s["volume"], f"{sid}.volume", positive=True)
        number(s["cost"], f"{sid}.cost", nonnegative=True)
    ids = [p["shipper_id"] for p in packings]
    if set(ids) - shippers.keys():
        raise ValueError("Packings reference unknown shipper IDs.")
    volumes = [round(shippers[sid]["volume"], 0) for sid in ids]
    maximum = max(volumes)
    c = (
        [shippers[sid]["cost"] for sid in ids]
        if objective == "shipping_cost"
        else [v + maximum for v in volumes]
    )
    a = [
        [integer(p["counts"].get(cid, 0), f"packing {j}: {cid}") for j, p in enumerate(packings)]
        for cid in carton_list
    ]
    total_cost, usage, records = 0.0, dict.fromkeys(shippers, 0), []
    for idx, profile in enumerate(shipment_profiles):
        frequency = integer(profile.get("frequency", 0), f"profile {idx}.frequency")
        counts = profile.get("counts", {})
        unknown = set(counts) - set(carton_list)
        if any(counts[c] for c in unknown):
            raise ValueError(f"Profile {idx} contains unselected carton IDs: {sorted(unknown)}.")
        b = [integer(counts.get(cid, 0), f"profile {idx}.{cid}") for cid in carton_list]
        if not any(b) or not frequency:
            continue
        if progress and (idx == 0 or idx % 25 == 0 or idx + 1 == len(shipment_profiles)):
            progress(f"Solving shipment profile {idx + 1} of {len(shipment_profiles)}")
        try:
            uncovered = [
                cid for cid, demand, row in zip(carton_list, b, a) if demand and not any(row)
            ]
            if uncovered:
                raise RuntimeError(f"No selected shipper can cover cartons: {uncovered}")
            x, obj, status = solve_min_integer(
                b,
                a,
                c,
                upper_bounds=upper_bounds_for_solve_min_integer(b, a),
                time_limit=solver_time_limit,
            )
        except RuntimeError as exc:
            issue = {
                "location": f"shipment profile {idx + 1}",
                "message": str(exc),
                "frequency": frequency,
                "counts": counts,
            }
            raise AnalysisError(
                "Analysis stopped: a shipment profile could not be solved. No final totals were produced.",
                [issue],
            ) from exc
        selections = []
        cost = 0.0
        for j, qty in enumerate(x):
            if qty:
                sid = ids[j]
                cost += qty * shippers[sid]["cost"]
                usage[sid] += frequency * qty
                selections.append(
                    {
                        "packing_id": packings[j].get("packing_id", str(j)),
                        "shipper_id": sid,
                        "quantity": qty,
                        "fit_method": packings[j].get("fit_method", "unspecified"),
                    }
                )
        total_cost += frequency * cost
        records.append(
            {
                "profile": idx + 1,
                "frequency": frequency,
                "counts": dict(zip(carton_list, b)),
                "cost_per_order": cost,
                "status": status,
                "objective_value": obj,
                "selections": selections,
            }
        )
    return total_cost, usage, records


def calculate_cost_count(
    shipment_profiles,
    shippers,
    carton_list,
    packings,
    solver_time_limit=60,
    objective="volume_penalty",
    progress=None,
):
    """Return frequency-weighted observed cost and usage. Unsolved demand raises AnalysisError.

    The default objective is rounded shipper volume plus largest candidate volume.
    Use objective='shipping_cost' to minimize the supplied modeled shipper costs.
    """
    cost, usage, records = _solve_profiles(
        shipment_profiles, shippers, carton_list, packings, solver_time_limit, objective, progress
    )
    if any(r["status"] != "Optimal" for r in records):
        warnings.warn(
            "Some solutions are feasible but not proven optimal; use structured results for per-profile status.",
            RuntimeWarning,
            stacklevel=2,
        )
    return cost, usage


def analyze_loaded(
    profiles,
    cartons,
    shippers,
    *,
    name="Scenario",
    sample_ratio=1.0,
    vector_length_limit=None,
    vector_freq_limit=0,
    random_seed=0,
    objective="volume_penalty",
    threshold=10,
    packing_cap=100,
    constrain_max_units=False,
    solver_time_limit=60,
    progress=None,
):
    """Analyze in-memory inputs and return structured observed results."""
    if not profiles:
        raise ValueError("No positive-frequency demand for the selected cartons.")
    carton_list = identifiers(list(cartons), "cartons")
    identifiers(list(shippers), "shippers")
    cartons = {cid: dimensions(d, f"carton {cid}") for cid, d in cartons.items()}
    for sid, shipper in shippers.items():
        dimensions([shipper["length"], shipper["width"], shipper["height"]], f"shipper {sid}")
        integer(shipper["max_units"], f"{sid}.max_units")
        number(shipper["cost"], f"{sid}.cost", nonnegative=True)
    ratio = number(sample_ratio, "sample_ratio", positive=True)
    if ratio > 1:
        raise ValueError("sample_ratio must be > 0 and <= 1.")
    limit = (
        len(carton_list)
        if vector_length_limit is None
        else integer(vector_length_limit, "vector_length_limit", minimum=1)
    )
    freq_limit = integer(vector_freq_limit, "vector_freq_limit")
    seed = integer(random_seed, "random_seed")
    if solver_time_limit is not None:
        integer(solver_time_limit, "solver_time_limit", minimum=1)
    if threshold is not None:
        integer(threshold, "threshold", minimum=1)
    if packing_cap is not None:
        integer(packing_cap, "packing_cap", minimum=1)
    # Validate before sampling, including profiles that a preview may exclude.
    normalized = Counter()
    for i, p in enumerate(profiles):
        frequency = integer(p.get("frequency", 0), f"profile {i}.frequency")
        if any(v for cid, v in p["counts"].items() if cid not in cartons):
            raise ValueError(f"Profile {i} contains unselected cartons.")
        counts = tuple(
            integer(p["counts"].get(cid, 0), f"profile {i}.{cid}") for cid in carton_list
        )
        if frequency and any(counts):
            normalized[counts] += frequency
    all_profiles = [
        {"frequency": f, "counts": dict(zip(carton_list, counts))}
        for counts, f in sorted(normalized.items())
    ]
    if not all_profiles:
        raise ValueError("No positive-frequency demand for the selected cartons.")
    total_frequency = sum(p["frequency"] for p in all_profiles)
    selected = all_profiles
    if ratio < 1:
        rng = random.Random(seed)
        # Weighted random permutation via exponential keys. Deterministic input
        # order and no zero-frequency probabilities.
        order = sorted(
            all_profiles, key=lambda p: -math.log(max(rng.random(), 1e-300)) / p["frequency"]
        )
        selected, covered = [], 0
        for p in order:
            selected.append(p)
            covered += p["frequency"]
            if covered >= ratio * total_frequency:
                break
        selected.sort(key=lambda p: tuple(p["counts"].values()))
    sampled_frequency = sum(p["frequency"] for p in selected)

    def vector(p):
        return tuple(int(p["counts"][cid] > 0) for cid in carton_list)

    vector_frequencies = Counter()
    for p in selected:
        vector_frequencies[vector(p)] += p["frequency"]
    vectors = sorted(
        v for v, f in vector_frequencies.items() if sum(v) <= limit and f >= freq_limit
    )
    allowed = set(vectors)
    selected = [p for p in selected if vector(p) in allowed]
    if not selected:
        raise ValueError("No demand remains after the configured vector filters.")
    included = sum(p["frequency"] for p in selected)
    if progress:
        progress(f"Generating packing capacities for {len(shippers)} shippers")
    max_fits = generate_max_fits_dict(
        {
            sid: [s["length"], s["width"], s["height"], s["max_units"]]
            for sid, s in shippers.items()
        },
        cartons,
        constrain_max_units,
    )
    packings = generate_packings(
        shippers,
        cartons,
        carton_list,
        max_fits,
        vectors,
        constrain_max_units,
        threshold,
        packing_cap,
        seed,
    )
    cost, usage, records = _solve_profiles(
        selected, shippers, carton_list, packings, solver_time_limit, objective, progress
    )
    carton_volume = sum(
        p["frequency"] * sum(qty * math.prod(cartons[cid]) for cid, qty in p["counts"].items())
        for p in selected
    )
    shipper_volume = sum(qty * shippers[sid]["volume"] for sid, qty in usage.items())
    efficiency = 100 * carton_volume / shipper_volume if shipper_volume else 0.0
    if efficiency > 100 + 1e-7:
        raise AnalysisError(
            "Packing efficiency exceeds 100%; check packing capacities and dimensions."
        )
    notes = []
    if included < total_frequency:
        notes.append("Observed totals cover a subset of demand; they have not been extrapolated.")
    if any(r["status"] != "Optimal" for r in records):
        notes.append("Some integer solutions are feasible but not proven optimal.")
    return ScenarioResult(
        name,
        cost,
        usage,
        efficiency,
        packings,
        max_fits,
        selected,
        {
            "total_frequency": total_frequency,
            "sampled_frequency": sampled_frequency,
            "included_frequency": included,
            "excluded_frequency": total_frequency - included,
            "included_fraction": included / total_frequency,
            "total_profiles": len(all_profiles),
            "included_profiles": len(selected),
            "carton_volume": carton_volume,
            "shipper_volume": shipper_volume,
        },
        {
            "objective": objective,
            "random_seed": seed,
            "sample_ratio": ratio,
            "vector_length_limit": limit,
            "vector_freq_limit": freq_limit,
            "fit_mode": "geometric" if threshold is None else "capacity_interpolation",
            "interpolation_threshold": threshold,
            "packing_cap": packing_cap,
            "constrain_max_units": constrain_max_units,
            "solver_time_limit": solver_time_limit,
        },
        records,
        shippers,
        cartons,
        warnings=notes,
    )
