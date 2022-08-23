from __future__ import annotations
import json
import attrs
from ..schema import Field


@attrs.define(kw_only=True)
class ObjectField(Field):
    type = "object"
    builtin = True
    supported_constraints = [
        "required",
        "minLength",
        "maxLength",
        "enum",
    ]

    # Read

    def create_value_reader(self):

        # Create reader
        def value_reader(cell):
            if not isinstance(cell, dict):
                if not isinstance(cell, str):
                    return None
                try:
                    cell = json.loads(cell)
                except Exception:
                    return None
                if not isinstance(cell, dict):
                    return None
            return cell

        return value_reader

    # Write

    def create_value_writer(self):

        # Create writer
        def value_writer(cell):
            return json.dumps(cell)

        return value_writer
