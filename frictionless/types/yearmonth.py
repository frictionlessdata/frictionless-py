from collections import namedtuple
from ..type import Type


class YearmonthType(Type):
    """Yearmonth type implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import types`

    """

    code = "yearmonth"
    builtin = True
    constraints = [
        "required",
        "minimum",
        "maximum",
        "enum",
    ]

    # Read

    def read_cell(self, cell):
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

    # Write

    def write_cell(self, cell):
        return f"{cell.year}-{cell.month:02}"


# Internal

yearmonth = namedtuple("yearmonth", ["year", "month"])
