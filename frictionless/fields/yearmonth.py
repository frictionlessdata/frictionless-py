from __future__ import annotations

from typing import Any, NamedTuple

import attrs

from ..schema import Field


@attrs.define(kw_only=True, repr=False)
class YearmonthField(Field):
    type = "yearmonth"
    builtin = True
    supported_constraints = [
        "required",
        "minimum",
        "maximum",
        "enum",
    ]

    # Read

    def create_value_reader(self):
        # Create reader
        def value_reader(cell: Any):
            if isinstance(cell, (tuple, list)):
                if len(cell) != 2:  # type: ignore
                    return None
                cell = yearmonth(year=cell[0], month=cell[1])  # type: ignore
            elif isinstance(cell, str):
                try:
                    year, month = cell.split("-")
                    year = int(year)
                    month = int(month)
                    if month < 1 or month > 12:
                        return None
                    cell = yearmonth(year, month)
                except Exception:
                    return None
            else:
                return None
            return cell

        return value_reader

    # Write

    def create_value_writer(self):
        # Create writer
        def value_writer(cell: Any):
            return f"{cell.year}-{cell.month:02}"

        return value_writer


# Internal


class yearmonth(NamedTuple):
    year: int
    month: int
