from __future__ import annotations

import json
from typing import Any, Dict, cast

import attrs

from ..schema import Field


@attrs.define(kw_only=True, repr=False)
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
        def value_reader(cell: Any):
            if not isinstance(cell, dict):
                if not isinstance(cell, str):
                    return None
                try:
                    cell = json.loads(cell)
                except Exception:
                    return None
                if not isinstance(cell, dict):
                    return None
            return cast(Dict[str, Any], cell)

        return value_reader

    # Write

    def create_value_writer(self):
        # Create writer
        def value_writer(cell: Any):
            return json.dumps(cell)

        return value_writer
