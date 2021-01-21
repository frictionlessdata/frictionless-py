import isodate
import datetime
from ..type import Type


class DurationType(Type):
    """Duration type implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import types`

    """

    code = "duration"
    constraints = [
        "required",
        "enum",
    ]

    # Read

    def read_cell(self, cell):
        if not isinstance(cell, (isodate.Duration, datetime.timedelta)):
            if not isinstance(cell, str):
                return None
            try:
                cell = isodate.parse_duration(cell)
            except Exception:
                return None
        return cell

    # Write

    def write_cell(self, cell):
        return isodate.duration_isoformat(cell)
