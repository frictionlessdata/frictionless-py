from datetime import datetime, time
from dateutil import parser
from ..type import Type
from .. import config


class TimeType(Type):
    """Time type implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import types`

    """

    supported_constraints = [
        "required",
        "minimum",
        "maximum",
        "enum",
    ]

    # Read

    def read_cell(self, cell):
        if not isinstance(cell, time):
            if not isinstance(cell, str):
                return None
            try:
                if self.field.format == "default":
                    # Guard against shorter formats supported by dateutil
                    assert cell[5] == ":"
                    assert len(cell) >= 8
                    cell = parser.isoparse(f"2000-01-01T{cell}").timetz()
                elif self.field.format == "any":
                    cell = parser.parse(cell).timetz()
                else:
                    cell = datetime.strptime(cell, self.field.format).timetz()
            except Exception:
                return None
        return cell

    # Write

    def write_cell(self, cell):
        format = self.field.get("format", config.DEFAULT_TIME_PATTERN)
        cell = cell.strftime(format)
        cell = cell.replace("+0000", "Z")
        return cell
