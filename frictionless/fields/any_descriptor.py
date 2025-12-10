from typing import Any, Literal, Optional

from .base_field_descriptor import BaseFieldDescriptor
from .field_constraints import BaseConstraints


class AnyFieldDescriptor(BaseFieldDescriptor):
    """The field contains values of a unspecified or mixed type."""

    type: Literal["any"] = "any"
    format: Optional[Literal["default"]] = None
    constraints: Optional[BaseConstraints[str]] = None

    def read_value(self, cell: Any) -> Any:
        # Any field accepts any value as-is
        return cell

    def write_value(self, cell: Any) -> Any:
        # Any field returns the value as-is
        return cell

