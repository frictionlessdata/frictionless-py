from __future__ import annotations
import attrs
import datetime
from typing import Any
from ..schema import Field
from ..platform import platform


@attrs.define(kw_only=True)
class DurationField(Field):
    type = "duration"
    builtin = True
    supported_constraints = [
        "required",
        "enum",
    ]

    # Read

    def create_value_reader(self):
        # Create reader
        def value_reader(cell: Any):
            if not isinstance(cell, (platform.isodate.Duration, datetime.timedelta)):
                if not isinstance(cell, str):
                    return None
                try:
                    cell = platform.isodate.parse_duration(cell)  # type: ignore
                except Exception:
                    return None
            return cell

        return value_reader

    # Write

    def create_value_writer(self):
        # Create writer
        def value_writer(cell: Any):  # type: ignore
            return platform.isodate.duration_isoformat(cell)  # type: ignore

        return value_writer
