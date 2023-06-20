from __future__ import annotations

from datetime import date, datetime
from typing import Any

import attrs

from .. import settings
from ..platform import platform
from ..schema import Field


@attrs.define(kw_only=True, repr=False)
class DateField(Field):
    type = "date"
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
        def value_reader(cell: Any):
            if isinstance(cell, datetime):
                value_time = cell.time()
                if (
                    value_time.hour == 0
                    and value_time.minute == 0
                    and value_time.second == 0
                ):
                    return datetime(cell.year, cell.month, cell.day).date()
                else:
                    return None
            if isinstance(cell, date):
                return cell
            if not isinstance(cell, str):
                return None
            try:
                if self.format == "default":
                    cell = datetime.strptime(cell, settings.DEFAULT_DATE_PATTERN).date()
                elif self.format == "any":
                    cell = platform.dateutil_parser.parse(cell).date()
                else:
                    cell = datetime.strptime(cell, self.format).date()
            except Exception:
                return None
            return cell

        return value_reader

    # Write

    def create_value_writer(self):
        # Create format
        format = self.format
        if format == settings.DEFAULT_FIELD_FORMAT:
            format = settings.DEFAULT_DATE_PATTERN

        # Create writer
        def value_writer(cell: Any):
            return cell.strftime(format)

        return value_writer
