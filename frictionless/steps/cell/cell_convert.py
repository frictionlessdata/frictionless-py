from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

import attrs

from ...pipeline import Step

if TYPE_CHECKING:
    from ...resource import Resource


@attrs.define(kw_only=True, repr=False)
class cell_convert(Step):
    """Convert cell

    Converts cell values of one or more fields using arbitrary functions, method
    invocations or dictionary translations.

    """

    type = "cell-convert"

    value: Optional[Any] = None
    """Value to set in the field's cells"""

    mapping: Optional[Dict[str, Any]] = None
    """Mapping to apply to the column"""

    function: Optional[Any] = None
    """Function to apply to the column"""

    field_name: Optional[str] = None
    """Name of the field to apply the transform on"""

    # Transform

    def transform_resource(self, resource: Resource):
        table = resource.to_petl()  # type: ignore
        function = self.function
        if not self.field_name:
            if not function:
                function = lambda _: self.value  # type: ignore
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
