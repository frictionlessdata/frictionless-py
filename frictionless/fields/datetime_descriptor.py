import datetime
from typing import Any, Literal, Optional

from .. import settings
from ..platform import platform
from .base_field_descriptor import BaseFieldDescriptor
from .field_constraints import ValueConstraints


class DatetimeFieldDescriptor(BaseFieldDescriptor):
    """The field contains a date with a time."""

    type: Literal["datetime"] = "datetime"
    format: Optional[str] = None
    constraints: Optional[ValueConstraints[datetime.datetime]] = None

    def read_value(self, cell: Any) -> Optional[datetime.datetime]:
        if not isinstance(cell, datetime.datetime):
            if not isinstance(cell, str):
                return None
            try:
                format_value = self.format or "default"
                if format_value == "default":
                    # Guard against shorter formats supported by dateutil
                    assert cell[16] == ":"
                    assert len(cell) >= 19
                    cell = platform.dateutil_parser.isoparse(cell)
                elif format_value == "any":
                    cell = platform.dateutil_parser.parse(cell)
                else:
                    cell = datetime.datetime.strptime(cell, format_value)
            except Exception:
                return None
        return cell

    def write_value(self, cell: Optional[datetime.datetime]) -> Optional[str]:
        if cell is None:
            return None
        format_value = self.format or "default"
        if format_value == settings.DEFAULT_FIELD_FORMAT:
            format_value = settings.DEFAULT_DATETIME_PATTERN
        result = cell.strftime(format_value)
        result = result.replace("+0000", "Z")
        return result
