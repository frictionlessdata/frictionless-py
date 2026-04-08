from typing import Any, Literal, Optional

from .base_field_descriptor import BaseFieldDescriptor
from .field_constraints import ValueConstraints


class YearFieldDescriptor(BaseFieldDescriptor):
    """The field contains a calendar year."""

    type: Literal["year"] = "year"
    format: Optional[Literal["default"]] = None
    constraints: Optional[ValueConstraints[int]] = None

    def read_value(self, cell: Any) -> Optional[int]:
        if not isinstance(cell, int):
            if not isinstance(cell, str):
                return None
            if len(cell) != 4:
                return None
            try:
                cell = int(cell)
            except Exception:
                return None
        if cell < 0 or cell > 9999:
            return None
        return cell

    def write_value(self, cell: Optional[int]) -> Optional[str]:
        if cell is None:
            return None
        return str(cell)

