from typing import Any, ClassVar, List, Literal, Optional

from pydantic import Field as PydanticField, AliasChoices

from .. import settings
from .base_field_descriptor import BaseFieldDescriptor
from .field_constraints import BaseConstraints

class BooleanFieldDescriptor(BaseFieldDescriptor):
    """The field contains boolean (true/false) data."""

    type: ClassVar[Literal["boolean"]] = "boolean"

    format: Optional[Literal["default"]] = None
    constraints: Optional[BaseConstraints[bool]] = None

    true_values: Optional[List[str]] = PydanticField(
        default=settings.DEFAULT_TRUE_VALUES,
        alias="trueValues",
        validation_alias=AliasChoices("trueValues", "true_values"),
    )
    """
    Values to be interpreted as "true" for boolean fields
    """

    false_values: Optional[List[str]] = PydanticField(
        default=settings.DEFAULT_FALSE_VALUES,
        alias="falseValues",
        validation_alias=AliasChoices("falseValues", "false_values"),
    )
    """
    Values to be interpreted as "false" for boolean fields
    """

    def read_value(self, cell: Any) -> Optional[bool]:
        if isinstance(cell, bool):
            return cell

        if isinstance(cell, str):
            if self.true_values and cell in self.true_values:
                return True
            if self.false_values and cell in self.false_values:
                return False

        return None

    def write_value(self, cell: Optional[bool]) -> Optional[str]:
        if self.true_values and self.false_values:
            return self.true_values[0] if cell else self.false_values[0]
        return None
