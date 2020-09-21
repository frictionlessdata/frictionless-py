from ..type import Type


class YearType(Type):
    """Year type implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import types`

    """

    supported_constraints = [
        "required",
        "minimum",
        "maximum",
        "enum",
    ]

    # Read

    def read_cell(self, cell):
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

    # Write

    def write_cell(self, cell):
        return str(cell)
