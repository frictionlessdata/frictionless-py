from ..helpers import cached_property
from ..type import Type


class BooleanType(Type):
    """Boolean type implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import types`

    """

    code = "boolean"
    constraints = [
        "required",
        "enum",
    ]

    # Read

    def read_cell(self, cell):
        if cell is True or cell is False:
            return cell
        return self.read_cell_mapping.get(cell)

    @cached_property
    def read_cell_mapping(self):
        mapping = {}
        for value in self.field.true_values:
            mapping[value] = True
        for value in self.field.false_values:
            mapping[value] = False
        return mapping

    # Write

    def write_cell(self, cell):
        return self.field.true_values[0] if cell else self.field.false_values[0]
