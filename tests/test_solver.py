import pytest

from cartonization.solver import solve_min_integer, upper_bounds_for_solve_min_integer


def test_upper_bounds_for_solve_min_integer():
    a = [[1, 2], [3, 0]]
    b = [4, 5]
    assert list(upper_bounds_for_solve_min_integer(b=b, a=a)) == [4, 2]


def test_solve_min_integer_simple():
    try:
        import pulp as pl
    except ImportError:
        pytest.skip("pulp not installed")

    if not pl.PULP_CBC_CMD(msg=False).available():
        pytest.skip("CBC solver not available")

    a = [[1, 0], [0, 1]]
    b = [1, 2]
    c = [1, 1]
    upper = upper_bounds_for_solve_min_integer(b=b, a=a)
    x, obj, status = solve_min_integer(b=b, a=a, c=c, upper_bounds=upper)

    assert status == "Optimal"
    assert x == [1, 2]
    assert obj == 3.0
