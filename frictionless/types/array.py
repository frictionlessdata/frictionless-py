import json
from ..type import Type


class ArrayType(Type):
    """Array type implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import types`

    """

    code = "array"
    builtin = True
    constraints = [
        "required",
        "minLength",
        "maxLength",
        "enum",
    ]

    # Read

    def read_cell(self, cell):
        if not isinstance(cell, list):
            if isinstance(cell, str):
                try:
                    cell = json.loads(cell)
                except Exception:
                    return None
                if not isinstance(cell, list):
                    return None
            elif isinstance(cell, tuple):
                cell = list(cell)
            else:
                return None
        if self.field.array_item_field:
            for index, item in enumerate(cell):
                item, note = self.field.array_item_field.read_cell(item)
                if note:
                    return None
                cell[index] = item
        return cell

    # Write

    def write_cell(self, cell):
        return json.dumps(cell)
