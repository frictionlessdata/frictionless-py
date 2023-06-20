from __future__ import annotations

import datetime
from typing import Any

import attrs

from ..platform import platform
from ..schema import Field


@attrs.define(kw_only=True, repr=False)
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
            if not isinstance(cell, (platform.isodate.Duration, datetime.timedelta)):  # type: ignore
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
