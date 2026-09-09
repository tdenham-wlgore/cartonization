"""Integer covering optimization with validated incumbent solutions."""

from __future__ import annotations

import math

import pulp as pl

from .validation import integer, number


def solve_min_integer(b, a, c, min_val=0, upper_bounds=None, time_limit=None, solver_name="cbc"):
    """Minimize c^T x subject to a x >= b, with nonnegative integer x.

    Returns (integer values, recomputed objective, status). An integer incumbent
    may be returned after a time limit as 'Feasible (not proven optimal)'.
    Infeasible, unbounded, fractional or bound-violating results raise RuntimeError.
    CBC is bundled with the pinned PuLP dependency. GLPK is an optional external solver.
    """
    min_val = integer(min_val, "min_val")
    if len(b) == 0 or len(c) == 0 or len(a) != len(b) or any(len(r) != len(c) for r in a):
        raise ValueError("a must be a nonempty rectangular len(b) x len(c) matrix.")
    b = [number(v, "b") for v in b]
    a = [[number(v, "a") for v in row] for row in a]
    c = [number(v, "c") for v in c]
    n = len(c)
    if upper_bounds is not None and len(upper_bounds) != n:
        raise ValueError("upper_bounds must have length len(c).")
    bounds = (
        [None] * n
        if upper_bounds is None
        else [None if v is None else number(v, "upper_bounds") for v in upper_bounds]
    )
    if any(v is not None and v < min_val for v in bounds):
        raise ValueError("Each upper bound must be >= min_val.")
    if time_limit is not None:
        time_limit = integer(time_limit, "time_limit", minimum=1)
    if any(c[j] < 0 and bounds[j] is None and all(row[j] >= 0 for row in a) for j in range(n)):
        raise ValueError(
            "Negative objective with unbounded nonnegative column; provide upper bounds."
        )
    if solver_name.lower() == "cbc":
        solver = pl.PULP_CBC_CMD(msg=False, timeLimit=time_limit, threads=1)
    elif solver_name.lower() == "glpk":
        solver = pl.GLPK_CMD(msg=False, options=["--tmlim", str(time_limit)] if time_limit else [])
    else:
        raise ValueError("solver_name must be 'cbc' or 'glpk'.")
    if not solver.available():
        raise RuntimeError(
            f"Solver {solver_name!r} is unavailable. Run python -m cartonization doctor."
        )
    prob = pl.LpProblem("MinInteger", pl.LpMinimize)
    variables = [
        pl.LpVariable(f"x{j}", lowBound=min_val, upBound=bounds[j], cat=pl.LpInteger)
        for j in range(n)
    ]
    prob += pl.lpDot(c, variables)
    for row, rhs in zip(a, b):
        prob += pl.lpDot(row, variables) >= rhs
    try:
        prob.solve(solver)
    except pl.PulpSolverError as exc:
        raise RuntimeError(f"{solver_name} failed to run: {exc}") from exc
    status = pl.LpStatus[prob.status]
    if prob.status in (pl.LpStatusInfeasible, pl.LpStatusUnbounded, pl.LpStatusUndefined):
        raise RuntimeError(f"Solver finished with status: {status}.")
    raw = [v.value() for v in variables]
    # A variable unused in both constraints and the objective is irrelevant.
    for j, value in enumerate(raw):
        if value is None and c[j] == 0 and all(row[j] == 0 for row in a):
            raw[j] = min_val
    if any(v is None or not math.isfinite(v) or abs(v - round(v)) > 1e-6 for v in raw):
        raise RuntimeError(f"Solver status {status}: no integer feasible solution returned.")
    x = [round(v) for v in raw]
    if any(v < min_val or (ub is not None and v > ub + 1e-7) for v, ub in zip(x, bounds)):
        raise RuntimeError("Returned solution violates variable bounds.")
    if any(sum(v * coef for v, coef in zip(x, row)) + 1e-7 < rhs for row, rhs in zip(a, b)):
        raise RuntimeError("Returned solution violates demand constraints.")
    proven = prob.status == pl.LpStatusOptimal and prob.sol_status == pl.LpSolutionOptimal
    return (
        x,
        float(sum(coef * v for coef, v in zip(c, x))),
        "Optimal" if proven else "Feasible (not proven optimal)",
    )


def upper_bounds_for_solve_min_integer(b, a):
    """Safe column caps for a covering model with nonnegative demand/coefficients."""
    if len(b) == 0 or len(a) != len(b) or not len(a[0]) or any(len(r) != len(a[0]) for r in a):
        raise ValueError("a and b must describe a nonempty rectangular covering model.")
    b = [number(v, "b", nonnegative=True) for v in b]
    a = [[number(v, "a", nonnegative=True) for v in row] for row in a]
    return [
        max(math.ceil(rhs / row[j]) if row[j] else 0 for rhs, row in zip(b, a))
        for j in range(len(a[0]))
    ]
