from __future__ import annotations
import attrs
from datetime import datetime
from ..platform import platform
from ..schema import Field
from .. import settings


@attrs.define(kw_only=True)
class DatetimeField(Field):
    type = "datetime"
    builtin = True
    supported_constraints = [
        "required",
        "minimum",
        "maximum",
        "enum",
    ]

    # Read

    # TODO: use different value_readers based on format (see string)
    def create_value_reader(self):

        # Create reader
        def value_reader(cell):
            if not isinstance(cell, datetime):
                if not isinstance(cell, str):
                    return None
                try:
                    if self.format == "default":
                        # Guard against shorter formats supported by dateutil
                        assert cell[16] == ":"
                        assert len(cell) >= 19
                        cell = platform.dateutil_parser.isoparse(cell)
                    elif self.format == "any":
                        cell = platform.dateutil_parser.parse(cell)
                    else:
                        cell = datetime.strptime(cell, self.format)
                except Exception:
                    return None
            return cell

        return value_reader

    # Write

    def create_value_writer(self):

        # Create format
        format = self.format
        if format == settings.DEFAULT_FIELD_FORMAT:
            format = settings.DEFAULT_DATETIME_PATTERN

        # Create writer
        def value_writer(cell):
            cell = cell.strftime(format)
            cell = cell.replace("+0000", "Z")
            return cell

        return value_writer
