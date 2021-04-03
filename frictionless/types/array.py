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
        return cell

    # Write

    def write_cell(self, cell):
        return json.dumps(cell)
