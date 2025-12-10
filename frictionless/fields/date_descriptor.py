import datetime
from typing import Any, Literal, Optional


from .. import settings
from .base_field_descriptor import BaseFieldDescriptor
from .field_constraints import ValueConstraints


class DateFieldDescriptor(BaseFieldDescriptor):
    """The field contains a date without a time."""

    type: Literal["date"] = "date"
    format: Optional[str] = None
    constraints: Optional[ValueConstraints[str]] = None

    def read_value(self, cell: Any) -> Optional[datetime.date]:
        from datetime import date, datetime
        from ..platform import platform

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
            format_value = self.format or "default"
            if format_value == "default":
                cell = datetime.strptime(cell, settings.DEFAULT_DATE_PATTERN).date()
            elif format_value == "any":
                cell = platform.dateutil_parser.parse(cell).date()
            else:
                cell = datetime.strptime(cell, format_value).date()
        except Exception:
            return None
        return cell

    def write_value(self, cell: Optional[datetime.date]) -> Optional[str]:
        if cell is None:
            return None
        format_value = self.format or "default"
        if format_value == settings.DEFAULT_FIELD_FORMAT:
            format_value = settings.DEFAULT_DATE_PATTERN
        return cell.strftime(format_value)
