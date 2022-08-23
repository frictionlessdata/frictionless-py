from __future__ import annotations
import attrs
from ..schema import Field


@attrs.define(kw_only=True)
class YearField(Field):
    type = "year"
    builtin = True
    supported_constraints = [
        "required",
        "minimum",
        "maximum",
        "enum",
    ]

    # Read

    def create_value_reader(self):

        # Create reader
        def value_reader(cell):
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

        return value_reader

    # Write

    def create_value_writer(self):

        # Create writer
        def value_writer(cell):
            return str(cell)

        return value_writer
