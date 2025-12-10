
import re
from decimal import Decimal
from typing import  Any, ClassVar, Literal, Optional, Pattern, Union, List

from pydantic import Field as PydanticField, BaseModel

from .. import settings
from .base_field_descriptor import BaseFieldDescriptor
from .field_constraints import ValueConstraints


class CategoryDict(BaseModel):
    """Category dictionary for field categories."""
    value: str
    label: Optional[str] = None

ICategories = Union[
    List[str],
    List[CategoryDict],
]

class IntegerFieldDescriptor(BaseFieldDescriptor):
    """The field contains integers - that is whole numbers."""

    type: Literal["integer"] = "integer"
    format: Optional[Literal["default"]] = None
    constraints: Optional[ValueConstraints[int]] = None

    categories: Optional[ICategories] = None
    """
    Property to restrict the field to a finite set of possible values
    """

    categories_ordered: Optional[bool] = PydanticField(
        default=None, alias="categoriesOrdered"
    )
    """
    When categoriesOrdered is true, implementations SHOULD regard the order of
    appearance of the values in the categories property as their natural order.
    """

    group_char: Optional[str] = PydanticField(default=None, alias="groupChar")
    """
    String whose value is used to group digits for integer/number fields
    """

    bare_number: bool = PydanticField(
        default=settings.DEFAULT_BARE_NUMBER, alias="bareNumber"
    )
    """
    If false leading and trailing non numbers will be removed for integer/number fields
    """

    pattern: ClassVar[Pattern[str]] = re.compile(r"((^[^-\d]*)|(\D*$))")

    def read_value(self, cell: Any) -> Optional[int]:
        if isinstance(cell, bool):
            return None

        elif isinstance(cell, int):
            return cell

        elif isinstance(cell, str):
            cell = cell.strip()

            # Process the cell (remove non-digit characters if bare_number is False)
            if not self.bare_number:
                cell = self.pattern.sub("", cell)

            # Cast the cell
            try:
                return int(cell)
            except Exception:
                return None

        elif isinstance(cell, float) and cell.is_integer():
            return int(cell)
        elif isinstance(cell, Decimal) and cell % 1 == 0:
            return int(cell)

        return None

    def write_value(self, cell: Optional[int]) -> Optional[str]:
        if cell is None:
            return None
        return str(cell)
