"""Shared validation and actionable, serializable issue reports."""

from __future__ import annotations

import math
from decimal import Decimal, InvalidOperation


class InputError(ValueError):
    """Invalid input, with locations suitable for a spreadsheet issue report."""

    def __init__(self, message: str, issues: list[dict] | None = None):
        self.issues = issues or [{"location": "input", "message": message}]
        super().__init__(message)


class AnalysisError(RuntimeError):
    """An analysis could not account for all selected demand."""

    def __init__(self, message: str, issues: list[dict] | None = None):
        self.issues = issues or [{"location": "analysis", "message": message}]
        super().__init__(message)


def invalid(location: str, message: str) -> InputError:
    return InputError(f"{location}: {message}", [{"location": location, "message": message}])


def number(value, location: str, *, positive=False, nonnegative=False) -> float:
    try:
        if isinstance(value, bool):
            raise ValueError
        result = float(value)
        if not math.isfinite(result):
            raise ValueError
    except (ValueError, TypeError, OverflowError) as exc:
        raise invalid(location, "Expected a finite number.") from exc
    if (positive and result <= 0) or (nonnegative and result < 0):
        raise invalid(
            location, "Expected a positive number." if positive else "Expected zero or more."
        )
    return result


def integer(value, location: str, *, minimum=0, blank_zero=False) -> int:
    if blank_zero and (value is None or value == ""):
        return 0
    try:
        if isinstance(value, bool):
            raise ValueError
        result = Decimal(str(value))
        if not result.is_finite() or result != result.to_integral_value() or result < minimum:
            raise ValueError
        return int(result)
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise invalid(
            location, f"Expected a whole number >= {minimum}; received {value!r}."
        ) from exc


def identifier(value, location: str) -> str:
    if value is None or isinstance(value, bool):
        raise invalid(location, "An identifier is required.")
    if isinstance(value, (float, int)):
        value = str(integer(value, location))
    result = str(value).strip()
    if not result:
        raise invalid(location, "An identifier is required.")
    return result


def identifiers(values, location: str) -> list[str]:
    if not isinstance(values, (list, tuple)) or not values:
        raise invalid(location, "Provide a nonempty list of identifiers.")
    result = [identifier(v, location) for v in values]
    if len(set(result)) != len(result):
        raise invalid(location, "Duplicate identifiers are not allowed.")
    return result


def dimensions(values, location="dimensions") -> tuple[float, float, float]:
    if len(values) != 3:
        raise invalid(location, "Exactly three dimensions are required.")
    return tuple(number(v, location, positive=True) for v in values)
