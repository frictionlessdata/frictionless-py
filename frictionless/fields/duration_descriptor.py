import datetime
from typing import Any, Literal, Optional

from ..platform import platform
from .base_field_descriptor import BaseFieldDescriptor
from .field_constraints import ValueConstraints


class DurationFieldDescriptor(BaseFieldDescriptor):
    """The field contains a duration of time."""

    type: Literal["duration"] = "duration"
    format: Optional[Literal["default"]] = None
    constraints: Optional[ValueConstraints[str]] = None

    def read_value(self, cell: Any) -> Any:
        if not isinstance(cell, (platform.isodate.Duration, datetime.timedelta)):  # type: ignore
            if not isinstance(cell, str):
                return None
            try:
                cell = platform.isodate.parse_duration(cell)  # type: ignore
            except Exception:
                return None
        return cell

    def write_value(self, cell: Any) -> Optional[str]:
        if cell is None:
            return None
        return platform.isodate.duration_isoformat(cell)  # type: ignore


