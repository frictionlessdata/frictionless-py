from typing import Any, Literal, NamedTuple, Optional

from .base_field_descriptor import BaseFieldDescriptor
from .field_constraints import ValueConstraints


class yearmonth(NamedTuple):
    """Internal representation of a year-month"""
    year: int
    month: int


class YearmonthFieldDescriptor(BaseFieldDescriptor):
    """The field contains a specific month of a specific year."""

    type: Literal["yearmonth"] = "yearmonth"
    format: Optional[Literal["default"]] = None
    constraints: Optional[ValueConstraints[str]] = None

    def read_value(self, cell: Any) -> Optional[yearmonth]:
        if isinstance(cell, (tuple, list)):
            if len(cell) != 2:  # type: ignore
                return None
            cell = yearmonth(year=cell[0], month=cell[1])  # type: ignore
        elif isinstance(cell, str):
            try:
                year, month = cell.split("-")
                year = int(year)
                month = int(month)
                if month < 1 or month > 12:
                    return None
                cell = yearmonth(year, month)
            except Exception:
                return None
        else:
            return None
        return cell

    def write_value(self, cell: Any) -> Optional[str]:
        if cell is None:
            return None
        return f"{cell.year}-{cell.month:02}"

