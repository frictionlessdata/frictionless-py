from __future__ import annotations
import attrs
from collections import namedtuple
from ..schema import Field


@attrs.define(kw_only=True)
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
        def value_reader(cell):
            if isinstance(cell, (tuple, list)):
                if len(cell) != 2:
                    return None
                cell = yearmonth(cell[0], cell[1])
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
        def value_writer(cell):
            return f"{cell.year}-{cell.month:02}"

        return value_writer


# Internal

yearmonth = namedtuple("yearmonth", ["year", "month"])
