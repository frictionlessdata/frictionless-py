from __future__ import annotations
import re
import attrs
from decimal import Decimal
from ..schema import Field
from .. import settings


@attrs.define(kw_only=True)
class NumberField(Field):
    type = "number"
    builtin = True
    supported_constraints = [
        "required",
        "minimum",
        "maximum",
        "enum",
    ]

    # Properties

    bare_number: bool = settings.DEFAULT_BARE_NUMBER
    """
    It specifies that the value is a bare number. If true, the pattern to remove non digit
    character does not get applied and vice versa. The default value is True.
    """

    float_number: bool = settings.DEFAULT_FLOAT_NUMBER
    """
    It specifies that the value is a float number.
    """

    decimal_char: str = settings.DEFAULT_DECIMAL_CHAR
    """
    It specifies the char to be used as decimal character. The default
    value is ".". It values can be: ".", "@" etc.
    """

    group_char: str = settings.DEFAULT_GROUP_CHAR
    """
    It specifies the char to be used as group character. The default value
    is "". It can take values such as: ",", "#" etc.
    """

    # Read

    def create_value_reader(self):

        # Create pattern
        pattern = None
        if not self.bare_number:
            pattern = re.compile(r"((^\D*)|(\D*$))")

        # Create processor
        processor = None
        properties = ["group_char", "decimal_char", "bare_number"]
        if set(properties).intersection(self.list_defined()):

            def processor_function(cell):
                if pattern:
                    cell = pattern.sub("", cell)
                cell = cell.replace(self.group_char, "")
                if self.decimal_char != "." and "." in cell:
                    return None
                cell = cell.replace(self.decimal_char, ".")
                return cell

            processor = processor_function

        # Create reader
        def value_reader(cell):
            Primary = Decimal
            Secondary = float
            if self.float_number:
                Primary = float
                Secondary = Decimal
            if isinstance(cell, str):
                cell = cell.strip()

                # Process the cell
                if processor:
                    cell = processor(cell)  # type: ignore
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

        return value_reader

    # Write

    def create_value_writer(self):

        # Create writer
        def value_writer(cell):
            if self.has_defined("group_char"):
                cell = f"{cell:,}".replace(",", self.group_char)
            else:
                cell = str(cell)
            if self.has_defined("decimalChar"):
                cell = cell.replace(".", self.decimal_char)
            return cell

        return value_writer

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "bareNumber": {"type": "boolean"},
            "floatNumber": {"type": "boolean"},
            "decimalChar": {"type": "string"},
            "groupChar": {"type": "string"},
        }
    }
