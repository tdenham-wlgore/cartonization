"""Repeatable focused timing of packing selection; does not run benchmarks in CI."""

import json
import random
from argparse import ArgumentParser
from pathlib import Path
from statistics import median
from time import perf_counter

from cartonization.packing import _select_spread_packings


def reference_select(points, columns, bases, cap):
    """Pre-0.2 farthest-first distance recomputation for benchmark comparison."""
    remaining = list(points)

    def vec(p):
        return [p[c] / bases[c] for c in columns]

    def distance(a, b):
        return sum(abs(x - y) for x, y in zip(a, b))

    vectors = [vec(p) for p in remaining]
    center = [sum(v[j] for v in vectors) / len(vectors) for j in range(len(columns))]
    first = max(range(len(vectors)), key=lambda i: distance(vectors[i], center))
    selected = [remaining.pop(first)]
    kept_vectors = [vectors.pop(first)]
    while remaining and len(selected) < cap:
        i = max(
            range(len(vectors)), key=lambda i: min(distance(vectors[i], v) for v in kept_vectors)
        )
        selected.append(remaining.pop(i))
        kept_vectors.append(vectors.pop(i))
    return selected


def main():
    parser = ArgumentParser()
    parser.add_argument("--candidates", type=int, default=1000)
    parser.add_argument("--cap", type=int, default=50)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if min(args.candidates, args.cap, args.repeat) < 1:
        parser.error("All benchmark sizes must be positive.")
    rng = random.Random(42)
    columns = list("ABCDEF")
    bases = {c: 100 for c in columns}
    unique = set()
    while len(unique) < args.candidates:
        unique.add(tuple(rng.randint(1, 99) for _ in columns))
    points = [dict(zip(columns, p)) for p in sorted(unique)]
    timings = {}
    outputs = {}
    for name, fn in [
        ("original_distance_scan", reference_select),
        ("incremental_distances", _select_spread_packings),
    ]:
        elapsed = []
        for _ in range(args.repeat):
            start = perf_counter()
            outputs[name] = fn(points, columns, bases, args.cap)
            elapsed.append(perf_counter() - start)
        timings[name] = median(elapsed)
    same = outputs["original_distance_scan"] == outputs["incremental_distances"]
    if not same:
        raise AssertionError("Selection changed between algorithms.")
    result = {
        "candidates": args.candidates,
        "cap": args.cap,
        "repeat": args.repeat,
        "identical_selection": same,
        "median_seconds": timings,
        "speedup": timings["original_distance_scan"] / timings["incremental_distances"],
    }
    print(json.dumps(result, indent=2))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
