from __future__ import annotations
import attrs
from typing import Optional, Any
from ...pipeline import Step


@attrs.define(kw_only=True)
class cell_convert(Step):
    """Convert cell

    Converts cell values of one or more fields using arbitrary functions, method
    invocations or dictionary translations.

    """

    type = "cell-convert"

    # State

    value: Optional[Any] = None
    """Value to set in the field's cells"""

    mapping: Optional[dict] = None
    """Mapping to apply to the column"""

    function: Optional[Any] = None
    """Function to apply to the column"""

    field_name: Optional[str] = None
    """Name of the field to apply the transform on"""

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
        elif self.mapping:
            resource.data = table.convert(self.field_name, self.mapping)  # type: ignore
        else:
            resource.data = table.update(self.field_name, self.value)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "value": {},
            "mapping": {"type": "object"},
            "fieldName": {"type": "string"},
        },
    }
