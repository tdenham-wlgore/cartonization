# -*- coding: utf-8 -*-
"""Run the bundled practice scenario and export a report through the package API."""

from __future__ import annotations

from pathlib import Path
from tempfile import mkdtemp

from cartonization import export_report, run_scenario
from cartonization.workflows import load_config


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    config, base_dir = load_config(repo_root / "examples" / "scenario.json")
    result = run_scenario(config, base_dir=base_dir, progress=print)

    output_root = repo_root / "outputs"
    output_root.mkdir(exist_ok=True)
    output_dir = Path(mkdtemp(prefix="python-example-", dir=output_root))
    export_report([result], output_dir)

    print(f"Scenario: {result.name}")
    print(f"Modeled shipping cost: ${result.total_cost:,.2f}")
    print(f"Included orders: {result.coverage['included_frequency']:,}")
    print(f"Total shippers: {sum(result.total_count.values()):,}")
    print(f"Packing efficiency: {result.packing_efficiency:.1f}%")
    print("Shipper usage:")
    for shipper, count in result.total_count.items():
        print(f"  {shipper}: {count:,}")
    print(f"Report: {output_dir / 'report.xlsx'}")


if __name__ == "__main__":
    main()
