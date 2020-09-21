from ..type import Type


class AnyType(Type):
    """Any type implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import types`

    """

    supported_constraints = [
        "required",
        "enum",
    ]

    # Read

    def read_cell(self, cell):
        return cell

    # Write

    def write_cell(self, cell):
        return str(cell)
