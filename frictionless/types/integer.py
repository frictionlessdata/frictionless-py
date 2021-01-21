import re
from decimal import Decimal
from ..metadata import Metadata
from ..type import Type


class IntegerType(Type):
    """Integer type implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import types`

    """

    code = "integer"
    constraints = [
        "required",
        "minimum",
        "maximum",
        "enum",
    ]

    # Read

    def read_cell(self, cell):
        if isinstance(cell, str):
            if self.read_cell_pattern:
                cell = self.read_cell_pattern.sub("", cell)
            try:
                return int(cell)
            except Exception:
                return None
        elif cell is True or cell is False:
            return None
        elif isinstance(cell, int):
            return cell
        elif isinstance(cell, float) and cell.is_integer():
            return int(cell)
        elif isinstance(cell, Decimal) and cell % 1 == 0:
            return int(cell)
        return None

    @Metadata.property(write=False)
    def read_cell_pattern(self):
        if not self.field.bare_number:
            return re.compile(r"((^\D*)|(\D*$))")

    # Write

    def write_cell(self, cell):
        return str(cell)
