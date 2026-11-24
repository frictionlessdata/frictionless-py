"""XML Schema's partial order for duration bounds."""

from __future__ import annotations

import calendar
import datetime
from typing import Any, Optional, Tuple

from ..platform import platform

# https://www.w3.org/TR/xmlschema-2/#duration-order
REFERENCE_MONTHS = ((1696, 9), (1697, 2), (1903, 3), (1903, 7))
MONTH_STARTS = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)
MICROSECONDS_PER_DAY = 86400 * 1000000


def compare_duration(left: Any, right: Any) -> Optional[int]:
    """Return -1, 0, 1, or None when durations have no determinate order."""
    left_parts = _components(left)
    right_parts = _components(right)
    if left_parts is None or right_parts is None:
        return None
    if left_parts == right_parts:
        return 0

    relations: set[int] = set()
    for year, month in REFERENCE_MONTHS:
        left_value = _project(left_parts, year, month)
        right_value = _project(right_parts, year, month)
        relations.add((left_value > right_value) - (left_value < right_value))
    # Equal at one reference and ordered at another is also indeterminate.
    return relations.pop() if len(relations) == 1 else None


def _components(value: Any) -> Optional[Tuple[int, int]]:
    months = 0
    if isinstance(value, platform.isodate.Duration):
        # XML Schema permits fractional seconds, but not fractional years/months.
        years, months = int(value.years), int(value.months)
        if years != value.years or months != value.months:
            return None
        months += years * 12
        value = value.tdelta
    if not isinstance(value, datetime.timedelta):
        return None
    microseconds = (
        value.days * MICROSECONDS_PER_DAY + value.seconds * 1000000 + value.microseconds
    )
    return months, microseconds


def _project(parts: Tuple[int, int], year: int, month: int) -> int:
    months, microseconds = parts
    year, month = divmod(year * 12 + month - 1 + months, 12)
    # Reference days are all the first of a month. Use the proleptic Gregorian
    # ordinal directly so long/negative durations do not overflow datetime.
    previous_year = year - 1
    days = (
        365 * previous_year
        + previous_year // 4
        - previous_year // 100
        + previous_year // 400
        + MONTH_STARTS[month]
        + (month >= 2 and calendar.isleap(year))
    )
    return days * MICROSECONDS_PER_DAY + microseconds
