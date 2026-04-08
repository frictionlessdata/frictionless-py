import re
from decimal import Decimal
from typing import Any, Callable, Literal, Optional, Pattern, Union

from pydantic import Field as PydanticField

from .. import settings
from .base_field_descriptor import BaseFieldDescriptor
from .field_constraints import ValueConstraints


class NumberFieldDescriptor(BaseFieldDescriptor):
    """The field contains numbers of any kind including decimals."""

    type: Literal["number"] = "number"
    format: Optional[Literal["default"]] = None
    constraints: Optional[ValueConstraints[Union[int, float]]] = None

    decimal_char: Optional[str] = PydanticField(default=None, alias="decimalChar")
    """
    String whose value is used to represent a decimal point for number fields
    """

    group_char: Optional[str] = PydanticField(default=None, alias="groupChar")
    """
    String whose value is used to group digits for integer/number fields
    """

    bare_number: Optional[bool] = PydanticField(default=None, alias="bareNumber")
    """
    If false leading and trailing non numbers will be removed for integer/number fields
    """

    float_number: Optional[bool] = PydanticField(default=None, alias="floatNumber")
    """
    It specifies that the value is a float number.
    """

    def read_value(self, cell: Any) -> Optional[Union[float, Decimal]]:
        # Create pattern
        pattern: Optional[Pattern[str]] = None
        bare_number_value = self.bare_number if self.bare_number is not None else settings.DEFAULT_BARE_NUMBER
        if not bare_number_value:
            pattern = re.compile(r"((^[^-\d]*)|(\D*$))")

        # Create processor
        processor: Optional[Callable[[str], Optional[str]]] = None
        decimal_char_value = self.decimal_char if self.decimal_char is not None else settings.DEFAULT_DECIMAL_CHAR
        group_char_value = self.group_char if self.group_char is not None else settings.DEFAULT_GROUP_CHAR

        if self.decimal_char is not None or self.group_char is not None or self.bare_number is not None:
            def processor_function(cell: str) -> Optional[str]:
                if pattern:
                    cell = pattern.sub("", cell)
                cell = cell.replace(group_char_value, "")
                if decimal_char_value != "." and "." in cell:
                    return None
                cell = cell.replace(decimal_char_value, ".")
                return cell

            processor = processor_function

        # Determine primary and secondary types
        Primary = Decimal
        Secondary = float
        float_number_value = self.float_number if self.float_number is not None else settings.DEFAULT_FLOAT_NUMBER
        if float_number_value:
            Primary = float
            Secondary = Decimal

        if isinstance(cell, str):
            cell = cell.strip()

            # Process the cell
            if processor:
                cell = processor(cell)
                if cell is None:
                    return None

            # Cast the cell
            try:
                return Primary(cell)  # type: ignore
            except Exception:
                return None

        elif isinstance(cell, Primary):
            return cell
        elif cell is True or cell is False:
            return None
        elif isinstance(cell, int):
            return cell
        elif isinstance(cell, Secondary):
            return Primary(str(cell) if Primary is Decimal else cell)
        return None

    def write_value(self, cell: Any) -> Optional[str]:
        if cell is None:
            return None
        
        if self.group_char is not None:
            cell = f"{cell:,}".replace(",", "g")
        else:
            cell = str(cell)
        if self.decimal_char is not None:
            cell = cell.replace(".", self.decimal_char)
        if self.group_char is not None:
            cell = cell.replace("g", self.group_char)
        return cell

