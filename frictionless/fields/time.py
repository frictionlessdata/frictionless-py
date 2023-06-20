from __future__ import annotations

from datetime import datetime, time
from typing import Any

import attrs

from .. import settings
from ..platform import platform
from ..schema import Field


@attrs.define(kw_only=True, repr=False)
class TimeField(Field):
    type = "time"
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
            if not isinstance(cell, time):
                if not isinstance(cell, str):
                    return None
                try:
                    if self.format == "default":
                        # Guard against shorter formats supported by dateutil
                        assert cell[5] == ":"
                        assert len(cell) >= 8
                        cell = platform.dateutil_parser.isoparse(
                            f"2000-01-01T{cell}"
                        ).timetz()
                    elif self.format == "any":
                        cell = platform.dateutil_parser.parse(cell).timetz()
                    else:
                        cell = datetime.strptime(cell, self.format).timetz()
                except Exception:
                    return None
            return cell

        return value_reader

    # Write

    def create_value_writer(self):
        # Create format
        format = self.format
        if format == settings.DEFAULT_FIELD_FORMAT:
            format = settings.DEFAULT_TIME_PATTERN

        # Create writer
        def value_writer(cell: Any):
            cell = cell.strftime(format)
            cell = cell.replace("+0000", "Z")
            return cell

        return value_writer
