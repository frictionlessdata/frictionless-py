from datetime import datetime, date
from dateutil.parser import parse
from ..type import Type
from .. import config


class DateType(Type):
    """Date type implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import types`

    """

    code = "date"
    builtin = True
    constraints = [
        "required",
        "minimum",
        "maximum",
        "enum",
    ]

    # Read

    def read_cell(self, cell):
        if isinstance(cell, datetime):
            value_time = cell.time()
            if value_time.hour == 0 and value_time.minute == 0 and value_time.second == 0:
                return datetime(cell.year, cell.month, cell.day).date()
            else:
                return None

        if isinstance(cell, date):
            return cell

        if not isinstance(cell, str):
            return None

        # Parse string date
        try:
            if self.field.format == "default":
                cell = datetime.strptime(cell, config.DEFAULT_DATE_PATTERN).date()
            elif self.field.format == "any":
                cell = parse(cell).date()
            else:
                cell = datetime.strptime(cell, self.field.format).date()
        except Exception:
            return None

        return cell

    # Write

    def write_cell(self, cell):
        format = self.field.get("format", config.DEFAULT_DATE_PATTERN)
        return cell.strftime(format)
