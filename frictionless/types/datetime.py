from datetime import datetime
from dateutil.parser import parse
from ..type import Type
from .. import config


class DatetimeType(Type):
    """Datetime type implementation.

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
        if not isinstance(cell, datetime):
            if not isinstance(cell, str):
                return None
            try:
                if self.field.format == "default":
                    pattern = config.DEFAULT_DATETIME_PATTERN
                    if len(cell) >= 20:
                        pattern = config.DEFAULT_DATETIME_PATTERN_WITH_TIMEZONE
                    cell = datetime.strptime(cell, pattern)
                elif self.field.format == "any":
                    cell = parse(cell)
                else:
                    cell = datetime.strptime(cell, self.field.format)
            except Exception:
                return None
        return cell

    # Write

    def write_cell(self, cell):
        format = self.field.get("format", config.DEFAULT_DATETIME_PATTERN_WITH_TIMEZONE)
        cell = cell.strftime(format)
        cell = cell.replace("+0000", "Z")
        return cell
