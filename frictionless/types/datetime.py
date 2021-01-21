from datetime import datetime
from dateutil import parser
from ..type import Type
from .. import config


class DatetimeType(Type):
    """Datetime type implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import types`

    """

    code = "datetime"
    constraints = [
        "required",
        "minimum",
        "maximum",
        "enum",
    ]

    # Read

    def read_cell(self, cell):
        if not isinstance(cell, datetime):
            if not isinstance(cell, str):
                return None
            try:
                if self.field.format == "default":
                    # Guard against shorter formats supported by dateutil
                    assert cell[16] == ":"
                    assert len(cell) >= 19
                    cell = parser.isoparse(cell)
                elif self.field.format == "any":
                    cell = parser.parse(cell)
                else:
                    cell = datetime.strptime(cell, self.field.format)
            except Exception:
                return None
        return cell

    # Write

    def write_cell(self, cell):
        format = self.field.get("format", config.DEFAULT_DATETIME_PATTERN)
        cell = cell.strftime(format)
        cell = cell.replace("+0000", "Z")
        return cell
