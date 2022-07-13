from __future__ import annotations
import attrs
from typing import Optional, Any
from ...pipeline import Step


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Currently, metadata profiles are not fully finished; will require improvements


@attrs.define(kw_only=True)
class cell_convert(Step):
    """Convert cell"""

    type = "cell-convert"

    # State

    value: Optional[Any] = None
    """TODO: add docs"""

    function: Optional[Any] = None
    """TODO: add docs"""

    field_name: Optional[str] = None
    """TODO: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        function = self.function
        if not self.field_name:
            if not function:
                function = lambda _: self.value
            resource.data = table.convertall(function)  # type: ignore
        elif self.function:
            resource.data = table.convert(self.field_name, function)  # type: ignore
        else:
            resource.data = table.update(self.field_name, self.value)  # type: ignore

    # Metadata

    metadata_profile = {
        "type": "object",
        "required": [],
        "properties": {
            "type": {"type": "string"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "value": {},
            "fieldName": {"type": "string"},
        },
    }
