# -*- coding: utf-8 -*-
"""End-to-end example of running a cartonization scenario analysis."""

from __future__ import annotations

from pathlib import Path

from cartonization.analysis import scenario_analysis
from cartonization.costs import shipping_cost_zone4


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    data_dir = repo_root / "data"

    total_cost, total_count, packing_efficiency, packings, max_fits, shipment_profiles = (
        scenario_analysis(
            history_file=str(data_dir / "shipment_history_test_data.xlsx"),
            history_file_sheet_name="Sheet1",
            history_file_fre_col="FREQUENCY",
            history_sample_ratio=1.0,
            vector_length_limit=4,
            vector_freq_limit=0,
            ref_file=str(data_dir / "reference_test_data.xlsx"),
            dim_cols=["LENGTH", "WIDTH", "HEIGHT"],
            ref_file_shipper_sheet="container_shipper_dims",
            ref_file_shipper_id_col="SHIPPER",
            ref_file_shipper_max_col="MAXUNITS",
            ref_file_carton_sheet="container_carton_dims",
            ref_file_carton_id_col="CARTON",
            carton_list=["C24", "C99", "C32", "C21", "C16", "C13"],
            shipper_list=[
                "S157G01",
                "S858G01",
                "S916G01",
                "NCG2002",
                "NCG2003",
                "NCG2005",
                "NCG2006",
                "NCG2007",
            ],
            shipping_cost_function=shipping_cost_zone4,
            shipper_fixed_cost=2.0,
            shipper_constrained_by_max_units=False,
            simple_frontier_max_fit_threshold=13,
        )
    )

    print(f"Total cost for scenario is ${round(total_cost, 0)}")
    print(f"Total shipper count is {sum(total_count.values())}")
    print(f"Packing efficiency is {packing_efficiency}%")
    print("Shipper\tCount\n" + "\n".join(f"{k}\t{v}" for k, v in total_count.items()))


if __name__ == "__main__":
    main()


# Version 0.2.0 correctness fixes can change the historical allocations.
# Use examples/comparison.json for a small hand-calculated acceptance example:
# $144 baseline and $120 after adding the small shipper.
# See docs/VERIFICATION.md for the full-history configuration and measured output.
