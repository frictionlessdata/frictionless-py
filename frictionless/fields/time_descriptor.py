import datetime
from datetime import time
from typing import Any, Literal, Optional

from .. import settings
from ..platform import platform
from .base_field_descriptor import BaseFieldDescriptor
from .field_constraints import ValueConstraints


class TimeFieldDescriptor(BaseFieldDescriptor):
    """The field contains a time without a date."""

    type: Literal["time"] = "time"
    format: Optional[str] = None
    constraints: Optional[ValueConstraints[time]] = None

    def read_value(self, cell: Any) -> Optional[time]:
        if not isinstance(cell, time):
            if not isinstance(cell, str):
                return None
            try:
                format_value = self.format or "default"
                if format_value == "default":
                    # Guard against shorter formats supported by dateutil
                    assert cell[5] == ":"
                    assert len(cell) >= 8
                    cell = platform.dateutil_parser.isoparse(
                        f"2000-01-01T{cell}"
                    ).timetz()
                elif format_value == "any":
                    cell = platform.dateutil_parser.parse(cell).timetz()
                else:
                    cell = datetime.datetime.strptime(cell, format_value).timetz()
            except Exception:
                return None
        return cell

    def write_value(self, cell: Optional[time]) -> Optional[str]:
        if cell is None:
            return None
        format_value = self.format or "default"
        if format_value == settings.DEFAULT_FIELD_FORMAT:
            format_value = settings.DEFAULT_TIME_PATTERN
        result = cell.strftime(format_value)
        result = result.replace("+0000", "Z")
        return result

