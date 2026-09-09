from cartonization.packing import generate_max_fits_dict, max_cartons_four_quadrant


def test_max_cartons_four_quadrant_simple():
    assert max_cartons_four_quadrant((10, 10, 10), (5, 5, 5)) == 8


def test_generate_max_fits_dict():
    shippers = {"S1": [10, 10, 10, 999]}
    cartons = {"C1": [5, 5, 5]}
    max_fits = generate_max_fits_dict(
        shippers=shippers, cartons=cartons, shipper_constrained_by_max_units=False
    )
    assert max_fits[("S1", "C1")] == 8
