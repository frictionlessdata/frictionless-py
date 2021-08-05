import re
from decimal import Decimal
from ..metadata import Metadata
from ..type import Type


class NumberType(Type):
    """Number type implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import types`

    """

    code = "number"
    builtin = True
    constraints = [
        "required",
        "minimum",
        "maximum",
        "enum",
    ]

    # Read

    def read_cell(self, cell):
        Primary = Decimal
        Secondary = float
        if self.field.float_number:
            Primary = float
            Secondary = Decimal
        if isinstance(cell, str):
            if self.read_cell_processor:
                cell = self.read_cell_processor(cell)
            try:
                return Primary(cell)
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

    @Metadata.property(write=False)
    def read_cell_processor(self):
        if set(["groupChar", "decimalChar", "bareNumber"]).intersection(
            self.field.keys()
        ):

            def processor(cell):
                cell = cell.replace(self.field.group_char, "")
                cell = cell.replace(self.field.decimal_char, ".")
                if self.read_cell_pattern:
                    cell = self.read_cell_pattern.sub("", cell)
                return cell

            return processor

    @Metadata.property(write=False)
    def read_cell_pattern(self):
        if not self.field.bare_number:
            return re.compile(r"((^\D*)|(\D*$))")

    # Write

    def write_cell(self, cell):
        if "groupChar" in self.field:
            cell = f"{cell:,}".replace(",", self.field.group_char)
        else:
            cell = str(cell)
        if "decimalChar" in self.field:
            cell = cell.replace(".", self.field.decimal_char)
        return cell
